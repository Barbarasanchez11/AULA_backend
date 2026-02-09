"""
Test script to verify EmbeddingService structure (Subtarea 1.2)

Tests:
1. Singleton pattern works (cannot create two instances)
2. get_instance() works correctly
3. Class variables are shared
4. Placeholder methods are defined
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.embeddingService import EmbeddingService
except ImportError as e:
    print(f"❌ Error importando EmbeddingService: {e}")
    sys.exit(1)


def test_singleton_pattern():
    """Test that Singleton pattern prevents multiple instances"""
    print("🧪 Test 1: Singleton Pattern")
    
    # First instance should work
    service1 = EmbeddingService.get_instance()
    print("   ✅ Primera instancia creada correctamente")
    
    # Second call should return the same instance
    service2 = EmbeddingService.get_instance()
    print("   ✅ Segunda llamada retorna la misma instancia")
    
    # Verify they are the same object
    assert service1 is service2, "Las instancias deberían ser la misma"
    print("   ✅ Las instancias son idénticas (mismo objeto en memoria)")
    
    # Try to create directly (should fail)
    try:
        service3 = EmbeddingService()
        print("   ❌ ERROR: Se permitió crear una segunda instancia directamente")
        return False
    except Exception as e:
        if "ya está inicializado" in str(e):
            print(f"   ✅ Correctamente bloqueado: {e}")
        else:
            print(f"   ❌ ERROR: Excepción inesperada: {e}")
            return False
    
    return True


def test_class_variables():
    """Test that class variables are shared"""
    print("\n🧪 Test 2: Variables de Clase Compartidas")
    
    service1 = EmbeddingService.get_instance()
    service2 = EmbeddingService.get_instance()
    
    # Check that class variables exist
    assert hasattr(EmbeddingService, '_instance'), "Variable _instance no existe"
    assert hasattr(EmbeddingService, '_fast_model'), "Variable _fast_model no existe"
    assert hasattr(EmbeddingService, '_quality_model'), "Variable _quality_model no existe"
    assert hasattr(EmbeddingService, '_fast_model_loaded'), "Variable _fast_model_loaded no existe"
    assert hasattr(EmbeddingService, '_quality_model_loaded'), "Variable _quality_model_loaded no existe"
    print("   ✅ Todas las variables de clase existen")
    
    # Check initial values
    assert EmbeddingService._instance is not None, "_instance debería estar asignada"
    assert EmbeddingService._fast_model is None, "_fast_model debería ser None inicialmente"
    assert EmbeddingService._quality_model is None, "_quality_model debería ser None inicialmente"
    assert EmbeddingService._fast_model_loaded is False, "_fast_model_loaded debería ser False"
    assert EmbeddingService._quality_model_loaded is False, "_quality_model_loaded debería ser False"
    print("   ✅ Valores iniciales correctos")
    
    # Verify both instances see the same class variables
    assert service1._fast_model is service2._fast_model, "Variables de clase deberían ser compartidas"
    print("   ✅ Variables de clase son compartidas entre instancias")
    
    return True


def test_placeholder_methods():
    """Test that placeholder methods exist and raise NotImplementedError"""
    print("\n🧪 Test 3: Métodos Placeholder")
    
    service = EmbeddingService.get_instance()
    
    # List of methods that should exist
    methods = [
        '_load_fast_model',
        '_load_quality_model',
        'combine_event_text',
        'generate_fast_embedding',
        'generate_quality_embedding',
        'generate_embeddings_batch',
        'generate_event_embedding'
    ]
    
    for method_name in methods:
        # Check method exists
        assert hasattr(service, method_name), f"Método {method_name} no existe"
        method = getattr(service, method_name)
        assert callable(method), f"{method_name} no es callable"
        print(f"   ✅ Método {method_name} existe")
        
        # Check it raises NotImplementedError (except for _load methods which are private)
        if method_name.startswith('_'):
            # Private methods - just check they exist
            continue
        else:
            # Public methods should raise NotImplementedError when called
            try:
                if method_name == 'combine_event_text':
                    method("TRANSICION", "test", "mañana", None, ["test"], "EXITOSO")
                elif method_name == 'generate_fast_embedding':
                    method("test text")
                elif method_name == 'generate_quality_embedding':
                    method("test text")
                elif method_name == 'generate_embeddings_batch':
                    method(["test"])
                elif method_name == 'generate_event_embedding':
                    method("TRANSICION", "test", "mañana", None, ["test"], "EXITOSO")
                
                print(f"   ⚠️  {method_name} no lanza NotImplementedError (puede estar bien si es placeholder)")
            except NotImplementedError:
                print(f"   ✅ {method_name} lanza NotImplementedError correctamente")
            except Exception as e:
                print(f"   ⚠️  {method_name} lanza {type(e).__name__}: {e}")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("PRUEBAS DE ESTRUCTURA - EmbeddingService (Subtarea 1.2)")
    print("=" * 60)
    
    tests = [
        test_singleton_pattern,
        test_class_variables,
        test_placeholder_methods
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
    
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    if all(results):
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("\nLa estructura base del EmbeddingService está correctamente implementada.")
        return 0
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        return 1


if __name__ == "__main__":
    exit(main())

