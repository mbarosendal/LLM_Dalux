from __future__ import annotations

# This module should own prompt processing and the agent loop.
#
# Flow:
# - validate and sanitize incoming prompt text
# - load active session state
# - build runtime instructions
# - call the LLM interface
# - decide whether to call tools
# - return structured response data
#
# Keep the route layer out of this logic so it stays testable.
