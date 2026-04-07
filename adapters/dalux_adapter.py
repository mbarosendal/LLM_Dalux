import httpx
from config import Config

class DaluxAdapter:

    def __init__(self):
        self._base = Config.DALUX_BASE_URL
        self._headers = {
            "x-api-key": Config.DALUX_API_KEY,
            "Content-Type": "application/json"
        }
        self._client = httpx.Client(timeout=15)

    # internal helper method for GET requests
    def _get(self, path: str, params: dict | None = None) -> dict | list:
        """Synchronous helper method to perform GET. Raises httpx.HTTPStatusError on non-2xx."""
        url = f"{self._base}{path}"
        with httpx.Client(timeout=15) as client:
            response = client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()

    def get_tasks(self, project_id: str) -> list:
        """GET /5.1/projects/{projectId}/tasks"""
        return self._get(f"/5.1/projects/{project_id}/tasks")    
    
    # Single resource endpoint returns as dict, not list
    def get_task(self, project_id: str, task_id: str) -> dict:
        """GET /3.3/projects/{projectId}/tasks/{taskId}"""
        return self._get(f"/3.3/projects/{project_id}/tasks/{task_id}")

    def get_task_attachments(self, project_id: str) -> list:
        """GET /1.1/projects/{projectId}/tasks/attachments"""
        return self._get(f"/1.1/projects/{project_id}/tasks/attachments")

    def get_task_changes(self, project_id: str) -> list:
        """GET /2.2/projects/{projectId}/tasks/changes"""
        return self._get(f"/2.2/projects/{project_id}/tasks/changes") 






