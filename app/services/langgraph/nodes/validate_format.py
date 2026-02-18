"""
Node 4: Validate and Format Recommendation

This node:
- Parses LLM response
- Validates against Pydantic schemas
- Calculates confidence
- Formats for database storage
"""

from datetime import datetime
from app.services.langgraph.state import RecommendationState


def node_validate_format(state: RecommendationState) -> RecommendationState:
    """
    Node 4: Validate and format recommendation.
    
    - Parses LLM response
    - Validates against Pydantic schemas
    - Calculates confidence
    - Formats for database storage
    
    Args:
        state: Current state with llm_response
        
    Returns:
        Updated state with recommendation and confidence
    """
    # TODO: Implement validation and formatting
    # - Parse LLM response
    # - Validate with Pydantic
    # - Calculate confidence
    # - Format for DB
    
    # Initialize metadata if not present
    if "metadata" not in state:
        state["metadata"] = {}
    state["metadata"]["timestamp_end"] = datetime.now()
    
    return state



