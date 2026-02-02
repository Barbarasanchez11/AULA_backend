from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any

class EventBase(BaseModel):
    situation: str = Field(..., max_length=100)
    context: Optional[Dict[str, Any]] = {}
    supports: List[str] = []
    result: str = Field(..., max_length=50)
    observations: Optional[str] = None

class EventCreate(EventBase):
    classroom_id: UUID

class EventResponse(EventBase):
    id: UUID
    classroom_id: UUID
    timestamp: datetime
    
    class Config:
        from_attributes = True
