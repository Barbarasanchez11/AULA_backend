"""
Test script to verify combine_event_text function (Subtarea 1.4)

Tests:
1. Combines all mandatory fields correctly
2. Handles optional fields (None values)
3. Formats lists correctly
4. Produces coherent text output
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embeddingService import EmbeddingService


def test_combine_all_fields():
    """Test combining all fields including optional ones"""
    print("🧪 Test 1: Combinar Todos los Campos")
    
    service = EmbeddingService.get_instance()
    
    result = service.combine_event_text(
        event_type="TRANSICION",
        description="Transición de juego libre a asamblea matutina",
        moment_of_day="mañana",
        day_of_week="lunes",
        supports=["Anticipación visual", "Mediación verbal"],
        result="EXITOSO",
        additional_supports="Se utilizó música de fondo",
        observations="Todos se incorporaron sin dificultades"
    )
    
    # Verify structure
    assert "TRANSICION" in result, "Debe incluir el tipo de evento"
    assert "Transición de juego libre a asamblea matutina" in result, "Debe incluir la descripción"
    assert "Momento: mañana" in result, "Debe incluir el momento del día"
    assert "Día: lunes" in result, "Debe incluir el día de la semana"
    assert "Anticipación visual" in result, "Debe incluir los apoyos"
    assert "Mediación verbal" in result, "Debe incluir todos los apoyos"
    assert "Se utilizó música de fondo" in result, "Debe incluir apoyos adicionales"
    assert "Resultado: EXITOSO" in result, "Debe incluir el resultado"
    assert "Todos se incorporaron sin dificultades" in result, "Debe incluir observaciones"
    
    print("   ✅ Todos los campos incluidos correctamente")
    print(f"   📝 Texto resultante: {result[:100]}...")
    return True


def test_combine_mandatory_fields_only():
    """Test combining only mandatory fields (no optional ones)"""
    print("\n🧪 Test 2: Solo Campos Obligatorios")
    
    service = EmbeddingService.get_instance()
    
    result = service.combine_event_text(
        event_type="APRENDIZAJE",
        description="Actividad de trabajo en mesa individual",
        moment_of_day="tarde",
        day_of_week=None,  # Opcional
        supports=["Adaptación del entorno"],
        result="PARCIAL",
        additional_supports=None,  # Opcional
        observations=None  # Opcional
    )
    
    # Verify mandatory fields are present
    assert "APRENDIZAJE" in result, "Debe incluir el tipo de evento"
    assert "Actividad de trabajo en mesa individual" in result, "Debe incluir la descripción"
    assert "Momento: tarde" in result, "Debe incluir el momento del día"
    assert "Adaptación del entorno" in result, "Debe incluir los apoyos"
    assert "Resultado: PARCIAL" in result, "Debe incluir el resultado"
    
    # Verify optional fields are NOT present
    assert "Día:" not in result, "No debe incluir día si es None"
    assert "Observaciones:" not in result, "No debe incluir observaciones si es None"
    
    print("   ✅ Solo campos obligatorios incluidos")
    print(f"   📝 Texto resultante: {result}")
    return True


def test_combine_with_day_of_week():
    """Test combining with day_of_week but no observations"""
    print("\n🧪 Test 3: Con Día de Semana, Sin Observaciones")
    
    service = EmbeddingService.get_instance()
    
    result = service.combine_event_text(
        event_type="CAMBIO_DE_RUTINA",
        description="Modificación del horario de recreo",
        moment_of_day="mediodia",
        day_of_week="viernes",
        supports=["Anticipación visual", "Adaptación del entorno"],
        result="DIFICULTAD",
        additional_supports=None,
        observations=None
    )
    
    # Verify structure
    assert "CAMBIO_DE_RUTINA" in result
    assert "Día: viernes" in result, "Debe incluir el día si se proporciona"
    assert "Observaciones:" not in result, "No debe incluir observaciones si es None"
    
    print("   ✅ Campos correctamente combinados")
    print(f"   📝 Texto resultante: {result}")
    return True


def test_combine_with_additional_supports():
    """Test combining with additional_supports"""
    print("\n🧪 Test 4: Con Apoyos Adicionales")
    
    service = EmbeddingService.get_instance()
    
    result = service.combine_event_text(
        event_type="REGULACION",
        description="Momento de regulación emocional",
        moment_of_day="tarde",
        day_of_week=None,
        supports=["Pausa sensorial", "Espacio tranquilo"],
        result="EXITOSO",
        additional_supports="Se utilizó música relajante",
        observations="El estudiante se calmó rápidamente"
    )
    
    # Verify additional_supports is included
    assert "Pausa sensorial" in result, "Debe incluir apoyos predefinidos"
    assert "Se utilizó música relajante" in result, "Debe incluir apoyos adicionales"
    assert "El estudiante se calmó rápidamente" in result, "Debe incluir observaciones"
    
    print("   ✅ Apoyos adicionales incluidos correctamente")
    print(f"   📝 Texto resultante: {result}")
    return True


def test_multiple_supports_formatting():
    """Test that multiple supports are formatted correctly"""
    print("\n🧪 Test 5: Formato de Múltiples Apoyos")
    
    service = EmbeddingService.get_instance()
    
    result = service.combine_event_text(
        event_type="TRANSICION",
        description="Cambio de actividad",
        moment_of_day="mañana",
        day_of_week="martes",
        supports=["Anticipación visual", "Mediación verbal", "Apoyo individual del adulto"],
        result="EXITOSO",
        additional_supports=None,
        observations=None
    )
    
    # Verify all supports are present and separated by commas
    assert "Anticipación visual" in result
    assert "Mediación verbal" in result
    assert "Apoyo individual del adulto" in result
    
    # Check that supports are in the "Apoyos utilizados:" section
    supports_section = result.split("Apoyos utilizados:")[1].split("Resultado:")[0]
    assert "Anticipación visual" in supports_section
    assert "Mediación verbal" in supports_section
    
    print("   ✅ Múltiples apoyos formateados correctamente")
    print(f"   📝 Texto resultante: {result}")
    return True


def test_empty_additional_supports():
    """Test that empty or whitespace-only additional_supports is ignored"""
    print("\n🧪 Test 6: Apoyos Adicionales Vacíos")
    
    service = EmbeddingService.get_instance()
    
    # Test with empty string
    result1 = service.combine_event_text(
        event_type="APRENDIZAJE",
        description="Actividad de aprendizaje",
        moment_of_day="mañana",
        day_of_week=None,
        supports=["Adaptación del entorno"],
        result="EXITOSO",
        additional_supports="",  # Empty string
        observations=None
    )
    
    # Test with whitespace only
    result2 = service.combine_event_text(
        event_type="APRENDIZAJE",
        description="Actividad de aprendizaje",
        moment_of_day="mañana",
        day_of_week=None,
        supports=["Adaptación del entorno"],
        result="EXITOSO",
        additional_supports="   ",  # Whitespace only
        observations=None
    )
    
    # Both should produce the same result (no additional_supports section)
    assert result1 == result2, "Strings vacíos y whitespace deberían tratarse igual"
    
    print("   ✅ Apoyos adicionales vacíos ignorados correctamente")
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("PRUEBAS DE COMBINACIÓN DE TEXTO - EmbeddingService (Subtarea 1.4)")
    print("=" * 70)
    
    tests = [
        test_combine_all_fields,
        test_combine_mandatory_fields_only,
        test_combine_with_day_of_week,
        test_combine_with_additional_supports,
        test_multiple_supports_formatting,
        test_empty_additional_supports
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
    
    if all(results):
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("\nLa función combine_event_text() está correctamente implementada.")
        print("Combina todos los campos del evento en un texto coherente.")
        return 0
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        return 1


if __name__ == "__main__":
    exit(main())

