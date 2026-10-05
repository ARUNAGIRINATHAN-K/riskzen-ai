from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas.health import HealthResponse, ServiceHealth
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check with component status",
    description="Returns system operational status, database connectivity, vector extension, and configured LLM provider.",
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check endpoint verifying database and system components."""
    db_health = ServiceHealth(status="healthy")
    vector_health = ServiceHealth(status="healthy")
    llm_health = ServiceHealth(
        status="configured",
        details={
            "provider": settings.LLM_PROVIDER,
            "model": settings.LLM_MODEL,
        },
    )

    # 1. Check PostgreSQL Database Connection
    try:
        result = await db.execute(text("SELECT 1"))
        _ = result.scalar()
        db_health.status = "healthy"
        db_health.details = {"connected": True}
    except Exception as exc:
        logger.error("Health check database query failed", error=str(exc))
        db_health.status = "unhealthy"
        db_health.details = {"connected": False, "error": str(exc)}

    # 2. Check pgvector extension
    try:
        result = await db.execute(
            text("SELECT installed_version FROM pg_available_extensions WHERE name = 'vector'")
        )
        row = result.fetchone()
        if row and row[0]:
            vector_health.status = "healthy"
            vector_health.details = {"installed": True, "version": row[0]}
        else:
            vector_health.status = "degraded"
            vector_health.details = {"installed": False, "note": "pgvector extension not yet enabled or not available"}
    except Exception as exc:
        logger.warn("Health check pgvector extension query failed", error=str(exc))
        vector_health.status = "unknown"
        vector_health.details = {"error": str(exc)}

    # Determine overall status
    if db_health.status == "healthy":
        overall_status = "healthy"
        status_code = status.HTTP_200_OK
    else:
        overall_status = "degraded" if db_health.status != "unhealthy" else "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE if db_health.status == "unhealthy" else status.HTTP_200_OK

    response_data = HealthResponse(
        status=overall_status,
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        database=db_health,
        vector_extension=vector_health,
        llm_provider=llm_health,
    )

    return JSONResponse(status_code=status_code, content=response_data.model_dump())
