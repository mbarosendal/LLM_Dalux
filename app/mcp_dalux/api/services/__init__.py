"""Application services for the HTTP/API layer.

Put session management, prompt orchestration, and LLM calls here.
Keep FastAPI route handlers thin and boring.

API layer: Pydantic models like StartSessionRequest and SendPromptRequest
Service layer: maps API contracts to/from SessionState
Orchestration layer: builds instructions from SessionState
Runtime/agent layer: uses the built instructions
"""
