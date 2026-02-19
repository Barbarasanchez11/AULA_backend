"""
Node 3: Generate Recommendation with LLM

This node:
- Builds prompt with context
- Calls Groq LLM
- Stores response and metadata
"""

from app.services.langgraph.state import RecommendationState


from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.langgraph.state import RecommendationState

def node_generate_llm(state: RecommendationState, llm) -> RecommendationState:
    """
    Node 3: Generate recommendation with LLM.
    
    - Builds prompt with context
    - Calls Groq LLM (via LangChain ChatGroq)
    - Stores raw response and metadata
    
    Args:
        state: Current state with event_data and context_for_llm
        llm: LLM client (ChatGroq instance)
        
    Returns:
        Updated state with llm_response and llm_metadata
    """
    # 1. Extract data from state
    event_data = state.get("event_data", {})
    context_for_llm = state.get("context_for_llm", "No historical context available.")
    
    # 2. Prepare System Prompt (The Persona)
    system_prompt = (
        "Eres un experto consultor pedagógico especializado en Trastorno del Espectro Autista (TEA). "
        "Tu misión es proporcionar recomendaciones accionables, empáticas y basadas en evidencia "
        "para docentes que enfrentan desafíos en el aula.\n\n"
        "REGLAS DE ORO:\n"
        "1. Sé breve y directo (máximo 3-4 párrafos).\n"
        "2. Usa un tono profesional pero cercano.\n"
        "3. Basa tu consejo en los DATOS HISTÓRICOS proporcionados si existen.\n"
        "4. No inventes datos personales.\n"
        "5. IMPORTANTE: Tu respuesta debe estar escrita íntegramente en ESPAÑOL."
    )
    
    # 3. Prepare Human Content (The Case)
    human_content = (
        f"DATOS DEL EVENTO ACTUAL:\n"
        f"- Tipo: {event_data.get('event_type')}\n"
        f"- Descripción: {event_data.get('description')}\n"
        f"- Contexto temporal: {event_data.get('context', {}).get('moment_of_day', 'N/A')}\n"
        f"- Apoyos utilizados: {', '.join(event_data.get('supports', []))}\n"
        f"- Observaciones: {event_data.get('observations', 'Ninguna')}\n\n"
        f"CONTEXTO HISTÓRICO Y PATRONES DETECTADOS EN ESTE AULA:\n"
        f"{context_for_llm}\n\n"
        f"Basándote en lo anterior, genera una recomendación pedagógica para el docente."
    )
    
    # 4. Invoke LLM
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_content)
        ]
        
        # Start timing
        start_time = datetime.utcnow()
        response = llm.invoke(messages)
        end_time = datetime.utcnow()
        
        # 5. Update State
        state["llm_response"] = response.content
        
        # Metadata tracking
        if "llm_metadata" not in state:
            state["llm_metadata"] = {}
        
        state["llm_metadata"]["tokens"] = getattr(response, "response_metadata", {}).get("token_usage", {})
        state["llm_metadata"]["duration_seconds"] = (end_time - start_time).total_seconds()
        state["llm_metadata"]["model"] = getattr(llm, "model_name", "unknown")
        
        if "metadata" not in state:
            state["metadata"] = {}
        state["metadata"]["node_3_completed"] = True
        state["metadata"]["node_3_timestamp"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        state["errors"].append({
            "node": "generate_llm",
            "severity": "critical",
            "message": f"LLM Invocation error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return state



