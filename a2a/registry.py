# File: a2a/registry.py
"""In-memory registry for A2A agent cards and executors."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .protocol import AgentCard


@dataclass
class AgentRegistry:
    cards: Dict[str, AgentCard] = field(default_factory=dict)
    executors: Dict[str, object] = field(default_factory=dict)

    def register(self, name: str, card: AgentCard, executor: object) -> None:
        self.cards[name.lower()] = card
        self.executors[name.lower()] = executor

    def get_card(self, name: str) -> AgentCard:
        key = name.lower()
        if key not in self.cards:
            raise KeyError(f"Agent card not found: {name}")
        return self.cards[key]

    def get_executor(self, name: str):
        key = name.lower()
        if key not in self.executors:
            raise KeyError(f"Agent executor not found: {name}")
        return self.executors[key]

    def list_agents(self) -> List[str]:
        return sorted(self.cards.keys())

    def all_cards(self) -> List[AgentCard]:
        return [self.cards[name] for name in self.list_agents()]


registry = AgentRegistry()
