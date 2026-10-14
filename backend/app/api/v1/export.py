import re
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.job import SearchJob
from app.models.lead import Lead
from app.services.export.excel_exporter import ExcelExporter

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/jobs/{job_id}")
async def export_job_leads(
    job_id: str,
    format: str = Query("xlsx", pattern="^(xlsx|csv)$"),
    db: AsyncSession = Depends(get_db)
):
    job = await db.get(SearchJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Search job not found")

    result = await db.execute(select(Lead).where(Lead.job_id == job_id))
    leads = result.scalars().all()

    clean_name = re.sub(r'[^\w\-]', '_', job.query)
    clean_name = clean_name[:40]

    if format == "xlsx":
        content = ExcelExporter.export_to_excel(leads, query_name=job.query)
        filename = f"leads_{clean_name}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        content = ExcelExporter.export_to_csv(leads)
        filename = f"leads_{clean_name}.csv"
        media_type = "text/csv; charset=utf-8"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
