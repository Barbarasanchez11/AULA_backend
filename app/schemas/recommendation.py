from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from .enums import RecommendationType, ConfidenceLevel


class RecommendationBase(BaseModel):
    """Esquema base para recomendaciones pedagógicas"""
    recommendation_type: RecommendationType = Field(..., description="Tipo de recomendación")
    title: str = Field(..., min_length=10, max_length=200, description="Título descriptivo y accionable")
    description: str = Field(..., min_length=20, max_length=1000, description="Explicación clara de la recomendación")
    applicable_context: str = Field(..., min_length=10, max_length=500, description="Cuándo y cómo aplicar esta recomendación")
    detected_pattern: str = Field(..., min_length=10, max_length=500, description="Breve explicación del patrón histórico que la sustenta")
    confidence: ConfidenceLevel = Field(..., description="Nivel de confianza basado en frecuencia del patrón")
    is_accepted: int = Field(0, description="Estado de la recomendación: 0=pendiente, 1=aceptada, -1=rechazada")


class RecommendationCreate(RecommendationBase):
    """Esquema para crear una nueva recomendación"""
    classroom_id: UUID = Field(..., description="ID del aula a la que pertenece la recomendación")


class RecommendationResponse(RecommendationBase):
    """Esquema de respuesta al consultar una recomendación"""
    id: UUID
    classroom_id: UUID
    generated_at: datetime = Field(..., description="Fecha y hora de generación de la recomendación")
    
    class Config:
        from_attributes = True

