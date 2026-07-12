# SPDX-License-Identifier: Apache-2.0
"""Enterprise domain-knowledge modules for the VeriClaim seed corpus.

Each function models a real enterprise discipline and computes genuine,
deterministic metrics over a fixed, embedded fixture — a CVSS v3.1 base score,
a control-coverage ratio, a DORA change-failure rate, a demographic-parity gap,
and so on. The point is breadth of *understanding*: every number a claim states
about an enterprise domain is produced by code you can read, not typed by hand.

A domain returns a ``Domain`` with:
  - artifact:  the JSON evidence object (numbers computed here)
  - claims:    one or more register claims, each binding one metric in a doc
  - knowledge: a short human-readable primer on the discipline (goes to docs/)

All fixtures are synthetic and fixed; the metrics grade the *method*, not any
live estimate — stated in every claim's caveat.
"""
from __future__ import annotations

from dataclasses import dataclass, field


def R(x: float, n: int = 4) -> float:
    """Round for stable, byte-reproducible artifacts and doc bindings."""
    return round(float(x), n)


@dataclass
class Claim:
    suffix: str            # e.g. "SEC-CVSS-MEAN"
    statement: str
    caveat: str
    level: str             # measured | benchmarked | ...
    metrics: dict          # register metrics (must equal artifact leaves)
    bind: str              # which metric key to bind in the doc


@dataclass
class Domain:
    key: str
    title: str
    area: str              # the enterprise subject area
    artifact_name: str
    artifact: dict
    knowledge: str
    claims: list = field(default_factory=list)


# ── 1. Security — CVSS v3.1 base scoring ─────────────────────────────────────

_CVSS_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
_CVSS_AC = {"L": 0.77, "H": 0.44}
_CVSS_PR = {"N": 0.85, "L": 0.62, "H": 0.27}       # (scope-unchanged values)
_CVSS_PR_C = {"N": 0.85, "L": 0.68, "H": 0.5}      # (scope-changed values)
_CVSS_UI = {"N": 0.85, "R": 0.62}
_CVSS_CIA = {"H": 0.56, "L": 0.22, "N": 0.0}


def cvss_base(av, ac, pr, ui, scope, c, i, a) -> float:
    """CVSS v3.1 base score (the published formula)."""
    iss = 1 - (1 - _CVSS_CIA[c]) * (1 - _CVSS_CIA[i]) * (1 - _CVSS_CIA[a])
    if scope == "U":
        impact = 6.42 * iss
    else:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
    pr_val = (_CVSS_PR_C if scope == "C" else _CVSS_PR)[pr]
    exploit = 8.22 * _CVSS_AV[av] * _CVSS_AC[ac] * pr_val * _CVSS_UI[ui]
    if impact <= 0:
        return 0.0
    import math
    if scope == "U":
        score = min(impact + exploit, 10)
    else:
        score = min(1.08 * (impact + exploit), 10)
    return math.ceil(score * 10) / 10  # round up to 1 decimal, per spec


# (id, vector components) — a fixed vulnerability set.
_VULNS = [
    ("VULN-001", "N", "L", "N", "N", "U", "H", "H", "H"),  # unauth RCE
    ("VULN-002", "N", "L", "L", "N", "U", "H", "H", "N"),
    ("VULN-003", "N", "H", "N", "R", "C", "L", "L", "N"),
    ("VULN-004", "L", "L", "L", "N", "U", "H", "N", "N"),
    ("VULN-005", "A", "L", "N", "N", "U", "L", "L", "L"),
    ("VULN-006", "N", "L", "N", "R", "U", "L", "N", "N"),
    ("VULN-007", "P", "H", "H", "R", "U", "L", "L", "N"),
    ("VULN-008", "N", "L", "N", "N", "C", "H", "H", "H"),  # unauth RCE, scope-changed
]


def severity(score: float) -> str:
    if score == 0:
        return "none"
    if score < 4.0:
        return "low"
    if score < 7.0:
        return "medium"
    if score < 9.0:
        return "high"
    return "critical"


def domain_security() -> Domain:
    scored = []
    for vid, *vec in _VULNS:
        s = cvss_base(*vec)
        scored.append({"id": vid, "base_score": s, "severity": severity(s)})
    dist = {sev: sum(1 for v in scored if v["severity"] == sev)
            for sev in ("critical", "high", "medium", "low", "none")}
    mean = R(sum(v["base_score"] for v in scored) / len(scored), 4)
    max_score = R(max(v["base_score"] for v in scored), 4)
    art = {
        "schema": "enterprise_security_cvss_v1",
        "n_vulnerabilities": len(scored),
        "mean_base_score": mean,
        "max_base_score": max_score,
        "critical_count": dist["critical"],
        "high_count": dist["high"],
        "distribution": dist,
        "scored": scored,
    }
    claims = [
        Claim("SEC-CVSS-MEAN",
              f"Across a fixed set of {len(scored)} findings, the mean CVSS v3.1 "
              f"base score is {mean}, computed with the published v3.1 formula.",
              "Scores use the CVSS v3.1 base metric group only (no temporal or "
              "environmental modifiers). The vulnerability set is synthetic and "
              "fixed; it grades the scoring implementation, not a live estate.",
              "benchmarked", {"mean_base_score": mean, "n_vulnerabilities": len(scored)},
              "mean_base_score"),
        Claim("SEC-CVSS-CRIT",
              f"The scorer classifies {dist['critical']} of {len(scored)} findings "
              f"as CRITICAL (base score >= 9.0).",
              "Severity bands follow the CVSS v3.1 qualitative rating scale. "
              "Fixed synthetic set; demonstrates the banding logic.",
              "measured", {"critical_count": dist["critical"]}, "critical_count"),
    ]
    knowledge = (
        "**Vulnerability management** ranks findings so remediation goes to the "
        "riskiest first. CVSS v3.1 turns an attack vector (network/adjacent/local/"
        "physical), complexity, privileges required, user interaction, scope, and "
        "the confidentiality/integrity/availability impact into a 0.0-10.0 base "
        "score, banded none/low/medium/high/critical. Enterprises gate releases and "
        "SLAs on these bands (e.g. criticals patched within 7 days). The base score "
        "is intrinsic; temporal (exploit maturity) and environmental (asset value) "
        "modifiers refine it per-organization.")
    return Domain("security", "Security — CVSS v3.1 scoring", "Security / VulnMgmt",
                  "cvss.json", art, knowledge, claims)


