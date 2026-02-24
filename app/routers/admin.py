from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
import random
from datetime import datetime, timedelta

from app.models.database import get_db
from app.models.models import Classroom, Event, Recommendation
from app.schemas.enums import EventType, EventResult, RecommendationType, ConfidenceLevel
from app.services.vector_store import VectorStore
from app.services.embeddingService import EmbeddingService

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

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

async def run_seed_logic(db: AsyncSession):
    # 1. Crear Aula Maestra para desarrollo
    FIXED_CLASSROOM_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    
    # Check if already exists to avoid duplicates
    result = await db.execute(select(Classroom).where(Classroom.id == FIXED_CLASSROOM_ID))
    aula_principal = result.scalar_one_or_none()
    
    if not aula_principal:
        aula_principal = Classroom(
            id=FIXED_CLASSROOM_ID,
            name="Aula TEA - Los Olivos (Demo)",
            type="TEA",
            extra_metadata={"teacher": "Equipo AULA+", "description": "Aula con datos masivos para pruebas"}
        )
        db.add(aula_principal)
        await db.flush()
    
    all_events = []
    # 2. Generar 30 eventos x 4 tipos = 120 eventos
    for e_type in EventType:
        for i in range(30):
            template = random.choice(TEMPLATES[e_type])
            description = template.format(**{k: random.choice(v) for k, v in VALUES.items()})
            
            day = random.choice(DAYS)
            res = random.choice(list(EventResult))
            if e_type == EventType.TRANSICION and day == "lunes":
                res = EventResult.DIFICULTAD
            
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
    
    # 4. Generar Embeddings en segundo plano para no bloquear el request? 
    # Mejor devolver respuesta y seguir buildeando
    return all_events, FIXED_CLASSROOM_ID

async def background_embeddings(events_data, classroom_id):
    vector_store = VectorStore()
    embedding_service = EmbeddingService.get_instance()
    
    for event in events_data:
        try:
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
                classroom_id=classroom_id,
                event_id=event.id,
                embedding=embedding,
                metadata={"event_type": event.event_type, "result": event.result},
                model_type="quality"
            )
        except Exception as e:
            print(f"Error seeding embedding for event {event.id}: {e}")

@router.post("/seed")
async def seed_database(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    Puebla la base de datos con datos de prueba masivos (120 eventos y 2 recomendaciones).
    El proceso de base de datos es síncrono para el request, pero los embeddings 
    se generan en background.
    """
    try:
        events, classroom_id = await run_seed_logic(db)
        # Lanzar embeddings en background
        background_tasks.add_task(background_embeddings, events, classroom_id)
        
        return {
            "status": "success",
            "message": f"Se han creado {len(events)} eventos y 2 recomendaciones.",
            "classroom_id": classroom_id,
            "note": "Los embeddings se están generando en segundo plano en el servidor."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
