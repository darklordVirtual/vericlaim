# SPDX-License-Identifier: Apache-2.0
"""A tiny greeting library — the simplest possible worked example.

The claim here is not a benchmark number but a *capability*: "we support N
languages." Claim-Oriented Programming registers that count, backs it with an
artifact listing the languages, and binds the doc to it — so the README can
never say "8 languages" while the code supports 6.
"""
from __future__ import annotations

GREETINGS: dict[str, str] = {
    "en": "Hello",
    "no": "Hei",
    "es": "Hola",
    "fr": "Bonjour",
    "de": "Hallo",
    "ja": "こんにちは",
}


def greet(name: str, lang: str = "en") -> str:
    """Greet *name* in *lang*, falling back to English for unknown languages."""
    word = GREETINGS.get(lang, GREETINGS["en"])
    return f"{word}, {name}!"


def supported_languages() -> list[str]:
    """The language codes we can greet in."""
    return sorted(GREETINGS)
