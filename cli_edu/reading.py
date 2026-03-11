from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from cli_edu.i18n import Translator
from cli_edu.models import Question, SessionConfig


@dataclass(frozen=True)
class ReadingQuestionRecord:
    prompt: str
    choices: tuple[str, ...]
    answer_index: int
    skill: str


@dataclass(frozen=True)
class PassageRecord:
    passage_id: str
    min_age: int
    max_age: int
    title: str
    passage: str
    questions: tuple[ReadingQuestionRecord, ...]


def content_path(locale: str) -> Path:
    return (
        Path(__file__).resolve().parent.parent / "content" / locale / "reading.json"
    )


def validate_reading_bank(data: list[dict[str, object]]) -> tuple[PassageRecord, ...]:
    passages: list[PassageRecord] = []

    for passage in data:
        passage_id = str(passage["id"])
        min_age = int(passage["min_age"])
        max_age = int(passage["max_age"])
        title = str(passage["title"])
        body = str(passage["passage"])
        question_records: list[ReadingQuestionRecord] = []

        if min_age > max_age:
            msg = f"Invalid age range in reading passage {passage_id}."
            raise ValueError(msg)

        for question in passage["questions"]:
            prompt = str(question["prompt"])
            choices = tuple(str(choice) for choice in question["choices"])
            answer_index = int(question["answer_index"])
            skill = str(question["skill"])

            if not choices:
                msg = f"Reading question without choices in passage {passage_id}."
                raise ValueError(msg)

            if answer_index < 0 or answer_index >= len(choices):
                msg = f"Invalid answer index in passage {passage_id}."
                raise ValueError(msg)

            question_records.append(
                ReadingQuestionRecord(
                    prompt=prompt,
                    choices=choices,
                    answer_index=answer_index,
                    skill=skill,
                )
            )

        passages.append(
            PassageRecord(
                passage_id=passage_id,
                min_age=min_age,
                max_age=max_age,
                title=title,
                passage=body,
                questions=tuple(question_records),
            )
        )

    return tuple(passages)


def load_reading_bank(locale: str) -> tuple[PassageRecord, ...]:
    path = content_path(locale)
    raw_data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw_data, list):
        msg = f"Reading bank at {path} must be a list."
        raise ValueError(msg)
    return validate_reading_bank(raw_data)


def is_eligible(passage: PassageRecord, config: SessionConfig) -> bool:
    return passage.min_age <= config.max_age and passage.max_age >= config.min_age


def choice_letter(index: int) -> str:
    return chr(ord("A") + index)


def to_question(
    passage: PassageRecord,
    record: ReadingQuestionRecord,
    translator: Translator,
) -> Question:
    correct_letter = choice_letter(record.answer_index)
    correct_choice = record.choices[record.answer_index]
    accepted_answers = (
        correct_letter.lower(),
        correct_letter,
        correct_choice.lower(),
    )
    rendered_choices = tuple(
        f"{choice_letter(index)}. {choice}"
        for index, choice in enumerate(record.choices)
    )
    return Question(
        prompt=record.prompt,
        accepted_answers=accepted_answers,
        correct_answer=f"{correct_letter}. {correct_choice}",
        skill=translator.t(record.skill),
        choices=rendered_choices,
        passage_id=passage.passage_id,
        passage_title=passage.title,
        passage_text=passage.passage,
    )


def build_reading_questions(
    rng: random.Random,
    config: SessionConfig,
    translator: Translator,
) -> list[Question]:
    bank = load_reading_bank(config.locale)
    eligible_passages = [passage for passage in bank if is_eligible(passage, config)]

    if not eligible_passages:
        msg = f"No reading passages available for locale {config.locale}."
        raise ValueError(msg)

    rng.shuffle(eligible_passages)
    questions: list[Question] = []

    while len(questions) < config.count:
        for passage in eligible_passages:
            ordered_records = list(passage.questions)
            rng.shuffle(ordered_records)
            remaining = config.count - len(questions)
            for record in ordered_records[:remaining]:
                questions.append(to_question(passage, record, translator))
            if len(questions) >= config.count:
                break
        else:
            rng.shuffle(eligible_passages)

    return questions
