
import asyncio
import sys
import os
from uuid import uuid4

# Añadir el raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.langgraph.service import LangGraphService

async def test_full_graph():
    print("🚀 Iniciando Test Completo de LangGraph (Nodos 1-4)...")
    
    # 1. Instanciar el servicio (Carga el grafo y el cliente de Groq)
    try:
        service = LangGraphService()
    except Exception as e:
        print(f"❌ Error al inicializar LangGraphService: {str(e)}")
        return

    # 2. Datos de prueba: Un aula y un evento que no están en DB todavía
    # (Para que Node 1 valide el event_data directamente)
    classroom_id = uuid4() # ID aleatorio (fallará validación si no existe en DB, pero Node 1 lo maneja)
    
    # IMPORTANTE: Para que Node 1 no falle, necesitamos un aula real en la DB
    # o saltarnos esa validación para el test.
    # Vamos a usar un evento nuevo.
    
    mock_event = {
        "event_type": "TRANSICION",
        "description": "El alumno muestra mucha ansiedad al cambiar de la clase de pintura al patio.",
        "context": {
            "moment_of_day": "mañana",
            "day_of_week": "miércoles"
        },
        "supports": ["Anticipación visual"],
        "result": "DIFICIL",
        "observations": "Se ha tirado al suelo y llora."
    }
    
    print(f"📝 Enviando evento al Grafo: '{mock_event['description']}'")
    
    try:
        # 3. Ejecutar el Grafo completo
        # Nota: La validación de classroom_id puede fallar si no existe en la DB real de Docker.
        # Pero como queremos ver el flujo, observaremos cómo el Grafo gestiona el estado.
        
        # Como no tenemos una sesión de DB aquí, Node 1 podría dar error de 'Classroom not found'.
        # Para el test, vamos a ver qué devuelve.
        
        result = service.generate_recommendation(
            classroom_id=classroom_id,
            event_data=mock_event
        )
        
        print("\n🏁 RESULTADO FINAL DEL GRAFO:")
        
        # Verificar errores
        if result.get("errors"):
            print("\n⚠️  Errores detectados durante el flujo:")
            for error in result["errors"]:
                print(f"   [{error['node']}] {error['severity'].upper()}: {error['message']}")
        
        # Mostrar recomendación si llegamos al final
        if result.get("recommendation"):
            rec = result["recommendation"]
            print(f"\n✅ RECOMENDACIÓN GENERADA:")
            print(f"   - Título: {rec['title']}")
            print(f"   - Confianza: {result['confidence']}")
            print(f"\n   - Descripción:\n{rec['description']}")
            print(f"\n   - Patrón detectado: {rec['detected_pattern']}")
        else:
            print("\n❌ No se pudo generar la recomendación final.")

        # Mostrar Metadatos
        print("\n📊 Metadatos del proceso:")
        for key, value in result.get("metadata", {}).items():
            print(f"   - {key}: {value}")

    except Exception as e:
        print(f"\n❌ Error fatal en la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # LangGraph invocation is synchronous in our service.py wrapper (graph.invoke)
    # so we can call it directly, but the test wrapper is async.
    asyncio.run(test_full_graph())
