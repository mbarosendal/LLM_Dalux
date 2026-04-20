from __future__ import annotations

# This module should own session lifecycle logic.
#
# Suggested responsibilities:
# - create_session(project_name, category)
# - get_session(session_id)
# - (optional) delete_session(session_id)
# - validate an active session exists before prompt handling
#
# Start with an in-memory store. Only (optionally) add persistence after the HTTP flow is stable.
