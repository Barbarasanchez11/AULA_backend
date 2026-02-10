"""
Script to import events from CSV file into AULA+ database.

This script:
1. Reads events from a CSV file
2. Normalizes text fields
3. Validates PII (rejects events with personal data)
4. Validates data schema
5. Imports events to PostgreSQL
6. Generates embeddings automatically (via API background tasks)

CSV Format:
- classroom_id: UUID of the classroom
- event_type: TRANSICION, CAMBIO_DE_RUTINA, APRENDIZAJE, REGULACION
- description: Event description (min 10 chars)
- moment_of_day: mañana, mediodia, tarde
- day_of_week: lunes, martes, miercoles, jueves, viernes, sabado, domingo (optional)
- duration_minutes: Integer (optional)
- supports: Comma-separated list (Anticipación visual, Adaptación del entorno, etc.)
- additional_supports: Text (optional)
- result: EXITOSO, PARCIAL, DIFICULTAD
- observations: Text (optional)
"""

import csv
import sys
import os
from pathlib import Path
from uuid import UUID
from typing import List, Dict, Optional
import asyncio

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.database import Base, get_db
from app.models.models import Event, Classroom
from app.schemas.enums import EventType, EventResult, MomentOfDay, DayOfWeek, SupportType
from app.services.text_normalizer import TextNormalizer
from app.services.pii_validator import PIIValidator
from app.services.embeddingService import EmbeddingService
from app.services.vector_store import VectorStore
from app.config import settings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EventImporter:
    """Service for importing events from CSV"""
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize EventImporter.
        
        Args:
            db_session: Database session
        """
        self.db = db_session
        self.normalizer = TextNormalizer()
        self.pii_validator = PIIValidator()
        self.embedding_service = EmbeddingService.get_instance()
        self.vector_store = VectorStore()
    
    def parse_supports(self, supports_str: str) -> List[str]:
        """
        Parse supports string (comma or semicolon-separated) into list.
        
        Supports both comma (,) and semicolon (;) as separators.
        
        Args:
            supports_str: Comma or semicolon-separated string of supports
            
        Returns:
            List of support strings
        """
        if not supports_str or not supports_str.strip():
            return []
        
        # Split by comma or semicolon and clean
        # Allow both "," and ";" as separators for convenience
        import re
        supports = [s.strip() for s in re.split(r'[;,]', supports_str)]
        # Remove empty strings
        supports = [s for s in supports if s]
        return supports
    
    def validate_supports(self, supports: List[str]) -> List[str]:
        """
        Validate that supports are valid SupportType values.
        
        Args:
            supports: List of support strings
            
        Returns:
            List of valid support strings
            
        Raises:
            ValueError: If any support is invalid
        """
        valid_supports = [st.value for st in SupportType]
        invalid = [s for s in supports if s not in valid_supports]
        
        if invalid:
            raise ValueError(f"Invalid supports: {', '.join(invalid)}. Valid supports: {', '.join(valid_supports)}")
        
        return supports
    
    async def validate_classroom(self, classroom_id: UUID) -> bool:
        """
        Validate that classroom exists.
        
        Args:
            classroom_id: UUID of classroom
            
        Returns:
            True if classroom exists, False otherwise
        """
        result = await self.db.execute(select(Classroom).where(Classroom.id == classroom_id))
        classroom = result.scalar_one_or_none()
        return classroom is not None
    
    def parse_row(self, row: Dict[str, str]) -> Dict:
        """
        Parse CSV row into event data.
        
        Args:
            row: Dictionary from CSV row
            
        Returns:
            Dictionary with parsed event data
            
        Raises:
            ValueError: If data is invalid
        """
        # Required fields - Note: classroom_id can be overridden in import_from_csv
        # This method doesn't handle override, it's handled at import level
        try:
            classroom_id = UUID(row['classroom_id'])
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid classroom_id: {row.get('classroom_id', 'missing')}")
        
        try:
            event_type = EventType(row['event_type'].strip())
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid event_type: {row.get('event_type', 'missing')}")
        
        description = row.get('description', '').strip()
        if not description or len(description) < 10:
            raise ValueError(f"Description must be at least 10 characters: '{description}'")
        
        try:
            moment_of_day = MomentOfDay(row['moment_of_day'].strip())
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid moment_of_day: {row.get('moment_of_day', 'missing')}")
        
        day_of_week = None
        if row.get('day_of_week') and row['day_of_week'].strip():
            try:
                day_of_week = DayOfWeek(row['day_of_week'].strip())
            except ValueError:
                raise ValueError(f"Invalid day_of_week: {row['day_of_week']}")
        
        duration_minutes = None
        if row.get('duration_minutes') and row['duration_minutes'].strip():
            try:
                duration_minutes = int(row['duration_minutes'].strip())
                if duration_minutes < 1:
                    raise ValueError("duration_minutes must be >= 1")
            except ValueError as e:
                raise ValueError(f"Invalid duration_minutes: {row['duration_minutes']}")
        
        supports_str = row.get('supports', '').strip()
        if not supports_str:
            raise ValueError("supports is required")
        
        supports = self.parse_supports(supports_str)
        if not supports:
            raise ValueError("At least one support is required")
        
        supports = self.validate_supports(supports)
        
        additional_supports = row.get('additional_supports', '').strip() or None
        
        try:
            result = EventResult(row['result'].strip())
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid result: {row.get('result', 'missing')}")
        
        observations = row.get('observations', '').strip() or None
        
        return {
            "classroom_id": classroom_id,
            "event_type": event_type.value,
            "description": description,
            "moment_of_day": moment_of_day.value,
            "day_of_week": day_of_week.value if day_of_week else None,
            "duration_minutes": duration_minutes,
            "supports": supports,
            "additional_supports": additional_supports,
            "result": result.value,
            "observations": observations
        }
    
    async def import_event(self, event_data: Dict) -> tuple[bool, str, Optional[UUID]]:
        """
        Import a single event.
        
        Args:
            event_data: Parsed event data
            
        Returns:
            Tuple of (success: bool, message: str, event_id: Optional[UUID])
        """
        try:
            # Validate classroom exists
            if not await self.validate_classroom(event_data["classroom_id"]):
                return False, f"Classroom {event_data['classroom_id']} not found", None
            
            # Normalize text fields
            normalized = self.normalizer.normalize_event_text(
                description=event_data["description"],
                additional_supports=event_data.get("additional_supports"),
                observations=event_data.get("observations")
            )
            
            # Validate PII
            pii_result = self.pii_validator.validate_event_text(
                description=normalized["description"],
                additional_supports=normalized["additional_supports"],
                observations=normalized["observations"]
            )
            
            if not pii_result.is_valid:
                return False, f"PII detected: {pii_result.get_error_message()}", None
            
            # Create event in database
            db_event = Event(
                classroom_id=event_data["classroom_id"],
                event_type=event_data["event_type"],
                description=normalized["description"],
                moment_of_day=event_data["moment_of_day"],
                day_of_week=event_data["day_of_week"],
                duration_minutes=event_data["duration_minutes"],
                supports=event_data["supports"],
                additional_supports=normalized["additional_supports"],
                result=event_data["result"],
                observations=normalized["observations"]
            )
            
            self.db.add(db_event)
            await self.db.commit()
            await self.db.refresh(db_event)
            
            # Generate embeddings in background (synchronous call for script)
            try:
                self._generate_and_store_embeddings(
                    event_id=db_event.id,
                    classroom_id=db_event.classroom_id,
                    event_type=db_event.event_type,
                    description=db_event.description,
                    moment_of_day=db_event.moment_of_day,
                    day_of_week=db_event.day_of_week,
                    supports=db_event.supports,
                    result=db_event.result,
                    additional_supports=db_event.additional_supports,
                    observations=db_event.observations
                )
            except Exception as e:
                # Log error but don't fail the import
                print(f"Warning: Failed to generate embeddings for event {db_event.id}: {e}")
            
            return True, "Event imported successfully", db_event.id
            
        except Exception as e:
            await self.db.rollback()
            return False, f"Error: {str(e)}", None
    
    def _generate_and_store_embeddings(
        self,
        event_id: UUID,
        classroom_id: UUID,
        event_type: str,
        description: str,
        moment_of_day: str,
        day_of_week: str | None,
        supports: List[str],
        result: str,
        additional_supports: str | None,
        observations: str | None
    ):
        """Generate and store embeddings for an event (synchronous version for script)"""
        try:
            # Generate embeddings (both fast and quality)
            embedding_fast = self.embedding_service.generate_event_embedding(
                event_type=event_type,
                description=description,
                moment_of_day=moment_of_day,
                day_of_week=day_of_week,
                supports=supports,
                result=result,
                additional_supports=additional_supports,
                observations=observations,
                model_type="fast"
            )
            
            embedding_quality = self.embedding_service.generate_event_embedding(
                event_type=event_type,
                description=description,
                moment_of_day=moment_of_day,
                day_of_week=day_of_week,
                supports=supports,
                result=result,
                additional_supports=additional_supports,
                observations=observations,
                model_type="quality"
            )
            
            # Store embeddings in VectorStore with metadata
            metadata = {
                "event_type": event_type,
                "result": result,
                "moment_of_day": moment_of_day,
                "original_event_id": str(event_id)
            }
            
            # Store fast embedding
            self.vector_store.add_event_embedding(
                classroom_id=classroom_id,
                event_id=str(event_id),
                embedding=embedding_fast,
                metadata={**metadata, "original_event_id": str(event_id)},
                model_type="fast"
            )
            
            # Store quality embedding
            self.vector_store.add_event_embedding(
                classroom_id=classroom_id,
                event_id=str(event_id),
                embedding=embedding_quality,
                metadata={**metadata, "original_event_id": str(event_id)},
                model_type="quality"
            )
            
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}") from e
    
    async def import_from_csv(
        self, 
        csv_path: str, 
        skip_errors: bool = True,
        override_classroom_id: Optional[UUID] = None
    ) -> Dict:
        """
        Import events from CSV file.
        
        Args:
            csv_path: Path to CSV file
            skip_errors: If True, continue importing even if some events fail
            override_classroom_id: Optional UUID to override classroom_id from CSV
            
        Returns:
            Dictionary with import statistics
        """
        results = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "classroom_id": override_classroom_id
        }
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    results["total"] += 1
                    
                    try:
                        # Parse row
                        event_data = self.parse_row(row)
                        
                        # Override classroom_id if provided
                        if override_classroom_id:
                            event_data["classroom_id"] = override_classroom_id
                        
                        # Import event
                        success, message, event_id = await self.import_event(event_data)
                        
                        if success:
                            results["successful"] += 1
                            # Store classroom_id from first successful import
                            if not results.get("classroom_id"):
                                results["classroom_id"] = event_data["classroom_id"]
                            print(f"✅ Row {row_num}: Event imported (ID: {event_id})")
                        else:
                            results["failed"] += 1
                            results["errors"].append({
                                "row": row_num,
                                "error": message,
                                "data": row
                            })
                            print(f"❌ Row {row_num}: {message}")
                            
                            if not skip_errors:
                                raise Exception(f"Import failed at row {row_num}: {message}")
                    
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({
                            "row": row_num,
                            "error": str(e),
                            "data": row
                        })
                        print(f"❌ Row {row_num}: {str(e)}")
                        
                        if not skip_errors:
                            raise
        
        except FileNotFoundError:
            raise Exception(f"CSV file not found: {csv_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
        
        return results


async def find_demo_classroom(session: AsyncSession) -> Optional[UUID]:
    """Find the AULA_TEA_DEMO classroom by name"""
    result = await session.execute(
        select(Classroom).where(Classroom.name == "AULA_TEA_DEMO")
    )
    classroom = result.scalar_one_or_none()
    return classroom.id if classroom else None


async def verify_embeddings(session: AsyncSession, classroom_id: UUID) -> Dict:
    """Verify that embeddings were generated for events"""
    from app.services.vector_store import VectorStore
    
    # Get all events for this classroom
    result = await session.execute(
        select(Event).where(Event.classroom_id == classroom_id)
    )
    events = result.scalars().all()
    
    if not events:
        return {"total_events": 0, "with_embeddings": 0, "percentage": 0.0}
    
    vector_store = VectorStore()
    
    # Check quality embeddings (primary)
    quality_count = vector_store.get_collection_count(classroom_id, "quality")
    
    # Check fast embeddings (optional)
    fast_count = vector_store.get_collection_count(classroom_id, "fast")
    
    total_events = len(events)
    with_embeddings = quality_count
    
    return {
        "total_events": total_events,
        "with_embeddings": with_embeddings,
        "quality_embeddings": quality_count,
        "fast_embeddings": fast_count,
        "percentage": (with_embeddings / total_events * 100) if total_events > 0 else 0.0
    }


async def main():
    """Main function to run the import"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import events from CSV file')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--skip-errors', action='store_true', default=True,
                       help='Continue importing even if some events fail (default: True)')
    parser.add_argument('--no-skip-errors', dest='skip_errors', action='store_false',
                       help='Stop importing on first error')
    parser.add_argument('--use-demo-classroom', action='store_true',
                       help='Automatically use AULA_TEA_DEMO classroom (overrides CSV classroom_id)')
    
    args = parser.parse_args()
    
    # Get database URL from settings or environment
    database_url = settings.database_url
    if not database_url:
        # Construct from individual settings
        postgres_user = os.getenv("POSTGRES_USER", "aulaplus")
        postgres_password = os.getenv("POSTGRES_PASSWORD", "dev_password_2024")
        postgres_db = os.getenv("POSTGRES_DB", "aulaplus_db")
        postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        database_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    # Create async engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("=" * 60)
    print("AULA+ Event Importer")
    print("=" * 60)
    print(f"CSV file: {args.csv_file}")
    print(f"Skip errors: {args.skip_errors}")
    print("=" * 60)
    print()
    
    async with async_session() as session:
        # Handle demo classroom option
        demo_classroom_id = None
        if args.use_demo_classroom:
            print("🔍 Looking for AULA_TEA_DEMO classroom...")
            demo_classroom_id = await find_demo_classroom(session)
            if not demo_classroom_id:
                print("❌ Error: AULA_TEA_DEMO classroom not found!")
                print("   Please run: python scripts/create_demo_classroom.py first")
                sys.exit(1)
            print(f"✅ Found AULA_TEA_DEMO classroom: {demo_classroom_id}")
            print()
        
        importer = EventImporter(session)
        
        try:
            # Import with optional demo classroom override
            results = await importer.import_from_csv(
                args.csv_file, 
                skip_errors=args.skip_errors,
                override_classroom_id=demo_classroom_id
            )
            
            print()
            print("=" * 60)
            print("IMPORT SUMMARY")
            print("=" * 60)
            print(f"Total rows processed: {results['total']}")
            print(f"✅ Successful: {results['successful']}")
            print(f"❌ Failed: {results['failed']}")
            
            if results['errors']:
                print()
                print("Errors:")
                for error in results['errors']:
                    print(f"  Row {error['row']}: {error['error']}")
            
            # Verify embeddings if import was successful
            if results['successful'] > 0:
                # Get classroom_id from results or use demo classroom
                classroom_id = demo_classroom_id
                if not classroom_id:
                    # Try to get from first successful event
                    # We'll need to track this in the import process
                    pass
                
                # Use classroom_id from results or demo classroom
                classroom_id = results.get("classroom_id") or demo_classroom_id
                
                if classroom_id:
                    print()
                    print("=" * 60)
                    print("EMBEDDING VERIFICATION")
                    print("=" * 60)
                    embedding_stats = await verify_embeddings(session, classroom_id)
                    print(f"Total events in database: {embedding_stats['total_events']}")
                    print(f"Events with quality embeddings: {embedding_stats['quality_embeddings']}")
                    print(f"Events with fast embeddings: {embedding_stats['fast_embeddings']}")
                    print(f"Embedding coverage: {embedding_stats['percentage']:.1f}%")
                    
                    if embedding_stats['percentage'] >= 95.0:
                        print("✅ Embeddings generated successfully!")
                    elif embedding_stats['percentage'] >= 80.0:
                        print("⚠️  Most embeddings generated, but some may be missing")
                    else:
                        print("❌ Warning: Many embeddings are missing")
                    print("=" * 60)
            
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            sys.exit(1)
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

