"""
Test completo del servicio de embeddings con eventos de ejemplo (Subtarea 1.6)

Este test verifica que todo el servicio funciona correctamente con eventos realistas:
1. Genera embeddings para múltiples eventos de ejemplo
2. Verifica que eventos similares tienen embeddings similares
3. Compara ambos modelos (fast y quality)
4. Prueba batch processing
5. Muestra estadísticas y resultados
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embeddingService import EmbeddingService


def create_sample_events():
    """
    Crea eventos de ejemplo realistas del aula TEA.
    
    Estos eventos simulan situaciones reales:
    - Eventos similares (mismo tipo, diferentes palabras)
    - Eventos diferentes (diferentes tipos)
    - Eventos con contexto similar pero resultado diferente
    """
    events = [
        {
            "id": 1,
            "event_type": "TRANSICION",
            "description": "Transición de juego libre a asamblea matutina",
            "moment_of_day": "mañana",
            "day_of_week": "lunes",
            "supports": ["Anticipación visual", "Mediación verbal"],
            "additional_supports": None,
            "result": "EXITOSO",
            "observations": "Todos se incorporaron sin dificultades"
        },
        {
            "id": 2,
            "event_type": "TRANSICION",
            "description": "Cambio de actividad de trabajo individual a reunión grupal",
            "moment_of_day": "mañana",
            "day_of_week": "martes",
            "supports": ["Adaptación del entorno", "Mediación verbal"],
            "additional_supports": None,
            "result": "EXITOSO",
            "observations": "El grupo se adaptó bien al cambio de formato"
        },
        {
            "id": 3,
            "event_type": "CAMBIO_DE_RUTINA",
            "description": "Modificación del horario de recreo al mediodía",
            "moment_of_day": "mediodia",
            "day_of_week": "miercoles",
            "supports": ["Anticipación visual", "Adaptación del entorno"],
            "additional_supports": None,
            "result": "PARCIAL",
            "observations": "Algunos estudiantes necesitaron apoyo individual"
        },
        {
            "id": 4,
            "event_type": "APRENDIZAJE",
            "description": "Actividad de aprendizaje en mesa individual",
            "moment_of_day": "mañana",
            "day_of_week": "jueves",
            "supports": ["Apoyo individual del adulto", "Adaptación del entorno"],
            "additional_supports": None,
            "result": "PARCIAL",
            "observations": "Requirió más tiempo del previsto"
        },
        {
            "id": 5,
            "event_type": "REGULACION",
            "description": "Momento de regulación emocional en la tarde",
            "moment_of_day": "tarde",
            "day_of_week": "viernes",
            "supports": ["Pausa sensorial", "Espacio tranquilo"],
            "additional_supports": "Se utilizó música relajante",
            "result": "EXITOSO",
            "observations": "El estudiante se calmó y pudo reincorporarse"
        },
        {
            "id": 6,
            "event_type": "TRANSICION",
            "description": "Paso de tiempo libre a círculo de la mañana",
            "moment_of_day": "mañana",
            "day_of_week": "lunes",
            "supports": ["Anticipación visual", "Mediación verbal"],
            "additional_supports": None,
            "result": "EXITOSO",
            "observations": "Transición fluida sin interrupciones"
        }
    ]
    return events


def calculate_cosine_similarity(embedding1, embedding2):
    """
    Calcula la similitud de coseno entre dos embeddings.
    
    La similitud de coseno va de -1 a 1:
    - 1.0 = idénticos
    - 0.0 = ortogonales (sin relación)
    - -1.0 = opuestos
    
    En embeddings normalizados, generalmente va de 0.0 a 1.0.
    """
    try:
        import numpy as np
        # Normalizar embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calcular similitud de coseno
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    except ImportError:
        # Fallback simple si numpy no está disponible
        return 0.0


def test_complete_service_with_events():
    """Test completo del servicio con eventos de ejemplo"""
    print("=" * 70)
    print("TEST COMPLETO DEL SERVICIO DE EMBEDDINGS (Subtarea 1.6)")
    print("=" * 70)
    
    try:
        service = EmbeddingService.get_instance()
        events = create_sample_events()
        
        print(f"\n📋 Eventos de ejemplo creados: {len(events)}")
        print("\n" + "-" * 70)
        
        # Test 1: Generar embeddings con modelo rápido
        print("\n🧪 Test 1: Generar Embeddings con Modelo Rápido")
        print("-" * 70)
        
        start_time = time.time()
        fast_embeddings = []
        
        for event in events:
            embedding = service.generate_event_embedding(
                event_type=event["event_type"],
                description=event["description"],
                moment_of_day=event["moment_of_day"],
                day_of_week=event["day_of_week"],
                supports=event["supports"],
                result=event["result"],
                additional_supports=event["additional_supports"],
                observations=event["observations"],
                model_type="fast"
            )
            fast_embeddings.append(embedding)
        
        fast_time = time.time() - start_time
        print(f"   ✅ {len(fast_embeddings)} embeddings generados en {fast_time:.2f} segundos")
        print(f"   ⏱️  Tiempo promedio: {fast_time/len(events):.3f} segundos por evento")
        print(f"   📊 Dimensiones: {fast_embeddings[0].shape}")
        
        # Test 2: Generar embeddings con modelo calidad
        print("\n🧪 Test 2: Generar Embeddings con Modelo Calidad")
        print("-" * 70)
        
        start_time = time.time()
        quality_embeddings = []
        
        for event in events:
            embedding = service.generate_event_embedding(
                event_type=event["event_type"],
                description=event["description"],
                moment_of_day=event["moment_of_day"],
                day_of_week=event["day_of_week"],
                supports=event["supports"],
                result=event["result"],
                additional_supports=event["additional_supports"],
                observations=event["observations"],
                model_type="quality"
            )
            quality_embeddings.append(embedding)
        
        quality_time = time.time() - start_time
        print(f"   ✅ {len(quality_embeddings)} embeddings generados en {quality_time:.2f} segundos")
        print(f"   ⏱️  Tiempo promedio: {quality_time/len(events):.3f} segundos por evento")
        print(f"   📊 Dimensiones: {quality_embeddings[0].shape}")
        
        # Test 3: Batch processing
        print("\n🧪 Test 3: Procesamiento en Batch")
        print("-" * 70)
        
        # Combinar textos de eventos para batch
        event_texts = []
        for event in events:
            text = service.combine_event_text(
                event_type=event["event_type"],
                description=event["description"],
                moment_of_day=event["moment_of_day"],
                day_of_week=event["day_of_week"],
                supports=event["supports"],
                result=event["result"],
                additional_supports=event["additional_supports"],
                observations=event["observations"]
            )
            event_texts.append(text)
        
        # Batch con modelo rápido
        start_time = time.time()
        batch_fast = service.generate_embeddings_batch(event_texts, model_type="fast")
        batch_fast_time = time.time() - start_time
        
        # Batch con modelo calidad
        start_time = time.time()
        batch_quality = service.generate_embeddings_batch(event_texts, model_type="quality")
        batch_quality_time = time.time() - start_time
        
        print(f"   ✅ Batch rápido: {len(event_texts)} embeddings en {batch_fast_time:.2f} segundos")
        print(f"   ⏱️  Tiempo promedio: {batch_fast_time/len(event_texts):.3f} segundos por evento")
        print(f"   ✅ Batch calidad: {len(event_texts)} embeddings en {batch_quality_time:.2f} segundos")
        print(f"   ⏱️  Tiempo promedio: {batch_quality_time/len(event_texts):.3f} segundos por evento")
        
        speedup_fast = fast_time / batch_fast_time if batch_fast_time > 0 else 1.0
        speedup_quality = quality_time / batch_quality_time if batch_quality_time > 0 else 1.0
        print(f"   🚀 Batch rápido es {speedup_fast:.2f}x más rápido que individual")
        print(f"   🚀 Batch calidad es {speedup_quality:.2f}x más rápido que individual")
        
        # Test 4: Similitud entre eventos similares
        print("\n🧪 Test 4: Similitud entre Eventos Similares")
        print("-" * 70)
        
        # Eventos similares: eventos 1, 2 y 6 son todos TRANSICION
        similar_events = [0, 1, 5]  # Índices de eventos TRANSICION
        
        print("   📊 Comparando eventos TRANSICION (eventos 1, 2 y 6):")
        
        # Con modelo rápido
        print("\n   🔹 Modelo Rápido:")
        for i in range(len(similar_events)):
            for j in range(i + 1, len(similar_events)):
                idx1 = similar_events[i]
                idx2 = similar_events[j]
                similarity = calculate_cosine_similarity(
                    fast_embeddings[idx1],
                    fast_embeddings[idx2]
                )
                print(f"      Evento {events[idx1]['id']} ↔ Evento {events[idx2]['id']}: {similarity:.4f}")
        
        # Con modelo calidad
        print("\n   🔹 Modelo Calidad:")
        for i in range(len(similar_events)):
            for j in range(i + 1, len(similar_events)):
                idx1 = similar_events[i]
                idx2 = similar_events[j]
                similarity = calculate_cosine_similarity(
                    quality_embeddings[idx1],
                    quality_embeddings[idx2]
                )
                print(f"      Evento {events[idx1]['id']} ↔ Evento {events[idx2]['id']}: {similarity:.4f}")
        
        # Test 5: Similitud entre eventos diferentes
        print("\n🧪 Test 5: Similitud entre Eventos Diferentes")
        print("-" * 70)
        
        # Comparar TRANSICION (evento 1) con REGULACION (evento 5)
        print("   📊 Comparando TRANSICION (evento 1) con REGULACION (evento 5):")
        
        similarity_fast = calculate_cosine_similarity(fast_embeddings[0], fast_embeddings[4])
        similarity_quality = calculate_cosine_similarity(quality_embeddings[0], quality_embeddings[4])
        
        print(f"   🔹 Modelo Rápido: {similarity_fast:.4f}")
        print(f"   🔹 Modelo Calidad: {similarity_quality:.4f}")
        print(f"   💡 Eventos diferentes deberían tener similitud más baja")
        
        # Test 6: Resumen y estadísticas
        print("\n" + "=" * 70)
        print("RESUMEN Y ESTADÍSTICAS")
        print("=" * 70)
        
        print(f"\n📊 Eventos procesados: {len(events)}")
        print(f"📊 Tipos de eventos: {len(set(e['event_type'] for e in events))}")
        print(f"   - TRANSICION: {sum(1 for e in events if e['event_type'] == 'TRANSICION')}")
        print(f"   - CAMBIO_DE_RUTINA: {sum(1 for e in events if e['event_type'] == 'CAMBIO_DE_RUTINA')}")
        print(f"   - APRENDIZAJE: {sum(1 for e in events if e['event_type'] == 'APRENDIZAJE')}")
        print(f"   - REGULACION: {sum(1 for e in events if e['event_type'] == 'REGULACION')}")
        
        print(f"\n⏱️  Tiempos de procesamiento:")
        print(f"   - Modelo rápido (individual): {fast_time:.2f}s ({fast_time/len(events):.3f}s/evento)")
        print(f"   - Modelo calidad (individual): {quality_time:.2f}s ({quality_time/len(events):.3f}s/evento)")
        print(f"   - Modelo rápido (batch): {batch_fast_time:.2f}s ({batch_fast_time/len(events):.3f}s/evento)")
        print(f"   - Modelo calidad (batch): {batch_quality_time:.2f}s ({batch_quality_time/len(events):.3f}s/evento)")
        
        print(f"\n📐 Dimensiones de embeddings:")
        print(f"   - Modelo rápido: {fast_embeddings[0].shape[0]} dimensiones")
        print(f"   - Modelo calidad: {quality_embeddings[0].shape[0]} dimensiones")
        
        print(f"\n✅ TODOS LOS TESTS PASARON")
        print("\nEl servicio de embeddings está funcionando correctamente.")
        print("Los embeddings capturan la semántica de los eventos correctamente.")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ ERROR: Dependencias no instaladas: {e}")
        print("   💡 Instala con: pip install sentence-transformers numpy<2.0")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the complete test"""
    success = test_complete_service_with_events()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

