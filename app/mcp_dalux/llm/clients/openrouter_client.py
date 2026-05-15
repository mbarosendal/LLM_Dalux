from __future__ import annotations

import asyncio
import logging

import httpx

from mcp_dalux.config import Config
from mcp_dalux.llm.clients.base_client import BaseClient
from mcp_dalux.llm.contracts import AgentDecision, LLMError
from mcp_dalux.llm.services.decision_service import build_structured_user_input, parse_agent_decision_output

logger = logging.getLogger(__name__)


class OpenRouterClient(BaseClient):
    _DEFAULT_PRIORITY_MODELS = [
        "openai/gpt-4o-mini",
        "google/gemini-2.5-flash",
        "anthropic/claude-3.5-sonnet",
        "qwen/qwen3-32b",
        "meta-llama/llama-3.3-70b-instruct",
    ]

    def __init__(self) -> None:
        self._last_model: str | None = None

    @property
    def model_name(self) -> str:
        return "OpenRouter"

    @property
    def version(self) -> str:
        return self._last_model or Config.OPENROUTER_MODEL or "auto"

    def _headers(self) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {Config.OPEN_ROUTER_KEY or ""}"}
        if Config.OPENROUTER_HTTP_REFERER:
            headers["HTTP-Referer"] = Config.OPENROUTER_HTTP_REFERER
        if Config.OPENROUTER_APP_TITLE:
            headers["X-Title"] = Config.OPENROUTER_APP_TITLE
        return headers

    def _normalize_model_name(self, model_name: object) -> str | None:
        if not isinstance(model_name, str) or not model_name.strip():
            return None
        return model_name.strip()

    def _extract_available_models(self, payload: object) -> list[str]:
        models_payload: list[object] = []
        if isinstance(payload, dict):
            if isinstance(payload.get("data"), list):
                models_payload = payload["data"]
            elif isinstance(payload.get("models"), list):
                models_payload = payload["models"]

        available_models: list[str] = []
        for item in models_payload:
            if not isinstance(item, dict):
                continue
            name = self._normalize_model_name(item.get("id") or item.get("name"))
            if name:
                available_models.append(name)
        return available_models

    def _build_model_candidates(self, available_models: list[str]) -> list[str]:
        explicit_models = [Config.OPENROUTER_MODEL, *Config.OPENROUTER_FALLBACK_MODELS]
        if Config.OPENROUTER_MODEL or Config.OPENROUTER_FALLBACK_MODELS:
            candidates = [model.strip() for model in explicit_models if model.strip()]
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
        async with httpx.AsyncClient(base_url=Config.OPENROUTER_BASE_URL, timeout=10.0, headers=self._headers()) as client:
            response = await client.get("/models")
            response.raise_for_status()
            payload = response.json()
        return self._extract_available_models(payload)

    def _extract_message_content(self, payload: object) -> str | None:
        if not isinstance(payload, dict):
            return None

        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return None

        message = first_choice.get("message")
        if not isinstance(message, dict):
            return None

        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            return "".join(parts) if parts else None
        return None

    async def generate_decision(self, text: str, instructions: str, tools: list[str] | None = None) -> AgentDecision:
        user_prompt = build_structured_user_input(text=text, tools=tools)

        try:
            available_models = await self._list_available_models()
            models_to_try = self._build_model_candidates(available_models)
            if not models_to_try:
                raise LLMError("No OpenRouter models are available. Set OPENROUTER_MODEL or ensure the key can list models.")

            last_error: Exception | None = None
            async with httpx.AsyncClient(base_url=Config.OPENROUTER_BASE_URL, timeout=20.0, headers=self._headers()) as client:
                for model in models_to_try:
                    try:
                        logger.info("Attempting OpenRouter decision with model: %s", model)
                        response = await asyncio.wait_for(
                            client.post(
                                "/chat/completions",
                                json={
                                    "model": model,
                                    "messages": [
                                        {"role": "system", "content": instructions},
                                        {"role": "user", "content": user_prompt},
                                    ],
                                    "stream": False,
                                    "temperature": 0,
                                    "max_tokens": 200,
                                },
                            ),
                            timeout=20.0,
                        )
                        response.raise_for_status()
                        payload = response.json()
                        raw_output = self._extract_message_content(payload)

                        self._last_model = model
                        return parse_agent_decision_output(
                            raw_output=raw_output,
                            provider_name=self.model_name,
                            logger=logger,
                            empty_message="OpenRouter returned no text.",
                        )
                    except asyncio.TimeoutError as exc:
                        last_error = exc
                        logger.warning("OpenRouter model %s timed out; trying next fallback.", model)
                    except Exception as exc:
                        last_error = exc
                        logger.warning("OpenRouter model %s failed: %s; trying next fallback.", model, exc)

            raise LLMError(f"All OpenRouter models failed: {last_error}") from last_error
        except Exception as exc:
            if isinstance(exc, LLMError):
                raise
            logger.exception("OpenRouter request failed")
            raise LLMError(f"OpenRouter request failed: {exc}") from exc

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(base_url=Config.OPENROUTER_BASE_URL, timeout=10.0, headers=self._headers()) as client:
                response = await client.get("/models")
                response.raise_for_status()
            logger.info("OpenRouter health check passed")
            return True
        except Exception as exc:
            logger.warning("OpenRouter health check failed: %s", exc)
            return False