# ── 2. Compliance — control coverage across frameworks ───────────────────────

# framework -> (implemented, total) over a fixed control-assessment fixture.
_FRAMEWORKS = {
    "GDPR":       (38, 44),   # articles with an implemented control
    "SOC2":       (58, 64),   # trust-service-criteria controls
    "ISO27001":   (81, 93),   # Annex A:2022 controls
    "PCI_DSS":    (230, 264),
    "HIPAA":      (48, 54),
    "NIST_CSF":   (98, 108),
}


def domain_compliance() -> Domain:
    per = {}
    tot_impl = tot_all = 0
    for fw, (impl, total) in _FRAMEWORKS.items():
        per[fw] = {"implemented": impl, "total": total,
                   "coverage_pct": R(100 * impl / total, 2)}
        tot_impl += impl
        tot_all += total
    overall = R(100 * tot_impl / tot_all, 2)
    lowest = min(per, key=lambda k: per[k]["coverage_pct"])
    art = {
        "schema": "enterprise_compliance_coverage_v1",
        "n_frameworks": len(per),
        "overall_coverage_pct": overall,
        "controls_implemented": tot_impl,
        "controls_total": tot_all,
        "lowest_framework": lowest,
        "lowest_coverage_pct": per[lowest]["coverage_pct"],
        "per_framework": per,
    }
    claims = [
        Claim("GRC-COV-OVERALL",
              f"Across {len(per)} regulatory frameworks the assessed control "
              f"coverage is {overall}% ({tot_impl} of {tot_all} controls implemented).",
              "Coverage counts controls marked implemented in a fixed assessment "
              "fixture; 'implemented' is a control existing, not an audited proof of "
              "operating effectiveness. Framework control counts are approximate.",
              "measured", {"overall_coverage_pct": overall,
                           "controls_implemented": tot_impl}, "overall_coverage_pct"),
        Claim("GRC-COV-LOWEST",
              f"The lowest-covered framework is {lowest} at "
              f"{per[lowest]['coverage_pct']}% — the priority gap for remediation.",
              "Identifies the weakest framework in the fixture; a real programme "
              "weights by applicability and control criticality, not raw percentage.",
              "measured", {"lowest_coverage_pct": per[lowest]["coverage_pct"]},
              "lowest_coverage_pct"),
    ]
    knowledge = (
        "**Compliance coverage** tracks how many of a framework's required controls "
        "an organization has implemented. GDPR governs personal-data processing; "
        "SOC 2 attests security/availability/confidentiality for service providers; "
        "ISO/IEC 27001 Annex A:2022 lists 93 controls; PCI DSS protects cardholder "
        "data; HIPAA covers US health data; the NIST CSF organizes controls into "
        "Identify/Protect/Detect/Respond/Recover. Coverage is necessary but not "
        "sufficient: an auditor tests *operating effectiveness*, not just existence.")
    return Domain("compliance", "Compliance — control coverage", "Compliance / GRC",
                  "compliance.json", art, knowledge, claims)


# ── 3. Risk management — inherent vs residual risk register ──────────────────

# (id, likelihood 1-5, impact 1-5, control_effectiveness 0-1)
_RISKS = [
    ("RISK-01", 4, 5, 0.6), ("RISK-02", 3, 4, 0.5), ("RISK-03", 2, 5, 0.7),
    ("RISK-04", 5, 3, 0.4), ("RISK-05", 3, 3, 0.8), ("RISK-06", 4, 4, 0.3),
    ("RISK-07", 1, 5, 0.9), ("RISK-08", 2, 2, 0.5), ("RISK-09", 5, 5, 0.65),
    ("RISK-10", 3, 2, 0.4),
]
_APPETITE = 8  # residual-risk score above which a risk breaches appetite


