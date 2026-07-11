# SPDX-License-Identifier: Apache-2.0
"""`vericlaim new-claim` — scaffold a claim the honest way, in one step.

Claim-Oriented Programming has a fixed shape: a deterministic evidence script
writes an artifact, the register cites it, and a doc anchor binds the number.
Typing all three by hand is the friction that makes people skip the discipline.
This command emits all three from one invocation:

    vericlaim new-claim CLAIM-PERF-001 \\
        --statement "The parser handles the 10k-line fixture under 200 ms." \\
        --metric p95_ms=180 --evidence-level benchmarked \\
        --artifact results/parse_bench.json --script bench/parse_bench.py

It writes the evidence SCRIPT (a stub whose measure() you implement — it fails
until you produce a real number, never fabricates one), and prints the register
block and the doc anchor to paste. It never edits your register automatically,
so it cannot corrupt it. Artifact first, always.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .pathsafe import PathSafetyError, check_relpath


def _slug(claim_id: str) -> str:
    return claim_id.lower().replace("-", "_")


def _parse_metrics(pairs: list[str]) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for p in pairs or []:
        if "=" not in p:
            raise ValueError(f"--metric expects key=value, got {p!r}")
        k, _, v = p.partition("=")
        k = k.strip()
        if not k:
            raise ValueError(f"--metric has an empty key: {p!r}")
        metrics[k] = v.strip()
    return metrics


def _num(v: str):
    """Render a metric value as a number when it parses as one, else a string."""
    try:
        i = int(v)
        return i
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v


EVIDENCE_STUB = '''\
# SPDX-License-Identifier: Apache-2.0
"""Evidence for {cid} — produced, never hand-typed.

Implement measure() to compute the claim's numbers from the real thing (parse a
benchmark result, count capabilities, run a checker). The script writes the
artifact and stamps its provenance. Until measure() returns real values this
raises, so `vericlaim reproduce` stays red — that is the point: no number
without evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

# vericlaim ships the provenance stamper; adjust the import to your layout.
try:
    from vericlaim.provenance import stamp
except Exception:  # pragma: no cover - stamp is optional if you inline it
    stamp = None

ARTIFACT = Path(__file__).resolve().parent / "{artifact_name}"
ARTIFACT_REL = "{artifact_rel}"


def measure() -> dict:
    """Return the claim's metrics, COMPUTED from the artifact-producing process.

    Replace the NotImplementedError with a real measurement, e.g.::

        result = json.loads(Path("build/bench.json").read_text())
        return {metric_example}
    """
    raise NotImplementedError("implement measure() with a real measurement")


def main() -> int:
    metrics = measure()
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\\n",
                        encoding="utf-8", newline="\\n")
    if stamp is not None:
        stamp(ARTIFACT_REL, script="python3 {script_rel}")
    print(f"wrote {{ARTIFACT_REL}}: {{metrics}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _register_block(claim_id, statement, evidence_level, artifact, metrics, caveat, script):
    lines = [f"  - id: {claim_id}",
             "    statement: >",
             f"      {statement}",
             f"    evidence_level: {evidence_level}",
             "    artifact:",
             f'      - "{artifact}"']
    if metrics:
        lines.append("    metrics:")
        for k, v in metrics.items():
            val = _num(v)
            lines.append(f"      {k}: {val}")
    lines.append("    caveat: >")
    lines.append(f"      {caveat}")
    lines.append(f'    reproduce: "python3 {script}"')
    return "\n".join(lines) + "\n"


def _doc_anchor(claim_id, metrics):
    if not metrics:
        return f"<!-- claim:{claim_id} -->\n<state the claim in prose here>\n"
    field = next(iter(metrics))
    val = metrics[field]
    return (f"<!-- claim:{claim_id} {field} -->\n"
            f"<your prose> <!-- v:{claim_id}.{field} -->**{val}** <rest of the "
            f"sentence, including the caveat>.\n")


def scaffold(root: Path, *, claim_id: str, statement: str, evidence_level: str,
             artifact: str, script: str, metrics: dict, caveat: str,
             write: bool = True) -> dict:
    """Write the evidence stub and return the register block + doc anchor text."""
    for rel in (artifact, script):
        try:
            check_relpath(rel)
        except PathSafetyError as exc:
            raise ValueError(f"{rel!r} is not a safe repo-relative path: {exc}") from exc

    script_path = root / script
    created = False
    if write:
        if script_path.exists():
            raise ValueError(f"{script} already exists — refusing to overwrite")
        artifact_name = Path(artifact).name
        metric_example = ("{" + ", ".join(f'"{k}": <computed>' for k in metrics) + "}") \
            if metrics else "{}"
        stub = EVIDENCE_STUB.format(
            cid=claim_id, artifact_name=artifact_name, artifact_rel=artifact,
            script_rel=script, metric_example=metric_example)
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(stub, encoding="utf-8", newline="\n")
        created = True

    return {
        "script_created": created,
        "script": script,
        "register_block": _register_block(claim_id, statement, evidence_level,
                                          artifact, metrics, caveat, script),
        "doc_anchor": _doc_anchor(claim_id, metrics),
    }


def add_parser(subparsers, parents) -> None:
    p = subparsers.add_parser(
        "new-claim", parents=parents,
        help="scaffold a claim: evidence-script stub + register block + doc anchor")
    p.add_argument("claim_id", help="e.g. CLAIM-PERF-001")
    p.add_argument("--statement", required=True, help="one-line claim statement")
    p.add_argument("--evidence-level", default="measured",
                   help="theoretical|measured|benchmarked|reproduced|machine_checked|externally_validated")
    p.add_argument("--metric", action="append", default=[], metavar="KEY=VALUE",
                   help="a number the docs will bind (repeatable)")
    p.add_argument("--artifact", default=None,
                   help="artifact path (default: results/<slug>.json)")
    p.add_argument("--script", default=None,
                   help="evidence script path (default: tools/evidence_<slug>.py)")
    p.add_argument("--caveat", default="TODO: state the scope and limitation of this claim.")
    p.add_argument("--no-write", action="store_true",
                   help="print only; do not write the evidence-script stub")


def run(args) -> int:
    root = getattr(args, "root", Path.cwd())
    root = Path(root).resolve()
    slug = _slug(args.claim_id)
    artifact = args.artifact or f"results/{slug}.json"
    script = args.script or f"tools/evidence_{slug}.py"
    try:
        metrics = _parse_metrics(args.metric)
        out = scaffold(root, claim_id=args.claim_id, statement=args.statement,
                       evidence_level=args.evidence_level, artifact=artifact,
                       script=script, metrics=metrics, caveat=args.caveat,
                       write=not args.no_write)
    except ValueError as exc:
        print(f"[FAIL] {exc}")
        return 1

    if out["script_created"]:
        print(f"  created  {out['script']}  (implement measure(); it fails until "
              f"you produce a real number)")
    print("\n# 1. paste into claims/register.yaml (under `claims:`)\n")
    print(out["register_block"])
    print("# 2. bind the number in a doc matched by doc_globs\n")
    print(out["doc_anchor"])
    print("# 3. implement measure(), run the script to write the artifact, then: vericlaim")
    return 0
