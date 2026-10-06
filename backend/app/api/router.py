from fastapi import APIRouter

from app.api.budget import router as budget_router
from app.api.data_quality import router as data_quality_router
from app.api.dependencies import router as dependencies_router
from app.api.health import router as health_router
from app.api.milestones import router as milestones_router
from app.api.projects import router as projects_router
from app.api.snapshots import router as snapshots_router
from app.api.sync import router as sync_router
from app.api.work_items import router as work_items_router

api_router = APIRouter()

# Health check
api_router.include_router(health_router, tags=["System"])

# Core Data Foundation Routers
api_router.include_router(projects_router)
api_router.include_router(work_items_router)
api_router.include_router(milestones_router)
api_router.include_router(dependencies_router)
api_router.include_router(budget_router)
api_router.include_router(data_quality_router)
api_router.include_router(snapshots_router)
api_router.include_router(sync_router)
