import csv
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter

# Configuration
NUM_EVENTS = 50
CLASSROOM_ID = "ef2d0843-3594-4cf7-89d6-e838a797f57c"  # Example classroom ID (change if needed)
STUDENTS = ["EST001", "EST002", "EST003", "EST004", "EST005"]

# Event types and their realistic descriptions
EVENT_TYPES = {
    "TRANSICION": [
        "Transición de juego libre a asamblea matutina",
        "Transición del patio al aula después del recreo",
        "Transición de actividad grupal a trabajo individual",
        "Transición de asamblea a actividad en mesa",
        "Transición de actividad estructurada a tiempo libre",
        "Transición de aula a comedor",
        "Transición de actividad individual a actividad grupal",
        "Transición de espacio interior a patio",
    ],
    "CAMBIO_DE_RUTINA": [
        "Cambio inesperado de horario de recreo",
        "Actividad nueva no prevista en la rutina",
        "Cambio de profesor de apoyo",
        "Modificación de la estructura de la jornada",
        "Cambio de espacio de trabajo",
        "Actividad cancelada sin previo aviso",
        "Cambio en el orden de actividades programadas",
        "Visita inesperada al aula",
    ],
    "APRENDIZAJE": [
        "Actividad de trabajo en mesa individual",
        "Actividad de comunicación con panel de pictogramas",
        "Actividad de reconocimiento de emociones",
        "Actividad de seguimiento de instrucciones",
        "Actividad de juego simbólico guiado",
        "Actividad de trabajo cooperativo en pequeño grupo",
        "Actividad de lectura compartida",
        "Actividad de expresión artística",
    ],
    "REGULACION": [
        "Momento de sobrecarga sensorial en el aula",
        "Necesidad de espacio de calma",
        "Sobrecarga auditiva durante actividad ruidosa",
        "Dificultad para regular emociones tras conflicto",
        "Necesidad de pausa sensorial tras actividad intensa",
        "Momento de ansiedad por cambio no anticipado",
        "Sobrecarga visual por demasiados estímulos",
        "Necesidad de regulación tras transición difícil",
    ],
}

# Predefined supports from the system
PREDEFINED_SUPPORTS = [
    "Anticipación visual",
    "Adaptación del entorno",
    "Mediación verbal",
    "Pausa sensorial",
    "Apoyo individual del adulto",
]

# Additional supports (free text) based on TEA literature
ADDITIONAL_SUPPORTS = [
    "Rincón de calma con cojines y luces tenues",
    "Pictogramas de secuencia de actividades",
    "Historia social sobre la transición",
    "Panel de comunicación con pictogramas",
    "Sistema de trabajo con cajas visuales",
    "Auriculares con cancelación de ruido",
    "Mesa con separadores visuales",
    "Cronómetro visual para anticipar tiempo",
    "Tarjetas de 'estoy bien' / 'necesito ayuda'",
    "Espacio tranquilo con elementos sensoriales",
    "Agenda visual del día",
    "Soporte de comunicación aumentativa",
]

# Realistic observations
OBSERVATIONS_SUCCESS = [
    "Todos se incorporaron sin dificultades",
    "La anticipación visual facilitó la transición",
    "El espacio de calma fue muy efectivo",
    "La combinación de apoyos funcionó muy bien",
    "Se observó una mejora en la participación",
    "Los estudiantes mostraron mayor autonomía",
    "La actividad se desarrolló con fluidez",
    "Se redujo significativamente la ansiedad",
    "Los apoyos visuales fueron clave para el éxito",
    "Se logró una regulación emocional adecuada",
]

OBSERVATIONS_PARTIAL = [
    "Algunos estudiantes necesitaron apoyo adicional",
    "Funcionó bien para la mayoría, pero hubo excepciones",
    "Requiere ajustes en la implementación",
    "Algunos estudiantes mostraron resistencia inicial",
    "Se necesitó más tiempo del previsto",
    "Funcionó mejor con apoyo individual complementario",
    "Algunos estudiantes necesitaron más estructura",
    "La efectividad varió según el estudiante",
]

OBSERVATIONS_DIFFICULTY = [
    "Algunos estudiantes mostraron resistencia al cambio",
    "Se observó aumento de conductas de evitación",
    "Fue necesario interrumpir la actividad",
    "Se requirió apoyo intensivo adicional",
    "Los estudiantes mostraron signos de sobrecarga",
    "La actividad generó ansiedad significativa",
    "Se necesitó tiempo extra para la regulación",
    "Fue necesario modificar el enfoque durante la actividad",
]

