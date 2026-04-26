# File: a2a/client.py
"""A2A client for dispatching tasks to registered executors."""
from __future__ import annotations

from .protocol import AgentCard, SendMessageSuccessResponse
from .registry import registry


class A2AClient:
    def send_message(self, agent_name: str, user_input: str, context_id: str) -> SendMessageSuccessResponse:
        executor = registry.get_executor(agent_name)
        card = registry.get_card(agent_name)
        task = executor.run(user_input=user_input, context_id=context_id)
        artifact = task.artifacts[0] if task.artifacts else None
        return SendMessageSuccessResponse(task=task, artifact=artifact, agent_card=card)

    def get_agent_card(self, agent_name: str) -> AgentCard:
        return registry.get_card(agent_name)

    def list_agents(self) -> list[str]:
        return registry.list_agents()
