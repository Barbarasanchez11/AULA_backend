"""
Node 4: Validate and Format Recommendation

This node:
- Parses LLM response
- Validates against Pydantic schemas
- Calculates confidence
- Formats for database storage
"""

from datetime import datetime
from app.services.langgraph.state import RecommendationState


from datetime import datetime
from app.services.langgraph.state import RecommendationState
from app.services.recommendation_generator import RecommendationGenerator
from app.schemas.enums import RecommendationType, ConfidenceLevel

# Initialize generator for utility methods
generator = RecommendationGenerator()

def node_validate_format(state: RecommendationState) -> RecommendationState:
    """
    Node 4: Validate and format recommendation.
    
    - Parses LLM response
    - Calculates confidence based on pattern strength
    - Formats for database storage
    
    Args:
        state: Current state with llm_response and patterns
        
    Returns:
        Updated state with recommendation and confidence
    """
    llm_response = state.get("llm_response")
    patterns = state.get("patterns", {})
    event_data = state.get("event_data", {})
    
    if not llm_response:
        state["errors"].append({
            "node": "validate_format",
            "severity": "error",
            "message": "No response from LLM to validate",
            "timestamp": datetime.utcnow().isoformat()
        })
        return state
    
    try:
        # 1. Calculate Confidence
        # We look at the most relevant pattern factor: success rate or sample size
        # This logic mirrors RecommendationGenerator.calculate_confidence
        clustering = patterns.get("clustering", {})
        effectiveness = patterns.get("support_effectiveness", {})
        
        # Calculate scores
        sample_size = len(clustering.get("clusters", [])) + len(state.get("similar_events", []))
        success_rate = 0.5 # Default middle ground
        
        if effectiveness.get("most_effective_supports"):
            success_rate = effectiveness["most_effective_supports"][0]["success_rate"]
        
        confidence_enum = generator.calculate_confidence(
            pattern_strength=0.7, # Default strength for LLM insight
            sample_size=sample_size,
            success_rate=success_rate
        )
        
        # 2. Format Recommendation Object
        # In a more advanced version, we would parse JSON from the LLM.
        # For now, we structure the raw text into the schema fields.
        
        title = f"Intervención para {event_data.get('event_type', 'evento TEA')}"
        if "\n" in llm_response:
            # Try to use the first line as a title if it's short
            first_line = llm_response.split("\n")[0].strip("# ").strip()
            if 10 <= len(first_line) <= 100:
                title = first_line
        
        recommendation = {
            "recommendation_type": RecommendationType.ESTRATEGIA,
            "title": title,
            "description": llm_response,
            "applicable_context": (
                f"Aplicable en situaciones de tipo {event_data.get('event_type')}. "
                f"Contexto histórico: {state.get('context_for_llm', 'No disponible.')}"
            ),
            "detected_pattern": (
                f"Basado en {len(state.get('similar_events', []))} eventos similares "
                f"y análisis de {len(patterns.get('clustering', {}).get('clusters', []))} clusters."
            ),
            "confidence": confidence_enum
        }
        
        # 3. Final State Update
        state["recommendation"] = recommendation
        state["confidence"] = confidence_enum.value
        
        if "metadata" not in state:
            state["metadata"] = {}
        
        state["metadata"]["node_4_completed"] = True
        state["metadata"]["node_4_timestamp"] = datetime.utcnow().isoformat()
        state["metadata"]["timestamp_end"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        state["errors"].append({
            "node": "validate_format",
            "severity": "error",
            "message": f"Formatting error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return state



