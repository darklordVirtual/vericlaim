# SPDX-License-Identifier: Apache-2.0
"""Tests for the Design-by-Contract layer: preconditions, lifecycle, blindness,
rate honesty, inheritance variance, coverage, the ratchet and the capability
contract.

Every mechanism gets a POSITIVE case (a well-formed register passes) and a
NEGATIVE case (the violation it exists to catch actually fails). A check with
only a positive test proves nothing: the tests would still pass if the check
returned an empty list unconditionally.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import pytest

from vericlaim.config import Config, load_config
from vericlaim.contract import (check_assumes, check_blindness, check_inheritance,
                                check_lifecycle, check_rates, rate_pairs,
                                retired_denylist, superseded_ids, wilson_upper)
from vericlaim.coverage import report, scan_text
from vericlaim.gate import (check_rate_anchor_pairing, check_retired_values,
                            check_superseded_anchors)
from vericlaim.ratchet import check as ratchet_check
from vericlaim.ratchet import measure as ratchet_measure
from vericlaim.register import RegisterError, load_register
from vericlaim.truth import check_capability_claims, check_roadmap_classified


def cfg_for(tmp_path: Path, **kw) -> Config:
    return Config(root=tmp_path, **kw)


# ── assumes: the claim's precondition ─────────────────────────────────────

def _claim_with_evidence(tmp_path: Path, payload: dict) -> dict:
    (tmp_path / "results").mkdir(exist_ok=True)
    (tmp_path / "results" / "e.json").write_text(json.dumps(payload),
                                                 encoding="utf-8")
    return {"id": "C-1", "artifact": ["results/e.json"], "metrics": {"x": 1}}


def test_assumes_pointer_holds(tmp_path):
    claim = _claim_with_evidence(tmp_path, {"dataset": "corpus-a"})
    claim["assumes"] = [{"key": "dataset", "value": "corpus-a",
                         "pointer": "/dataset"}]
    assert check_assumes([claim], cfg_for(tmp_path)) == []


def test_assumes_violation_is_caught(tmp_path):
    """The precondition is the point: evidence measured outside the declared
    scope must fail, which prose in `caveat` can never do."""
    claim = _claim_with_evidence(tmp_path, {"dataset": "corpus-b"})
    claim["assumes"] = [{"key": "dataset", "value": "corpus-a",
                         "pointer": "/dataset"}]
    findings = check_assumes([claim], cfg_for(tmp_path))
    assert len(findings) == 1
    assert findings[0][0].startswith("assumes-violated:")


def test_assumes_unresolvable_pointer_fails_closed(tmp_path):
    claim = _claim_with_evidence(tmp_path, {"dataset": "corpus-a"})
    claim["assumes"] = [{"key": "seed", "value": "1", "pointer": "/nope"}]
    findings = check_assumes([claim], cfg_for(tmp_path))
    assert findings and "unresolved" in findings[0][0]


def test_require_assumes_forces_machine_readable_scope(tmp_path):
    claim = _claim_with_evidence(tmp_path, {"x": 1})
    assert check_assumes([claim], cfg_for(tmp_path)) == []
    findings = check_assumes([claim], cfg_for(tmp_path, require_assumes=True))
    assert findings and findings[0][0].startswith("assumes-missing:")


def test_enterprise_profile_forces_require_assumes(tmp_path):
    (tmp_path / "vericlaim.toml").write_text(
        '[vericlaim]\nrequire_assumes = false\n', encoding="utf-8")
    cfg = load_config(tmp_path, profile_override="enterprise")
    assert cfg.require_assumes is True


# ── lifecycle ─────────────────────────────────────────────────────────────

def test_superseded_claim_must_name_its_replacement(tmp_path):
    claims = [{"id": "C-1", "status": "superseded"}]
    findings = check_lifecycle(claims, cfg_for(tmp_path))
    assert findings and findings[0][0].startswith("superseded-no-replacement:")


def test_superseded_by_must_resolve(tmp_path):
    claims = [{"id": "C-1", "status": "superseded", "superseded_by": "C-9"}]
    findings = check_lifecycle(claims, cfg_for(tmp_path))
    assert findings[0][0].startswith("superseded-unknown-replacement:")


def test_valid_supersession_passes(tmp_path):
    claims = [{"id": "C-1", "status": "superseded", "superseded_by": "C-2"},
              {"id": "C-2", "status": "active"}]
    assert check_lifecycle(claims, cfg_for(tmp_path)) == []
    assert superseded_ids(claims) == {"C-1"}


def test_unknown_status_fails(tmp_path):
    findings = check_lifecycle([{"id": "C-1", "status": "retired"}],
                               cfg_for(tmp_path))
    assert findings[0][0].startswith("status-unknown:")


def test_retired_values_become_a_derived_denylist(tmp_path):
    claims = [{"id": "C-1", "retired_values": ["8.0584x"]}]
    deny = retired_denylist(claims)
    assert deny and deny[0][0] == "8.0584x"
    doc = tmp_path / "README.md"
    doc.write_text("we still say 8.0584x here\n", encoding="utf-8")
    findings = check_retired_values(cfg_for(tmp_path), doc,
                                    doc.read_text(encoding="utf-8"), deny)
    assert findings and findings[0][0].startswith("retired-value:")


def test_retired_values_honour_stale_exclude(tmp_path):
    doc = tmp_path / "history.md"
    doc.write_text("historically 8.0584x\n", encoding="utf-8")
    cfg = cfg_for(tmp_path, stale_exclude=("history.md",))
    assert check_retired_values(cfg, doc, doc.read_text(encoding="utf-8"),
                                [("8.0584x", "why")]) == []


def test_superseded_claim_may_not_be_anchored_on_the_front_page(tmp_path):
    doc = tmp_path / "README.md"
    doc.write_text("<!-- claim:C-1 x -->\nvalue 1\n", encoding="utf-8")
    cfg = cfg_for(tmp_path, front_page=("README.md",))
    findings = check_superseded_anchors(cfg, doc, doc.read_text(encoding="utf-8"),
                                        {"C-1"})
    assert findings and findings[0][0].startswith("superseded-on-front-page:")


def test_superseded_anchor_is_allowed_off_the_front_page(tmp_path):
    doc = tmp_path / "docs" / "archive.md"
    doc.parent.mkdir()
    doc.write_text("<!-- claim:C-1 x -->\nvalue 1\n", encoding="utf-8")
    cfg = cfg_for(tmp_path, front_page=("README.md",))
    assert check_superseded_anchors(cfg, doc, doc.read_text(encoding="utf-8"),
                                    {"C-1"}) == []


# ── blindness: a sealed set is spent after one use ────────────────────────

def test_blind_claim_requires_a_sealed_set(tmp_path):
    findings = check_blindness([{"id": "C-1", "blindness": "blind"}],
                               cfg_for(tmp_path))
    assert findings[0][0].startswith("blind-no-sealed-set:")


def test_two_active_claims_may_not_share_a_sealed_set(tmp_path):
    claims = [{"id": "C-1", "blindness": "blind", "sealed_set": "bfcl-v4"},
              {"id": "C-2", "blindness": "blind", "sealed_set": "bfcl-v4"}]
    findings = check_blindness(claims, cfg_for(tmp_path))
    assert findings and findings[0][0].startswith("sealed-set-reused:")


def test_a_superseded_round_may_keep_its_sealed_set(tmp_path):
    """The set was spent by the older round; archiving it must not be a
    finding, or supersession would be punished instead of encouraged."""
    claims = [{"id": "C-1", "blindness": "blind", "sealed_set": "s",
               "status": "superseded", "superseded_by": "C-2"},
              {"id": "C-2", "blindness": "blind", "sealed_set": "s"}]
    assert check_blindness(claims, cfg_for(tmp_path)) == []


# ── rate honesty ──────────────────────────────────────────────────────────

def test_wilson_upper_does_not_certify_zero_from_a_small_sample():
    """The whole reason for Wilson over the normal approximation: at p=0 the
    normal interval is [0, 0] and would licence '0% failures, guaranteed'."""
    assert wilson_upper(0, 70) > Decimal("0.05")
    assert wilson_upper(0, 500) < wilson_upper(0, 70)
    assert Decimal(0) <= wilson_upper(3, 10) <= Decimal(1)


def test_wilson_upper_rejects_empty_sample():
    with pytest.raises(ValueError):
        wilson_upper(0, 0)


def _rate_claim(**metrics) -> dict:
    return {"id": "C-1", "metrics": metrics,
            "rate": {"metric": "far_pct", "bound_metric": "far_upper_pct",
                     "successes": 0, "n": 500}}


def test_rate_claim_with_correct_bound_passes(tmp_path):
    upper = wilson_upper(0, 500) * 100
    claim = _rate_claim(far_pct=0.0, far_upper_pct=float(round(upper, 2)))
    assert check_rates([claim], cfg_for(tmp_path)) == []


def test_rate_claim_without_a_bound_metric_fails(tmp_path):
    claim = _rate_claim(far_pct=0.0)
    claim["rate"].pop("bound_metric")
    findings = check_rates([claim], cfg_for(tmp_path))
    assert findings[0][0].startswith("rate-no-bound:")


def test_rate_claim_with_an_understated_bound_fails(tmp_path):
    claim = _rate_claim(far_pct=0.0, far_upper_pct=0.01)
    findings = check_rates([claim], cfg_for(tmp_path))
    assert findings and findings[0][0].startswith("rate-mismatch:")


def test_rate_claim_with_impossible_sample_fails(tmp_path):
    claim = _rate_claim(far_pct=0.0, far_upper_pct=0.76)
    claim["rate"]["successes"] = 501
    findings = check_rates([claim], cfg_for(tmp_path))
    assert findings[0][0].startswith("rate-invalid-sample:")


def test_anchor_may_not_quote_a_rate_without_its_bound(tmp_path):
    doc = tmp_path / "README.md"
    doc.write_text("<!-- claim:C-1 far_pct -->\n0.0% of calls\n", encoding="utf-8")
    pairs = rate_pairs([_rate_claim(far_pct=0.0, far_upper_pct=0.76)])
    findings = check_rate_anchor_pairing(cfg_for(tmp_path), doc,
                                          doc.read_text(encoding="utf-8"), pairs)
    assert findings and findings[0][0].startswith("rate-bound-unquoted:")


def test_anchor_quoting_both_passes(tmp_path):
    doc = tmp_path / "README.md"
    doc.write_text("<!-- claim:C-1 far_pct far_upper_pct -->\n0.0% (<=0.76%)\n",
                   encoding="utf-8")
    pairs = rate_pairs([_rate_claim(far_pct=0.0, far_upper_pct=0.76)])
    assert check_rate_anchor_pairing(cfg_for(tmp_path), doc,
                                      doc.read_text(encoding="utf-8"), pairs) == []


# ── inheritance variance ──────────────────────────────────────────────────

def _bundle(tmp_path: Path, level: str) -> str:
    d = tmp_path / "bundles" / "abc"
    d.mkdir(parents=True)
    claim = json.dumps({"id": "SRC-1", "evidence_level": level})
    (d / "claim.json").write_text(claim, encoding="utf-8", newline="\n")
    sha = hashlib.sha256((d / "claim.json").read_bytes()).hexdigest()
    (d / "MANIFEST.json").write_text(
        json.dumps({"schema": "bundle_v1", "files": {"claim.json": sha}}),
        encoding="utf-8", newline="\n")
    return "bundles/abc"


def test_vendored_claim_may_be_demoted(tmp_path):
    src = _bundle(tmp_path, "benchmarked")
    claim = {"id": "C-1", "evidence_level": "measured", "derived_from": src}
    assert check_inheritance([claim], cfg_for(tmp_path)) == []


def test_vendored_claim_may_not_be_promoted(tmp_path):
    """Meyer's redeclaration rule: a descendant never strengthens what it
    inherits without evidence of its own."""
    src = _bundle(tmp_path, "measured")
    claim = {"id": "C-1", "evidence_level": "externally_validated",
             "derived_from": src}
    findings = check_inheritance([claim], cfg_for(tmp_path))
    assert findings and findings[0][0].startswith("derived-level-promoted:")


def test_tampered_source_bundle_breaks_inheritance(tmp_path):
    src = _bundle(tmp_path, "measured")
    (tmp_path / src / "claim.json").write_text(
        json.dumps({"id": "SRC-1", "evidence_level": "measured", "x": 1}),
        encoding="utf-8", newline="\n")
    findings = check_inheritance(
        [{"id": "C-1", "evidence_level": "measured", "derived_from": src}],
        cfg_for(tmp_path))
    assert any(f[0].startswith("derived-bundle-tampered:") for f in findings)


def test_missing_source_bundle_fails_closed(tmp_path):
    findings = check_inheritance(
        [{"id": "C-1", "evidence_level": "measured", "derived_from": "nope"}],
        cfg_for(tmp_path))
    assert findings[0][0].startswith("derived-from-missing:")


# ── coverage ──────────────────────────────────────────────────────────────

def test_anchored_paragraph_counts_as_bound():
    text = ("<!-- claim:C-1 x -->\n"
            "The value is 42 across 3 files.\n")
    bound, unbound, _ = scan_text(text, [])
    assert (bound, unbound) == (2, 0)


def test_unanchored_numbers_are_counted_as_unbound():
    bound, unbound, misses = scan_text("It runs in 180 ms.\n", [])
    assert (bound, unbound) == (0, 1)
    assert misses == [(1, "180")]


def test_fenced_code_is_not_prose():
    text = "```\nx = 12345\n```\n"
    bound, unbound, _ = scan_text(text, [])
    assert unbound == 0


def test_allowlisted_shapes_are_not_claims():
    import re
    text = "Released 2026-07-14, version 1.2.3, on Python 3.11.\n"
    allow = [re.compile(p) for p in
             (r"^\d{4}-\d{2}-\d{2}$", r"^\d+\.\d+\.\d+$", r"^3\.1\d$")]
    _, unbound, misses = scan_text(text, allow)
    assert unbound == 0, misses


def test_report_shape_is_stable(tmp_path):
    doc = tmp_path / "README.md"
    doc.write_text("Runs in 180 ms.\n", encoding="utf-8")
    rec = report(cfg_for(tmp_path), [doc])
    assert rec["schema"] == "vericlaim_coverage_v1"
    assert rec["numbers_unbound"] == 1
    assert rec["coverage_pct"] == 0.0


# ── the ratchet ───────────────────────────────────────────────────────────

def test_ratchet_fails_when_a_quantity_grows(tmp_path):
    cfg = cfg_for(tmp_path, ratchet=(("legacy_shell_claims", 0),))
    actual = ratchet_measure([{"id": "C-1", "reproduce": "sh x"}], cfg,
                             baselined=0, unbound_numbers=None)
    notes: list[str] = []
    findings = ratchet_check(actual, cfg, notes)
    assert findings and findings[0][0] == "ratchet-regression:legacy_shell_claims"


def test_ratchet_notes_a_gain_it_can_lock_in(tmp_path):
    cfg = cfg_for(tmp_path, ratchet=(("legacy_shell_claims", 5),))
    notes: list[str] = []
    assert ratchet_check({"legacy_shell_claims": 1}, cfg, notes) == []
    assert notes and "tighten" in notes[0]


def test_ratchet_rejects_an_unknown_metric(tmp_path):
    cfg = cfg_for(tmp_path, ratchet=(("velocity", 3),))
    findings = ratchet_check({}, cfg, [])
    assert findings[0][0].startswith("ratchet-unknown-metric:")


def test_unmeasured_ratchet_metric_is_a_note_not_a_pass(tmp_path):
    """A metric that could not be measured must not silently satisfy its
    ceiling — that would be the check quietly disabling itself."""
    cfg = cfg_for(tmp_path, ratchet=(("unbound_numbers", 10),))
    notes: list[str] = []
    assert ratchet_check({}, cfg, notes) == []
    assert notes and "not measured" in notes[0]


def test_non_integer_ratchet_ceiling_is_rejected(tmp_path):
    (tmp_path / "vericlaim.toml").write_text(
        '[vericlaim.ratchet]\nlegacy_shell_claims = "many"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="integer ceiling"):
        load_config(tmp_path)


# ── the capability contract ───────────────────────────────────────────────

def test_unshipped_capability_stated_as_present_fails(tmp_path):
    cfg = cfg_for(tmp_path, capabilities=(("sandboxed runner", "designed"),),
                  front_page=("README.md",))
    findings = check_capability_claims(
        cfg, "README.md", "The sandboxed runner isolates every command.\n")
    assert findings and findings[0][0].startswith("capability-overstated:")


def test_hedged_mention_of_future_work_passes(tmp_path):
    cfg = cfg_for(tmp_path, capabilities=(("sandboxed runner", "designed"),),
                  front_page=("README.md",))
    assert check_capability_claims(
        cfg, "README.md",
        "A sandboxed runner is on the roadmap, not yet built.\n") == []


def test_shipped_capability_may_be_stated_plainly(tmp_path):
    cfg = cfg_for(tmp_path, capabilities=(("value token", "shipped"),),
                  front_page=("README.md",))
    assert check_capability_claims(
        cfg, "README.md", "A value token pins the next literal.\n") == []


def test_capability_check_only_guards_the_front_page(tmp_path):
    cfg = cfg_for(tmp_path, capabilities=(("sandboxed runner", "designed"),),
                  front_page=("README.md",))
    assert check_capability_claims(
        cfg, "docs/notes.md", "The sandboxed runner isolates commands.\n") == []


def test_unclassified_roadmap_item_is_a_finding(tmp_path):
    (tmp_path / "ROADMAP.md").write_text(
        "- ⏳ **Quantum reproduce.** Someday.\n", encoding="utf-8")
    cfg = cfg_for(tmp_path, roadmap="ROADMAP.md",
                  capabilities=(("value token", "shipped"),))
    findings = check_roadmap_classified(cfg)
    assert findings and findings[0][0].startswith("roadmap-unclassified:")


def test_classified_roadmap_item_passes(tmp_path):
    (tmp_path / "ROADMAP.md").write_text(
        "- ⏳ **Quantum reproduce.** Someday.\n", encoding="utf-8")
    cfg = cfg_for(tmp_path, roadmap="ROADMAP.md",
                  capabilities=(("Quantum reproduce", "designed"),))
    assert check_roadmap_classified(cfg) == []


# ── register shape validation for the new fields ──────────────────────────

def test_register_rejects_a_non_string_status():
    text = ('schema_version: "1"\nclaims:\n  - id: C-1\n    status: 3\n')
    with pytest.raises(RegisterError, match="`status` must be str"):
        load_register(text)


def test_register_rejects_a_non_mapping_assumes_entry():
    text = ('schema_version: "1"\nclaims:\n  - id: C-1\n'
            '    assumes:\n      - "just a string"\n')
    with pytest.raises(RegisterError, match="`assumes` entry"):
        load_register(text)
