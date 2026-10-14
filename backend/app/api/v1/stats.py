from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.models.job import SearchJob
from app.models.lead import Lead
from app.schemas.job import SearchJobStats

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("", response_model=SearchJobStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    # Total jobs
    total_jobs_res = await db.execute(select(func.count(SearchJob.id)))
    total_jobs = total_jobs_res.scalar() or 0

    # Completed jobs
    completed_jobs_res = await db.execute(
        select(func.count(SearchJob.id)).where(SearchJob.status == "completed")
    )
    completed_jobs = completed_jobs_res.scalar() or 0

    # Total leads
    total_leads_res = await db.execute(select(func.count(Lead.id)))
    total_leads = total_leads_res.scalar() or 0

    # Leads with phone
    phone_res = await db.execute(
        select(func.count(Lead.id)).where(
            and_(Lead.phone.isnot(None), Lead.phone != "")
        )
    )
    leads_with_phone = phone_res.scalar() or 0

    # Leads with email
    email_res = await db.execute(
        select(func.count(Lead.id)).where(
            and_(Lead.email.isnot(None), Lead.email != "")
        )
    )
    leads_with_email = email_res.scalar() or 0

    # Leads with website
    website_res = await db.execute(
        select(func.count(Lead.id)).where(
            and_(Lead.website_url.isnot(None), Lead.website_url != "")
        )
    )
    leads_with_website = website_res.scalar() or 0

    return SearchJobStats(
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        total_leads=total_leads,
        leads_with_phone=leads_with_phone,
        leads_with_email=leads_with_email,
        leads_with_website=leads_with_website
    )
