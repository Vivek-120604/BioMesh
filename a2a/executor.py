# File: a2a/executor.py
"""Executor base class for running A2A agent tasks."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from .protocol import Artifact, Message, Task, TaskState, TaskStatus


class AgentExecutor(ABC):
    """Base executor that manages the full A2A task lifecycle."""

    name: str
    description: str
    artifact_type: str

    def __init__(self, name: str, description: str, artifact_type: str) -> None:
        self.name = name
        self.description = description
        self.artifact_type = artifact_type

    @abstractmethod
    def execute(self, task: Task) -> Artifact:
        """Execute the task and return an artifact."""

    def run(self, user_input: str, context_id: str) -> Task:
        input_message = Message.from_text(user_input)
        task = Task(
            task_id=str(uuid4()),
            context_id=context_id,
            input_message=input_message,
            status=TaskStatus(state=TaskState.SUBMITTED),
        )
        task.status = TaskStatus(state=TaskState.WORKING, message=f"{self.name} started")
        try:
            artifact = self.execute(task)
            task.artifacts.append(artifact)
            task.output_message = Message.from_text(artifact.content, role="assistant")
            task.status = TaskStatus(
                state=TaskState.COMPLETED,
                message=f"{self.name} completed",
                updated_at=datetime.utcnow().isoformat() + "Z",
            )
            return task
        except Exception as exc:  # pragma: no cover - surfaced to API/UI as failure state
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message=f"{self.name} failed: {exc}",
                updated_at=datetime.utcnow().isoformat() + "Z",
            )
            task.output_message = Message.from_text(str(exc), role="assistant")
            return task

    def build_artifact(self, title: str, content: str, metadata: Dict[str, Any] | None = None) -> Artifact:
        return Artifact(
            type=self.artifact_type,
            title=title,
            content=content,
            metadata=metadata or {},
        )
