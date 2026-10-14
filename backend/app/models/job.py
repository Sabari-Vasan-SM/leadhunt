import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class SearchJob(Base):
    __tablename__ = "search_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, discovering, crawling, completed, failed
    current_stage = Column(String(100), default="Queued")
    total_discovered = Column(Integer, default=0)
    total_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    logs = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    leads = relationship("Lead", back_populates="job", cascade="all, delete-orphan", lazy="selectin")
