# SPDX-License-Identifier: Apache-2.0
"""Import a verified library bundle into a target vericlaim project.

The library is DISTRIBUTION, never a source of truth: everything is verified
locally, offline, before a single byte is vendored —

1. the bundle verifies (every file matches the manifest, the manifest matches
   the bundle id);
2. only ``status: verified`` bundles import — candidates are quarantined and
   refuse;
3. content is vendored under ``claims/imported/<claim>-<bundle12>/`` and the
   generated register entry hash-locks it: the vendored ``provenance.json``
   (and any literature files) become `literature` entries with their exact
   SHA-256, so the target repo's OWN gate detects any post-import tampering;
4. the evidence level is the bundle's mapped level and the caveat arrives
   already extended with harvest provenance — the import adds, never removes.

    python3 integrations/library/import_bundle.py --bundle <dir> --target <repo>
"""
from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundlefmt import load_bundle  # noqa: E402


class ImportRefused(ValueError):
    """The bundle must not be imported. Nothing was written."""


def _yaml_block(key: str, text: str, indent: str = "    ") -> str:
    lines = textwrap.wrap(str(text), width=72) or [""]
    body = "\n".join(f"{indent}  {ln}" for ln in lines)
    return f"{indent}{key}: >\n{body}\n"


def _entry_yaml(claim: dict, lit_entries: list[dict]) -> str:
    out = [f"  - id: {claim['id']}\n"]
    out.append(_yaml_block("statement", claim.get("statement", "")))
    out.append(f"    evidence_level: {claim['evidence_level']}\n")
    out.append("    artifact:\n")
    for rel in claim["artifact"]:
        out.append(f'      - "{rel}"\n')
    if claim.get("n") is not None:
        out.append(f"    n: {claim['n']}\n")
    metrics = claim.get("metrics")
    if isinstance(metrics, dict) and metrics:
        out.append("    metrics:\n")
        for k, v in metrics.items():
            out.append(f"      {k}: {v}\n")
    out.append(_yaml_block("caveat", claim.get("caveat", "")))
    out.append("    literature:\n")
    for e in lit_entries:
        out.append(f'      - source: "{e["source"]}"\n')
        out.append(f"        sha256: {e['sha256']}\n")
        out.append(f'        file: "{e["file"]}"\n')
        if e.get("locator"):
            out.append(f'        locator: "{e["locator"]}"\n')
    return "".join(out)


def import_bundle(bundle_dir: Path, target: Path, *,
                  register: str = "claims/register.yaml") -> dict:
    """Verify, vendor, and register a bundle in *target*. Returns a summary."""
    b = load_bundle(Path(bundle_dir))  # raises BundleError on any tampering
    if b["status"] != "verified":
        raise ImportRefused(
            f"bundle {b['bundle_id'][:12]} has status {b['status']!r} — a "
            f"candidate is an unverified assertion and cannot be imported as "
            f"a claim; produce evidence in a gated repo first")
    target = Path(target)
    reg_path = target / register
    if not reg_path.exists():
        raise ImportRefused(f"target has no register at {register} — run "
                            f"`vericlaim init` first")

    claim = dict(b["claim"])
    cid = claim["id"]
    bid = b["bundle_id"]
    vend_rel = Path("claims") / "imported" / f"{cid}-{bid[:12]}"
    vend = target / vend_rel
    if vend.exists():
        raise ImportRefused(f"{vend_rel} already exists — this bundle is "
                            f"already imported")
    if f"- id: {cid}\n" in reg_path.read_text(encoding="utf-8"):
        raise ImportRefused(f"claim id {cid} already present in the target "
                            f"register")

    files = b["manifest"]["files"]
    src_dir = Path(bundle_dir)
    for rel in list(files) + ["MANIFEST.json"]:
        dest = vend / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((src_dir / rel).read_bytes())

    # Register entry: vendored artifact paths + hash-locking literature.
    prov = b["provenance"]
    origin = (f"library bundle {bid} from {prov.get('source_repo', '?')}"
              f"@{str(prov.get('source_commit', ''))[:12]}")
    claim["artifact"] = [f"{vend_rel.as_posix()}/{rel}"
                        for rel in claim.get("artifact", [])]
    lit_entries = [{
        "source": origin,
        "sha256": files["provenance.json"],
        "file": f"{vend_rel.as_posix()}/provenance.json",
        "locator": f"level mapping {prov.get('level_mapping', '?')}; "
                   f"source gate {prov.get('source_gate', '?')}",
    }]
    for rel, sha in sorted(files.items()):
        if rel.startswith("literature/"):
            lit_entries.append({"source": f"{origin} ({rel})", "sha256": sha,
                                "file": f"{vend_rel.as_posix()}/{rel}"})

    reg_text = reg_path.read_text(encoding="utf-8")
    if "claims: []" in reg_text:
        reg_text = reg_text.replace("claims: []", "claims:", 1)
    entry = _entry_yaml(claim, lit_entries)
    reg_path.write_text(reg_text.rstrip("\n") + "\n\n" + entry,
                        encoding="utf-8")
    return {"claim_id": cid, "bundle_id": bid,
            "vendored_dir": vend_rel.as_posix(), "register": register,
            "literature_entries": len(lit_entries)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--target", required=True, type=Path)
    args = ap.parse_args()
    r = import_bundle(args.bundle, args.target)
    print(f"[OK] imported {r['claim_id']} (bundle {r['bundle_id'][:12]}) "
          f"into {r['vendored_dir']} with {r['literature_entries']} "
          f"hash-locking literature entr(ies)")
    print("     run `vericlaim` in the target to confirm the gate is green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
