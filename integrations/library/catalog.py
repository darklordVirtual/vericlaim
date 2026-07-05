# SPDX-License-Identifier: Apache-2.0
"""Generate a human-readable Markdown catalog of the claims library.

Reads the authoritative /ledger/export, keeps ONLY the latest version per
identity (source_repo, source_claim_id) — no duplicates — and renders
grouped Markdown tables: one section per source repo, with reference
claims split into their own bibliography table.

    python3 integrations/library/catalog.py \\
        --url https://<worker>.workers.dev --out presentation/library-catalog.md
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REF_RE = re.compile(r"^(.*?) \((\d{4}|None)\) is a registrar-verified work "
                    r"\(([^)]+)\)")


def _get(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"user-agent": "vericlaim-catalog/1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def latest_rows(export: dict) -> list[dict]:
    seen: dict[tuple, dict] = {}
    for row in export.get("library", []):   # seq ascending -> last wins
        seen[(row["source_repo"], row["source_claim_id"])] = row
    return sorted(seen.values(),
                  key=lambda r: (r["source_repo"], r["source_claim_id"]))


def _short(text: str, n: int = 110) -> str:
    text = " ".join(str(text).split()).replace("|", "\\|")
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def render(rows: list[dict], url: str) -> str:
    by_repo: dict[str, list[dict]] = {}
    for r in rows:
        by_repo.setdefault(r["source_repo"], []).append(r)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out = [
        "# Claims-biblioteket — katalog",
        "",
        f"Generert fra `{url}/ledger/export` {ts} av "
        "`integrations/library/catalog.py` — **kun nyeste versjon per claim** "
        "(supersederte versjoner ligger i ledgeren som historikk). "
        f"Unike oppføringer: **{len(rows)}** fra {len(by_repo)} kilderepoer. "
        "Regenerér fremfor å håndredigere.",
        "",
    ]
    for repo, items in sorted(by_repo.items()):
        claims = [r for r in items
                  if not r["source_claim_id"].startswith("REF-")]
        refs = [r for r in items if r["source_claim_id"].startswith("REF-")]
        out.append(f"## {repo} — {len(items)} oppføringer")
        out.append("")
        if claims:
            out.append("| Claim | Nivå | Påstand |")
            out.append("|---|---|---|")
            for r in claims:
                c = json.loads(r["claim"])
                out.append(f"| `{c.get('id', '?')}` "
                           f"| {c.get('evidence_level', '?')} "
                           f"| {_short(c.get('statement', ''))} |")
            out.append("")
        if refs:
            out.append(f"### Registrar-verifiserte referanser ({len(refs)})")
            out.append("")
            out.append("| Ref | Verk | År | Registrar-ID |")
            out.append("|---|---|---|---|")
            for r in refs:
                c = json.loads(r["claim"])
                m = REF_RE.match(str(c.get("statement", "")))
                title, year, wid = (m.groups() if m
                                    else (_short(c.get("statement", ""), 70),
                                          "?", "?"))
                out.append(f"| `{c.get('id', '?')}` | {_short(title, 80)} "
                           f"| {year} | `{wid}` |")
            out.append("")
    out.append("---")
    out.append("*Hver oppføring er en claim med committet artefakt i "
               "kilderepoet; caveats og evidens ligger i bundlen "
               "(`/library/bundle/<id>`), historikk i `/library/versions`. "
               "Kandidat-status finnes ikke i denne katalogen — alle "
               "oppføringer er `verified`.*")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    export = _get(args.url.rstrip("/") + "/ledger/export")
    rows = latest_rows(export)
    args.out.write_text(render(rows, args.url.rstrip("/")), encoding="utf-8")
    statuses = {r["status"] for r in rows}
    print(f"[OK] {len(rows)} unike oppføringer -> {args.out} "
          f"(statuser: {sorted(statuses)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
