import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.budget import BudgetRecordResponse, BudgetSummaryResponse
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/projects/{project_id}/budget", tags=["Budget"])


@router.post(
    "/upload",
    response_model=list[BudgetRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a financial budget CSV file",
)
async def upload_budget_csv(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not (file.filename.endswith(".csv") or file.filename.endswith(".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a valid .csv file",
        )

    try:
        content_bytes = await file.read()
        csv_text = content_bytes.decode("utf-8-sig")
        records = await BudgetService.ingest_csv_budget(
            db, project_id=project_id, csv_content=csv_text, filename=file.filename
        )
        return records
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file could not be decoded as UTF-8",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[BudgetRecordResponse],
    summary="List all budget line item records for a project",
)
async def list_budget_records(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await BudgetService.list_budget_records(db, project_id)


@router.get(
    "/summary",
    response_model=BudgetSummaryResponse,
    summary="Get aggregated budget summary with total planned, actual, and variance",
)
async def get_budget_summary(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    summary = await BudgetService.get_budget_summary(db, project_id)
    if not summary:
        raise HTTPException(status_code=404, detail="No budget records found for this project")
    return summary
