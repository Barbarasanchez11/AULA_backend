from typing import Dict, Any
from uuid import UUID
import logging

from app.services.langgraph.services.context_searcher import ContextSearcher
from app.services.pattern_analysis import PatternAnalysisService

logger = logging.getLogger(__name__)

class ContextService:
    """
    Main orchestrator for gathering historical and structural context.
    Delegates specialized tasks to Searcher, Analyzer, and Builder.
    """
    
    def __init__(self):
        self.searcher = ContextSearcher()
        self.pattern_service = PatternAnalysisService()

    async def get_event_context(self, event_data: Dict[str, Any], classroom_id: UUID) -> Dict[str, Any]:
        """
        Coordinates the gathering of context for a given event.
        """
        # Step 2: Search for similar events (delegated to ContextSearcher)
        similar_events = self.searcher.search_similar_events(event_data, classroom_id)
        
        # Step 3: Pattern analysis (To be fully integrated)
        # For now, we return basic results
        return {
            "similar_events": similar_events,
            "patterns": {},
            "context_for_llm": f"Historical search found {len(similar_events)} relevant events."
        }
