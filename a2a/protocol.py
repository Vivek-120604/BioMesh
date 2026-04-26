# File: a2a/protocol.py
"""Core A2A protocol schemas used by BioMesh.

The models are intentionally explicit so the registry, client, API, and UI can
exchange tasks, agent cards, and artifacts without relying on ad hoc dicts.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskState(str, Enum):
    SUBMITTED = "SUBMITTED"
    WORKING = "WORKING"
    INPUT_REQUESTED = "INPUT_REQUESTED"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    FAILED = "FAILED"


class TextPart(BaseModel):
    type: str = Field(default="text")
    text: str


class Message(BaseModel):
    role: str = Field(default="user")
    parts: List[TextPart]

    @classmethod
    def from_text(cls, text: str, role: str = "user") -> "Message":
        return cls(role=role, parts=[TextPart(text=text)])

    def as_text(self) -> str:
        return "\n".join(part.text for part in self.parts)


class Artifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskStatus(BaseModel):
    state: TaskState
    message: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: __import__("datetime").datetime.utcnow().isoformat() + "Z")


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    context_id: str
    input_message: Message
    output_message: Optional[Message] = None
    status: TaskStatus
    artifacts: List[Artifact] = Field(default_factory=list)


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str] = Field(default_factory=list)


class AgentCard(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"
    url: str
    protocol: str = Field(default="A2A")
    skills: List[AgentSkill] = Field(default_factory=list)
    input_modes: List[str] = Field(default_factory=lambda: ["text/plain"])
    output_modes: List[str] = Field(default_factory=lambda: ["text/plain"])
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    agent_name: str
    user_input: str
    context_id: str


class SendMessageSuccessResponse(BaseModel):
    task: Task
    artifact: Optional[Artifact] = None
    agent_card: Optional[AgentCard] = None
    ok: bool = True
