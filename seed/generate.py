# SPDX-License-Identifier: Apache-2.0
"""Deterministic seed generator for a large VeriClaim corpus.

Produces N artifact-backed claims that pass the gate, to stress-test VeriClaim at
scale. Every number is *computed* from a deterministic synthetic corpus (never
typed by hand): each "document" is derived from sha256(seed || index), and we
measure real properties of it — byte length, run-length compression ratio,
distinct byte count, and lossless round-trip — then bind those numbers through
the register and a documentation anchor, exactly as the discipline requires.

Usage:
    python seed/generate.py            # default N documents
    python seed/generate.py --n 500    # extremely much information

It writes, under seed/:
    artifacts/doc_XXXX.json (+ .provenance.json)   one evidence file per claim
    claims/register.yaml                            N claims
    claims/baseline.json                            empty (green from scratch)
    docs/results.md                                 every claim bound by an anchor
    vericlaim.toml                                  gate config for this workspace
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SEED_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SEED_ROOT.parent
CORPUS_SEED = b"vericlaim-seed-corpus-v1"

# ── deterministic synthetic corpus ──────────────────────────────────────────


def make_document(index: int) -> bytes:
    """A deterministic byte string with real run structure to compress.

    Expand sha256(seed || index) into a stream, then stamp runs of a repeated
    byte at deterministic positions so RLE has something genuine to exploit.
    Same index -> same bytes, on every machine, forever.
    """
    h = hashlib.sha256(CORPUS_SEED + index.to_bytes(4, "big")).digest()
    length = 128 + (h[0] << 1)                 # 128..638 bytes
    stream = bytearray()
    while len(stream) < length:
        stream.extend(hashlib.sha256(bytes(stream) + h).digest())
    stream = stream[:length]
    # Insert a run whose length is derived from the hash: real, deterministic.
    run_byte = h[1]
    run_len = 8 + (h[2] % 48)
    pos = h[3] % max(1, length - run_len)
    for i in range(run_len):
        stream[pos + i] = run_byte
    return bytes(stream)


def rle_encode(data: bytes) -> bytes:
    """Classic byte-oriented RLE: (count, byte) pairs, count capped at 255."""
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        b = data[i]
        run = 1
        while i + run < n and data[i + run] == b and run < 255:
            run += 1
        out.append(run)
        out.append(b)
        i += run
    return bytes(out)


def rle_decode(data: bytes) -> bytes:
    out = bytearray()
    for i in range(0, len(data), 2):
        out.extend([data[i + 1]] * data[i])
    return bytes(out)


_WORDS = ("claim evidence artifact provenance register gate drift anchor "
          "reproduce hash lossless corpus tenant routing ontology grounding "
          "citation snapshot deterministic verified caveat").split()


def make_literature_text(index: int) -> str:
    """A deterministic synthetic 'abstract' to be hash-locked as a citation.

    Not a real paper — a stand-in that exercises the literature-integrity check
    (file must still hash to its registered sha256) at scale.
    """
    h = hashlib.sha256(b"seed-lit-" + index.to_bytes(4, "big")).digest()
    n_words = 40 + h[0] % 40
    words = [_WORDS[(h[i % len(h)] + i) % len(_WORDS)] for i in range(n_words)]
    body = " ".join(words)
    return (f"# Synthetic work {index:04d}\n\n"
            f"Abstract. {body}.\n\n"
            f"Locator: seed-work-{index:04d}; deterministic; hash-locked.\n")


def measure(index: int) -> dict:
    """Real, deterministic measurements of document *index*."""
    doc = make_document(index)
    encoded = rle_encode(doc)
    decoded = rle_decode(encoded)
    ratio = round(len(doc) / len(encoded), 4)
    return {
        "schema": "seed_doc_v1",
        "doc_index": index,
        "byte_length": len(doc),
        "encoded_length": len(encoded),
        "rle_ratio": ratio,
        "distinct_bytes": len(set(doc)),
        "roundtrip_lossless": decoded == doc,
        "sha256_prefix": hashlib.sha256(doc).hexdigest()[:16],
    }


# ── provenance (write sidecars directly; one git call for the whole batch) ──


def git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, cwd=REPO_ROOT, check=True)
        return out.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def write_lf(path: Path, text: str) -> None:
    """Write text with LF endings regardless of OS (no newline translation).

    VeriClaim hashes artifact bytes exactly; Python's text mode would rewrite
    \\n to \\r\\n on Windows and break every provenance hash.
    """
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, obj: dict) -> str:
    text = json.dumps(obj, indent=2) + "\n"
    write_lf(path, text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_provenance(artifact: Path, sha: str, commit: str | None, ts: str) -> None:
    record = {
        "schema": "vericlaim_provenance_v2",
        "artifact": artifact.name,
        "artifact_sha256": sha,
        "script": "python3 seed/generate.py",
        "git_commit": commit,
        "generated_at": ts,
        "produced_by": "seed-generator",
    }
    sidecar = artifact.with_name(artifact.name + ".provenance.json")
    write_lf(sidecar, json.dumps(record, indent=2) + "\n")


# ── register + docs emitters ─────────────────────────────────────────────────

CONFIG = """\
# VeriClaim seed workspace — an isolated, large, deterministic corpus used to
# stress-test the gate at scale. Regenerate with: python seed/generate.py --n N
[vericlaim]
profile             = "adopt"
register            = "claims/register.yaml"
baseline            = "claims/baseline.json"
doc_globs           = ["docs/*.md"]
required_fields     = ["id", "statement", "evidence_level", "artifact", "caveat"]
evidence_levels     = ["theoretical", "measured", "benchmarked", "reproduced", "machine_checked", "externally_validated"]
require_provenance  = true
# Seed artifacts are a regenerable working corpus, not committed evidence.
require_git_tracked = false

