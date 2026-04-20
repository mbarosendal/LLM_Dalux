from fastapi import APIRouter

router = APIRouter(tags=["health"])

# Add health endpoints here. Minimal at first, then extend with dependency checks such as config, session store, and LLM reachability later.

@router.get("/health")
def health_check() -> dict:
    """Minimal connectivity check for deployment and local testing.
    
        """
    return {"ok": True, "service": "mcp-dalux-http-api"}
