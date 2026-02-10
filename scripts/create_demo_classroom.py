#!/usr/bin/env python3
"""
Script to create a demo classroom for testing

Creates a new classroom named "AULA_TEA_DEMO" in the database.
Uses the existing database configuration from the project.
"""

import asyncio
import sys
import os
from pathlib import Path
from uuid import UUID

# Add parent directory to path to import app modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Change to project root to ensure .env is found
os.chdir(project_root)

try:
    from app.models.database import AsyncSessionLocal
    from app.models.models import Classroom
    from sqlalchemy import select
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("\nPlease ensure:")
    print("  1. You are in the project root directory")
    print("  2. Virtual environment is activated")
    print("  3. Dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


async def create_demo_classroom():
    """Create a demo classroom named 'AULA_TEA_DEMO'"""
    
    print("🎓 Creating demo classroom 'AULA_TEA_DEMO'...")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if classroom already exists
            result = await db.execute(
                select(Classroom).where(Classroom.name == "AULA_TEA_DEMO")
            )
            existing_classroom = result.scalar_one_or_none()
            
            if existing_classroom:
                print(f"\n⚠️  Classroom 'AULA_TEA_DEMO' already exists!")
                print(f"   ID: {existing_classroom.id}")
                print(f"   Type: {existing_classroom.type}")
                print(f"   Created at: {existing_classroom.created_at}")
                print("\n✅ Using existing classroom.")
                return existing_classroom.id
            
            # Create new classroom
            demo_classroom = Classroom(
                name="AULA_TEA_DEMO",
                type="TEA",
                extra_metadata={"demo": True, "purpose": "Testing and demonstration"}
            )
            
            db.add(demo_classroom)
            await db.commit()
            await db.refresh(demo_classroom)
            
            print(f"\n✅ Classroom created successfully!")
            print(f"   ID: {demo_classroom.id}")
            print(f"   Name: {demo_classroom.name}")
            print(f"   Type: {demo_classroom.type}")
            print(f"   Created at: {demo_classroom.created_at}")
            print(f"   Metadata: {demo_classroom.extra_metadata}")
            print("\n" + "="*60)
            print("✅ Demo classroom ready to use!")
            print("="*60 + "\n")
            
            return demo_classroom.id
            
        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error creating classroom: {str(e)}")
            print("\nPlease ensure:")
            print("  1. PostgreSQL is running")
            print("  2. Database connection is configured correctly in .env")
            print("  3. Database and tables exist (run migrations if needed)")
            sys.exit(1)


async def verify_classroom(classroom_id: UUID):
    """Verify that the classroom was created correctly"""
    
    print("\n🔍 Verifying classroom creation...")
    
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Classroom).where(Classroom.id == classroom_id)
            )
            classroom = result.scalar_one_or_none()
            
            if not classroom:
                print("❌ Error: Classroom not found in database!")
                return False
            
            print(f"✅ Verification successful!")
            print(f"   Classroom ID: {classroom.id}")
            print(f"   Name: {classroom.name}")
            print(f"   Type: {classroom.type}")
            print(f"   Created at: {classroom.created_at}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying classroom: {str(e)}")
            return False


async def main():
    """Main function"""
    try:
        # Create classroom
        classroom_id = await create_demo_classroom()
        
        # Verify creation
        verified = await verify_classroom(classroom_id)
        
        if verified:
            print(f"\n💡 Next steps:")
            print(f"   1. Use this classroom ID for importing events:")
            print(f"      {classroom_id}")
            print(f"   2. Update CLASSROOM_ID in generate_synthetic_data.py if needed")
            print(f"   3. Import events: python scripts/import_events_from_csv.py synthetic_events_tea.csv\n")
            sys.exit(0)
        else:
            print("\n❌ Verification failed. Please check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

