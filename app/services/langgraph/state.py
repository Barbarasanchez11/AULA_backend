"""
State Definition for LangGraph Recommendation Flow

Defines the TypedDict that flows between nodes in the recommendation generation graph.
"""

from typing import List, Dict, Any, Optional, TypedDict
from uuid import UUID


class RecommendationState(TypedDict):
    """
    State that flows between nodes in the LangGraph.
    
    This TypedDict defines the structure of data that passes through the graph.
    All fields are optional except where noted, to allow incremental building.
    """
    # === INPUT (filled at start) ===
    event_id: Optional[UUID]              # ID of event if it already exists in DB
    classroom_id: UUID                   # ID of classroom (required)
    event_data: Optional[Dict[str, Any]]  # Event data if it's a new event
    
    # === CONTEXT (filled in Node 2) ===
    similar_events: List[Dict[str, Any]]  # Similar events found
    patterns: Dict[str, Any]              # Detected patterns (temporal, effectiveness, clustering)
    context_for_llm: Optional[str]        # Formatted context for LLM
    
    # === GENERATION (filled in Node 3) ===
    llm_response: Optional[str]           # Raw LLM response
    llm_metadata: Optional[Dict[str, Any]] # LLM call metadata (tokens, time, etc.)
    
    # === OUTPUT (filled in Node 4) ===
    recommendation: Optional[Dict[str, Any]] # Validated and formatted recommendation
    confidence: Optional[str]              # Calculated confidence (ALTA/MEDIA/BAJA)
    
    # === CONTROL ===
    errors: List[Dict[str, Any]]          # Errors encountered (with severity)
    metadata: Dict[str, Any]              # Process metadata (timestamps, etc.)