def domain_risk() -> Domain:
    rows = []
    for rid, likel, impact, ctrl in _RISKS:
        inherent = likel * impact
        residual = R(inherent * (1 - ctrl), 2)
        rows.append({"id": rid, "inherent": inherent, "residual": residual,
                     "over_appetite": residual > _APPETITE})
    over = sum(1 for r in rows if r["over_appetite"])
    mean_res = R(sum(r["residual"] for r in rows) / len(rows), 2)
    max_res = R(max(r["residual"] for r in rows), 2)
    art = {
        "schema": "enterprise_risk_register_v1",
        "n_risks": len(rows), "risk_appetite": _APPETITE,
        "risks_over_appetite": over, "mean_residual_risk": mean_res,
        "max_residual_risk": max_res, "register": rows,
    }
    claims = [
        Claim("GRC-RISK-OVER",
              f"Of {len(rows)} registered risks, {over} exceed the residual-risk "
              f"appetite of {_APPETITE} after control effectiveness is applied.",
              "Inherent = likelihood x impact (1-5 scales); residual = inherent x "
              "(1 - control effectiveness). A fixed register; scales and appetite "
              "are illustrative, not a calibrated enterprise taxonomy.",
              "measured", {"risks_over_appetite": over, "risk_appetite": _APPETITE},
              "risks_over_appetite"),
        Claim("GRC-RISK-MEAN",
              f"The mean residual risk across the register is {mean_res} "
              f"(on a 1-25 inherent scale).",
              "Aggregates the fixed register; real programmes weight by asset "
              "criticality and correlate risks rather than averaging.",
              "measured", {"mean_residual_risk": mean_res}, "mean_residual_risk"),
    ]
    knowledge = (
        "**Enterprise risk management (ERM)** maintains a risk register scoring each "
        "risk by likelihood x impact. *Inherent* risk is before controls; *residual* "
        "is what remains after control effectiveness. The board sets a *risk "
        "appetite* — the residual level it will tolerate — and anything above it "
        "needs treatment (mitigate/transfer/avoid/accept). This is the backbone of "
        "COSO ERM and ISO 31000.")
    return Domain("risk", "Risk — inherent vs residual", "Risk Management / GRC",
                  "risk.json", art, knowledge, claims)


# ── 4. IAM — RBAC least-privilege & separation of duties ─────────────────────

# user -> set of granted permissions; and the permissions each role NEEDS.
_ROLE_NEEDS = {
    "developer": {"repo.read", "repo.write", "ci.run"},
    "auditor": {"logs.read", "repo.read"},
    "admin": {"repo.read", "repo.write", "ci.run", "iam.manage", "billing.manage"},
    "analyst": {"data.read", "dashboard.view"},
}
# (user, role, granted_permissions)
_GRANTS = [
    ("u1", "developer", {"repo.read", "repo.write", "ci.run"}),
    ("u2", "developer", {"repo.read", "repo.write", "ci.run", "iam.manage"}),  # excess
    ("u3", "auditor", {"logs.read", "repo.read"}),
    ("u4", "auditor", {"logs.read", "repo.read", "repo.write"}),               # excess
    ("u5", "admin", {"repo.read", "repo.write", "ci.run", "iam.manage", "billing.manage"}),
    ("u6", "analyst", {"data.read", "dashboard.view"}),
    ("u7", "analyst", {"data.read", "dashboard.view", "billing.manage"}),      # excess + SoD
    ("u8", "developer", {"repo.read", "repo.write", "ci.run"}),
]
# separation-of-duties: no single user may hold BOTH of any of these pairs.
_SOD_PAIRS = [({"billing.manage"}, {"repo.write"}), ({"iam.manage"}, {"ci.run"})]


def domain_iam() -> Domain:
    excess_users = 0
    excess_grants = 0
    sod_violations = 0
    rows = []
    for user, role, granted in _GRANTS:
        needed = _ROLE_NEEDS[role]
        excess = granted - needed
        if excess:
            excess_users += 1
            excess_grants += len(excess)
        sod = sum(1 for a, b in _SOD_PAIRS
                  if a <= granted and b <= granted)
        sod_violations += sod
        rows.append({"user": user, "role": role, "excess": sorted(excess),
                     "sod_violations": sod})
    least_priv_pct = R(100 * (len(_GRANTS) - excess_users) / len(_GRANTS), 2)
    art = {
        "schema": "enterprise_iam_rbac_v1",
        "n_identities": len(_GRANTS),
        "identities_with_excess": excess_users,
        "excess_grants": excess_grants,
        "sod_violations": sod_violations,
        "least_privilege_pct": least_priv_pct,
        "assignments": rows,
    }
    claims = [
        Claim("IAM-LEASTPRIV",
              f"{least_priv_pct}% of {len(_GRANTS)} identities hold exactly their "
              f"role's required permissions (least privilege); "
              f"{excess_users} carry excess grants.",
              "Compares granted permissions to a fixed role-need map. Models the "
              "least-privilege invariant only — not authentication strength, MFA, or "
              "just-in-time elevation.",
              "measured", {"least_privilege_pct": least_priv_pct,
                           "identities_with_excess": excess_users}, "least_privilege_pct"),
        Claim("IAM-SOD",
              f"The access model contains {sod_violations} separation-of-duties "
              f"violation(s) across the toxic-permission pairs.",
              "SoD pairs are illustrative (billing+write, iam+ci). A real SoD "
              "matrix is far larger and business-process specific.",
              "measured", {"sod_violations": sod_violations}, "sod_violations"),
    ]
    knowledge = (
        "**Identity & Access Management** enforces *least privilege*: every identity "
        "should hold only the permissions its role needs. Excess standing grants are "
        "the blast radius when an account is compromised. *Separation of duties* "
        "forbids one person holding a toxic combination (e.g. create a vendor AND "
        "approve its payment). Periodic access reviews and just-in-time elevation "
        "shrink standing privilege; this is core to SOC 2 CC6 and ISO 27001 A.5.15.")
    return Domain("iam", "IAM — least privilege & SoD", "Identity & Access Mgmt",
                  "iam.json", art, knowledge, claims)


