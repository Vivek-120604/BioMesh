# File: a2a/__init__.py
"""A2A protocol package for BioMesh.
Provides models, client, executor and registry for agent-to-agent orchestration.
"""
from .protocol import *
from .executor import *
from .client import *
from .registry import *

__all__ = [
    "TaskState",
    "TextPart",
    "Message",
    "Artifact",
    "Task",
    "AgentSkill",
    "AgentCard",
    "SendMessageRequest",
    "SendMessageSuccessResponse",
    "AgentExecutor",
    "A2AClient",
    "AgentRegistry",
    "registry",
]
