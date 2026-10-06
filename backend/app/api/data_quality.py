import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.data_quality import DataQualityReportResponse
from app.services.data_quality_service import DataQualityService

router = APIRouter(prefix="/projects/{project_id}/data-quality", tags=["Data Quality"])


@router.get(
    "",
    response_model=DataQualityReportResponse,
    summary="Get project data quality report and composite reliability score",
)
async def get_data_quality_report(
    project_id: uuid.UUID,
    refresh: bool = Query(default=False, description="Whether to trigger fresh evaluation"),
    db: AsyncSession = Depends(get_db),
):
    try:
        if refresh:
            return await DataQualityService.evaluate_data_quality(db, project_id)
        return await DataQualityService.get_data_quality_report(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