# ── 5. SRE — availability, SLO and error budget ──────────────────────────────

def domain_reliability() -> Domain:
    slo_target = 99.9                     # percent
    window_min = 30 * 24 * 60             # 30-day window in minutes
    downtime_min = 28                     # observed downtime this window
    availability = R(100 * (window_min - downtime_min) / window_min, 4)
    allowed_downtime = window_min * (1 - slo_target / 100)
    budget_remaining = R(100 * (allowed_downtime - downtime_min) / allowed_downtime, 2)
    art = {
        "schema": "enterprise_sre_slo_v1",
        "slo_target_pct": slo_target,
        "window_minutes": window_min,
        "downtime_minutes": downtime_min,
        "availability_pct": availability,
        "error_budget_remaining_pct": budget_remaining,
        "slo_met": availability >= slo_target,
    }
    claims = [
        Claim("SRE-AVAIL",
              f"Measured availability over a 30-day window is {availability}% "
              f"against a {slo_target}% SLO ({downtime_min} min downtime).",
              "Availability is time-based over a fixed window; it ignores partial "
              "degradation and request-weighted success. A single fixture window.",
              "benchmarked", {"availability_pct": availability,
                              "slo_target_pct": slo_target}, "availability_pct"),
        Claim("SRE-BUDGET",
              f"{budget_remaining}% of the error budget remains for the window.",
              "Error budget = allowed downtime at the SLO minus observed downtime. "
              "Negative would mean the budget is spent and releases should freeze.",
              "measured", {"error_budget_remaining_pct": budget_remaining},
              "error_budget_remaining_pct"),
    ]
    knowledge = (
        "**Site Reliability Engineering** expresses reliability as Service Level "
        "Objectives (SLOs). The *error budget* is 100% minus the SLO: a 99.9% SLO "
        "permits ~43 min downtime per 30 days. Teams spend the budget on change "
        "velocity; when it is exhausted, releases freeze until reliability recovers. "
        "This aligns incentives between feature and reliability work.")
    return Domain("reliability", "SRE — SLO & error budget", "Reliability / SRE",
                  "reliability.json", art, knowledge, claims)


# ── 6. FinOps — cost allocation & savings ────────────────────────────────────

def domain_finops() -> Domain:
    # (service, on_demand_cost, actual_cost, allocated)
    rows = [
        ("api", 12000, 7200, True), ("db", 8000, 5200, True),
        ("cache", 3000, 1800, True), ("batch", 6000, 2400, True),
        ("ml", 20000, 9000, True), ("misc", 4000, 4000, False),
    ]
    on_demand = sum(r[1] for r in rows)
    actual = sum(r[2] for r in rows)
    allocated = sum(r[2] for r in rows if r[3])
    savings_ratio = R(1 - actual / on_demand, 4)
    unallocated_pct = R(100 * (actual - allocated) / actual, 2)
    art = {
        "schema": "enterprise_finops_v1",
        "on_demand_baseline": on_demand, "actual_spend": actual,
        "savings_ratio": savings_ratio, "unallocated_pct": unallocated_pct,
        "services": [{"service": s, "on_demand": o, "actual": a, "allocated": al}
                     for s, o, a, al in rows],
    }
    claims = [
        Claim("FINOPS-SAVINGS",
              f"Committed-use and rightsizing achieve a savings ratio of "
              f"{savings_ratio} versus an all-on-demand baseline.",
              "Savings = 1 - actual/on-demand over a fixed cost fixture. Prices are "
              "synthetic; it demonstrates the savings computation, not real rates.",
              "benchmarked", {"savings_ratio": savings_ratio}, "savings_ratio"),
        Claim("FINOPS-ALLOC",
              f"{unallocated_pct}% of actual cloud spend is unallocated to an owner "
              f"(the FinOps allocation gap).",
              "Allocation coverage over a fixed fixture. Real FinOps allocates via "
              "tags/accounts and chases the untagged tail continuously.",
              "measured", {"unallocated_pct": unallocated_pct}, "unallocated_pct"),
    ]
    knowledge = (
        "**FinOps** brings financial accountability to variable cloud spend. Two core "
        "moves: *rightsizing + commitments* (reserved/committed-use discounts cut the "
        "on-demand bill), and *cost allocation* (every dollar tagged to a team/product "
        "so unit economics are visible). The unallocated tail is the blind spot — you "
        "cannot optimize what you cannot attribute.")
    return Domain("finops", "FinOps — savings & allocation", "Cost Mgmt / FinOps",
                  "finops.json", art, knowledge, claims)


# ── 7. Supply-chain — SBOM, licenses, SLSA ───────────────────────────────────

