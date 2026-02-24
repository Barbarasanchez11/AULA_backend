from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from typing import List, Optional


from app.models.database import get_db
from app.models.models import Event, Classroom
from app.schemas.event import EventCreate, EventResponse, EventContext, EventUpdate, SimilarEventResponse, PatternAnalysisResponse
from app.schemas.enums import EventType, EventResult, MomentOfDay, DayOfWeek, SupportType
from app.services.embeddingService import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.pattern_analysis import PatternAnalysisService
from app.services.text_normalizer import TextNormalizer
from app.services.pii_validator import PIIValidator

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

def event_model_to_response(event: Event) -> EventResponse:
    """Convert Event model to EventResponse schema"""
    return EventResponse(
        id=event.id,
        classroom_id=event.classroom_id,
        event_type=EventType(event.event_type),
        description=event.description,
        context=EventContext(
            moment_of_day=MomentOfDay(event.moment_of_day),
            day_of_week=DayOfWeek(event.day_of_week) if event.day_of_week else None,
            duration_minutes=event.duration_minutes
        ),
        supports=[SupportType(support) for support in event.supports],
        additional_supports=event.additional_supports,
        result=EventResult(event.result),
        observations=event.observations,
        timestamp=event.timestamp,
        is_planned=event.is_planned
    )

@router.get("/", response_model=List[EventResponse])
async def list_events(
    classroom_id: UUID = Query(..., description="ID of the classroom to filter events"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all events for a specific classroom.
    
    Returns a list of all events belonging to the specified classroom.
    Requires classroom_id as a query parameter.
    """
    # Validate that the classroom exists
    result = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Get all events for this classroom
    result = await db.execute(select(Event).where(Event.classroom_id == classroom_id))
    events = result.scalars().all()
    
    # Convert models to response schemas
    return [event_model_to_response(event) for event in events]


@router.get("/patterns", response_model=PatternAnalysisResponse)
async def analyze_patterns(
    classroom_id: UUID = Query(..., description="ID of the classroom to analyze"),
    clustering_eps: float = Query(0.3, ge=0.0, le=1.0, description="DBSCAN eps parameter (0.0-1.0)"),
    clustering_min_samples: int = Query(2, ge=2, description="DBSCAN min_samples parameter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze patterns in classroom events.
    
    Performs three types of analysis:
    - Clustering: Groups similar events using semantic similarity
    - Temporal patterns: Detects day of week and moment of day patterns
    - Support effectiveness: Analyzes which supports work best
    
    Returns comprehensive pattern analysis results.
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
            detail="No events found for this classroom. Create some events first."
        )
    
    try:
        # Initialize pattern analysis service
        pattern_service = PatternAnalysisService()
        
        # Perform analysis
        analysis_results = pattern_service.analyze_all_patterns(
            classroom_id=classroom_id,
            events=events,
            clustering_eps=clustering_eps,
            clustering_min_samples=clustering_min_samples
        )
        
        return PatternAnalysisResponse(
            clustering=analysis_results.get("clustering", {}),
            temporal_patterns=analysis_results.get("temporal_patterns", {}),
            support_effectiveness=analysis_results.get("support_effectiveness", {})
        )
    
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Pattern analysis service not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing patterns: {str(e)}"
        )


@router.get("/similar", response_model=List[SimilarEventResponse])
async def get_similar_events(
    event_id: UUID = Query(..., description="ID of the event to find similar events for"),
    classroom_id: UUID = Query(..., description="ID of the classroom"),
    top_k: int = Query(5, ge=1, le=20, description="Number of similar events to return (1-20)"),
    model_type: str = Query("quality", regex="^(fast|quality)$", description="Model to use for search (fast or quality)"),
    min_similarity: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity score (0.0 to 1.0)"),
    event_type_filter: Optional[str] = Query(None, description="Filter by event type (optional)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Find similar events using semantic search.
    
    Given an event ID, generates its embedding and searches for similar events
    in the same classroom using vector similarity.
    
    Returns a list of similar events ordered by similarity score (highest first).
    """
    # Validate that the classroom exists
    result = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Get the source event
    result = await db.execute(select(Event).where(Event.id == event_id))
    source_event = result.scalar_one_or_none()
    
    if not source_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Verify event belongs to the classroom
    if source_event.classroom_id != classroom_id:
        raise HTTPException(status_code=400, detail="Event does not belong to the specified classroom")
    
    try:
        # Get services
        embedding_service = EmbeddingService.get_instance()
        vector_store = VectorStore()
        
        # Generate embedding for the source event
        query_embedding = embedding_service.generate_event_embedding(
            event_type=source_event.event_type,
            description=source_event.description,
            moment_of_day=source_event.moment_of_day,
            day_of_week=source_event.day_of_week,
            supports=source_event.supports,
            result=source_event.result,
            additional_supports=source_event.additional_supports,
            observations=source_event.observations,
            model_type=model_type
        )
        
        # Prepare filters (model_type is now handled by collection selection, not filter)
        search_filters = None
        if event_type_filter:
            search_filters = {"event_type": event_type_filter}
        
        # Search for similar events (model_type determines which collection to search)
        similar_results = vector_store.search_similar_events(
            classroom_id=classroom_id,
            query_embedding=query_embedding,
            top_k=top_k + 1,  # +1 because we'll filter out the source event
            filters=search_filters,
            min_similarity=min_similarity,
            model_type=model_type
        )
        
        # If no similar events found, return empty list (this is normal if embeddings haven't been generated yet)
        if not similar_results:
            return []
        
        # Get full event details from database
        similar_events = []
        for result_item in similar_results:
            # Extract original event_id from metadata
            original_event_id_str = result_item["metadata"].get("original_event_id")
            if not original_event_id_str:
                # Fallback: try to parse from the stored event_id
                stored_id = result_item["metadata"].get("event_id", "")
                # Remove _fast or _quality suffix if present
                original_event_id_str = stored_id.replace("_fast", "").replace("_quality", "")
            
            try:
                similar_event_id = UUID(original_event_id_str)
                
                # Skip if it's the source event itself
                if similar_event_id == event_id:
                    continue
                
                # Get event from database
                result = await db.execute(select(Event).where(Event.id == similar_event_id))
                similar_event = result.scalar_one_or_none()
                
                if similar_event:
                    similar_events.append(SimilarEventResponse(
                        event=event_model_to_response(similar_event),
                        similarity_score=result_item["score"]
                    ))
            except (ValueError, TypeError):
                # Skip invalid UUIDs
                continue
        
        # Sort by similarity score (highest first) and limit to top_k
        similar_events.sort(key=lambda x: x.similarity_score, reverse=True)
        return similar_events[:top_k]
        
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="Embedding service not available. Ensure sentence-transformers and chromadb are installed."
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404, 400, etc.)
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_similar_events: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching for similar events: {str(e)}"
        )


