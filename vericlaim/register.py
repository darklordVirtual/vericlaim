# SPDX-License-Identifier: Apache-2.0
"""Zero-dependency parser for the claim register (a restricted YAML subset).

The register is intentionally parseable without PyYAML so the gate has no
third-party supply-chain surface — a gate you must trust should not itself pull
in dependencies. The supported subset is small and documented in
docs/claim-register-spec.md:

    claims:
      - id: CLAIM-001                 # scalar fields
        statement: >                  # folded block scalar (joined with spaces)
          multi-line text ...
        evidence_level: measured
        artifact:                     # string list
          - results/x.json
        metrics:                      # one-level map of name -> number
          ratio: 2.5
        caveat: "one line, or a > block"

If your register needs richer YAML, install PyYAML and it will be used
automatically (see load_register); otherwise this parser handles the subset.
"""
from __future__ import annotations

import re
from typing import Any


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _scalar(value: str) -> Any:
    value = value.strip()
    if value in ("null", "~", ""):
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    unquoted = _strip_quotes(value)
    if unquoted != value:
        return unquoted
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _parse_subset(text: str) -> list[dict]:
    """Parse the restricted subset into a list of claim dicts."""
    claims: list[dict] = []
    current: dict | None = None
    lines = text.splitlines()
    i = 0
    in_claims = False
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            i += 1
            continue
        if not in_claims:
            if re.match(r"^claims:\s*$", line):
                in_claims = True
            i += 1
            continue

        item = re.match(r"^  - (\w+):\s*(.*)$", line)
        if item:
            current = {item.group(1): _scalar(item.group(2))}
            claims.append(current)
            i += 1
            continue

        field = re.match(r"^    (\w+):\s*(.*)$", line)
        if field and current is not None:
            key, value = field.group(1), field.group(2).strip()
            if value in (">", "|", ">-", "|-"):
                block: list[str] = []
                i += 1
                while i < len(lines) and (not lines[i].strip() or lines[i].startswith("      ")):
                    if lines[i].strip():
                        block.append(lines[i].strip())
                    i += 1
                current[key] = " ".join(block)
                continue
            if value == "":
                items: list[str] = []
                mapping: dict[str, Any] = {}
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    lm = re.match(r"^      - (.+)$", nxt)
                    mm = re.match(r"^      (\w+):\s*(.+)$", nxt)
                    if lm:
                        items.append(_strip_quotes(lm.group(1)))
                    elif mm:
                        mapping[mm.group(1)] = _scalar(mm.group(2))
                    elif not nxt.strip():
                        pass
                    else:
                        break
                    i += 1
                current[key] = mapping if mapping else items
                continue
            current[key] = _scalar(value)
            i += 1
            continue
        i += 1
    return claims


def load_register(text: str) -> list[dict]:
    """Parse the register. Uses PyYAML when available, else the bundled subset."""
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        claims = data.get("claims", []) if isinstance(data, dict) else []
        return [c for c in claims if isinstance(c, dict)]
    except Exception:
        return _parse_subset(text)