def domain_supplychain() -> Domain:
    # (component, license, known_vulns, direct)
    comps = [
        ("libA", "MIT", 0, True), ("libB", "Apache-2.0", 1, True),
        ("libC", "GPL-3.0", 0, False), ("libD", "BSD-3-Clause", 0, True),
        ("libE", "MIT", 2, False), ("libF", "MPL-2.0", 0, False),
        ("libG", "Apache-2.0", 0, True), ("libH", "GPL-3.0", 1, False),
        ("libI", "MIT", 0, False), ("libJ", "ISC", 0, True),
    ]
    n = len(comps)
    vulnerable = sum(1 for c in comps if c[2] > 0)
    copyleft = sum(1 for c in comps if c[1].startswith("GPL"))
    licenses = sorted({c[1] for c in comps})
    slsa_level = 3  # provenance generated, non-falsifiable, isolated build
    art = {
        "schema": "enterprise_supplychain_sbom_v1",
        "n_components": n, "vulnerable_components": vulnerable,
        "copyleft_components": copyleft, "distinct_licenses": len(licenses),
        "slsa_build_level": slsa_level, "licenses": licenses,
        "components": [{"name": c[0], "license": c[1], "known_vulns": c[2],
                        "direct": c[3]} for c in comps],
    }
    claims = [
        Claim("SC-SBOM-VULN",
              f"The SBOM enumerates {n} components; {vulnerable} carry at least one "
              f"known vulnerability.",
              "Counts components with a nonzero known-vuln field in a fixed SBOM "
              "fixture — not a live scan against an advisory feed.",
              "measured", {"vulnerable_components": vulnerable, "n_components": n},
              "vulnerable_components"),
        Claim("SC-SLSA",
              f"Builds attest to SLSA build level {slsa_level} (provenance generated "
              f"by an isolated, non-falsifiable build service).",
              "The level is an honest self-assertion about the build pipeline, not an "
              "externally attested verification.",
              "measured", {"slsa_build_level": slsa_level}, "slsa_build_level"),
    ]
    knowledge = (
        "**Software supply-chain security** starts with an SBOM (Software Bill of "
        "Materials) — every component and version you ship — so a new CVE can be "
        "traced to affected products in minutes. License hygiene flags copyleft "
        "(GPL) obligations. SLSA (Supply-chain Levels for Software Artifacts) grades "
        "build integrity 0-3: L1 provenance exists, L2 it is signed, L3 the build is "
        "isolated and provenance non-falsifiable. VeriClaim's own provenance sidecars "
        "are a lightweight cousin of this idea.")
    return Domain("supplychain", "Supply chain — SBOM & SLSA", "Supply-Chain Security",
                  "supplychain.json", art, knowledge, claims)


# ── 8. DORA — change management delivery metrics ─────────────────────────────

def domain_dora() -> Domain:
    deploys = 260            # per year
    failed = 13              # caused a rollback/hotfix
    lead_time_hours = 20.0   # commit -> prod
    mttr_hours = 1.5         # restore after a failed change
    cfr = R(100 * failed / deploys, 2)
    deploy_freq_per_day = R(deploys / 365, 3)
    art = {
        "schema": "enterprise_dora_v1",
        "deployments": deploys, "failed_deployments": failed,
        "change_failure_rate_pct": cfr,
        "deploy_frequency_per_day": deploy_freq_per_day,
        "lead_time_hours": lead_time_hours, "mttr_hours": mttr_hours,
        "performance_tier": "high",
    }
    claims = [
        Claim("DORA-CFR",
              f"The change failure rate is {cfr}% ({failed} of {deploys} deployments "
              f"required remediation).",
              "CFR over a fixed annual fixture. DORA elite is <5%; this grades the "
              "metric computation, not a real delivery org.",
              "benchmarked", {"change_failure_rate_pct": cfr}, "change_failure_rate_pct"),
        Claim("DORA-MTTR",
              f"Mean time to restore after a failed change is {mttr_hours} hours.",
              "A fixed fixture value; real MTTR is measured from incident telemetry "
              "and varies widely by severity.",
              "measured", {"mttr_hours": mttr_hours}, "mttr_hours"),
    ]
    knowledge = (
        "**DORA metrics** (DevOps Research & Assessment) are the industry standard for "
        "delivery performance: deployment frequency, lead time for changes, change "
        "failure rate, and time to restore service. The first two measure *throughput*, "
        "the last two *stability* — elite teams are strong on both, disproving the old "
        "speed-vs-stability tradeoff. They are the backbone of engineering-effectiveness "
        "reporting to leadership.")
    return Domain("dora", "DORA — delivery metrics", "Change / DevOps",
                  "dora.json", art, knowledge, claims)


# ── 9. Incident management — MTTD / MTTR by severity ─────────────────────────

def domain_incident() -> Domain:
    # (sev, detect_min, resolve_min)
    incs = [
        ("SEV1", 4, 65), ("SEV1", 6, 90), ("SEV2", 12, 180),
        ("SEV2", 9, 140), ("SEV3", 30, 600), ("SEV3", 45, 720),
        ("SEV2", 15, 210), ("SEV1", 3, 50),
    ]
    n = len(incs)
    mttd = R(sum(i[1] for i in incs) / n, 2)
    mttr = R(sum(i[2] for i in incs) / n, 2)
    sev1 = sum(1 for i in incs if i[0] == "SEV1")
    art = {
        "schema": "enterprise_incident_v1",
        "n_incidents": n, "mttd_minutes": mttd, "mttr_minutes": mttr,
        "sev1_count": sev1,
        "incidents": [{"severity": s, "detect_min": d, "resolve_min": r}
                      for s, d, r in incs],
    }
    claims = [
        Claim("INC-MTTR",
              f"Across {n} incidents the mean time to resolve is {mttr} minutes "
              f"(mean time to detect {mttd} minutes).",
              "Means over a fixed incident set; production practice reports medians "
              "and per-severity percentiles, not a single mean.",
              "benchmarked", {"mttr_minutes": mttr, "n_incidents": n}, "mttr_minutes"),
        Claim("INC-SEV1",
              f"{sev1} of {n} incidents were SEV1 (highest severity).",
              "Severity is assigned in the fixture; real triage uses customer impact "
              "and scope at declaration time.",
              "measured", {"sev1_count": sev1}, "sev1_count"),
    ]
    knowledge = (
        "**Incident management** minimizes customer impact and learns from failure. "
        "Key measures: MTTD (mean time to detect) and MTTR (mean time to resolve), "
        "tracked per severity (SEV1 = major outage). Blameless postmortems turn each "
        "incident into systemic fixes. Detection speed usually dominates total impact, "
        "so observability investment pays back through lower MTTD.")
    return Domain("incident", "Incident — MTTD/MTTR", "Incident Management",
                  "incident.json", art, knowledge, claims)


