import httpx
from config import Config

class DaluxAdapter:

    # Constructor retrieves config values, headers, and initializes HTTP client
    def __init__(self):
        self._scoped_project_id = Config.DALUX_SCOPED_PROJECT_ID
        self._use_test_project = Config.IS_TEST_PROJECT_ONLY
        self._base = Config.DALUX_BASE_URL
        self._headers = {
            "x-api-key": Config.DALUX_API_KEY,
            "Content-Type": "application/json"
        }
        self._client = httpx.Client(timeout=15)

    def enforce_project_constraints(self, project_id: str | None = None) -> str:
        """Return effective project id and enforce test-mode constraints."""
        approved_project_id = project_id or self._scoped_project_id
        if self._use_test_project and approved_project_id != self._scoped_project_id:
            raise ValueError("Test mode is enabled; only the configured DALUX_PROJECT_ID is allowed.")
        return approved_project_id

    # Internal helper method for GET requests
    def _get(self, path: str, params: dict | None = None) -> dict | list:
        """Synchronous helper method to perform GET. Raises httpx.HTTPStatusError on non-2xx."""
        url = f"{self._base}{path}"
        response = self._client.get(url, headers=self._headers, params=params)
        response.raise_for_status()
        return response.json()

    def _normalize_collection(self, payload: dict | list, unwrap_key: str | None = None) -> list[dict]:
        """Normalize documented Dalux collections to a list of dict objects."""
        items = payload.get("items", []) if isinstance(payload, dict) else []

        normalized: list[dict] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            value = item.get(unwrap_key, {}) if unwrap_key else item
            if isinstance(value, dict):
                normalized.append(value)
        return normalized

    def _first_or_none(self, payload: dict | list) -> dict | None:
        """Return first item from a documented Dalux collection envelope."""
        items = self._normalize_collection(payload)
        return items[0] if items else None

    # Public methods for GET endpoints related to Tasks
    
    def get_tasks(self, project_id: str | None = None) -> list[dict]:
        """GET /5.1/projects/{projectId}/tasks"""
        project_id = self.enforce_project_constraints(project_id)
        payload = self._get(f"/5.1/projects/{project_id}/tasks")
        return self._normalize_collection(payload, unwrap_key="data")
    
    # Single resource endpoint returns as dict, not list
    def get_task(self, task_id: str, project_id: str | None = None) -> dict | None:
        """GET /3.3/projects/{projectId}/tasks/{taskId}"""
        project_id = self.enforce_project_constraints(project_id)
        payload = self._get(f"/3.3/projects/{project_id}/tasks/{task_id}")
        return self._first_or_none(payload)

    def get_task_attachments(self, project_id: str | None = None) -> list[dict]:
        """GET /1.1/projects/{projectId}/tasks/attachments"""
        project_id = self.enforce_project_constraints(project_id)
        payload = self._get(f"/1.1/projects/{project_id}/tasks/attachments")
        return self._normalize_collection(payload)

    def get_task_changes(self, project_id: str | None = None) -> list[dict]:
        """GET /2.2/projects/{projectId}/tasks/changes"""
        project_id = self.enforce_project_constraints(project_id)
        payload = self._get(f"/2.2/projects/{project_id}/tasks/changes")
        return self._normalize_collection(payload)






