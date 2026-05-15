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

    # App mode determines whether to start the web API or the MCP server.
    APP_MODE = os.getenv("APP_MODE", "mcp").lower()
    MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http").lower()
    # Only relevant for MCP mode with HTTP transport (not stdio)
    MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT = int(os.getenv("MCP_PORT", os.getenv("PORT", "8000")))
    MCP_API_TOKEN = os.getenv("MCP_API_TOKEN")
    MCP_HTTP_PATH = os.getenv("MCP_HTTP_PATH", "/mcp")
    # Supported modes: none, bearer, url-token
    MCP_AUTH_MODE = os.getenv("MCP_AUTH_MODE", "url-token").lower()

    # HTTP server config (for web API mode).
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8001"))
    API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")
    TRUSTED_HOSTS = [host.strip() for host in os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1,[::1]").split(",") if host.strip()]
    CORS_ALLOW_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if origin.strip()]

    # Limit of agent rounds (one full cycle of tool usage) to prevent infinite loops.
    MAX_AGENT_ROUNDS = 3
    # Agent selection: "claude", "gemini", "ollama", "openrouter"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

    # Claude runtime config.
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-6").lower()

    # Gemini runtime config
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").lower()
    # Fallback models to try if the primary model fails (comma-separated)
    GEMINI_FALLBACK_MODELS = [m.strip().lower() for m in os.getenv("GEMINI_FALLBACK_MODELS", "gemini-2.5-flash-lite,gemini-2.5-pro").split(",")]

    # Ollama runtime config.
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "")
    OLLAMA_FALLBACK_MODELS = [m.strip() for m in os.getenv("OLLAMA_FALLBACK_MODELS", "").split(",") if m.strip()]

    # OpenRouter runtime config.
    OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "").strip()
    OPENROUTER_FALLBACK_MODELS = [m.strip() for m in os.getenv("OPENROUTER_FALLBACK_MODELS", "").split(",") if m.strip()]
    OPENROUTER_HTTP_REFERER = os.getenv("OPENROUTER_HTTP_REFERER", "").strip()
    OPENROUTER_APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "").strip()

    @classmethod
    def validate(cls) -> None:
        if cls.APP_MODE not in {"web_api", "mcp"}:
            raise ValueError("APP_MODE must be either 'web_api' or 'mcp'.")
        if cls.APP_MODE == "mcp" and cls.MCP_TRANSPORT not in {"stdio", "http", "sse", "streamable-http"}:
            raise ValueError("MCP_TRANSPORT must be either 'stdio', 'http', 'sse', or 'streamable-http'.")
        if cls.APP_MODE == "mcp" and cls.MCP_AUTH_MODE not in {"none", "bearer", "url-token"}:
            raise ValueError("MCP_AUTH_MODE must be one of: 'none', 'bearer', 'url-token'.")
        if cls.APP_MODE == "mcp" and not cls.MCP_HTTP_PATH.startswith("/"):
            raise ValueError("MCP_HTTP_PATH must start with '/'.")
        if cls.APP_MODE == "mcp" and not (1 <= cls.MCP_PORT <= 65535):
            raise ValueError("MCP_PORT must be a valid TCP port between 1 and 65535.")
        if cls.APP_MODE == "web_api" and not cls.API_AUTH_TOKEN:
            raise ValueError("API_AUTH_TOKEN is required when APP_MODE is 'web_api'.")
        if not cls.TRUSTED_HOSTS:
            raise ValueError("TRUSTED_HOSTS must include at least one host.")
        if not cls.DALUX_BASE_URL:
            raise ValueError("DALUX_BASE_URL is not set in the environment variables.")
        if not cls.DALUX_API_KEY:
            raise ValueError("DALUX_API_KEY is not set in the environment variables.")
        if not cls.DALUX_SCOPED_PROJECT_ID:
            raise ValueError("DALUX_PROJECT_ID is not set in the environment variables.")
        # if not cls.DALUX_USER_ID:
        #     raise ValueError("DALUX_USER_ID is not set in the environment variables.")
        if cls.APP_MODE == "web_api":
            if cls.LLM_PROVIDER not in {"claude", "gemini", "mock", "ollama", "openrouter"}:
                raise ValueError("LLM_PROVIDER must be set to 'claude', 'gemini', 'mock', 'ollama', or 'openrouter'.")
            if cls.LLM_PROVIDER == "claude" and not cls.CLAUDE_API_KEY:
                raise ValueError("CLAUDE_API_KEY is required when LLM_PROVIDER is 'claude'.")
            if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER is 'gemini'.")
            if cls.LLM_PROVIDER == "openrouter" and not cls.OPEN_ROUTER_KEY:
                raise ValueError("OPEN_ROUTER_KEY is required when LLM_PROVIDER is 'openrouter'.")
