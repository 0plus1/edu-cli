# cli-edu

Small interactive CLI for age-appropriate maths practice.

## Run

Start with the interactive menu:

```bash
uv run cli-edu
```

Or launch a session directly:

```bash
uv run cli-edu --age 9 --min-age 8 --max-age 10 --count 8 --seed 7
```

## What it does

- Uses age bands to choose suitable arithmetic and word problems.
- Asks each question interactively before moving on.
- Shows progress, a live accuracy bar, and time spent per question and per session.

## Quality checks

```bash
uv run ruff check .
```
