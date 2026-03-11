from __future__ import annotations

import random

from cli_edu.i18n import Translator
from cli_edu.models import AgeLevel, Problem, ProblemGenerator, SessionConfig


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

    return config


def addition_problem(rng: random.Random, low: int, high: int, skill: str) -> Problem:
    left = rng.randint(low, high)
    right = rng.randint(low, high)
    return Problem(
        prompt=f"{left} + {right} = ?",
        answer=left + right,
        skill=skill,
    )


def subtraction_problem(
    rng: random.Random,
    low: int,
    high: int,
    skill: str,
) -> Problem:
    left = rng.randint(low, high)
    right = rng.randint(low, left)
    return Problem(
        prompt=f"{left} - {right} = ?",
        answer=left - right,
        skill=skill,
    )


def multiplication_problem(rng: random.Random, max_factor: int, skill: str) -> Problem:
    left = rng.randint(2, max_factor)
    right = rng.randint(2, max_factor)
    return Problem(
        prompt=f"{left} x {right} = ?",
        answer=left * right,
        skill=skill,
    )


def division_problem(rng: random.Random, max_factor: int, skill: str) -> Problem:
    divisor = rng.randint(2, max_factor)
    quotient = rng.randint(2, max_factor)
    dividend = divisor * quotient
    return Problem(
        prompt=f"{dividend} / {divisor} = ?",
        answer=quotient,
        skill=skill,
    )


def word_problem(
    rng: random.Random,
    translator: Translator,
    item_key: str,
    low: int,
    high: int,
    skill: str,
) -> Problem:
    groups = rng.randint(2, 5)
    per_group = rng.randint(low, high)
    total = groups * per_group
    return Problem(
        prompt=translator.t(
            "problem.word_bags",
            groups=groups,
            per_group=per_group,
            item=translator.t(item_key),
        ),
        answer=total,
        skill=skill,
    )


def level_for_age(age: int, translator: Translator) -> AgeLevel:
    addition = translator.t("skill.addition")
    subtraction = translator.t("skill.subtraction")
    multiplication = translator.t("skill.multiplication")
    division = translator.t("skill.division")
    word_problem_skill = translator.t("skill.word_problem")

    if age <= 5:
        return AgeLevel(
            label="ages 4-5",
            generators=(
                lambda rng: addition_problem(rng, 1, 10, addition),
                lambda rng: subtraction_problem(rng, 1, 10, subtraction),
            ),
        )
    if age <= 7:
        return AgeLevel(
            label="ages 6-7",
            generators=(
                lambda rng: addition_problem(rng, 5, 20, addition),
                lambda rng: subtraction_problem(rng, 5, 20, subtraction),
                lambda rng: word_problem(
                    rng,
                    translator,
                    "item.stickers",
                    2,
                    6,
                    word_problem_skill,
                ),
            ),
        )
    if age <= 9:
        return AgeLevel(
            label="ages 8-9",
            generators=(
                lambda rng: addition_problem(rng, 10, 60, addition),
                lambda rng: subtraction_problem(rng, 10, 60, subtraction),
                lambda rng: multiplication_problem(rng, 10, multiplication),
                lambda rng: word_problem(
                    rng,
                    translator,
                    "item.apples",
                    3,
                    9,
                    word_problem_skill,
                ),
            ),
        )
    if age <= 11:
        return AgeLevel(
            label="ages 10-11",
            generators=(
                lambda rng: addition_problem(rng, 25, 150, addition),
                lambda rng: subtraction_problem(rng, 25, 150, subtraction),
                lambda rng: multiplication_problem(rng, 12, multiplication),
                lambda rng: division_problem(rng, 12, division),
                lambda rng: word_problem(
                    rng,
                    translator,
                    "item.marbles",
                    4,
                    12,
                    word_problem_skill,
                ),
            ),
        )
    return AgeLevel(
        label="ages 12-14",
        generators=(
            lambda rng: addition_problem(rng, 100, 500, addition),
            lambda rng: subtraction_problem(rng, 100, 500, subtraction),
            lambda rng: multiplication_problem(rng, 15, multiplication),
            lambda rng: division_problem(rng, 15, division),
            lambda rng: word_problem(
                rng,
                translator,
                "item.cards",
                6,
                15,
                word_problem_skill,
            ),
        ),
    )


def ages_in_range(config: SessionConfig) -> list[int]:
    return list(range(config.min_age, config.max_age + 1))


def build_problem_set(
    rng: random.Random,
    config: SessionConfig,
    translator: Translator,
) -> list[Problem]:
    problems: list[Problem] = []
    candidate_ages = ages_in_range(config)
    planned_generators: list[ProblemGenerator] = []

    for _ in range(config.count):
        if not planned_generators:
            age = rng.choice(candidate_ages)
            level = level_for_age(age, translator)
            planned_generators = list(level.generators)
            rng.shuffle(planned_generators)

        generator = planned_generators.pop()
        problems.append(generator(rng))

    return problems
