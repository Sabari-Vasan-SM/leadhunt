import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("search_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    business_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True, index=True)
    pincode = Column(String(20), nullable=True)
    phone = Column(String(50), nullable=True, index=True)
    email = Column(String(150), nullable=True, index=True)
    website_url = Column(Text, nullable=True)
    google_maps_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    source_name = Column(String(50), default="OpenStreetMap")
    confidence_score = Column(Float, default=1.0)
    raw_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("SearchJob", back_populates="leads")
