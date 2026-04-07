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
        return self._get(f"/5.1/projects/{project_id}/tasks")    

    # def get_task
    # def get_task_attachment
    # def get_tash_changes




