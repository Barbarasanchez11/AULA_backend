from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.models.database import get_db
from app.models.models import Event, Classroom
from app.schemas.event import EventCreate, EventResponse, EventContext, EventUpdate
from app.schemas.enums import EventType, EventResult, MomentOfDay, DayOfWeek, SupportType

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

def event_model_to_response(event: Event) -> EventResponse:
    """Convert Event model to EventResponse schema"""
    return EventResponse(
        id=event.id,
        classroom_id=event.classroom_id,
        event_type=EventType(event.event_type),
        description=event.description,
        context=EventContext(
            moment_of_day=MomentOfDay(event.moment_of_day),
            day_of_week=DayOfWeek(event.day_of_week) if event.day_of_week else None,
            duration_minutes=event.duration_minutes
        ),
        supports=[SupportType(support) for support in event.supports],
        additional_supports=event.additional_supports,
        result=EventResult(event.result),
        observations=event.observations,
        timestamp=event.timestamp
    )

@router.get("/", response_model=List[EventResponse])
async def list_events(
    classroom_id: UUID = Query(..., description="ID of the classroom to filter events"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all events for a specific classroom.
    
    Returns a list of all events belonging to the specified classroom.
    Requires classroom_id as a query parameter.
    """
    # Validate that the classroom exists
    result = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Get all events for this classroom
    result = await db.execute(select(Event).where(Event.classroom_id == classroom_id))
    events = result.scalars().all()
    
    # Convert models to response schemas
    return [event_model_to_response(event) for event in events]

@router.get("/{id}", response_model=EventResponse)
async def get_event(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get a specific event by ID.
    
    Returns the event details if found, or 404 if not found.
    """
    result = await db.execute(select(Event).where(Event.id == id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event_model_to_response(event)

@router.put("/{id}", response_model=EventResponse)
async def update_event(id: UUID, event_update: EventUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update an event by ID.
    
    Updates only the provided fields and returns the updated event.
    Returns 404 if the event is not found.
    """
    result = await db.execute(select(Event).where(Event.id == id))
    db_event = result.scalar_one_or_none()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update only the fields that were provided
    update_data = event_update.model_dump(exclude_unset=True)
    
    # Handle context separately (nested object)
    if "context" in update_data and update_data["context"]:
        context_data = update_data.pop("context")
        if context_data.get("moment_of_day") is not None:
            moment = context_data["moment_of_day"]
            db_event.moment_of_day = moment.value if isinstance(moment, MomentOfDay) else moment
        if context_data.get("day_of_week") is not None:
            day = context_data["day_of_week"]
            db_event.day_of_week = day.value if isinstance(day, DayOfWeek) else day
        if context_data.get("duration_minutes") is not None:
            db_event.duration_minutes = context_data["duration_minutes"]
    
    # Handle enum fields
    if "event_type" in update_data and update_data["event_type"] is not None:
        event_type = update_data.pop("event_type")
        db_event.event_type = event_type.value if isinstance(event_type, EventType) else event_type
    
    if "result" in update_data and update_data["result"] is not None:
        result = update_data.pop("result")
        db_event.result = result.value if isinstance(result, EventResult) else result
    
    if "supports" in update_data and update_data["supports"] is not None:
        supports = update_data.pop("supports")
        db_event.supports = [
            support.value if isinstance(support, SupportType) else support 
            for support in supports
        ]
    
    # Update remaining fields
    for field, value in update_data.items():
        if value is not None:
            setattr(db_event, field, value)
    
    await db.commit()
    await db.refresh(db_event)
    
    return event_model_to_response(db_event)

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
    
    # Convert model to response schema
    return event_model_to_response(db_event)
