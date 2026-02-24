
import asyncio
import sys
import os
from uuid import uuid4

# Añadir el raíz del proyecto al path para poder importar la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.langgraph.services.context_service import ContextService

async def test_context_retrieval():
    print("🚀 Iniciando Test de ContextService (Nodo 2 - Punto 2)...")
    
    # 1. Instanciar el servicio
    service = ContextService()
    
    # 2. Crear un evento de prueba (Datos simulados)
    classroom_id = uuid4()
    mock_event = {
        "event_type": "TRANSICION",
        "description": "El alumno se niega a entrar al aula tras el recreo.",
        "context": {
            "moment_of_day": "tarde",
            "day_of_week": "lunes"
        },
        "supports": ["Apoyo visual"],
        "result": "DIFICIL"
    }
    
    print(f"🔍 Buscando contexto para evento: '{mock_event['description']}'")
    
    try:
        # 3. Ejecutar la búsqueda de contexto
        # Nota: Esto intentará conectar con ChromaDB. 
        # Si la base de datos está vacía, devolverá una lista vacía.
        result = await service.get_event_context(mock_event, classroom_id)
        
        print("\n✅ Resultado de la orquestación:")
        print(f"   - Eventos similares encontrados: {len(result['similar_events'])}")
        print(f"   - Patrones detectados: {result['patterns']}")
        print(f"   - Resumen para el LLM: {result['context_for_llm']}")
        
        if len(result['similar_events']) > 0:
            print("\n📊 Detalle del primer evento similar:")
            first = result['similar_events'][0]
            print(f"     ID: {first['event_id']}")
            print(f"     Score de similitud: {first['score']:.4f}")
        else:
            print("\n💡 Nota: No se encontraron eventos similares (es normal si ChromaDB está vacío).")
            
    except Exception as e:
        print(f"\n❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_context_retrieval())
