"""
Test script to verify lazy loading of embedding models (Subtarea 1.3)

Tests:
1. Models are not loaded initially
2. Fast model loads when first accessed
3. Fast model doesn't reload if already loaded
4. Quality model loads when first accessed
5. Quality model doesn't reload if already loaded
6. Both models can be loaded simultaneously
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embeddingService import EmbeddingService


def test_initial_state():
    """Test that models are not loaded initially"""
    print("🧪 Test 1: Estado Inicial")
    
    # Reset the service (for testing)
    EmbeddingService._instance = None
    EmbeddingService._fast_model = None
    EmbeddingService._quality_model = None
    EmbeddingService._fast_model_loaded = False
    EmbeddingService._quality_model_loaded = False
    
    service = EmbeddingService.get_instance()
    
    # Check initial state
    assert EmbeddingService._fast_model is None, "Modelo rápido debería ser None inicialmente"
    assert EmbeddingService._quality_model is None, "Modelo calidad debería ser None inicialmente"
    assert EmbeddingService._fast_model_loaded is False, "Flag rápido debería ser False"
    assert EmbeddingService._quality_model_loaded is False, "Flag calidad debería ser False"
    
    print("   ✅ Modelos no están cargados inicialmente")
    return True


def test_fast_model_lazy_load():
    """Test that fast model loads only when needed"""
    print("\n🧪 Test 2: Carga Lazy del Modelo Rápido")
    
    # Reset
    EmbeddingService._instance = None
    EmbeddingService._fast_model = None
    EmbeddingService._quality_model = None
    EmbeddingService._fast_model_loaded = False
    EmbeddingService._quality_model_loaded = False
    
    service = EmbeddingService.get_instance()
    
    # Verify not loaded
    assert EmbeddingService._fast_model is None, "Modelo no debería estar cargado"
    print("   ✅ Modelo rápido no está cargado antes de llamar _load_fast_model()")
    
    # Load the model
    print("   ⏳ Cargando modelo rápido (esto puede tardar unos segundos la primera vez)...")
    start_time = time.time()
    service._load_fast_model()
    load_time = time.time() - start_time
    
    # Verify loaded
    assert EmbeddingService._fast_model is not None, "Modelo debería estar cargado"
    assert EmbeddingService._fast_model_loaded is True, "Flag debería ser True"
    print(f"   ✅ Modelo rápido cargado en {load_time:.2f} segundos")
    
    # Verify model is a SentenceTransformer
    assert hasattr(EmbeddingService._fast_model, 'encode'), "Modelo debería tener método encode"
    print("   ✅ Modelo tiene método encode() (es un SentenceTransformer)")
    
    return True


def test_fast_model_no_reload():
    """Test that fast model doesn't reload if already loaded"""
    print("\n🧪 Test 3: Modelo Rápido No Se Recarga")
    
    service = EmbeddingService.get_instance()
    
    # Ensure model is loaded
    if not EmbeddingService._fast_model_loaded:
        service._load_fast_model()
    
    # Get reference to current model
    original_model = EmbeddingService._fast_model
    
    # Try to load again
    print("   ⏳ Intentando cargar modelo rápido de nuevo...")
    start_time = time.time()
    service._load_fast_model()
    reload_time = time.time() - start_time
    
    # Verify it's the same model (not reloaded)
    assert EmbeddingService._fast_model is original_model, "Debería ser el mismo modelo (no recargado)"
    assert reload_time < 0.1, f"Recarga debería ser instantánea (<0.1s), tomó {reload_time:.2f}s"
    print(f"   ✅ Modelo no se recargó (verificación instantánea: {reload_time:.4f}s)")
    
    return True


