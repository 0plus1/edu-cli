from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    prompt: str
    accepted_answers: tuple[str, ...]
    correct_answer: str
    skill: str
    choices: tuple[str, ...] = ()
    passage_id: str | None = None
    passage_title: str | None = None
    passage_text: str | None = None


QuestionGenerator = Callable[[random.Random], Question]


@dataclass(frozen=True)
class AgeLevel:
    label: str
    generators: tuple[QuestionGenerator, ...]


@dataclass(frozen=True)
class SessionConfig:
    target_age: int
    min_age: int
    max_age: int
    count: int
    locale: str = "en"
    exercise_type: str = "math"
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
