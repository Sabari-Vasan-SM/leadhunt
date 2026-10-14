from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class LeadBase(BaseModel):
    business_name: str
    category: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    google_maps_url: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = "OpenStreetMap"
    confidence_score: float = 1.0

class LeadCreate(LeadBase):
    job_id: str
    raw_metadata: Optional[Dict[str, Any]] = None

class LeadResponse(LeadBase):
    id: str
    job_id: str
    created_at: datetime
    raw_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class LeadFilterParams(BaseModel):
    query: Optional[str] = None
    city: Optional[str] = None
    has_phone: Optional[bool] = None
    has_email: Optional[bool] = None
    has_website: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
