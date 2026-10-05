from typing import Any, Optional
from pydantic import BaseModel, Field


class ServiceHealth(BaseModel):
    status: str = Field(..., description="'healthy', 'unhealthy', or 'degraded'")
    details: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall system health: 'healthy', 'degraded', 'unhealthy'")
    version: str = Field(default="0.1.0", description="API version")
    environment: str = Field(..., description="Application environment")
    database: ServiceHealth
    vector_extension: ServiceHealth
    llm_provider: ServiceHealth
