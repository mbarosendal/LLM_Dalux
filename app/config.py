import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve .env from project root so server startup does not depend on cwd.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

class Config:
    # Switches to enforce project constraints 
    # TEST_MODE_ON = True
    IS_TEST_PROJECT_ONLY = True
    DALUX_PROJECT_ID = os.getenv("DALUX_PROJECT_ID")

    DALUX_BASE_URL = os.getenv("DALUX_BASE_URL")
    DALUX_API_KEY = os.getenv("DALUX_API_KEY")

    @classmethod
    def validate(cls) -> None:
        if not cls.DALUX_BASE_URL:
            raise ValueError("DALUX_BASE_URL is not set in the environment variables.")
        if not cls.DALUX_API_KEY:
            raise ValueError("DALUX_API_KEY is not set in the environment variables.")
        if not cls.DALUX_PROJECT_ID:
            raise ValueError("DALUX_PROJECT_ID is not set in the environment variables.")
