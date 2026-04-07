import httpx
from config import Config

class DaluxAdapter:

    def __init__(self):
        self.base = Config.DALUX_BASE_URL
        self.headers = {
            "x-api-key": Config.DALUX_API_KEY,
            "Content-Type": "application/json"
        }
        self._client = httpx.Client(timeout=15)


    def get_tasks(self, project_id: str) -> list:
        url = f"{self.base}/5.1/projects/{project_id}/tasks"

        response = self._client.get(
            url,
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()


    # def get_task
    # def get_task_attachment
    # def get_tash_changes


