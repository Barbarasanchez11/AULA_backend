"""
Test script for semantic search functionality.

Tests semantic search with different query texts and evaluates if results make sense.
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.models import Event, Classroom
from app.services.embeddingService import EmbeddingService
from app.services.vector_store import VectorStore
from app.config import settings

# Use settings for database URL
DATABASE_URL = settings.database_url

async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def find_demo_classroom() -> UUID:
    """Find the AULA_TEA_DEMO classroom ID"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Classroom).where(Classroom.name == "AULA_TEA_DEMO")
        )
        classroom = result.scalar_one_or_none()
        if not classroom:
            raise ValueError("AULA_TEA_DEMO classroom not found. Run create_demo_classroom.py first.")
        return classroom.id


async def search_semantic(query_text: str, classroom_id: UUID, top_k: int = 3, model_type: str = "quality"):
    """
    Perform semantic search for events similar to the query text.
    
    Args:
        query_text: Text to search for
        classroom_id: ID of the classroom to search in
        top_k: Number of results to return
        model_type: Model to use ("fast" or "quality")
    
    Returns:
        List of similar events with scores
    """
    # Initialize services
    embedding_service = EmbeddingService.get_instance()
    vector_store = VectorStore()
    
    # Generate embedding for the query text
    query_embedding = embedding_service.generate_quality_embedding(query_text) if model_type == "quality" else embedding_service.generate_fast_embedding(query_text)
    
    # Search for similar events
    similar_results = vector_store.search_similar_events(
        classroom_id=classroom_id,
        query_embedding=query_embedding,
        top_k=top_k,
        model_type=model_type,
        min_similarity=0.0
    )
    
    # Get full event details from database
    async with AsyncSessionLocal() as session:
        events_with_scores = []
        for result in similar_results:
            event_id = UUID(result["event_id"])
            score = result["score"]
            
            # Get event from database
            db_result = await session.execute(
                select(Event).where(Event.id == event_id)
            )
            event = db_result.scalar_one_or_none()
            
            if event:
                events_with_scores.append({
                    "event": event,
                    "score": score
                })
        
        return events_with_scores


def format_event_summary(event: Event, score: float) -> str:
    """Format event information for display"""
    return f"""
  Score: {score:.3f}
  Type: {event.event_type}
  Description: {event.description}
  Moment: {event.moment_of_day}
  Result: {event.result}
  Supports: {', '.join(event.supports)}
  Observations: {event.observations or 'N/A'}
"""


async def test_search(query_text: str, classroom_id: UUID, query_name: str):
    """Test a single semantic search query"""
    print(f"\n{'='*70}")
    print(f"🔍 Search Query: '{query_text}'")
    print(f"{'='*70}")
    
    try:
        results = await search_semantic(query_text, classroom_id, top_k=3, model_type="quality")
        
        if not results:
            print("❌ No similar events found.")
            return False
        
        print(f"\n✅ Found {len(results)} similar events:\n")
        
        for idx, result in enumerate(results, 1):
            event = result["event"]
            score = result["score"]
            print(f"--- Result {idx} ---")
            print(format_event_summary(event, score))
        
        # Evaluate if results make sense
        print(f"\n📊 Evaluation:")
        print(f"   Query: '{query_text}'")
        print(f"   Results: {len(results)} events found")
        
        # Check if results are relevant
        relevant_count = 0
        for result in results:
            event = result["event"]
            description_lower = event.description.lower()
            observations_lower = (event.observations or "").lower()
            query_lower = query_text.lower()
            
            # Check if query terms appear in description or observations
            query_terms = query_lower.split()
            matches = sum(1 for term in query_terms if term in description_lower or term in observations_lower)
            
            if matches > 0 or result["score"] > 0.5:
                relevant_count += 1
        
        relevance_percentage = (relevant_count / len(results)) * 100 if results else 0
        print(f"   Relevance: {relevant_count}/{len(results)} events seem relevant ({relevance_percentage:.0f}%)")
        
        if relevance_percentage >= 66:
            print(f"   ✅ Results make sense!")
        elif relevance_percentage >= 33:
            print(f"   ⚠️  Some results may not be very relevant")
        else:
            print(f"   ❌ Results don't seem very relevant")
        
        return relevance_percentage >= 66
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function to run all semantic search tests"""
    print("="*70)
    print("🧪 Semantic Search Test Script")
    print("="*70)
    
    try:
        # Find demo classroom
        print("\n🔍 Looking for AULA_TEA_DEMO classroom...")
        classroom_id = await find_demo_classroom()
        print(f"✅ Found classroom: {classroom_id}")
        
        # Test queries
        test_queries = [
            ("sobrecarga sensorial", "Sensory overload"),
            ("problemas de comunicación", "Communication problems"),
            ("cambios de rutina", "Routine changes"),
        ]
        
        print(f"\n📝 Running {len(test_queries)} semantic search tests...")
        print(f"   Model: quality (mpnet)")
        print(f"   Top K: 3 events per query")
        
        results_summary = []
        for query_text, query_name in test_queries:
            success = await test_search(query_text, classroom_id, query_name)
            results_summary.append((query_text, success))
        
        # Final summary
        print(f"\n{'='*70}")
        print("📊 FINAL SUMMARY")
        print(f"{'='*70}")
        
        for query_text, success in results_summary:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: '{query_text}'")
        
        passed = sum(1 for _, success in results_summary if success)
        total = len(results_summary)
        print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        
        if passed == total:
            print("\n🎉 All semantic searches are working correctly!")
        else:
            print("\n⚠️  Some searches may need adjustment.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