# Intentional patterns for AI to detect
# Some supports are more effective than others
SUPPORT_EFFECTIVENESS = {
    "Anticipación visual": 0.85,  # Muy efectivo
    "Pausa sensorial": 0.90,  # Muy efectivo
    "Adaptación del entorno": 0.75,  # Moderadamente efectivo
    "Mediación verbal": 0.70,  # Moderadamente efectivo
    "Apoyo individual del adulto": 0.80,  # Efectivo
}

# Most difficult times of day
CRITICAL_MOMENTS = {
    "mañana": 0.30,  # 30% de eventos en mañana (algunos más difíciles)
    "mediodia": 0.25,  # 25% en mediodía
    "tarde": 0.45,  # 45% en tarde (más eventos, algunos más difíciles)
}


DAYS_OF_WEEK = ["lunes", "martes", "miercoles", "jueves", "viernes"]

# Most problematic event types
PROBLEMATIC_EVENTS = {
    "CAMBIO_DE_RUTINA": 0.40,  # 40% de dificultad
    "REGULACION": 0.30,  # 30% de dificultad
    "TRANSICION": 0.15,  # 15% de dificultad
    "APRENDIZAJE": 0.10,  # 10% de dificultad
}


def generate_result(event_type: str, supports: List[str]) -> str:
    """
    Generate a result based on event type and supports used.
    Includes intentional patterns for AI to detect.
    """
    # Calculate base effectiveness based on supports
    base_effectiveness = sum(SUPPORT_EFFECTIVENESS.get(support, 0.5) for support in supports) / len(supports)
    
    # Adjust based on event type
    difficulty_probability = PROBLEMATIC_EVENTS.get(event_type, 0.15)
    
    # Generate result with target distribution: 70% successful, 20% partial, 10% difficulty
    rand = random.random()
    
    if rand < 0.70:  # 70% successful
        # Adjust based on effectiveness
        if base_effectiveness > 0.80:
            return "EXITOSO"
        elif base_effectiveness > 0.65:
            return random.choice(["EXITOSO", "EXITOSO", "PARCIAL"])  # 66% successful, 33% partial
        else:
            return random.choice(["EXITOSO", "PARCIAL", "PARCIAL"])  # 33% successful, 66% partial
    elif rand < 0.90:  # 20% partial
        return "PARCIAL"
    else:  # 10% difficulty
        return "DIFICULTAD"


def generate_event(classroom_id: str, student: str, event_num: int) -> Dict:
    """Generate a realistic synthetic event"""
    
    # Select event type
    event_type = random.choice(list(EVENT_TYPES.keys()))
    description = random.choice(EVENT_TYPES[event_type])
    
    # Add anonymized student reference
    if random.random() < 0.3:  # 30% of events mention student
        description = f"{description} (estudiante {student})"
    
    # Select moment of day according to distribution
    moment_of_day = random.choices(
        list(CRITICAL_MOMENTS.keys()),
        weights=list(CRITICAL_MOMENTS.values())
    )[0]
    
    # Select day of week
    day_of_week = random.choice(DAYS_OF_WEEK)
    
    # Duration (optional, 60% of events have duration)
    duration_minutes = None
    if random.random() < 0.6:
        if event_type == "TRANSICION":
            duration_minutes = random.randint(2, 10)
        elif event_type == "REGULACION":
            duration_minutes = random.randint(5, 20)
        elif event_type == "APRENDIZAJE":
            duration_minutes = random.randint(15, 45)
        else:  # CAMBIO_DE_RUTINA
            duration_minutes = random.randint(5, 15)
    
    # Select supports (1-3 supports)
    num_supports = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
    supports = random.sample(PREDEFINED_SUPPORTS, num_supports)
    
    # Additional support (40% of events have additional support)
    additional_supports = None
    if random.random() < 0.4:
        additional_supports = random.choice(ADDITIONAL_SUPPORTS)
    
    # Generate result based on patterns
    result = generate_result(event_type, supports)
    
    # Observations according to result
    if result == "EXITOSO":
        observations = random.choice(OBSERVATIONS_SUCCESS)
    elif result == "PARCIAL":
        observations = random.choice(OBSERVATIONS_PARTIAL)
    else:  # DIFICULTAD
        observations = random.choice(OBSERVATIONS_DIFFICULTY)
    
    return {
        "classroom_id": classroom_id,
        "event_type": event_type,
        "description": description,
        "moment_of_day": moment_of_day,
        "day_of_week": day_of_week,
        "duration_minutes": duration_minutes,
        "supports": ";".join(supports),
        "additional_supports": additional_supports,
        "result": result,
        "observations": observations,
    }


