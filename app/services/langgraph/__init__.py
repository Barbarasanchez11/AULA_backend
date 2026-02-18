"""
LangGraph Service Package for AULA+

This package contains the LangGraph orchestration for recommendation generation.

Structure:
- state.py: State definition (TypedDict)
- nodes/: Individual node implementations
- graph.py: Graph construction
- service.py: Main service orchestrator
"""

# Lazy imports to avoid loading heavy dependencies (PyTorch, sentence-transformers)
# when only importing nodes or state
from app.services.langgraph.state import RecommendationState

# LangGraphService is imported lazily to avoid loading all ML dependencies
# Import it explicitly when needed: from app.services.langgraph.service import LangGraphService
def _get_langgraph_service():
    """Lazy loader for LangGraphService"""
    from app.services.langgraph.service import LangGraphService
    return LangGraphService

__all__ = ["RecommendationState", "_get_langgraph_service"]



