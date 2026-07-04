# SPDX-License-Identifier: Apache-2.0
"""Harvest gate-verified claims from a source repo into library bundles.

Honesty rules, enforced fail-closed:

- The source repo's OWN gate must pass at harvest time (``gate_cmd``); a red
  source refuses the whole harvest — the library only preserves claims that
  were verified where they were made.
- A foreign evidence level must have an explicit entry in ``level_map``; an
  unmapped level refuses. The mapping is curation policy, written down —
  never inferred, and by convention never an upgrade.
- The caveat is *extended* with harvest provenance (``caveat_extra``), never
  trimmed or replaced.
- Denylisted claims (``exclude`` — e.g. withdrawn material) are skipped.
- Every cited artifact must exist and is preserved byte-exact under
  ``artifacts/``; scripts named by the claim's ``reproduce`` command are
  preserved under ``code/``; curated literature notes under ``literature/``.

Usage (see mappings/*.toml for per-source configs):

    python3 integrations/library/harvest.py --source ~/REMORA-research \\
        --config integrations/library/mappings/remora.toml --out build/library
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundlefmt import build_bundle  # noqa: E402

VERICLAIM_LEVELS = {"theoretical", "measured", "benchmarked", "reproduced",
                    "machine_checked", "externally_validated"}


class HarvestError(ValueError):
    """The harvest cannot proceed honestly. Nothing is written."""


def _load_claims(register_text: str) -> list[dict]:
    """Full YAML when available (foreign registers use nested structures);
    vericlaim's own fail-closed subset parser otherwise."""
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(register_text) or {}
        claims = data.get("claims", []) if isinstance(data, dict) else []
        return [c for c in claims if isinstance(c, dict)]
    except ImportError:
        root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(root))
        from vericlaim.register import load_register
        return load_register(register_text)


def _git_commit(root: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _run_source_gate(src: Path, gate_cmd: str) -> None:
    proc = subprocess.run(shlex.split(gate_cmd), cwd=src,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise HarvestError(
            f"source gate failed ({gate_cmd!r} exited {proc.returncode}) — "
            f"refusing to harvest from a repo whose own claims do not "
            f"verify.\n{proc.stdout}{proc.stderr}")


def _map_level(level: str, level_map: dict[str, str]) -> str:
    if level in level_map:
        mapped = level_map[level]
        if mapped not in VERICLAIM_LEVELS:
            raise HarvestError(f"level_map maps {level!r} to unknown vericlaim "
                               f"level {mapped!r}")
        return mapped
    if level in VERICLAIM_LEVELS:
        return level  # native level, no mapping needed
    raise HarvestError(
        f"evidence level {level!r} has no entry in level_map and is not a "
        f"vericlaim level — refusing to guess a mapping")


def _reproduce_scripts(src: Path, reproduce: str | None) -> list[str]:
    """Repo-relative paths named by the reproduce command that exist on disk —
    the code that computes the claim, identified from the command itself."""
    if not reproduce:
        return []
    out = []
    for token in shlex.split(str(reproduce)):
        p = src / token
        if p.is_file():
            out.append(token)
    return out


def harvest_repo(src: Path, out_root: Path, cfg: dict) -> dict[str, str]:
    """Harvest all mappable claims from *src*; returns {claim_id: bundle_id}.

    Raises HarvestError (before writing anything) on a red source gate, an
    unmapped level, or a missing artifact — a partial library is a lie.
    """
    src = Path(src)
    reg_path = src / cfg["register"]
    if not reg_path.exists():
        raise HarvestError(f"source register not found: {reg_path}")
    if cfg.get("gate_cmd"):
        _run_source_gate(src, cfg["gate_cmd"])

    claims = _load_claims(reg_path.read_text(encoding="utf-8"))
    commit = _git_commit(src)
    level_map = cfg.get("level_map") or {}
    exclude = set(cfg.get("exclude") or [])
    literature = cfg.get("literature") or {}
    caveat_extra = (cfg.get("caveat_extra") or "").format(commit=commit[:12])

    # Validate everything first (fail closed), then write.
    prepared: list[tuple[dict, dict, dict[str, bytes]]] = []
    for c in claims:
        cid = c.get("id", "<missing-id>")
        if cid in exclude:
            continue
        level = _map_level(str(c.get("evidence_level")), level_map)
        arts = c.get("artifact") or c.get("artifacts") or []
        if isinstance(arts, str):
            arts = [arts]
        files: dict[str, bytes] = {}
        for rel in arts:
            p = src / rel
            if not p.is_file():
                raise HarvestError(f"{cid}: cited artifact missing in source "
                                   f"repo: {rel}")
            files[f"artifacts/{rel}"] = p.read_bytes()
        for rel in _reproduce_scripts(src, c.get("reproduce")):
            files[f"code/{rel}"] = (src / rel).read_bytes()
        for lit_path in literature.get(cid, []):
            lp = Path(lit_path)
            if not lp.is_file():
                raise HarvestError(f"{cid}: curated literature file missing: "
                                   f"{lit_path}")
            files[f"literature/{lp.name}"] = lp.read_bytes()
        # A native register's own hash-verified literature entries: preserve
        # the committed files so the bundle carries the claim's citations.
        reg_lit = c.get("literature") or []
        if isinstance(reg_lit, dict):
            reg_lit = [reg_lit]
        for entry in reg_lit:
            rel = entry.get("file") if isinstance(entry, dict) else None
            if not rel:
                continue
            p = src / rel
            if not p.is_file():
                raise HarvestError(f"{cid}: register literature file missing "
                                   f"in source repo: {rel}")
            files[f"literature/{rel}"] = p.read_bytes()

        caveat = str(c.get("caveat", "")).strip()
        if caveat_extra:
            caveat = f"{caveat} {caveat_extra}".strip()
        out_claim = {
            "id": cid,
            "statement": c.get("statement"),
            "evidence_level": level,
            "artifact": [f"artifacts/{rel}" for rel in arts],
            "caveat": caveat,
        }
        for opt in ("n", "metrics", "literature"):
            if c.get(opt) is not None:
                out_claim[opt] = c[opt]
        if c.get("reproduce"):
            out_claim["source_reproduce"] = c["reproduce"]

        prov = {
            "source_repo": cfg.get("repo", str(src)),
            "source_commit": commit,
            "source_claim_id": cid,
            "source_evidence_level": c.get("evidence_level"),
            "level_mapping": f"{c.get('evidence_level')}->{level}",
            "source_gate": "passed" if cfg.get("gate_cmd") else "not_run",
            "harvest_tool": "vericlaim-library harvest_v1",
        }
        prepared.append((out_claim, prov, files))

    results: dict[str, str] = {}
    for out_claim, prov, files in prepared:
        bid, _ = build_bundle(Path(out_root), claim=out_claim, provenance=prov,
                              files=files, status="verified")
        results[out_claim["id"]] = bid
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    cfg = tomllib.loads(args.config.read_text(encoding="utf-8"))
    # allow literature paths relative to the config file
    lit = {cid: [str((args.config.parent / p)) for p in paths]
           for cid, paths in (cfg.get("literature") or {}).items()}
    cfg["literature"] = lit
    results = harvest_repo(args.source, args.out, cfg)
    for cid, bid in results.items():
        print(f"[OK] {cid} -> {bid}")
    print(f"[OK] harvested {len(results)} claim(s) into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
