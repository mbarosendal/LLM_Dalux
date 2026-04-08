import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
<<<<<<< HEAD:config.py
    # Switch to enforce project constraints
    # USE_TEST_MODE = True
    IS_TEST_PROJECT_ONLY = True
    DALUX_SCOPED_PROJECT_ID = os.getenv("DALUX_PROJECT_ID")
=======
    # Switches to enforce project constraints 
    # TEST_MODE_ON = True
    USE_TEST_PROJECT_ONLY = True
    DALUX_PROJECT_ID = os.getenv("DALUX_PROJECT_ID")
>>>>>>> ca56b6ee0ce032f78858d3779f0638cd48aa3a2e:app/config.py

    DALUX_BASE_URL = os.getenv("DALUX_BASE_URL")
    DALUX_API_KEY = os.getenv("DALUX_API_KEY")

    @classmethod
    def validate(cls) -> None:
        if not cls.DALUX_BASE_URL:
            raise ValueError("DALUX_BASE_URL is not set in the environment variables.")
        if not cls.DALUX_API_KEY:
            raise ValueError("DALUX_API_KEY is not set in the environment variables.")
        if not cls.DALUX_SCOPED_PROJECT_ID:
            raise ValueError("DALUX_PROJECT_ID is not set in the environment variables.")
