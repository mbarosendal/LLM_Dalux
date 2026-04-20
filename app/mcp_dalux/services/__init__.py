"""Application services for the HTTP/API layer.

Put session management, prompt orchestration, and LLM calls here.
Keep FastAPI route handlers thin and boring.

API layer: Pydantic models like CreateSessionRequest and SendPromptRequest
Service layer: converts API models into SessionContext
Orchestration layer: builds instructions from SessionContext
Runtime/agent layer: uses the built instructions
"""
