"""
Interactive Demo Script for AULA+ Presentation at OdiseIA4Good

This script demonstrates the complete AI workflow:
1. Classroom data overview
2. Semantic search example
3. Pattern detection
4. Recommendation generation

Includes pauses for explanation and saves results to files.
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter

# Add parent directory to path to import app modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False
    # Fallback: simple ANSI codes
    class Fore:
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'
        RESET_ALL = '\033[0m'

try:
    from app.models.database import AsyncSessionLocal
    from app.models.models import Event, Classroom
    from app.services.pattern_analysis import PatternAnalysisService
    from app.services.recommendation_generator import RecommendationGenerator
    from app.services.embeddingService import EmbeddingService
    from app.services.vector_store import VectorStore
    from app.schemas.enums import RecommendationType, ConfidenceLevel
    from sqlalchemy import select
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("\nPlease ensure:")
    print("  1. You are in the project root directory")
    print("  2. Your virtual environment is activated (`source venv/bin/activate`)")
    print("  3. All dependencies are installed (`pip install -r requirements.txt`)")
    sys.exit(1)


# Output directory for saved results
OUTPUT_DIR = Path("demo_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def print_header(text: str, color: str = Fore.CYAN):
    """Print a formatted header."""
    if HAS_COLORS:
        print(f"\n{color}{Style.BRIGHT}{'='*70}")
        print(f"{text.center(70)}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
    else:
        print(f"\n{'='*70}")
        print(f"{text.center(70)}")
        print(f"{'='*70}\n")


def print_section(text: str, color: str = Fore.YELLOW):
    """Print a section header."""
    if HAS_COLORS:
        print(f"\n{color}{Style.BRIGHT}▶ {text}{Style.RESET_ALL}")
        print(f"{'─'*70}")
    else:
        print(f"\n▶ {text}")
        print(f"{'─'*70}")


def print_info(text: str, indent: int = 0):
    """Print informational text."""
    indent_str = " " * indent
    print(f"{indent_str}ℹ️  {text}")


def print_success(text: str, indent: int = 0):
    """Print success message."""
    indent_str = " " * indent
    if HAS_COLORS:
        print(f"{indent_str}{Fore.GREEN}✅ {text}{Style.RESET_ALL}")
    else:
        print(f"{indent_str}✅ {text}")


def print_warning(text: str, indent: int = 0):
    """Print warning message."""
    indent_str = " " * indent
    if HAS_COLORS:
        print(f"{indent_str}{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")
    else:
        print(f"{indent_str}⚠️  {text}")


def wait_for_user(message: str = "Presiona ENTER para continuar..."):
    """Wait for user to press Enter."""
    if HAS_COLORS:
        input(f"\n{Fore.MAGENTA}{Style.BRIGHT}⏸  {message}{Style.RESET_ALL}")
    else:
        input(f"\n⏸  {message}")


def save_to_file(content: str, filename: str):
    """Save content to a file in the output directory."""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print_success(f"Resultados guardados en: {filepath}")


async def find_demo_classroom() -> UUID:
    """Find the AULA_TEA_DEMO classroom."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Classroom).where(Classroom.name == "AULA_TEA_DEMO")
        )
        classroom = result.scalar_one_or_none()
        if not classroom:
            raise Exception("Classroom 'AULA_TEA_DEMO' not found. Please run create_demo_classroom.py first.")
        return classroom.id


