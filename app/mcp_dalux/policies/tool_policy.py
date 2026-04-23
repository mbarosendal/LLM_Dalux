import time
from functools import wraps
from typing import Any, Callable

from fastmcp.exceptions import ToolError


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
        # Keyed by (function name, session key) with a list of timestamps (floats to represent seconds).
        self.calls_by_timed_session: dict[tuple[str, str], list[float]] = {}

    def _get_scope_key(self, kwargs: dict[str, Any]) -> str:
        """Resolve the transport-agnostic limiter scope key from call kwargs."""
        scope_key = kwargs.get("scope_key")
        if isinstance(scope_key, str) and scope_key:
            return scope_key

        message = "Tool policy scope key is required. Pass scope_key from the transport layer."
        raise ToolError(message) from ToolPolicyError(message)

    # The __call__ method lets the decorator pass parameters and wrap the target function (fn).
    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Enforce the rolling call window before executing the tool function by tracking  ."""
            scope_key = self._get_scope_key(kwargs)
            counter_key = (fn.__name__, scope_key)
            # Returns a float number of seconds passed since a shared and fixed arbitrary point  (e.g. system start).
            now = time.monotonic()
            rolling_cutoff = now - self.window_seconds

            # Filter out calls that took place before the rolling cutoff (call_time is a float tracking call age in seconds).
            recent_calls = [
                call_time for call_time in self.calls_by_timed_session.get(counter_key, []) if call_time > rolling_cutoff
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
