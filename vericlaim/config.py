# SPDX-License-Identifier: Apache-2.0
"""Configuration loading for the vericlaim gate.

Config lives in ``vericlaim.toml`` at the project root (or a path passed to the
CLI). Requires Python 3.11+ for the stdlib ``tomllib`` — no third-party deps.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


PROFILES = ("adopt", "strict", "enterprise")


@dataclass(frozen=True)
class Config:
    root: Path
    # Policy profile. `adopt` is intentionally permissive for onboarding; `strict`
    # is the recommended production destination (secure by default); `enterprise`
    # adds regulated-tier controls (signing/attestation — see the profiles doc).
    profile: str = "adopt"
    # Legacy string `reproduce` shell commands: an explicit opt-in, honored only
    # under `adopt`. strict/enterprise force this False (no unstructured shell).
    allow_legacy_shell: bool = False
    register: str = "claims/register.yaml"
    baseline: str = "claims/baseline.json"
    manifest: str | None = "claims/manifest.md"
    doc_globs: tuple[str, ...] = ("README.md", "docs/**/*.md")
    # Source files scanned for claim anchors in comments (`# claim:ID field`).
    # Off by default: code binding is opt-in per project.
    code_globs: tuple[str, ...] = ()
    required_fields: tuple[str, ...] = (
        "id", "statement", "evidence_level", "artifact", "caveat",
    )
    evidence_levels: tuple[str, ...] = (
        "theoretical", "measured", "benchmarked", "reproduced",
        "machine_checked", "externally_validated",
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

    @property
    def strict_mode(self) -> bool:
        """True under strict/enterprise — the secure-by-default profiles."""
        return self.profile in ("strict", "enterprise")

    @property
    def legacy_shell_allowed(self) -> bool:
        """Legacy shell reproduce is allowed ONLY when explicitly opted in AND
        the profile is not strict/enterprise. CI in strict mode can never run it."""
        return self.allow_legacy_shell and not self.strict_mode


DEFAULT_CONFIG_NAME = "vericlaim.toml"


def load_config(root: Path, config_path: Path | None = None,
                profile_override: str | None = None) -> Config:
    """Load Config from ``vericlaim.toml``; fall back to defaults if absent.

    *profile_override* (from ``--profile``) wins over the file. Under strict or
    enterprise, security controls are forced on (secure by default): provenance
    and git-tracking required, legacy shell reproduction disabled — regardless of
    what the file requests.
    """
    cfg_path = config_path or (root / DEFAULT_CONFIG_NAME)
    if not cfg_path.exists():
        base_profile = profile_override or "adopt"
        strict = base_profile in ("strict", "enterprise")
        return Config(root=root, profile=base_profile,
                      require_provenance=strict, require_git_tracked=strict)
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
    profile = profile_override or str(v.get("profile", base.profile))
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}; expected one of {PROFILES}")
    strict = profile in ("strict", "enterprise")
    # Secure by default: strict/enterprise force the security controls on and
    # forbid legacy shell, no matter what the file says.
    return Config(
        root=root,
        profile=profile,
        allow_legacy_shell=(False if strict else bool(v.get("allow_legacy_shell", False))),
        register=str(v.get("register", base.register)),
        baseline=str(v.get("baseline", base.baseline)),
        manifest=(str(v["manifest"]) if "manifest" in v else base.manifest),
        doc_globs=_tuple("doc_globs", base.doc_globs),
        code_globs=_tuple("code_globs", base.code_globs),
        required_fields=_tuple("required_fields", base.required_fields),
        evidence_levels=_tuple("evidence_levels", base.evidence_levels),
        evidence_exclude=_tuple("evidence_exclude", base.evidence_exclude),
        stale_exclude=_tuple("stale_exclude", base.stale_exclude),
        stale_strings=stale_tuple,
        require_provenance=(True if strict else bool(v.get("require_provenance", base.require_provenance))),
        require_git_tracked=(True if strict else bool(v.get("require_git_tracked", base.require_git_tracked))),
    )
