from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "riskzen-backend",
        "version": "0.0.1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
