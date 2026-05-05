import asyncio
import logging

from fastapi import APIRouter

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.llm.client_factory import get_llm_client

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> dict:
    """Check overall system health: Dalux API and LLM client connectivity."""
    dalux_ok = False
    llm_ok = False

    # Check Dalux connectivity
    try:
        adapter = DaluxAdapter()
        dalux_ok = await asyncio.to_thread(adapter.check_connectivity)
        adapter._client.close()
    except Exception as exc:
        logger.warning(f"Dalux health check failed: {exc}")

    # Check LLM client health
    try:
        llm_client = get_llm_client()
        llm_ok = await llm_client.check_health()
    except Exception as exc:
        logger.warning(f"LLM health check failed: {exc}")

    overall_ok = dalux_ok and llm_ok
    return {
        "ok": overall_ok,
        "service": "mcp-dalux-http-api",
        "dalux": dalux_ok,
        "llm": llm_ok,
    }
