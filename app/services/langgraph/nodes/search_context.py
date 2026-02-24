"""
Node 2: Search for Context

This node:
- Searches for similar events using VectorStore
- Analyzes patterns using PatternAnalysisService
- Formats context for LLM
"""

from datetime import datetime
from app.services.langgraph.state import RecommendationState
from app.services.langgraph.services.context_service import ContextService
from app.services.langgraph.utils.async_utils import run_async

# Initialize service
context_service = ContextService()

def node_search_context(state: RecommendationState) -> RecommendationState:
    """
    Node 2: Search for context (similar events + patterns).
    
    - Searches for similar events using VectorStore (via ContextService)
    - Analyzes patterns using PatternAnalysisService (via ContextService)
    - Formats context for LLM
    
    Args:
        state: Current state with event data
        
    Returns:
        Updated state with context (similar_events, patterns, context_for_llm)
    """
    classroom_id = state.get("classroom_id")
    event_data = state.get("event_data")
    
    # Check if we have what we need
    if not classroom_id or not event_data:
        state["errors"].append({
            "node": "search_context",
            "severity": "error",
            "message": "Missing classroom_id or event_data in state",
            "timestamp": datetime.utcnow().isoformat()
        })
        return state
    
    try:
        # Call the orchestrator service
        # Using run_async because LangGraph nodes are sync but our service is async
        results = run_async(context_service.get_event_context(event_data, classroom_id))
        
        # Update state with results
        state["similar_events"] = results.get("similar_events", [])
        state["patterns"] = results.get("patterns", {})
        state["context_for_llm"] = results.get("context_for_llm", "")
        
        # Success metadata
        if "metadata" not in state:
            state["metadata"] = {}
        state["metadata"]["node_2_completed"] = True
        state["metadata"]["node_2_timestamp"] = datetime.utcnow().isoformat()
        state["metadata"]["similar_events_count"] = len(state["similar_events"])
        
    except Exception as e:
        state["errors"].append({
            "node": "search_context",
            "severity": "error",
            "message": f"Error gathering context: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return state



