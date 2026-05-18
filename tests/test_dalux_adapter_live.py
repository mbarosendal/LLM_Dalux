import pytest
from mcp_dalux.adapters.dalux_adapter import DaluxAdapter

pytestmark = pytest.mark.integration

# Command to run tests: uv run pytest -vv -s -rA


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


def test_live_get_users_smoke():
    adapter = DaluxAdapter()
    try:
        result = adapter.get_users()
        items = result.get("items", []) if isinstance(result, dict) else []
        if not items:
            pytest.skip("No users found in project; cannot verify get_users response shape.")
    finally:
        adapter._client.close()

    assert isinstance(result, dict)
    assert "items" in result
    assert isinstance(items, list)
    if items:
        assert isinstance(result["items"][0], dict)


def test_live_get_user_smoke():
    adapter = DaluxAdapter()
    try:
        result = adapter.get_users()
        users = result.get("items", []) if isinstance(result, dict) else []
        if not users:
            pytest.skip("No users found in the project; cannot test get_user endpoint.")
        user_id = users[0].get("userId")
        if not user_id:
            pytest.skip("First user does not have a userId; cannot test get_user endpoint.")
        result = adapter.get_user(user_id)
    finally:
        adapter._client.close()

    assert isinstance(result, dict)
    assert result.get("userId") == user_id


def test_live_get_workpackages_smoke():
    adapter = DaluxAdapter()
    try:
        result = adapter.get_workpackages()
        items = result.get("items", []) if isinstance(result, dict) else []
        if not items:
            pytest.skip("No workpackages found in the project; cannot verify get_workpackages response shape.")
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
