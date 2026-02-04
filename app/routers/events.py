from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.database import get_db
from app.models.models import Event, Classroom
from app.schemas.event import EventCreate, EventResponse

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new event.
    
    Creates a new pedagogical event for a classroom.
    Validates that the classroom exists before creating the event.
    """
    # Validate that the classroom exists
    result = await db.execute(select(Classroom).where(Classroom.id == event.classroom_id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Convert EventContext to separate fields
    # Convert List[SupportType] to JSON array of strings
    db_event = Event(
        classroom_id=event.classroom_id,
        event_type=event.event_type.value,
        description=event.description,
        moment_of_day=event.context.moment_of_day.value,
        day_of_week=event.context.day_of_week.value if event.context.day_of_week else None,
        duration_minutes=event.context.duration_minutes,
        supports=[support.value for support in event.supports],
        additional_supports=event.additional_supports,
        result=event.result.value,
        observations=event.observations
    )
    
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    
    return db_event
