# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-HASHCHAIN-001 — the append-only hash chain detects
every single-entry mutation.

Builds a chain over a fixed battery of N=64 entries, confirms the untouched
chain verifies, then applies EVERY single-entry mutation (three deterministic
mutation kinds per entry: full replace, byte prepend, first-byte bitflip) and
confirms verify() returns False for each one. The metric tamper_detected is the
real count of mutations caught — measured, not assumed. Deterministic: same
artifact on every run (entries, mutations and hashes are all fixed).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (hashchain.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from hashchain import build_chain, verify  # noqa: E402
from _util import emit  # noqa: E402

N_ENTRIES = 64


def reference_entries() -> list[bytes]:
    """The fixed, deterministic entry battery (64 distinct non-empty records)."""
    return [f"vericlaim-hashchain-record-{i:04d}".encode("ascii")
            for i in range(N_ENTRIES)]


def mutations_for(entries: list[bytes], i: int) -> list[tuple[str, bytes]]:
    """Return the deterministic single-entry mutations of entry *i*.

    Each mutation is (kind, new_entry_value) and is guaranteed to differ from
    the original entry, so a correct chain MUST reject every one of them:
      * replace          - swap the whole entry for a distinct sentinel
      * prepend_byte      - prepend a NUL byte (changes length, so differs)
      * bitflip_first     - flip the low bit of the first byte
    """
    original = entries[i]
    return [
        ("replace", f"TAMPERED-{i:04d}".encode("ascii")),
        ("prepend_byte", b"\x00" + original),
        ("bitflip_first", bytes([original[0] ^ 0x01]) + original[1:]),
    ]


def run() -> dict:
    entries = reference_entries()
    chain = build_chain(entries)

    untampered_ok = verify(entries, chain)

    kinds = ("replace", "prepend_byte", "bitflip_first")
    by_kind = {k: {"tested": 0, "detected": 0} for k in kinds}
    tested = 0
    detected = 0

    for i in range(len(entries)):
        for kind, new_value in mutations_for(entries, i):
            # Only a genuine change counts as a mutation under test.
            if new_value == entries[i]:
                continue
            mutated = list(entries)
            mutated[i] = new_value
            tested += 1
            by_kind[kind]["tested"] += 1
            # A tamper is "detected" when verify rejects the mutated entries
            # against the ORIGINAL (untampered) chain of head digests.
            if verify(mutated, chain) is False:
                detected += 1
                by_kind[kind]["detected"] += 1

    return {
        "schema": "claimlib_hashchain_v1",
        "module": "hashchain",
        "hash": "sha256",
        "construction": "record_hash(prev, entry) = sha256(prev || entry)",
        "n_entries": N_ENTRIES,
        "tamper_mutations_tested": tested,
        "tamper_detected": detected,
        "tamper_missed": tested - detected,
        "untampered_verifies": untampered_ok,
        "head_hex": chain[-1],
        "by_mutation_type": by_kind,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "hashchain.json", obj,
         script="python3 claimlib/modules/hashchain/evidence.py")
    # claim:CLAIM-LIB-HASHCHAIN-001 tamper_detected
    # Over the fixed battery of 64 entries, every single-entry mutation is
    # caught: 3 deterministic mutations per entry (replace, prepend_byte,
    # bitflip_first) give 64 * 3 = 192 mutations tested, and all 192 are
    # detected, so tamper_detected = 192 and tamper_missed = 0.
    print(f"hashchain: {obj['tamper_detected']}/{obj['tamper_mutations_tested']} "
          f"single-entry mutations detected over {obj['n_entries']} entries "
          f"(missed={obj['tamper_missed']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
