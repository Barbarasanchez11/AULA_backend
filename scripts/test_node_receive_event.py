"""
Script de prueba para el Nodo 1: receive_event

Este script prueba la funcionalidad del nodo receive_event de LangGraph:
- Validación de classroom_id
- Carga de evento desde BD (si event_id existe)
- Validación de event_data (si se proporciona)
- Manejo de errores

Uso:
    python scripts/test_node_receive_event.py
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the node using importlib to avoid loading __init__.py files
# that would trigger imports of LangGraphService -> PatternAnalysisService -> EmbeddingService -> sentence-transformers
# This allows testing the node in isolation without requiring PyTorch/ML dependencies
import importlib.util

# Import state first (it's just a TypedDict, no dependencies)
from app.services.langgraph.state import RecommendationState

# Import node directly from file to bypass package __init__.py
node_file = project_root / "app" / "services" / "langgraph" / "nodes" / "receive_event.py"
spec = importlib.util.spec_from_file_location("receive_event_node", node_file)
receive_event_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receive_event_module)
node_receive_event = receive_event_module.node_receive_event
from app.models.database import AsyncSessionLocal
from app.models.models import Classroom
from sqlalchemy import select


async def find_or_create_demo_classroom() -> UUID:
    """Find or create the demo classroom (AULA_TEA_DEMO)"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Classroom).where(Classroom.name == "AULA_TEA_DEMO")
        )
        classroom = result.scalar_one_or_none()
        
        if not classroom:
            # Create the classroom if it doesn't exist
            print("  ℹ️  AULA_TEA_DEMO not found. Creating it...")
            classroom = Classroom(
                name="AULA_TEA_DEMO",
                type="TEA",
                extra_metadata={"demo": True, "purpose": "Testing and demonstration"}
            )
            db.add(classroom)
            await db.commit()
            await db.refresh(classroom)
            print(f"  ✅ Created AULA_TEA_DEMO (ID: {classroom.id})")
        
        return classroom.id


