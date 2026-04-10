import time
from functools import wraps
from typing import Any, Callable

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context


class ToolPolicyError(RuntimeError):
    """Raised when a tool policy constraint is violated."""


class ToolPolicy:
    """Decorator to enforce per-tool rolling call caps per session."""

    def __init__(self, max_calls: int = 5, window_seconds: int = 15) -> None:
        if max_calls < 1:
            raise ValueError("max_calls must be >= 1")
        if window_seconds < 1:
            raise ValueError("window_seconds must be >= 1")

        self.max_calls = max_calls
        self.window_seconds = window_seconds
        # Keyed by (function name, session key) with a list of timestamps .
        self.calls_by_timed_session: dict[tuple[str, str], list[float]] = {}

    def _get_session_key(self) -> str:
        """Resolve a stable key for the current FastMCP session."""
        try:
            ctx = get_context()
            if ctx.session_id:
                return f"session:{ctx.session_id}"
            return "unknown-session"
        except RuntimeError:
            # Fallback for execution paths without an active FastMCP context.
            return "no-active-context"

    # The __call__ method lets the decorator pass parameters and wrap the target function (fn).
    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            session_key = self._get_session_key()
            counter_key = (fn.__name__, session_key)
            now = time.monotonic()
            rolling_cutoff = now - self.window_seconds

            # Count only recent calls (later than/more recent than the rolling cutoff) by filtering out timestamps outside the rolling window.
            recent_calls = [
                timestamp
                for timestamp in self.calls_by_timed_session.get(counter_key, [])
                if timestamp > rolling_cutoff
            ]

            if len(recent_calls) >= self.max_calls:
                message = (
                    f"Tool call limit reached for '{fn.__name__}' in this session: "
                    f"max {self.max_calls} calls per {self.window_seconds} seconds."
                )
                raise ToolError(message) from ToolPolicyError(message)

            recent_calls.append(now)
            self.calls_by_timed_session[counter_key] = recent_calls
            return fn(*args, **kwargs)

        return wrapper
