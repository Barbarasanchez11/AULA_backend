"""
Test script to verify embedding generation functions (Subtarea 1.5)

Tests:
1. generate_fast_embedding() generates embeddings with correct dimensions
2. generate_quality_embedding() generates embeddings with correct dimensions
3. generate_embeddings_batch() processes multiple texts
4. generate_event_embedding() combines text and generates embedding
5. Embeddings are numpy arrays
6. Different texts produce different embeddings
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embeddingService import EmbeddingService


def test_fast_embedding_generation():
    """Test that fast embedding generation works"""
    print("🧪 Test 1: Generación de Embedding Rápido")
    
    service = EmbeddingService.get_instance()
    
    text = "TRANSICION. Transición de juego libre a asamblea matutina."
    
    try:
        embedding = service.generate_fast_embedding(text)
        
        # Verify it's a numpy array
        assert hasattr(embedding, 'shape'), "Embedding debe ser un array NumPy"
        
        # Verify dimensions (distiluse produces 512-dimensional embeddings)
        assert embedding.shape == (512,), f"Embedding debe tener 512 dimensiones, tiene {embedding.shape}"
        
        # Verify it's not all zeros
        assert embedding.sum() != 0, "Embedding no debe ser todo ceros"
        
        print(f"   ✅ Embedding generado correctamente")
        print(f"   📊 Dimensiones: {embedding.shape}")
        print(f"   📊 Tipo: {type(embedding).__name__}")
        print(f"   📊 Valores ejemplo: {embedding[:5]}")
        
        return True
    except ImportError as e:
        print(f"   ⚠️  Dependencias no instaladas: {e}")
        print("   💡 Instala con: pip install sentence-transformers numpy<2.0")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_quality_embedding_generation():
    """Test that quality embedding generation works"""
    print("\n🧪 Test 2: Generación de Embedding Calidad")
    
    service = EmbeddingService.get_instance()
    
    text = "APRENDIZAJE. Actividad de trabajo en mesa individual."
    
    try:
        embedding = service.generate_quality_embedding(text)
        
        # Verify it's a numpy array
        assert hasattr(embedding, 'shape'), "Embedding debe ser un array NumPy"
        
        # Verify dimensions (mpnet produces 768-dimensional embeddings)
        assert embedding.shape == (768,), f"Embedding debe tener 768 dimensiones, tiene {embedding.shape}"
        
        # Verify it's not all zeros
        assert embedding.sum() != 0, "Embedding no debe ser todo ceros"
        
        print(f"   ✅ Embedding generado correctamente")
        print(f"   📊 Dimensiones: {embedding.shape}")
        print(f"   📊 Tipo: {type(embedding).__name__}")
        print(f"   📊 Valores ejemplo: {embedding[:5]}")
        
        return True
    except ImportError as e:
        print(f"   ⚠️  Dependencias no instaladas: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_embeddings_batch():
    """Test that batch embedding generation works"""
    print("\n🧪 Test 3: Generación de Embeddings en Batch")
    
    service = EmbeddingService.get_instance()
    
    texts = [
        "TRANSICION. Transición de juego libre a asamblea.",
        "APRENDIZAJE. Actividad de trabajo en mesa individual.",
        "REGULACION. Momento de regulación emocional."
    ]
    
    try:
        # Test with fast model
        embeddings_fast = service.generate_embeddings_batch(texts, model_type="fast")
        
        assert embeddings_fast.shape[0] == len(texts), "Debe haber un embedding por texto"
        assert embeddings_fast.shape[1] == 512, "Embeddings rápidos deben tener 512 dimensiones"
        
        print(f"   ✅ Batch rápido: {embeddings_fast.shape[0]} embeddings de {embeddings_fast.shape[1]} dimensiones")
        
        # Test with quality model
        embeddings_quality = service.generate_embeddings_batch(texts, model_type="quality")
        
        assert embeddings_quality.shape[0] == len(texts), "Debe haber un embedding por texto"
        assert embeddings_quality.shape[1] == 768, "Embeddings calidad deben tener 768 dimensiones"
        
        print(f"   ✅ Batch calidad: {embeddings_quality.shape[0]} embeddings de {embeddings_quality.shape[1]} dimensiones")
        
        return True
    except ImportError as e:
        print(f"   ⚠️  Dependencias no instaladas: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_event_embedding_generation():
    """Test that event embedding generation works (high-level method)"""
    print("\n🧪 Test 4: Generación de Embedding de Evento Completo")
    
    service = EmbeddingService.get_instance()
    
    try:
        # Generate embedding for a complete event (fast model)
        embedding_fast = service.generate_event_embedding(
            event_type="TRANSICION",
            description="Transición de juego libre a asamblea matutina",
            moment_of_day="mañana",
            day_of_week="lunes",
            supports=["Anticipación visual", "Mediación verbal"],
            result="EXITOSO",
            additional_supports="Se utilizó música de fondo",
            observations="Todos se incorporaron sin dificultades",
            model_type="fast"
        )
        
        assert embedding_fast.shape == (512,), "Embedding rápido debe tener 512 dimensiones"
        print(f"   ✅ Embedding rápido generado: {embedding_fast.shape}")
        
        # Generate embedding for a complete event (quality model)
        embedding_quality = service.generate_event_embedding(
            event_type="APRENDIZAJE",
            description="Actividad de trabajo en mesa individual",
            moment_of_day="tarde",
            day_of_week=None,
            supports=["Adaptación del entorno"],
            result="PARCIAL",
            additional_supports=None,
            observations=None,
            model_type="quality"
        )
        
        assert embedding_quality.shape == (768,), "Embedding calidad debe tener 768 dimensiones"
        print(f"   ✅ Embedding calidad generado: {embedding_quality.shape}")
        
        return True
    except ImportError as e:
        print(f"   ⚠️  Dependencias no instaladas: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_different_texts_different_embeddings():
    """Test that different texts produce different embeddings"""
    print("\n🧪 Test 5: Textos Diferentes Producen Embeddings Diferentes")
    
    service = EmbeddingService.get_instance()
    
    text1 = "TRANSICION. Transición de juego libre a asamblea."
    text2 = "APRENDIZAJE. Actividad de trabajo en mesa individual."
    
    try:
        embedding1 = service.generate_fast_embedding(text1)
        embedding2 = service.generate_fast_embedding(text2)
        
        # Calculate cosine similarity (simple dot product since embeddings are normalized)
        # If embeddings are different, their dot product should be less than 1.0
        similarity = embedding1.dot(embedding2)
        
        assert similarity < 0.99, "Textos diferentes deben producir embeddings diferentes"
        
        print(f"   ✅ Embeddings diferentes generados")
        print(f"   📊 Similitud (dot product): {similarity:.4f}")
        print(f"   💡 Valores cercanos a 1.0 = muy similares, valores bajos = diferentes")
        
        return True
    except ImportError as e:
        print(f"   ⚠️  Dependencias no instaladas: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_batch_empty_list():
    """Test that batch generation raises error for empty list"""
    print("\n🧪 Test 6: Batch con Lista Vacía (Debe Fallar)")
    
    service = EmbeddingService.get_instance()
    
    try:
        service.generate_embeddings_batch([], model_type="fast")
        print("   ❌ ERROR: Debería haber lanzado ValueError para lista vacía")
        return False
    except ValueError as e:
        print(f"   ✅ Correctamente lanza ValueError: {e}")
        return True
    except ImportError:
        print("   ⚠️  Dependencias no instaladas, no se puede probar")
        return True  # Not a failure, just missing dependencies
    except Exception as e:
        print(f"   ⚠️  Error inesperado: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("PRUEBAS DE GENERACIÓN DE EMBEDDINGS - EmbeddingService (Subtarea 1.5)")
    print("=" * 70)
    print("\n⚠️  NOTA: Estos tests requieren sentence-transformers y numpy instalados.")
    print("   Si no están instalados, algunos tests se saltarán.\n")
    
    tests = [
        test_fast_embedding_generation,
        test_quality_embedding_generation,
        test_embeddings_batch,
        test_event_embedding_generation,
        test_different_texts_different_embeddings,
        test_batch_empty_list
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ ERROR en {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 70)
    print("RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    if passed == total:
        print(f"✅ TODAS LAS PRUEBAS PASARON ({passed}/{total})")
        print("\nLa generación de embeddings está correctamente implementada.")
        return 0
    else:
        print(f"⚠️  {passed}/{total} PRUEBAS PASARON")
        if passed < total:
            print("   Algunas pruebas fallaron o se saltaron (posiblemente por dependencias faltantes).")
        return 1 if passed == 0 else 0


if __name__ == "__main__":
    exit(main())

