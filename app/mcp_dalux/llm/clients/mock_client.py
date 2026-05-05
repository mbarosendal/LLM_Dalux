from __future__ import annotations

from mcp_dalux.llm.clients.base_client import BaseClient
from mcp_dalux.llm.contracts import AgentDecision, ToolRequest


class MockClient(BaseClient):
    @property
    def model_name(self) -> str:
        return "Mock"

    @property
    def version(self) -> str:
        return "1.0"

    async def generate_decision(
        self,
        text: str,
        instructions: str,
        tools: list[str] | None = None,
    ) -> AgentDecision:
        normalized_text = text.lower().strip()

        if "tool results:" in normalized_text:
            return AgentDecision(
                mode="answer",
                response="Final answer based on dispatched tool results.",
                raw_output="mock-final-answer",
            )

        available_tools = tools or []
        if available_tools and any(keyword in normalized_text for keyword in ("tool", "lookup", "find")):
            return AgentDecision(
                mode="tools",
                response="I need to use a tool before answering.",
                tool_requests=[
                    ToolRequest(
                        tool_name=available_tools[0],
                        arguments={"prompt": text, "instructions": instructions},
                    )
                ],
                raw_output="mock-tool-request",
            )

        return AgentDecision(
            mode="answer",
            response=f"Mock answer: {text}",
            raw_output="mock-answer",
        )

    async def check_health(self) -> bool:
        """Mock client is always healthy."""
        return True
