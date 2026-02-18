"""
Node 3: Generate Recommendation with LLM

This node:
- Builds prompt with context
- Calls Groq LLM
- Stores response and metadata
"""

from app.services.langgraph.state import RecommendationState


def node_generate_llm(state: RecommendationState, llm) -> RecommendationState:
    """
    Node 3: Generate recommendation with LLM.
    
    - Builds prompt with context
    - Calls Groq LLM
    - Stores response
    
    Args:
        state: Current state with context_for_llm
        llm: LLM client (ChatGroq instance)
        
    Returns:
        Updated state with llm_response and llm_metadata
    """
    # TODO: Implement LLM generation
    # - Build prompt from context
    # - Call llm.invoke()
    # - Store response and metadata
    
    return state