async def get_classroom_overview(classroom_id: UUID) -> Dict[str, Any]:
    """Get overview of classroom data."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Event).where(Event.classroom_id == classroom_id)
        )
        events = result.scalars().all()
        
        if not events:
            raise Exception(f"No events found for classroom {classroom_id}")
        
        # Analyze event types
        event_types = Counter(e.event_type for e in events)
        results = Counter(e.result for e in events)
        moments = Counter(e.moment_of_day for e in events)
        
        return {
            "total_events": len(events),
            "event_types": dict(event_types),
            "results": dict(results),
            "moments": dict(moments),
            "events": events
        }


async def perform_semantic_search(classroom_id: UUID, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Perform semantic search for similar events."""
    embedding_service = EmbeddingService.get_instance()
    vector_store = VectorStore()
    
    # Generate query embedding
    query_embedding = embedding_service.generate_quality_embedding(query)
    
    # Search
    similar_results = vector_store.search_similar_events(
        classroom_id=classroom_id,
        query_embedding=query_embedding,
        top_k=top_k,
        model_type="quality",
        min_similarity=0.0
    )
    
    # Get full event details
    events_with_scores = []
    async with AsyncSessionLocal() as session:
        for result in similar_results:
            event_id = result["event_id"]
            if isinstance(event_id, str):
                event_id = UUID(event_id)
            score = result["score"]
            
            db_result = await session.execute(
                select(Event).where(Event.id == event_id)
            )
            event = db_result.scalar_one_or_none()
            
            if event:
                events_with_scores.append({
                    "event": event,
                    "score": score
                })
    
    return events_with_scores


async def analyze_patterns(classroom_id: UUID, events: List[Event]) -> Dict[str, Any]:
    """Analyze patterns in events."""
    pattern_service = PatternAnalysisService()
    patterns = pattern_service.analyze_all_patterns(
        classroom_id=classroom_id,
        events=events,
        clustering_eps=0.3,
        clustering_min_samples=2
    )
    return patterns


