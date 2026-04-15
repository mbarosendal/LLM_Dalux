"""User-specific instruction template."""

USER_CONTEXT_TEMPLATE = """
USER CONTEXT:
- The current user ("me", "my", "mine", etc.) maps to DALUX userId: {actor_user_id}
- For personal queries (for example "my tasks"), first call get_current_user_context first to anchor the actor userId, and include the user's name in your response.
- If no user information is available to you here or after calling get_current_user_context, you may ask user for their name and use it to look up their information via get_users.

USERS-RELATED TOOLS:
- get_current_user_context
- get_users
- get_user
"""