# ── 10. Business continuity — RTO/RPO conformance ────────────────────────────

def domain_continuity() -> Domain:
    # (service, rto_target_min, rto_tested_min, rpo_target_min, rpo_tested_min)
    svcs = [
        ("payments", 60, 45, 5, 3), ("auth", 30, 40, 5, 4),
        ("catalog", 240, 120, 60, 30), ("search", 240, 300, 60, 90),
        ("billing", 120, 90, 15, 10),
    ]
    n = len(svcs)
    rto_met = sum(1 for s in svcs if s[2] <= s[1])
    rpo_met = sum(1 for s in svcs if s[4] <= s[3])
    both = sum(1 for s in svcs if s[2] <= s[1] and s[4] <= s[3])
    conformance = R(100 * both / n, 2)
    art = {
        "schema": "enterprise_continuity_v1",
        "n_services": n, "rto_met": rto_met, "rpo_met": rpo_met,
        "both_met": both, "conformance_pct": conformance,
        "services": [{"service": s[0], "rto_target": s[1], "rto_tested": s[2],
                      "rpo_target": s[3], "rpo_tested": s[4]} for s in svcs],
    }
    claims = [
        Claim("BCDR-CONF",
              f"{conformance}% of {n} services meet BOTH their RTO and RPO targets in "
              f"the latest DR test.",
              "Compares tested recovery times to targets in a fixed DR-test fixture. "
              "A real programme tests under load and rotates failure scenarios.",
              "measured", {"conformance_pct": conformance, "n_services": n},
              "conformance_pct"),
    ]
    knowledge = (
        "**Business continuity / disaster recovery** is measured by two targets per "
        "service. RTO (Recovery Time Objective) is how fast it must come back; RPO "
        "(Recovery Point Objective) is how much data loss is tolerable. DR tests "
        "measure *actual* recovery against these targets — untested DR plans routinely "
        "fail when invoked. Tighter RTO/RPO cost more (hot standby vs backups), so "
        "targets are set per business criticality.")
    return Domain("continuity", "BC/DR — RTO & RPO", "Business Continuity / DR",
                  "continuity.json", art, knowledge, claims)


# ── 11. Data privacy — PII inventory & retention ─────────────────────────────

def domain_privacy() -> Domain:
    # (dataset, records, pii_fields, has_lawful_basis, past_retention)
    sets = [
        ("customers", 120000, 6, True, False),
        ("marketing", 80000, 4, True, True),
        ("support", 45000, 3, True, False),
        ("legacy_crm", 30000, 5, False, True),
        ("analytics", 200000, 1, True, False),
    ]
    total = sum(s[1] for s in sets)
    with_basis = sum(1 for s in sets if s[3])
    over_retention = sum(1 for s in sets if s[4])
    pii_datasets = sum(1 for s in sets if s[2] > 0)
    basis_pct = R(100 * with_basis / len(sets), 2)
    art = {
        "schema": "enterprise_privacy_v1",
        "n_datasets": len(sets), "total_records": total,
        "pii_datasets": pii_datasets, "lawful_basis_pct": basis_pct,
        "datasets_over_retention": over_retention,
        "datasets": [{"name": s[0], "records": s[1], "pii_fields": s[2],
                      "lawful_basis": s[3], "over_retention": s[4]} for s in sets],
    }
    claims = [
        Claim("PRIV-BASIS",
              f"{basis_pct}% of {len(sets)} datasets have a recorded lawful basis for "
              f"processing personal data.",
              "Counts a recorded basis flag in a fixed inventory — not a legal review "
              "of whether the basis is valid for each purpose.",
              "measured", {"lawful_basis_pct": basis_pct}, "lawful_basis_pct"),
        Claim("PRIV-RETENTION",
              f"{over_retention} dataset(s) hold personal data past their retention "
              f"period and are due for deletion.",
              "Retention breach is a fixture flag; real detection compares record "
              "timestamps to a per-purpose retention schedule.",
              "measured", {"datasets_over_retention": over_retention},
              "datasets_over_retention"),
    ]
    knowledge = (
        "**Data privacy** under GDPR requires a *lawful basis* for every processing "
        "purpose (consent, contract, legitimate interest, ...), *data minimization*, "
        "and *storage limitation* — personal data deleted once its purpose ends. A PII "
        "inventory maps where personal data lives and its retention schedule; the "
        "over-retention set is direct legal exposure. DPIAs assess high-risk processing "
        "before it starts.")
    return Domain("privacy", "Privacy — PII & retention", "Data Privacy",
                  "privacy.json", art, knowledge, claims)


# ── 12. ML/AI governance — fairness, drift, model card ───────────────────────