async def generate_recommendations(classroom_id: UUID, events: List[Event], patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate recommendations from patterns."""
    async with AsyncSessionLocal() as session:
        recommendation_generator = RecommendationGenerator(db_session=session)
        recommendations = await recommendation_generator.generate_all_recommendations(
            classroom_id=classroom_id,
            events=events,
            pattern_results=patterns,
            clustering_eps=0.3,
            clustering_min_samples=2
        )
        return recommendations


def format_confidence(confidence: ConfidenceLevel) -> str:
    """Format confidence level."""
    if confidence == ConfidenceLevel.ALTA:
        return f"{Fore.GREEN}🟢 ALTA{Style.RESET_ALL}" if HAS_COLORS else "🟢 ALTA"
    elif confidence == ConfidenceLevel.MEDIA:
        return f"{Fore.YELLOW}🟡 MEDIA{Style.RESET_ALL}" if HAS_COLORS else "🟡 MEDIA"
    else:
        return f"{Fore.RED}🔴 BAJA{Style.RESET_ALL}" if HAS_COLORS else "🔴 BAJA"


async def main():
    """Main demo function."""
    print_header("🎓 AULA+ - DEMOSTRACIÓN COMPLETA", Fore.CYAN)
    print_info("Sistema de IA para análisis pedagógico en aulas TEA")
    print_info("Presentación: OdiseIA4Good")
    print_info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    wait_for_user("Iniciar la demostración...")
    
    try:
        # Step 1: Classroom Overview
        print_header("📊 PASO 1: VISIÓN GENERAL DEL AULA", Fore.BLUE)
        
        print_section("Buscando aula de demostración...")
        classroom_id = await find_demo_classroom()
        print_success(f"Aula encontrada: {classroom_id}")
        
        wait_for_user()
        
        print_section("Analizando datos del aula...")
        overview = await get_classroom_overview(classroom_id)
        
        print_info(f"Total de eventos registrados: {overview['total_events']}")
        print()
        
        print_info("Distribución por tipo de evento:")
        for event_type, count in overview['event_types'].items():
            percentage = (count / overview['total_events']) * 100
            print(f"   • {event_type}: {count} eventos ({percentage:.1f}%)")
        print()
        
        print_info("Distribución por resultado:")
        for result, count in overview['results'].items():
            percentage = (count / overview['total_events']) * 100
            print(f"   • {result}: {count} eventos ({percentage:.1f}%)")
        print()
        
        print_info("Distribución por momento del día:")
        for moment, count in overview['moments'].items():
            percentage = (count / overview['total_events']) * 100
            print(f"   • {moment}: {count} eventos ({percentage:.1f}%)")
        
        # Save overview
        overview_text = f"""VISIÓN GENERAL DEL AULA
========================

Total de eventos: {overview['total_events']}

Distribución por tipo:
{chr(10).join(f"  - {k}: {v} ({v/overview['total_events']*100:.1f}%)" for k, v in overview['event_types'].items())}

Distribución por resultado:
{chr(10).join(f"  - {k}: {v} ({v/overview['total_events']*100:.1f}%)" for k, v in overview['results'].items())}

Distribución por momento:
{chr(10).join(f"  - {k}: {v} ({v/overview['total_events']*100:.1f}%)" for k, v in overview['moments'].items())}
"""
        save_to_file(overview_text, "01_classroom_overview.txt")
        
        wait_for_user("Continuar con búsqueda semántica...")
        
        # Step 2: Semantic Search
        print_header("🔍 PASO 2: BÚSQUEDA SEMÁNTICA", Fore.BLUE)
        
        print_section("Ejemplo: Buscar eventos similares a 'sobrecarga sensorial'")
        query = "sobrecarga sensorial"
        print_info(f"Consulta: '{query}'")
        print_info("El sistema busca eventos semánticamente similares usando embeddings...")
        
        wait_for_user()
        
        search_results = await perform_semantic_search(classroom_id, query, top_k=3)
        
        if search_results:
            print_success(f"Encontrados {len(search_results)} eventos similares:\n")
            
            search_text = f"BÚSQUEDA SEMÁNTICA\n==================\n\nConsulta: '{query}'\n\n"
            
            for i, result in enumerate(search_results, 1):
                event = result["event"]
                score = result["score"]
                
                print(f"   {i}. Similitud: {score:.3f}")
                print(f"      Tipo: {event.event_type}")
                print(f"      Descripción: {event.description}")
                print(f"      Resultado: {event.result}")
                print(f"      Apoyos: {', '.join(event.supports)}")
                if event.observations:
                    print(f"      Observaciones: {event.observations}")
                print()
                
                search_text += f"Resultado {i} (Similitud: {score:.3f}):\n"
                search_text += f"  Tipo: {event.event_type}\n"
                search_text += f"  Descripción: {event.description}\n"
                search_text += f"  Resultado: {event.result}\n"
                search_text += f"  Apoyos: {', '.join(event.supports)}\n"
                if event.observations:
                    search_text += f"  Observaciones: {event.observations}\n"
                search_text += "\n"
            
            save_to_file(search_text, "02_semantic_search.txt")
        else:
            print_warning("No se encontraron eventos similares.")
        
        wait_for_user("Continuar con análisis de patrones...")
        
        # Step 3: Pattern Analysis
        print_header("📈 PASO 3: ANÁLISIS DE PATRONES", Fore.BLUE)
        
        print_section("Detectando patrones en los eventos...")
        print_info("El sistema analiza:")
        print_info("  • Clusters de eventos similares (agrupación semántica)", 2)
        print_info("  • Patrones temporales (días y momentos críticos)", 2)
        print_info("  • Efectividad de apoyos pedagógicos", 2)
        
        wait_for_user()
        
        patterns = await analyze_patterns(classroom_id, overview['events'])
        
        # Clustering
        clustering = patterns.get("clustering", {})
        if "error" not in clustering:
            n_clusters = clustering.get("n_clusters", 0)
            n_outliers = clustering.get("n_outliers", 0)
            print_success(f"Clusters detectados: {n_clusters}")
            print_info(f"Eventos sin cluster (outliers): {n_outliers}")
        else:
            print_warning(f"Error en clustering: {clustering.get('error')}")
        
        # Temporal patterns
        temporal = patterns.get("temporal_patterns", {})
        most_common_moment = temporal.get("most_common_moment")
        most_common_day = temporal.get("most_common_day")
        if most_common_moment:
            moment_count = temporal.get("moment_of_day", {}).get(most_common_moment, 0)
            percentage = (moment_count / overview['total_events'] * 100) if overview['total_events'] > 0 else 0
            print_success(f"Momento más común: {most_common_moment} ({percentage:.1f}% de eventos)")
        if most_common_day:
            day_count = temporal.get("day_of_week", {}).get(most_common_day, 0)
            percentage = (day_count / overview['total_events'] * 100) if overview['total_events'] > 0 else 0
            print_success(f"Día más común: {most_common_day} ({percentage:.1f}% de eventos)")
        
        # Support effectiveness
        support_effectiveness = patterns.get("support_effectiveness", {})
        most_effective = support_effectiveness.get("most_effective_supports", [])
        if most_effective:
            top_support = most_effective[0]
            if isinstance(top_support, dict):
                support_name = top_support.get("support", "Unknown")
                success_rate = top_support.get("success_rate", 0)
                print_success(f"Apoyo más efectivo: {support_name} ({success_rate:.1%} de éxito)")
        
        # Save patterns
        patterns_text = f"""ANÁLISIS DE PATRONES
===================

CLUSTERING:
  Clusters detectados: {clustering.get('n_clusters', 0) if 'error' not in clustering else 'Error'}
  Outliers: {clustering.get('n_outliers', 0) if 'error' not in clustering else 'N/A'}

PATRONES TEMPORALES:
  Momento más común: {most_common_moment or 'N/A'}
  Día más común: {most_common_day or 'N/A'}

EFECTIVIDAD DE APOYOS:
  Apoyo más efectivo: {most_effective[0].get('support', 'N/A') if most_effective and isinstance(most_effective[0], dict) else 'N/A'}
"""
        save_to_file(patterns_text, "03_pattern_analysis.txt")
        
        wait_for_user("Continuar con generación de recomendaciones...")
        
        # Step 4: Recommendations
        print_header("💡 PASO 4: RECOMENDACIONES PEDAGÓGICAS", Fore.BLUE)
        
        print_section("Generando recomendaciones basadas en patrones detectados...")
        print_info("El sistema crea recomendaciones accionables con:")
        print_info("  • Nivel de confianza basado en la fuerza del patrón", 2)
        print_info("  • Explicación del patrón detectado", 2)
        print_info("  • Contexto de aplicación", 2)
        
        wait_for_user()
        
        recommendations = await generate_recommendations(classroom_id, overview['events'], patterns)
        
        if recommendations:
            print_success(f"Generadas {len(recommendations)} recomendaciones:\n")
            
            recs_text = "RECOMENDACIONES PEDAGÓGICAS\n==========================\n\n"
            
            for i, rec in enumerate(recommendations, 1):
                title = rec.get("title", "Sin título")
                description = rec.get("description", "")
                detected_pattern = rec.get("detected_pattern", "")
                confidence = rec.get("confidence")
                rec_type = rec.get("recommendation_type")
                
                print(f"   {i}. {title}")
                print(f"      Confianza: {format_confidence(confidence) if confidence else 'N/A'}")
                print(f"      Tipo: {rec_type.value if hasattr(rec_type, 'value') else rec_type}")
                print(f"      Descripción: {description[:80]}..." if len(description) > 80 else f"      Descripción: {description}")
                print()
                
                recs_text += f"Recomendación {i}:\n"
                recs_text += f"  Título: {title}\n"
                recs_text += f"  Confianza: {confidence.value if hasattr(confidence, 'value') else confidence}\n"
                recs_text += f"  Tipo: {rec_type.value if hasattr(rec_type, 'value') else rec_type}\n"
                recs_text += f"  Descripción: {description}\n"
                recs_text += f"  Patrón detectado: {detected_pattern}\n"
                recs_text += f"  Contexto: {rec.get('applicable_context', 'N/A')}\n\n"
            
            save_to_file(recs_text, "04_recommendations.txt")
        else:
            print_warning("No se generaron recomendaciones.")
        
        wait_for_user()
        
        # Final summary
        print_header("✅ DEMOSTRACIÓN COMPLETA", Fore.GREEN)
        print_success("Flujo completo ejecutado exitosamente:")
        print_info("  ✓ Visión general del aula", 2)
        print_info("  ✓ Búsqueda semántica", 2)
        print_info("  ✓ Análisis de patrones", 2)
        print_info("  ✓ Generación de recomendaciones", 2)
        print()
        print_info(f"Todos los resultados han sido guardados en: {OUTPUT_DIR.absolute()}")
        print()
        print_success("¡Listo para la presentación! 🎉")
        
    except Exception as e:
        print_warning(f"Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

