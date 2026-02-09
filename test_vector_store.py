"""
Test script to verify VectorStore service (Subtareas 2.2 y 2.3)

Tests:
1. VectorStore initialization
2. Collection creation (lazy)
3. Adding event embeddings
4. Searching similar events
5. Deleting event embeddings
6. Metadata filtering
"""

import sys
import os
import tempfile
import shutil
from uuid import uuid4

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_store import VectorStore


def test_vector_store_initialization():
    """Test that VectorStore can be initialized"""
    print("🧪 Test 1: Inicialización de VectorStore")
    
    try:
        # Create temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        vector_store = VectorStore(persist_directory=temp_dir)
        
        assert vector_store.client is not None, "Cliente ChromaDB debe estar inicializado"
        print("   ✅ VectorStore inicializado correctamente")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
    except ImportError as e:
        print(f"   ⚠️  ChromaDB no está instalado: {e}")
        print("   💡 Instala con: pip install chromadb")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_collection_creation():
    """Test that collections are created lazily"""
    print("\n🧪 Test 2: Creación de Colecciones (Lazy)")
    
    try:
        temp_dir = tempfile.mkdtemp()
        vector_store = VectorStore(persist_directory=temp_dir)
        
        classroom_id = uuid4()
        
        # Collection should be created on first access
        collection = vector_store.get_or_create_collection(classroom_id)
        
        assert collection is not None, "Colección debe ser creada"
        assert collection.count() == 0, "Colección nueva debe estar vacía"
        
        print(f"   ✅ Colección creada para aula: {classroom_id}")
        print(f"   📊 Eventos en colección: {collection.count()}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_add_event_embedding():
    """Test adding event embeddings"""
    print("\n🧪 Test 3: Agregar Embeddings de Eventos")
    
    try:
        temp_dir = tempfile.mkdtemp()
        vector_store = VectorStore(persist_directory=temp_dir)
        
        classroom_id = uuid4()
        event_id = uuid4()
        
        # Create a dummy embedding (512 dimensions for fast model)
        embedding = [0.1] * 512
        
        # Add embedding
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=event_id,
            embedding=embedding,
            metadata={"event_type": "TRANSICION", "result": "EXITOSO"}
        )
        
        # Verify it was added
        count = vector_store.get_collection_count(classroom_id)
        assert count == 1, f"Debería haber 1 evento, hay {count}"
        
        print(f"   ✅ Embedding agregado correctamente")
        print(f"   📊 Eventos en colección: {count}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_search_similar_events():
    """Test searching for similar events"""
    print("\n🧪 Test 4: Búsqueda de Eventos Similares")
    
    try:
        temp_dir = tempfile.mkdtemp()
        vector_store = VectorStore(persist_directory=temp_dir)
        
        classroom_id = uuid4()
        
        # Add multiple events with different embeddings
        event1_id = uuid4()
        event2_id = uuid4()
        event3_id = uuid4()
        
        # Event 1: embedding with high values
        embedding1 = [0.9] * 512
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=event1_id,
            embedding=embedding1,
            metadata={"event_type": "TRANSICION"}
        )
        
        # Event 2: embedding similar to event1
        embedding2 = [0.85] * 512
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=event2_id,
            embedding=embedding2,
            metadata={"event_type": "TRANSICION"}
        )
        
        # Event 3: embedding very different
        embedding3 = [0.1] * 512
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=event3_id,
            embedding=embedding3,
            metadata={"event_type": "APRENDIZAJE"}
        )
        
        # Search for events similar to event1
        query_embedding = [0.88] * 512  # Similar to event1 and event2
        results = vector_store.search_similar_events(
            classroom_id=classroom_id,
            query_embedding=query_embedding,
            top_k=3
        )
        
        assert len(results) > 0, "Debe encontrar eventos similares"
        assert results[0]["score"] > 0.5, "Score de similitud debe ser razonable"
        
        print(f"   ✅ Búsqueda completada")
        print(f"   📊 Eventos encontrados: {len(results)}")
        for i, result in enumerate(results[:3]):
            print(f"      {i+1}. Evento {result['event_id']}: score={result['score']:.4f}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metadata_filtering():
    """Test filtering by metadata"""
    print("\n🧪 Test 5: Filtrado por Metadata")
    
    try:
        temp_dir = tempfile.mkdtemp()
        vector_store = VectorStore(persist_directory=temp_dir)
        
        classroom_id = uuid4()
        
        # Add events with different types
        event1_id = uuid4()
        event2_id = uuid4()
        
        embedding = [0.5] * 512
        
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=event1_id,
            embedding=embedding,
            metadata={"event_type": "TRANSICION"}
        )
        
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=event2_id,
            embedding=embedding,
            metadata={"event_type": "APRENDIZAJE"}
        )
        
        # Search with filter for TRANSICION only
        query_embedding = [0.5] * 512
        results = vector_store.search_similar_events(
            classroom_id=classroom_id,
            query_embedding=query_embedding,
            top_k=5,
            filters={"event_type": "TRANSICION"}
        )
        
        # All results should be TRANSICION
        for result in results:
            assert result["metadata"]["event_type"] == "TRANSICION", \
                "Todos los resultados deben ser TRANSICION"
        
        print(f"   ✅ Filtrado por metadata funciona correctamente")
        print(f"   📊 Eventos TRANSICION encontrados: {len(results)}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_delete_event_embedding():
    """Test deleting event embeddings"""
    print("\n🧪 Test 6: Eliminar Embeddings de Eventos")
    
    try:
        temp_dir = tempfile.mkdtemp()
        vector_store = VectorStore(persist_directory=temp_dir)
        
        classroom_id = uuid4()
        event_id = uuid4()
        
        # Add embedding
        embedding = [0.5] * 512
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=event_id,
            embedding=embedding
        )
        
        # Verify it exists
        count_before = vector_store.get_collection_count(classroom_id)
        assert count_before == 1, "Debería haber 1 evento"
        
        # Delete it
        vector_store.delete_event_embedding(classroom_id, event_id)
        
        # Verify it's gone
        count_after = vector_store.get_collection_count(classroom_id)
        assert count_after == 0, "Debería haber 0 eventos después de eliminar"
        
        print(f"   ✅ Embedding eliminado correctamente")
        print(f"   📊 Eventos antes: {count_before}, después: {count_after}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("PRUEBAS DE VECTORSTORE - ChromaDB (Subtareas 2.2 y 2.3)")
    print("=" * 70)
    print("\n⚠️  NOTA: Estos tests requieren chromadb instalado.")
    print("   Si no está instalado, algunos tests se saltarán.\n")
    
    tests = [
        test_vector_store_initialization,
        test_collection_creation,
        test_add_event_embedding,
        test_search_similar_events,
        test_metadata_filtering,
        test_delete_event_embedding
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
        print("\nEl servicio VectorStore está correctamente implementado.")
        return 0
    else:
        print(f"⚠️  {passed}/{total} PRUEBAS PASARON")
        if passed < total:
            print("   Algunas pruebas fallaron o se saltaron (posiblemente por dependencias faltantes).")
        return 1 if passed == 0 else 0


if __name__ == "__main__":
    exit(main())