def print_state_summary(state: RecommendationState, test_name: str):
    """Print a summary of the state after node execution"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    print(f"\n✅ Event Data:")
    if state.get("event_data"):
        event_data = state["event_data"]
        print(f"  - ID: {event_data.get('id', 'N/A')}")
        print(f"  - Type: {event_data.get('event_type', 'N/A')}")
        print(f"  - Description: {event_data.get('description', 'N/A')[:50]}...")
        print(f"  - Result: {event_data.get('result', 'N/A')}")
    else:
        print("  - No event_data in state")
    
    print(f"\n📊 Metadata:")
    metadata = state.get("metadata", {})
    for key, value in metadata.items():
        print(f"  - {key}: {value}")
    
    print(f"\n❌ Errors ({len(state.get('errors', []))}):")
    errors = state.get("errors", [])
    if errors:
        for i, error in enumerate(errors, 1):
            print(f"  {i}. [{error.get('severity', 'unknown')}] {error.get('message', 'No message')}")
    else:
        print("  - No errors")
    
    print(f"\n{'='*60}\n")


async def test_1_load_event_by_id():
    """Test 1: Load event by event_id"""
    print("\n🧪 TEST 1: Load event by event_id")
    
    classroom_id = await find_or_create_demo_classroom()
    
    # We need to get an event_id from the classroom
    # For now, we'll use a placeholder - in real test, query an event
    from app.models.models import Event
    from app.schemas.enums import EventType, EventResult, MomentOfDay, SupportType
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Event).where(Event.classroom_id == classroom_id).limit(1)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            print("  ℹ️  No events found in classroom. Creating a test event...")
            # Create a test event
            test_event = Event(
                classroom_id=classroom_id,
                event_type=EventType.TRANSICION.value,
                description="Evento de prueba para test del nodo receive_event",
                moment_of_day=MomentOfDay.MORNING.value,
                day_of_week=None,
                duration_minutes=15,
                supports=[SupportType.VISUAL_ANTICIPATION.value],
                additional_supports=None,
                result=EventResult.EXITOSO.value,
                observations="Evento creado automáticamente para testing"
            )
            db.add(test_event)
            await db.commit()
            await db.refresh(test_event)
            event_id = test_event.id
            print(f"  ✅ Created test event (ID: {event_id})")
        else:
            event_id = event.id
            print(f"  ℹ️  Using existing event (ID: {event_id})")
    
    state: RecommendationState = {
        "classroom_id": classroom_id,
        "event_id": event_id,
        "event_data": None,
        "similar_events": [],
        "patterns": {},
        "context_for_llm": None,
        "llm_response": None,
        "llm_metadata": None,
        "recommendation": None,
        "confidence": None,
        "errors": [],
        "metadata": {}
    }
    
    result_state = node_receive_event(state)
    print_state_summary(result_state, "Load event by event_id")
    
    # Validate success
    assert result_state.get("event_data") is not None, "event_data should be loaded"
    assert len(result_state.get("errors", [])) == 0, "Should have no errors"
    print("  ✅ Test 1 PASSED")


async def test_2_validate_event_data():
    """Test 2: Validate event_data provided directly"""
    print("\n🧪 TEST 2: Validate event_data provided directly")
    
    classroom_id = await find_or_create_demo_classroom()
    
    event_data = {
        "event_type": "TRANSICION",
        "description": "El estudiante tuvo dificultades durante la transición del recreo al aula",
        "context": {
            "moment_of_day": "tarde",
            "day_of_week": "lunes",
            "duration_minutes": 15
        },
        "supports": ["Anticipación visual", "Mediación verbal"],
        "result": "DIFICULTAD",
        "observations": "Necesita más tiempo para la transición"
    }
    
    state: RecommendationState = {
        "classroom_id": classroom_id,
        "event_id": None,
        "event_data": event_data,
        "similar_events": [],
        "patterns": {},
        "context_for_llm": None,
        "llm_response": None,
        "llm_metadata": None,
        "recommendation": None,
        "confidence": None,
        "errors": [],
        "metadata": {}
    }
    
    result_state = node_receive_event(state)
    print_state_summary(result_state, "Validate event_data")
    
    # Validate success
    assert result_state.get("event_data") is not None, "event_data should be validated"
    assert len(result_state.get("errors", [])) == 0, "Should have no errors"
    print("  ✅ Test 2 PASSED")


async def test_3_invalid_classroom():
    """Test 3: Invalid classroom_id"""
    print("\n🧪 TEST 3: Invalid classroom_id")
    
    fake_classroom_id = UUID("00000000-0000-0000-0000-000000000000")
    
    state: RecommendationState = {
        "classroom_id": fake_classroom_id,
        "event_id": None,
        "event_data": {
            "event_type": "TRANSICION",
            "description": "Test description with enough characters",
            "context": {"moment_of_day": "mañana"},
            "supports": ["Anticipación visual"],
            "result": "EXITOSO"
        },
        "similar_events": [],
        "patterns": {},
        "context_for_llm": None,
        "llm_response": None,
        "llm_metadata": None,
        "recommendation": None,
        "confidence": None,
        "errors": [],
        "metadata": {}
    }
    
    result_state = node_receive_event(state)
    print_state_summary(result_state, "Invalid classroom_id")
    
    # Validate error
    errors = result_state.get("errors", [])
    assert len(errors) > 0, "Should have errors for invalid classroom"
    assert any("not found" in err.get("message", "").lower() for err in errors), "Should have 'not found' error"
    print("  ✅ Test 3 PASSED (correctly detected error)")


async def test_4_invalid_event_data():
    """Test 4: Invalid event_data structure"""
    print("\n🧪 TEST 4: Invalid event_data structure")
    
    classroom_id = await find_or_create_demo_classroom()
    
    # Missing required fields
    invalid_event_data = {
        "event_type": "TRANSICION",
        # Missing description, context, supports, result
    }
    
    state: RecommendationState = {
        "classroom_id": classroom_id,
        "event_id": None,
        "event_data": invalid_event_data,
        "similar_events": [],
        "patterns": {},
        "context_for_llm": None,
        "llm_response": None,
        "llm_metadata": None,
        "recommendation": None,
        "confidence": None,
        "errors": [],
        "metadata": {}
    }
    
    result_state = node_receive_event(state)
    print_state_summary(result_state, "Invalid event_data")
    
    # Validate error
    errors = result_state.get("errors", [])
    assert len(errors) > 0, "Should have errors for invalid event_data"
    assert any("missing" in err.get("message", "").lower() for err in errors), "Should have 'missing' error"
    print("  ✅ Test 4 PASSED (correctly detected error)")


async def test_5_no_event_data():
    """Test 5: Neither event_id nor event_data provided"""
    print("\n🧪 TEST 5: Neither event_id nor event_data provided")
    
    classroom_id = await find_or_create_demo_classroom()
    
    state: RecommendationState = {
        "classroom_id": classroom_id,
        "event_id": None,
        "event_data": None,
        "similar_events": [],
        "patterns": {},
        "context_for_llm": None,
        "llm_response": None,
        "llm_metadata": None,
        "recommendation": None,
        "confidence": None,
        "errors": [],
        "metadata": {}
    }
    
    result_state = node_receive_event(state)
    print_state_summary(result_state, "No event data")
    
    # Validate error
    errors = result_state.get("errors", [])
    assert len(errors) > 0, "Should have errors when no event data provided"
    assert any("either" in err.get("message", "").lower() for err in errors), "Should have 'either' error message"
    print("  ✅ Test 5 PASSED (correctly detected error)")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TESTING NODE 1: receive_event")
    print("="*60)
    
    try:
        await test_1_load_event_by_id()
        await test_2_validate_event_data()
        await test_3_invalid_classroom()
        await test_4_invalid_event_data()
        await test_5_no_event_data()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

