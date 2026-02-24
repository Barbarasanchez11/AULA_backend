from typing import Dict, Any
from uuid import UUID
import logging

from app.services.langgraph.services.context_searcher import ContextSearcher
from app.services.pattern_analysis import PatternAnalysisService
from app.services.langgraph.repositories.event_repository import get_all_events_for_classroom

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
        
        # Step 3: Pattern analysis
        # Fetch all events to analyze trends
        db_events = await get_all_events_for_classroom(classroom_id)
        patterns = self.pattern_service.analyze_all_patterns(classroom_id, db_events)
        
        # Step 4: Context Building (Formatted string for LLM)
        context_str = self._build_context_string(similar_events, patterns)
        
        return {
            "similar_events": similar_events,
            "patterns": patterns,
            "context_for_llm": context_str
        }

    def _build_context_string(self, similar_events: list, patterns: dict) -> str:
        """
        Formats findings into a natural language prompt fragment for the LLM.
        """
        sections = []
        
        # Historical context
        if similar_events:
            sections.append(f"Found {len(similar_events)} similar historical events.")
        else:
            sections.append("No direct similar historical events found.")

        # Temporal context
        temporal = patterns.get("temporal_patterns", {})
        if temporal.get("most_common_day") or temporal.get("most_common_moment"):
            sections.append(
                f"Classroom trends: Most events occur on {temporal.get('most_common_day', 'N/A')} "
                f"during the {temporal.get('most_common_moment', 'N/A')}."
            )

        # Strategy context
        effectiveness = patterns.get("support_effectiveness", {})
        most_effective = effectiveness.get("most_effective_supports", [])
        if most_effective:
            top_support = most_effective[0]["support"]
            rate = most_effective[0]["success_rate"] * 100
            sections.append(f"Highly effective strategy: {top_support} ({rate:.0f}% success rate).")

        return " ".join(sections)
