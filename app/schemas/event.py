from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from .enums import (
    EventType,
    EventResult,
    MomentOfDay,
    DayOfWeek,
    SupportType
)


class EventContext(BaseModel):
    """Contexto estructurado de un evento"""
    moment_of_day: MomentOfDay = Field(..., description="Momento del día en que ocurrió el evento")
    day_of_week: Optional[DayOfWeek] = Field(None, description="Día de la semana (opcional)")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duración en minutos (opcional)")

class EventContextUpdate(BaseModel):
    """Contexto estructurado de un evento para actualización (todos los campos opcionales)"""
    moment_of_day: Optional[MomentOfDay] = Field(None, description="Momento del día en que ocurrió el evento")
    day_of_week: Optional[DayOfWeek] = Field(None, description="Día de la semana (opcional)")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duración en minutos (opcional)")


class EventBase(BaseModel):
    """Esquema base para eventos pedagógicos"""
    event_type: EventType = Field(..., description="Tipo de evento pedagógico")
    description: str = Field(..., min_length=10, max_length=500, description="Descripción breve y objetiva de la situación")
    context: EventContext = Field(..., description="Contexto temporal y situacional del evento")
    supports: List[SupportType] = Field(..., min_length=1, description="Lista de apoyos utilizados (al menos uno)")
    additional_supports: Optional[str] = Field(None, max_length=200, description="Apoyos adicionales en texto libre (opcional)")
    result: EventResult = Field(..., description="Resultado del evento")
    observations: Optional[str] = Field(None, max_length=1000, description="Observaciones adicionales (opcional)")

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Valida que la descripción no esté vacía después de quitar espacios"""
        if not v.strip():
            raise ValueError("La descripción no puede estar vacía")
        return v.strip()


class EventCreate(EventBase):
    """Esquema para crear un nuevo evento"""
    classroom_id: UUID = Field(..., description="ID del aula a la que pertenece el evento")


class EventUpdate(BaseModel):
    """Esquema para actualizar un evento (todos los campos opcionales)"""
    event_type: Optional[EventType] = Field(None, description="Tipo de evento pedagógico")
    description: Optional[str] = Field(None, min_length=10, max_length=500, description="Descripción breve y objetiva de la situación (mínimo 10 caracteres si se proporciona)")
    context: Optional[EventContextUpdate] = Field(None, description="Contexto temporal y situacional del evento")
    supports: Optional[List[SupportType]] = Field(None, min_length=1, description="Lista de apoyos utilizados (mínimo 1 si se proporciona)")
    additional_supports: Optional[str] = Field(None, max_length=200, description="Apoyos adicionales en texto libre")
    result: Optional[EventResult] = Field(None, description="Resultado del evento")
    observations: Optional[str] = Field(None, max_length=1000, description="Observaciones adicionales")
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Valida que la descripción no esté vacía si se proporciona"""
        if v is not None and not v.strip():
            raise ValueError("La descripción no puede estar vacía")
        return v.strip() if v else None

class EventResponse(EventBase):
    """Esquema de respuesta al consultar un evento"""
    id: UUID
    classroom_id: UUID
    timestamp: datetime
    
    class Config:
        from_attributes = True


class SimilarEventResponse(BaseModel):
    """Esquema de respuesta para eventos similares"""
    event: EventResponse = Field(..., description="Evento similar encontrado")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Score de similitud (0.0 a 1.0)")
    
    class Config:
        from_attributes = True
