from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.job import SearchJob
from app.schemas.job import SearchJobCreate, SearchJobResponse
from app.services.pipeline.scraping_manager import ScrapingManager

router = APIRouter(prefix="/jobs", tags=["Jobs"])
scraping_manager = ScrapingManager()

@router.post("", response_model=SearchJobResponse)
async def create_search_job(
    payload: SearchJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    job = SearchJob(
        query=payload.query.strip(),
        category=payload.category.strip() if payload.category else None,
        location=payload.location.strip() if payload.location else None,
        status="pending",
        current_stage="Queued in background",
        total_discovered=0,
        total_processed=0,
        logs=[]
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Launch background task
    background_tasks.add_task(
        scraping_manager.run_pipeline,
        job.id,
        payload.max_results,
        payload.enable_website_crawl
    )

    return job

@router.get("", response_model=List[SearchJobResponse])
async def list_jobs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SearchJob).order_by(desc(SearchJob.created_at)).limit(limit)
    )
    return result.scalars().all()

@router.get("/{job_id}", response_model=SearchJobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(SearchJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Search job not found")
    return job

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(SearchJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Search job not found")
    await db.delete(job)
    await db.commit()
    return {"message": "Job deleted successfully"}
