from typing import Dict, Any, Optional
from pydantic import ValidationError
from app.schemas.event import EventBase

def validate_event_data(event_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that event_data has the required fields and correct structure using Pydantic.
    
    Args:
        event_data: Dictionary with event data to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    try:
        # Use Pydantic to validate the structure, types, and constraints
        EventBase(**event_data)
        return True, None
    except ValidationError as e:
        # Format Pydantic errors into a more readable string
        error_messages = []
        for error in e.errors():
            loc = " -> ".join(str(i) for i in error["loc"])
            msg = error["msg"]
            error_messages.append(f"{loc}: {msg}")
        
        return False, "; ".join(error_messages)
    except Exception as e:
        return False, f"Unexpected validation error: {str(e)}"
