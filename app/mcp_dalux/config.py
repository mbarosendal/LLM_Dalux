import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Config:
    IS_TEST_PROJECT_ONLY = True
    DALUX_SCOPED_PROJECT_ID = os.getenv("DALUX_PROJECT_ID")

    DALUX_BASE_URL = os.getenv("DALUX_BASE_URL")
    DALUX_API_KEY = os.getenv("DALUX_API_KEY")

    # Optional user context for personal queries.
    DALUX_USER_ID = os.getenv("DALUX_USER_ID")

    # Transport mode: 'stdio' for local, 'http' for API server.
    MCP_TRANSPORT = "stdio"
    # See client_factory.py for options
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

    # Limit of agent rounds (one full cycle of tool usage) to prevent infinite loops.
    MAX_AGENT_ROUNDS = 2

    # Claude runtime config.
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-6")

    # Gemini runtime config (to be added when Gemini client is wired up)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

    @classmethod
    def validate(cls) -> None:
        if cls.MCP_TRANSPORT not in {"stdio", "http"}:
            raise ValueError("MCP_TRANSPORT must be either 'stdio' or 'http'.")
        if cls.LLM_PROVIDER not in {"claude", "mock", "gemini"}:
            raise ValueError("LLM_PROVIDER must be one of: claude, mock, gemini.")
        if not cls.DALUX_BASE_URL:
            raise ValueError("DALUX_BASE_URL is not set in the environment variables.")
        if not cls.DALUX_API_KEY:
            raise ValueError("DALUX_API_KEY is not set in the environment variables.")
        if not cls.DALUX_SCOPED_PROJECT_ID:
            raise ValueError("DALUX_PROJECT_ID is not set in the environment variables.")
        if not cls.DALUX_USER_ID:
            raise ValueError("DALUX_USER_ID is not set in the environment variables.")
        if cls.LLM_PROVIDER == "claude" and not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY is required when LLM_PROVIDER is 'claude'.")
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER is 'gemini'.")
