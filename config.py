import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    
    DALUX_BASE_URL = os.getenv("DALUX_BASE_URL")
    DALUX_API_KEY = os.getenv("DALUX_API_KEY")
    DALUX_PROJECT_ID = os.getenv("DALUX_PROJECT_ID") # Hardcoded to testproject

    @classmethod
    def validate(cls) -> None:
        if not cls.DALUX_BASE_URL:
            raise ValueError("DALUX_BASE_URL is not set in the environment variables.")
        if not cls.DALUX_API_KEY:
            raise ValueError("DALUX_API_KEY is not set in the environment variables.")
        if not cls.DALUX_PROJECT_ID:
            raise ValueError("DALUX_PROJECT_ID is not set in the environment variables.")
