from enum import Enum


class EventType(str, Enum):
    """Tipos de eventos pedagógicos del aula"""
    TRANSICION = "TRANSICION"
    CAMBIO_DE_RUTINA = "CAMBIO_DE_RUTINA"
    APRENDIZAJE = "APRENDIZAJE"
    REGULACION = "REGULACION"


class EventResult(str, Enum):
    """Resultado de un evento"""
    EXITOSO = "EXITOSO"
    PARCIAL = "PARCIAL"
    DIFICULTAD = "DIFICULTAD"


class MomentOfDay(str, Enum):
    """Momento del día"""
    MORNING = "mañana"
    MIDDAY = "mediodia"
    AFTERNOON = "tarde"


class DayOfWeek(str, Enum):
    """Día de la semana"""
    MONDAY = "lunes"
    TUESDAY = "martes"
    WEDNESDAY = "miércoles"
    THURSDAY = "jueves"
    FRIDAY = "viernes"
    SATURDAY = "sábado"
    SUNDAY = "domingo"


class SupportType(str, Enum):
    """Tipos de apoyos predefinidos"""
    VISUAL_ANTICIPATION = "Anticipación visual"
    ENVIRONMENT_ADAPTATION = "Adaptación del entorno"
    VERBAL_MEDIATION = "Mediación verbal"
    SENSORY_BREAK = "Pausa sensorial"
    INDIVIDUAL_ADULT_SUPPORT = "Apoyo individual del adulto"


class RecommendationType(str, Enum):
    """Tipos de recomendaciones"""
    ANTICIPACION = "ANTICIPACION"
    ESTRATEGIA = "ESTRATEGIA"
    ADAPTACION = "ADAPTACION"


class ConfidenceLevel(str, Enum):
    """Nivel de confianza de una recomendación"""
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"

