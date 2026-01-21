from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Iterable, List


@dataclass(frozen=True)
class Idea:
    bot_id: int
    network_layer: int
    sequence: int
    summary: str
    created_at: str


@dataclass
class Bot:
    bot_id: int
    network_layers: List[int]
    idea_rate: float
    sequence: int = 0
    fractional_accumulator: float = 0.0

    def generate_ideas(self) -> List[Idea]:
        ideas: List[Idea] = []
        base_count = int(self.idea_rate)
        fractional = self.idea_rate - base_count
        extra = 0
        if fractional > 0:
            self.fractional_accumulator += fractional
            if self.fractional_accumulator >= 1:
                extra = 1
                self.fractional_accumulator -= 1
        total = base_count + extra
        for _ in range(total):
            self.sequence += 1
            layer = self.network_layers[(self.sequence + self.bot_id) % len(self.network_layers)]
            ideas.append(
                Idea(
                    bot_id=self.bot_id,
                    network_layer=layer,
                    sequence=self.sequence,
                    summary=self._summarize(layer),
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )
        return ideas

    def _summarize(self, layer: int) -> str:
        heuristic = (self.bot_id * 31 + self.sequence * 17 + layer * 13) % 100
        if heuristic < 33:
            return f"Refuerzo de consenso en capa {layer}"
        if heuristic < 66:
            return f"Optimización de latencia en capa {layer}"
        return f"Prueba de resiliencia en capa {layer}"


@dataclass
class BotEngine:
    bot_count: int
    idea_rate: float
    seed: int
    network_layers: List[int]
    bots: List[Bot] = field(init=False)
    total_ideas: int = 0
    history: Deque[Idea] = field(default_factory=lambda: deque(maxlen=500))

    def __post_init__(self) -> None:
        if self.bot_count <= 0:
            raise ValueError("bot_count debe ser mayor que 0")
        if not self.network_layers:
            raise ValueError("network_layers no puede estar vacío")
        self.bots = [
            Bot(
                bot_id=bot_id,
                network_layers=self.network_layers,
                idea_rate=self.idea_rate,
            )
            for bot_id in range(self.bot_count)
        ]

    def tick(self) -> List[Idea]:
        ideas: List[Idea] = []
        for bot in self.bots:
            bot_ideas = bot.generate_ideas()
            if bot_ideas:
                ideas.extend(bot_ideas)
        self.total_ideas += len(ideas)
        self.history.extend(ideas)
        return ideas

    def status(self) -> dict:
        return {
            "bot_count": self.bot_count,
            "idea_rate": self.idea_rate,
            "seed": self.seed,
            "network_layers": len(self.network_layers),
            "total_ideas": self.total_ideas,
            "last_generated": self.history[-1].created_at if self.history else None,
        }

    def recent_ideas(self, limit: int = 100) -> List[dict]:
        return [self._idea_to_dict(idea) for idea in list(self.history)[-limit:]]

    @staticmethod
    def _idea_to_dict(idea: Idea) -> dict:
        return {
            "bot_id": idea.bot_id,
            "network_layer": idea.network_layer,
            "sequence": idea.sequence,
            "summary": idea.summary,
            "created_at": idea.created_at,
        }


def ideas_to_payload(ideas: Iterable[Idea]) -> List[dict]:
    return [BotEngine._idea_to_dict(idea) for idea in ideas]
