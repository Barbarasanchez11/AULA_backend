"""
LangGraph Service Package for AULA+

This package contains the LangGraph orchestration for recommendation generation.

Structure:
- state.py: State definition (TypedDict)
- nodes/: Individual node implementations
- graph.py: Graph construction
- service.py: Main service orchestrator
"""

from app.services.langgraph.service import LangGraphService
from app.services.langgraph.state import RecommendationState

__all__ = ["LangGraphService", "RecommendationState"]


