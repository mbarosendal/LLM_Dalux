import httpx
import pytest
import respx

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.config import Config

# 1) Config values are "monkeypatched" (temporarily overrides Python objects/attributes) so the adapter always uses predictable test settings
@pytest.fixture
def adapter(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Config, "DALUX_SCOPED_PROJECT_ID", "project-123")
    monkeypatch.setattr(Config, "IS_TEST_PROJECT_ONLY", True)
    monkeypatch.setattr(Config, "DALUX_BASE_URL", "https://dalux.example")
    monkeypatch.setattr(Config, "DALUX_API_KEY", "fake-key")

    instance = DaluxAdapter()
    yield instance
    instance._client.close()

# 2) Mock the exact endpoint call the adapter makes and return a realistic response envelope
@respx.mock
def test_get_tasks_returns_normalized_items(adapter: DaluxAdapter):
    # route is a RESPX route object (a library object from RESPX with tracking info) returned by the respx.get() method
    route = respx.get("https://dalux.example/5.1/projects/project-123/tasks").mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [
                    {"data": {"id": "t-1", "title": "First task"}},
                    {"data": {"id": "t-2", "title": "Second task"}},
                ]
            },
        )
    )

    # 3) Execute the method under test
    result = adapter.get_tasks()

    # Verifies the adapter actually made the expected HTTP call
    assert route.called
    # Verifies normalization returned the expected number of items
    assert len(result) == 2
    # Verifies the returned shape/content, not just that something came back
    assert result[0]["id"] == "t-1"
    assert result[1]["title"] == "Second task"
