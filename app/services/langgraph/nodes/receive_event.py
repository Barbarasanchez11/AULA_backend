"""
Node 1: Receive and Validate Event

This node:
- Validates that classroom_id exists
- If event_id exists, loads event from DB
- If event_data exists, validates it
- Prepares state for next node
"""

from typing import Dict, Any
from datetime import datetime
from app.services.langgraph.state import RecommendationState


def node_receive_event(state: RecommendationState) -> RecommendationState:
    """
    Node 1: Receive and validate event.
    
    - Validates that classroom_id exists
    - If event_id exists, loads event from DB
    - If event_data exists, validates it
    - Prepares state for next node
    
    Args:
        state: Current state with input data
        
    Returns:
        Updated state with validated event data
    """
    # TODO: Implement event reception and validation
    # - Validate classroom_id exists
    # - Load event from DB if event_id provided
    # - Validate event_data if provided
    # - Prepare state for next node
    
    # Initialize metadata and errors if not present
    if "metadata" not in state:
        state["metadata"] = {}
    state["metadata"]["timestamp_start"] = datetime.now()
    
    if "errors" not in state:
        state["errors"] = []
    
    return state


