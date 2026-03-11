from __future__ import annotations

import time
from dataclasses import dataclass, replace

import click

from cli_edu.i18n import Translator
from cli_edu.models import Question, SessionConfig, SessionSummary

ORANGE = "\033[38;5;208m"
RESET = "\033[0m"


@dataclass(frozen=True)
class QuestionResult:
    is_correct: bool
    duration_seconds: float


def colored(text: str, color: str) -> str:
    if not click.get_current_context().color:
        return text
    return f"{color}{text}{RESET}"


def make_bar(completed: int, total: int, width: int = 20) -> str:
    safe_total = max(total, 1)
    filled = round(width * completed / safe_total)
    return f"[{'#' * filled}{'-' * (width - filled)}]"


def score_color(percentage: float) -> str:
    if percentage < 40:
        return "red"
    if percentage < 70:
        return ORANGE
    return "green"


def render_progress(
    translator: Translator,
    current: int,
    total: int,
) -> str:
    bar = make_bar(current, total)
    return translator.t("session.progress", current=current, total=total, bar=bar)


def render_accuracy(translator: Translator, correct: int, answered: int) -> str:
    if answered == 0:
        percentage = 0.0
    else:
        percentage = (correct / answered) * 100

    bar = make_bar(round(percentage), 100)
    color = score_color(percentage)
    line = translator.t("session.accuracy", percentage=percentage, bar=bar)

    if color == "red":
        return click.style(line, fg="red")
    if color == "green":
        return click.style(line, fg="green")
    return colored(line, ORANGE)


def format_duration(seconds: float) -> str:
    minutes, remainder = divmod(seconds, 60)
    if minutes >= 1:
        return f"{int(minutes)}m {remainder:.1f}s"
    return f"{remainder:.1f}s"


def ask_question(
    translator: Translator,
    index: int,
    total: int,
    correct: int,
    question: Question,
) -> QuestionResult:
    answered = index - 1
    click.echo()
    click.secho(render_progress(translator, index, total), fg="cyan")
    click.echo(render_accuracy(translator, correct, answered))
    if question.passage_text is not None:
        click.secho(translator.t("session.passage_header"), fg="blue")
        if question.passage_title is not None:
            click.echo(translator.t("session.passage_title", title=question.passage_title))
        click.echo(question.passage_text)
        click.echo()
    click.echo(
        translator.t(
            "session.question",
            index=index,
            skill=question.skill,
            prompt=question.prompt,
        )
    )
    for choice in question.choices:
        click.echo(choice)

    started_at = time.perf_counter()
    answer = click.prompt(translator.t("session.answer_prompt"), type=str).strip()
    duration_seconds = time.perf_counter() - started_at
    normalized_answer = answer.lower()
    is_correct = normalized_answer in question.accepted_answers

    if is_correct:
        click.secho(translator.t("session.correct"), fg="green")
    else:
        click.secho(
            translator.t("session.incorrect", answer=question.correct_answer),
            fg="red",
        )

    updated_correct = correct + int(is_correct)
    click.echo(render_accuracy(translator, updated_correct, index))
    click.echo(
        translator.t(
            "session.question_time",
            duration=format_duration(duration_seconds),
        )
    )
    return QuestionResult(
        is_correct=is_correct,
        duration_seconds=duration_seconds,
    )


def run_session(
    questions: list[Question],
    config: SessionConfig,
    translator: Translator,
) -> SessionSummary:
    session_started_at = time.perf_counter()
    click.secho(
        translator.t(
            "session.start",
            exercise_type=translator.t(f"exercise.{config.exercise_type}").lower(),
            age_label=config.age_label,
        ),
        fg="blue",
        bold=True,
    )
    click.echo(translator.t("session.total_questions", count=config.count))

    summary = SessionSummary(
        total=config.count,
        correct=0,
        total_duration_seconds=0.0,
        question_durations_seconds=(),
    )

    shown_passages: set[str] = set()
    for index, question in enumerate(questions, start=1):
        if question.passage_id is not None and question.passage_id in shown_passages:
            question = Question(
                prompt=question.prompt,
                accepted_answers=question.accepted_answers,
                correct_answer=question.correct_answer,
                skill=question.skill,
                choices=question.choices,
                passage_id=question.passage_id,
                passage_title=None,
                passage_text=None,
            )
        elif question.passage_id is not None:
            shown_passages.add(question.passage_id)

        result = ask_question(
            translator,
            index,
            config.count,
            summary.correct,
            question,
        )
        updated_correct = summary.correct + int(result.is_correct)
        summary = replace(
            summary,
            correct=updated_correct,
            question_durations_seconds=(
                *summary.question_durations_seconds,
                result.duration_seconds,
            ),
        )

    total_duration_seconds = time.perf_counter() - session_started_at
    summary = replace(summary, total_duration_seconds=total_duration_seconds)
    percentage = (summary.correct / summary.total) * 100
    click.echo()
    click.secho(translator.t("session.complete"), fg="blue", bold=True)
    click.echo(render_accuracy(translator, summary.correct, summary.total))
    click.echo(
        translator.t(
            "session.final_score",
            correct=summary.correct,
            total=summary.total,
            percentage=percentage,
        )
    )
    click.echo(
        translator.t(
            "session.total_time",
            duration=format_duration(summary.total_duration_seconds),
        )
    )

    for index, duration in enumerate(summary.question_durations_seconds, start=1):
        click.echo(
            translator.t(
                "session.per_question_time",
                index=index,
                duration=format_duration(duration),
            )
        )

    return summary
