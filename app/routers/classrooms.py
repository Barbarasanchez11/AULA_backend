from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.database import get_db
from app.models.models import Classroom
from app.schemas.classroom import ClassroomResponse

router = APIRouter(
    prefix="/classrooms",
    tags=["classrooms"]
)

@router.get("/", response_model=List[ClassroomResponse])
async def list_classrooms(db: AsyncSession = Depends(get_db)):
    """
    List all classrooms in the system.
    
    Returns a list of all classrooms with their basic information.
    """
    result = await db.execute(select(Classroom))
    classrooms = result.scalars().all()
    return classrooms

