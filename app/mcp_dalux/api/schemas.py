from __future__ import annotations

from pydantic import BaseModel, Field

# Add request/response contracts here before building business logic.
# These models "freeze contracts" so the API stays stable.
#
# Start with:
# - CreateSessionRequest
# - CreateSessionResponse
# - SendPromptRequest
# - SendPromptResponse
# - ApiError
#
# Keeping the schemas minimal at first.

class ApiError(BaseModel):
    code: str = Field(..., description="Short machine-readable error code")
    message: str = Field(..., description="Human-readable error message")


class CreateSessionRequest(BaseModel):
    project_name: str = Field(..., min_length=1)
    category: str = Field(default="tasks")

class CreateSessionResponse(BaseModel):
    session_id: str
    startTime: str
    endTime : str
    project_name: str
    category: str
    subject : str


class SendPromptRequest(BaseModel):
    timestamp: str
    text: str = Field(..., min_length=1)


class SendPromptResponse(BaseModel):
    session_id: str
    timestamp: str
    text: str
