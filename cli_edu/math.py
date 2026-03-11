from __future__ import annotations

import random

from cli_edu.i18n import Translator
from cli_edu.models import AgeLevel, Question, QuestionGenerator, SessionConfig


def addition_problem(rng: random.Random, low: int, high: int, skill: str) -> Question:
    left = rng.randint(low, high)
    right = rng.randint(low, high)
    answer = left + right
    return Question(
        prompt=f"{left} + {right} = ?",
        accepted_answers=(str(answer),),
        correct_answer=str(answer),
        skill=skill,
    )


def subtraction_problem(
    rng: random.Random,
    low: int,
    high: int,
    skill: str,
) -> Question:
    left = rng.randint(low, high)
    right = rng.randint(low, left)
    answer = left - right
    return Question(
        prompt=f"{left} - {right} = ?",
        accepted_answers=(str(answer),),
        correct_answer=str(answer),
        skill=skill,
    )


def multiplication_problem(
    rng: random.Random,
    max_factor: int,
    skill: str,
) -> Question:
    left = rng.randint(2, max_factor)
    right = rng.randint(2, max_factor)
    answer = left * right
    return Question(
        prompt=f"{left} x {right} = ?",
        accepted_answers=(str(answer),),
        correct_answer=str(answer),
        skill=skill,
    )


def division_problem(rng: random.Random, max_factor: int, skill: str) -> Question:
    divisor = rng.randint(2, max_factor)
    quotient = rng.randint(2, max_factor)
    dividend = divisor * quotient
    return Question(
        prompt=f"{dividend} / {divisor} = ?",
        accepted_answers=(str(quotient),),
        correct_answer=str(quotient),
        skill=skill,
    )


def word_problem(
    rng: random.Random,
    translator: Translator,
    item_key: str,
    low: int,
    high: int,
    skill: str,
) -> Question:
    groups = rng.randint(2, 5)
    per_group = rng.randint(low, high)
    total = groups * per_group
    return Question(
        prompt=translator.t(
            "problem.word_bags",
            groups=groups,
            per_group=per_group,
            item=translator.t(item_key),
        ),
        accepted_answers=(str(total),),
        correct_answer=str(total),
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


def build_math_questions(
    rng: random.Random,
    config: SessionConfig,
    translator: Translator,
) -> list[Question]:
    questions: list[Question] = []
    candidate_ages = list(range(config.min_age, config.max_age + 1))
    planned_generators: list[QuestionGenerator] = []

    for _ in range(config.count):
        if not planned_generators:
            age = rng.choice(candidate_ages)
            level = level_for_age(age, translator)
            planned_generators = list(level.generators)
            rng.shuffle(planned_generators)

        generator = planned_generators.pop()
        questions.append(generator(rng))

    return questions