@router.get("/{id}", response_model=EventResponse)
async def get_event(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get a specific event by ID.
    
    Returns the event details if found, or 404 if not found.
    """
    result = await db.execute(select(Event).where(Event.id == id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event_model_to_response(event)


@router.put("/{id}", response_model=EventResponse)
async def update_event(
    id: UUID,
    event_update: EventUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an event by ID.
    
    Updates only the provided fields and returns the updated event.
    If fields that affect embeddings are updated, embeddings are regenerated.
    Returns 404 if the event is not found.
    """
    result = await db.execute(select(Event).where(Event.id == id))
    db_event = result.scalar_one_or_none()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Track if embedding-relevant fields were updated
    embedding_fields_updated = False
    
    # Update only the fields that were provided
    update_data = event_update.model_dump(exclude_unset=True)
    
    # Handle context separately (nested object)
    if "context" in update_data and update_data["context"]:
        context_data = update_data.pop("context")
        if context_data.get("moment_of_day") is not None:
            moment = context_data["moment_of_day"]
            db_event.moment_of_day = moment.value if isinstance(moment, MomentOfDay) else moment
            embedding_fields_updated = True
        if context_data.get("day_of_week") is not None:
            day = context_data["day_of_week"]
            db_event.day_of_week = day.value if isinstance(day, DayOfWeek) else day
            embedding_fields_updated = True
        if context_data.get("duration_minutes") is not None:
            db_event.duration_minutes = context_data["duration_minutes"]
            # duration_minutes doesn't affect embedding, so no flag update
    
    # Handle enum fields
    if "event_type" in update_data and update_data["event_type"] is not None:
        event_type = update_data.pop("event_type")
        db_event.event_type = event_type.value if isinstance(event_type, EventType) else event_type
        embedding_fields_updated = True
    
    if "result" in update_data and update_data["result"] is not None:
        result = update_data.pop("result")
        db_event.result = result.value if isinstance(result, EventResult) else result
        embedding_fields_updated = True
    
    if "supports" in update_data and update_data["supports"] is not None:
        supports = update_data.pop("supports")
        db_event.supports = [
            support.value if isinstance(support, SupportType) else support 
            for support in supports
        ]
        embedding_fields_updated = True
    
    # Normalize and validate text fields if they are being updated
    normalizer = TextNormalizer()
    pii_validator = PIIValidator()
    
    # Prepare normalized and validated text fields
    if "description" in update_data and update_data["description"] is not None:
        embedding_fields_updated = True
        # Normalize
        normalized_description = normalizer.normalize_text(update_data["description"])
        # Validate PII
        pii_result = pii_validator.validate_text(normalized_description, context="description")
        if not pii_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=pii_result.get_error_message()
            )
        db_event.description = normalized_description
    
    if "additional_supports" in update_data and update_data["additional_supports"] is not None:
        embedding_fields_updated = True
        # Normalize
        normalized_additional_supports = normalizer.normalize_text(update_data["additional_supports"])
        # Validate PII
        pii_result = pii_validator.validate_text(normalized_additional_supports, context="additional_supports")
        if not pii_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=pii_result.get_error_message()
            )
        db_event.additional_supports = normalized_additional_supports
    
    if "observations" in update_data and update_data["observations"] is not None:
        embedding_fields_updated = True
        # Normalize
        normalized_observations = normalizer.normalize_text(update_data["observations"])
        # Validate PII
        pii_result = pii_validator.validate_text(normalized_observations, context="observations")
        if not pii_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=pii_result.get_error_message()
            )
        db_event.observations = normalized_observations
    
    # Update other fields
    for field, value in update_data.items():
        if value is not None and field not in ["description", "additional_supports", "observations"]:
            setattr(db_event, field, value)
    
    await db.commit()
    await db.refresh(db_event)
    
    # Regenerate embeddings if embedding-relevant fields were updated
    if embedding_fields_updated:
        # Use normalized values for embeddings
        background_tasks.add_task(
            _generate_and_store_embeddings,
            event_id=db_event.id,
            classroom_id=db_event.classroom_id,
            event_type=db_event.event_type,
            description=db_event.description,  # Already normalized
            moment_of_day=db_event.moment_of_day,
            day_of_week=db_event.day_of_week,
            supports=db_event.supports,
            result=db_event.result,
            additional_supports=db_event.additional_supports,  # Already normalized
            observations=db_event.observations  # Already normalized
        )
    
    return event_model_to_response(db_event)

