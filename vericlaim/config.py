# SPDX-License-Identifier: Apache-2.0
"""Configuration loading for the vericlaim gate.

Config lives in ``vericlaim.toml`` at the project root (or a path passed to the
CLI). Requires Python 3.11+ for the stdlib ``tomllib`` — no third-party deps.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    root: Path
    register: str = "claims/register.yaml"
    baseline: str = "claims/baseline.json"
    manifest: str | None = "claims/manifest.md"
    doc_globs: tuple[str, ...] = ("README.md", "docs/**/*.md")
    required_fields: tuple[str, ...] = (
        "id", "statement", "evidence_level", "artifact", "caveat",
    )
    evidence_levels: tuple[str, ...] = (
        "theoretical", "measured", "benchmarked", "reproduced",
        "externally_validated",
    )
    evidence_exclude: tuple[str, ...] = ()
    stale_exclude: tuple[str, ...] = ()
    stale_strings: tuple[tuple[str, str], ...] = ()
    # When true, every artifact a claim cites must carry a provenance sidecar
    # (<artifact>.provenance.json) recording how it was produced.
    require_provenance: bool = False
    # When true, every artifact must be tracked by git (a "committed artifact"
    # must actually be committed). Off by default so non-git checkouts and tests
    # still work; recommended on in CI.
    require_git_tracked: bool = False

    def path(self, rel: str) -> Path:
        return self.root / rel


DEFAULT_CONFIG_NAME = "vericlaim.toml"


def load_config(root: Path, config_path: Path | None = None) -> Config:
    """Load Config from ``vericlaim.toml``; fall back to defaults if absent."""
    cfg_path = config_path or (root / DEFAULT_CONFIG_NAME)
    if not cfg_path.exists():
        return Config(root=root)
    data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    v = data.get("vericlaim", {}) if isinstance(data, dict) else {}
    stale = v.get("stale_strings", {})
    stale_tuple = tuple(
        (str(k), str(val)) for k, val in stale.items()
    ) if isinstance(stale, dict) else ()

    def _tuple(key: str, default: tuple) -> tuple:
        val = v.get(key)
        return tuple(val) if isinstance(val, list) else default

    base = Config(root=root)
    return Config(
        root=root,
        register=str(v.get("register", base.register)),
        baseline=str(v.get("baseline", base.baseline)),
        manifest=(str(v["manifest"]) if "manifest" in v else base.manifest),
        doc_globs=_tuple("doc_globs", base.doc_globs),
        required_fields=_tuple("required_fields", base.required_fields),
        evidence_levels=_tuple("evidence_levels", base.evidence_levels),
        evidence_exclude=_tuple("evidence_exclude", base.evidence_exclude),
        stale_exclude=_tuple("stale_exclude", base.stale_exclude),
        stale_strings=stale_tuple,
        require_provenance=bool(v.get("require_provenance", base.require_provenance)),
        require_git_tracked=bool(v.get("require_git_tracked", base.require_git_tracked)),
    )
