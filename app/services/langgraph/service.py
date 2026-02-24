"""
LangGraph Service for AULA+

Main service orchestrator for recommendation generation using LangGraph.
Coordinates all services and manages the graph execution.
"""

from typing import Dict, Any, Optional
from uuid import UUID

try:
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    HuggingFaceEndpoint = None

from app.config import settings
from app.services.vector_store import VectorStore
from app.services.pattern_analysis import PatternAnalysisService
from app.services.embeddingService import EmbeddingService
from app.services.langgraph.state import RecommendationState
from app.services.langgraph.graph import build_recommendation_graph


class LangGraphService:
    """
    Service for orchestrating recommendation generation using LangGraph.
    
    Manages the flow:
    1. Receive and validate event
    2. Search for context (similar events + patterns)
    3. Generate recommendation with LLM
    4. Validate and format recommendation
    """
    
    def __init__(self):
        """
        Initialize LangGraphService with required services and Groq client.
        
        Raises:
            ImportError: If LangGraph dependencies are not installed.
            ValueError: If GROQ_API_KEY is not configured.
        """
        if HuggingFaceEndpoint is None:
            raise ImportError(
                "LangGraph dependencies for HuggingFace are not installed. "
                "Install with: pip install langgraph langchain langchain-huggingface"
            )
        
        # Initialize services
        self.vector_store = VectorStore()
        self.pattern_service = PatternAnalysisService()
        self.embedding_service = EmbeddingService.get_instance()
        
        # Initialize HuggingFace LLM client
        if not settings.hf_api_key:
            raise ValueError("HF_API_KEY not found in configuration. Set it in .env file.")
        
        self.llm = HuggingFaceEndpoint(
            repo_id=settings.hf_model_id,
            huggingfacehub_api_token=settings.hf_api_key,
            temperature=settings.llm_temperature,
            max_new_tokens=settings.llm_max_tokens,
            task="text-generation",
            # Repetición y penalización opcional
            # repetition_penalty=1.1
        )
        
        # Initialize graph (will be built on first use)
        self._graph = None
    
    @property
    def graph(self):
        """Lazy-load the graph on first access."""
        if self._graph is None:
            self._graph = build_recommendation_graph(self.llm)
        return self._graph
    
    def generate_recommendation(
        self,
        classroom_id: UUID,
        event_id: Optional[UUID] = None,
        event_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a recommendation using the LangGraph workflow.
        
        Args:
            classroom_id: ID of the classroom
            event_id: Optional ID of existing event
            event_data: Optional data for new event
            
        Returns:
            Dict with recommendation and metadata
            
        Raises:
            ValueError: If both event_id and event_data are None
        """
        if event_id is None and event_data is None:
            raise ValueError("Either event_id or event_data must be provided")
        
        # Initialize state
        initial_state: RecommendationState = {
            "event_id": event_id,
            "classroom_id": classroom_id,
            "event_data": event_data,
            "similar_events": [],
            "patterns": {},
            "context_for_llm": None,
            "llm_response": None,
            "llm_metadata": None,
            "recommendation": None,
            "confidence": None,
            "errors": [],
            "metadata": {}
        }
        
        # Run graph
        final_state = self.graph.invoke(initial_state)
        
        return final_state

