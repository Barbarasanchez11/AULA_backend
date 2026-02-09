"""
Embedding Service for AULA+

This service manages the loading and generation of embeddings using a hybrid approach:
- Fast model (distiluse): For quick searches and previews
- Quality model (mpnet): For clustering, historical analysis, and recommendation generation

Uses Singleton pattern to ensure only one instance exists and models are loaded once.
"""

from typing import List, Optional, Literal
from uuid import UUID

# Optional imports - will be available when dependencies are installed
try:
    import numpy as np
except ImportError:
    np = None  # Will be available when numpy is installed

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None  # Will be available when sentence-transformers is installed


class EmbeddingService:
    """
    Service for generating embeddings from events using sentence-transformers models.
    
    Implements Singleton pattern to ensure models are loaded only once in memory.
    Uses lazy loading to avoid loading models until they are first needed.
    """
    
    # Class variables (shared across all instances)
    _instance = None
    _fast_model = None
    _quality_model = None
    _fast_model_loaded = False
    _quality_model_loaded = False
    
    def __init__(self):
        """
        Initialize EmbeddingService instance.
        
        Raises:
            Exception: If an instance already exists (Singleton pattern).
        """
        if EmbeddingService._instance is not None:
            raise Exception("EmbeddingService ya está inicializado. Usa get_instance() en su lugar.")
        EmbeddingService._instance = self
    
    @staticmethod
    def get_instance() -> 'EmbeddingService':
        """
        Get or create the singleton instance of EmbeddingService.
        
        Returns:
            EmbeddingService: The unique instance of the service.
        """
        if EmbeddingService._instance is None:
            EmbeddingService()
        return EmbeddingService._instance
    
    def _load_fast_model(self) -> None:
        """
        Load the fast embedding model (distiluse-base-multilingual-cased-v2).
        
        This method uses lazy loading - the model is only loaded when first needed.
        """
        raise NotImplementedError("_load_fast_model() will be implemented in next subtask")
    
    def _load_quality_model(self) -> None:
        """
        Load the quality embedding model (paraphrase-multilingual-mpnet-base-v2).
        
        This method uses lazy loading - the model is only loaded when first needed.
        """
        raise NotImplementedError("_load_quality_model() will be implemented in next subtask")
    
    def combine_event_text(
        self,
        event_type: str,
        description: str,
        moment_of_day: str,
        day_of_week: Optional[str],
        supports: List[str],
        result: str,
        observations: Optional[str] = None
    ) -> str:
        """
        Combine all event fields into a single text string for embedding generation.
        
        Args:
            event_type: Type of the event (e.g., "TRANSICION")
            description: Description of the event
            moment_of_day: Moment of day (e.g., "mañana")
            day_of_week: Day of week (optional, e.g., "lunes")
            supports: List of supports used
            result: Result of the event (e.g., "EXITOSO")
            observations: Optional observations
            
        Returns:
            str: Combined text representation of the event
        """
        raise NotImplementedError("combine_event_text() will be implemented in next subtask")
    
    def generate_fast_embedding(self, text: str):
        """
        Generate embedding using the fast model (distiluse).
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            np.ndarray: Embedding vector (512 dimensions)
        """
        raise NotImplementedError("generate_fast_embedding() will be implemented in next subtask")
    
    def generate_quality_embedding(self, text: str):
        """
        Generate embedding using the quality model (mpnet).
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            np.ndarray: Embedding vector (768 dimensions)
        """
        raise NotImplementedError("generate_quality_embedding() will be implemented in next subtask")
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        model_type: Literal["fast", "quality"] = "quality"
    ):
        """
        Generate embeddings for multiple texts in batch (more efficient).
        
        Args:
            texts: List of texts to generate embeddings for
            model_type: Which model to use ("fast" or "quality")
            
        Returns:
            np.ndarray: Array of embeddings (shape: [num_texts, embedding_dim])
        """
        raise NotImplementedError("generate_embeddings_batch() will be implemented in next subtask")
    
    def generate_event_embedding(
        self,
        event_type: str,
        description: str,
        moment_of_day: str,
        day_of_week: Optional[str],
        supports: List[str],
        result: str,
        observations: Optional[str] = None,
        model_type: Literal["fast", "quality"] = "quality"
    ):
        """
        High-level method to generate embedding for a complete event.
        
        This method combines the event text and generates the embedding in one call.
        
        Args:
            event_type: Type of the event
            description: Description of the event
            moment_of_day: Moment of day
            day_of_week: Day of week (optional)
            supports: List of supports used
            result: Result of the event
            observations: Optional observations
            model_type: Which model to use ("fast" or "quality")
            
        Returns:
            np.ndarray: Embedding vector
        """
        raise NotImplementedError("generate_event_embedding() will be implemented in next subtask")

