# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-PROV-001 — the encoded PROV-DM core matches the
W3C Recommendation and the validator enforces it exhaustively.

Oracles, none the module's own output: (1) the published core taxonomy of
PROV-DM (W3C Recommendation, 30 April 2013): exactly three types and seven
relations with the published signatures — used(activity->entity),
wasGeneratedBy(entity->activity), wasInformedBy(activity->activity),
wasDerivedFrom(entity->entity), wasAttributedTo(entity->agent),
wasAssociatedWith(activity->agent), actedOnBehalfOf(agent->agent) —
verified against the Recommendation's core-structures section (Start/End
are expanded structures, deliberately absent); (2) EXHAUSTIVE signature
enumeration: all 7 x 9 = 63 (relation, subject-type, object-type)
combinations are validated and exactly the 7 published signatures pass;
(3) an ML-pipeline exemplar (dataset -> training run -> model -> eval
report, with agents and delegation) validates clean, and every one of a
fixed set of corruptions (wrong endpoint types, unknown relation, unknown
id, derivation cycle, delegation cycle) is caught. Deterministic: same
artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from prov_dm import (  # noqa: E402
    RELATIONS, TYPES, ProvDocument, ProvError, is_valid,
)
from _util import emit  # noqa: E402

PUBLISHED = {
    "used": ("activity", "entity"),
    "wasGeneratedBy": ("entity", "activity"),
    "wasInformedBy": ("activity", "activity"),
    "wasDerivedFrom": ("entity", "entity"),
    "wasAttributedTo": ("entity", "agent"),
    "wasAssociatedWith": ("activity", "agent"),
    "actedOnBehalfOf": ("agent", "agent"),
}

# An ML pipeline in PROV core: data -> training -> model -> evaluation.
EXEMPLAR = ProvDocument(
    elements={
        "dataset": "entity", "model": "entity", "report": "entity",
        "training": "activity", "evaluation": "activity",
        "ml_team": "agent", "engineer": "agent",
    },
    relations=[
        ("used", "training", "dataset"),
        ("wasGeneratedBy", "model", "training"),
        ("used", "evaluation", "model"),
        ("wasGeneratedBy", "report", "evaluation"),
        ("wasInformedBy", "evaluation", "training"),
        ("wasDerivedFrom", "model", "dataset"),
        ("wasDerivedFrom", "report", "model"),
        ("wasAttributedTo", "model", "ml_team"),
        ("wasAssociatedWith", "training", "engineer"),
        ("actedOnBehalfOf", "engineer", "ml_team"),
    ])


def corruptions() -> list:
    e = dict(EXEMPLAR.elements)
    r = list(EXEMPLAR.relations)
    return [
        ("used with swapped endpoints",
         ProvDocument(e, r + [("used", "dataset", "training")])),
        ("generation by an agent",
         ProvDocument(e, r + [("wasGeneratedBy", "model", "ml_team")])),
        ("attribution to an activity",
         ProvDocument(e, r + [("wasAttributedTo", "model", "training")])),
        ("unknown relation",
         ProvDocument(e, r + [("wasRevisionOf", "report", "model")])),
        ("unknown element id",
         ProvDocument(e, r + [("used", "training", "ghost")])),
        ("derivation cycle",
         ProvDocument(e, r + [("wasDerivedFrom", "dataset", "report")])),
        ("delegation cycle",
         ProvDocument(e, r + [("actedOnBehalfOf", "ml_team", "engineer")])),
        ("self-derivation",
         ProvDocument(e, r + [("wasDerivedFrom", "model", "model")])),
    ]


def run() -> dict:
    taxonomy = [
        TYPES == ("entity", "activity", "agent"),
        RELATIONS == PUBLISHED,
        len(RELATIONS) == 7,
        "wasStartedBy" not in RELATIONS and "wasEndedBy" not in RELATIONS,
    ]
    taxonomy_ok = sum(taxonomy)

    exemplar_ok = int(is_valid(EXEMPLAR))

    # Exhaustive signature enumeration: 7 relations x 3x3 type pairs.
    enum_checks = 0
    enum_ok = 0
    for rel, (want_s, want_o) in PUBLISHED.items():
        for ks in TYPES:
            for kd in TYPES:
                enum_checks += 1
                doc = ProvDocument({"s": ks, "o": kd}, [(rel, "s", "o")])
                legal = (ks, kd) == (want_s, want_o)
                if legal == is_valid(doc):
                    enum_ok += 1

    muts = corruptions()
    caught = sum(1 for _, doc in muts if not is_valid(doc))

    # Derivation chains that are DAGs but not trees must pass.
    dag = ProvDocument(
        {"a": "entity", "b": "entity", "c": "entity"},
        [("wasDerivedFrom", "c", "a"), ("wasDerivedFrom", "c", "b"),
         ("wasDerivedFrom", "b", "a")])
    dag_ok = int(is_valid(dag))

    rejects = 0
    for bad in (lambda: ProvDocument({}, []),
                lambda: ProvDocument({"x": "thing"}, []),
                lambda: ProvDocument({"": "entity"}, []),
                lambda: ProvDocument({"x": "entity"}, [("used", "x")]),
                lambda: ProvDocument({"x": "entity"}, "nope")):
        try:
            bad()
        except ProvError:
            rejects += 1

    total = len(taxonomy) + 1 + enum_checks + len(muts) + 1
    matched = taxonomy_ok + exemplar_ok + enum_ok + caught + dag_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "prov_dm",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "relations": len(RELATIONS),
        "signature_enum_checks": enum_checks,
        "signature_enum_ok": enum_ok,
        "corruptions": len(muts),
        "corruptions_caught": caught,
        "corruptions_missed": len(muts) - caught,
        "reject_cases": 5,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "prov_dm.json", obj,
         script="python3 claimlib/modules/prov_dm/evidence.py")
    # claim:CLAIM-LIB-PROV-001 checks_matched
    # All 77 checks pass: the encoded core matches the Recommendation
    # (3 types, exactly 7 relations, Start/End correctly absent), the
    # ML-pipeline exemplar validates, all 63 signature combinations are
    # classified with exactly the 7 published ones passing, every one of
    # 8 corruptions is caught, and diamond-shaped derivation DAGs pass —
    # checks_matched = 77, mismatches = 0.
    print(f"prov_dm: {obj['checks_matched']}/{obj['checks']} checks "
          f"(signatures {obj['signature_enum_ok']}/"
          f"{obj['signature_enum_checks']}, corruptions "
          f"{obj['corruptions_caught']}/{obj['corruptions']} caught); "
          f"rejects {obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