[vericlaim.stale_strings]
"""

BASELINE = json.dumps({
    "schema": "vericlaim_baseline_v1",
    "description": "Seed workspace starts green; no grandfathered violations.",
    "known_violations": [],
}, indent=2) + "\n"


def yaml_block(text: str, indent: str) -> str:
    """Emit a YAML folded scalar body, indented."""
    return "\n".join(indent + line for line in text.split("\n"))


def register_entry(cid: str, m: dict, level: str, lit_sha: str) -> str:
    statement = (
        f"Seed document {m['doc_index']:04d} is {m['byte_length']} bytes, "
        f"compresses under run-length encoding at a ratio of {m['rle_ratio']}x, "
        f"uses {m['distinct_bytes']} distinct byte values, and round-trips "
        f"losslessly."
    )
    caveat = (
        "A synthetic, deterministically generated document used to stress-test "
        "the gate at scale. The ratio reflects an artificial run structure, not "
        "any real-world compression result."
    )
    return f"""\
  - id: {cid}
    statement: >
{yaml_block(statement, "      ")}
    evidence_level: {level}
    artifact:
      - "artifacts/doc_{m['doc_index']:04d}.json"
    metrics:
      byte_length: {m['byte_length']}
      rle_ratio: {m['rle_ratio']}
      distinct_bytes: {m['distinct_bytes']}
      roundtrip_lossless: {1 if m['roundtrip_lossless'] else 0}
    caveat: >
{yaml_block(caveat, "      ")}
    literature:
      - source: "Synthetic seed work {m['doc_index']:04d} (deterministic; not a real publication)"
        sha256: {lit_sha}
        file: "literature/work_{m['doc_index']:04d}.txt"
        locator: "seed-work-{m['doc_index']:04d}"
    reproduce: "python3 seed/generate.py"
"""


def doc_entry(cid: str, m: dict) -> str:
    return f"""\
### Document {m['doc_index']:04d}

<!-- claim:{cid} rle_ratio -->
Document {m['doc_index']:04d} ({m['byte_length']} bytes, {m['distinct_bytes']} distinct byte values)
compresses under run-length encoding at a ratio of
<!-- v:{cid}.rle_ratio -->**{m['rle_ratio']}**, and the encode/decode round-trip
is lossless (`roundtrip_lossless = {1 if m['roundtrip_lossless'] else 0}`).
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300, help="number of documents/claims")
    args = ap.parse_args()
    n = args.n

    (SEED_ROOT / "artifacts").mkdir(parents=True, exist_ok=True)
    (SEED_ROOT / "claims").mkdir(parents=True, exist_ok=True)
    (SEED_ROOT / "docs").mkdir(parents=True, exist_ok=True)
    (SEED_ROOT / "literature").mkdir(parents=True, exist_ok=True)

    write_lf(SEED_ROOT / "vericlaim.toml", CONFIG)
    write_lf(SEED_ROOT / "claims" / "baseline.json", BASELINE)

    commit = git_commit()
    ts = datetime.now(timezone.utc).isoformat()
    levels = ["measured", "benchmarked"]

    reg_parts = [
        "---\n",
        "# VeriClaim seed register — GENERATED by seed/generate.py. Do not hand-edit;\n",
        f"# regenerate with: python seed/generate.py --n {n}\n\n",
        'schema_version: "1"\n\n',
        "claims:\n\n",
    ]
    doc_parts = [
        "# Seed corpus results\n\n",
        f"Generated by `seed/generate.py` — {n} deterministic documents, each a "
        "gate-bound claim.\nEvery number below is computed by the generator and "
        "bound to the register.\n\n",
    ]

    for i in range(n):
        m = measure(i)
        cid = f"CLAIM-SEED-{i:04d}"
        artifact = SEED_ROOT / "artifacts" / f"doc_{i:04d}.json"
        sha = write_json(artifact, m)
        write_provenance(artifact, sha, commit, ts)
        lit_text = make_literature_text(i)
        lit_path = SEED_ROOT / "literature" / f"work_{i:04d}.txt"
        write_lf(lit_path, lit_text)
        lit_sha = hashlib.sha256(lit_text.encode("utf-8")).hexdigest()
        reg_parts.append(register_entry(cid, m, levels[i % len(levels)], lit_sha))
        reg_parts.append("\n")
        doc_parts.append(doc_entry(cid, m))
        doc_parts.append("\n")

    write_lf(SEED_ROOT / "claims" / "register.yaml", "".join(reg_parts))
    write_lf(SEED_ROOT / "docs" / "results.md", "".join(doc_parts))

    print(f"seeded {n} claims + artifacts + provenance + bound docs under seed/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
