from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    prompt: str
    answer: int
    skill: str


ProblemGenerator = Callable[[random.Random], Problem]


@dataclass(frozen=True)
class AgeLevel:
    label: str
    generators: tuple[ProblemGenerator, ...]


@dataclass(frozen=True)
class SessionConfig:
    target_age: int
    min_age: int
    max_age: int
    count: int
    seed: int | None = None

    @property
    def age_label(self) -> str:
        if self.min_age == self.max_age:
            return str(self.min_age)
        return f"{self.min_age}-{self.max_age}"


@dataclass(frozen=True)
class SessionSummary:
    total: int
    correct: int
    total_duration_seconds: float
    question_durations_seconds: tuple[float, ...]
