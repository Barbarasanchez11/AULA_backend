from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.models.database import get_db
from app.models.models import Recommendation, Classroom
from app.schemas.recommendation import RecommendationResponse, RecommendationCreate
from app.schemas.enums import RecommendationType, ConfidenceLevel

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

def recommendation_model_to_response(recommendation: Recommendation) -> RecommendationResponse:
    """Convert Recommendation model to RecommendationResponse schema"""
    return RecommendationResponse(
        id=recommendation.id,
        classroom_id=recommendation.classroom_id,
        recommendation_type=RecommendationType(recommendation.recommendation_type),
        title=recommendation.title,
        description=recommendation.description,
        applicable_context=recommendation.applicable_context,
        detected_pattern=recommendation.detected_pattern,
        confidence=ConfidenceLevel(recommendation.confidence),
        generated_at=recommendation.generated_at
    )

@router.get("/", response_model=List[RecommendationResponse])
async def list_recommendations(
    classroom_id: UUID = Query(..., description="ID of the classroom to filter recommendations"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all recommendations for a specific classroom.
    
    Returns a list of all recommendations belonging to the specified classroom.
    Requires classroom_id as a query parameter.
    """
    # Validate that the classroom exists
    result = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Get all recommendations for this classroom
    result = await db.execute(select(Recommendation).where(Recommendation.classroom_id == classroom_id))
    recommendations = result.scalars().all()
    
    # Convert models to response schemas
    return [recommendation_model_to_response(rec) for rec in recommendations]

@router.get("/{id}", response_model=RecommendationResponse)
async def get_recommendation(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get a specific recommendation by ID.
    
    Returns the recommendation details if found, or 404 if not found.
    """
    result = await db.execute(select(Recommendation).where(Recommendation.id == id))
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    return recommendation_model_to_response(recommendation)

@router.post("/", response_model=RecommendationResponse, status_code=201)
async def create_recommendation(recommendation: RecommendationCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new recommendation.
    
    Creates a new pedagogical recommendation for a classroom.
    Validates that the classroom exists before creating the recommendation.
    
    Note: In production, recommendations are generated automatically by the system.
    This endpoint is useful for testing and manual creation during development.
    """
    # Validate that the classroom exists
    result = await db.execute(select(Classroom).where(Classroom.id == recommendation.classroom_id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Create recommendation from schema
    db_recommendation = Recommendation(
        classroom_id=recommendation.classroom_id,
        recommendation_type=recommendation.recommendation_type.value,
        title=recommendation.title,
        description=recommendation.description,
        applicable_context=recommendation.applicable_context,
        detected_pattern=recommendation.detected_pattern,
        confidence=recommendation.confidence.value
    )
    
    db.add(db_recommendation)
    await db.commit()
    await db.refresh(db_recommendation)
    
    # Convert model to response schema
    return recommendation_model_to_response(db_recommendation)

