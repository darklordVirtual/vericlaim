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


def _strip_inline_comment(value: str) -> str:
    """Drop a trailing YAML inline comment (whitespace + ``#``), respecting quotes.

    PyYAML treats ` #...` as a comment; the bundled parser must agree, or the
    same register parses to different values depending on whether PyYAML happens
    to be installed (and a value like ``2.5  # ratio`` would parse to a string
    that later crashes numeric checks). A ``#`` with no preceding whitespace, or
    one inside quotes, is part of the scalar and is preserved.
    """
    s = value.strip()
    if not s:
        return s
    if s[0] in "\"'":
        end = s.find(s[0], 1)
        if end == -1:
            return s  # unterminated quote — leave untouched
        head, tail = s[: end + 1], s[end + 1:]
        m = re.search(r"\s#", tail)
        return (head + (tail[: m.start()] if m else tail)).strip()
    m = re.search(r"\s#", s)
    return (s[: m.start()] if m else s).strip()


def _scalar(value: str) -> Any:
    value = _strip_inline_comment(value.strip())
    if value in ("null", "~", ""):
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    # The bundled parser implements block style only. An UNQUOTED value opening a
    # flow collection ('[a, b]', '{k: v}', or a malformed '[broken') is NOT valid
    # here — reject it (fail closed) instead of silently mis-reading it as a plain
    # string, which is fail-OPEN. Empty [] / {} are allowed; quote the value if you
    # really mean a literal starting with a bracket. (With PyYAML installed, full
    # flow syntax is supported and this path is not used.)
    if value[0] in "[{" and value not in ("[]", "{}"):
        raise RegisterError(
            f"unsupported flow collection {value!r}: the zero-dependency parser "
            f"uses block style only. Rewrite in block style, quote a literal "
            f"bracket, or install PyYAML for full YAML support.")
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
                maps: list[dict[str, Any]] = []
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    # `- key: value` opens a map item (list of maps, e.g.
                    # `literature:` entries); 8-space `key: value` lines
                    # continue it. Checked before the plain-item pattern,
                    # which would otherwise swallow `- source: x` whole.
                    dm = re.match(r"^      - (\w+):\s*(.*)$", nxt)
                    cm = re.match(r"^        (\w+):\s*(.*)$", nxt)
                    lm = re.match(r"^      - (.+)$", nxt)
                    mm = re.match(r"^      (\w+):\s*(.+)$", nxt)
                    if dm:
                        maps.append({dm.group(1): _scalar(dm.group(2))})
                    elif cm and maps:
                        maps[-1][cm.group(1)] = _scalar(cm.group(2))
                    elif lm:
                        items.append(_strip_quotes(lm.group(1)))
                    elif mm:
                        mapping[mm.group(1)] = _scalar(mm.group(2))
                    elif not nxt.strip():
                        pass
                    else:
                        break
                    i += 1
                current[key] = maps if maps else (mapping if mapping else items)
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
