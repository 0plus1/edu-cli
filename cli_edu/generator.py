from __future__ import annotations

import random

from cli_edu.models import AgeLevel, Problem, ProblemGenerator, SessionConfig


def validate_config(config: SessionConfig) -> SessionConfig:
    if not 4 <= config.target_age <= 14:
        msg = "Age must be between 4 and 14."
        raise ValueError(msg)

    if not 4 <= config.min_age <= 14:
        msg = "Minimum age must be between 4 and 14."
        raise ValueError(msg)

    if not 4 <= config.max_age <= 14:
        msg = "Maximum age must be between 4 and 14."
        raise ValueError(msg)

    if config.min_age > config.max_age:
        msg = "Minimum age cannot be greater than maximum age."
        raise ValueError(msg)

    if config.count < 1:
        msg = "Count must be at least 1."
        raise ValueError(msg)

    return config


def addition_problem(rng: random.Random, low: int, high: int) -> Problem:
    left = rng.randint(low, high)
    right = rng.randint(low, high)
    return Problem(
        prompt=f"{left} + {right} = ?",
        answer=left + right,
        skill="addition",
    )


def subtraction_problem(rng: random.Random, low: int, high: int) -> Problem:
    left = rng.randint(low, high)
    right = rng.randint(low, left)
    return Problem(
        prompt=f"{left} - {right} = ?",
        answer=left - right,
        skill="subtraction",
    )


def multiplication_problem(rng: random.Random, max_factor: int) -> Problem:
    left = rng.randint(2, max_factor)
    right = rng.randint(2, max_factor)
    return Problem(
        prompt=f"{left} x {right} = ?",
        answer=left * right,
        skill="multiplication",
    )


def division_problem(rng: random.Random, max_factor: int) -> Problem:
    divisor = rng.randint(2, max_factor)
    quotient = rng.randint(2, max_factor)
    dividend = divisor * quotient
    return Problem(
        prompt=f"{dividend} / {divisor} = ?",
        answer=quotient,
        skill="division",
    )


def word_problem(rng: random.Random, item: str, low: int, high: int) -> Problem:
    groups = rng.randint(2, 5)
    per_group = rng.randint(low, high)
    total = groups * per_group
    return Problem(
        prompt=(
            f"There are {groups} bags with {per_group} {item} in each bag. "
            f"How many {item} are there altogether?"
        ),
        answer=total,
        skill="word problem",
    )


def level_for_age(age: int) -> AgeLevel:
    if age <= 5:
        return AgeLevel(
            label="ages 4-5",
            generators=(
                lambda rng: addition_problem(rng, 1, 10),
                lambda rng: subtraction_problem(rng, 1, 10),
            ),
        )
    if age <= 7:
        return AgeLevel(
            label="ages 6-7",
            generators=(
                lambda rng: addition_problem(rng, 5, 20),
                lambda rng: subtraction_problem(rng, 5, 20),
                lambda rng: word_problem(rng, "stickers", 2, 6),
            ),
        )
    if age <= 9:
        return AgeLevel(
            label="ages 8-9",
            generators=(
                lambda rng: addition_problem(rng, 10, 60),
                lambda rng: subtraction_problem(rng, 10, 60),
                lambda rng: multiplication_problem(rng, 10),
                lambda rng: word_problem(rng, "apples", 3, 9),
            ),
        )
    if age <= 11:
        return AgeLevel(
            label="ages 10-11",
            generators=(
                lambda rng: addition_problem(rng, 25, 150),
                lambda rng: subtraction_problem(rng, 25, 150),
                lambda rng: multiplication_problem(rng, 12),
                lambda rng: division_problem(rng, 12),
                lambda rng: word_problem(rng, "marbles", 4, 12),
            ),
        )
    return AgeLevel(
        label="ages 12-14",
        generators=(
            lambda rng: addition_problem(rng, 100, 500),
            lambda rng: subtraction_problem(rng, 100, 500),
            lambda rng: multiplication_problem(rng, 15),
            lambda rng: division_problem(rng, 15),
            lambda rng: word_problem(rng, "cards", 6, 15),
        ),
    )


def ages_in_range(config: SessionConfig) -> list[int]:
    return list(range(config.min_age, config.max_age + 1))


def build_problem_set(rng: random.Random, config: SessionConfig) -> list[Problem]:
    problems: list[Problem] = []
    candidate_ages = ages_in_range(config)
    planned_generators: list[ProblemGenerator] = []

    for _ in range(config.count):
        if not planned_generators:
            age = rng.choice(candidate_ages)
            level = level_for_age(age)
            planned_generators = list(level.generators)
            rng.shuffle(planned_generators)

        generator = planned_generators.pop()
        problems.append(generator(rng))

    return problems
