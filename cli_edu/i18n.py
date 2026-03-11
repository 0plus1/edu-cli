from __future__ import annotations

from dataclasses import dataclass

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "it")
LOCALE_ALIASES = {
    "en": "en",
    "en_us": "en",
    "en-gb": "en",
    "en_us.utf-8": "en",
    "english": "en",
    "it": "it",
    "it_it": "it",
    "it-it": "it",
    "it_it.utf-8": "it",
    "italian": "it",
}

TRANSLATIONS = {
    "en": {
        "app.choose_setup": "Choose a maths practice setup:",
        "app.menu_option": "Select a menu option",
        "app.selected": "Selected: {label}",
        "app.prompt_seed": "Seed for repeatable questions (leave blank for random)",
        "app.prompt_target_age": "Target age",
        "app.prompt_min_age": "Minimum age",
        "app.prompt_max_age": "Maximum age",
        "app.prompt_count": "Number of questions",
        "app.option_age": "Target age for the child.",
        "app.option_min_age": "Lower age bound.",
        "app.option_max_age": "Upper age bound.",
        "app.option_count": "Number of questions.",
        "app.option_seed": "Random seed for repeatable sessions.",
        "app.option_locale": "Locale to use. Supported: en, it.",
        "error.age": "Age must be between 4 and 14.",
        "error.min_age": "Minimum age must be between 4 and 14.",
        "error.max_age": "Maximum age must be between 4 and 14.",
        "error.age_order": "Minimum age cannot be greater than maximum age.",
        "error.count": "Count must be at least 1.",
        "error.locale": "Unsupported locale '{locale}'. Supported locales: en, it.",
        "preset.4_5": "Ages 4-5",
        "preset.6_7": "Ages 6-7",
        "preset.8_9": "Ages 8-9",
        "preset.10_11": "Ages 10-11",
        "preset.12_14": "Ages 12-14",
        "preset.custom": "Custom",
        "skill.addition": "addition",
        "skill.subtraction": "subtraction",
        "skill.multiplication": "multiplication",
        "skill.division": "division",
        "skill.word_problem": "word problem",
        "item.stickers": "stickers",
        "item.apples": "apples",
        "item.marbles": "marbles",
        "item.cards": "cards",
        "problem.word_bags": (
            "There are {groups} bags with {per_group} {item} in each bag. "
            "How many {item} are there altogether?"
        ),
        "session.progress": "Progress {current}/{total} {bar}",
        "session.accuracy": "Accuracy {percentage:>5.1f}% {bar}",
        "session.question": "Question {index}: [{skill}] {prompt}",
        "session.answer_prompt": "Your answer",
        "session.correct": "Correct!",
        "session.incorrect": "Not quite. The right answer is {answer}.",
        "session.question_time": "Time for this question: {duration}",
        "session.start": "Starting maths practice for ages {age_label}",
        "session.total_questions": "Total questions: {count}",
        "session.complete": "Session complete",
        "session.final_score": "Final score: {correct}/{total} ({percentage:.1f}%)",
        "session.total_time": "Total time: {duration}",
        "session.per_question_time": "Question {index} time: {duration}",
    },
    "it": {
        "app.choose_setup": "Scegli una sessione di esercizi di matematica:",
        "app.menu_option": "Seleziona un'opzione del menu",
        "app.selected": "Selezionato: {label}",
        "app.prompt_seed": "Seed per domande ripetibili (lascia vuoto per casuale)",
        "app.prompt_target_age": "Eta di riferimento",
        "app.prompt_min_age": "Eta minima",
        "app.prompt_max_age": "Eta massima",
        "app.prompt_count": "Numero di domande",
        "app.option_age": "Eta di riferimento per il bambino.",
        "app.option_min_age": "Limite inferiore dell'eta.",
        "app.option_max_age": "Limite superiore dell'eta.",
        "app.option_count": "Numero di domande.",
        "app.option_seed": "Seed casuale per sessioni ripetibili.",
        "app.option_locale": "Lingua da usare. Supportate: en, it.",
        "error.age": "L'eta deve essere compresa tra 4 e 14.",
        "error.min_age": "L'eta minima deve essere compresa tra 4 e 14.",
        "error.max_age": "L'eta massima deve essere compresa tra 4 e 14.",
        "error.age_order": "L'eta minima non puo essere maggiore dell'eta massima.",
        "error.count": "Il numero di domande deve essere almeno 1.",
        "error.locale": "Locale '{locale}' non supportata. Locali supportate: en, it.",
        "preset.4_5": "Eta 4-5",
        "preset.6_7": "Eta 6-7",
        "preset.8_9": "Eta 8-9",
        "preset.10_11": "Eta 10-11",
        "preset.12_14": "Eta 12-14",
        "preset.custom": "Personalizzato",
        "skill.addition": "addizione",
        "skill.subtraction": "sottrazione",
        "skill.multiplication": "moltiplicazione",
        "skill.division": "divisione",
        "skill.word_problem": "problema testuale",
        "item.stickers": "adesivi",
        "item.apples": "mele",
        "item.marbles": "biglie",
        "item.cards": "carte",
        "problem.word_bags": (
            "Ci sono {groups} sacchetti con {per_group} {item} in ogni sacchetto. "
            "Quanti {item} ci sono in tutto?"
        ),
        "session.progress": "Avanzamento {current}/{total} {bar}",
        "session.accuracy": "Precisione {percentage:>5.1f}% {bar}",
        "session.question": "Domanda {index}: [{skill}] {prompt}",
        "session.answer_prompt": "La tua risposta",
        "session.correct": "Corretto!",
        "session.incorrect": "Non proprio. La risposta giusta e {answer}.",
        "session.question_time": "Tempo per questa domanda: {duration}",
        "session.start": "Inizio esercizi di matematica per eta {age_label}",
        "session.total_questions": "Domande totali: {count}",
        "session.complete": "Sessione completata",
        "session.final_score": "Punteggio finale: {correct}/{total} ({percentage:.1f}%)",
        "session.total_time": "Tempo totale: {duration}",
        "session.per_question_time": "Tempo domanda {index}: {duration}",
    },
}


@dataclass(frozen=True)
class Translator:
    locale: str

    def t(self, key: str, **kwargs: object) -> str:
        template = TRANSLATIONS[self.locale].get(key, TRANSLATIONS[DEFAULT_LOCALE][key])
        return template.format(**kwargs)


def normalize_locale(locale: str | None) -> str:
    if locale is None:
        return DEFAULT_LOCALE

    normalized = locale.strip().lower().replace("-", "_")
    resolved = LOCALE_ALIASES.get(normalized)
    if resolved is None:
        msg = TRANSLATIONS[DEFAULT_LOCALE]["error.locale"].format(locale=locale)
        raise ValueError(msg)
    return resolved


def get_translator(locale: str | None) -> Translator:
    return Translator(locale=normalize_locale(locale))
