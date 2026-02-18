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
"""

from datetime import datetime
from app.services.langgraph.state import RecommendationState
from app.services.langgraph.utils.async_utils import run_async
from app.services.langgraph.validators.classroom_validator import validate_classroom_exists
from app.services.langgraph.validators.event_validator import validate_event_data
from app.services.langgraph.repositories.event_repository import load_event_from_db


def node_receive_event(state: RecommendationState) -> RecommendationState:
    """
    Node 1: Receive and validate event.
    
    This is the entry point of the LangGraph recommendation flow. It performs:
    1. Validates that classroom_id exists in the database
    2. If event_id is provided, loads the event from the database
    3. If event_data is provided, validates its structure
    4. Prepares the state with validated event_data for subsequent nodes
    5. Initializes metadata and error tracking
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
    classroom_exists, classroom_error = run_async(validate_classroom_exists(classroom_id))
    
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
        loaded_event_data, load_error = run_async(
            load_event_from_db(event_id, classroom_id)
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
        is_valid, validation_error = validate_event_data(event_data)
        
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
