from __future__ import annotations

import asyncio
import logging
import os

from google import genai
from google.genai import types

from mcp_dalux.config import Config
from mcp_dalux.llm.clients.base_client import BaseClient
from mcp_dalux.llm.contracts import AgentDecision, LLMError
from mcp_dalux.llm.services.decision_service import (
    build_structured_user_input,
    parse_agent_decision_output,
)

logger = logging.getLogger(__name__)


class GeminiClient(BaseClient):
    _AUTO_PRIORITY_MODELS = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    def _normalize_model_name(self, model_name: object) -> str | None:
        if not isinstance(model_name, str) or not model_name:
            return None
        return model_name.removeprefix("models/").strip().lower()

    def _list_available_text_models(self, client: genai.Client) -> list[str]:
        available_models: list[str] = []
        try:
            for model in client.models.list():
                name = self._normalize_model_name(getattr(model, "name", None))
                supported_methods = getattr(model, "supported_generation_methods", None) or []
                if name and "generateContent" in supported_methods:
                    available_models.append(name)
        except Exception as exc:
            logger.warning(f"Could not list Gemini models; using configured order only: {exc}")
        return available_models

    def _build_model_candidates(self) -> list[str]:
        env_primary = os.getenv("GEMINI_MODEL")
        env_fallbacks = os.getenv("GEMINI_FALLBACK_MODELS")

        if env_primary or env_fallbacks:
            candidates = [Config.GEMINI_MODEL] + Config.GEMINI_FALLBACK_MODELS
        else:
            candidates = self._AUTO_PRIORITY_MODELS

        seen: set[str] = set()
        ordered_candidates: list[str] = []
        for model in candidates:
            normalized = model.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered_candidates.append(normalized)
        return ordered_candidates

    @property
    def model_name(self) -> str:
        return "Gemini"

    @property
    def version(self) -> str:
        return Config.GEMINI_MODEL

    async def generate_decision(
        self,
        text: str,
        instructions: str,
        tools: list[str] | None = None,
    ) -> AgentDecision:
        user_prompt = build_structured_user_input(text=text, tools=tools)
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        config = types.GenerateContentConfig(
            system_instruction=instructions,
            temperature=0,
            response_mime_type="application/json",
        )

        # Prefer models that the API actually reports as available.
        configured_models = self._build_model_candidates()
        available_models = self._list_available_text_models(client)
        models_to_try = [model for model in configured_models if model in available_models] or configured_models
        last_error = None

        for model in models_to_try:
            try:
                logger.info(f"Attempting to generate decision with model: {model}")
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=model,
                        contents=user_prompt,
                        config=config,
                    ),
                    timeout=20.0,
                )
                logger.info(f"Successfully generated decision with model: {model}")
                # Process the text output into our internal AgentDecision format.
                return parse_agent_decision_output(
                    raw_output=getattr(response, "text", None),
                    provider_name=self.model_name,
                    logger=logger,
                    empty_message="Gemini returned no text.",
                )
            except asyncio.TimeoutError as exc:
                last_error = exc
                logger.warning(f"Model {model} timed out; trying next fallback.")
            except Exception as exc:
                last_error = exc
                logger.warning(f"Model {model} failed: {exc}; trying next fallback.")

        # All models failed.
        logger.exception(f"All Gemini models failed. Last error: {last_error}")
        raise LLMError(f"All Gemini models failed: {last_error}") from last_error

    async def check_health(self) -> bool:
        """Check Gemini client health by making a lightweight API call to list available models."""
        try:
            if not Config.GEMINI_API_KEY:
                logger.warning("Gemini health check failed: GEMINI_API_KEY not set")
                return False

            client = genai.Client(api_key=Config.GEMINI_API_KEY)
            # List available models as a lightweight health check.
            await asyncio.to_thread(
                client.models.list,
            )
            logger.info("Gemini health check passed")
            return True
        except Exception as exc:
            logger.warning(f"Gemini health check failed: {exc}")
            return False
