
import asyncio
import sys
import os
import random
from uuid import uuid4
from datetime import datetime, timedelta

# Añadir el raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import AsyncSessionLocal
from app.models.models import Classroom, Event, Recommendation
from app.schemas.enums import EventType, EventResult, RecommendationType, ConfidenceLevel
from app.services.vector_store import VectorStore
from app.services.embeddingService import EmbeddingService

# Diccionarios de datos para generar variedad pedagógica
TEMPLATES = {
    EventType.TRANSICION: [
        "Cambio de clase de {act1} a {act2}.",
        "Entrada al centro desde el {transp}.",
        "Desplazamiento por el pasillo hacia {lugar}.",
        "Fin de {act1} y comienzo de tiempo de {act2}."
    ],
    EventType.APRENDIZAJE: [
        "Tarea de {materia} en mesa individual.",
        "Actividad grupal de {materia} con compañeros.",
        "Uso de tablet para actividad de {materia}.",
        "Sesión de logopedia enfocada en {materia}."
    ],
    EventType.REGULACION: [
        "Molestia por factor sensorial: {ruido}.",
        "Frustración al no conseguir {objeto}.",
        "Momento de sobrecarga tras actividad de {act1}.",
        "Búsqueda de autorregulación en {lugar}."
    ],
    EventType.CAMBIO_DE_RUTINA: [
        "Ausencia del profesor habitual de {materia}.",
        "Cambio inesperado de horario: hoy no hay {act1}.",
        "Simulacro de emergencia en el centro.",
        "Celebración de {festividad} no anticipada."
    ]
}

VALUES = {
    "act1": ["Pintura", "Matemáticas", "Música", "Juego Libre", "Comedor"],
    "act2": ["Patio", "Asamblea", "Logopedia", "Relajación", "Gimnasio"],
    "transp": ["Autobús", "Coche familiar", "Andando"],
    "lugar": ["el huerto", "la biblioteca", "el rincón de calma", "el aula de informática"],
    "materia": ["lectoescritura", "conteo numérico", "identificación de emociones", "autonomía"],
    "ruido": ["obras externas", "gritos en el pasillo", "luces fluorescentes", "olor fuerte"],
    "objeto": ["el juguete favorito", "terminar el dibujo", "salir el primero"],
    "festividad": ["un cumpleaños", "Carnaval", "el Día del Libro"]
}

DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes"]
MOMENTS = ["mañana", "mediodia", "tarde"]
SUPPORTS = ["Anticipación visual", "Adaptación del entorno", "Mediación verbal", "Pausa sensorial", "Apoyo individual del adulto"]

async def seed_db():
    print("🌱 Iniciando población MASIVA de base de datos...")
    
    async with AsyncSessionLocal() as db:
        # 1. Crear Aula Maestra para desarrollo
        aula_principal = Classroom(
            id=uuid4(),
            name="Aula TEA - Los Olivos (Demo)",
            type="TEA",
            extra_metadata={"teacher": "Equipo AULA+", "description": "Aula con datos masivos para pruebas"}
        )
        db.add(aula_principal)
        await db.flush()
        
        all_events = []
        
        # 2. Generar 30 eventos x 4 tipos = 120 eventos
        for e_type in EventType:
            print(f"   Generating 30 events for {e_type.value}...")
            for i in range(30):
                # Construir descripción aleatoria basada en templates
                template = random.choice(TEMPLATES[e_type])
                description = template.format(**{k: random.choice(v) for k, v in VALUES.items()})
                
                # Simular patrones: por ejemplo, las transiciones los lunes suelen ser difíciles
                day = random.choice(DAYS)
                res = random.choice(list(EventResult))
                if e_type == EventType.TRANSICION and day == "lunes":
                    res = EventResult.DIFICULTAD # Forzamos un patrón para la IA
                
                event = Event(
                    id=uuid4(),
                    classroom_id=aula_principal.id,
                    event_type=e_type.value,
                    description=description,
                    moment_of_day=random.choice(MOMENTS),
                    day_of_week=day,
                    supports=random.sample(SUPPORTS, k=random.randint(1, 3)),
                    result=res.value,
                    observations=f"Evento generado automáticamente para el set de pruebas #{i}.",
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
                )
                all_events.append(event)
        
        db.add_all(all_events)
        
        # 3. Añadir Recomendaciones estratégicas
        recs = [
            Recommendation(
                id=uuid4(), classroom_id=aula_principal.id,
                recommendation_type=RecommendationType.ESTRATEGIA.value,
                title="Gestión de Lunes Críticos",
                description="Se observa una recurrencia sistemática de registros con dificultad en las transiciones de los lunes. Se sugiere reforzar la agenda visual el domingo tarde o lunes primera hora.",
                applicable_context="Lunes mañana - Transición de casa al aula.",
                detected_pattern="Patrón de dificultad alta detectado en eventos de tipo Transición los lunes.",
                confidence=ConfidenceLevel.ALTA.value
            ),
            Recommendation(
                id=uuid4(), classroom_id=aula_principal.id,
                recommendation_type=RecommendationType.ADAPTACION.value,
                title="Optimización de Apoyo Individual",
                description="Las tareas de lectoescritura muestran un 100% de éxito cuando interviene el apoyo individual del adulto.",
                applicable_context="Actividades de Aprendizaje en mesa.",
                detected_pattern="Correlación positiva entre 'Apoyo individual' y 'Éxito' en el área de Aprendizaje.",
                confidence=ConfidenceLevel.MEDIA.value
            )
        ]
        db.add_all(recs)
        
        await db.commit()
        print(f"✅ DB Relacional poblada con {len(all_events)} eventos.")

        # 4. Generar Embeddings (Esto tardará un poco por el volumen)
        print(f"🧠 Generando {len(all_events)} embeddings en ChromaDB. Por favor, espera...")
        vector_store = VectorStore()
        embedding_service = EmbeddingService.get_instance()
        
        count = 0
        for event in all_events:
            embedding = embedding_service.generate_event_embedding(
                event_type=event.event_type,
                description=event.description,
                moment_of_day=event.moment_of_day,
                day_of_week=event.day_of_week,
                supports=event.supports,
                result=event.result,
                observations=event.observations,
                model_type="quality"
            )
            
            vector_store.add_event_embedding(
                classroom_id=aula_principal.id,
                event_id=event.id,
                embedding=embedding,
                metadata={"event_type": event.event_type, "result": event.result},
                model_type="quality"
            )
            count += 1
            if count % 20 == 0:
                print(f"   ... procesados {count}/{len(all_events)} embeddings")
            
        print("✅ Simulación semántica completada con éxito.")
        print("-" * 50)
        print(f"ID PARA USAR EN FRONTEND: {aula_principal.id}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(seed_db())
