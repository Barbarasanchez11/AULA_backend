from app.models.database import engine, Base
from app.models.models import Classroom, Event, Recommendation

async def init_db():
    async with engine.begin() as conn:
        # Warning: This will drop all tables! Useful for dev only.
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
