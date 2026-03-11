# AGENTS

- Aim: keep this project as a small, friendly CLI for age-appropriate maths practice.
- Code quality: prefer small modules, clear names, and simple interactive flows.
- Tooling: use `uv`, keep `ruff` clean, and avoid adding unnecessary dependencies.
- I18n: use the key-based catalog in `cli_edu/i18n.py`; do not hardcode user-facing strings in feature modules.
- I18n updates: when adding UI text, add an English key, an Italian translation, and thread the translator through the call site.
