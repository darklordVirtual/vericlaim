# SPDX-License-Identifier: Apache-2.0
"""Adversarial tests for the fail-closed hardening pass.

Each test attacks one of the review findings and proves the gate now fails
closed: declarative reproduce is covered by provenance and manifest coverage,
reproduce_outputs are bound to the claim's artifacts, a configured manifest
cannot vanish silently, strict refuses unestablishable metrics, the register
parser rejects malformed entries and wrong field types, the baseline cannot
absorb new occurrences of a baselined problem, and the reproduction runner
sees files hidden in subdirectories.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from vericlaim.config import Config
from vericlaim.gate import (
    _load_baseline,
    check_manifest,
    check_manifest_coverage,
    check_metrics_match_artifact,
    check_provenance,
    run as gate_run,
)
from vericlaim.register import RegisterError, load_register
from vericlaim.repro import ReproSpec, run_declarative


def _cfg(tmp: Path, **over) -> Config:
    return Config(root=tmp, **over)


def _declarative_claim(art: str = "results/x.json", **over) -> dict:
    claim = {
        "id": "CLAIM-D-001",
        "statement": "s",
        "evidence_level": "measured",
        "artifact": [art],
        "caveat": "c",
        "reproduce_argv": ["python3", "gen.py", "--output-dir", "{output_dir}"],
        "reproduce_outputs": [art],
    }
    claim.update(over)
    return claim


# ── P0-1: declarative claims are produced evidence, not static facts ────────

def test_declarative_claim_requires_provenance(tmp_path):
    art = tmp_path / "results" / "x.json"
    art.parent.mkdir()
    art.write_text('{"v": 1}')
    cfg = _cfg(tmp_path, require_provenance=True)
    ids = [e for e, _ in check_provenance([_declarative_claim()], cfg)]
    assert any(e.startswith("provenance-missing") for e in ids), ids


def test_declarative_claim_needs_manifest_coverage(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "manifest.md").write_text("| File | SHA-256 |\n")
    cfg = _cfg(tmp_path, manifest="claims/manifest.md")
    ids = [e for e, _ in check_manifest_coverage([_declarative_claim()], cfg)]
    assert any(e.startswith("manifest-uncovered") for e in ids), ids


def test_legacy_claim_still_covered(tmp_path):
    cfg = _cfg(tmp_path, require_provenance=True)
    claim = _declarative_claim()
    del claim["reproduce_argv"], claim["reproduce_outputs"]
    claim["reproduce"] = "python gen.py"
    art = tmp_path / "results" / "x.json"
    art.parent.mkdir()
    art.write_text('{"v": 1}')
    ids = [e for e, _ in check_provenance([claim], cfg)]
    assert any(e.startswith("provenance-missing") for e in ids)


# ── P0-2: reproduce_outputs must equal the claim's artifacts ────────────────

def _write_min_workspace(tmp: Path, claim: dict) -> None:
    (tmp / "claims").mkdir(exist_ok=True)
    (tmp / "vericlaim.toml").write_text(
        '[vericlaim]\nregister = "claims/register.yaml"\n')
    body = ["claims:"]
    body.append(f"  - id: {claim['id']}")
    body.append("    statement: >")
    body.append("      s")
    body.append(f"    evidence_level: {claim['evidence_level']}")
    body.append("    artifact:")
    for a in claim["artifact"]:
        body.append(f"      - {a}")
    body.append("    caveat: >")
    body.append("      c")
    body.append("    reproduce_argv:")
    for a in claim["reproduce_argv"]:
        body.append(f'      - "{a}"')
    body.append("    reproduce_outputs:")
    for o in claim["reproduce_outputs"]:
        body.append(f"      - {o}")
    (tmp / "claims" / "register.yaml").write_text("\n".join(body) + "\n")


def test_reproduce_outputs_must_match_artifacts(tmp_path, capsys):
    from vericlaim.reproduce import reproduce

    claim = _declarative_claim(
        art="results/real.json",
        reproduce_outputs=["results/unrelated.json"])
    _write_min_workspace(tmp_path, claim)
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "real.json").write_text("{}")
    cfg = _cfg(tmp_path)
    rc = reproduce(cfg, quiet=True)
    out = capsys.readouterr().out
    assert rc == 1
    assert "reproduce_outputs must equal" in out


# ── P0-3: a configured manifest cannot vanish silently ──────────────────────

def test_missing_configured_manifest_fails(tmp_path):
    cfg = _cfg(tmp_path, manifest="claims/manifest.md")
    ids = [e for e, _ in check_manifest(cfg, notes=[])]
    assert any(e.startswith("manifest-missing") for e in ids)


def test_unset_manifest_is_explicitly_off_under_adopt(tmp_path):
    cfg = _cfg(tmp_path, manifest=None)
    assert check_manifest(cfg, notes=[]) == []
    assert check_manifest_coverage([_declarative_claim()], cfg) == []


def test_strict_requires_manifest_for_reproducible_claims(tmp_path):
    cfg = _cfg(tmp_path, manifest=None, profile="strict")
    ids = [e for e, _ in check_manifest_coverage([_declarative_claim()], cfg)]
    assert any(e.startswith("manifest-required") for e in ids)
    # ...but not when nothing is reproducible.
    static = {"id": "C", "artifact": ["a.json"]}
    assert check_manifest_coverage([static], cfg) == []


# ── strict metrics: absent keys are findings, not skips ─────────────────────

def _metric_claim(tmp: Path, artifact_payload: dict) -> dict:
    art = tmp / "results" / "m.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(artifact_payload))
    return {"id": "CLAIM-M-001", "artifact": ["results/m.json"],
            "metrics": {"latency_ms": 42}}


def test_missing_metric_key_skipped_under_adopt(tmp_path):
    claim = _metric_claim(tmp_path, {"unrelated": 1})
    assert check_metrics_match_artifact([claim], _cfg(tmp_path)) == []


def test_missing_metric_key_fails_under_strict(tmp_path):
    claim = _metric_claim(tmp_path, {"unrelated": 1})
    ids = [e for e, _ in check_metrics_match_artifact(
        [claim], _cfg(tmp_path, profile="strict"))]
    assert any(e.startswith("metrics-key-missing") for e in ids)


def test_present_but_wrong_metric_fails_under_any_profile(tmp_path):
    claim = _metric_claim(tmp_path, {"latency_ms": 41})
    ids = [e for e, _ in check_metrics_match_artifact([claim], _cfg(tmp_path))]
    assert any(e.startswith("metrics-artifact-mismatch") for e in ids)


# ── register parser: malformed entries and wrong types fail closed ──────────

@pytest.mark.parametrize("text", [
    "claims: [oops]\n",
    "claims:\n  - malformed-entry\n",
    "claims:\n  - 42\n",
    "claims: not-a-list\n",
])
def test_malformed_claim_entries_raise(text):
    pytest.importorskip("yaml")
    with pytest.raises(RegisterError):
        load_register(text)


@pytest.mark.parametrize("snippet", [
    "    id: [CLAIM, LIST]\n",
    "    id: 42\n",
])
def test_non_string_id_raises(snippet):
    pytest.importorskip("yaml")
    text = ("claims:\n  -\n" + snippet
            + "    statement: s\n    evidence_level: measured\n"
              "    artifact: [a.json]\n    caveat: c\n")
    with pytest.raises(RegisterError):
        load_register(text)


def test_wrong_field_types_raise():
    pytest.importorskip("yaml")
    base = ("claims:\n  - id: CLAIM-T-001\n    statement: s\n"
            "    evidence_level: measured\n    caveat: c\n")
    for bad in ("    artifact: {a: b}\n",
                "    artifact: [1, 2]\n",
                "    metrics: [1]\n",
                "    reproduce_argv: python gen.py\n",
                "    reproduce_argv: [python, 42]\n",
                "    reproduce_outputs: results/x.json\n",
                "    literature: [just-a-string]\n"):
        with pytest.raises(RegisterError):
            load_register(base + bad)


def test_valid_shapes_still_load():
    text = ("claims:\n  - id: CLAIM-OK-001\n    statement: s\n"
            "    evidence_level: measured\n    artifact:\n      - a.json\n"
            "    caveat: c\n    metrics:\n      x: 1\n"
            "    reproduce_argv:\n      - python3\n      - gen.py\n"
            "    reproduce_outputs:\n      - a.json\n")
    claims = load_register(text)
    assert claims[0]["id"] == "CLAIM-OK-001"


# ── baseline: a baselined id cannot absorb NEW occurrences ───────────────────

def _workspace_with_stale_strings(tmp: Path, occurrences: int,
                                  baseline_count: int | None) -> Config:
    (tmp / "claims").mkdir(parents=True)
    (tmp / "claims" / "register.yaml").write_text("claims:\n")
    entry: dict = {"error_id": "stale-string:README.md:forbidden",
                   "reason": "grandfathered"}
    if baseline_count is not None:
        entry["count"] = baseline_count
    (tmp / "claims" / "baseline.json").write_text(
        json.dumps({"known_violations": [entry]}))
    (tmp / "README.md").write_text("forbidden\n" * occurrences)
    return _cfg(tmp, doc_globs=("README.md",),
                stale_strings=(("forbidden", "corrected wording"),))


def test_baseline_grandfathers_exactly_one_occurrence(tmp_path, capsys):
    cfg = _workspace_with_stale_strings(tmp_path, occurrences=1,
                                        baseline_count=None)
    assert gate_run(cfg, quiet=True) == 0
    cfg2 = _workspace_with_stale_strings(tmp_path / "two", 2, None)
    assert gate_run(cfg2, quiet=True) == 1  # the SECOND occurrence is new


def test_baseline_count_extends_allowance(tmp_path):
    cfg = _workspace_with_stale_strings(tmp_path, occurrences=2,
                                        baseline_count=2)
    assert gate_run(cfg, quiet=True) == 0
    cfg2 = _workspace_with_stale_strings(tmp_path / "three", 3, 2)
    assert gate_run(cfg2, quiet=True) == 1


def test_baseline_invalid_count_rejected(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "baseline.json").write_text(
        json.dumps({"known_violations": [
            {"error_id": "x", "count": 0}]}))
    with pytest.raises(RegisterError):
        _load_baseline(_cfg(tmp_path))


# ── reproduction runner: subdirectory files are undeclared outputs ───────────

def _spec_for(tmp: Path, script: str, outputs: list[str]) -> ReproSpec:
    gen = tmp / "gen.py"
    gen.write_text(script, encoding="utf-8")
    return ReproSpec.parse(
        {"argv": [sys.executable, str(gen), "{output_dir}"],
         "outputs": outputs},
        allow_legacy_shell=False)


def test_repro_flags_file_hidden_in_subdir(tmp_path):
    committed = tmp_path / "out.json"
    committed.write_text('{"v": 1}', encoding="utf-8", newline="\n")
    script = (
        "import sys, pathlib\n"
        "d = pathlib.Path(sys.argv[1])\n"
        "(d / 'out.json').write_text('{\"v\": 1}', encoding='utf-8', newline='\\n')\n"
        "(d / 'hidden').mkdir()\n"
        "(d / 'hidden' / 'sneaky.txt').write_text('x')\n")
    res = run_declarative(_cfg(tmp_path), _spec_for(tmp_path, script, ["out.json"]))
    assert not res.ok
    assert "undeclared" in res.reason


def test_repro_clean_run_passes(tmp_path):
    committed = tmp_path / "out.json"
    committed.write_text('{"v": 1}', encoding="utf-8", newline="\n")
    script = (
        "import sys, pathlib\n"
        "d = pathlib.Path(sys.argv[1])\n"
        "(d / 'out.json').write_text('{\"v\": 1}', encoding='utf-8', newline='\\n')\n")
    res = run_declarative(_cfg(tmp_path), _spec_for(tmp_path, script, ["out.json"]))
    assert res.ok, res.reason
    assert "out.json" in res.output_sha256
    assert res.output_sha256["out.json"] == hashlib.sha256(
        committed.read_bytes()).hexdigest()
