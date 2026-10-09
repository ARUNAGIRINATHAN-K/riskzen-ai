from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.router import api_router
from app.config import settings
from app.scheduler.jobs import shutdown_scheduler, start_scheduler
from app.utils.logging import get_logger, setup_logging

setup_logging()
logger = get_logger("riskzen.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(
        "RiskZen Backend starting",
        environment=settings.ENVIRONMENT,
        log_level=settings.LOG_LEVEL,
        llm_provider=settings.LLM_PROVIDER,
    )
    # Start background scheduler in non-testing environments
    if settings.ENVIRONMENT != "testing":
        try:
            start_scheduler()
        except Exception as exc:
            logger.warn("Scheduler failed to start during lifespan", error=str(exc))

    yield

    if settings.ENVIRONMENT != "testing":
        try:
            shutdown_scheduler()
        except Exception as exc:
            logger.warn("Scheduler shutdown error", error=str(exc))

    logger.info("RiskZen Backend shutting down")


app = FastAPI(
    title="RiskZen API",
    description="AI-Powered Project Risk Early-Warning & Mitigation System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoints
@app.get("/", tags=["General"])
async def root():
    return {
        "app": "RiskZen API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# Include Health router at top-level /health as well
app.include_router(health_router, prefix="")

# Mount versioned API router at /api/v1
app.include_router(api_router, prefix="/api/v1")
