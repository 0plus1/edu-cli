from __future__ import annotations

import random

import click

from cli_edu.generator import build_question_set, validate_config
from cli_edu.i18n import get_translator
from cli_edu.models import SessionConfig
from cli_edu.session import run_session

EXERCISE_TYPES = ("math", "reading", "mixed")


def prompt_seed(translator) -> int | None:
    raw_value = click.prompt(
        translator.t("app.prompt_seed"),
        default="",
        show_default=False,
    )
    if raw_value == "":
        return None
    return int(raw_value)


def prompt_exercise_type(translator) -> str:
    click.echo(f"1. {translator.t('exercise.math')}")
    click.echo(f"2. {translator.t('exercise.reading')}")
    click.echo(f"3. {translator.t('exercise.mixed')}")
    selection = click.prompt(
        translator.t("app.prompt_exercise_type"),
        type=click.IntRange(1, 3),
        default=1,
    )
    return EXERCISE_TYPES[selection - 1]


def prompt_custom_config(translator, locale: str) -> SessionConfig:
    exercise_type = prompt_exercise_type(translator)
    target_age = click.prompt(
        translator.t("app.prompt_target_age"),
        type=click.IntRange(4, 14),
        default=9,
    )
    min_age = click.prompt(
        translator.t("app.prompt_min_age"),
        type=click.IntRange(4, 14),
        default=target_age,
    )
    max_age = click.prompt(
        translator.t("app.prompt_max_age"),
        type=click.IntRange(min_age, 14),
        default=target_age,
    )
    count = click.prompt(
        translator.t("app.prompt_count"),
        type=click.IntRange(1, 20),
        default=5,
    )
    seed = prompt_seed(translator)
    return SessionConfig(
        target_age=target_age,
        min_age=min_age,
        max_age=max_age,
        count=count,
        locale=locale,
        exercise_type=exercise_type,
        seed=seed,
    )


def preset_options(locale: str) -> dict[int, tuple[str, SessionConfig | None]]:
    return {
        1: (
            get_translator(locale).t("preset.4_5"),
            SessionConfig(target_age=5, min_age=4, max_age=5, count=5, locale=locale),
        ),
        2: (
            get_translator(locale).t("preset.6_7"),
            SessionConfig(target_age=7, min_age=6, max_age=7, count=5, locale=locale),
        ),
        3: (
            get_translator(locale).t("preset.8_9"),
            SessionConfig(target_age=9, min_age=8, max_age=9, count=5, locale=locale),
        ),
        4: (
            get_translator(locale).t("preset.10_11"),
            SessionConfig(
                target_age=11,
                min_age=10,
                max_age=11,
                count=5,
                locale=locale,
            ),
        ),
        5: (
            get_translator(locale).t("preset.12_14"),
            SessionConfig(
                target_age=13,
                min_age=12,
                max_age=14,
                count=5,
                locale=locale,
            ),
        ),
        6: (get_translator(locale).t("preset.custom"), None),
    }


def prompt_for_config(translator, locale: str) -> SessionConfig:
    presets = preset_options(locale)
    click.secho(translator.t("app.choose_setup"), fg="blue", bold=True)
    click.echo(f"1. {translator.t('exercise.math')}")
    click.echo(f"2. {translator.t('exercise.reading')}")
    click.echo(f"3. {translator.t('exercise.mixed')}")
    exercise_type = click.prompt(
        translator.t("app.prompt_exercise_type"),
        type=click.IntRange(1, 3),
        default=1,
    )
    selected_exercise_type = EXERCISE_TYPES[exercise_type - 1]
    click.echo()
    for number, (label, _) in presets.items():
        click.echo(f"{number}. {label}")

    selection = click.prompt(
        translator.t("app.menu_option"),
        type=click.IntRange(1, len(presets)),
        default=3,
    )
    label, preset = presets[selection]

    if preset is None:
        return prompt_custom_config(translator, locale)

    click.echo(translator.t("app.selected", label=label))
    count = click.prompt(
        translator.t("app.prompt_count"),
        type=click.IntRange(1, 20),
        default=preset.count,
    )
    seed = prompt_seed(translator)
    return SessionConfig(
        target_age=preset.target_age,
        min_age=preset.min_age,
        max_age=preset.max_age,
        count=count,
        locale=locale,
        exercise_type=selected_exercise_type,
        seed=seed,
    )


def build_config_from_args(
    age: int | None,
    min_age: int | None,
    max_age: int | None,
    count: int | None,
    locale: str,
    exercise_type: str,
    seed: int | None,
) -> SessionConfig:
    target_age = age if age is not None else 9
    return SessionConfig(
        target_age=target_age,
        min_age=min_age if min_age is not None else target_age,
        max_age=max_age if max_age is not None else target_age,
        count=count if count is not None else 5,
        locale=locale,
        exercise_type=exercise_type,
        seed=seed,
    )


@click.command()
@click.option("--age", type=click.IntRange(4, 14), help="Target age for the child.")
@click.option("--min-age", type=click.IntRange(4, 14), help="Lower age bound.")
@click.option("--max-age", type=click.IntRange(4, 14), help="Upper age bound.")
@click.option("--count", type=click.IntRange(1, 20), help="Number of questions.")
@click.option("--locale", default="en", help="Locale to use. Supported: en, it.")
@click.option("--exercise-type", default="math", help="Exercise type. Supported: math, reading, mixed.")
@click.option("--seed", type=int, help="Random seed for repeatable sessions.")
def main(
    age: int | None,
    min_age: int | None,
    max_age: int | None,
    count: int | None,
    locale: str,
    exercise_type: str,
    seed: int | None,
) -> None:
    try:
        translator = get_translator(locale)
    except ValueError as error:
        raise click.ClickException(str(error)) from error

    if all(
        value is None for value in (age, min_age, max_age, count, seed)
    ) and exercise_type == "math":
        config = prompt_for_config(translator, translator.locale)
    else:
        config = build_config_from_args(
            age,
            min_age,
            max_age,
            count,
            translator.locale,
            exercise_type,
            seed,
        )

    try:
        validated = validate_config(config, translator)
    except ValueError as error:
        raise click.ClickException(str(error)) from error

    rng = random.Random(validated.seed)
    questions = build_question_set(rng, validated, translator)
    run_session(questions, validated, translator)
