from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models.database import Base

class Classroom(Base):
    __tablename__ = "classrooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, default="TEA")
    extra_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    events = relationship("Event", back_populates="classroom", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=False)
    
    # Event fields
    situation = Column(String(100), nullable=False)
    context = Column(JSON, default={})
    supports = Column(JSON, default=[])
    result = Column(String(50), nullable=False)
    observations = Column(Text, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    classroom = relationship("Classroom", back_populates="events")
