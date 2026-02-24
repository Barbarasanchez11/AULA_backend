from typing import Dict, Any, List
from uuid import UUID
import logging
from app.services.vector_store import VectorStore
from app.services.embeddingService import EmbeddingService

logger = logging.getLogger(__name__)

class ContextSearcher:
    """
    Specialized service for searching similar events in the vector database.
    (Point 2 of our implementation plan)
    """
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedding_service = EmbeddingService.get_instance()

    def search_similar_events(self, event_data: Dict[str, Any], classroom_id: UUID) -> List[Dict[str, Any]]:
        """
        Searches for similar events in the history using semantic similarity.
        """
        try:
            context = event_data.get("context", {})
            
            # 1. Generate embedding for the current event
            query_embedding = self.embedding_service.generate_event_embedding(
                event_type=event_data.get("event_type", ""),
                description=event_data.get("description", ""),
                moment_of_day=context.get("moment_of_day", ""),
                day_of_week=context.get("day_of_week"),
                supports=event_data.get("supports", []),
                result=event_data.get("result", ""),
                additional_supports=event_data.get("additional_supports"),
                observations=event_data.get("observations"),
                model_type="quality"
            )

            # 2. Perform the search in the vector store
            results = self.vector_store.search_similar_events(
                classroom_id=classroom_id,
                query_embedding=query_embedding,
                top_k=5,
                min_similarity=0.6
            )
            
            return results

        except Exception as e:
            logger.error(f"Error in ContextSearcher.search_similar_events: {str(e)}")
            return []
