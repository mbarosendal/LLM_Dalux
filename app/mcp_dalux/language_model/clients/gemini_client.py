from __future__ import annotations

import asyncio
import logging

from google import genai
from google.genai import types

from mcp_dalux.config import Config
from mcp_dalux.language_model.clients.base_client import BaseClient
from mcp_dalux.language_model.contracts import AgentDecision
from mcp_dalux.language_model.decision_service import (
    build_structured_user_prompt,
    parse_agent_decision_output,
)

logger = logging.getLogger(__name__)


class GeminiClient(BaseClient):
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
        user_prompt = build_structured_user_prompt(text=text, tools=tools)

        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        config = types.GenerateContentConfig(
            system_instruction=instructions,
            temperature=0,
            response_mime_type="application/json",
        )

        # Send the prompt with tools and get the response.
        # Gemini's Python SDK does not currently support async, so we run it in a thread to avoid blocking.
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=Config.GEMINI_MODEL,
            contents=user_prompt,
            config=config,
        )

        # Process the raw text output into our internal AgentDecision format.
        return parse_agent_decision_output(
            raw_output=getattr(response, "text", None),
            provider_name=self.model_name,
            logger=logger,
            empty_message="Gemini returned no text.",
        )