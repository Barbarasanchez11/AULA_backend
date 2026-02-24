from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.models.database import get_db
from app.models.models import Recommendation, Classroom, Event
from app.schemas.recommendation import RecommendationResponse, RecommendationCreate
from app.schemas.enums import RecommendationType, ConfidenceLevel
from app.services.recommendation_generator import RecommendationGenerator
from app.services.pattern_analysis import PatternAnalysisService

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
        is_accepted=int(recommendation.is_accepted),
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
    
    # Get all recommendations for this classroom, excluding rejected ones (-1)
    # Rejected recommendations are kept in the DB for model learning but not shown to the frontend
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.classroom_id == classroom_id,
            Recommendation.is_accepted != -1
        )
    )
    recommendations = result.scalars().all()
    
    # Convert models to response schemas
    return [recommendation_model_to_response(rec) for rec in recommendations]


@router.post("/generate", response_model=List[RecommendationResponse], status_code=201)
async def generate_recommendations(
    classroom_id: UUID = Query(..., description="ID of the classroom to generate recommendations for"),
    clustering_eps: float = Query(0.3, ge=0.0, le=1.0, description="DBSCAN eps parameter for pattern analysis"),
    clustering_min_samples: int = Query(2, ge=2, description="DBSCAN min_samples parameter for pattern analysis"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate recommendations automatically based on pattern analysis.
    
    Analyzes patterns in classroom events and generates actionable recommendations:
    - Support effectiveness recommendations
    - Temporal pattern recommendations
    - Clustering-based recommendations
    
    All generated recommendations are saved to the database and returned.
    """
    # Validate that the classroom exists
    result = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Get all events for this classroom
    result = await db.execute(select(Event).where(Event.classroom_id == classroom_id))
    events = result.scalars().all()
    
    if not events:
        raise HTTPException(
            status_code=404,
            detail="No events found for this classroom. Create some events first to generate recommendations."
        )
    
    try:
        # 1. Analyze patterns
        pattern_analysis_service = PatternAnalysisService()
        patterns = pattern_analysis_service.analyze_all_patterns(
            classroom_id=classroom_id,
            events=events,
            clustering_eps=clustering_eps,
            clustering_min_samples=clustering_min_samples
        )

        # 2. Generate recommendations from patterns
        recommendation_generator = RecommendationGenerator(db)
        recommendation_dicts = await recommendation_generator.generate_all_recommendations(
            classroom_id=classroom_id,
            events=events,
            pattern_results=patterns,  # Use pre-computed patterns
            clustering_eps=clustering_eps,
            clustering_min_samples=clustering_min_samples
        )
        
        if not recommendation_dicts:
            raise HTTPException(
                status_code=404,
                detail="No patterns detected strong enough to generate recommendations. "
                       "More events or stronger patterns are needed."
            )
        
        # 3. Save recommendations to database
        saved_recommendations = []
        for rec_dict in recommendation_dicts:
            db_recommendation = Recommendation(
                classroom_id=classroom_id,
                recommendation_type=rec_dict["recommendation_type"].value,
                title=rec_dict["title"],
                description=rec_dict["description"],
                applicable_context=rec_dict["applicable_context"],
                detected_pattern=rec_dict["detected_pattern"],
                confidence=rec_dict["confidence"].value
            )
            db.add(db_recommendation)
            saved_recommendations.append(db_recommendation)
        
        await db.commit()
        
        # Refresh all recommendations to get IDs
        for rec in saved_recommendations:
            await db.refresh(rec)
        
        # Convert to response schemas
        return [recommendation_model_to_response(rec) for rec in saved_recommendations]
    
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Recommendation generation service not available: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


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

@router.patch("/{id}/accept", response_model=RecommendationResponse)
async def accept_recommendation(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Mark a recommendation as accepted (is_accepted = 1).
    """
    result = await db.execute(select(Recommendation).where(Recommendation.id == id))
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.is_accepted = 1
    await db.commit()
    await db.refresh(recommendation)
    
    return recommendation_model_to_response(recommendation)


@router.patch("/{id}/reject", response_model=RecommendationResponse)
async def reject_recommendation(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Mark a recommendation as rejected (is_accepted = -1).
    
    Rejected recommendations are kept in the database so the system can
    learn from them in the future (negative feedback loop).
    The frontend should use this state to filter out recommendations the
    teacher has explicitly dismissed.
    
    States: 0=pending, 1=accepted, -1=rejected
    """
    result = await db.execute(select(Recommendation).where(Recommendation.id == id))
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.is_accepted = -1
    await db.commit()
    await db.refresh(recommendation)
    
    return recommendation_model_to_response(recommendation)
