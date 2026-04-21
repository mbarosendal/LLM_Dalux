from mcp_dalux.language_model.clients.base_client import BaseClient
from mcp_dalux.language_model.contracts import AgentDecision, ToolRequest

class ClaudeClient(BaseClient):

    @property
    def model_name(self) -> str:
        return "Claude"
    
    @property
    def version(self) -> str:
        return "Unknown"

    async def generate_decision(self, text: str, instructions: str, tools: list[str] | None = None) -> AgentDecision:
        # Dummy logic to test branching decision flow based on text input - whether to just answer or to use tools
        normalized_text = text.lower().strip()

        if tools and any(keyword in normalized_text for keyword in ("tool", "lookup", "find")):
            return AgentDecision(
                mode="tools",
                message="I need to use a tool before answering.",
                tool_requests=[
                    ToolRequest(
                        tool_name=tools[0],
                        arguments={"prompt": text, "instructions": instructions},
                    )
                ],
                raw_output="dummy-tool-request",
            )

        return AgentDecision(
            mode="answer",
            message=f"Claude answer: {text}",
            raw_output="dummy-answer",
        )