"""Tasks-specific instruction block."""

TASKS_CONTEXT = """
TASKS CONTEXT:
Tasks are a core part of Dalux project management. Tasks are discrete work items in our around a construction project,
that can be assigned to users, tracked for progress (changes), and queried for details. They often contain rich 
descriptions, due dates, assignees, and status information that users want to query.

- If user asks about status of task(s), use get_task_changes() because it provides richer status inference.
- Prefer taskSummaries from get_task_changes() when answering status questions.
- Use get_tasks() for list/search workflows and get_task() only when task_id is already known.
- Avoid exposing internal IDs unless the user explicitly asks for them.

"""

# ADD PRESENTATION STYLE:
# - Instruct in how to design overview of tasks...
# design a minimal table for multiple items, If LLM feels the table will be crammed or long, maybe ask user to specify their query or offer to paginate the results for them (maybe 30 at a time?)
# ALWAYS notify the user if you paginated results and ask if they want more results.
# otherwise prioritize these fields for tasks:
# - ...
# - prioritize inferredStatus as central information (not action or status) -- otherwise open or closed