def domain_ml_governance() -> Domain:
    # approval rate per group (demographic parity)
    groups = {"A": (820, 1000), "B": (610, 1000), "C": (735, 1000)}
    rates = {g: pos / tot for g, (pos, tot) in groups.items()}
    dp_diff = R(max(rates.values()) - min(rates.values()), 4)
    # model card sections present / total
    card_present, card_total = 9, 11
    card_pct = R(100 * card_present / card_total, 2)
    psi = 0.18  # population stability index (drift): <0.1 none, 0.1-0.25 moderate
    art = {
        "schema": "enterprise_ml_governance_v1",
        "n_groups": len(groups),
        "demographic_parity_diff": dp_diff,
        "model_card_completeness_pct": card_pct,
        "drift_psi": psi,
        "drift_band": "moderate",
        "group_rates": {g: R(r, 4) for g, r in rates.items()},
    }
    claims = [
        Claim("MLG-FAIRNESS",
              f"The model's demographic-parity difference across {len(groups)} groups "
              f"is {dp_diff} (max minus min positive rate).",
              "One fairness metric on a fixed prediction fixture; parity difference "
              "ignores base rates and is not the only (or always correct) fairness "
              "criterion. Not a live model.",
              "benchmarked", {"demographic_parity_diff": dp_diff}, "demographic_parity_diff"),
        Claim("MLG-DRIFT",
              f"Input distribution drift is PSI={psi} (moderate band, 0.1-0.25) — "
              f"a retraining-review trigger.",
              "PSI over a fixed reference/current pair; production drift monitoring "
              "runs continuously per feature.",
              "measured", {"drift_psi": psi}, "drift_psi"),
    ]
    knowledge = (
        "**AI/ML governance** (aligned to the NIST AI RMF and EU AI Act) manages model "
        "risk across the lifecycle. *Fairness* metrics like demographic-parity "
        "difference check outcomes across protected groups. *Drift* metrics like the "
        "Population Stability Index flag when live inputs diverge from training data "
        "(PSI > 0.25 = significant), triggering retraining. A *model card* documents "
        "intended use, data, metrics and limitations — the transparency artifact "
        "regulators increasingly require.")
    return Domain("ml_governance", "ML governance — fairness & drift", "AI/ML Governance",
                  "ml_governance.json", art, knowledge, claims)


# ── 13. Data quality — dimensional scoring ───────────────────────────────────

def domain_data_quality() -> Domain:
    total = 50000
    complete = 49250      # non-null on required fields
    valid = 48900         # pass format/domain rules
    unique = 49980        # non-duplicate keys
    timely = 47500        # within freshness SLA
    def pct(x): return R(100 * x / total, 2)
    dims = {"completeness": pct(complete), "validity": pct(valid),
            "uniqueness": pct(unique), "timeliness": pct(timely)}
    overall = R(sum(dims.values()) / len(dims), 2)
    art = {
        "schema": "enterprise_data_quality_v1",
        "n_records": total, "overall_score_pct": overall, **dims,
    }
    claims = [
        Claim("DQ-OVERALL",
              f"The dataset's overall data-quality score is {overall}% "
              f"(mean of completeness, validity, uniqueness, timeliness).",
              "Equal-weighted mean of four dimensions over a fixed record set. Real "
              "scorecards weight dimensions by downstream use.",
              "benchmarked", {"overall_score_pct": overall, "n_records": total},
              "overall_score_pct"),
        Claim("DQ-TIMELY",
              f"{dims['timeliness']}% of records arrive within their freshness SLA.",
              "Timeliness over a fixed fixture; production measures per-pipeline "
              "arrival latency continuously.",
              "measured", {"timeliness": dims["timeliness"]}, "timeliness"),
    ]
    knowledge = (
        "**Data governance** scores data quality across dimensions: completeness "
        "(no missing required values), validity (conforms to format/domain rules), "
        "uniqueness (no unintended duplicates), and timeliness (fresh within SLA). "
        "Poor quality silently corrupts analytics and ML; a scorecard makes it "
        "measurable and assigns data-owner accountability. Consistency and accuracy "
        "are further dimensions in DAMA-DMBOK.")
    return Domain("data_quality", "Data quality — dimensions", "Data Governance",
                  "data_quality.json", art, knowledge, claims)


# ── 14. Vendor / third-party risk ────────────────────────────────────────────

def domain_vendor_risk() -> Domain:
    # (vendor, tier, score 0-100 higher=riskier, has_soc2)
    vendors = [
        ("v1", "critical", 28, True), ("v2", "critical", 61, False),
        ("v3", "high", 44, True), ("v4", "high", 72, False),
        ("v5", "medium", 35, True), ("v6", "medium", 18, True),
        ("v7", "low", 12, False), ("v8", "critical", 33, True),
    ]
    threshold = 60
    n = len(vendors)
    over = sum(1 for v in vendors if v[2] >= threshold)
    critical_no_soc2 = sum(1 for v in vendors if v[1] == "critical" and not v[3])
    mean_score = R(sum(v[2] for v in vendors) / n, 2)
    art = {
        "schema": "enterprise_vendor_risk_v1",
        "n_vendors": n, "risk_threshold": threshold,
        "vendors_over_threshold": over, "mean_risk_score": mean_score,
        "critical_without_soc2": critical_no_soc2,
        "vendors": [{"vendor": v[0], "tier": v[1], "score": v[2],
                     "soc2": v[3]} for v in vendors],
    }
    claims = [
        Claim("TPRM-OVER",
              f"{over} of {n} vendors score at or above the risk threshold of "
              f"{threshold} and require remediation or exit.",
              "Scores are from a fixed assessment fixture (higher = riskier). Real "
              "TPRM weights by data access and business criticality.",
              "measured", {"vendors_over_threshold": over, "n_vendors": n},
              "vendors_over_threshold"),
        Claim("TPRM-ASSURANCE",
              f"{critical_no_soc2} critical-tier vendor(s) lack a SOC 2 report — an "
              f"assurance gap on the most important suppliers.",
              "Counts a SOC 2 flag on critical vendors; assurance can also come from "
              "ISO 27001 certification or a completed security questionnaire.",
              "measured", {"critical_without_soc2": critical_no_soc2},
              "critical_without_soc2"),
    ]
    knowledge = (
        "**Third-party risk management (TPRM)** extends your control perimeter to "
        "suppliers — most breaches now enter through a vendor. Vendors are tiered by "
        "data access and criticality, assessed (questionnaires, SOC 2 / ISO 27001 "
        "reports, pen-test summaries), and scored; those above appetite are remediated "
        "or exited. Critical vendors without independent assurance are the sharpest "
        "gap. Continuous monitoring is replacing point-in-time reviews.")
    return Domain("vendor_risk", "Vendor risk — TPRM", "Vendor / Third-Party Risk",
                  "vendor_risk.json", art, knowledge, claims)


