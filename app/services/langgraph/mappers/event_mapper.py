from typing import Dict, Any
from app.models.models import Event

def event_model_to_dict(event: Event) -> Dict[str, Any]:
    """
    Convert an Event SQLAlchemy model to a dictionary for state.
    
    Args:
        event: Event SQLAlchemy model instance
        
    Returns:
        Dictionary with event data in the format expected by the state
    """
    return {
        "id": str(event.id),
        "classroom_id": str(event.classroom_id),
        "event_type": event.event_type,
        "description": event.description,
        "context": {
            "moment_of_day": event.moment_of_day,
            "day_of_week": event.day_of_week,
            "duration_minutes": event.duration_minutes
        },
        "supports": event.supports if event.supports else [],
        "additional_supports": event.additional_supports,
        "result": event.result,
        "observations": event.observations,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None
    }
