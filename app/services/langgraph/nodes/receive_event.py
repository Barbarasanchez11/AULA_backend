"""
Node 1: Receive and Validate Event

This node is the entry point of the LangGraph recommendation flow.
It validates inputs and loads/validates event data to prepare the state for subsequent nodes.

Responsibilities:
- Validates that classroom_id exists in the database
- If event_id is provided, loads the event from the database
- If event_data is provided, validates its structure and required fields
- Converts Event model to dictionary format for state
- Initializes metadata and error tracking
- Handles errors gracefully by adding them to state["errors"]

Architecture Notes:
- This node is synchronous (required by LangGraph)
- Uses asyncio.run() to execute async database operations
- Uses AsyncSessionLocal for database access
- Follows singleton pattern for database session management

Error Handling:
- Non-critical errors are added to state["errors"] and processing continues
- Critical errors (missing classroom, invalid event) stop the flow
- All errors include severity level and descriptive messages
"""

from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.langgraph.state import RecommendationState
from app.models.database import AsyncSessionLocal
from app.models.models import Classroom, Event
from app.schemas.enums import EventType, EventResult, MomentOfDay, DayOfWeek, SupportType


def _run_async(coro):
    """
    Helper function to run async code from sync context.
    
    Handles both cases:
    - No event loop running: uses asyncio.run()
    - Event loop already running: uses nest_asyncio to allow nested loops
    
    Args:
        coro: Coroutine to run
        
    Returns:
        Result of the coroutine
    """
    try:
        # Try to get running event loop
        loop = asyncio.get_running_loop()
        # If we're here, there's a running loop
        # Use nest_asyncio to allow nested event loops
        try:
            import nest_asyncio
            nest_asyncio.apply()
            # Now we can use asyncio.run() even with a running loop
            return asyncio.run(coro)
        except ImportError:
            raise RuntimeError(
                "nest_asyncio is required when running async code from sync context "
                "within an existing event loop. Install with: pip install nest-asyncio"
            )
    except RuntimeError:
        # No event loop running, safe to use asyncio.run()
        return asyncio.run(coro)


async def _validate_classroom_exists(classroom_id: UUID) -> tuple[bool, Optional[str]]:
    """
    Validate that a classroom exists in the database.
    
    Args:
        classroom_id: UUID of the classroom to validate
        
    Returns:
        Tuple of (exists: bool, error_message: Optional[str])
        - If exists: (True, None)
        - If not exists: (False, error_message)
        - If database error: (False, error_message)
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


async def _load_event_from_db(event_id: UUID, classroom_id: UUID) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Load an event from the database by ID and validate it belongs to the classroom.
    
    Args:
        event_id: UUID of the event to load
        classroom_id: UUID of the classroom (for validation)
        
    Returns:
        Tuple of (event_data: Optional[Dict], error_message: Optional[str])
        - If found: (event_dict, None)
        - If not found: (None, error_message)
        - If database error: (None, error_message)
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
            event_dict = _event_model_to_dict(event)
            return event_dict, None
            
    except Exception as e:
        return None, f"Database error while loading event: {str(e)}"


def _event_model_to_dict(event: Event) -> Dict[str, Any]:
    """
    Convert an Event SQLAlchemy model to a dictionary for state.
    
    This function extracts all relevant fields from the Event model and formats them
    as a dictionary that matches the structure expected by the state and subsequent nodes.
    
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


def _validate_event_data(event_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that event_data has the required fields and correct structure.
    
    Validates:
    - Required fields: event_type, description, context, supports, result
    - Context structure: moment_of_day (required), day_of_week (optional), duration_minutes (optional)
    - Field types and constraints
    
    Args:
        event_data: Dictionary with event data to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
        - If valid: (True, None)
        - If invalid: (False, error_message)
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


def node_receive_event(state: RecommendationState) -> RecommendationState:
    """
    Node 1: Receive and validate event.
    
    This is the entry point of the LangGraph recommendation flow. It performs:
    1. Validates that classroom_id exists in the database
    2. If event_id is provided, loads the event from the database
    3. If event_data is provided, validates its structure
    4. Prepares the state with validated event_data for subsequent nodes
    5. Initializes metadata and error tracking
    
    Flow:
    - Validates classroom_id (required)
    - If event_id exists: loads event from DB and converts to dict
    - If event_data exists: validates structure
    - If both exist: event_id takes priority
    - If neither exists: adds error to state
    
    Error Handling:
    - Non-critical errors are added to state["errors"] with severity "warning"
    - Critical errors (missing classroom, invalid event) are added with severity "error"
    - Processing continues even with warnings, but stops with critical errors
    
    Args:
        state: Current state with input data (must contain classroom_id and either event_id or event_data)
        
    Returns:
        Updated state with:
        - event_data: Dictionary with validated event data (if successful)
        - metadata: Initialized with timestamp_start
        - errors: List of errors encountered (if any)
        
    Raises:
        RuntimeError: If asyncio.run() fails (should not happen in normal operation)
    """
    # Initialize metadata and errors if not present
    if "metadata" not in state:
        state["metadata"] = {}
    state["metadata"]["timestamp_start"] = datetime.utcnow().isoformat()
    
    if "errors" not in state:
        state["errors"] = []
    
    # Extract inputs
    classroom_id = state.get("classroom_id")
    event_id = state.get("event_id")
    event_data = state.get("event_data")
    
    # Validate classroom_id exists
    if classroom_id is None:
        state["errors"].append({
            "node": "receive_event",
            "severity": "error",
            "message": "classroom_id is required but was not provided",
            "timestamp": datetime.utcnow().isoformat()
        })
        return state
    
    # Validate classroom exists in database
    classroom_exists, classroom_error = _run_async(_validate_classroom_exists(classroom_id))
    
    if not classroom_exists:
        state["errors"].append({
            "node": "receive_event",
            "severity": "error",
            "message": classroom_error or "Classroom validation failed",
            "timestamp": datetime.utcnow().isoformat()
        })
        return state
    
    # Determine which data source to use (event_id takes priority)
    if event_id is not None:
        # Load event from database
        loaded_event_data, load_error = _run_async(
            _load_event_from_db(event_id, classroom_id)
        )
        
        if load_error:
            state["errors"].append({
                "node": "receive_event",
                "severity": "error",
                "message": load_error,
                "timestamp": datetime.utcnow().isoformat()
            })
            return state
        
        # Successfully loaded event
        state["event_data"] = loaded_event_data
        state["metadata"]["event_source"] = "database"
        state["metadata"]["event_id"] = str(event_id)
        
    elif event_data is not None:
        # Validate event_data structure
        is_valid, validation_error = _validate_event_data(event_data)
        
        if not is_valid:
            state["errors"].append({
                "node": "receive_event",
                "severity": "error",
                "message": validation_error or "Event data validation failed",
                "timestamp": datetime.utcnow().isoformat()
            })
            return state
        
        # Ensure event_data has classroom_id
        if "classroom_id" not in event_data:
            event_data["classroom_id"] = str(classroom_id)
        
        # Successfully validated event_data
        state["event_data"] = event_data
        state["metadata"]["event_source"] = "input"
        
    else:
        # Neither event_id nor event_data provided
        state["errors"].append({
            "node": "receive_event",
            "severity": "error",
            "message": "Either event_id or event_data must be provided",
            "timestamp": datetime.utcnow().isoformat()
        })
        return state
    
    # Success: event_data is ready for next node
    state["metadata"]["node_1_completed"] = True
    state["metadata"]["node_1_timestamp"] = datetime.utcnow().isoformat()
    
    return state



