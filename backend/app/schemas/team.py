import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TeamMemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(default="engineer", max_length=100)
    email: Optional[str] = None
    github_username: Optional[str] = None


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberResponse(TeamMemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    members: list[TeamMemberResponse] = Field(default_factory=list)
