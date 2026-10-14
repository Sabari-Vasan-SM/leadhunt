from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SearchJobCreate(BaseModel):
    query: str = Field(..., description="Natural language search query e.g. 'salons in Coimbatore'")
    category: Optional[str] = Field(None, description="Explicit category override e.g. 'salon'")
    location: Optional[str] = Field(None, description="Explicit location override e.g. 'Coimbatore'")
    max_results: Optional[int] = Field(default=30, ge=5, le=100)
    enable_website_crawl: bool = Field(default=True, description="Crawl discovered business websites for contact info")

class SearchJobResponse(BaseModel):
    id: str
    query: str
    category: Optional[str] = None
    location: Optional[str] = None
    status: str
    current_stage: Optional[str] = None
    total_discovered: int = 0
    total_processed: int = 0
    error_message: Optional[str] = None
    logs: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SearchJobStats(BaseModel):
    total_jobs: int
    completed_jobs: int
    total_leads: int
    leads_with_phone: int
    leads_with_email: int
    leads_with_website: int
