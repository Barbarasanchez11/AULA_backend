from typing import Optional
from uuid import UUID
from sqlalchemy import select
from app.models.database import AsyncSessionLocal
from app.models.models import Classroom

async def validate_classroom_exists(classroom_id: UUID) -> tuple[bool, Optional[str]]:
    """
    Validate that a classroom exists in the database.
    
    Args:
        classroom_id: UUID of the classroom to validate
        
    Returns:
        Tuple of (exists: bool, error_message: Optional[str])
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Classroom).where(Classroom.id == classroom_id)
            )
            classroom = result.scalar_one_or_none()
            
            if classroom is None:
                return False, f"Classroom with id {classroom_id} not found"
            
            return True, None
            
    except Exception as e:
        return False, f"Database error while validating classroom: {str(e)}"
