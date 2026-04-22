from __future__ import annotations

import asyncio
import logging

from anthropic import AsyncAnthropic

from mcp_dalux.config import Config
from mcp_dalux.language_model.clients.base_client import BaseClient
from mcp_dalux.language_model.contracts import AgentDecision
from mcp_dalux.language_model.decision_service import (
    build_structured_user_prompt,
    parse_agent_decision_output,
)

logger = logging.getLogger(__name__)


class ClaudeClient(BaseClient):
    @property
    def model_name(self) -> str:
        return "Claude"

    @property
    def version(self) -> str:
        return Config.CLAUDE_MODEL

    async def generate_decision(
        self,
        text: str,
        instructions: str,
        tools: list[str] | None = None,
    ) -> AgentDecision:
        user_prompt = build_structured_user_prompt(text=text, tools=tools)

        client = AsyncAnthropic(api_key=Config.CLAUDE_API_KEY or "")

        # Send the prompt with tools and get the response.
        try:
            response = await asyncio.wait_for(
                client.messages.create(
                    model=Config.CLAUDE_MODEL,
                    max_tokens=200,
                    temperature=0,
                    system=instructions,
                    messages=[
                        {
                            "role": "user",
                            "content": user_prompt,
                        }
                    ],
                ),
                timeout=20.0,
            )
        except Exception:
            logger.exception("Claude SDK request failed")
            raise
        
        raw_output = "\n".join(
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text" and getattr(block, "text", None)
        )

        # Process the raw text output into our internal AgentDecision format.
        return parse_agent_decision_output(
            raw_output=raw_output,
            provider_name=self.model_name,
            logger=logger,
            empty_message="Claude returned no text.",
        )
