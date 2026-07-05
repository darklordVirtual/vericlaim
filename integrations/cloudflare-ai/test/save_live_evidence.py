#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run live_test.py against a deployed Worker and record the outcome as a
claim artifact (with provenance). The artifact is a dated snapshot of a live
system — it is NOT reproducible offline, which is why the claim it backs is
graded `measured` with a staleness caveat and carries no `reproduce` command.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from vericlaim.provenance import stamp  # noqa: E402

ARTIFACT = HERE / "artifacts" / "research_live.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--date", required=True,
                    help="ISO date of the run (recorded in the artifact)")
    args = ap.parse_args()

    proc = subprocess.run(
        [sys.executable, str(HERE / "live_test.py"), "--url", args.url],
        capture_output=True, text=True)
    out = proc.stdout
    m = re.search(r"(\d+)/(\d+) checks passed", out)
    if not m:
        print(out)
        print("could not parse live_test output", file=sys.stderr)
        return 1
    passed, total = int(m.group(1)), int(m.group(2))
    research_checks = {
        name: bool(re.search(rf"\[PASS\] {re.escape(name)}", out))
        for name in ("research summary",
                     "research search finds conformal risk control",
                     "research oracle grounds an answer",
                     "research oracle refuses the off-corpus",
                     "mcp search_literature_rag")
    }
    artifact = {
        "date": args.date,
        "url": args.url,
        "checks_passed": passed,
        "checks_total": total,
        "all_passed": passed == total and proc.returncode == 0,
        "research_checks": research_checks,
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    stamp(str(ARTIFACT.relative_to(ROOT)),
          script=f"python3 integrations/cloudflare-ai/test/"
                 f"save_live_evidence.py --url {args.url} --date {args.date}",
          produced_by="live-test")
    print(out)
    print(f"artifact: {ARTIFACT} ({passed}/{total})")
    return 0 if artifact["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
