#!/usr/bin/env python3
"""
Generador de Datos Sintéticos para Aula TEA

Genera eventos sintéticos realistas basados en literatura pedagógica sobre aulas TEA.
Incluye patrones detectables para validar el sistema de análisis de patrones.

Basado en:
- Literatura sobre apoyos pedagógicos TEA
- Tipos de eventos comunes en aulas TEA
- Distribución realista de resultados
- Patrones temporales y de efectividad
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter

# Configuración
NUM_EVENTOS = 50
CLASSROOM_ID = "ef2d0843-3594-4cf7-89d6-e838a797f57c"  # ID de aula de ejemplo (cambiar si es necesario)
ESTUDIANTES = ["EST001", "EST002", "EST003", "EST004", "EST005"]

# Tipos de eventos y sus descripciones realistas
TIPOS_EVENTOS = {
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

# Apoyos predefinidos del sistema
APOYOS_PREDEFINIDOS = [
    "Anticipación visual",
    "Adaptación del entorno",
    "Mediación verbal",
    "Pausa sensorial",
    "Apoyo individual del adulto",
]

# Apoyos adicionales (texto libre) basados en literatura TEA
APOYOS_ADICIONALES = [
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

# Observaciones realistas
OBSERVACIONES_EXITOSO = [
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

OBSERVACIONES_PARCIAL = [
    "Algunos estudiantes necesitaron apoyo adicional",
    "Funcionó bien para la mayoría, pero hubo excepciones",
    "Requiere ajustes en la implementación",
    "Algunos estudiantes mostraron resistencia inicial",
    "Se necesitó más tiempo del previsto",
    "Funcionó mejor con apoyo individual complementario",
    "Algunos estudiantes necesitaron más estructura",
    "La efectividad varió según el estudiante",
]

OBSERVACIONES_DIFICULTAD = [
    "Algunos estudiantes mostraron resistencia al cambio",
    "Se observó aumento de conductas de evitación",
    "Fue necesario interrumpir la actividad",
    "Se requirió apoyo intensivo adicional",
    "Los estudiantes mostraron signos de sobrecarga",
    "La actividad generó ansiedad significativa",
    "Se necesitó tiempo extra para la regulación",
    "Fue necesario modificar el enfoque durante la actividad",
]

# Patrones intencionales para que la IA los detecte
# Algunos apoyos son más efectivos que otros
EFECTIVIDAD_APOYOS = {
    "Anticipación visual": 0.85,  # Muy efectivo
    "Pausa sensorial": 0.90,  # Muy efectivo
    "Adaptación del entorno": 0.75,  # Moderadamente efectivo
    "Mediación verbal": 0.70,  # Moderadamente efectivo
    "Apoyo individual del adulto": 0.80,  # Efectivo
}

# Momentos del día más difíciles
MOMENTOS_CRITICOS = {
    "mañana": 0.30,  # 30% de eventos en mañana (algunos más difíciles)
    "mediodia": 0.25,  # 25% en mediodía
    "tarde": 0.45,  # 45% en tarde (más eventos, algunos más difíciles)
}

# Días de la semana
DIAS_SEMANA = ["lunes", "martes", "miercoles", "jueves", "viernes"]

# Tipos de eventos más problemáticos
EVENTOS_PROBLEMATICOS = {
    "CAMBIO_DE_RUTINA": 0.40,  # 40% de dificultad
    "REGULACION": 0.30,  # 30% de dificultad
    "TRANSICION": 0.15,  # 15% de dificultad
    "APRENDIZAJE": 0.10,  # 10% de dificultad
}


def generar_resultado(event_type: str, apoyos: List[str]) -> str:
    """
    Genera un resultado basado en el tipo de evento y los apoyos utilizados.
    Incluye patrones intencionales para que la IA los detecte.
    """
    # Calcular efectividad base según apoyos
    efectividad_base = sum(EFECTIVIDAD_APOYOS.get(apoyo, 0.5) for apoyo in apoyos) / len(apoyos)
    
    # Ajustar según tipo de evento
    probabilidad_dificultad = EVENTOS_PROBLEMATICOS.get(event_type, 0.15)
    
    # Generar resultado con distribución objetivo: 70% exitoso, 20% parcial, 10% dificultad
    rand = random.random()
    
    if rand < 0.70:  # 70% exitoso
        # Ajustar según efectividad
        if efectividad_base > 0.80:
            return "EXITOSO"
        elif efectividad_base > 0.65:
            return random.choice(["EXITOSO", "EXITOSO", "PARCIAL"])  # 66% exitoso, 33% parcial
        else:
            return random.choice(["EXITOSO", "PARCIAL", "PARCIAL"])  # 33% exitoso, 66% parcial
    elif rand < 0.90:  # 20% parcial
        return "PARCIAL"
    else:  # 10% dificultad
        return "DIFICULTAD"


def generar_evento(classroom_id: str, estudiante: str, evento_num: int) -> Dict:
    """Genera un evento sintético realista"""
    
    # Seleccionar tipo de evento
    event_type = random.choice(list(TIPOS_EVENTOS.keys()))
    description = random.choice(TIPOS_EVENTOS[event_type])
    
    # Añadir referencia al estudiante de forma anonimizada
    if random.random() < 0.3:  # 30% de eventos mencionan estudiante
        description = f"{description} (estudiante {estudiante})"
    
    # Seleccionar momento del día según distribución
    moment_of_day = random.choices(
        list(MOMENTOS_CRITICOS.keys()),
        weights=list(MOMENTOS_CRITICOS.values())
    )[0]
    
    # Seleccionar día de la semana
    day_of_week = random.choice(DIAS_SEMANA)
    
    # Duración (opcional, 60% de eventos tienen duración)
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
    
    # Seleccionar apoyos (1-3 apoyos)
    num_apoyos = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
    apoyos = random.sample(APOYOS_PREDEFINIDOS, num_apoyos)
    
    # Apoyo adicional (40% de eventos tienen apoyo adicional)
    additional_supports = None
    if random.random() < 0.4:
        additional_supports = random.choice(APOYOS_ADICIONALES)
    
    # Generar resultado basado en patrones
    result = generar_resultado(event_type, apoyos)
    
    # Observaciones según resultado
    if result == "EXITOSO":
        observations = random.choice(OBSERVACIONES_EXITOSO)
    elif result == "PARCIAL":
        observations = random.choice(OBSERVACIONES_PARCIAL)
    else:  # DIFICULTAD
        observations = random.choice(OBSERVACIONES_DIFICULTAD)
    
    return {
        "classroom_id": classroom_id,
        "event_type": event_type,
        "description": description,
        "moment_of_day": moment_of_day,
        "day_of_week": day_of_week,
        "duration_minutes": duration_minutes,
        "supports": ";".join(apoyos),
        "additional_supports": additional_supports,
        "result": result,
        "observations": observations,
    }


def generar_eventos_sinteticos(num_eventos: int, classroom_id: str) -> List[Dict]:
    """Genera una lista de eventos sintéticos"""
    eventos = []
    
    for i in range(num_eventos):
        # Rotar entre estudiantes para variabilidad
        estudiante = ESTUDIANTES[i % len(ESTUDIANTES)]
        evento = generar_evento(classroom_id, estudiante, i + 1)
        eventos.append(evento)
    
    return eventos


def guardar_csv(eventos: List[Dict], filename: str):
    """Guarda los eventos en un archivo CSV"""
    if not eventos:
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
        writer.writerows(eventos)
    
    print(f"✅ Archivo CSV guardado: {filename}")


def mostrar_resumen(eventos: List[Dict]):
    """Muestra un resumen de los eventos generados"""
    print("\n" + "="*60)
    print("RESUMEN DE EVENTOS SINTÉTICOS GENERADOS")
    print("="*60)
    
    print(f"\n📊 Total de eventos: {len(eventos)}")
    
    # Distribución por tipo
    tipos = Counter(e["event_type"] for e in eventos)
    print("\n📋 Distribución por tipo de evento:")
    for tipo, count in tipos.most_common():
        porcentaje = (count / len(eventos)) * 100
        print(f"   - {tipo}: {count} ({porcentaje:.1f}%)")
    
    # Distribución por resultado
    resultados = Counter(e["result"] for e in eventos)
    print("\n✅ Distribución por resultado:")
    for resultado, count in resultados.most_common():
        porcentaje = (count / len(eventos)) * 100
        print(f"   - {resultado}: {count} ({porcentaje:.1f}%)")
    
    # Distribución por momento del día
    momentos = Counter(e["moment_of_day"] for e in eventos)
    print("\n⏰ Distribución por momento del día:")
    for momento, count in momentos.most_common():
        porcentaje = (count / len(eventos)) * 100
        print(f"   - {momento}: {count} ({porcentaje:.1f}%)")
    
    # Apoyos más utilizados
    todos_apoyos = []
    for evento in eventos:
        todos_apoyos.extend(evento["supports"].split(";"))
    apoyos_count = Counter(todos_apoyos)
    print("\n🛠️  Apoyos más utilizados:")
    for apoyo, count in apoyos_count.most_common(5):
        porcentaje = (count / len(eventos)) * 100
        print(f"   - {apoyo}: {count} veces ({porcentaje:.1f}% de eventos)")
    
    # Efectividad de apoyos (patrón intencional)
    print("\n📈 Efectividad de apoyos (patrón intencional):")
    for apoyo in APOYOS_PREDEFINIDOS:
        eventos_con_apoyo = [e for e in eventos if apoyo in e["supports"]]
        if eventos_con_apoyo:
            exitosos = sum(1 for e in eventos_con_apoyo if e["result"] == "EXITOSO")
            total = len(eventos_con_apoyo)
            tasa_exito = (exitosos / total) * 100 if total > 0 else 0
            print(f"   - {apoyo}: {tasa_exito:.1f}% éxito ({exitosos}/{total} eventos)")
    
    # Eventos con apoyo adicional
    con_apoyo_adicional = sum(1 for e in eventos if e["additional_supports"])
    print(f"\n➕ Eventos con apoyo adicional: {con_apoyo_adicional} ({con_apoyo_adicional/len(eventos)*100:.1f}%)")
    
    # Eventos con duración
    con_duracion = sum(1 for e in eventos if e["duration_minutes"])
    print(f"⏱️  Eventos con duración registrada: {con_duracion} ({con_duracion/len(eventos)*100:.1f}%)")
    
    print("\n" + "="*60)
    print("✅ Datos sintéticos generados correctamente")
    print("="*60 + "\n")


def main():
    """Función principal"""
    print("🎲 Generador de Datos Sintéticos para Aula TEA")
    print("="*60)
    print(f"\nGenerando {NUM_EVENTOS} eventos sintéticos...")
    print("Basado en literatura pedagógica sobre aulas TEA\n")
    
    # Generar eventos
    eventos = generar_eventos_sinteticos(NUM_EVENTOS, CLASSROOM_ID)
    
    # Guardar en CSV
    filename = "synthetic_events_tea.csv"
    guardar_csv(eventos, filename)
    
    # Mostrar resumen
    mostrar_resumen(eventos)
    
    print(f"💡 Próximos pasos:")
    print(f"   1. Revisa el archivo: {filename}")
    print(f"   2. Importa los datos: python scripts/import_events_from_csv.py {filename}")
    print(f"   3. Valida los patrones: GET /events/patterns?classroom_id={CLASSROOM_ID}")
    print(f"   4. Genera recomendaciones: POST /recommendations/generate?classroom_id={CLASSROOM_ID}\n")


if __name__ == "__main__":
    # Fijar semilla para reproducibilidad (opcional, comentar para variabilidad)
    # random.seed(42)
    main()

