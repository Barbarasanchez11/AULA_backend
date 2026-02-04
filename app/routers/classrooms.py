from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

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

@router.get("/{id}", response_model=ClassroomResponse)
async def get_classroom(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get a specific classroom by ID.
    
    Returns the classroom details if found, or 404 if not found.
    """
    result = await db.execute(select(Classroom).where(Classroom.id == id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    return classroom

