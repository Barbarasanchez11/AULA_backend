"""
Test script to verify lazy loading logic without downloading models (Subtarea 1.3)

This test verifies the lazy loading logic without requiring internet connection.
It uses mocks to simulate model loading.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embeddingService import EmbeddingService


class TestLazyLoadingLogic(unittest.TestCase):
    """Test lazy loading logic without actually loading models"""
    
    def setUp(self):
        """Reset service state before each test"""
        EmbeddingService._instance = None
        EmbeddingService._fast_model = None
        EmbeddingService._quality_model = None
        EmbeddingService._fast_model_loaded = False
        EmbeddingService._quality_model_loaded = False
    
    def test_initial_state(self):
        """Test that models are not loaded initially"""
        print("🧪 Test 1: Estado Inicial")
        service = EmbeddingService.get_instance()
        
        self.assertIsNone(EmbeddingService._fast_model)
        self.assertIsNone(EmbeddingService._quality_model)
        self.assertFalse(EmbeddingService._fast_model_loaded)
        self.assertFalse(EmbeddingService._quality_model_loaded)
        print("   ✅ Modelos no están cargados inicialmente")
    
    @patch('app.services.embeddingService.SentenceTransformer')
    def test_fast_model_lazy_load(self, mock_sentence_transformer):
        """Test that fast model loads only when needed"""
        print("\n🧪 Test 2: Carga Lazy del Modelo Rápido")
        
        # Mock the SentenceTransformer
        mock_model = Mock()
        mock_model.encode = Mock(return_value=[[0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        # Set SentenceTransformer to be available
        import app.services.embeddingService as es_module
        es_module.SentenceTransformer = mock_sentence_transformer
        
        service = EmbeddingService.get_instance()
        
        # Verify not loaded
        self.assertIsNone(EmbeddingService._fast_model)
        print("   ✅ Modelo rápido no está cargado antes de llamar _load_fast_model()")
        
        # Load the model
        service._load_fast_model()
        
        # Verify loaded
        self.assertIsNotNone(EmbeddingService._fast_model)
        self.assertTrue(EmbeddingService._fast_model_loaded)
        self.assertEqual(mock_sentence_transformer.call_count, 1)
        mock_sentence_transformer.assert_called_with("distiluse-base-multilingual-cased-v2")
        print("   ✅ Modelo rápido cargado correctamente")
    
    @patch('app.services.embeddingService.SentenceTransformer')
    def test_fast_model_no_reload(self, mock_sentence_transformer):
        """Test that fast model doesn't reload if already loaded"""
        print("\n🧪 Test 3: Modelo Rápido No Se Recarga")
        
        # Mock the SentenceTransformer
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        # Set SentenceTransformer to be available
        import app.services.embeddingService as es_module
        es_module.SentenceTransformer = mock_sentence_transformer
        
        service = EmbeddingService.get_instance()
        
        # Load first time
        service._load_fast_model()
        first_model = EmbeddingService._fast_model
        first_call_count = mock_sentence_transformer.call_count
        
        # Try to load again
        service._load_fast_model()
        
        # Verify it's the same model (not reloaded)
        self.assertIs(EmbeddingService._fast_model, first_model)
        self.assertEqual(mock_sentence_transformer.call_count, first_call_count)
        print("   ✅ Modelo no se recargó (mismo objeto en memoria)")
    
    @patch('app.services.embeddingService.SentenceTransformer')
    def test_quality_model_lazy_load(self, mock_sentence_transformer):
        """Test that quality model loads only when needed"""
        print("\n🧪 Test 4: Carga Lazy del Modelo Calidad")
        
        # Mock the SentenceTransformer
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        # Set SentenceTransformer to be available
        import app.services.embeddingService as es_module
        es_module.SentenceTransformer = mock_sentence_transformer
        
        service = EmbeddingService.get_instance()
        
        # Verify not loaded
        self.assertIsNone(EmbeddingService._quality_model)
        print("   ✅ Modelo calidad no está cargado antes de llamar _load_quality_model()")
        
        # Load the model
        service._load_quality_model()
        
        # Verify loaded
        self.assertIsNotNone(EmbeddingService._quality_model)
        self.assertTrue(EmbeddingService._quality_model_loaded)
        self.assertEqual(mock_sentence_transformer.call_count, 1)
        mock_sentence_transformer.assert_called_with("paraphrase-multilingual-mpnet-base-v2")
        print("   ✅ Modelo calidad cargado correctamente")
    
    @patch('app.services.embeddingService.SentenceTransformer')
    def test_quality_model_no_reload(self, mock_sentence_transformer):
        """Test that quality model doesn't reload if already loaded"""
        print("\n🧪 Test 5: Modelo Calidad No Se Recarga")
        
        # Mock the SentenceTransformer
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        # Set SentenceTransformer to be available
        import app.services.embeddingService as es_module
        es_module.SentenceTransformer = mock_sentence_transformer
        
        service = EmbeddingService.get_instance()
        
        # Load first time
        service._load_quality_model()
        first_model = EmbeddingService._quality_model
        first_call_count = mock_sentence_transformer.call_count
        
        # Try to load again
        service._load_quality_model()
        
        # Verify it's the same model (not reloaded)
        self.assertIs(EmbeddingService._quality_model, first_model)
        self.assertEqual(mock_sentence_transformer.call_count, first_call_count)
        print("   ✅ Modelo no se recargó (mismo objeto en memoria)")
    
    @patch('app.services.embeddingService.SentenceTransformer')
    def test_both_models_loaded(self, mock_sentence_transformer):
        """Test that both models can be loaded simultaneously"""
        print("\n🧪 Test 6: Ambos Modelos Cargados Simultáneamente")
        
        # Mock the SentenceTransformer to return different mocks
        mock_fast_model = Mock()
        mock_quality_model = Mock()
        
        def side_effect(model_name):
            if "distiluse" in model_name:
                return mock_fast_model
            elif "mpnet" in model_name:
                return mock_quality_model
            return Mock()
        
        mock_sentence_transformer.side_effect = side_effect
        
        # Set SentenceTransformer to be available
        import app.services.embeddingService as es_module
        es_module.SentenceTransformer = mock_sentence_transformer
        
        service = EmbeddingService.get_instance()
        
        # Load both models
        service._load_fast_model()
        service._load_quality_model()
        
        # Verify both are loaded
        self.assertIsNotNone(EmbeddingService._fast_model)
        self.assertIsNotNone(EmbeddingService._quality_model)
        self.assertTrue(EmbeddingService._fast_model_loaded)
        self.assertTrue(EmbeddingService._quality_model_loaded)
        
        # Verify they are different models
        self.assertIsNot(EmbeddingService._fast_model, EmbeddingService._quality_model)
        
        print("   ✅ Ambos modelos están cargados")
        print("   ✅ Son modelos diferentes (no comparten instancia)")


def main():
    """Run all tests"""
    print("=" * 70)
    print("PRUEBAS DE LÓGICA DE CARGA LAZY - EmbeddingService (Subtarea 1.3)")
    print("=" * 70)
    print("\n⚠️  NOTA: Este test usa mocks, no descarga modelos reales.\n")
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLazyLoadingLogic)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("\nLa lógica de carga lazy está correctamente implementada.")
        return 0
    else:
        print(f"❌ {len(result.failures)} PRUEBAS FALLARON, {len(result.errors)} ERRORES")
        return 1


if __name__ == "__main__":
    exit(main())

