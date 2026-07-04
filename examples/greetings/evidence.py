# SPDX-License-Identifier: Apache-2.0
"""Produce the evidence artifact for the greetings example.

Deterministic: it writes exactly what the code supports, so the number in the
docs is always the number the code can prove.

    python examples/greetings/evidence.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from greetings import greet, supported_languages  # noqa: E402


def main() -> int:
    langs = supported_languages()
    artifact = {
        "schema": "greetings_v1",
        "n_languages": len(langs),
        "languages": langs,
        "sample": {lang: greet("Ada", lang) for lang in langs},
    }
    out = Path(__file__).resolve().parent / "artifacts" / "greetings.json"
    out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"[OK] wrote {out}")
    print(f"     n_languages={len(langs)} ({', '.join(langs)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
