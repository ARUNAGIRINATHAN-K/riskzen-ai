from fastapi import APIRouter

from app.api.health import router as health_router

api_router = APIRouter()

# Health check
api_router.include_router(health_router, tags=["System"])

# Future routers will be added here as modules are built:
# api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
# api_router.include_router(risks_router, prefix="/risks", tags=["Risks"])
# api_router.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
# api_router.include_router(actions_router, prefix="/actions", tags=["Actions"])
