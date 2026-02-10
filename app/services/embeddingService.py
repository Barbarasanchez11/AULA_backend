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
            raise Exception("EmbeddingService is already initialized. Use get_instance() instead.")
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
        If the model is already loaded, this method does nothing.
        
        Raises:
            ImportError: If sentence_transformers is not installed.
            Exception: If the model cannot be loaded.
        """
        # Check if already loaded
        if EmbeddingService._fast_model_loaded:
            return
        
        # Check if SentenceTransformer is available
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers no está instalado. "
                "Instálalo con: pip install sentence-transformers"
            )
        
        try:
            # Load the fast model
            model_name = "distiluse-base-multilingual-cased-v2"
            EmbeddingService._fast_model = SentenceTransformer(model_name)
            EmbeddingService._fast_model_loaded = True
        except Exception as e:
            raise Exception(
                f"Error al cargar el modelo rápido '{model_name}': {str(e)}. "
                "Asegúrate de tener conexión a internet para descargar el modelo."
            ) from e
    
    def _load_quality_model(self) -> None:
        """
        Load the quality embedding model (paraphrase-multilingual-mpnet-base-v2).
        
        This method uses lazy loading - the model is only loaded when first needed.
        If the model is already loaded, this method does nothing.
        
        Raises:
            ImportError: If sentence_transformers is not installed.
            Exception: If the model cannot be loaded.
        """
        # Check if already loaded
        if EmbeddingService._quality_model_loaded:
            return
        
        # Check if SentenceTransformer is available
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers no está instalado. "
                "Instálalo con: pip install sentence-transformers"
            )
        
        try:
            # Load the quality model
            model_name = "paraphrase-multilingual-mpnet-base-v2"
            EmbeddingService._quality_model = SentenceTransformer(model_name)
            EmbeddingService._quality_model_loaded = True
        except Exception as e:
            raise Exception(
                f"Error al cargar el modelo de calidad '{model_name}': {str(e)}. "
                "Asegúrate de tener conexión a internet para descargar el modelo."
            ) from e
    
    def combine_event_text(
        self,
        event_type: str,
        description: str,
        moment_of_day: str,
        day_of_week: Optional[str],
        supports: List[str],
        result: str,
        additional_supports: Optional[str] = None,
        observations: Optional[str] = None
    ) -> str:
        """
        Combine all event fields into a single text string for embedding generation.
        
        This method creates a structured text representation that captures all semantic
        information from the event, which is then used to generate embeddings.
        
        Args:
            event_type: Type of the event (e.g., "TRANSICION")
            description: Description of the event
            moment_of_day: Moment of day (e.g., "mañana")
            day_of_week: Day of week (optional, e.g., "lunes")
            supports: List of supports used (predefined supports)
            result: Result of the event (e.g., "EXITOSO")
            additional_supports: Additional supports in free text (optional)
            observations: Optional observations
            
        Returns:
            str: Combined text representation of the event
        """
        # Start with event type and description (core information)
        parts = [
            f"{event_type}. {description}."
        ]
        
        # Add temporal context
        context_parts = [f"Momento: {moment_of_day}"]
        if day_of_week:
            context_parts.append(f"Día: {day_of_week}")
        parts.append(" ".join(context_parts) + ".")
        
        # Add supports
        supports_text = ", ".join(supports)
        if additional_supports and additional_supports.strip():
            supports_text += f". {additional_supports.strip()}"
        parts.append(f"Apoyos utilizados: {supports_text}.")
        
        # Add result
        parts.append(f"Resultado: {result}.")
        
        # Add observations if present
        if observations and observations.strip():
            parts.append(f"Observaciones: {observations.strip()}.")
        
        # Join all parts with spaces
        return " ".join(parts)
    
    def generate_fast_embedding(self, text: str):
        """
        Generate embedding using the fast model (distiluse).
        
        This method uses lazy loading - the model is loaded only when first needed.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            np.ndarray: Embedding vector (512 dimensions)
            
        Raises:
            ImportError: If sentence_transformers or numpy is not installed.
            Exception: If the model cannot be loaded or encoding fails.
        """
        # Ensure model is loaded (lazy loading)
        self._load_fast_model()
        
        # Check if numpy is available
        if np is None:
            raise ImportError(
                "numpy no está instalado. "
                "Instálalo con: pip install numpy<2.0"
            )
        
        # Generate embedding
        try:
            embedding = EmbeddingService._fast_model.encode(text)
            return embedding
        except Exception as e:
            raise Exception(
                f"Error al generar embedding con modelo rápido: {str(e)}"
            ) from e
    
    def generate_quality_embedding(self, text: str):
        """
        Generate embedding using the quality model (mpnet).
        
        This method uses lazy loading - the model is loaded only when first needed.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            np.ndarray: Embedding vector (768 dimensions)
            
        Raises:
            ImportError: If sentence_transformers or numpy is not installed.
            Exception: If the model cannot be loaded or encoding fails.
        """
        # Ensure model is loaded (lazy loading)
        self._load_quality_model()
        
        # Check if numpy is available
        if np is None:
            raise ImportError(
                "numpy no está instalado. "
                "Instálalo con: pip install numpy<2.0"
            )
        
        # Generate embedding
        try:
            embedding = EmbeddingService._quality_model.encode(text)
            return embedding
        except Exception as e:
            raise Exception(
                f"Error al generar embedding con modelo calidad: {str(e)}"
            ) from e
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        model_type: Literal["fast", "quality"] = "quality"
    ):
        """
        Generate embeddings for multiple texts in batch (more efficient).
        
        Batch processing is more efficient than processing texts one by one.
        This method uses lazy loading - models are loaded only when first needed.
        
        Args:
            texts: List of texts to generate embeddings for
            model_type: Which model to use ("fast" or "quality")
            
        Returns:
            np.ndarray: Array of embeddings (shape: [num_texts, embedding_dim])
            
        Raises:
            ValueError: If texts list is empty.
            ImportError: If sentence_transformers or numpy is not installed.
            Exception: If the model cannot be loaded or encoding fails.
        """
        if not texts:
            raise ValueError("La lista de textos no puede estar vacía")
        
        # Check if numpy is available
        if np is None:
            raise ImportError(
                "numpy no está instalado. "
                "Instálalo con: pip install numpy<2.0"
            )
        
        # Select model based on model_type
        if model_type == "fast":
            self._load_fast_model()
            model = EmbeddingService._fast_model
        else:  # quality
            self._load_quality_model()
            model = EmbeddingService._quality_model
        
        # Generate embeddings in batch
        try:
            embeddings = model.encode(texts)
            return embeddings
        except Exception as e:
            raise Exception(
                f"Error al generar embeddings en batch con modelo {model_type}: {str(e)}"
            ) from e
    
    def generate_event_embedding(
        self,
        event_type: str,
        description: str,
        moment_of_day: str,
        day_of_week: Optional[str],
        supports: List[str],
        result: str,
        additional_supports: Optional[str] = None,
        observations: Optional[str] = None,
        model_type: Literal["fast", "quality"] = "quality"
    ):
        """
        High-level method to generate embedding for a complete event.
        
        This method combines the event text and generates the embedding in one call.
        It's a convenience method that calls combine_event_text() and then
        generate_fast_embedding() or generate_quality_embedding().
        
        Args:
            event_type: Type of the event
            description: Description of the event
            moment_of_day: Moment of day
            day_of_week: Day of week (optional)
            supports: List of supports used
            result: Result of the event
            additional_supports: Additional supports in free text (optional)
            observations: Optional observations
            model_type: Which model to use ("fast" or "quality")
            
        Returns:
            np.ndarray: Embedding vector
            
        Raises:
            ImportError: If sentence_transformers or numpy is not installed.
            Exception: If the model cannot be loaded or encoding fails.
        """
        # Combine event fields into a single text
        combined_text = self.combine_event_text(
            event_type=event_type,
            description=description,
            moment_of_day=moment_of_day,
            day_of_week=day_of_week,
            supports=supports,
            result=result,
            additional_supports=additional_supports,
            observations=observations
        )
        
        # Generate embedding using the specified model
        if model_type == "fast":
            return self.generate_fast_embedding(combined_text)
        else:  # quality
            return self.generate_quality_embedding(combined_text)

