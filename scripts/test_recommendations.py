"""
Test script for recommendation generation functionality.

Tests recommendation generation for AULA_TEA_DEMO classroom and displays:
- Each recommendation with title, description, reasoning, and confidence
- Evaluation of usefulness and clarity
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID
from typing import List, Dict, Any

# Add parent directory to path to import app modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

try:
    from app.models.database import AsyncSessionLocal
    from app.models.models import Event, Classroom
    from app.services.pattern_analysis import PatternAnalysisService
    from app.services.recommendation_generator import RecommendationGenerator
    from app.schemas.enums import RecommendationType, ConfidenceLevel
    from sqlalchemy import select
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("\nPlease ensure:")
    print("  1. You are in the project root directory")
    print("  2. Your virtual environment is activated (`source venv/bin/activate`)")
    print("  3. All dependencies are installed (`pip install -r requirements.txt`)")
    sys.exit(1)


async def find_demo_classroom() -> UUID:
    """Finds the ID of the 'AULA_TEA_DEMO' classroom."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Classroom).where(Classroom.name == "AULA_TEA_DEMO")
        )
        classroom = result.scalar_one_or_none()
        if not classroom:
            raise Exception("Classroom 'AULA_TEA_DEMO' not found. Please run create_demo_classroom.py first.")
        return classroom.id


async def generate_recommendations(
    classroom_id: UUID,
    clustering_eps: float = 0.3,
    clustering_min_samples: int = 2
) -> List[Dict[str, Any]]:
    """
    Generate recommendations for a classroom.
    
    Args:
        classroom_id: UUID of the classroom
        clustering_eps: DBSCAN eps parameter for pattern analysis
        clustering_min_samples: DBSCAN min_samples parameter
        
    Returns:
        List of recommendation dictionaries
    """
    async with AsyncSessionLocal() as session:
        # Get all events for this classroom
        result = await session.execute(
            select(Event).where(Event.classroom_id == classroom_id)
        )
        events = result.scalars().all()
        
        if not events:
            raise Exception(f"No events found for classroom {classroom_id}")
        
        # 1. Analyze patterns
        pattern_service = PatternAnalysisService()
        patterns = pattern_service.analyze_all_patterns(
            classroom_id=classroom_id,
            events=events,
            clustering_eps=clustering_eps,
            clustering_min_samples=clustering_min_samples
        )
        
        # 2. Generate recommendations
        recommendation_generator = RecommendationGenerator(db_session=session)
        recommendations = await recommendation_generator.generate_all_recommendations(
            classroom_id=classroom_id,
            events=events,
            pattern_results=patterns,
            clustering_eps=clustering_eps,
            clustering_min_samples=clustering_min_samples
        )
        
        return recommendations


def format_confidence(confidence: ConfidenceLevel) -> str:
    """Format confidence level for display."""
    confidence_map = {
        ConfidenceLevel.ALTA: "🟢 ALTA",
        ConfidenceLevel.MEDIA: "🟡 MEDIA",
        ConfidenceLevel.BAJA: "🔴 BAJA"
    }
    return confidence_map.get(confidence, str(confidence.value))


def format_recommendation_type(rec_type: RecommendationType) -> str:
    """Format recommendation type for display."""
    type_map = {
        RecommendationType.ANTICIPACION: "⏰ Anticipación",
        RecommendationType.ESTRATEGIA: "🛠️  Estrategia",
        RecommendationType.ADAPTACION: "📊 Adaptación"
    }
    return type_map.get(rec_type, rec_type.value if hasattr(rec_type, 'value') else str(rec_type))


def print_recommendation(rec: Dict[str, Any], index: int):
    """Print a single recommendation in a formatted way."""
    print(f"\n{'='*70}")
    print(f"📋 Recomendación #{index + 1}")
    print(f"{'='*70}")
    
    # Type and confidence
    rec_type = rec.get("recommendation_type")
    confidence = rec.get("confidence")
    type_str = format_recommendation_type(rec_type) if rec_type else "Desconocido"
    confidence_str = format_confidence(confidence) if confidence else "Desconocido"
    
    print(f"Tipo: {type_str} | Confianza: {confidence_str}")
    print(f"{'─'*70}")
    
    # Title
    title = rec.get("title", "Sin título")
    print(f"\n📌 Título:")
    print(f"   {title}")
    
    # Description
    description = rec.get("description", "Sin descripción")
    print(f"\n📝 Descripción:")
    # Wrap long descriptions
    words = description.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > 65:  # 65 chars per line (70 - 5 for indent)
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(" ".join(current_line))
    
    for line in lines:
        print(f"   {line}")
    
    # Why it's recommended (detected pattern)
    detected_pattern = rec.get("detected_pattern", "Sin patrón detectado")
    print(f"\n🔍 Por qué se recomienda:")
    # Wrap long patterns
    words = detected_pattern.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > 65:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(" ".join(current_line))
    
    for line in lines:
        print(f"   {line}")
    
    # Applicable context
    applicable_context = rec.get("applicable_context", "Sin contexto especificado")
    print(f"\n💡 Cuándo aplicar:")
    # Wrap long contexts
    words = applicable_context.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > 65:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(" ".join(current_line))
    
    for line in lines:
        print(f"   {line}")


