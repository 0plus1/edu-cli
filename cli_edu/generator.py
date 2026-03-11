from __future__ import annotations

import random

from cli_edu.i18n import Translator
from cli_edu.math import build_math_questions
from cli_edu.models import Question, SessionConfig
from cli_edu.reading import build_reading_questions

SUPPORTED_EXERCISE_TYPES = ("math", "reading", "mixed")


def validate_config(config: SessionConfig, translator: Translator) -> SessionConfig:
    if not 4 <= config.target_age <= 14:
        msg = translator.t("error.age")
        raise ValueError(msg)

    if not 4 <= config.min_age <= 14:
        msg = translator.t("error.min_age")
        raise ValueError(msg)

    if not 4 <= config.max_age <= 14:
        msg = translator.t("error.max_age")
        raise ValueError(msg)

    if config.min_age > config.max_age:
        msg = translator.t("error.age_order")
        raise ValueError(msg)

    if config.count < 1:
        msg = translator.t("error.count")
        raise ValueError(msg)

    if config.exercise_type not in SUPPORTED_EXERCISE_TYPES:
        msg = translator.t("error.exercise_type", exercise_type=config.exercise_type)
        raise ValueError(msg)

    return config


def build_question_set(
    rng: random.Random,
    config: SessionConfig,
    translator: Translator,
) -> list[Question]:
    if config.exercise_type == "math":
        return build_math_questions(rng, config, translator)

    if config.exercise_type == "reading":
        return build_reading_questions(rng, config, translator)

    math_count = config.count // 2
    reading_count = config.count - math_count

    math_config = SessionConfig(
        target_age=config.target_age,
        min_age=config.min_age,
        max_age=config.max_age,
        count=math_count,
        locale=config.locale,
        exercise_type="math",
        seed=config.seed,
    )
    reading_config = SessionConfig(
        target_age=config.target_age,
        min_age=config.min_age,
        max_age=config.max_age,
        count=reading_count,
        locale=config.locale,
        exercise_type="reading",
        seed=config.seed,
    )

    questions = build_math_questions(rng, math_config, translator)
    questions.extend(build_reading_questions(rng, reading_config, translator))
    rng.shuffle(questions)
    return questions