def generate_synthetic_events(num_events: int, classroom_id: str) -> List[Dict]:
    """Generate a list of synthetic events"""
    events = []
    
    for i in range(num_events):
        # Rotate between students for variability
        student = STUDENTS[i % len(STUDENTS)]
        event = generate_event(classroom_id, student, i + 1)
        events.append(event)
    
    return events


def save_csv(events: List[Dict], filename: str):
    """Save events to a CSV file"""
    if not events:
        return
    
    fieldnames = [
        "classroom_id",
        "event_type",
        "description",
        "moment_of_day",
        "day_of_week",
        "duration_minutes",
        "supports",
        "additional_supports",
        "result",
        "observations",
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)
    
    print(f"✅ CSV file saved: {filename}")


def show_summary(events: List[Dict]):
    """Show a summary of generated events"""
    print("\n" + "="*60)
    print("SYNTHETIC EVENTS GENERATION SUMMARY")
    print("="*60)
    
    print(f"\n📊 Total events: {len(events)}")
    
    # Distribution by type
    types = Counter(e["event_type"] for e in events)
    print("\n📋 Distribution by event type:")
    for event_type, count in types.most_common():
        percentage = (count / len(events)) * 100
        print(f"   - {event_type}: {count} ({percentage:.1f}%)")
    
    # Distribution by result
    results = Counter(e["result"] for e in events)
    print("\n✅ Distribution by result:")
    for result, count in results.most_common():
        percentage = (count / len(events)) * 100
        print(f"   - {result}: {count} ({percentage:.1f}%)")
    
    # Distribution by moment of day
    moments = Counter(e["moment_of_day"] for e in events)
    print("\n⏰ Distribution by moment of day:")
    for moment, count in moments.most_common():
        percentage = (count / len(events)) * 100
        print(f"   - {moment}: {count} ({percentage:.1f}%)")
    
    # Most used supports
    all_supports = []
    for event in events:
        all_supports.extend(event["supports"].split(";"))
    supports_count = Counter(all_supports)
    print("\n🛠️  Most used supports:")
    for support, count in supports_count.most_common(5):
        percentage = (count / len(events)) * 100
        print(f"   - {support}: {count} times ({percentage:.1f}% of events)")
    
    # Support effectiveness (intentional pattern)
    print("\n📈 Support effectiveness (intentional pattern):")
    for support in PREDEFINED_SUPPORTS:
        events_with_support = [e for e in events if support in e["supports"]]
        if events_with_support:
            successful = sum(1 for e in events_with_support if e["result"] == "EXITOSO")
            total = len(events_with_support)
            success_rate = (successful / total) * 100 if total > 0 else 0
            print(f"   - {support}: {success_rate:.1f}% success ({successful}/{total} events)")
    
    # Events with additional support
    with_additional = sum(1 for e in events if e["additional_supports"])
    print(f"\n➕ Events with additional support: {with_additional} ({with_additional/len(events)*100:.1f}%)")
    
    # Events with duration
    with_duration = sum(1 for e in events if e["duration_minutes"])
    print(f"⏱️  Events with recorded duration: {with_duration} ({with_duration/len(events)*100:.1f}%)")
    
    print("\n" + "="*60)
    print("✅ Synthetic data generated successfully")
    print("="*60 + "\n")


def main():
    """Main function"""
    print("🎲 Synthetic Data Generator for TEA Classroom")
    print("="*60)
    print(f"\nGenerating {NUM_EVENTS} synthetic events...")
    print("Based on pedagogical literature about TEA classrooms\n")
    
    # Generate events
    events = generate_synthetic_events(NUM_EVENTS, CLASSROOM_ID)
    
    # Save to CSV
    filename = "synthetic_events_tea.csv"
    save_csv(events, filename)
    
    # Show summary
    show_summary(events)
    
    print(f"💡 Next steps:")
    print(f"   1. Review the file: {filename}")
    print(f"   2. Import the data: python scripts/import_events_from_csv.py {filename}")
    print(f"   3. Validate patterns: GET /events/patterns?classroom_id={CLASSROOM_ID}")
    print(f"   4. Generate recommendations: POST /recommendations/generate?classroom_id={CLASSROOM_ID}\n")


if __name__ == "__main__":
    
    main()

