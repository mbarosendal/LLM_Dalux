from functools import wraps
from typing import Any, Callable

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context


class ToolPolicyError(RuntimeError):
    """Raised when a tool policy constraint is violated."""


class ToolPolicy:
    """Decorator to enforce per-tool call caps per user prompt."""

    def __init__(self, max_calls: int = 5) -> None:
        if max_calls < 1:
            raise ValueError("max_calls must be >= 1")

        self.max_calls = max_calls
        # Using a dict keyed by (function name, request key) to track calls per tool per request.
        self.calls_by_request: dict[tuple[str, str], int] = {}

    # Uses a FastMcp method to retrieve a stable key for the current user prompt.
    def _get_request_key(self) -> str:
        """Resolve a stable key for the current user prompt."""
        try:
            ctx = get_context()
            return ctx.origin_request_id or ctx.request_id or "unknown-request"
        except RuntimeError:
            # Fallback for execution paths without an active FastMCP context.
            return "no-active-context"

    # The __call__ method lets the decorator pass parameters and wrap the target function (fn).
    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            request_key = self._get_request_key()
            counter_key = (fn.__name__, request_key)
            calls = self.calls_by_request.get(counter_key, 0)

            if calls >= self.max_calls:
                message = (
                    f"Tool call limit reached for '{fn.__name__}' in this request "
                    f"({self.max_calls})."
                )
                raise ToolError(message) from ToolPolicyError(message)

            self.calls_by_request[counter_key] = calls + 1
            return fn(*args, **kwargs)

        return wrapper