def test_quality_model_lazy_load():
    """Test that quality model loads only when needed"""
    print("\n🧪 Test 4: Carga Lazy del Modelo Calidad")
    
    # Reset only quality model
    EmbeddingService._quality_model = None
    EmbeddingService._quality_model_loaded = False
    
    service = EmbeddingService.get_instance()
    
    # Verify not loaded
    assert EmbeddingService._quality_model is None, "Modelo no debería estar cargado"
    print("   ✅ Modelo calidad no está cargado antes de llamar _load_quality_model()")
    
    # Load the model
    print("   ⏳ Cargando modelo calidad (esto puede tardar unos segundos la primera vez)...")
    start_time = time.time()
    service._load_quality_model()
    load_time = time.time() - start_time
    
    # Verify loaded
    assert EmbeddingService._quality_model is not None, "Modelo debería estar cargado"
    assert EmbeddingService._quality_model_loaded is True, "Flag debería ser True"
    print(f"   ✅ Modelo calidad cargado en {load_time:.2f} segundos")
    
    # Verify model is a SentenceTransformer
    assert hasattr(EmbeddingService._quality_model, 'encode'), "Modelo debería tener método encode"
    print("   ✅ Modelo tiene método encode() (es un SentenceTransformer)")
    
    return True


def test_quality_model_no_reload():
    """Test that quality model doesn't reload if already loaded"""
    print("\n🧪 Test 5: Modelo Calidad No Se Recarga")
    
    service = EmbeddingService.get_instance()
    
    # Ensure model is loaded
    if not EmbeddingService._quality_model_loaded:
        service._load_quality_model()
    
    # Get reference to current model
    original_model = EmbeddingService._quality_model
    
    # Try to load again
    print("   ⏳ Intentando cargar modelo calidad de nuevo...")
    start_time = time.time()
    service._load_quality_model()
    reload_time = time.time() - start_time
    
    # Verify it's the same model (not reloaded)
    assert EmbeddingService._quality_model is original_model, "Debería ser el mismo modelo (no recargado)"
    assert reload_time < 0.1, f"Recarga debería ser instantánea (<0.1s), tomó {reload_time:.2f}s"
    print(f"   ✅ Modelo no se recargó (verificación instantánea: {reload_time:.4f}s)")
    
    return True


def test_both_models_loaded():
    """Test that both models can be loaded simultaneously"""
    print("\n🧪 Test 6: Ambos Modelos Cargados Simultáneamente")
    
    service = EmbeddingService.get_instance()
    
    # Ensure both are loaded
    if not EmbeddingService._fast_model_loaded:
        service._load_fast_model()
    if not EmbeddingService._quality_model_loaded:
        service._load_quality_model()
    
    # Verify both are loaded
    assert EmbeddingService._fast_model is not None, "Modelo rápido debería estar cargado"
    assert EmbeddingService._quality_model is not None, "Modelo calidad debería estar cargado"
    assert EmbeddingService._fast_model_loaded is True, "Flag rápido debería ser True"
    assert EmbeddingService._quality_model_loaded is True, "Flag calidad debería ser True"
    
    # Verify they are different models
    assert EmbeddingService._fast_model is not EmbeddingService._quality_model, "Deberían ser modelos diferentes"
    
    print("   ✅ Ambos modelos están cargados")
    print("   ✅ Son modelos diferentes (no comparten instancia)")
    
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("PRUEBAS DE CARGA LAZY - EmbeddingService (Subtarea 1.3)")
    print("=" * 70)
    print("\n⚠️  NOTA: La primera vez que se ejecute, los modelos se descargarán")
    print("   desde internet. Esto puede tardar varios minutos.\n")
    
    tests = [
        test_initial_state,
        test_fast_model_lazy_load,
        test_fast_model_no_reload,
        test_quality_model_lazy_load,
        test_quality_model_no_reload,
        test_both_models_loaded
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except ImportError as e:
            print(f"\n❌ ERROR: {e}")
            print("   Instala sentence-transformers con: pip install sentence-transformers")
            return 1
        except Exception as e:
            print(f"\n❌ ERROR en {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 70)
    print("RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    if all(results):
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("\nLa carga lazy de modelos está correctamente implementada.")
        print("Los modelos se cargan solo cuando se necesitan y no se recargan.")
        return 0
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        return 1


if __name__ == "__main__":
    exit(main())

