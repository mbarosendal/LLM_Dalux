"""Tasks-specific instruction block."""

TASKS_CONTEXT = """
TASKS CONTEXT:
Tasks are a core part of Dalux project management. Tasks are discrete work items in our around a construction project,
that can be assigned to users, tracked for progress (changes), and queried for details. They often contain rich 
descriptions, due dates, assignees, and status information that users want to query.

TASK-RELATED TOOLS:
- get_task - Use this when a task_id is already known and user wants detailed info about that specific task.
- get_tasks - Use this for to get an overview of many tasks
- get_task_changes - Use this if user asks about the status of task(s), because it provides enriched status inference (taskSummaries) 
"""
