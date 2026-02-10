"""
Test script for pattern analysis functionality.

Tests pattern analysis for AULA_TEA_DEMO classroom and displays:
- Clusters of similar events
- Temporal patterns (critical moments of day)
- Support effectiveness
- Pedagogical interpretation
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID
from typing import Dict, Any, List

# Add parent directory to path to import app modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

try:
    from app.models.database import AsyncSessionLocal
    from app.models.models import Event, Classroom
    from app.services.pattern_analysis import PatternAnalysisService
    from sqlalchemy import select
    from collections import Counter
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


async def analyze_patterns(classroom_id: UUID, clustering_eps: float = 0.3, clustering_min_samples: int = 2) -> Dict[str, Any]:
    """
    Perform pattern analysis for a classroom.
    
    Args:
        classroom_id: UUID of the classroom
        clustering_eps: DBSCAN eps parameter for clustering
        clustering_min_samples: DBSCAN min_samples parameter
        
    Returns:
        Dictionary with all pattern analysis results
    """
    async with AsyncSessionLocal() as session:
        # Get all events for this classroom
        result = await session.execute(
            select(Event).where(Event.classroom_id == classroom_id)
        )
        events = result.scalars().all()
        
        if not events:
            raise Exception(f"No events found for classroom {classroom_id}")
        
        # Initialize pattern analysis service
        pattern_service = PatternAnalysisService()
        
        # Perform analysis (not async, but we're in async context)
        patterns = pattern_service.analyze_all_patterns(
            classroom_id=classroom_id,
            events=events,
            clustering_eps=clustering_eps,
            clustering_min_samples=clustering_min_samples
        )
        
        return patterns, events


def print_clustering_results(clustering: Dict[str, Any], events: List[Event]):
    """Print clustering analysis results."""
    print("\n" + "="*70)
    print("📊 CLUSTERING ANALYSIS")
    print("="*70)
    
    if "error" in clustering:
        print(f"❌ Error in clustering: {clustering['error']}")
        return
    
    n_clusters = clustering.get("n_clusters", 0)
    n_outliers = clustering.get("n_outliers", 0)
    clusters = clustering.get("clusters", {})
    
    print(f"\n🔍 Clusters detected: {n_clusters}")
    print(f"📌 Outliers (events that don't fit any cluster): {n_outliers}")
    print(f"📦 Total events analyzed: {len(events)}")
    
    if n_clusters == 0:
        print("\n⚠️  No clusters detected. This could mean:")
        print("   - Events are too diverse (increase clustering_eps)")
        print("   - Not enough similar events (decrease clustering_min_samples)")
        return
    
    # Create event lookup by ID
    event_dict = {event.id: event for event in events}
    
    # Print details for each cluster
    # clusters is a list of lists, where each inner list contains event_ids
    for cluster_id, event_ids in enumerate(clusters):
        cluster_events = [event_dict[eid] for eid in event_ids if eid in event_dict]
        
        if not cluster_events:
            continue
        
        print(f"\n{'─'*70}")
        print(f"📦 Cluster {cluster_id} ({len(cluster_events)} events)")
        print(f"{'─'*70}")
        
        # Analyze event types in this cluster
        event_types = Counter(e.event_type for e in cluster_events)
        print(f"   Event types:")
        for event_type, count in event_types.most_common():
            percentage = (count / len(cluster_events)) * 100
            print(f"      - {event_type}: {count} ({percentage:.1f}%)")
        
        # Analyze results in this cluster
        results = Counter(e.result for e in cluster_events)
        print(f"   Results:")
        for result, count in results.most_common():
            percentage = (count / len(cluster_events)) * 100
            print(f"      - {result}: {count} ({percentage:.1f}%)")
        
        # Most common supports in this cluster
        all_supports = []
        for event in cluster_events:
            all_supports.extend(event.supports)
        support_counts = Counter(all_supports)
        if support_counts:
            print(f"   Most common supports:")
            for support, count in support_counts.most_common(3):
                percentage = (count / len(cluster_events)) * 100
                print(f"      - {support}: {count} times ({percentage:.1f}% of events)")
        
        # Sample descriptions
        print(f"   Sample descriptions:")
        for i, event in enumerate(cluster_events[:3], 1):
            print(f"      {i}. {event.description[:80]}..." if len(event.description) > 80 else f"      {i}. {event.description}")


def print_temporal_patterns(temporal: Dict[str, Any]):
    """Print temporal pattern analysis results."""
    print("\n" + "="*70)
    print("⏰ TEMPORAL PATTERNS")
    print("="*70)
    
    day_counts = temporal.get("day_of_week", {})
    moment_counts = temporal.get("moment_of_day", {})
    day_moment_combinations = temporal.get("day_moment_combinations", {})
    most_common_day = temporal.get("most_common_day")
    most_common_moment = temporal.get("most_common_moment")
    
    print(f"\n📅 Day of week distribution:")
    total_days = sum(day_counts.values())
    for day, count in sorted(day_counts.items()):
        percentage = (count / total_days * 100) if total_days > 0 else 0
        print(f"   - {day}: {count} events ({percentage:.1f}%)")
    
    if most_common_day:
        print(f"\n   ⚠️  Most common day: {most_common_day} ({day_counts.get(most_common_day, 0)} events)")
    
    print(f"\n🕐 Moment of day distribution:")
    total_moments = sum(moment_counts.values())
    for moment, count in sorted(moment_counts.items()):
        percentage = (count / total_moments * 100) if total_moments > 0 else 0
        print(f"   - {moment}: {count} events ({percentage:.1f}%)")
    
    if most_common_moment:
        print(f"\n   ⚠️  Most common moment: {most_common_moment} ({moment_counts.get(most_common_moment, 0)} events)")
    
    if day_moment_combinations:
        print(f"\n📊 Day-Moment combinations (top 5):")
        # day_moment_combinations is a dict with keys like "lunes_mañana"
        sorted_combos = sorted(day_moment_combinations.items(), key=lambda x: x[1], reverse=True)[:5]
        for combo_key, count in sorted_combos:
            # combo_key is like "lunes_mañana"
            parts = combo_key.split("_", 1)
            day = parts[0] if len(parts) > 0 else "unknown"
            moment = parts[1] if len(parts) > 1 else "unknown"
            percentage = (count / total_days * 100) if total_days > 0 else 0
            print(f"   - {day} {moment}: {count} events ({percentage:.1f}%)")


def print_support_effectiveness(support_effectiveness: Dict[str, Any]):
    """Print support effectiveness analysis results."""
    print("\n" + "="*70)
    print("🛠️  SUPPORT EFFECTIVENESS")
    print("="*70)
    
    success_rates = support_effectiveness.get("support_success_rates", {})
    most_effective = support_effectiveness.get("most_effective_supports", [])
    usage_counts = support_effectiveness.get("support_usage_counts", {})
    successful_combinations = support_effectiveness.get("successful_combinations", [])
    
    if not success_rates:
        print("\n⚠️  No support effectiveness data available.")
        return
    
    print(f"\n✅ Success rates by support:")
    sorted_supports = sorted(success_rates.items(), key=lambda x: x[1], reverse=True)
    for support, rate in sorted_supports:
        usage = usage_counts.get(support, 0)
        print(f"   - {support}: {rate:.1%} success rate ({usage} uses)")
    
    if most_effective:
        print(f"\n🏆 Most effective supports:")
        # most_effective is a list of dicts: [{"support": "...", "success_rate": 0.xx}, ...]
        for item in most_effective[:5]:
            support = item.get("support", "Unknown")
            rate = item.get("success_rate", 0)
            usage = usage_counts.get(support, 0)
            print(f"   - {support}: {rate:.1%} success ({usage} uses)")
    
    if successful_combinations:
        print(f"\n💡 Successful support combinations (top 5):")
        # successful_combinations is a list of dicts: [{"supports": [...], "success_rate": 0.xx, "usage_count": N}, ...]
        for combo_data in successful_combinations[:5]:
            supports = combo_data.get("supports", [])
            rate = combo_data.get("success_rate", 0)
            usage = combo_data.get("usage_count", 0)
            combo_str = " + ".join(supports)
            print(f"   - {combo_str}: {rate:.1%} success rate ({usage} uses)")


def interpret_patterns(patterns: Dict[str, Any], events: List[Event]) -> str:
    """Provide pedagogical interpretation of detected patterns."""
    print("\n" + "="*70)
    print("🎓 PEDAGOGICAL INTERPRETATION")
    print("="*70)
    
    interpretations = []
    
    # Clustering interpretation
    clustering = patterns.get("clustering", {})
    if "error" not in clustering:
        n_clusters = clustering.get("n_clusters", 0)
        if n_clusters > 0:
            interpretations.append(f"✅ Se detectaron {n_clusters} grupos de eventos similares, lo que sugiere patrones recurrentes en el aula.")
        else:
            interpretations.append("⚠️  No se detectaron clusters claros. Los eventos pueden ser muy diversos o necesitar más datos.")
    
    # Temporal interpretation
    temporal = patterns.get("temporal_patterns", {})
    most_common_moment = temporal.get("most_common_moment")
    if most_common_moment:
        moment_count = temporal.get("moment_of_day", {}).get(most_common_moment, 0)
        total_events = len(events)
        percentage = (moment_count / total_events * 100) if total_events > 0 else 0
        interpretations.append(f"⏰ El momento más común es '{most_common_moment}' ({percentage:.1f}% de eventos), lo que puede indicar momentos críticos del día.")
    
    # Support effectiveness interpretation
    support_effectiveness = patterns.get("support_effectiveness", {})
    most_effective = support_effectiveness.get("most_effective_supports", [])
    if most_effective:
        # most_effective is a list of dicts: [{"support": "...", "success_rate": 0.xx}, ...]
        top_support_item = most_effective[0]
        top_support = top_support_item.get("support", "Unknown") if isinstance(top_support_item, dict) else top_support_item
        rate = top_support_item.get("success_rate", 0) if isinstance(top_support_item, dict) else support_effectiveness.get("support_success_rates", {}).get(top_support, 0)
        interpretations.append(f"🛠️  El apoyo más efectivo es '{top_support}' ({rate:.1%} de éxito), lo que sugiere que funciona bien en este contexto.")
    
    # Overall assessment
    if not interpretations:
        interpretations.append("⚠️  No se detectaron patrones claros. Puede ser necesario más tiempo de observación o ajustar los parámetros de análisis.")
    
    print("\n📝 Interpretación:")
    for i, interpretation in enumerate(interpretations, 1):
        print(f"   {i}. {interpretation}")
    
    # Pedagogical recommendations
    print("\n💡 Recomendaciones pedagógicas:")
    if most_effective:
        top_support = most_effective[0].get("support", "Unknown") if isinstance(most_effective[0], dict) else most_effective[0]
        print(f"   - Considera usar '{top_support}' más frecuentemente, ya que muestra alta efectividad.")
    
    most_common_moment = temporal.get("most_common_moment")
    if most_common_moment:
        print(f"   - Presta especial atención al momento '{most_common_moment}', donde ocurren más eventos.")
    
    n_clusters = clustering.get("n_clusters", 0)
    if n_clusters > 0:
        print(f"   - Los {n_clusters} grupos detectados pueden ayudar a identificar situaciones similares y aplicar estrategias probadas.")
    
    return "\n".join(interpretations)


async def main():
    """Main function to run pattern analysis test."""
    print("="*70)
    print("🧪 Pattern Analysis Test Script")
    print("="*70)
    
    try:
        # Find demo classroom
        print("\n🔍 Looking for AULA_TEA_DEMO classroom...")
        classroom_id = await find_demo_classroom()
        print(f"✅ Found classroom: {classroom_id}")
        
        # Run pattern analysis
        print("\n📊 Running pattern analysis...")
        print("   Parameters: clustering_eps=0.3, clustering_min_samples=2")
        
        patterns, events = await analyze_patterns(
            classroom_id=classroom_id,
            clustering_eps=0.3,
            clustering_min_samples=2
        )
        
        print(f"✅ Analysis complete! Analyzed {len(events)} events.")
        
        # Display results
        print_clustering_results(patterns.get("clustering", {}), events)
        print_temporal_patterns(patterns.get("temporal_patterns", {}))
        print_support_effectiveness(patterns.get("support_effectiveness", {}))
        interpret_patterns(patterns, events)
        
        print("\n" + "="*70)
        print("✅ Pattern analysis test completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during pattern analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

