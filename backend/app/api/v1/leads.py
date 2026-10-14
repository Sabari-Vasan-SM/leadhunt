from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, or_
from app.core.database import get_db
from app.models.lead import Lead
from app.models.job import SearchJob
from app.schemas.lead import LeadResponse

router = APIRouter(tags=["Leads"])

@router.get("/jobs/{job_id}/leads")
async def get_job_leads(
    job_id: str,
    search: Optional[str] = Query(None, description="Search term in name, address, phone, or email"),
    city: Optional[str] = Query(None),
    has_phone: Optional[bool] = Query(None),
    has_email: Optional[bool] = Query(None),
    has_website: Optional[bool] = Query(None),
    sort_by: str = Query("confidence_score"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    # Verify job exists
    job = await db.get(SearchJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Search job not found")

    query = select(Lead).where(Lead.job_id == job_id)

    # Search filter
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Lead.business_name.ilike(term),
                Lead.address.ilike(term),
                Lead.city.ilike(term),
                Lead.phone.ilike(term),
                Lead.email.ilike(term)
            )
        )

    # Attribute filters
    if city and city.strip():
        query = query.where(Lead.city.ilike(f"%{city.strip()}%"))

    if has_phone is True:
        query = query.where(Lead.phone.isnot(None), Lead.phone != "")
    elif has_phone is False:
        query = query.where(or_(Lead.phone.is_(None), Lead.phone == ""))

    if has_email is True:
        query = query.where(Lead.email.isnot(None), Lead.email != "")
    elif has_email is False:
        query = query.where(or_(Lead.email.is_(None), Lead.email == ""))

    if has_website is True:
        query = query.where(Lead.website_url.isnot(None), Lead.website_url != "")
    elif has_website is False:
        query = query.where(or_(Lead.website_url.is_(None), Lead.website_url == ""))

    # Count total matching
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sorting
    sort_col = getattr(Lead, sort_by, Lead.confidence_score)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    leads = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return {
        "items": [LeadResponse.model_validate(lead) for lead in leads],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": total_pages
    }
