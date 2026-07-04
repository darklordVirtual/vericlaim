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

SUPPORTED_SCHEMA_VERSIONS = {"1"}


class RegisterError(ValueError):
    """The register could not be parsed. The gate treats this as a hard failure
    (fail closed) rather than silently seeing zero claims."""


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


_ITEM_ID_RE = re.compile(r"^\s*-\s+id:", re.MULTILINE)


def _check_schema_version(text: str) -> None:
    m = re.search(r"^\s*schema_version:\s*[\"']?([^\"'\s#]+)", text, re.MULTILINE)
    if m and m.group(1) not in SUPPORTED_SCHEMA_VERSIONS:
        raise RegisterError(
            f"unsupported schema_version {m.group(1)!r} "
            f"(supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)})")


def load_register(text: str) -> list[dict]:
    """Parse the register — FAIL CLOSED.

    Uses PyYAML when installed, else the bundled subset parser. Either way, a
    file that *looks* like it has claims (contains ``- id:`` items) but parses
    to zero is a misparse and raises RegisterError, so a formatting mistake can
    never silently disable the gate. A genuinely empty register (``claims: []``)
    is fine and returns [].
    """
    _check_schema_version(text)
    n_items = len(_ITEM_ID_RE.findall(text))

    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    if yaml is not None:
        try:
            data = yaml.safe_load(text) or {}
        except yaml.YAMLError as exc:  # real parse error → fail closed
            raise RegisterError(f"invalid YAML: {exc}") from exc
        claims = data.get("claims", []) if isinstance(data, dict) else []
        claims = [c for c in claims if isinstance(c, dict)]
    else:
        claims = _parse_subset(text)

    if n_items > 0 and len(claims) < n_items:
        raise RegisterError(
            f"register has {n_items} '- id:' item(s) but only {len(claims)} "
            f"parsed — a formatting error would otherwise silently disable the "
            f"gate. Fix the register (or install PyYAML for full YAML support).")
    return claims
