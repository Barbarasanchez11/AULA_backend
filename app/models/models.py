from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text, Integer
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
    
    # Relationships
    events = relationship("Event", back_populates="classroom", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="classroom", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    
    # IDs and relationships
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=False)
    
    # Main fields
    event_type = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    
    # Context fields (structured instead of JSON)
    moment_of_day = Column(String(20), nullable=False)
    day_of_week = Column(String(20), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Supports
    supports = Column(JSON, default=[])
    additional_supports = Column(Text, nullable=True)
    
    # Result and observations
    result = Column(String(50), nullable=False)
    observations = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    classroom = relationship("Classroom", back_populates="events")


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    # IDs and relationships
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=False)
    
    # Main fields
    recommendation_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    applicable_context = Column(Text, nullable=False)
    detected_pattern = Column(Text, nullable=False)
    confidence = Column(String(20), nullable=False)
    is_accepted = Column(Integer, default=0) # 0 para False, 1 para True (compatible con SQLite/Postgres)
    
    # Timestamp
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    classroom = relationship("Classroom", back_populates="recommendations")