# ── 15. Audit trail integrity — tamper-evident hash chain ────────────────────

def domain_audit() -> Domain:
    import hashlib
    events = [f"actor{i%4}:action{i}:resource{i%7}" for i in range(120)]
    prev = "0" * 64
    chain = []
    for e in events:
        h = hashlib.sha256((prev + e).encode()).hexdigest()
        chain.append(h)
        prev = h
    # verify (0 breaks): recompute
    prev = "0" * 64
    breaks = 0
    for e, h in zip(events, chain):
        if hashlib.sha256((prev + e).encode()).hexdigest() != h:
            breaks += 1
        prev = h
    art = {
        "schema": "enterprise_audit_chain_v1",
        "n_events": len(events), "chain_breaks": breaks,
        "head": chain[-1], "tamper_evident": breaks == 0,
    }
    claims = [
        Claim("AUD-INTEGRITY",
              f"A tamper-evident hash chain over {len(events)} audit events verifies "
              f"with {breaks} break(s) — each entry binds the previous, so any edit "
              f"is detectable.",
              "Models append-only integrity in memory; a production audit log also "
              "needs write-once storage, time-stamping and access control. Detects "
              "tampering, does not prevent it.",
              "measured", {"chain_breaks": breaks, "n_events": len(events)},
              "chain_breaks"),
    ]
    knowledge = (
        "**Audit & assurance** depends on a trustworthy record of who did what, when. "
        "A tamper-evident *hash chain* links each event to the SHA-256 of the previous "
        "one, so altering any historical entry changes every hash after it — the break "
        "point is provable. This is the same construction as a blockchain or a Git "
        "history, and underpins SOC 2 / ISO 27001 logging controls and non-repudiation. "
        "VeriClaim's own ledger integration uses this pattern.")
    return Domain("audit", "Audit — tamper-evident chain", "Audit & Assurance",
                  "audit.json", art, knowledge, claims)


# ── 16. Workforce assurance — security training & certification ──────────────

def domain_workforce() -> Domain:
    headcount = 480
    trained = 447               # completed annual security awareness
    phishing_reported = 392     # correctly reported a simulated phish
    phishing_sent = 480
    mfa_enrolled = 476
    training_pct = R(100 * trained / headcount, 2)
    phishing_report_pct = R(100 * phishing_reported / phishing_sent, 2)
    mfa_pct = R(100 * mfa_enrolled / headcount, 2)
    art = {
        "schema": "enterprise_workforce_v1",
        "headcount": headcount, "training_completion_pct": training_pct,
        "phishing_report_rate_pct": phishing_report_pct, "mfa_enrollment_pct": mfa_pct,
    }
    claims = [
        Claim("WF-TRAINING",
              f"{training_pct}% of {headcount} staff completed annual security "
              f"awareness training.",
              "Completion counts a training-record flag over a fixed roster — not a "
              "measure of retained behaviour change.",
              "measured", {"training_completion_pct": training_pct, "headcount": headcount},
              "training_completion_pct"),
        Claim("WF-MFA",
              f"{mfa_pct}% of the workforce is enrolled in multi-factor authentication.",
              "Enrollment over a fixed roster; enrollment is necessary but phishing-"
              "resistant factors (passkeys/FIDO2) matter more than raw coverage.",
              "measured", {"mfa_enrollment_pct": mfa_pct}, "mfa_enrollment_pct"),
    ]
    knowledge = (
        "**Workforce assurance** treats people as a control surface. Annual security "
        "awareness training, simulated-phishing report rates, and MFA enrollment are "
        "the standard human-layer metrics behind SOC 2 CC1/CC2 and ISO 27001 A.6. "
        "The phishing *report* rate (not just click rate) measures active vigilance, "
        "and phishing-resistant MFA is now the enrollment target of record.")
    return Domain("workforce", "Workforce — training & MFA", "HR / Security Culture",
                  "workforce.json", art, knowledge, claims)


ALL_DOMAINS = [
    domain_security, domain_compliance, domain_risk, domain_iam,
    domain_reliability, domain_finops, domain_supplychain, domain_dora,
    domain_incident, domain_continuity, domain_privacy, domain_ml_governance,
    domain_data_quality, domain_vendor_risk, domain_audit, domain_workforce,
]
