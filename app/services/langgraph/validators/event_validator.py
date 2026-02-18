from typing import Dict, Any, Optional
from app.schemas.enums import EventType, EventResult, MomentOfDay, DayOfWeek

def validate_event_data(event_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that event_data has the required fields and correct structure.
    
    Args:
        event_data: Dictionary with event data to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    # Check required top-level fields
    required_fields = ["event_type", "description", "context", "supports", "result"]
    for field in required_fields:
        if field not in event_data:
            return False, f"Missing required field: {field}"
    
    # Validate event_type
    try:
        EventType(event_data["event_type"])
    except (ValueError, KeyError):
        return False, f"Invalid event_type: {event_data.get('event_type')}. Must be one of: {[e.value for e in EventType]}"
    
    # Validate description
    description = event_data.get("description", "")
    if not isinstance(description, str) or len(description.strip()) < 10:
        return False, "description must be a non-empty string with at least 10 characters"
    
    # Validate context structure
    context = event_data.get("context", {})
    if not isinstance(context, dict):
        return False, "context must be a dictionary"
    
    if "moment_of_day" not in context:
        return False, "context.moment_of_day is required"
    
    try:
        MomentOfDay(context["moment_of_day"])
    except (ValueError, KeyError):
        return False, f"Invalid moment_of_day: {context.get('moment_of_day')}. Must be one of: {[m.value for m in MomentOfDay]}"
    
    # Validate day_of_week if provided
    if "day_of_week" in context and context["day_of_week"] is not None:
        try:
            DayOfWeek(context["day_of_week"])
        except (ValueError, KeyError):
            return False, f"Invalid day_of_week: {context.get('day_of_week')}. Must be one of: {[d.value for d in DayOfWeek]}"
    
    # Validate supports
    supports = event_data.get("supports", [])
    if not isinstance(supports, list) or len(supports) == 0:
        return False, "supports must be a non-empty list"
    
    # Validate result
    try:
        EventResult(event_data["result"])
    except (ValueError, KeyError):
        return False, f"Invalid result: {event_data.get('result')}. Must be one of: {[r.value for r in EventResult]}"
    
    return True, None
