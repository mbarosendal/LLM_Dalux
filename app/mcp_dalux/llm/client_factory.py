from __future__ import annotations

from mcp_dalux.config import Config
from mcp_dalux.llm.clients.base_client import BaseClient
from mcp_dalux.llm.clients.claude_client import ClaudeClient
from mcp_dalux.llm.clients.gemini_client import GeminiClient
from mcp_dalux.llm.clients.openrouter_client import OpenRouterClient
from mcp_dalux.llm.clients.ollama_client import OllamaClient
from mcp_dalux.llm.clients.mock_client import MockClient


def get_llm_client() -> BaseClient:
    """Return the configured language-model client."""
    if Config.LLM_PROVIDER == "claude":
        return ClaudeClient()
    if Config.LLM_PROVIDER == "gemini":
        return GeminiClient()
    if Config.LLM_PROVIDER == "openrouter":
        return OpenRouterClient()
    if Config.LLM_PROVIDER == "ollama":
        return OllamaClient()
    if Config.LLM_PROVIDER == "mock":
        return MockClient()

    raise ValueError(f"Unsupported LLM_PROVIDER: {Config.LLM_PROVIDER}")
