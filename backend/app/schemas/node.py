from datetime import datetime

from pydantic import BaseModel, Field


class NodeRead(BaseModel):
    id: str
    machine_id: str
    hostname: str
    os_name: str | None
    kernel: str | None
    architecture: str | None
    online: bool
    last_seen_at: datetime | None
    created_at: datetime


class EnrollmentTokenCreate(BaseModel):
    expires_in_hours: int | None = Field(default=24, ge=1, le=720)


class EnrollmentTokenRead(BaseModel):
    id: str
    token: str
    expires_at: datetime | None


class AgentEnrollRequest(BaseModel):
    enrollment_token: str
    machine_id: str = Field(min_length=1, max_length=512)
    hostname: str = Field(min_length=1, max_length=255)
    os_name: str | None = Field(default=None, max_length=255)
    kernel: str | None = Field(default=None, max_length=255)
    architecture: str | None = Field(default=None, max_length=64)


class AgentEnrollResponse(BaseModel):
    node_id: str
    agent_token: str
