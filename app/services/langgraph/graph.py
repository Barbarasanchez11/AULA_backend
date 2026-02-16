"""
LangGraph Graph Construction

Builds and configures the StateGraph for recommendation generation flow.
"""

from typing import Optional

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    StateGraph = None
    END = None

from app.services.langgraph.state import RecommendationState
from app.services.langgraph.nodes import (
    node_receive_event,
    node_search_context,
    node_generate_llm,
    node_validate_format
)


def build_recommendation_graph(llm) -> StateGraph:
    """
    Build the LangGraph StateGraph with all nodes and edges.
    
    Args:
        llm: LLM client (ChatGroq instance) to pass to generate_llm node
        
    Returns:
        StateGraph: Configured graph ready to use.
        
    Raises:
        ImportError: If LangGraph dependencies are not installed.
    """
    if StateGraph is None or END is None:
        raise ImportError(
            "LangGraph dependencies are not installed. "
            "Install with: pip install langgraph langchain langchain-groq"
        )
    
    # Create StateGraph
    workflow = StateGraph(RecommendationState)
    
    # Add nodes
    workflow.add_node("receive_event", node_receive_event)
    workflow.add_node("search_context", node_search_context)
    
    # For generate_llm, we need to pass llm, so we create a wrapper
    def generate_llm_wrapper(state: RecommendationState) -> RecommendationState:
        return node_generate_llm(state, llm)
    
    workflow.add_node("generate_llm", generate_llm_wrapper)
    workflow.add_node("validate_format", node_validate_format)
    
    # Define edges (flow)
    workflow.set_entry_point("receive_event")
    workflow.add_edge("receive_event", "search_context")
    workflow.add_edge("search_context", "generate_llm")
    workflow.add_edge("generate_llm", "validate_format")
    workflow.add_edge("validate_format", END)
    
    # Compile graph
    graph = workflow.compile()
    return graph

