from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select
from app.models.database import AsyncSessionLocal
from app.models.models import Event
from app.services.langgraph.mappers.event_mapper import event_model_to_dict

async def load_event_from_db(event_id: UUID, classroom_id: UUID) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Load an event from the database by ID and validate it belongs to the classroom.
    
    Args:
        event_id: UUID of the event to load
        classroom_id: UUID of the classroom (for validation)
        
    Returns:
        Tuple of (event_data: Optional[Dict], error_message: Optional[str])
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Event).where(
                    Event.id == event_id,
                    Event.classroom_id == classroom_id
                )
            )
            event = result.scalar_one_or_none()
            
            if event is None:
                return None, f"Event with id {event_id} not found or does not belong to classroom {classroom_id}"
            
            # Convert Event model to dictionary
            event_dict = event_model_to_dict(event)
            return event_dict, None
            
    except Exception as e:
        return None, f"Database error while loading event: {str(e)}"
