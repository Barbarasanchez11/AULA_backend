from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.models.database import get_db
from app.models.models import Classroom
from app.schemas.classroom import ClassroomResponse, ClassroomCreate, ClassroomUpdate

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

@router.post("/", response_model=ClassroomResponse, status_code=201)
async def create_classroom(classroom: ClassroomCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new classroom.
    
    Creates a new classroom with the provided data and returns the created classroom.
    """
    db_classroom = Classroom(
        name=classroom.name,
        type=classroom.type,
        extra_metadata=classroom.extra_metadata or {}
    )
    
    db.add(db_classroom)
    await db.commit()
    await db.refresh(db_classroom)
    
    return db_classroom

@router.put("/{id}", response_model=ClassroomResponse)
async def update_classroom(id: UUID, classroom_update: ClassroomUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update a classroom by ID.
    
    Updates only the provided fields and returns the updated classroom.
    Returns 404 if the classroom is not found.
    """
    result = await db.execute(select(Classroom).where(Classroom.id == id))
    db_classroom = result.scalar_one_or_none()
    
    if not db_classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Update only the fields that were provided
    update_data = classroom_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_classroom, field, value)
    
    await db.commit()
    await db.refresh(db_classroom)
    
    return db_classroom

