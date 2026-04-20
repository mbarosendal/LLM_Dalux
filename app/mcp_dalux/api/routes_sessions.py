from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Add session-related endpoints we expose here.

# Build order:
# 1. Add request/response models in api.schemas.
# 2. Add session creation first.
# 3. Store sessions in memory first; persistence can come later.
# 4. Add prompt sending after session creation works.
# 5. Only then connect the agent loop and LLM client.
#
# Endpoints:
# - POST /sessions/create
# - POST /sessions/{sessionId}/prompts/send
# - GET /sessions/{sessionId} (optional for debugging)
# - DELETE /sessions/{sessionId} (optional cleanup)