def evaluate_recommendations(recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate if recommendations are useful and clear."""
    if not recommendations:
        return {
            "total": 0,
            "useful": 0,
            "clear": 0,
            "high_confidence": 0,
            "evaluation": "No hay recomendaciones para evaluar."
        }
    
    total = len(recommendations)
    useful_count = 0
    clear_count = 0
    high_confidence_count = 0
    
    for rec in recommendations:
        # Check if useful (has title, description, and detected_pattern)
        has_title = bool(rec.get("title", "").strip())
        has_description = bool(rec.get("description", "").strip())
        has_pattern = bool(rec.get("detected_pattern", "").strip())
        has_context = bool(rec.get("applicable_context", "").strip())
        
        if has_title and has_description and has_pattern and has_context:
            useful_count += 1
        
        # Check if clear (description is not too short, not too long)
        description = rec.get("description", "")
        if 50 <= len(description) <= 500:
            clear_count += 1
        
        # Check confidence
        confidence = rec.get("confidence")
        if confidence == ConfidenceLevel.ALTA:
            high_confidence_count += 1
    
    useful_percentage = (useful_count / total * 100) if total > 0 else 0
    clear_percentage = (clear_count / total * 100) if total > 0 else 0
    high_confidence_percentage = (high_confidence_count / total * 100) if total > 0 else 0
    
    # Overall evaluation
    if useful_percentage >= 80 and clear_percentage >= 80:
        evaluation = "✅ Las recomendaciones son muy útiles y claras."
    elif useful_percentage >= 60 and clear_percentage >= 60:
        evaluation = "✅ Las recomendaciones son útiles y claras en general."
    elif useful_percentage >= 40:
        evaluation = "⚠️  Las recomendaciones son parcialmente útiles. Algunas necesitan más información."
    else:
        evaluation = "❌ Las recomendaciones necesitan mejoras. Faltan datos importantes."
    
    return {
        "total": total,
        "useful": useful_count,
        "clear": clear_count,
        "high_confidence": high_confidence_count,
        "useful_percentage": useful_percentage,
        "clear_percentage": clear_percentage,
        "high_confidence_percentage": high_confidence_percentage,
        "evaluation": evaluation
    }


async def main():
    """Main function to run recommendation generation test."""
    print("="*70)
    print("🧪 Recommendation Generation Test Script")
    print("="*70)
    
    try:
        # Find demo classroom
        print("\n🔍 Looking for AULA_TEA_DEMO classroom...")
        classroom_id = await find_demo_classroom()
        print(f"✅ Found classroom: {classroom_id}")
        
        # Generate recommendations
        print("\n📊 Generating recommendations...")
        print("   Parameters: clustering_eps=0.3, clustering_min_samples=2")
        
        recommendations = await generate_recommendations(
            classroom_id=classroom_id,
            clustering_eps=0.3,
            clustering_min_samples=2
        )
        
        if not recommendations:
            print("\n⚠️  No recommendations generated.")
            print("   This could mean:")
            print("   - Not enough events to detect patterns")
            print("   - Patterns are not strong enough")
            print("   - Try adjusting clustering parameters")
            return
        
        print(f"✅ Generated {len(recommendations)} recommendations\n")
        
        # Display each recommendation
        for i, rec in enumerate(recommendations):
            print_recommendation(rec, i)
        
        # Evaluate recommendations
        print("\n" + "="*70)
        print("📊 EVALUATION")
        print("="*70)
        
        evaluation = evaluate_recommendations(recommendations)
        
        print(f"\n📈 Statistics:")
        print(f"   Total recommendations: {evaluation['total']}")
        print(f"   Useful (complete info): {evaluation['useful']}/{evaluation['total']} ({evaluation['useful_percentage']:.1f}%)")
        print(f"   Clear (good length): {evaluation['clear']}/{evaluation['total']} ({evaluation['clear_percentage']:.1f}%)")
        print(f"   High confidence: {evaluation['high_confidence']}/{evaluation['total']} ({evaluation['high_confidence_percentage']:.1f}%)")
        
        print(f"\n🎯 Overall Assessment:")
        print(f"   {evaluation['evaluation']}")
        
        # Additional insights
        print(f"\n💡 Insights:")
        if evaluation['high_confidence_percentage'] >= 50:
            print(f"   ✅ Más del 50% de las recomendaciones tienen confianza alta.")
        else:
            print(f"   ⚠️  Menos del 50% de las recomendaciones tienen confianza alta.")
            print(f"      Considera recopilar más eventos para fortalecer los patrones.")
        
        if evaluation['useful_percentage'] < 100:
            print(f"   ⚠️  Algunas recomendaciones faltan información importante.")
            print(f"      Revisa que todos los campos estén completos.")
        
        print("\n" + "="*70)
        print("✅ Recommendation generation test completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during recommendation generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

