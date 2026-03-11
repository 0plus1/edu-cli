from __future__ import annotations

import random

import click

from cli_edu.generator import build_problem_set, validate_config
from cli_edu.models import SessionConfig
from cli_edu.session import run_session

PRESETS: dict[int, tuple[str, SessionConfig | None]] = {
    1: ("Ages 4-5", SessionConfig(target_age=5, min_age=4, max_age=5, count=5)),
    2: ("Ages 6-7", SessionConfig(target_age=7, min_age=6, max_age=7, count=5)),
    3: ("Ages 8-9", SessionConfig(target_age=9, min_age=8, max_age=9, count=5)),
    4: ("Ages 10-11", SessionConfig(target_age=11, min_age=10, max_age=11, count=5)),
    5: ("Ages 12-14", SessionConfig(target_age=13, min_age=12, max_age=14, count=5)),
    6: ("Custom", None),
}


def prompt_seed() -> int | None:
    raw_value = click.prompt(
        "Seed for repeatable questions (leave blank for random)",
        default="",
        show_default=False,
    )
    if raw_value == "":
        return None
    return int(raw_value)


def prompt_custom_config() -> SessionConfig:
    target_age = click.prompt("Target age", type=click.IntRange(4, 14), default=9)
    min_age = click.prompt(
        "Minimum age",
        type=click.IntRange(4, 14),
        default=target_age,
    )
    max_age = click.prompt(
        "Maximum age",
        type=click.IntRange(min_age, 14),
        default=target_age,
    )
    count = click.prompt("Number of questions", type=click.IntRange(1, 20), default=5)
    seed = prompt_seed()
    return SessionConfig(
        target_age=target_age,
        min_age=min_age,
        max_age=max_age,
        count=count,
        seed=seed,
    )


def prompt_for_config() -> SessionConfig:
    click.secho("Choose a maths practice setup:", fg="blue", bold=True)
    for number, (label, _) in PRESETS.items():
        click.echo(f"{number}. {label}")

    selection = click.prompt(
        "Select a menu option",
        type=click.IntRange(1, len(PRESETS)),
        default=3,
    )
    label, preset = PRESETS[selection]

    if preset is None:
        return prompt_custom_config()

    click.echo(f"Selected: {label}")
    count = click.prompt(
        "Number of questions",
        type=click.IntRange(1, 20),
        default=preset.count,
    )
    seed = prompt_seed()
    return SessionConfig(
        target_age=preset.target_age,
        min_age=preset.min_age,
        max_age=preset.max_age,
        count=count,
        seed=seed,
    )


def build_config_from_args(
    age: int | None,
    min_age: int | None,
    max_age: int | None,
    count: int | None,
    seed: int | None,
) -> SessionConfig:
    target_age = age if age is not None else 9
    return SessionConfig(
        target_age=target_age,
        min_age=min_age if min_age is not None else target_age,
        max_age=max_age if max_age is not None else target_age,
        count=count if count is not None else 5,
        seed=seed,
    )


@click.command()
@click.option("--age", type=click.IntRange(4, 14), help="Target age for the child.")
@click.option("--min-age", type=click.IntRange(4, 14), help="Lower age bound.")
@click.option("--max-age", type=click.IntRange(4, 14), help="Upper age bound.")
@click.option("--count", type=click.IntRange(1, 20), help="Number of questions.")
@click.option("--seed", type=int, help="Random seed for repeatable sessions.")
def main(
    age: int | None,
    min_age: int | None,
    max_age: int | None,
    count: int | None,
    seed: int | None,
) -> None:
    if all(value is None for value in (age, min_age, max_age, count, seed)):
        config = prompt_for_config()
    else:
        config = build_config_from_args(age, min_age, max_age, count, seed)

    try:
        validated = validate_config(config)
    except ValueError as error:
        raise click.ClickException(str(error)) from error

    rng = random.Random(validated.seed)
    problems = build_problem_set(rng, validated)
    run_session(problems, validated)
