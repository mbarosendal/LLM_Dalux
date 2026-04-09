import os

import pytest

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter

pytestmark = pytest.mark.integration

def test_live_get_tasks_smoke():
    adapter = DaluxAdapter()
    try:
        result = adapter.get_tasks()
        items = result.get("items", []) if isinstance(result, dict) else []
        if not items:
            pytest.skip("No tasks found in the project; cannot verify get_tasks response shape.")
    finally:
        adapter._client.close()
    
    assert isinstance(result, dict)
    assert "items" in result
    assert isinstance(items, list)
    if items:
        assert isinstance(result["items"][0], dict)

# Test getting a task by ID, using the first task from get_tasks as a reference
def test_live_get_task_smoke():
    adapter = DaluxAdapter()
    try:
        result = adapter.get_tasks()
        tasks = result.get("items", []) if isinstance(result, dict) else []
        if not tasks:
            pytest.skip("No tasks found in the project; cannot test get_task endpoint.")
        task_id = tasks[0].get("taskId")
        if not task_id:
            pytest.skip("First task does not have a taskId; cannot test get_task endpoint.")
        result = adapter.get_task(task_id)
    finally:
        adapter._client.close()

    assert isinstance(result, dict)
    assert result.get("taskId") == task_id


def test_live_get_task_changes_smoke():
    adapter = DaluxAdapter()
    try:
        result = adapter.get_task_changes()
        items = result.get("items", []) if isinstance(result, dict) else []
        if not items:
            pytest.skip("No task changes found in the project; cannot verify get_task_changes response shape.")
    finally:
        adapter._client.close()

    assert isinstance(result, dict)
    assert "items" in result
    assert isinstance(items, list)
    if items:
        assert isinstance(result["items"][0], dict)


# def test_live_get_task_attachments_smoke():
#     adapter = DaluxAdapter()
#     try:
#         result = adapter.get_task_attachments()
#     finally:
#         adapter._client.close()

#     assert isinstance(result, dict)
    

