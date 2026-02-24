from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any

class ClassroomBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    type: str = Field(default="TEA", max_length=50)
    extra_metadata: Optional[Dict[str, Any]] = {}

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    type: Optional[str] = Field(None, max_length=50)
    extra_metadata: Optional[Dict[str, Any]] = None

class ClassroomResponse(ClassroomBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
