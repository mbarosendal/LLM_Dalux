import os

import pytest

from adapters.dalux_adapter import DaluxAdapter

pytestmark = pytest.mark.integration

def test_live_get_tasks_smoke():
    adapter = DaluxAdapter()
    try:
        result = adapter.get_tasks()
    finally:
        adapter._client.close()

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
