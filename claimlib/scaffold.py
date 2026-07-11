# SPDX-License-Identifier: Apache-2.0
"""Scaffold a new claim-bound claimlib module from a domain-flavored template.

VeriClaim as a code generator: pick a template shape, name your module and its
subject area, and this emits a ready-to-fill module + evidence + test that follow
the claimlib contract. It NEVER fabricates numbers -- the generated evidence
refuses to run until you replace its TODO reference battery with genuinely,
independently-known values -- and it NEVER edits MODULES.py or the register; it
prints the MODULES.py entry for you to paste once the evidence is real.

    python claimlib/scaffold.py <name> --template <kind> --domain "<Area>"
        [--claim-id <ID>] [--title "<Title>"] [--force]

Templates (see claimlib/templates/): validator, checksum, codec, calculator.

Workflow:
    1. scaffold            -> modules/<name>/{<name>.py, evidence.py} + tests/test_<name>.py
    2. implement <name>.py and a real reference battery in evidence.py
    3. add the claim anchor + the printed MODULES.py entry
    4. python claimlib/build.py  &&  python -m vericlaim --root claimlib
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"
TEMPLATE_KINDS = ("validator", "checksum", "codec", "calculator")
_BIND_FIELD = {
    "validator": "correct",
    "checksum": "reference_vectors_matched",
    "codec": "roundtrip_lossless",
    "calculator": "correct",
}


def _class_name(name: str) -> str:
    """foo_bar -> FooBarError (a valid, readable exception class name)."""
    parts = re.split(r"[^0-9a-zA-Z]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) + "Error"


def _substitute(text: str, mapping: dict) -> str:
    for key, value in mapping.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def _render(name: str, kind: str, domain: str, claim_id: str, title: str) -> dict:
    mapping = {
        "NAME": name,
        "CLAIM_ID": claim_id,
        "DOMAIN": domain,
        "TITLE": title,
        "CLASS": _class_name(name),
        "SCHEMA": f"claimlib_{name}_v1",
    }
    tdir = TEMPLATES / kind
    return {
        "module": _substitute((tdir / "module.py.tmpl").read_text(encoding="utf-8"), mapping),
        "evidence": _substitute((tdir / "evidence.py.tmpl").read_text(encoding="utf-8"), mapping),
        "test": _substitute((tdir / "test.py.tmpl").read_text(encoding="utf-8"), mapping),
    }


def _write_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def modules_entry(name: str, kind: str, domain: str, claim_id: str, title: str) -> str:
    """The MODULES.py dict to paste once the evidence is real (fill statement/caveat)."""
    return f'''    {{
        "name": "{name}",
        "lang": "python",
        "claim_id": "{claim_id}",
        "title": "{title}",
        "area": "{domain}",
        "evidence_level": "measured",
        "code_files": ["{name}.py"],
        "artifact": "{name}.json",
        "register_metrics": [ "..." ],
        "bind_field": "{_BIND_FIELD[kind]}",
        "statement": "TODO: state exactly what the evidence proved, with the numbers.",
        "caveat": "TODO: what is NOT proven; the reference is fixed, not exhaustive.",
        "knowledge": "TODO: what the primitive is and why vendoring it is useful."
    }},'''


def scaffold(name: str, kind: str, domain: str, claim_id: str, title: str,
             *, force: bool = False) -> list[Path]:
    rendered = _render(name, kind, domain, claim_id, title)
    mdir = HERE / "modules" / name
    targets = {
        mdir / f"{name}.py": rendered["module"],
        mdir / "evidence.py": rendered["evidence"],
        HERE / "tests" / f"test_{name}.py": rendered["test"],
    }
    existing = [p for p in targets if p.exists()]
    if existing and not force:
        raise SystemExit(f"[scaffold] refusing to overwrite: "
                         f"{', '.join(str(p) for p in existing)} (use --force)")
    for path, text in targets.items():
        _write_lf(path, text)
    return list(targets)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a claim-bound claimlib module.")
    parser.add_argument("name", help="module name (snake_case), e.g. sip_uri")
    parser.add_argument("--template", "-t", choices=TEMPLATE_KINDS, required=True)
    parser.add_argument("--domain", "-d", required=True,
                        help='subject area, e.g. "Telecom / Signalling"')
    parser.add_argument("--claim-id", help="claim id (default CLAIM-LIB-<NAME>-001)")
    parser.add_argument("--title", help="human title (default derived from name)")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args(argv)

    if not re.fullmatch(r"[a-z][a-z0-9_]*", args.name):
        raise SystemExit("[scaffold] name must be snake_case ([a-z][a-z0-9_]*)")
    claim_id = args.claim_id or f"CLAIM-LIB-{args.name.upper().replace('_', '-')}-001"
    title = args.title or args.name.replace("_", " ").title()

    written = scaffold(args.name, args.template, args.domain, claim_id, title, force=args.force)
    print("[scaffold] wrote:")
    for path in written:
        print(f"  {path.relative_to(HERE.parent)}")
    print("\n[scaffold] next: implement the module + a REAL reference battery in "
          "evidence.py\n(the generated evidence refuses to run until you do), then "
          "add the claim\nanchor and paste this into claimlib/MODULES.py:\n")
    print(modules_entry(args.name, args.template, args.domain, claim_id, title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