def _delete_event_embeddings(classroom_id: UUID, event_id: UUID):
    """
    Background task to delete embeddings for an event.
    
    This function runs in the background after the HTTP response is sent.
    """
    try:
        vector_store = VectorStore()
        vector_store.delete_event_embedding(
            classroom_id=classroom_id,
            event_id=event_id,
            delete_both_models=True
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error deleting embeddings for event {event_id}: {e}")


@router.delete("/{id}", status_code=204)
async def delete_event(
    id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an event by ID.
    
    Deletes the event from the database and removes its embeddings from the vector store.
    Returns 204 No Content if successful, or 404 if not found.
    """
    result = await db.execute(select(Event).where(Event.id == id))
    db_event = result.scalar_one_or_none()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Store IDs before deletion
    event_id = db_event.id
    classroom_id = db_event.classroom_id
    
    await db.delete(db_event)
    await db.commit()
    
    # Delete embeddings in background
    background_tasks.add_task(
        _delete_event_embeddings,
        classroom_id=classroom_id,
        event_id=event_id
    )
    
    return None

def _generate_and_store_embeddings(
    event_id: UUID,
    classroom_id: UUID,
    event_type: str,
    description: str,
    moment_of_day: str,
    day_of_week: str | None,
    supports: List[str],
    result: str,
    additional_supports: str | None,
    observations: str | None
):
    """
    Background task to generate and store embeddings for an event.
    
    This function runs in the background after the HTTP response is sent,
    so it doesn't block the API response.
    """
    try:
        # Get services
        embedding_service = EmbeddingService.get_instance()
        vector_store = VectorStore()
        
        # Generate embeddings (both fast and quality)
        embedding_fast = embedding_service.generate_event_embedding(
            event_type=event_type,
            description=description,
            moment_of_day=moment_of_day,
            day_of_week=day_of_week,
            supports=supports,
            result=result,
            additional_supports=additional_supports,
            observations=observations,
            model_type="fast"
        )
        
        embedding_quality = embedding_service.generate_event_embedding(
            event_type=event_type,
            description=description,
            moment_of_day=moment_of_day,
            day_of_week=day_of_week,
            supports=supports,
            result=result,
            additional_supports=additional_supports,
            observations=observations,
            model_type="quality"
        )
        
        # Store embeddings in VectorStore with metadata
        metadata = {
            "event_type": event_type,
            "result": result,
            "moment_of_day": moment_of_day
        }
        
        # Store fast embedding (for quick searches)
        # Use event_id directly (not with suffix, since we use separate collections)
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=str(event_id),  # Use event_id directly
            embedding=embedding_fast,
            metadata={**metadata, "original_event_id": str(event_id)},
            model_type="fast"
        )
        
        # Store quality embedding (for analysis and recommendations)
        # Use event_id directly (not with suffix, since we use separate collections)
        vector_store.add_event_embedding(
            classroom_id=classroom_id,
            event_id=str(event_id),  # Use event_id directly
            embedding=embedding_quality,
            metadata={**metadata, "original_event_id": str(event_id)},
            model_type="quality"
        )
        
    except Exception as e:
        # Log error but don't fail the request
        # In production, you might want to use a proper logging system
        print(f"Error generating embeddings for event {event_id}: {e}")


@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event: EventCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new event.
    
    Creates a new pedagogical event for a classroom.
    Validates that the classroom exists before creating the event.
    Automatically generates and stores embeddings for semantic search.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Log the received event data for debugging
    logger.info(f"Creating event for classroom {event.classroom_id}")
    logger.debug(f"Event data: {event.model_dump()}")
    # Validate that the classroom exists
    result = await db.execute(select(Classroom).where(Classroom.id == event.classroom_id))
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Normalize text fields
    normalizer = TextNormalizer()
    normalized = normalizer.normalize_event_text(
        description=event.description,
        additional_supports=event.additional_supports,
        observations=event.observations
    )
    
    # Validate PII (check for personal data)
    pii_validator = PIIValidator()
    pii_result = pii_validator.validate_event_text(
        description=normalized["description"],
        additional_supports=normalized["additional_supports"],
        observations=normalized["observations"]
    )
    
    if not pii_result.is_valid:
        raise HTTPException(
            status_code=400,
            detail=pii_result.get_error_message()
        )
    
    # Convert EventContext to separate fields
    # Convert List[SupportType] to JSON array of strings
    # Use normalized text instead of original
    db_event = Event(
        classroom_id=event.classroom_id,
        event_type=event.event_type.value,
        description=normalized["description"],
        moment_of_day=event.context.moment_of_day.value,
        day_of_week=event.context.day_of_week.value if event.context.day_of_week else None,
        duration_minutes=event.context.duration_minutes,
        supports=[support.value for support in event.supports],
        additional_supports=normalized["additional_supports"],
        result=event.result.value,
        observations=normalized["observations"],
        is_planned=event.is_planned,
        timestamp=event.timestamp.replace(tzinfo=None) if event.timestamp else datetime.utcnow()
    )
    
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    
    # Schedule background task to generate and store embeddings
    # This runs after the HTTP response is sent, so it doesn't block the API
    background_tasks.add_task(
        _generate_and_store_embeddings,
        event_id=db_event.id,
        classroom_id=db_event.classroom_id,
        event_type=db_event.event_type,
        description=db_event.description,
        moment_of_day=db_event.moment_of_day,
        day_of_week=db_event.day_of_week,
        supports=db_event.supports,
        result=db_event.result,
        additional_supports=db_event.additional_supports,
        observations=db_event.observations
    )
    
    # Convert model to response schema
    return event_model_to_response(db_event)
