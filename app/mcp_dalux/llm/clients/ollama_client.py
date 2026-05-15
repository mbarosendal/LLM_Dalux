from __future__ import annotations

import asyncio
import logging

import httpx

from mcp_dalux.config import Config
from mcp_dalux.llm.clients.base_client import BaseClient
from mcp_dalux.llm.contracts import AgentDecision, LLMError
from mcp_dalux.llm.services.decision_service import build_structured_user_input, parse_agent_decision_output

logger = logging.getLogger(__name__)


class OllamaClient(BaseClient):
    _DEFAULT_PRIORITY_MODELS = ["qwen2.5", "llama3.1", "llama3.2", "gemma3", "phi4"]

    def __init__(self) -> None:
        self._last_model: str | None = None

    @property
    def model_name(self) -> str:
        return "Ollama"

    @property
    def version(self) -> str:
        return self._last_model or Config.OLLAMA_MODEL or "auto"

    def _normalize_model_name(self, model_name: object) -> str | None:
        if not isinstance(model_name, str) or not model_name.strip():
            return None
        return model_name.strip().lower()

    def _build_model_candidates(self, available_models: list[str]) -> list[str]:
        explicit_models = [Config.OLLAMA_MODEL, *Config.OLLAMA_FALLBACK_MODELS]
        if Config.OLLAMA_MODEL or Config.OLLAMA_FALLBACK_MODELS:
            candidates = [model.strip().lower() for model in explicit_models if model.strip()]
        else:
            normalized_available = [model for model in available_models if model]
            prioritized: list[str] = []
            for needle in self._DEFAULT_PRIORITY_MODELS:
                prioritized.extend([model for model in normalized_available if needle in model and model not in prioritized])
            candidates = prioritized or normalized_available

        seen: set[str] = set()
        ordered_candidates: list[str] = []
        for model in candidates:
            if model not in seen:
                seen.add(model)
                ordered_candidates.append(model)
        return ordered_candidates

    async def _list_available_models(self) -> list[str]:
        async with httpx.AsyncClient(base_url=Config.OLLAMA_BASE_URL, timeout=10.0) as client:
            response = await client.get("/api/tags")
            response.raise_for_status()
            payload = response.json()

        models = payload.get("models", []) if isinstance(payload, dict) else []
        available_models: list[str] = []
        for item in models:
            if not isinstance(item, dict):
                continue
            name = self._normalize_model_name(item.get("name"))
            if name:
                available_models.append(name)
        return available_models

    async def generate_decision(self, text: str, instructions: str, tools: list[str] | None = None) -> AgentDecision:
        user_prompt = build_structured_user_input(text=text, tools=tools)

        try:
            available_models = await self._list_available_models()
            models_to_try = self._build_model_candidates(available_models)
            if not models_to_try:
                raise LLMError("No Ollama models are available. Pull one with `ollama pull <model>`.")

            last_error: Exception | None = None
            async with httpx.AsyncClient(base_url=Config.OLLAMA_BASE_URL, timeout=20.0) as client:
                for model in models_to_try:
                    try:
                        logger.info("Attempting Ollama decision with model: %s", model)
                        response = await asyncio.wait_for(
                            client.post(
                                "/api/chat",
                                json={
                                    "model": model,
                                    "messages": [
                                        {"role": "system", "content": instructions},
                                        {"role": "user", "content": user_prompt},
                                    ],
                                    "stream": False,
                                    "format": "json",
                                    "options": {"temperature": 0},
                                },
                            ),
                            timeout=20.0,
                        )
                        response.raise_for_status()
                        payload = response.json()
                        raw_output = None
                        if isinstance(payload, dict):
                            message = payload.get("message") or {}
                            if isinstance(message, dict):
                                raw_output = message.get("content")

                        self._last_model = model
                        return parse_agent_decision_output(
                            raw_output=raw_output,
                            provider_name=self.model_name,
                            logger=logger,
                            empty_message="Ollama returned no text.",
                        )
                    except asyncio.TimeoutError as exc:
                        last_error = exc
                        logger.warning("Ollama model %s timed out; trying next fallback.", model)
                    except Exception as exc:
                        last_error = exc
                        logger.warning("Ollama model %s failed: %s; trying next fallback.", model, exc)

            raise LLMError(f"All Ollama models failed: {last_error}") from last_error
        except Exception as exc:
            if isinstance(exc, LLMError):
                raise
            logger.exception("Ollama request failed")
            raise LLMError(f"Ollama request failed: {exc}") from exc

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(base_url=Config.OLLAMA_BASE_URL, timeout=10.0) as client:
                response = await client.get("/api/tags")
                response.raise_for_status()
            logger.info("Ollama health check passed")
            return True
        except Exception as exc:
            logger.warning("Ollama health check failed: %s", exc)
            return False