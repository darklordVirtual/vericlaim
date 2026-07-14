# SPDX-License-Identifier: Apache-2.0
"""The claimlib registry - reusable, claim-bound code artifacts across Python,
TypeScript and React. GENERATED/maintained alongside claimlib/build.py. Each
entry describes one module; build.py runs its evidence, reads the metrics, and
emits the aggregated register, per-module docs, README and one vendorable
bundle_v1 per module. 'lang' selects the toolchain (python|typescript|react).
"""
from __future__ import annotations

MODULES = [
    {
        "name": "cvss",
        "lang": "python",
        "claim_id": "CLAIM-LIB-CVSS-001",
        "references": ["cvss-v3.1"],
        "title": "CVSS v3.1 base scoring",
        "area": "Security / Vulnerability Management",
        "evidence_level": "benchmarked",
        "code_files": [
            "cvss.py"
        ],
        "artifact": "cvss.json",
        "register_metrics": [
            "reference_vectors_matched",
            "reference_vectors",
            "mismatches"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored CVSS v3.1 base-score scorer reproduces all published reference base scores in a fixed set exactly, with 0 mismatches — including scope change and the v3.1 Roundup rule.",
        "caveat": "Base metric group only (no temporal or environmental modifiers). Correctness is demonstrated over a fixed published-reference vector set, not proven for every possible vector.",
        "knowledge": "CVSS v3.1 turns an attack vector, complexity, privileges, user interaction, scope and CIA impact into a 0.0-10.0 base score. This module parses the standard `CVSS:3.1/...` vector string and applies the published FIRST formula (impact, exploitability, scope, Roundup). Vendor it to score vulnerabilities consistently; the claim proves the arithmetic matches the reference, so you inherit a checked scorer, not a re-implementation to re-audit."
    },
    {
        "name": "hashchain",
        "lang": "python",
        "claim_id": "CLAIM-LIB-HASHCHAIN-001",
        "references": ["haber-1991", "fips-180-4"],
        "title": "Tamper-evident append-only hash chain",
        "area": "Security / Data Integrity",
        "evidence_level": "measured",
        "code_files": [
            "hashchain.py"
        ],
        "artifact": "hashchain.json",
        "register_metrics": [
            "n_entries",
            "tamper_mutations_tested",
            "tamper_detected",
            "tamper_missed"
        ],
        "bind_field": "tamper_detected",
        "statement": "The vendored append-only hash chain (record hash = sha256(prev || entry)) detects every single-entry mutation over a fixed 64-entry battery: all 192 mutations tested (64 entries x 3 deterministic kinds -- full replace, byte prepend, first-byte bitflip) are caught, with tamper_missed = 0. The untampered chain verifies True, and correctness is cross-checked against an independent raw-hashlib oracle.",
        "caveat": "Detection is demonstrated over a fixed reference battery of single-entry mutations, not proven for every possible input. It is tamper-EVIDENT, not tamper-PROOF: an adversary who can rewrite the stored chain of head digests alongside the entries can forge a consistent history, so authenticate the head (HMAC or a signature) for adversarial settings. Security also rests on SHA-256 collision resistance.",
        "knowledge": "A hash chain makes an append-only log self-authenticating: each record's hash folds in the previous record's hash, so the head digest commits to the entire ordered history -- the same idea behind Git commit graphs and blockchain blocks. Changing, inserting, deleting or reordering any past entry changes that record's hash and every hash after it, so recomputing the chain from the claimed entries and comparing digests reveals the tampering. Vendor it to get an integrity-checked audit log or ledger; the claim proves the construction catches the enumerated mutations, so you inherit a checked primitive rather than a re-implementation to re-audit. For untrusted storage, sign or HMAC the head so the chain itself cannot be silently rewritten."
    },
    {
        "name": "merkle",
        "lang": "python",
        "claim_id": "CLAIM-LIB-MERKLE-001",
        "references": ["merkle-1988", "rfc-6962", "fips-180-4"],
        "title": "Merkle tree SHA-256 inclusion proofs",
        "area": "Security / Cryptographic Integrity",
        "evidence_level": "measured",
        "code_files": [
            "merkle.py"
        ],
        "artifact": "merkle.json",
        "register_metrics": [
            "n_leaves",
            "proofs_verified",
            "tampered_rejected",
            "false_accepts"
        ],
        "bind_field": "proofs_verified",
        "statement": "The vendored SHA-256 binary Merkle tree produces inclusion proofs that all verify against the committed root (proofs_verified = n_leaves) over a fixed 9-leaf battery, and rejects every single-leaf tamper (tampered_rejected = 9) with false_accepts = 0; the built root is additionally cross-checked byte-for-byte against an independent from-scratch reference computation.",
        "caveat": "Demonstrated over one fixed 9-leaf battery (which does exercise the odd-level duplicate-last-node rule at three levels), not proven for all tree shapes or inputs. The hashing scheme intentionally omits RFC 6962 leaf/node domain-separation tags, so roots are not second-preimage resistant across trees of differing leaf counts; tampering evidence covers leaf-content mutation, not adversarial proof forgery.",
        "knowledge": "A Merkle tree hashes an ordered list of leaves pairwise up to a single root digest, so any party holding the root can verify that a given leaf is included via a short O(log n) audit path of sibling hashes rather than re-hashing the whole set. This module uses sha256 with the Bitcoin-style duplicate-last-node rule for odd levels (documented explicitly so proofs are portable), exposing build_root, inclusion_proof, and verify_proof. Vendor it for tamper-evident logs, transparency/commitment schemes, or content addressing; the claim proves proofs verify and leaf tampering is caught, so you inherit a checked implementation rather than an unaudited re-write."
    },
    {
        "name": "rle",
        "lang": "python",
        "claim_id": "CLAIM-LIB-RLE-001",
        "title": "Byte run-length codec (lossless round-trip)",
        "area": "Data / Compression",
        "evidence_level": "benchmarked",
        "code_files": [
            "rle.py"
        ],
        "artifact": "rle.json",
        "register_metrics": [
            "n_cases",
            "roundtrip_lossless",
            "overall_ratio"
        ],
        "bind_field": "roundtrip_lossless",
        "statement": "The vendored byte-oriented run-length codec round-trips losslessly on every case in a fixed, diverse corpus (long runs, sparse spikes, deterministic pseudo-random noise, structured text, and the empty string): decode(encode(x)) == x for all 15 cases (roundtrip_lossless == n_cases), verified by exact byte equality against the original input, not against the codec's own output.",
        "caveat": "RLE is a compressor only for redundant data: it EXPANDS low-redundancy input to two output bytes per symbol, so overall_ratio can fall below 1.0 (0.6649 on this corpus, which is deliberately noise-heavy). The claim proves lossless round-trip, not a compression guarantee, and correctness is demonstrated over a fixed corpus rather than proven for every possible input.",
        "knowledge": "Run-length encoding is the simplest lossless compression scheme: it replaces each maximal run of identical symbols with a (count, symbol) pair, shrinking long uniform stretches (bitmaps, sparse buffers, padded records) while leaving a total, exactly invertible mapping. This module implements the classic byte-pair variant, splitting runs longer than 255 across pairs so any bytes input encodes and decodes back byte-for-byte. Vendor it when you need a dependency-free, auditable codec whose inverse is proven; the claim binds the round-trip property so you inherit a checked codec rather than a re-implementation to re-audit."
    },
    {
        "name": "luhn",
        "lang": "python",
        "claim_id": "CLAIM-LIB-LUHN-001",
        "references": ["luhn-1960", "iso-7812-1"],
        "title": "Luhn (mod-10) checksum",
        "area": "Payments / Data Integrity",
        "evidence_level": "measured",
        "code_files": [
            "luhn.py"
        ],
        "artifact": "luhn.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored Luhn (mod-10) implementation classifies every number in a fixed table of 12 independently-known cases correctly — 8 known-valid (the Wikipedia example, published Visa/Mastercard/Amex/Discover/Diners test cards, and a trivial single-zero) and 4 known-invalid (off-by-one and non-Luhn sequences) — with 0 errors, and its check_digit() reproduces the trailing check digit of each valid reference number.",
        "caveat": "Correctness is demonstrated over a fixed reference table of published test numbers, not proven for all inputs. Luhn is a check-digit scheme that catches all single-digit errors and most adjacent transpositions; it is a data-entry checksum, NOT a cryptographic integrity or authenticity guarantee, and validity does not imply a number is real or issued.",
        "knowledge": "The Luhn algorithm (ISO/IEC 7812-1, the 'mod 10' formula) is the check-digit standard used to catch typos in payment card numbers, IMEIs, and many national IDs. Working right-to-left it doubles every second digit (subtracting 9 when the result exceeds 9), sums all digits, and treats the number as valid when that total is a multiple of 10. This module exposes is_valid() to check a full number and check_digit() to compute the digit that completes a partial one; vendor it to validate identifiers at data-entry time and inherit a checked implementation rather than re-auditing another hand-rolled loop."
    },
    {
        "name": "semver",
        "lang": "python",
        "claim_id": "CLAIM-LIB-SEMVER-001",
        "references": ["semver-2.0.0"],
        "title": "Semantic Versioning 2.0.0 compare + range grammar",
        "area": "Software Supply Chain / Dependency Resolution",
        "evidence_level": "measured",
        "code_files": [
            "semver.py"
        ],
        "artifact": "semver.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored SemVer 2.0.0 library reproduces every required answer over a fixed 46-row reference battery (18 precedence comparisons drawn verbatim from the spec's golden ordering chain plus core/build/numeric-vs-alnum rules, and 28 satisfies rows over exact/>=/</caret/tilde ranges): correct = 46 with 0 errors. parse rejects malformed input and leading zeros; compare honors pre-release < release, numeric-below-alphanumeric, and larger-identifier-set precedence; build metadata is ignored for ordering.",
        "caveat": "Range grammar is deliberately modest: only exact 'x.y.z', '>=x.y.z', '<x.y.z', caret '^x.y.z', and tilde '~x.y.z' (no OR/hyphen/x-ranges, no '<=', '>', '!='). Ranges are evaluated purely by SemVer 2.0.0 precedence against derived bounds, so a pre-release is included or excluded strictly by section 11 precedence (e.g. 2.0.0-alpha counts as < 2.0.0) rather than npm's extra same-tuple pre-release exclusion heuristic. Correctness is demonstrated over a fixed reference battery, not proven for every possible input.",
        "knowledge": "Semantic Versioning encodes MAJOR.MINOR.PATCH plus optional pre-release and build metadata, and defines a strict precedence order (spec section 11): core compared numerically, a pre-release ranked below its associated release, and pre-release identifiers compared left-to-right with numeric identifiers below alphanumeric ones. Package managers layer range operators on top of this ordering (caret pins the left-most non-zero element, tilde allows patch-level drift) to decide which published versions an install may resolve to. Vendor this module to compare versions and evaluate those common ranges consistently; the claim proves the precedence arithmetic and range bounds match the spec, so you inherit a checked resolver rather than a re-implementation to re-audit."
    },
    {
        "name": "tokenbucket",
        "lang": "python",
        "claim_id": "CLAIM-LIB-TOKENBUCKET-001",
        "references": ["rfc-2697"],
        "title": "Token-bucket rate limiter (capacity invariant)",
        "area": "Reliability / Rate Limiting",
        "evidence_level": "measured",
        "code_files": [
            "tokenbucket.py"
        ],
        "artifact": "tokenbucket.json",
        "register_metrics": [
            "n_events",
            "allowed",
            "denied",
            "capacity_violations"
        ],
        "bind_field": "capacity_violations",
        "statement": "The vendored token-bucket rate limiter enforces its capacity invariant with 0 capacity_violations across a fixed 8-event chronological trace: the number of available tokens is clamped to capacity on every refill, so even a long idle gap (t=10s, which would otherwise bank 8 tokens) never grants more than a full bucket's burst (measured allowed=6, denied=2).",
        "caveat": "The invariant is demonstrated over one fixed trace (capacity=3, refill=1/s, unit cost) plus unit tests, not proven for every capacity/rate/cost combination; the limiter is time-injected (the caller supplies monotonic timestamps) and uses IEEE-754 floats, so it does not measure wall-clock time itself and is subject to normal floating-point rounding.",
        "knowledge": "A token bucket is the classic rate-limiting primitive: a bucket holds up to `capacity` tokens and refills at a steady `refill_per_sec`, and each request spends tokens, so short bursts pass (up to the bucket depth) while the long-run average rate stays bounded. Its key safety property is that refills are clamped at capacity, so accumulated idle time can never be banked into an unbounded later burst. This module makes time an explicit argument to every call, which removes hidden wall-clock reads and makes limiter behaviour fully deterministic and testable. Vendor it to meter API quotas or traffic consistently and inherit a checked capacity invariant rather than re-auditing another ad-hoc limiter."
    },
    {
        "name": "retry",
        "lang": "python",
        "claim_id": "CLAIM-LIB-RETRY-001",
        "references": ["brooker-2015"],
        "title": "Deterministic exponential backoff with full jitter",
        "area": "Reliability / Distributed Systems",
        "evidence_level": "measured",
        "code_files": [
            "retry.py"
        ],
        "artifact": "retry.json",
        "register_metrics": [
            "n_attempts",
            "within_bounds",
            "out_of_bounds",
            "deterministic"
        ],
        "bind_field": "within_bounds",
        "statement": "The vendored full-jitter backoff computes each delay as a hash-seeded draw from [0, min(cap, base*2**attempt)]: over a fixed 16-attempt reference schedule (attempts 0..15, base=1.0, cap=60.0, seed=1337) all 16 delays land inside their independently-computed [0, ceiling] window (within_bounds=16, out_of_bounds=0), and a seeded replay reproduces the schedule byte-for-byte (deterministic=1).",
        "caveat": "Bounds and reproducibility are demonstrated over one fixed schedule (fixed base/cap/seed, attempts 0..15), not proven for every parameter combination. The jitter is a deterministic SHA-256 spreading function, not a cryptographically unpredictable PRNG, and delays are rounded to 6 decimals for byte-stable serialization.",
        "knowledge": "Retrying a failed remote call immediately, in lockstep with every other client, produces a synchronized 'thundering herd' that keeps the dependency down. Capped exponential backoff (min(cap, base*2**attempt)) grows the wait between attempts, and 'full jitter' (AWS, 2015) then draws the actual delay uniformly from [0, that ceiling] so clients decorrelate instead of all firing at the ceiling. This module keeps full jitter's spread but derives the draw from a SHA-256 hash of (seed, attempt) rather than a PRNG, so the schedule is reproducible in tests and logs and identical across processes, while different seeds still decorrelate different clients."
    },
    {
        "name": "rbac",
        "lang": "python",
        "claim_id": "CLAIM-LIB-RBAC-001",
        "references": ["incits-359-2012", "saltzer-1975"],
        "title": "RBAC least-privilege & separation-of-duties audit",
        "area": "Security / Identity & Access Management",
        "evidence_level": "measured",
        "code_files": [
            "rbac.py"
        ],
        "artifact": "rbac.json",
        "register_metrics": [
            "n_identities",
            "seeded_excess",
            "detected_excess",
            "seeded_sod",
            "detected_sod",
            "false_positives"
        ],
        "bind_field": "detected_excess",
        "statement": "The vendored RBAC auditor detects every seeded over-privilege and separation-of-duties finding in a fixed 13-identity access matrix: all 6 excess grants (detected_excess == seeded_excess == 6) and all 3 toxic-pair violations (detected_sod == seeded_sod == 3), with 0 false positives — no hand-verified clean identity is ever flagged.",
        "caveat": "Recall and the zero-false-positive property are measured over one fixed, hand-seeded reference matrix, not proven for arbitrary inputs. The checker compares held permissions against a supplied least-privilege baseline and explicit SoD pairs; it does not infer baselines, expand role hierarchies/inheritance, or model attribute- or time-based conditions, and its correctness is only as good as the role_needs and sod_pairs it is given.",
        "knowledge": "Role-Based Access Control grants permissions to roles and assigns roles to identities; two enduring control objectives sit on top of it. Least privilege says an identity should hold no permission its role does not need — anything extra ('excess') is attack surface and audit debt. Separation of duties says certain permissions are toxic in combination (create a payment AND approve it; deploy code AND review it) and must never rest with one identity, even when a mis-scoped role would technically allow both. This module makes both checks mechanical and independent, so an over-broad role cannot silently launder an SoD violation into 'authorized'."
    },
    {
        "name": "errorbudget",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ERRORBUDGET-001",
        "references": ["google-sre-2016"],
        "title": "SLO / error-budget arithmetic",
        "area": "SRE / Reliability Engineering",
        "evidence_level": "measured",
        "code_files": [
            "errorbudget.py"
        ],
        "artifact": "errorbudget.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored SLO / error-budget calculator reproduces the textbook SRE availability, error-budget, and budget-remaining formulas exactly on every one of a fixed 9-row hand-computed reference battery (correct = 9, errors = 0), including budget-exhaustion, overspend (negative remaining), zero-downtime, and 4-dp rounding edge cases.",
        "caveat": "Correctness is demonstrated over a fixed hand-computed reference table (9 rows), not proven for every possible input. It is pure time-window arithmetic on a single SLO window: it does not model burn-rate alerting, multi-window/multi-burn-rate policies, request-ratio (event-based) SLOs, or rolling windows. Availability and remaining% are rounded to 4 dp and the budget to 6 dp for byte-stable artifacts.",
        "knowledge": "Site Reliability Engineering measures a service against a Service Level Objective (SLO) — e.g. 99.9% availability over 30 days. The complement of the SLO is the error budget: the amount of downtime the target permits over the window (budget = window * (1 - SLO/100)). Teams spend that budget on risk — releases, experiments, incidents — and 'budget remaining' tracks how much allowance is left before the SLO is breached, going negative once overspent. Vendor this module to compute availability and error budgets consistently; the claim proves the arithmetic matches the published formulas, so you inherit a checked calculator rather than a re-implementation to re-audit."
    },
    {
        "name": "result",
        "lang": "typescript",
        "claim_id": "CLAIM-LIB-RESULT-001",
        "references": ["wadler-1995"],
        "title": "Result<T, E> typed error handling",
        "area": "TypeScript / Error Handling",
        "evidence_level": "benchmarked",
        "code_files": [
            "result.ts"
        ],
        "artifact": "result.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored TypeScript Result<T, E> combinators (ok, err, map, mapErr, andThen, unwrapOr, isOk, isErr, fromThrowing) produce the expected outcome on every one of a fixed reference battery whose expected values are written independently of the module (correct = n_cases, errors = 0), covering ok/err propagation, monadic short-circuiting, and throw capture.",
        "caveat": "Correctness is demonstrated over a fixed reference battery, not proven for all inputs, and the evidence checks runtime behaviour (run with node) — it does not assert the module type-checks under a specific tsc strictness. Result is a value-level discipline; it does not stop you ignoring an Err you never inspect.",
        "knowledge": "Result<T, E> makes failure a value instead of a thrown exception: a function returns Ok<T> on success or Err<E> on failure, and the caller must handle both branches before reaching the value. Combinators (map, mapErr, andThen) thread the happy path and short-circuit on the first error, the way Rust's Result or fp-ts's Either do. Vendor it to get exhaustive, type-checked error handling in TypeScript with zero dependencies; the claim proves the combinators behave as specified, so you inherit a checked primitive rather than a re-implementation to re-audit."
    },
    {
        "name": "usePagination",
        "lang": "react",
        "claim_id": "CLAIM-LIB-USEPAGINATION-001",
        "title": "usePagination React hook",
        "area": "React / UI State",
        "evidence_level": "benchmarked",
        "code_files": [
            "usePagination.tsx",
            "pagination.logic.ts"
        ],
        "artifact": "usePagination.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors",
            "invalid_inputs_rejected"
        ],
        "bind_field": "correct",
        "statement": "The pure pagination core behind the usePagination React hook computes the correct page window (page clamp, slice indices, item count, prev/next flags) on every one of a fixed reference battery with independently hand-written expected windows (correct = n_cases, errors = 0), and fails closed on all 4 invalid-sizing inputs.",
        "caveat": "The claim covers the framework-agnostic core (pagination.logic.ts) run under node, NOT React runtime rendering: the vendored usePagination.tsx is a thin, reviewed binding over that core (useState + useMemo) and is shipped but not rendered in the evidence. Correctness is over a fixed battery, not proven for all inputs.",
        "knowledge": "A huge share of React bugs live in state logic, not markup. The effective pattern is to put the logic in a pure, framework-agnostic function and make the hook a thin binding — so the hard part is unit-testable without a DOM. usePagination does exactly that: pagination.logic.ts computes the clamped page, slice indices and prev/next flags, and usePagination.tsx wraps it in useState/useMemo. Vendor both; the claim proves the core is correct, so you inherit checked pagination state rather than re-deriving off-by-one slice math in every project."
    },
    {
        "name": "crc32",
        "lang": "python",
        "claim_id": "CLAIM-LIB-CRC32-001",
        "references": ["ieee-802-3", "rfc-1952"],
        "title": "CRC-32 (IEEE 802.3) checksum",
        "area": "Data / Integrity & Checksums",
        "evidence_level": "measured",
        "code_files": [
            "crc32.py"
        ],
        "artifact": "crc32.json",
        "register_metrics": [
            "reference_vectors_matched",
            "reference_vectors",
            "mismatches"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored CRC-32 (IEEE 802.3, reflected poly 0xEDB88320) implementation reproduces every value in a fixed 291-vector reference set exactly, with 0 mismatches: the 3 published check values (crc32(b\"\")==0, crc32(b\"123456789\")==0xCBF43926, crc32 of the lazy-dog pangram==0x414FA339) plus 288 byte strings cross-checked for exact equality against the independent stdlib oracle zlib.crc32, so reference_vectors_matched == reference_vectors == 291.",
        "caveat": "Correctness is demonstrated over a fixed reference set (3 published check values plus 288 byte strings agreeing with zlib.crc32), not proven for every possible input. CRC-32 is an error-DETECTION checksum for accidental corruption, NOT a cryptographic hash or MAC: it is linear and trivially forgeable, so it provides no integrity or authenticity guarantee against an adversary.",
        "knowledge": "CRC-32 (IEEE 802.3) is the cyclic redundancy check used by zip, gzip, PNG and Ethernet to catch accidental data corruption. It treats the message as a polynomial over GF(2) and computes the remainder modulo the reflected generator polynomial 0xEDB88320, with input/output reflected and init/final XOR of 0xFFFFFFFF, yielding an unsigned 32-bit value. This module implements the standard byte-wise table algorithm directly (no zlib inside), so you can vendor a dependency-free checksum; the claim proves it matches the published check vectors and agrees byte-for-byte with zlib.crc32, so you inherit a checked implementation rather than a re-implementation to re-audit."
    },
    {
        "name": "base32",
        "lang": "python",
        "claim_id": "CLAIM-LIB-BASE32-001",
        "references": ["rfc-4648"],
        "title": "RFC 4648 base32 encode/decode",
        "area": "Data / Encoding",
        "evidence_level": "measured",
        "code_files": [
            "base32.py"
        ],
        "artifact": "base32.json",
        "register_metrics": [
            "reference_vectors_matched",
            "reference_vectors",
            "mismatches"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored RFC 4648 base32 codec passes all 17 reference checks with 0 mismatches: it reproduces every one of the 7 RFC 4648 section 10 test vectors exactly (b\"\"->\"\", b\"f\"->\"MY======\", ... b\"foobar\"->\"MZXW6YTBOI======\"), and over 10 fixed byte inputs its encode/decode agree byte-for-byte with Python's stdlib base64.b32encode/b32decode (an independent oracle the module never calls) while round-tripping decode(encode(x)) == x exactly.",
        "caveat": "Standard RFC 4648 base32 alphabet with '=' padding only (no base32hex, no Crockford variant, and case-sensitive decoding). Correctness is demonstrated over a fixed reference set of published vectors plus stdlib cross-checks, not proven for every possible input. base64 is used solely as the evidence/test oracle and is never invoked inside the vendored module.",
        "knowledge": "Base32 (RFC 4648) encodes arbitrary bytes into a 32-character, case-insensitive-friendly alphabet (A-Z, 2-7), packing every 5 input bytes into 8 output symbols and padding a short final group with '=' — useful where the output must survive case-folding or be spoken/typed (TOTP secrets, DNS labels, filenames). This module implements the bit-packing directly rather than delegating to a library, exposing encode(bytes)->str and its exact inverse decode(str)->bytes, which fails closed on bad length, unknown symbols, or malformed padding. Vendor it for a dependency-free, auditable codec; the claim binds the RFC vectors and stdlib-oracle agreement, so you inherit a checked encoder rather than a re-implementation to re-audit."
    },
    {
        "name": "jsonpointer",
        "lang": "python",
        "claim_id": "CLAIM-LIB-JSONPOINTER-001",
        "references": ["rfc-6901"],
        "title": "RFC 6901 JSON Pointer resolution",
        "area": "Data / JSON Processing",
        "evidence_level": "measured",
        "code_files": [
            "jsonpointer.py"
        ],
        "artifact": "jsonpointer.json",
        "register_metrics": [
            "reference_cases",
            "reference_cases_passed",
            "failures"
        ],
        "bind_field": "reference_cases_passed",
        "statement": "The vendored RFC 6901 JSON Pointer resolver reproduces every published result in RFC 6901 section 5's worked example — the exact example document evaluated at all 12 example pointers (\"\" -> whole document, \"/foo\" -> [\"bar\",\"baz\"], \"/foo/0\" -> \"bar\", \"/\" -> 0, \"/a~1b\" -> 1, \"/c%d\" -> 2, \"/e^f\" -> 3, \"/g|h\" -> 4, \"/i\\\\j\" -> 5, \"/k\\\"l\" -> 6, \"/ \" -> 7, \"/m~0n\" -> 8) — with reference_cases_passed = 12 and failures = 0, including the ~1 and ~0 unescaping (in that order) and the empty-pointer whole-document case.",
        "caveat": "Correctness is demonstrated over RFC 6901's single published example set (12 pointers), not proven for every possible document or pointer. resolve raises KeyError on a missing object member and IndexError on an out-of-range, non-numeric, leading-zero, or '-' array index (it resolves an existing pointer rather than implementing JSON Pointer's URI-fragment '#' form or the RFC 6902 add/append semantics of '-').",
        "knowledge": "A JSON Pointer (RFC 6901) is a compact string that identifies one value inside a JSON document: the empty string references the whole document, and otherwise a sequence of '/'-separated reference tokens walks object members by key and array elements by base-10 index. Because '/' and '~' are structural, they are escaped inside a token as ~1 and ~0 and must be unescaped ~1-before-~0 so that a literal '~1' round-trips. Vendor this module to dereference config paths, JSON Patch targets, or API response fields consistently; the claim proves it matches the RFC's own example evaluations, so you inherit a checked resolver rather than a re-implementation to re-audit."
    },
    {
        "name": "lru",
        "lang": "python",
        "claim_id": "CLAIM-LIB-LRU-001",
        "references": ["mattson-1970"],
        "title": "Fixed-capacity LRU cache",
        "area": "Data Structures / Caching",
        "evidence_level": "measured",
        "code_files": [
            "lru.py"
        ],
        "artifact": "lru.json",
        "register_metrics": [
            "n_operations",
            "operations_correct",
            "mismatches"
        ],
        "bind_field": "operations_correct",
        "statement": "The vendored fixed-capacity LRU cache reproduces the correct behaviour on every operation of two hand-traced batteries (a capacity-3 mixed trace exercising hit-refresh, capacity eviction, and update-in-place, plus the canonical LeetCode-146 capacity-2 example): all 21 operations match their independently hand-computed get-results AND post-operation key sets (operations_correct = 21, mismatches = 0), and the cache size never exceeds capacity at any step.",
        "caveat": "Correctness is demonstrated over two fixed, hand-derived operation traces (21 operations total), not proven for every possible sequence. Expected get-results and key sets are hand-computed in the evidence, never read back from the cache. The cache is single-threaded and not safe for concurrent mutation, holds strong references to keys/values (no TTL or weak-reference eviction), and uses least-RECENTLY-used as its only eviction policy (not LFU/size/cost-aware).",
        "knowledge": "An LRU cache bounds memory by keeping at most `capacity` entries and, when full, evicting the key that has gone longest without being read or written -- the workhorse policy behind page caches, HTTP/object caches, and memoization tables. The classic O(1) implementation pairs a hash map with a recency-ordered linked list so both lookup and eviction are constant time; this module uses Python's `collections.OrderedDict` (move_to_end / popitem) to get the same behaviour in pure stdlib. Vendor it to add a checked, dependency-free cache; the claim proves the recency and eviction semantics match hand-derived reference traces, so you inherit a checked data structure rather than a re-implementation with an off-by-one eviction bug to re-audit."
    },
    {
        "name": "deepEqual",
        "lang": "typescript",
        "claim_id": "CLAIM-LIB-DEEPEQUAL-001",
        "references": ["ecma-262-2024"],
        "title": "deepEqual structural deep equality",
        "area": "TypeScript / Data Comparison",
        "evidence_level": "benchmarked",
        "code_files": [
            "deepEqual.ts"
        ],
        "artifact": "deepEqual.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored TypeScript deepEqual(a, b) structural equality function returns the expected boolean on every one of a fixed 42-row reference battery whose expected values are hand-written independently of the module (correct = n_cases = 42, errors = 0), covering primitives, NaN-equals-NaN, null-distinct-from-undefined, arrays (length + element-wise), plain objects (identical key-set + recursive values, key-order irrelevant, undefined-value-vs-absent-key distinct), Date-by-getTime, and differing-type mismatches.",
        "caveat": "Correctness is demonstrated over a fixed reference battery, not proven for all inputs, and the evidence checks runtime behaviour (run with node) rather than asserting a specific tsc strictness. Cyclic structures are explicitly out of scope (a self-referential input recurses until stack overflow), and the plain-object comparison covers own enumerable string keys only -- not Maps, Sets, RegExps, typed arrays, symbol keys, or prototype/class identity.",
        "knowledge": "Deep equality compares two values by structure rather than by reference: two distinct objects are equal when their contents match recursively, unlike the === operator which only reports reference identity for objects. The subtle edges are the ones JavaScript gets 'wrong' by default -- NaN !== NaN (so a structural comparator must special-case it to true), Dates and arrays need element/timestamp comparison, and an explicit `{a: undefined}` must stay distinct from `{}`. Vendor it for test assertions, memoization/change-detection, and cache-key checks; the claim proves the comparator handles these edges as specified, so you inherit a checked primitive rather than a re-implementation to re-audit."
    },
    {
        "name": "cx",
        "lang": "typescript",
        "claim_id": "CLAIM-LIB-CX-001",
        "title": "cx classnames combiner",
        "area": "TypeScript / UI Utilities",
        "evidence_level": "measured",
        "code_files": [
            "cx.ts"
        ],
        "artifact": "cx.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored TypeScript cx classnames combiner produces the expected space-separated string on every one of a fixed 14-case reference battery whose expected outputs are hand-written literals independent of the module (correct = n_cases = 14, errors = 0), covering strings, numbers (nonzero kept, 0/NaN dropped), recursively flattened arrays, { className: boolean } objects (truthy keys only), skipped falsy inputs, preserved document order, and preserved duplicates.",
        "caveat": "Correctness is demonstrated over a fixed reference battery, not proven for all inputs, and the evidence checks runtime behaviour (run with node) rather than asserting the module type-checks under a specific tsc strictness. De-duplication is intentionally NOT performed and document order is preserved, so repeated tokens appear multiple times; the caller is responsible for any dedupe. Objects are iterated in Object.keys order; symbol keys and non-string/number/array/object token types contribute nothing.",
        "knowledge": "A classnames combiner assembles the `class` attribute for a component from a mix of static strings and conditional flags, so you write cx(\"btn\", { active: isActive }, isLarge && \"btn-lg\") instead of hand-splicing strings and stray spaces. This is the ubiquitous `classnames`/`clsx` pattern: truthy tokens are joined with single spaces and every falsy value is dropped, with nested arrays flattened and object keys included only when their value is truthy. Vendor it to get dependency-free conditional class composition in TypeScript; the claim proves the join/skip/flatten behaviour matches hand-written expected strings, so you inherit a checked utility rather than a re-implementation to re-audit."
    },
    {
        "name": "groupBy",
        "lang": "typescript",
        "claim_id": "CLAIM-LIB-GROUPBY-001",
        "references": ["ecma-262-2024"],
        "title": "groupBy array partition (order-preserving)",
        "area": "TypeScript / Collections",
        "evidence_level": "measured",
        "code_files": [
            "groupBy.ts"
        ],
        "artifact": "groupBy.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored TypeScript groupBy(items, key) partitions an array into a Record<string, T[]> and produces the expected record on every one of a fixed 10-case reference battery whose expected records are hand-written independently of the module (correct = 10, errors = 0): buckets appear in first-seen key order and items keep their original input order within each bucket, covering parity/first-letter/object-field grouping, empty and singleton inputs, numeric-key coercion, and a data-driven \"__proto__\" key that becomes an ordinary own bucket with no prototype pollution.",
        "caveat": "Correctness is demonstrated over a fixed reference battery, not proven for all inputs, and the evidence checks runtime behaviour (run with node) rather than asserting the module type-checks under a specific tsc strictness. The comparison is by JSON.stringify, so it pins insertion/serialization order but treats key values as strings (numeric keys are coerced to strings and integer-like keys follow JS's own numeric-first property ordering); the key function must return a string.",
        "knowledge": "groupBy is the workhorse collection primitive for turning a flat list into buckets keyed by a projection — the SQL GROUP BY of everyday code, used for tallies, indexes, and report rollups. The subtle correctness properties are stability (items must stay in input order within a bucket) and safety against a data-driven \"__proto__\" key, which naive plain-object implementations mishandle by mutating the prototype chain. This module accumulates in a Map (safe for every string key, order-preserving) and materialises the result with defineProperty, so it is both stable and pollution-safe; vendor it to inherit a checked partitioner rather than re-auditing another hand-rolled reduce."
    },
    {
        "name": "chunk",
        "lang": "typescript",
        "claim_id": "CLAIM-LIB-CHUNK-001",
        "title": "chunk array into fixed-size groups",
        "area": "TypeScript / Array Utilities",
        "evidence_level": "measured",
        "code_files": [
            "chunk.ts"
        ],
        "artifact": "chunk.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors",
            "invalid_inputs_rejected"
        ],
        "bind_field": "correct",
        "statement": "The vendored TypeScript chunk<T>(arr, size) partitions an array into consecutive fixed-size sub-arrays (final chunk shorter when length is not an exact multiple) and produces the expected partition on every one of a fixed 8-case reference battery whose expected outputs are hand-written independently of the module (correct = n_cases = 8, errors = 0), including the spec examples chunk([1..7],3)->[[1,2,3],[4,5,6],[7]] and chunk([],3)->[]; it also rejects all 4 invalid sizes (0, -1, -5, 1.5) with a RangeError (invalid_inputs_rejected = 4).",
        "caveat": "Correctness is demonstrated over a fixed reference battery, not proven for all inputs, and the evidence checks runtime behaviour (run with node) — it does not assert the module type-checks under a specific tsc strictness. The guard rejects any size that is not an integer >= 1 (so fractional sizes throw, slightly stronger than the literal 'size < 1' spec); chunks are shallow slices, so nested object elements are shared by reference with the input.",
        "knowledge": "Chunking splits a flat list into fixed-size batches — the standard primitive behind paginating results, batching API/database writes, and laying items into grid rows. chunk(arr, size) walks the array in strides of `size`, slicing each window, so the final batch is shorter whenever the length is not a multiple of the size, and an empty input yields no chunks. A size below 1 has no sensible meaning (and a naive loop would never advance), so it fails closed with a RangeError. Vendor it to get dependency-free, off-by-one-checked batching instead of re-deriving slice math in every project."
    },
    {
        "name": "parseQuery",
        "lang": "typescript",
        "claim_id": "CLAIM-LIB-PARSEQUERY-001",
        "references": ["whatwg-url"],
        "title": "Query-string parse + stringify",
        "area": "TypeScript / URL & Web",
        "evidence_level": "measured",
        "code_files": [
            "parseQuery.ts"
        ],
        "artifact": "parseQuery.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored TypeScript parseQuery / stringifyQuery pair produces the expected result on every one of a fixed 32-case reference battery whose expected values are written independently of the module (correct = 32, errors = 0): hand-written parse/stringify expectations (repeated keys -> ordered arrays such as parseQuery(\"?a=1&b=2&a=3\") -> {a:[\"1\",\"3\"], b:\"2\"}, leading \"?\" handling, URI-decoding, empty-pair skipping, extra-\"=\" handling), stringify's stable sorted key order and form-style encoding, round-trip stability, and a per-key cross-check of decoding against the built-in URLSearchParams.getAll (an independent reference).",
        "caveat": "Correctness is demonstrated over a fixed reference battery run under node, not proven for all inputs, and the evidence checks runtime behaviour rather than asserting the module type-checks under a specific tsc strictness. The serializer emits keys in sorted order (not insertion order) and uses application/x-www-form-urlencoded style ('+' for space), so a stringify->parse round-trip preserves values but may reorder keys and normalizes '+'/%20; it is not a byte-exact inverse of every arbitrary query string.",
        "knowledge": "A URL query string is a '&'-separated list of 'key=value' pairs where keys can repeat and both sides are percent-encoded (with '+' historically meaning space in form submissions). parseQuery decodes each pair and collapses repeated keys into ordered arrays so 'a=1&a=3' becomes {a:[\"1\",\"3\"]}, while stringifyQuery reverses that with a deterministic sorted key order for stable, diffable output. Vendor it to read and build query strings consistently with zero dependencies; the claim proves the parse/serialize behaviour matches hand-written expectations and agrees with URLSearchParams, so you inherit a checked helper rather than a re-implementation to re-audit."
    },
    {
        "name": "formatDuration",
        "lang": "typescript",
        "claim_id": "CLAIM-LIB-FORMATDURATION-001",
        "title": "formatDuration compact duration formatter",
        "area": "TypeScript / Formatting",
        "evidence_level": "measured",
        "code_files": [
            "formatDuration.ts"
        ],
        "artifact": "formatDuration.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored TypeScript formatDuration(ms) renders a compact human-readable duration matching a hand-written reference table on every one of a fixed 21-case battery whose expected strings are computed independently of the module (correct = 21, errors = 0): it drops zero-valued units, renders the value 0 as \"0s\", truncates sub-second remainders to whole seconds, composes d/h/m/s (e.g. 90061000ms -> \"1d 1h 1m 1s\"), and throws RangeError on negative and non-finite input.",
        "caveat": "Correctness is demonstrated over a fixed reference battery run with node (runtime behaviour), not proven for all inputs and not asserting the module type-checks under a specific tsc strictness. Output is English single-letter units (d/h/m/s) with no localization, pluralization, weeks/months, or fractional-second display; sub-second precision is truncated (floored), not rounded.",
        "knowledge": "A compact duration formatter turns a raw millisecond count into a short human-readable string for logs, dashboards and UIs. formatDuration decomposes the value into days (86400s), hours (3600s), minutes (60s) and seconds, then drops zero-valued units so only the significant magnitudes show (with the whole-value 0 special-cased to \"0s\"), floors sub-second remainders, and rejects negative or non-finite input with a RangeError. Vendor it for consistent, dependency-free duration display; the claim proves the output matches an independent reference table, so you inherit a checked formatter rather than a re-implementation to re-audit."
    },
    {
        "name": "useUndoRedo",
        "lang": "react",
        "claim_id": "CLAIM-LIB-USEUNDOREDO-001",
        "title": "useUndoRedo React hook",
        "area": "React / UI State",
        "evidence_level": "measured",
        "code_files": [
            "useUndoRedo.tsx",
            "undoredo.logic.ts"
        ],
        "artifact": "useUndoRedo.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The pure undo/redo core behind the useUndoRedo React hook (a {past, present, future} history with push/undo/redo/canUndo/canRedo) produces the correct present value and canUndo/canRedo flags after every step of a fixed 12-action reference sequence with independently hand-computed expected snapshots (correct = n_cases = 12, errors = 0), including redo-stack clearing on a new set(), and undo-at-base / redo-at-tip fail-closed no-ops.",
        "caveat": "The claim covers the framework-agnostic core (undoredo.logic.ts) run under node, NOT React runtime rendering: the vendored useUndoRedo.tsx is a thin, reviewed useReducer binding over that core and is shipped but not rendered in the evidence. Correctness is demonstrated over one fixed action sequence, not proven for all histories or value types.",
        "knowledge": "Undo/redo is most robustly modeled as three immutable stacks — past states, the present, and a future (redo) stack — rather than mutating one buffer. A new edit (push) records the old present onto past and clears future, so an edit made after undoing forks history and discards the abandoned redo branch, matching how editors behave. Keeping this logic in a pure, framework-agnostic core makes the tricky part (stack transitions, boundary no-ops) unit-testable without a DOM, while the React hook stays a thin useReducer binding. Vendor both; the claim proves the core transitions are correct, so you inherit checked history state instead of re-deriving stack juggling per project."
    },
    {
        "name": "useAsync",
        "lang": "react",
        "claim_id": "CLAIM-LIB-USEASYNC-001",
        "title": "useAsync React hook (async request state machine)",
        "area": "React / UI State",
        "evidence_level": "measured",
        "code_files": [
            "useAsync.tsx",
            "async.logic.ts"
        ],
        "artifact": "useAsync.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The pure async state machine behind the useAsync React hook produces the correct next-state on every one of a fixed 9-row transition table with independently hand-written expected states (correct = n_cases = 9, errors = 0): start -> pending always clears error and preserves prior data (stale-while-revalidate), resolve -> success sets data and clears error, and reject -> error sets error and preserves prior data, across idle/pending/success/error origins including falsy (0) resolve data.",
        "caveat": "The claim covers the framework-agnostic core reducer (async.logic.ts) run under node, NOT React runtime rendering: the vendored useAsync.tsx is a thin, reviewed binding (useReducer + a run callback that dispatches start then resolve/reject) shipped but not executed in the evidence. Correctness is demonstrated over a fixed transition table, not proven for all state/action combinations; the reducer is total (unknown actions leave state unchanged) but the battery does not enumerate every path.",
        "knowledge": "Most async-UI bugs are state-machine bugs, not markup: a request is simultaneously loading, has stale data, and might error, and ad-hoc booleans (isLoading, hasError) drift out of sync. The durable fix is to model the request as an explicit status: idle | pending | success | error and drive it with a pure reducer, keeping the React hook a thin binding so the transitions are unit-testable without a DOM. useAsync does exactly that: async.logic.ts is the reducer over {status, data, error} and useAsync.tsx wraps it in useReducer with a run() that dispatches start then resolve/reject. Vendor both; the claim proves the core transitions, so you inherit a checked request state machine rather than re-deriving loading-flag logic in every component."
    },
    {
        "name": "useStepper",
        "lang": "react",
        "claim_id": "CLAIM-LIB-USESTEPPER-001",
        "title": "useStepper React hook",
        "area": "React / UI State",
        "evidence_level": "measured",
        "code_files": [
            "useStepper.tsx",
            "stepper.logic.ts"
        ],
        "artifact": "useStepper.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The pure stepper core behind the useStepper React hook computes the correct multi-step navigation state (index clamped to [0, stepCount-1], isFirst/isLast flags, progress = index/(stepCount-1) rounded to 4 dp or 0 for a single step, and clamped next/prev targets) on every one of a fixed 11-case reference battery with independently hand-computed expected states (correct = n_cases = 11, errors = 0).",
        "caveat": "The claim covers the framework-agnostic core (stepper.logic.ts) run under node, NOT React runtime rendering: the vendored useStepper.tsx is a thin, reviewed binding over that core (useState + useMemo) and is shipped but not rendered in the evidence. Correctness is demonstrated over a fixed battery, not proven for all inputs; the core fails closed (RangeError) on a non-positive or non-integer stepCount.",
        "knowledge": "Multi-step wizards are a classic source of off-by-one bugs: clamping the active step, deciding when Back/Next should disable, and computing a progress fraction all invite index errors. The durable pattern is to put that arithmetic in a pure, framework-agnostic function and make the hook a thin binding, so the hard part is unit-testable without a DOM. useStepper does exactly that: stepper.logic.ts derives the clamped index, isFirst/isLast flags, a 0..1 progress value and clamped next/prev targets, and useStepper.tsx wraps it in useState/useMemo. Vendor both; the claim proves the core is correct, so you inherit checked wizard-navigation state rather than re-deriving clamp and progress math in every project."
    },
    {
        "name": "useDebouncedValue",
        "lang": "react",
        "claim_id": "CLAIM-LIB-USEDEBOUNCED-001",
        "title": "useDebouncedValue React hook",
        "area": "React / UI State",
        "evidence_level": "measured",
        "code_files": [
            "useDebouncedValue.tsx",
            "debounce.logic.ts"
        ],
        "artifact": "useDebouncedValue.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The pure trailing-debounce core behind the useDebouncedValue React hook reproduces the hand-computed emissions on every one of a fixed 9-case reference battery of event traces (correct = n_cases = 9, errors = 0): rapid bursts collapse to their last value, events spaced at least delayMs apart each emit at eventTime + delayMs, a gap exactly equal to delayMs counts as fired, and a gap one below is coalesced. Expected emissions are derived by hand from the trailing-debounce definition, independent of the module.",
        "caveat": "The claim covers the framework-agnostic core (debounce.logic.ts) run under node, NOT React runtime rendering or real timers: the vendored useDebouncedValue.tsx is a thin, reviewed setTimeout binding over the same model, shipped but not executed in the evidence. The simulator assumes a chronologically sorted event trace and models a boundary gap of exactly delayMs as fired (>=); correctness is demonstrated over a fixed battery, not proven for all traces.",
        "knowledge": "Debouncing coalesces a rapid stream of events (keystrokes, resize, scroll) into a single trailing update that fires only after activity has been quiet for delayMs, so expensive work runs once instead of on every change. The effective React pattern is to put the timing model in a pure, framework-agnostic function and make the hook a thin binding, so the off-by-one-prone logic is unit-testable without a DOM or fake timers. debounce.logic.ts is a deterministic simulator: emitDebounced(events, delayMs) returns, for a trace of timed values, exactly the emissions a trailing debounce would produce, and useDebouncedValue.tsx wraps that same model in useState + useEffect + setTimeout. Vendor both; the claim proves the core timing is correct, so you inherit checked debounce behaviour rather than re-deriving timer-reset logic in every project."
    },
    {
        "name": "iban",
        "lang": "python",
        "claim_id": "CLAIM-LIB-IBAN-001",
        "references": ["iso-13616-2020", "iso-7064"],
        "title": "IBAN validation (ISO 13616 / MOD-97-10)",
        "area": "Finance / Payments & Banking",
        "evidence_level": "measured",
        "code_files": [
            "iban.py"
        ],
        "artifact": "iban.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors",
            "check_digit_correct"
        ],
        "bind_field": "correct",
        "statement": "The vendored IBAN validator (ISO 13616 / ISO 7064 MOD-97-10) classifies every entry in a fixed 12-row table of officially published IBANs correctly (correct = 12, errors = 0): 8 canonical registry / Wikipedia example IBANs (GB82WEST12345698765432, DE89370400440532013000, NO9386011117947, ES9121000418450200051332, ...) are accepted and 4 single-digit-mutated variants are rejected; independently, recomputing the two check digits from the BBAN reproduces the embedded check digits of all 5 tested valid IBANs.",
        "caveat": "Validation is the MOD-97-10 arithmetic plus a general [A-Z]{2}[0-9]{2}[A-Z0-9]+ shape and a 15..34 length check; it does NOT enforce per-country BBAN length or the national bank/branch structure, so a string with the right length and a correct check digit but a wrong national format can still pass. Correctness is demonstrated over a fixed table of published examples, not proven for every country or input.",
        "knowledge": "An IBAN wraps a national bank account number with a two-letter country code and two check digits so cross-border transfers can be validated before money moves. The check is ISO 7064 MOD-97-10: move the first four characters to the end, map letters to numbers (A=10..Z=35), and require the resulting integer to be congruent to 1 modulo 97 -- a scheme that catches all single-digit errors and most transpositions. Vendor this module to validate AND to generate the check digits of IBANs with zero dependencies; the claim proves it matches the published registry examples, so you inherit a checked validator rather than a re-implementation to re-audit."
    },
    {
        "name": "money",
        "lang": "python",
        "claim_id": "CLAIM-LIB-MONEY-001",
        "references": ["ieee-754-2019", "balinski-2001"],
        "title": "Cent-exact money allocation + banker's rounding",
        "area": "Finance / Accounting",
        "evidence_level": "measured",
        "code_files": [
            "money.py"
        ],
        "artifact": "money.json",
        "register_metrics": [
            "n_alloc_cases",
            "cent_exact",
            "cent_lost",
            "n_round_cases",
            "round_correct"
        ],
        "bind_field": "cent_exact",
        "statement": "The vendored money library allocates a total into integer minor-unit shares that sum EXACTLY back to the total on every one of a fixed 8-case battery (cent_exact = 8, cent_lost = 0), matches 5 independently hand-computed splits (allocate(100,[1,1,1]) = [34,33,33], allocate(100,[1,1,1,1,1,1]) = [17,17,17,17,16,16], allocate(1000,[1,2,1]) = [250,500,250]), and reproduces published ROUND_HALF_EVEN (banker's rounding) results on all 10 rows of a fixed table (0.5 -> 0, 1.5 -> 2, 2.5 -> 2, 3.5 -> 4, 2.675 -> 2.68).",
        "caveat": "The cent-exact invariant is an arithmetic identity checked over a fixed battery of totals/weights (non-negative integer minor units, non-negative integer weights, not all zero); it does not model currencies with non-decimal subunits, negative totals, or rounding of the allocation itself. round_money rounds decimal values (pass strings, not floats, to avoid binary-float error before rounding) and is HALF_EVEN only.",
        "knowledge": "Two everyday money bugs are rounding bias and lost pennies. Rounding halves 'up' biases long-run totals upward; banker's rounding (ROUND_HALF_EVEN, the IEEE 754 and accounting default) rounds a tie to the nearest even digit so the bias cancels. Splitting a bill three ways with naive division loses or mints a cent; the largest-remainder (Hamilton) method floors each share and hands the leftover units to the largest remainders so the parts always sum back to the total. This module works in integer minor units to avoid float entirely; vendor it to allocate invoices, taxes, or payouts and inherit a checked cent-exact splitter and a checked banker's rounder rather than re-auditing another ad-hoc division."
    },
    {
        "name": "mod11",
        "lang": "python",
        "claim_id": "CLAIM-LIB-MOD11-001",
        "references": ["brreg-orgnr"],
        "title": "Weighted MOD-11 check digits (Norwegian orgnr)",
        "area": "Finance / Identifiers & Validation",
        "evidence_level": "benchmarked",
        "code_files": [
            "mod11.py"
        ],
        "artifact": "mod11.json",
        "register_metrics": [
            "n_payloads",
            "checkdigit_defined",
            "roundtrip_valid",
            "tamper_mutations",
            "tamper_detected",
            "tamper_missed"
        ],
        "bind_field": "tamper_missed",
        "statement": "The vendored weighted MOD-11 check-digit library detects EVERY single-digit alteration over the complete space of 4-digit payloads under weights (2,3,4,5): all 409095 single-digit mutations of the 9091 well-defined check-digited numbers are caught (tamper_detected = 409095, tamper_missed = 0), every one of those numbers round-trips (compute the check digit, then validate = True; roundtrip_valid = 9091), and the Norwegian organisasjonsnummer reference 123456785 (payload 12345678 under weights 3,2,7,6,5,4,3,2 -> check 5) validates while 123456784 does not.",
        "caveat": "The exhaustive tamper / round-trip proof covers 4-digit payloads under one fixed weight vector; the single-error-detection property generalises (11 is prime and no weight is a multiple of 11) but is machine-verified only for that space, not every length. check_digit raises rather than emitting 'X' when the MOD-11 result is 10 (so it is numeric-only and does not cover ISBN-10's X), and MOD-11 catches all single-digit errors and most transpositions but is a checksum, not a cryptographic integrity guarantee.",
        "knowledge": "A weighted MOD-11 check digit is the integrity digit behind Norwegian organisation and bank account numbers, KID payment references, ISBN-10, and many national IDs: multiply each payload digit by a position weight, sum, reduce modulo 11, and take 11 minus that (11 -> 0). Because 11 is prime, every single-digit change alters the weighted sum modulo 11 and is detected -- a stronger guarantee than a plain sum. Vendor this module to validate and generate those identifiers with zero dependencies; the claim proves single-digit errors are caught exhaustively over the tested space, so you inherit a checked check-digit routine rather than a re-implementation to re-audit."
    },
    {
        "name": "modbus_crc",
        "lang": "python",
        "claim_id": "CLAIM-LIB-MODBUS-CRC-001",
        "references": ["modbus-serial-v1.02"],
        "title": "CRC-16/MODBUS frame check",
        "area": "Industrial / Fieldbus & Protocols",
        "evidence_level": "measured",
        "code_files": [
            "modbus_crc.py"
        ],
        "artifact": "modbus_crc.json",
        "register_metrics": [
            "reference_vectors",
            "reference_vectors_matched",
            "mismatches",
            "crosscheck_matched"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored CRC-16/MODBUS implementation (reflected poly 0xA001, init 0xFFFF, no final XOR) reproduces every value in a fixed 267-vector reference set with 0 mismatches: the published CRC-catalogue check value crc16_modbus(b\"123456789\") == 0x4B37, plus 266 byte strings (empty, single bytes, all-zero / all-0xFF runs, a Modbus read-holding-registers frame, and every single byte value 0..255) that agree byte-for-byte with an independent table-driven implementation computed in the evidence.",
        "caveat": "Correctness is demonstrated over a fixed reference set (one published catalogue value plus table-cross-checked byte strings), not proven for every input. CRC-16 is an error-DETECTION checksum for accidental corruption on a serial link, NOT a cryptographic hash or MAC: it is linear and trivially forgeable, so it gives no integrity or authenticity guarantee against an adversary.",
        "knowledge": "Modbus RTU, the serial fieldbus dialect ubiquitous in PLCs and industrial sensors, protects every frame with a 16-bit CRC using the reflected polynomial 0xA001, an initial value of 0xFFFF, and no final XOR, transmitted low byte first. This module computes the CRC and offers append / verify helpers; the claim proves it reproduces the published catalogue check value 0x4B37 and agrees with an independent table-driven CRC, so you can vendor a dependency-free, checked frame-check for Modbus tooling or gateways rather than re-auditing another CRC loop."
    },
    {
        "name": "oee",
        "lang": "python",
        "claim_id": "CLAIM-LIB-OEE-001",
        "references": ["nakajima-1988"],
        "title": "OEE (Overall Equipment Effectiveness)",
        "area": "Industrial / Manufacturing Analytics",
        "evidence_level": "measured",
        "code_files": [
            "oee.py"
        ],
        "artifact": "oee.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored OEE calculator reproduces the canonical published worked example (Vorne / oee.com) exactly to 4 dp -- Availability 0.8881, Performance 0.8611, Quality 0.9780, OEE 0.7479 from Planned 420 min, Run 373 min, Ideal Cycle 1.0 s, Total 19271, Good 18848 -- and matches all 3 hand-computed reference cases (correct = 3, errors = 0), including the perfect-line boundary (all factors 1.0) and the each-factor-one-half case (OEE 0.125).",
        "caveat": "OEE is pure ratio arithmetic (Availability x Performance x Quality); the module fails closed on non-positive denominators and on factors above 1 (run > planned, good > total, ideal cycle too large), but it does not model the six big losses, planned vs unplanned stop classification, or multi-shift roll-ups. Values are compared to 4 decimal places; correctness is demonstrated over a fixed reference table, not proven for every input.",
        "knowledge": "Overall Equipment Effectiveness is the factory-floor standard for how fully a machine is used, the product of three ratios: Availability (run time over planned time), Performance (actual over theoretical throughput), and Quality (good units over total). 100% is perfect production; about 85% is considered world-class. The published worked example resolves to 74.79%, and this module reproduces it. Vendor it to compute OEE and its factors consistently across lines and shifts; the claim proves the arithmetic matches the published reference, so you inherit a checked calculator rather than a spreadsheet formula to re-audit."
    },
    {
        "name": "nmea",
        "lang": "python",
        "claim_id": "CLAIM-LIB-NMEA-001",
        "references": ["nmea-0183"],
        "title": "NMEA 0183 sentence checksum",
        "area": "Industrial / Telemetry & Sensors",
        "evidence_level": "measured",
        "code_files": [
            "nmea.py"
        ],
        "artifact": "nmea.json",
        "register_metrics": [
            "n_published",
            "published_correct",
            "published_errors",
            "roundtrip_ok",
            "tamper_detected"
        ],
        "bind_field": "published_correct",
        "statement": "The vendored NMEA 0183 checksum reproduces the published '*HH' checksum of every one of 3 canonical example sentences ($GPGGA,...*47, $GPRMC,...*68, $GPGSA,...*39) exactly (published_correct = 3, published_errors = 0) and all 3 are accepted by is_valid; independently, for 4 payloads the build / verify round-trip holds (a built sentence validates; roundtrip_ok = 4) and a single-character mutation is detected in every case (tamper_detected = 4).",
        "caveat": "The checksum is the simple XOR of the characters between '$' and '*'; the module verifies that field and can build sentences, but it does NOT parse or validate the sentence's fields, talker ID, or semantics, and the XOR is an accidental-corruption check, not a cryptographic integrity guarantee. Correctness is demonstrated over a fixed set of published sentences plus a self-consistency battery, not proven for every input.",
        "knowledge": "NMEA 0183 is the line-oriented ASCII protocol that GPS receivers, marine instruments, and much SCADA telemetry use to emit sentences like '$GPGGA,...*47'. The two hex digits after '*' are the XOR of every character between '$' and '*', a lightweight guard against line noise. Vendor this module to validate incoming sentences and to build correctly-checksummed ones with zero dependencies; the claim proves it reproduces the checksums of the canonical published sentences, so you inherit a checked checksum routine rather than a re-implementation to re-audit."
    },
    {
        "name": "imei",
        "lang": "python",
        "claim_id": "CLAIM-LIB-IMEI-001",
        "references": ["3gpp-ts-23-003", "iso-7812-1"],
        "title": "IMEI validation (Luhn check digit)",
        "area": "Telecom / Device Identity",
        "evidence_level": "measured",
        "code_files": [
            "imei.py"
        ],
        "artifact": "imei.json",
        "register_metrics": [
            "reference_vectors",
            "reference_vectors_matched",
            "mismatches"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored IMEI validator accepts the published GSMA / Wikipedia example IMEI 490154203237518 and reconstructs its check digit (check_digit(\"49015420323751\") == 8), and its is_valid verdict agrees with an INDEPENDENT from-scratch Luhn implementation on every one of a fixed 261-vector battery (the published IMEI, corrupted and wrong-length variants, and 256 deterministic pseudo-random 15-digit strings): reference_vectors_matched = 261, mismatches = 0.",
        "caveat": "Validation is the 15-digit length plus the Luhn (mod-10) check digit over the first 14 digits; it does NOT verify that the Type Allocation Code is really assigned by the GSMA or that the device exists, and it does not handle the 16-digit IMEISV. Luhn catches all single-digit errors and most adjacent transpositions but is a data-entry checksum, not proof a number is genuine. Correctness is demonstrated over a fixed battery, not proven for every input.",
        "knowledge": "An IMEI is the 15-digit identity of a cellular device: an 8-digit Type Allocation Code, a 6-digit serial, and a trailing Luhn check digit over the first 14 digits -- the same mod-10 scheme used on payment cards. Networks and device registries validate it at the check-digit level before any lookup. Vendor this module to validate and parse IMEIs with zero dependencies; the claim proves it accepts the published example and agrees with an independent Luhn oracle across the battery, so you inherit a checked validator rather than a re-implementation to re-audit."
    },
    {
        "name": "hamming74",
        "lang": "python",
        "claim_id": "CLAIM-LIB-HAMMING74-001",
        "references": ["hamming-1950"],
        "title": "Hamming(7,4) single-error correction",
        "area": "Telecom / Forward Error Correction",
        "evidence_level": "machine_checked",
        "code_files": [
            "hamming74.py"
        ],
        "artifact": "hamming74.json",
        "register_metrics": [
            "trials",
            "corrected",
            "miscorrected",
            "error_position_correct",
            "min_code_distance"
        ],
        "bind_field": "corrected",
        "statement": "The vendored Hamming(7,4) coder corrects EVERY single-bit error, verified exhaustively: over the complete space of 16 data values x 8 error patterns (no error plus a flip at each of the 7 positions) = 128 trials, decoding always recovers the original 4 bits and reports the exact flipped position (corrected = 128, miscorrected = 0, error_position_correct = 128), and the 16 codewords have minimum Hamming distance 3.",
        "caveat": "The exhaustive proof covers SINGLE-bit errors only. Hamming(7,4) has minimum distance 3, so it corrects any one-bit error but a two-bit error is mis-corrected to the wrong nibble (it lacks the distance-4 SECDED extension that would merely DETECT double errors). The code carries 4 data bits per 7-bit codeword; framing multi-byte data across codewords is the caller's responsibility.",
        "knowledge": "Forward error correction lets a receiver fix bit errors without retransmission -- essential on one-way or high-latency links. The Hamming(7,4) code adds 3 parity bits to 4 data bits so that the parity syndrome of a received word points directly at the position of any single flipped bit, which the decoder then corrects. Because its 16 codewords are pairwise at Hamming distance >= 3, any single-bit error stays closest to the true codeword. Vendor this module for a checked, dependency-free single-error-correcting building block; the claim proves correction over the ENTIRE single-error space by enumeration, so you inherit a proven coder rather than a re-implementation to re-audit."
    },
    {
        "name": "e164",
        "lang": "python",
        "claim_id": "CLAIM-LIB-E164-001",
        "references": ["itu-e164"],
        "title": "E.164 phone number validation",
        "area": "Telecom / Numbering Plans",
        "evidence_level": "measured",
        "code_files": [
            "e164.py"
        ],
        "artifact": "e164.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors",
            "country_code_correct"
        ],
        "bind_field": "correct",
        "statement": "The vendored E.164 validator classifies every entry in a fixed 13-row battery of phone numbers correctly (correct = 13, errors = 0): 8 well-formed international numbers are accepted and 5 malformed ones rejected (missing '+', leading zero after '+', too short, non-digit, and 16 digits exceeding the E.164 maximum), and the country calling code resolves as expected for all 13 rows (country_code_correct = 13) by longest-prefix match, so +358... yields 358 (Finland) rather than a shorter code.",
        "caveat": "This validates E.164 SYNTAX (leading '+', 7..15 digits, no leading zero on the country code) and extracts the calling code from a CURATED subset of published ITU assignments; it is NOT full national-number validation (no libphonenumber-style per-country length / prefix rules), and a number outside the curated code table returns None for the country code. Correctness is demonstrated over a fixed battery, not proven for every number.",
        "knowledge": "ITU-T E.164 is the international telephone numbering plan: a '+', a 1-3 digit country calling code, then the national number, at most 15 digits total, with no leading zero on the country code. The first parsing step is almost always the same -- check that shape and split off the calling code by longest-prefix match (so +358 resolves to Finland, not +35 or +3). Vendor this module to normalise and route phone numbers with zero dependencies; the claim proves it classifies the battery and resolves calling codes correctly, so you inherit a checked format validator rather than a re-implementation to re-audit (reach for libphonenumber when you need full national validation)."
    },
    {
        "name": "cidr",
        "lang": "python",
        "claim_id": "CLAIM-LIB-CIDR-001",
        "references": ["rfc-4632"],
        "title": "IPv4 CIDR / subnet math",
        "area": "Telecom / IP Address Management",
        "evidence_level": "benchmarked",
        "code_files": [
            "cidr.py"
        ],
        "artifact": "cidr.json",
        "register_metrics": [
            "n_networks",
            "checks",
            "checks_matched",
            "mismatches"
        ],
        "bind_field": "checks_matched",
        "statement": "The vendored IPv4 CIDR calculator -- which implements the 32-bit subnet arithmetic DIRECTLY and never imports ipaddress -- agrees with Python's stdlib ipaddress on every one of 140 checks across a fixed 12-network battery (checks_matched = 140, mismatches = 0): network and broadcast address, netmask, total address count, usable host count, and first/last usable host per network, plus a full hosts() enumeration count for narrow prefixes and a membership sweep (network, broadcast, and the addresses just outside), including the RFC 3021 /31 point-to-point and single-host /32 cases.",
        "caveat": "ipaddress is the independent oracle and is NOT used inside the vendored module. Correctness is demonstrated over a fixed battery of networks, not proven for every possible input. IPv4 only; parsing rejects leading-zero octets (no octal ambiguity). 'Usable hosts' follows the common convention (block size minus network+broadcast for /0../30, 2 for a /31, 1 for a /32).",
        "knowledge": "CIDR subnetting is the everyday management-plane task on routers, firewalls and ISP IPAM: given 192.0.2.0/24 decide the network address, the directed broadcast, the mask, how many usable hosts, and whether an address is inside the block -- all of it bit arithmetic on the 32-bit integer. This module implements that arithmetic from scratch (so it carries no dependency) and the claim proves it matches Python's ipaddress across the battery, so you inherit a checked, dependency-free IPv4 calculator rather than a re-implementation to re-audit."
    },
    {
        "name": "ipv6",
        "lang": "python",
        "claim_id": "CLAIM-LIB-IPV6-001",
        "references": ["rfc-4291", "rfc-5952"],
        "title": "IPv6 parsing + RFC 5952 compression",
        "area": "Telecom / IPv6 Addressing",
        "evidence_level": "benchmarked",
        "code_files": [
            "ipv6.py"
        ],
        "artifact": "ipv6.json",
        "register_metrics": [
            "n_addresses",
            "n_cidrs",
            "checks",
            "checks_matched",
            "mismatches"
        ],
        "bind_field": "checks_matched",
        "statement": "The vendored IPv6 parser / RFC 5952 compressor -- implemented DIRECTLY and never importing ipaddress -- agrees with Python's stdlib ipaddress on all 38 checks across a fixed battery of 12 addresses and 7 CIDRs (checks_matched = 38, mismatches = 0): compress(parse(s)) equals .compressed and explode(parse(s)) equals .exploded for each address, and the compressed network address plus total address count match for each CIDR, exercising the RFC 5952 edges (leftmost-longest zero run wins, a single zero group is never shortened to '::').",
        "caveat": "ipaddress is the independent oracle and is NOT used inside the vendored module. Dotted-quad IPv4-embedded IPv6 (e.g. ::ffff:192.0.2.1) is out of scope and rejected. Correctness is demonstrated over a fixed battery, not proven for every possible address.",
        "knowledge": "IPv6 text has many spellings for one address, so RFC 5952 defines a single canonical form: lowercase hex, no leading zeros per group, and the longest run of zero groups (leftmost on a tie) collapsed to '::'. Getting that compression exactly right -- and never collapsing a lone zero group -- is the subtle part every implementation must match. This module parses and canonicalises IPv6 from scratch; the claim proves it agrees with Python's ipaddress across the battery, so you inherit a checked, dependency-free IPv6 formatter rather than a re-implementation to re-audit."
    },
    {
        "name": "macaddr",
        "lang": "python",
        "claim_id": "CLAIM-LIB-MACADDR-001",
        "references": ["ieee-802", "ieee-ra-eui-guidelines"],
        "title": "MAC / EUI-48 parsing + IEEE 802 flags",
        "area": "Telecom / Layer-2 Addressing",
        "evidence_level": "measured",
        "code_files": [
            "macaddr.py"
        ],
        "artifact": "macaddr.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors",
            "notation_forms_tested"
        ],
        "bind_field": "correct",
        "statement": "The vendored MAC / EUI-48 library decodes the IEEE 802 flag bits correctly on every one of a fixed 7-address battery (correct = 7, errors = 0): the I/G multicast bit and U/L locally-administered bit of the first octet, plus broadcast detection -- checked against hand-written expected flags for well-known MACs (01:00:5e:.. and 33:33:.. multicast, ff:ff:ff:ff:ff:ff broadcast, 02:.. and 52:54:00:.. locally administered, ordinary vendor-OUI unicast). Independently, the colon, hyphen, Cisco-dotted, and bare-hex spellings of one address all parse to the same 48-bit integer.",
        "caveat": "Flag semantics follow the IEEE 802 first-octet bit definitions, demonstrated over a fixed battery rather than proven for every address. The module normalises and decodes; it does NOT look up the OUI's registered vendor (no IEEE registry is bundled) and covers EUI-48 (not EUI-64).",
        "knowledge": "A MAC address is written four different ways (aa:bb:.., aa-bb-.., Cisco aabb.ccdd.eeff, bare aabbccddeeff), and the two low bits of its first octet carry meaning: the I/G bit marks multicast vs unicast and the U/L bit marks a locally-administered (e.g. virtualised/randomised) vs globally-unique address. This module parses every notation to one integer and decodes those flags; the claim proves the decoding matches the IEEE rules and the notations agree, so you inherit a checked L2-address helper rather than a re-implementation to re-audit."
    },
    {
        "name": "aspath",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ASPATH-001",
        "references": ["rfc-4271", "rfc-6996", "rfc-5398", "rfc-6793"],
        "title": "BGP AS-path + ASN classification",
        "area": "Telecom / BGP Routing",
        "evidence_level": "measured",
        "code_files": [
            "aspath.py"
        ],
        "artifact": "aspath.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored BGP AS-path library classifies every one of a fixed 17-ASN battery correctly against the published RFC allocations (correct = 17, errors = 0), pinning both sides of every boundary: private 64512-65534 and 4200000000-4294967294 (RFC 6996), reserved 0 (RFC 7607), 23456 AS_TRANS (RFC 6793), 65535 and 4294967295 last-ASN (RFC 7300), and documentation 64496-64511 and 65536-65551 (RFC 5398); and it parses an AS_SEQUENCE, measures its length, extracts the origin AS, and strips private ASNs.",
        "caveat": "Classification follows the RFC/IANA ranges over a fixed battery, not proven for every value; the ranges themselves can be updated by future IANA action. strip_private is a simple filter (removes every private ASN), not Cisco's positional remove-private-as semantics, and parse handles an AS_SEQUENCE (space-separated ASNs), not AS_SET/confederation segment notation.",
        "knowledge": "Every BGP route carries an AS-path -- the list of Autonomous Systems it traversed -- and operators constantly reason about it: how long is it (shorter is preferred), who originated it, and are any ASNs private or reserved (which must not leak to the public Internet). The private, reserved, and documentation ASN ranges are fixed by RFCs 6996/7300/5398/7607/6793. This module parses the path and classifies ASNs against those ranges; the claim proves the classification matches the published boundaries, so you inherit a checked routing helper rather than a re-implementation to re-audit."
    },
    {
        "name": "ipchecksum",
        "lang": "python",
        "claim_id": "CLAIM-LIB-IPCHECKSUM-001",
        "references": ["rfc-1071", "rfc-791"],
        "title": "RFC 1071 Internet checksum",
        "area": "Telecom / Packet Processing",
        "evidence_level": "measured",
        "code_files": [
            "ipchecksum.py"
        ],
        "artifact": "ipchecksum.json",
        "register_metrics": [
            "reference_vectors",
            "reference_vectors_matched",
            "mismatches",
            "crosscheck_matched"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored RFC 1071 Internet checksum reproduces every value in a fixed 268-vector reference set with 0 mismatches: the published IPv4-header worked example (header 4500 0073 0000 4000 4011 0000 c0a8 0001 c0a8 00c7 checksums to 0xb861), the verify round-trip (inserting 0xb861 makes the full header checksum to 0), and 266 byte strings (empty, odd/even lengths, all-zero / all-0xFF, and every single byte value 0..255) that agree with an independent struct-based implementation computed in the evidence.",
        "caveat": "Correctness is demonstrated over a fixed reference set (one published header value plus an independent-implementation cross-check), not proven for every input. The Internet checksum is an error-DETECTION checksum for accidental corruption, not a cryptographic hash or MAC -- it is linear and trivially forgeable, and (being 16-bit one's complement) it cannot distinguish +0 from -0.",
        "knowledge": "The Internet checksum (RFC 1071) protects IPv4, ICMP, UDP and TCP headers: sum the data as 16-bit big-endian words in one's-complement arithmetic (folding carries back in), then take the complement; a receiver that sums the whole datagram including the checksum gets all-ones, whose complement is zero. This module computes and verifies it directly; the claim proves it reproduces the published IPv4 example and agrees with an independent implementation, so you inherit a checked, dependency-free checksum for packet tooling rather than a re-implementation to re-audit."
    },
    {
        "name": "vlan",
        "lang": "python",
        "claim_id": "CLAIM-LIB-VLAN-001",
        "references": ["ieee-802-1q"],
        "title": "802.1Q VLAN ID validation + ranges",
        "area": "Telecom / VLAN Management",
        "evidence_level": "measured",
        "code_files": [
            "vlan.py"
        ],
        "artifact": "vlan.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors",
            "range_parse_correct",
            "range_roundtrip_correct"
        ],
        "bind_field": "correct",
        "statement": "The vendored 802.1Q VLAN library classifies VLAN-ID validity correctly on every one of a fixed 9-case battery (correct = 9, errors = 0), pinning the reservations (0 priority-tagged and 4095 reserved are invalid; 1..4094 valid); and over 6 range strings it parses the compact 'a,b-c' notation to the expected sorted, de-duplicated list and reformats it to the canonical range text (range_parse_correct = 6, range_roundtrip_correct = 6).",
        "caveat": "Validity follows the IEEE 802.1Q assignable range (1..4094); the module does not model 802.1ad QinQ stacking, per-switch reserved-VLAN customisation, or VLAN names. Correctness is demonstrated over a fixed battery, not proven for every input.",
        "knowledge": "An 802.1Q VLAN ID is a 12-bit field, but only 1..4094 are assignable: 0 marks a priority-tagged (untagged) frame and 4095 is reserved. Switch and ISP configs express VLAN membership as compact ranges like '1,10-12,4094', which must be parsed, de-duplicated, and re-emitted canonically. This module validates VIDs and round-trips those range lists; the claim proves the validity rule matches 802.1Q and the parse/format round-trips, so you inherit a checked VLAN helper rather than a re-implementation to re-audit."
    },
    {
        "name": "levenshtein",
        "lang": "python",
        "claim_id": "CLAIM-LIB-LEVENSHTEIN-001",
        "references": ["levenshtein-1966", "wagner-1974"],
        "title": "Levenshtein edit distance",
        "area": "General / Strings & Text",
        "evidence_level": "measured",
        "code_files": [
            "levenshtein.py"
        ],
        "artifact": "levenshtein.json",
        "register_metrics": [
            "n_reference",
            "reference_correct",
            "reference_errors",
            "symmetry_ok",
            "triangle_ok"
        ],
        "bind_field": "reference_correct",
        "statement": "The vendored Levenshtein edit distance reproduces every published textbook value in a fixed 8-row battery (reference_correct = 8, reference_errors = 0): kitten->sitting = 3, Saturday->Sunday = 3, flaw->lawn = 2, gumbo->gambol = 2, book->back = 2, ''->'abc' = 3, and identity pairs = 0; and over a fixed word set it satisfies the metric axioms -- identity, symmetry on all 100 ordered pairs, and the triangle inequality on all 1000 ordered triples.",
        "caveat": "Costs are the classic unit-cost model (insertion, deletion, substitution each cost 1); it is NOT Damerau-Levenshtein (adjacent transposition is 2, not 1) and applies no custom cost weights. Correctness is demonstrated over a fixed battery plus the metric-axiom sweep, not proven for every pair of strings.",
        "knowledge": "Levenshtein distance is the minimum number of single-character insertions, deletions, or substitutions to turn one string into another -- the workhorse behind spell-check suggestions, fuzzy matching, and diff tooling. The standard Wagner-Fischer dynamic program computes it in O(m*n) time; a correct implementation also forms a true metric (identity, symmetry, triangle inequality). This module uses the two-row DP; the claim proves it matches the published distances and satisfies the metric axioms, so you inherit a checked distance function rather than a re-implementation to re-audit."
    },
    {
        "name": "topo_sort",
        "lang": "python",
        "claim_id": "CLAIM-LIB-TOPOSORT-001",
        "references": ["kahn-1962"],
        "title": "Topological sort + cycle detection",
        "area": "General / Graph Algorithms",
        "evidence_level": "measured",
        "code_files": [
            "topo_sort.py"
        ],
        "artifact": "topo_sort.json",
        "register_metrics": [
            "n_dags",
            "valid_orderings",
            "invalid_orderings",
            "n_cyclic",
            "cycles_detected"
        ],
        "bind_field": "valid_orderings",
        "statement": "The vendored topological sort (Kahn's algorithm, deterministic smallest-first tie-break) produces an edge-respecting order for every one of a fixed 6-DAG battery (valid_orderings = 6, invalid_orderings = 0) -- each order contains every node exactly once and places the tail of every edge before its head -- and detects every one of 4 cyclic graphs (self-loop, 2-cycle, 3-cycle, embedded cycle), with has_cycle True and topo_sort raising CycleError.",
        "caveat": "Correctness is demonstrated over a fixed battery of graphs, not proven for every graph. Nodes must be mutually comparable for the deterministic smallest-first ordering (e.g. all strings or all ints); an edge referencing an unknown node fails closed. Edges are (u, v) meaning 'u before v'.",
        "knowledge": "A topological sort orders a directed acyclic graph so every dependency comes before whatever depends on it -- the primitive behind build systems, task schedulers, database migration ordering, and package resolution. Kahn's algorithm repeatedly emits a node with no remaining incoming edges; if any node never reaches in-degree zero, the graph has a cycle and no order exists. This module emits ready nodes smallest-first for a deterministic result and fails closed on a cycle; the claim proves every output respects all edges and every cycle is caught, so you inherit a checked ordering primitive rather than a re-implementation to re-audit."
    },
    {
        "name": "sha256",
        "lang": "python",
        "claim_id": "CLAIM-LIB-SHA256-001",
        "references": ["fips-180-4"],
        "title": "SHA-256 (FIPS 180-4) from scratch",
        "area": "Security / Cryptographic Hashing",
        "evidence_level": "benchmarked",
        "code_files": [
            "sha256.py"
        ],
        "artifact": "sha256.json",
        "register_metrics": [
            "reference_vectors",
            "reference_vectors_matched",
            "mismatches",
            "crosscheck_matched"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored SHA-256 -- which implements the FIPS 180-4 padding, 64-word message schedule and 64-round compression DIRECTLY on 32-bit integers and never imports hashlib -- reproduces every value in a fixed 398-vector reference set with 0 mismatches: the 3 published FIPS check values (sha256(b\"\") == e3b0c442...b855, sha256(b\"abc\") == ba7816bf...15ad, and the 448-bit example) plus 395 byte strings (block-boundary lengths 55/56/64/65, a long input, every single byte 0..255, and incremental lengths across blocks) that agree byte-for-byte with the independent stdlib hashlib.sha256.",
        "caveat": "hashlib.sha256 is the independent oracle and is NOT used inside the vendored module. Correctness is demonstrated over a fixed reference set, not proven for every input. SHA-256 is a cryptographic hash for integrity and commitment, NOT a password hash -- use PBKDF2/scrypt/argon2 for passwords -- and a bare hash is not a MAC (use HMAC for authentication). This is a clear, from-scratch reference implementation, not a side-channel-hardened or performance-tuned one.",
        "knowledge": "SHA-256 (FIPS 180-4) maps any input to a 256-bit digest such that finding collisions or preimages is computationally infeasible -- the backbone of digital signatures, TLS certificates, Git object ids, Bitcoin, and content addressing. It processes 512-bit blocks through a 64-round compression function mixing eight 32-bit state words with round constants derived from the cube roots of primes. This module implements the whole algorithm from scratch (no hashlib), so you can vendor a dependency-free, auditable hash; the claim proves it matches the published FIPS vectors and agrees byte-for-byte with hashlib, so you inherit a checked implementation rather than a re-implementation to re-audit."
    },
    {
        "name": "hmac_sha256",
        "lang": "python",
        "claim_id": "CLAIM-LIB-HMAC-SHA256-001",
        "references": ["rfc-2104", "rfc-4231"],
        "title": "HMAC-SHA256 (RFC 2104) from scratch",
        "area": "Security / Message Authentication",
        "evidence_level": "benchmarked",
        "code_files": [
            "hmac_sha256.py"
        ],
        "artifact": "hmac_sha256.json",
        "register_metrics": [
            "reference_vectors",
            "reference_vectors_matched",
            "mismatches",
            "oracle_agreements"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored HMAC-SHA256 -- which implements the RFC 2104 construction DIRECTLY (key normalization, ipad/opad, two-pass hash) over hashlib.sha256 and never calls the stdlib hmac module -- passes all 13 checks with 0 mismatches: it agrees byte-for-byte with stdlib hmac on all 10 battery inputs (the RFC 4231 HMAC-SHA256 test key/message pairs, including the oversized 131-byte key that must be hashed down, plus empty and block-sized keys), reproduces the published RFC 4231 Test Case 2 tag (5bdcc146...3843), and its constant-time verify accepts the correct tag and rejects a single flipped bit.",
        "caveat": "The stdlib hmac module is the independent oracle for the HMAC construction; the underlying compression is hashlib.sha256 (so this proves the HMAC wrapper, not SHA-256 itself -- see the sha256 module for that). Correctness is over a fixed battery, not proven for every input. verify is constant-time in the tag comparison, but this is a clear reference implementation, not a fully side-channel-hardened one.",
        "knowledge": "HMAC (RFC 2104) turns a plain hash into a keyed message authentication code: HMAC(K, m) = H((K XOR opad) || H((K XOR ipad) || m)). It lets two parties holding a shared secret verify that a message is authentic and untampered, and underpins TOTP/HOTP, JWT (HS256), AWS request signing, and webhook signatures. Verifying a tag must be constant-time so an attacker cannot forge one byte at a time. This module implements the construction from scratch; the claim proves it matches stdlib hmac and the RFC 4231 vector, so you inherit a checked MAC rather than a re-implementation to re-audit."
    },
    {
        "name": "hotp",
        "lang": "python",
        "claim_id": "CLAIM-LIB-HOTP-001",
        "references": ["rfc-4226"],
        "title": "HOTP one-time passwords (RFC 4226)",
        "area": "Security / Authentication (2FA)",
        "evidence_level": "benchmarked",
        "code_files": [
            "hotp.py"
        ],
        "artifact": "hotp.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored HOTP generator reproduces every published RFC 4226 Appendix D test vector exactly (correct = 10, errors = 0): for the reference secret b\"12345678901234567890\" the 6-digit HOTP for counters 0..9 is 755224, 287082, 359152, 969429, 338314, 254676, 287922, 162583, 399871, 520489, computed via HMAC-SHA1 of the counter and the RFC 4226 dynamic-truncation to a 31-bit value reduced modulo 10**digits.",
        "caveat": "Correctness is demonstrated over the published RFC 4226 vectors, not proven for every secret/counter. HOTP is event-based (the caller owns the moving counter and its resynchronization window); it authenticates possession of the shared secret, so the secret must be provisioned and stored securely, and SHA-1 here is the HMAC PRF as the RFC mandates (not a security weakness in this HOTP context).",
        "knowledge": "HOTP (RFC 4226) is the HMAC-based one-time-password algorithm behind hardware tokens and authenticator apps: it HMACs an incrementing counter with a shared secret, then 'dynamically truncates' the MAC to a short human-typable code. Each counter value yields a fresh single-use code, so an intercepted code is worthless once used. This module implements the generation and truncation exactly; the claim proves it reproduces the official RFC 4226 vectors, so you inherit a checked OTP generator rather than a re-implementation to re-audit (and TOTP builds directly on it)."
    },
    {
        "name": "totp",
        "lang": "python",
        "claim_id": "CLAIM-LIB-TOTP-001",
        "references": ["rfc-6238", "rfc-4226"],
        "title": "TOTP one-time passwords (RFC 6238)",
        "area": "Security / Authentication (2FA)",
        "evidence_level": "benchmarked",
        "code_files": [
            "totp.py"
        ],
        "artifact": "totp.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors"
        ],
        "bind_field": "correct",
        "statement": "The vendored TOTP generator reproduces every published RFC 6238 Appendix B (SHA-1) test vector exactly (correct = 6, errors = 0): for the reference secret b\"12345678901234567890\" with 8 digits and a 30-second step, the TOTP at Unix times 59, 1111111109, 1111111111, 1234567890, 2000000000 and 20000000000 is 94287082, 07081804, 14050471, 89005924, 69279037 and 65353130, derived as HOTP over the time counter floor((now - T0) / step).",
        "caveat": "Correctness is demonstrated over the published RFC 6238 SHA-1 vectors, not proven for every input; the SHA-256/SHA-512 modes are implemented but each is validated here only via SHA-1 (RFC 6238 uses different per-algorithm seeds). Verification (accepting a code within a +/- step window for clock skew, and rejecting reuse) is the caller's responsibility, and the shared secret must be stored securely.",
        "knowledge": "TOTP (RFC 6238) is HOTP with the counter replaced by the current time divided into fixed steps (usually 30 s), so the code rotates automatically without a stored counter -- the '6-digit code' in Google Authenticator, Authy, and most 2FA. The verifier recomputes the expected code for the current window (often allowing one step of clock skew) and compares. This module computes TOTP with selectable digest and digit count; the claim proves it reproduces the official RFC 6238 vectors, so you inherit a checked TOTP generator rather than a re-implementation to re-audit."
    },
    {
        "name": "pbkdf2",
        "lang": "python",
        "claim_id": "CLAIM-LIB-PBKDF2-001",
        "references": ["rfc-8018", "rfc-6070"],
        "title": "PBKDF2 key derivation (RFC 8018)",
        "area": "Security / Password Hashing",
        "evidence_level": "benchmarked",
        "code_files": [
            "pbkdf2.py"
        ],
        "artifact": "pbkdf2.json",
        "register_metrics": [
            "reference_vectors",
            "reference_vectors_matched",
            "mismatches",
            "oracle_matched"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored PBKDF2 -- which implements the RFC 8018 block function T_i = U_1 XOR ... XOR U_c DIRECTLY over an HMAC PRF and never calls hashlib.pbkdf2_hmac -- reproduces every value in an 11-vector reference set with 0 mismatches: the 3 published RFC 6070 PBKDF2-HMAC-SHA1 vectors (('password','salt',1,20) -> 0c60c80f...37a6, (...,2,20) -> ea6c014d...8957, (...,4096,20) -> 4b007901...29c1) plus 8 (hash, password, salt, iterations, dklen) cases over SHA-1/256/512 (multi-block output, empty password, empty salt) that agree byte-for-byte with the independent stdlib hashlib.pbkdf2_hmac.",
        "caveat": "hashlib.pbkdf2_hmac is the independent oracle and is NOT called inside the vendored module. Correctness is over a fixed reference set, not proven for every input. PBKDF2 is a deliberately slow password KDF; choose a high iteration count (>= hundreds of thousands for SHA-256 today) and a unique random salt per password. This pure-Python implementation is far slower than the C stdlib one and is not constant-time; for production password storage prefer scrypt or argon2.",
        "knowledge": "PBKDF2 (RFC 8018 / PKCS#5) stretches a password into a cryptographic key by iterating an HMAC PRF thousands of times over the password and a per-user salt, so brute-forcing stolen hashes costs the attacker that same multiplier per guess. It is the classic password-hashing and key-derivation function (WPA2, disk encryption, many app login stores). This module implements the construction from scratch; the claim proves it matches the RFC 6070 vectors and agrees with hashlib.pbkdf2_hmac, so you inherit a checked KDF rather than a re-implementation to re-audit."
    },
    {
        "name": "hkdf",
        "lang": "python",
        "claim_id": "CLAIM-LIB-HKDF-001",
        "references": ["rfc-5869", "rfc-8446"],
        "title": "HKDF key derivation (RFC 5869)",
        "area": "Security / Key Derivation",
        "evidence_level": "benchmarked",
        "code_files": [
            "hkdf.py"
        ],
        "artifact": "hkdf.json",
        "register_metrics": [
            "n_vectors",
            "checks",
            "reference_vectors_matched",
            "mismatches"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored HKDF (extract-then-expand) reproduces the published RFC 5869 SHA-256 test vectors exactly (reference_vectors_matched = 9, mismatches = 0): across Test Case 1 (basic), Test Case 2 (longer inputs, L=82), and Test Case 3 (zero-length salt and info) it matches the RFC's PRK and OKM hex, and the standalone expand(PRK) step reproduces each OKM -- all three checks per case, hand-written verbatim from the RFC.",
        "caveat": "The RFC 5869 published vectors are the independent oracle. Correctness is demonstrated over those fixed vectors (SHA-256), not proven for every input. HKDF derives keys from an already-high-entropy secret (a Diffie-Hellman shared secret, a master key); it is NOT a password hash -- run a low-entropy password through PBKDF2/scrypt/argon2 first. Bind context into the info parameter for domain separation between derived keys.",
        "knowledge": "HKDF (RFC 5869) is the modern key-derivation function used by TLS 1.3, the Signal protocol, and Noise: 'extract' concentrates the entropy of an input keying material into a uniform pseudorandom key PRK = HMAC(salt, IKM), and 'expand' stretches PRK into any number of independent output keys via a counter-chained HMAC, with an info label for domain separation. This module implements both steps; the claim proves it reproduces the official RFC 5869 vectors (including the 82-byte case), so you inherit a checked KDF rather than a re-implementation to re-audit."
    },
    {
        "name": "percentile",
        "lang": "python",
        "claim_id": "CLAIM-LIB-PERCENTILE-001",
        "references": ["hyndman-1996"],
        "title": "Percentiles / quantiles (p50 / p95 / p99)",
        "area": "Observability / Metrics & Statistics",
        "evidence_level": "benchmarked",
        "code_files": [
            "percentile.py"
        ],
        "artifact": "percentile.json",
        "register_metrics": [
            "n_datasets",
            "checks",
            "checks_matched",
            "mismatches",
            "nearest_rank_correct"
        ],
        "bind_field": "checks_matched",
        "statement": "The vendored percentile calculator agrees with Python's stdlib statistics on every one of 605 checks across a fixed 6-dataset battery (checks_matched = 605, mismatches = 0): the linear method matches statistics.quantiles(data, n=100, method=\"inclusive\") for every percentile p in 1..99 and matches statistics.median at the 50th, and the nearest-rank method matches its hand-computed definition on 5 boundary cases (including p=0, p=100, and interior ranks).",
        "caveat": "statistics is the independent oracle and is NOT imported by the vendored module. Two methods are provided: linear (the numpy default / statistics 'inclusive' interpolation) and nearest_rank; other conventions (exclusive, lower/higher/midpoint) are out of scope. Correctness is demonstrated over a fixed battery, not proven for every dataset; percentiles are exact over the given data, not a streaming estimate.",
        "knowledge": "Percentiles are how you actually read a latency distribution: the p50 (median) is the typical experience, while the p95 / p99 tail is where SLOs live and where users feel pain that an average hides. The subtlety is that 'the 95th percentile' has several definitions that disagree on small samples; the common ones are linear interpolation between order statistics and the nearest-rank rule. This module implements both exactly; the claim proves the linear method matches Python's statistics module and the nearest-rank method matches its definition, so you inherit a checked quantile function rather than a re-implementation to re-audit."
    },
    {
        "name": "apdex",
        "lang": "python",
        "claim_id": "CLAIM-LIB-APDEX-001",
        "references": ["apdex-spec"],
        "title": "Apdex application performance index",
        "area": "Observability / Service Level Indicators",
        "evidence_level": "measured",
        "code_files": [
            "apdex.py"
        ],
        "artifact": "apdex.json",
        "register_metrics": [
            "n_cases",
            "correct",
            "errors",
            "zone_correct"
        ],
        "bind_field": "correct",
        "statement": "The vendored Apdex calculator reproduces a fixed 5-case hand-computed reference battery exactly (correct = 5, errors = 0), including the all-satisfied (1.0) and all-frustrated (0.0) extremes and the zone boundaries (a sample exactly at T is satisfied, exactly at 4T is tolerating), and it classifies all 4 zone-boundary probes correctly -- computing Apdex_T = (satisfied + tolerating/2) / total with satisfied <= T, tolerating in (T, 4T], frustrated > 4T.",
        "caveat": "Correctness is demonstrated over a fixed hand-computed battery, not proven for every input; the score is rounded to 4 decimal places. The threshold model is the standard single-T Apdex (tolerating boundary fixed at 4T); it does not model per-endpoint thresholds or weighted samples, and it fails closed on an empty sample set or non-positive T.",
        "knowledge": "Apdex (Application Performance Index) turns a pile of response-time samples into one 0..1 satisfaction score against a target time T: requests at or under T are 'satisfied', up to 4T 'tolerating' (counted half), and beyond that 'frustrated'. It is a compact SLI that product and ops teams can track and alert on without staring at a full histogram. This module implements the zoning and scoring exactly; the claim proves it matches the published definition on a hand-computed battery, so you inherit a checked SLI rather than a re-implementation to re-audit."
    },
    {
        "name": "csv_rfc4180",
        "lang": "python",
        "claim_id": "CLAIM-LIB-CSV-RFC4180-001",
        "references": ["rfc-4180"],
        "title": "RFC 4180 CSV parse + write",
        "area": "Data / Serialization",
        "evidence_level": "benchmarked",
        "code_files": [
            "csv_rfc4180.py"
        ],
        "artifact": "csv_rfc4180.json",
        "register_metrics": [
            "checks",
            "checks_matched",
            "mismatches",
            "parse_matched",
            "roundtrip_matched"
        ],
        "bind_field": "checks_matched",
        "statement": "The vendored RFC 4180 CSV codec -- which parses and writes CSV DIRECTLY and never imports the csv module -- passes all 17 checks with 0 mismatches: parse(text) equals list(csv.reader(text)) on 12 inputs (quoted fields, embedded delimiters, embedded newlines, doubled quotes, empty fields, CRLF and LF records, and a trailing delimiter), and parse(format_rows(rows)) round-trips 5 record sets (including fields that require quoting).",
        "caveat": "The stdlib csv module is the independent oracle and is NOT imported by the vendored module. Correctness is demonstrated over a fixed battery of RFC-4180-conformant inputs, not proven for every input; the codec models the RFC 4180 core (single-character delimiter and quotechar, doubled-quote escaping, CRLF/LF records) and not dialect extras like comment lines, skipinitialspace, or alternate escape characters.",
        "knowledge": "CSV looks trivial until a field contains a comma, a newline, or a quote -- then you need RFC 4180's quoting rules (wrap the field in double quotes and double any embedded quote), and a hand-rolled str.split(',') silently corrupts the data. This module implements a proper state-machine parser and a quoting writer with zero dependencies; the claim proves the parser agrees with Python's csv module and the writer round-trips, so you inherit a checked codec rather than a split-on-comma bug waiting to happen."
    },
    {
        "name": "varint",
        "lang": "python",
        "claim_id": "CLAIM-LIB-VARINT-001",
        "references": ["protobuf-encoding", "dwarf-5"],
        "title": "Varint / LEB128 integer encoding",
        "area": "Data / Serialization",
        "evidence_level": "benchmarked",
        "code_files": [
            "varint.py"
        ],
        "artifact": "varint.json",
        "register_metrics": [
            "reference_vectors",
            "reference_vectors_matched",
            "published_matched",
            "zigzag_matched",
            "unsigned_roundtrip_ok"
        ],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored varint codec reproduces all 14 published reference vectors (reference_vectors_matched = 14): the 7 LEB128 unsigned vectors (0->00, 1->01, 127->7f, 128->8001, 255->ff01, 300->ac02, 624485->e58e26) and the 7 ZigZag mappings (0->0, -1->1, 1->2, -2->3, 2->4, -64->127, 63->126); and it round-trips losslessly over 76 unsigned values (powers of two up to 2**64-1) and 1004 signed values (-500..499 plus 31/62-bit boundaries).",
        "caveat": "Correctness is demonstrated over the published vectors plus a wide round-trip range, not proven for every integer. Unsigned values must be non-negative; decoding rejects a truncated varint and one exceeding 64 bits. This is the base-128 LEB128 / protobuf wire encoding, not the SQLite or Git variants.",
        "knowledge": "A varint stores an integer in as few bytes as its magnitude needs, using seven bits per byte with the top bit as a continuation flag -- so small numbers cost one byte, and the stream is self-delimiting. It is the integer wire format of Protocol Buffers and many binary protocols; ZigZag mapping first folds signed numbers so that -1, 1, -2 encode as small unsigned 1, 2, 3 instead of maximal values. This module implements both; the claim proves it matches the published LEB128 vectors and round-trips, so you inherit a checked codec rather than a re-implementation to re-audit."
    },
    {
        "name": "pem",
        "lang": "python",
        "claim_id": "CLAIM-LIB-PEM-001",
        "references": ["rfc-7468", "rfc-5280"],
        "title": "PEM textual encoding (RFC 7468)",
        "area": "Security / TLS & PKI",
        "evidence_level": "benchmarked",
        "code_files": [
            "pem.py"
        ],
        "artifact": "pem.json",
        "register_metrics": [
            "n_ders",
            "checks",
            "checks_matched",
            "mismatches"
        ],
        "bind_field": "checks_matched",
        "statement": "The vendored PEM codec (RFC 7468) passes all 11 checks with 0 mismatches: for a fixed set of DER blobs (a small SEQUENCE, empty, single byte, and long payloads) decode(encode(der, label)) round-trips to (label, der), the base64 body matches the stdlib base64 and every line wraps at 64 characters, and a two-block PEM parses into the correct list of (label, der) pairs -- the codec implements the envelope itself and never imports the csv/pem parts of the stdlib beyond base64.",
        "caveat": "The stdlib base64 is the independent oracle for the body. Correctness is demonstrated over a fixed battery, not proven for every input. The module handles the RFC 7468 encapsulation (BEGIN/END labels, 64-column base64, matching END label); it does NOT parse the DER structure inside, validate certificates, or support the optional headers of the legacy RFC 1421 privacy-enhanced-mail format.",
        "knowledge": "PEM is the ubiquitous text form of TLS material: a certificate or key is DER (binary ASN.1), base64-encoded and wrapped between '-----BEGIN CERTIFICATE-----' and '-----END CERTIFICATE-----' lines so it survives copy-paste and config files. Getting the label matching and 64-column wrapping right matters for interoperability. This module encodes and decodes the envelope with zero dependencies; the claim proves it round-trips DER and matches the stdlib base64, so you inherit a checked codec for handling certs and keys in mTLS tooling rather than a re-implementation to re-audit."
    },
    {
        "name": "spki_pin",
        "lang": "python",
        "claim_id": "CLAIM-LIB-SPKI-PIN-001",
        "references": ["rfc-7469", "rfc-8446"],
        "title": "SPKI public-key pins (RFC 7469)",
        "area": "Security / TLS & PKI",
        "evidence_level": "benchmarked",
        "code_files": [
            "spki_pin.py"
        ],
        "artifact": "spki_pin.json",
        "register_metrics": [
            "n_spkis",
            "checks",
            "checks_matched",
            "mismatches"
        ],
        "bind_field": "checks_matched",
        "statement": "The vendored SPKI pinning library passes all 16 checks with 0 mismatches: for each SPKI sample the pin equals base64(sha256(spki)) computed independently via the stdlib hashlib/base64, matches() accepts the correct pin even when it is the backup among several, rejects a wrong pin, and the pin-sha256=\"...\" directive form is well-shaped -- with a constant-time comparison that scans all pins without an early exit.",
        "caveat": "The stdlib hashlib and base64 are the independent oracles. Correctness is over a fixed battery, not proven for every input; the SPKI is treated as opaque bytes (the module does not extract the SPKI from a certificate -- pair it with an X.509 parser). Pinning is operationally risky: pin a backup key and set sane lifetimes, or a key rotation can lock clients out (the reason HPKP was deprecated for the browser HTTP header, though SPKI pinning remains standard for mobile/mTLS clients).",
        "knowledge": "Certificate pinning narrows trust from 'any CA the system trusts' to 'this specific public key (or its backup)'. An RFC 7469 pin is base64(SHA-256(SubjectPublicKeyInfo)); a client stores it and refuses a connection whose chain presents no matching pinned key, defeating a mis-issued-but-technically-valid certificate. This module computes and verifies pins with a constant-time compare; the claim proves the pin equals the hash-of-SPKI and that matching accepts/rejects correctly, so you inherit a checked pinning primitive rather than a re-implementation to re-audit."
    },
    {
        "name": "lamport",
        "lang": "python",
        "claim_id": "CLAIM-LIB-LAMPORT-001",
        "references": ["lamport-1979", "fips-205", "rfc-8391"],
        "title": "Lamport one-time signatures (hash-based, post-quantum)",
        "area": "Security / Post-Quantum Cryptography",
        "evidence_level": "benchmarked",
        "code_files": [
            "lamport.py"
        ],
        "artifact": "lamport.json",
        "register_metrics": [
            "n_cases",
            "valid_ok",
            "tamper_msg_detected",
            "tamper_sig_detected",
            "forgeries_accepted"
        ],
        "bind_field": "valid_ok",
        "statement": "The vendored Lamport one-time signature verifies every honestly-produced signature (valid_ok = 5 over a fixed 5-case battery) and rejects all 15 tampering attempts with forgeries_accepted = 0: for each (seed, message) case, verify(message, sign(message, sk), pk) is True, while verifying the signature against a changed message, against a signature with one byte flipped, and against a different key pair all return False. Security rests only on SHA-256 preimage resistance, so the scheme is post-quantum (not broken by Shor's algorithm).",
        "caveat": "This is a ONE-TIME signature: signing two different messages under the same key leaks the private key and lets an attacker forge -- callers MUST use each key pair once (chain them under a Merkle tree, i.e. XMSS/SLH-DSA, to sign many messages). Correctness and rejection are demonstrated over a fixed battery, not proven for every input; keys/signatures are large (public key 16 KiB), and the deterministic seed-based keygen here is for reproducible evidence, not production key generation (which needs a secret random seed).",
        "knowledge": "Lamport signatures show that a digital signature needs nothing more than a one-way (hash) function: the private key is two secrets per message bit, the public key is their hashes, and signing reveals the secret matching each bit of the message digest -- a verifier re-hashes and checks. Because it relies only on hash preimage resistance, it is quantum-resistant, and it is the conceptual seed of the NIST post-quantum hash-based standards (SLH-DSA / SPHINCS+, XMSS). Vendor it to understand and use a checked post-quantum primitive; the claim proves valid signatures verify and forgeries are rejected, so you inherit a checked one-time signature rather than a re-implementation to re-audit."
    },
    {
        "name": "nist_csf",
        "lang": "python",
        "claim_id": "CLAIM-LIB-NIST-CSF-001",
        "references": ["nist-csf-2.0"],
        "title": "NIST CSF 2.0 coverage",
        "area": "Security / Governance & Compliance",
        "evidence_level": "measured",
        "code_files": [
            "nist_csf.py"
        ],
        "artifact": "nist_csf.json",
        "register_metrics": [
            "n_functions",
            "n_categories",
            "checks",
            "checks_matched",
            "mismatches"
        ],
        "bind_field": "checks_matched",
        "statement": "The vendored NIST CSF 2.0 coverage model matches the published taxonomy and arithmetic on all 30 checks with 0 mismatches: the six Functions are exactly Govern, Identify, Protect, Detect, Respond and Recover; all 22 Categories map to the correct Function (their two-letter prefix); and coverage() computes hand-verified fractions (all six Govern categories -> GV coverage 1.0, a 2-of-3 subset -> 0.6667, the full set -> overall 1.0, the empty set -> 0).",
        "caveat": "The taxonomy is the independently-known NIST CSF 2.0 (CSWP 29) Function/Category structure; the module encodes Functions and Categories (not the finer Subcategories or Informative References) and scores simple category-level coverage, which is a planning aid, not a maturity assessment or a certification. Correctness is demonstrated over a fixed set of checks, not a claim that any particular program is 'compliant'.",
        "knowledge": "The NIST Cybersecurity Framework 2.0 is the common language security programs use to organize and communicate risk work: six Functions (the 2024 revision added Govern) each broken into Categories and Subcategories. Teams map their controls to this structure to see where they are strong and where gaps sit. This module encodes the Function/Category taxonomy and computes coverage; the claim proves the encoded taxonomy matches the framework and the math is correct, so you inherit a checked coverage model rather than a hand-maintained spreadsheet to re-audit."
    },
    {
        "name": "nis2",
        "lang": "python",
        "claim_id": "CLAIM-LIB-NIS2-001",
        "references": ["nis2-directive"],
        "title": "EU NIS2 Directive Article 21 coverage",
        "area": "Security / Governance & Compliance",
        "evidence_level": "measured",
        "code_files": [
            "nis2.py"
        ],
        "artifact": "nis2.json",
        "register_metrics": [
            "n_measures",
            "checks",
            "checks_matched",
            "mismatches"
        ],
        "bind_field": "checks_matched",
        "statement": "The vendored NIS2 coverage model matches the Directive and arithmetic on all 7 checks with 0 mismatches: the encoded measures are exactly the ten Article 21(2) items a..j of Directive (EU) 2022/2555, and coverage() computes hand-verified values -- the empty set -> 0.0, the full set -> 1.0, a 4-of-10 subset -> 0.4 with the missing list its exact complement.",
        "caveat": "The set of measures is the independently-known Article 21(2)(a)-(j) list; the module scores coverage of those ten headline measures, which is an internal gap-tracking aid, NOT legal advice or a determination of regulatory compliance (which depends on national transposition, proportionality to the entity, and competent-authority interpretation). Correctness is demonstrated over a fixed set of checks.",
        "knowledge": "The EU NIS2 Directive (2022/2555) raises the cybersecurity baseline for essential and important entities across the Union; its Article 21(2) lists ten minimum risk-management measures -- from risk analysis and incident handling to supply-chain security, cryptography, and multi-factor authentication. Organizations track which measures they have implemented to prepare for the obligation. This module encodes the ten measures and computes coverage; the claim proves the measures match the Directive and the math is correct, so you inherit a checked gap-tracking model rather than a hand-maintained checklist to re-audit."
    },
    {
        "name": "soc2",
        "lang": "python",
        "claim_id": "CLAIM-LIB-SOC2-001",
        "references": ["aicpa-tsc-2017"],
        "title": "SOC 2 Trust Services Criteria coverage",
        "area": "Compliance / Audit Frameworks",
        "evidence_level": "measured",
        "code_files": ["soc2.py"],
        "artifact": "soc2.json",
        "register_metrics": ["n_categories", "n_common_criteria", "checks", "checks_matched", "mismatches"],
        "bind_field": "checks_matched",
        "statement": "The vendored SOC 2 coverage model matches the AICPA Trust Services Criteria taxonomy and arithmetic on all 8 checks with 0 mismatches: the five Trust Services Categories are exactly Security, Availability, Processing Integrity, Confidentiality and Privacy; the nine Common Criteria series are CC1..CC9; and coverage() computes hand-verified fractions (empty -> 0.0, all nine CC -> 1.0, a 3-of-9 subset -> 0.3333 with the correct missing list).",
        "caveat": "The taxonomy is the independently-known AICPA Trust Services Criteria structure; the module encodes the five categories and the nine Common Criteria series (not the individual points of focus or the category-specific criteria for Availability/PI/Confidentiality/Privacy) and scores simple criteria-level coverage, which is a readiness aid, not a SOC 2 report or an auditor's opinion.",
        "knowledge": "SOC 2 is the service-organization audit report most SaaS vendors are asked for; it attests controls against the AICPA Trust Services Criteria -- five categories, with Security (the Common Criteria CC1..CC9) always in scope and Availability, Processing Integrity, Confidentiality, and Privacy added as needed. Teams map their controls to this structure to plan an audit and track readiness. This module encodes the taxonomy and computes coverage; the claim proves the encoded criteria match the framework and the math is correct, so you inherit a checked readiness model rather than a spreadsheet to re-audit."
    },
    {
        "name": "iso27001",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ISO27001-001",
        "references": ["iso-27001-2022"],
        "title": "ISO/IEC 27001:2022 Annex A coverage",
        "area": "Compliance / Audit Frameworks",
        "evidence_level": "measured",
        "code_files": ["iso27001.py"],
        "artifact": "iso27001.json",
        "register_metrics": ["n_themes", "n_controls", "checks", "checks_matched", "mismatches"],
        "bind_field": "checks_matched",
        "statement": "The vendored ISO/IEC 27001:2022 coverage model matches Annex A and arithmetic on all 13 checks with 0 mismatches: the four themes are Organizational (37 controls), People (8), Physical (14) and Technological (34), summing to 93; control-id validation accepts in-range ids (A.5.1, A.8.34) and rejects out-of-range or unknown-theme ids (A.6.9, A.9.1); and coverage() computes hand-verified per-theme and overall fractions.",
        "caveat": "The theme structure and per-theme control counts are the independently-known Annex A:2022 taxonomy; the module validates a control's theme and in-range number (A.<5-8>.<n>) and scores theme-level coverage, but does not carry each control's title or the ISO/IEC 27002 implementation guidance, and coverage is a planning aid, not a certification.",
        "knowledge": "ISO/IEC 27001 is the international certification standard for an information security management system; the 2022 revision reorganized Annex A into 93 controls under four themes (Organizational, People, Physical, Technological). Organizations pursuing certification track which Annex A controls they have implemented per theme. This module encodes the theme structure and control counts and computes coverage; the claim proves the encoded taxonomy matches the standard (and totals 93) and the math is correct, so you inherit a checked coverage model rather than a spreadsheet to re-audit."
    },
    {
        "name": "pci_dss",
        "lang": "python",
        "claim_id": "CLAIM-LIB-PCI-DSS-001",
        "references": ["pci-dss-4.0"],
        "title": "PCI DSS v4.0 coverage",
        "area": "Compliance / Audit Frameworks",
        "evidence_level": "measured",
        "code_files": ["pci_dss.py"],
        "artifact": "pci_dss.json",
        "register_metrics": ["n_goals", "n_requirements", "checks", "checks_matched", "mismatches"],
        "bind_field": "checks_matched",
        "statement": "The vendored PCI DSS v4.0 coverage model matches the standard and arithmetic on all 20 checks with 0 mismatches: the six goals and twelve requirements are present, each requirement maps to the correct goal (1-2 under goal 1, 3-4 under 2, 5-6 under 3, 7-9 under 4, 10-11 under 5, 12 under 6), and coverage() computes hand-verified per-goal and overall fractions.",
        "caveat": "The requirement-and-goal structure is the independently-known PCI DSS v4.0 taxonomy; the module encodes the twelve top-level requirements and their goal grouping (not the hundreds of sub-requirements or the customized-approach/compensating-control options) and scores requirement-level coverage, which is a scoping and gap-tracking aid, not an Attestation of Compliance or a QSA assessment.",
        "knowledge": "PCI DSS governs any organization that handles payment card data; version 4.0 keeps the familiar twelve requirements under six goals, from 'build and maintain a secure network' to 'maintain an information security policy'. Merchants and service providers track which requirements they meet to scope and prepare for assessment. This module encodes the requirements and their goal grouping and computes coverage; the claim proves the encoded structure matches the standard and the math is correct, so you inherit a checked coverage model rather than a spreadsheet to re-audit."
    },
    {
        "name": "benford",
        "lang": "python",
        "claim_id": "CLAIM-LIB-BENFORD-001",
        "references": ["benford-1938"],
        "title": "Benford's Law leading-digit analysis",
        "area": "Audit / Forensic Analytics",
        "evidence_level": "benchmarked",
        "code_files": ["benford.py"],
        "artifact": "benford.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "expected_ok", "digit_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored Benford's Law analyzer passes all 25 checks with 0 mismatches: the expected distribution equals log10(1 + 1/d) for every digit 1..9 (matching the published frequencies 0.301, 0.176, ... 0.046 to 3 dp and summing to 1), leading-digit extraction is correct on 10 cases (including sub-1 and negative values), and the conformance statistics behave as defined -- a near-Benford dataset (the leading digits of 2**1..2**500) conforms while a strongly non-Benford dataset does not, with a larger MAD and chi-square.",
        "caveat": "Benford's Law is a SCREEN, not proof: many legitimate datasets (bounded ranges, assigned numbers like invoice IDs, small samples) do not follow it, and conformance does not prove data is genuine nor non-conformance prove fraud. The default MAD threshold (0.015, 'close conformity' per Nigrini) is a heuristic. Correctness is demonstrated over a fixed battery of the formula, digit extraction, and statistic behaviour, not proven for every dataset.",
        "knowledge": "Benford's Law says that in many natural datasets the leading digit is 1 about 30% of the time and 9 under 5%, following log10(1 + 1/d). Forensic accountants and auditors screen ledgers, expense reports, and tax data against this distribution: a sharp deviation is a red flag worth investigating (invented numbers tend to be too uniform). This module computes the leading digit, the expected/observed distributions, and the chi-square and MAD statistics; the claim proves the expected distribution equals the Benford formula and the statistics behave as defined, so you inherit a checked anomaly screen rather than a re-implementation to re-audit."
    },
    {
        "name": "double_entry",
        "lang": "python",
        "claim_id": "CLAIM-LIB-DOUBLE-ENTRY-001",
        "references": ["pacioli-1494"],
        "title": "Double-entry bookkeeping invariants",
        "area": "Audit / Accounting Integrity",
        "evidence_level": "measured",
        "code_files": ["double_entry.py"],
        "artifact": "double_entry.json",
        "register_metrics": ["n_journals", "checks", "checks_matched", "mismatches", "classify_correct"],
        "bind_field": "checks_matched",
        "statement": "The vendored double-entry ledger library passes all 13 checks with 0 mismatches: it classifies every journal in a fixed 5-case battery as balanced or unbalanced correctly (including split entries and one-sided postings), the net account balances of every balanced journal sum to exactly zero, and a hand-computed trial balance reproduces the per-account debit/credit totals and net balances exactly (integer minor units, no floating point).",
        "caveat": "The invariant checked is the fundamental balancing identity (total debits == total credits, net balances sum to zero) over a fixed battery, demonstrated not proven for every journal. It does not model account normal-balance sides, chart-of-accounts semantics, multi-currency, sub-ledgers, or period close; amounts are non-negative integer minor units, and the caller supplies well-formed postings.",
        "knowledge": "Double-entry bookkeeping is the 500-year-old integrity check at the heart of every ledger: each transaction posts equal debits and credits, so across the books total debits equal total credits and every account's net balances sum to zero -- the trial balance an auditor runs first. This module checks that invariant and builds a trial balance in integer minor units; the claim proves it identifies balanced vs. unbalanced journals correctly and that the sums are exact, so you inherit a checked ledger primitive rather than a re-implementation with a rounding bug to re-audit."
    },
    {
        "name": "audit_sampling",
        "lang": "python",
        "claim_id": "CLAIM-LIB-AUDIT-SAMPLING-001",
        "references": ["aicpa-audit-sampling"],
        "title": "Attribute-sampling sample sizes (Poisson)",
        "area": "Audit / Statistical Sampling",
        "evidence_level": "benchmarked",
        "code_files": ["audit_sampling.py"],
        "artifact": "audit_sampling.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "example_ok", "consistency_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored attribute-sampling calculator passes all 17 checks with 0 mismatches: each zero-deviation reliability factor equals -ln(1 - confidence) to within table rounding (the Poisson basis); the sample sizes reproduce the standard worked examples (5% tolerable at 95% confidence with 0 expected deviations -> 60; and 24, 30, 93 for other plans); sample size grows monotonically with expected deviations; and for every (tolerable, confidence) the achieved upper deviation rate at the computed size is at most the tolerable rate.",
        "caveat": "The reliability factors are the published AICPA Audit Guide Poisson values (rounded), tabulated only for confidence 90/95/99% and 0-3 expected deviations; the module sizes an ATTRIBUTE sample (tests of controls) and does not cover monetary-unit (dollar-unit) sampling, variables sampling, or finite-population correction. Sizing is a planning aid; evaluating results and the sufficiency of evidence remains the auditor's judgment.",
        "knowledge": "When an auditor tests a control, they need a sample large enough that a clean result gives real assurance. The Poisson (AICPA Audit Guide) method sizes it from a reliability factor R: sample size = ceil(R / tolerable_rate), and after testing, the achieved upper deviation rate is R / sample size -- so a 5% tolerable rate at 95% confidence with zero expected deviations needs 60 items. This module encodes the factors and the arithmetic; the claim proves the factors match their Poisson basis, the sizes match the standard examples, and the plan achieves its tolerable rate, so you inherit a checked sampling calculator rather than a table to re-key."
    },
    {
        "name": "chacha20",
        "lang": "python",
        "claim_id": "CLAIM-LIB-CHACHA20-001",
        "references": ["rfc-8439"],
        "title": "ChaCha20 stream cipher (RFC 8439) from scratch",
        "area": "Security / Stream Ciphers",
        "evidence_level": "benchmarked",
        "code_files": ["chacha20.py"],
        "artifact": "chacha20.json",
        "register_metrics": ["reference_vectors", "reference_vectors_matched", "mismatches", "roundtrips", "roundtrips_ok"],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored from-scratch ChaCha20 (RFC 8439) reproduces all 4 published reference vectors byte-exactly -- the section 2.1.1 quarter round, the section 2.3.2 block-function keystream, the Appendix A.1 all-zero keystream block, and the section 2.4.2 'sunscreen' ciphertext -- with 0 mismatches, and encrypt/decrypt round-trips losslessly on all 7 cases of a varied-length battery.",
        "caveat": "Confidentiality only: ChaCha20 provides no integrity -- an attacker can flip ciphertext bits; use an AEAD (ChaCha20-Poly1305) in real protocols and NEVER reuse a (key, nonce) pair. Pure-Python throughput is far below native crypto, and the implementation is not constant-time: this artifact is for verification, vendoring into audit/teaching contexts, and cross-checking -- not bulk or side-channel-sensitive encryption. Correctness is demonstrated over the published vector set, not proven for all inputs.",
        "knowledge": "ChaCha20 is the stream cipher used by TLS 1.3, WireGuard and OpenSSH: a 4x4 state of 32-bit words (constants, 256-bit key, counter, 96-bit nonce) run through 20 add-xor-rotate rounds produces a 64-byte keystream block that is XORed with the message; decryption is the same operation. This module implements the RFC 8439 IETF variant from scratch in pure integer arithmetic with fail-closed input checks and counter-overflow rejection; the claim proves it matches the RFC's published vectors byte-for-byte, so you inherit a checked reference implementation rather than one more unaudited copy."
    },
    {
        "name": "jwt_hs256",
        "lang": "python",
        "claim_id": "CLAIM-LIB-JWT-HS256-001",
        "references": ["rfc-7515", "rfc-7519", "rfc-4648"],
        "title": "JWS/JWT HS256 sign + strict verify (RFC 7515/7519)",
        "area": "Security / Authentication (JWT)",
        "evidence_level": "benchmarked",
        "code_files": ["jwt_hs256.py"],
        "artifact": "jwt_hs256.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "rfc7515_a1_matched", "rejections_correct"],
        "bind_field": "checks_matched",
        "statement": "The vendored JWS/JWT HS256 library passes all 37 checks with 0 mismatches: the RFC 7515 Appendix A.1 published example signature reproduces exactly (6 checks), the base64url codec matches its RFC 4648 vectors (12), exp/nbf validation with explicit injected time behaves per RFC 7519 at the boundaries (10), the adversarial battery -- alg 'none', asymmetric-alg confusion, tampered payloads, malformed tokens -- is rejected fail-closed (8), and signing is deterministic and round-trips (1).",
        "caveat": "HS256 (symmetric HMAC-SHA256) only: no RSA/ECDSA support, and the verifier accepts exclusively alg=HS256 by design. Claims validation covers exp/nbf with caller-supplied time (the module never reads a clock); aud/iss/sub semantics, key management, rotation and revocation are the caller's responsibility. The published-example and adversarial batteries demonstrate, not prove, correctness for all tokens.",
        "knowledge": "A JSON Web Token is two base64url-encoded JSON parts signed over 'header.payload' -- RFC 7515's JWS compact serialization with claim semantics from RFC 7519. Most JWT vulnerabilities are verifier bugs: accepting alg=none, letting the token pick the algorithm, or sloppy time handling. This module implements sign and a strict verifier (fixed algorithm allowlist, injected time, fail-closed parsing); the claim proves it reproduces the RFC's published example signature and rejects the classic confusion attacks, so you inherit a checked token core instead of another JWT pitfall."
    },
    {
        "name": "punycode",
        "lang": "python",
        "claim_id": "CLAIM-LIB-PUNYCODE-001",
        "references": ["rfc-3492"],
        "title": "Punycode (RFC 3492) encode/decode",
        "area": "Telecom / Internationalized DNS (IDNA)",
        "evidence_level": "benchmarked",
        "code_files": ["punycode.py"],
        "artifact": "punycode.json",
        "register_metrics": ["samples", "samples_matched", "mismatches", "stdlib_checks", "stdlib_ok"],
        "bind_field": "samples_matched",
        "statement": "The vendored Punycode codec reproduces all 19 published RFC 3492 section 7.1 sample strings exactly in both directions (samples_matched = 19, mismatches = 0), accepts the RFC's mixed-case digit spelling on decode, and agrees with Python's independent stdlib punycode codec on all 56 cross-checks over the samples plus a fixed extra battery.",
        "caveat": "Raw Punycode only: no 'xn--' ACE prefix handling and no IDNA normalization (case folding, ContextJ, bidi rules) -- pair it with an IDNA layer for real domain processing. Mixed-case annotation (RFC 3492 appendix A) is intentionally not implemented: the encoder emits lowercase digits as IDNA requires, and sample (I)'s expected form is the canonical lowercase spelling.",
        "knowledge": "Punycode is the Bootstring algorithm instantiated with DNS parameters: it maps any Unicode string to a unique ASCII string (the encoding beneath internationalized domain names' xn-- labels) by emitting the basic code points literally and encoding the positions and values of the rest as generalized-variable-length integers with bias adaptation. This module implements RFC 3492 encode and decode from scratch with the reference implementation's 32-bit overflow ceiling; the claim proves it reproduces every published sample of the RFC in both directions and matches the stdlib's independent implementation, so you inherit a checked IDN building block."
    },
    {
        "name": "dns_name",
        "lang": "python",
        "claim_id": "CLAIM-LIB-DNS-NAME-001",
        "references": ["rfc-1035", "rfc-1123"],
        "title": "DNS hostname validation (RFC 1035/1123)",
        "area": "Telecom / DNS Naming",
        "evidence_level": "measured",
        "code_files": ["dns_name.py"],
        "artifact": "dns_name.json",
        "register_metrics": ["n_cases", "correct", "mismatches", "wire_matched", "equality_matched"],
        "bind_field": "correct",
        "statement": "The vendored DNS hostname validator classifies all 23 battery names correctly (correct = 23, mismatches = 0) -- the 63-octet label and 253-character presentation-name boundaries, the LDH letter-digit-hyphen rule with RFC 1123's digit-start allowance, hyphen edge cases and empty labels -- and passes all 6 wire-format length computations and 5 case-insensitive equality checks, with the label boundary cross-checked against Python's stdlib encoder.",
        "caveat": "Hostname (LDH) validation per RFC 1035 section 2.3.4 and RFC 1123 section 2.1 -- not general DNS-name validation (DNS proper permits arbitrary binary labels), and not IDNA: Unicode names must be Punycode/IDNA-encoded first. Underscore service labels (e.g. _sip._tcp) are non-hostname names and are rejected unless the caller opts in.",
        "knowledge": "A DNS hostname is a dot-separated sequence of LDH labels: 1-63 octets each, letters/digits/hyphens, no leading or trailing hyphen, at most 255 octets in wire form -- which is what limits the presentation form to 253 characters (each label costs a length octet plus a terminating root byte). RFC 1123 relaxed RFC 952 to allow digit-first labels. This module validates names against exactly those published rules and computes the wire length; the claim proves the boundaries sit precisely where the RFCs put them, so you inherit a checked validator instead of a regex approximation."
    },
    {
        "name": "erlang_b",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ERLANG-B-001",
        "references": ["erlang-1917"],
        "title": "Erlang B blocking probability + circuit planner",
        "area": "Telecom / Traffic Engineering",
        "evidence_level": "benchmarked",
        "code_files": ["erlang_b.py"],
        "artifact": "erlang_b.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "exact_rational_ok", "table_rows_ok", "inverse_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored Erlang B library passes all 20 checks with 0 mismatches: the stable recursion agrees with the closed formula recomputed in exact rational arithmetic on all 8 cases to 12 decimal places, satisfies B(1,A) = A/(1+A) algebraically on 4, reproduces the 3 published traffic-table rows for 10 circuits (4.461 E at 1% blocking, 5.092 E at 2%, 6.216 E at 5%) within table precision with the planner inverse recovering N = 10 for each, and is monotone in circuits and traffic.",
        "caveat": "The Erlang B model assumes Poisson arrivals, blocked-calls-cleared (no retry, no queueing) and infinite sources -- real traffic with redial or burstiness needs Erlang C or engineering margin. Published table loads are rounded to 3-4 significant figures, so table rows are checked to 1% relative and the inverse to the same tolerance; the recursion itself is exact to float precision.",
        "knowledge": "Erlang B answers the sizing question of every loss system -- how many circuits (trunks, DSP channels, charging points) does A erlangs of offered traffic need so that at most a target fraction of arrivals is blocked? B(N, A) = (A^N/N!)/sum(A^x/x!), computed here with the overflow-free recursion B(n) = A*B(n-1)/(n + A*B(n-1)), plus the planner's inverse. The claim proves the recursion IS the closed formula (exact-rational agreement) and matches the published engineering tables, so an ISP or telco vendoring it inherits checked dimensioning math."
    },
    {
        "name": "kid",
        "lang": "python",
        "claim_id": "CLAIM-LIB-KID-001",
        "references": ["nets-ocr-giro", "luhn-1960", "brreg-orgnr"],
        "title": "Norwegian KID check digits (MOD10 + MOD11, OCR giro)",
        "area": "Finance / Norwegian Payments (KID)",
        "evidence_level": "benchmarked",
        "code_files": ["kid.py"],
        "artifact": "kid.json",
        "register_metrics": ["tampers", "tampers_caught", "tampers_missed", "mod10_luhn_agreement", "mod10_space", "orgnr_agreement"],
        "bind_field": "tampers_missed",
        "statement": "The vendored KID library misses ZERO of 859095 single-digit tamperings: over the complete space of 4-digit payloads, every single-digit alteration of every valid KID is rejected in BOTH registered variants (MOD10 and MOD11). Its MOD10 agrees with an independent from-scratch Luhn on all 10000 payloads of that space, and its MOD11 agrees with the published organisasjonsnummer construction on a 1027-point sweep with all 3 publicly listed orgnr (Equinor, Bronnoysundregistrene, DNB) validating.",
        "caveat": "Check-digit math per the Nets/Mastercard Payment Services OCR giro system specification -- MOD10 (Luhn weights 2,1 right-to-left) and MOD11 (weights 2..7 cyclic right-to-left, remainder 1 meaning no valid digit). The module enforces the outer 2-25-digit bound; the minimum KID length and which variant applies are per OCR agreement with the bank and must be enforced by the caller. A valid check digit proves well-formedness, never that the invoice exists.",
        "knowledge": "Every Norwegian OCR giro payment carries a KID -- kundeidentifikasjon -- whose last digit is a check digit in one of two registered schemes: MOD10 (the Luhn algorithm, as on payment cards) or the weighted MOD11 (the same construction that protects organisasjonsnummer, where a weighted sum's remainder decides the digit and remainder 1 makes the payload unusable). This module computes, validates and generates both variants in one vendorable file; the claim proves exhaustive single-digit tamper detection and agreement with two independent constructions, so an invoicing system inherits checked payment-reference handling."
    },
    {
        "name": "annuity",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ANNUITY-001",
        "references": ["kellison-2009"],
        "title": "Annuity loan payment + integer-oere amortization",
        "area": "Finance / Loans & Interest",
        "evidence_level": "benchmarked",
        "code_files": ["annuity.py"],
        "artifact": "annuity.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "textbook_payment_mu", "identity_ok", "identity_checks"],
        "bind_field": "checks_matched",
        "statement": "The vendored annuity library passes all 32 checks with 0 mismatches: it reproduces the standard published textbook payment ($100,000 at 0.5% per month over 360 months gives exactly $599.55), satisfies the exact accounting identities on every one of 6 loans -- final balance exactly 0, principal column summing exactly to the principal, every interest cell equal to the banker's-rounded balance-times-rate, payments summing to principal plus total interest -- agrees with an independent 50-digit decimal evaluation of the closed formula on all 6, and handles the zero-rate even split.",
        "caveat": "Constant-rate annuity mathematics in integer minor units: no fees, no rate changes, no day-count conventions, no grace periods -- and the final payment absorbs cumulative rounding by design (it can differ from the constant payment by a few minor units). Norwegian 'effektiv rente' (EU APR) disclosure math is a different calculation not provided here.",
        "knowledge": "An annuity loan repays principal P over n periods at rate i with the constant payment P*i/(1-(1+i)^-n); each payment covers the period's interest first and the remainder amortizes principal, so interest falls and amortization grows over the schedule. Doing this in floating-point kroner is how spreadsheets leak oere. This module computes the payment and the full schedule entirely in integer minor units with banker's rounding, ending at a balance of exactly zero; the claim proves the textbook example and the exact identities an accountant would check, so an invoicing or loan system inherits a schedule that reconciles to the oere."
    },
    {
        "name": "bloom_filter",
        "lang": "python",
        "claim_id": "CLAIM-LIB-BLOOM-001",
        "references": ["bloom-1970"],
        "title": "Bloom filter (no false negatives + exact FP analysis)",
        "area": "Data Structures / Probabilistic Sets",
        "evidence_level": "benchmarked",
        "code_files": ["bloom_filter.py"],
        "artifact": "bloom_filter.json",
        "register_metrics": ["members", "false_negatives", "probes", "false_positives_measured", "formula_checks", "formula_ok"],
        "bind_field": "false_negatives",
        "statement": "The vendored Bloom filter produces ZERO false negatives over an exhaustive 500-member battery (false_negatives = 0 -- the defining guarantee), its measured 46 false positives over 2000 disjoint probes sit within twice the analytical expectation, its false-positive formula matches exact rational recomputation on all 5 (m, n, k) triples to 12 decimal places, and optimal_k reproduces max(1, round((m/n) ln 2)) on all 4 cases.",
        "caveat": "No-false-negatives is verified exhaustively for the fixed battery and holds by construction for any inserted element, but the false-POSITIVE rate is probabilistic: the classical formula assumes independent uniform hash functions, and the SHA-256 double-hashing here approximates that. No deletion support (that needs a counting filter); serialized filters are only comparable across identical (m, k) parameters.",
        "knowledge": "A Bloom filter answers set membership in O(k) with a bit array m bits wide: k hash functions set k bits per insertion, and a query reports 'present' only when all k bits are set -- so absence answers are definitive and presence answers carry a tunable false-positive rate (1-(1-1/m)^(kn))^k. This module implements the filter with SHA-256-derived double hashing plus the exact analysis functions; the claim proves the no-false-negative guarantee and that the analysis math is exact, so you inherit a checked probabilistic set for dedupe, caching and pre-filters."
    },
    {
        "name": "uuid_tools",
        "lang": "python",
        "claim_id": "CLAIM-LIB-UUID-001",
        "references": ["rfc-9562"],
        "title": "UUID parse/format + deterministic v3/v5 (RFC 9562)",
        "area": "Data / Identifiers (UUID)",
        "evidence_level": "benchmarked",
        "code_files": ["uuid_tools.py"],
        "artifact": "uuid_tools.json",
        "register_metrics": ["rfc_vectors", "rfc_vectors_matched", "mismatches", "stdlib_cross_checks", "stdlib_matched", "bit_checks", "bit_checks_ok"],
        "bind_field": "rfc_vectors_matched",
        "statement": "The vendored UUID library reproduces all 12 RFC 9562 published vectors exactly (rfc_vectors_matched = 12, mismatches = 0), agrees with Python's independent stdlib uuid3/uuid5 on all 64 cross-checks over a fixed (namespace, name) battery, and places the version and variant bits correctly in all 128 bit-placement checks.",
        "caveat": "Deterministic name-based UUIDs only (v3 MD5, v5 SHA-1) plus parse/format/inspect: no random v4 or time-based v1/v6/v7 GENERATION, since the module refuses nondeterminism by design (inspection of those versions works). Name-based UUIDs are deterministic by specification: the same namespace and name always produce the same UUID -- do not use them where unlinkability matters. MD5/SHA-1 here are identity derivations per the RFC, not security primitives.",
        "knowledge": "A UUID is a 128-bit identifier whose version and variant bits encode how it was generated; RFC 9562 (which obsoletes RFC 4122) specifies the layout and algorithms. Name-based UUIDs (v3/v5) hash a namespace UUID plus a name so independent systems derive the SAME identifier without coordination -- ideal for content addressing and idempotency keys. This module implements parse, format, inspection and v3/v5 generation from scratch; the claim proves it matches the RFC's vectors and the stdlib's independent implementation, so you inherit checked identifier plumbing."
    },
    {
        "name": "base58",
        "lang": "python",
        "claim_id": "CLAIM-LIB-BASE58-001",
        "references": ["base58-draft"],
        "title": "Base58 encode/decode (Bitcoin alphabet)",
        "area": "Data / Encoding",
        "evidence_level": "benchmarked",
        "code_files": ["base58.py"],
        "artifact": "base58.json",
        "register_metrics": ["reference_vectors", "reference_vectors_matched", "mismatches", "roundtrip_cases", "roundtrip_ok"],
        "bind_field": "reference_vectors_matched",
        "statement": "The vendored Base58 codec reproduces all 24 published reference vectors exactly in both directions (reference_vectors_matched = 24, mismatches = 0) -- the draft-msporny-base58 vectors including 'Hello World!' -> '2NEpo7TZRRrLZSi2U' and the Bitcoin Core encode/decode set with its long leading-zero runs -- and round-trips losslessly on all 14 structural cases.",
        "caveat": "Raw Base58 only -- NOT Base58Check: no version byte and no double-SHA-256 checksum, so a typo in an address-like string is not detected at this layer. The alphabet is the Bitcoin one (no 0, O, I, l); other ecosystems (Ripple, Flickr) permute it. Decoding is strict: any character outside the alphabet fails closed.",
        "knowledge": "Base58 is base-conversion encoding over an alphabet chosen to survive human eyes and keyboards: the ambiguous 0/O and I/l are removed, and each leading zero byte is written as a literal '1' so binary prefixes survive the integer conversion. It is the encoding of Bitcoin addresses, IPFS CIDs (base58btc) and many key formats. This module implements encode and decode from scratch with fail-closed alphabet checking; the claim proves it matches the published vector sets byte-for-byte, so you inherit a checked codec instead of a copy-pasted gist."
    },
    {
        "name": "pt100",
        "lang": "python",
        "claim_id": "CLAIM-LIB-PT100-001",
        "references": ["iec-60751"],
        "title": "Pt100 RTD curve (IEC 60751 Callendar-Van Dusen)",
        "area": "Industrial / Temperature Sensing (RTD)",
        "evidence_level": "benchmarked",
        "code_files": ["pt100.py"],
        "artifact": "pt100.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "table_points", "table_ok", "sweep_points", "roundtrip_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored Pt100 library passes all 18 checks with 0 mismatches: it reproduces all 8 published IEC 60751 standard-table resistance points (100.0000 ohm at 0 degC, 138.5055 at 100, 18.5201 at -200, 390.4811 at 850, ...), each point independently re-derived from the standard coefficients at 50-digit decimal precision, round-trips temperature through resistance and back to under 1e-6 degC on all 1051 points of a full-span 1-degree sweep (worst 3.6e-10), and scales exactly to Pt1000.",
        "caveat": "This is the STANDARD IEC 60751 curve (alpha = 0.00385 sensors, -200..850 degC), not a calibration: a physical sensor has a tolerance class (AA/A/B/C), lead-wire resistance, self-heating and drift that this module does not model. Individual sensor calibration replaces the standard coefficients with fitted ones.",
        "knowledge": "Pt100 platinum RTDs are the workhorse of industrial temperature measurement, and IEC 60751 standardizes their resistance-temperature relationship via the Callendar-Van Dusen polynomial (quadratic above 0 degC, an added quartic term below). Converting a measured resistance to a temperature correctly -- including the exact quadratic inversion above zero -- is exactly the kind of formula that gets mistyped in PLC code. This module implements both directions with fail-closed domain checks; the claim proves the published table points and micro-degree round-trip precision, so you inherit checked sensor math."
    },
    {
        "name": "slo_burnrate",
        "lang": "python",
        "claim_id": "CLAIM-LIB-SLO-BURNRATE-001",
        "references": ["sre-workbook-2018", "google-sre-2016"],
        "title": "SLO burn-rate alerting math (SRE Workbook ch. 5)",
        "area": "SRE / SLO Alerting",
        "evidence_level": "benchmarked",
        "code_files": ["slo_burnrate.py"],
        "artifact": "slo_burnrate.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "workbook_rows", "workbook_rows_ok", "policy_tiers_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored burn-rate library passes all 17 checks with 0 mismatches: it reproduces the Google SRE Workbook's published 30-day alerting table exactly (2% budget in 1 h is burn rate 14.4, 5% in 6 h is 6, 10% in 3 d is 1, each with its long/12 short window), validates the shipped three-tier policy against the formula, satisfies 7 algebraic identities (including burn rate 1000 exhausting a 30-day budget in 0.72 h), and implements the multiwindow condition so an at-threshold or single-window signal does NOT page.",
        "caveat": "The arithmetic of the Workbook's method, not an alerting system: it computes burn rates, thresholds and windows -- your monitoring stack must measure the error ratios. The published table assumes a 30-day SLO period; other periods rescale via the same formula. Threshold comparisons are strict-greater by design, so a ratio exactly at threshold does not fire.",
        "knowledge": "Error-budget alerting pages on how FAST the budget burns, not on raw error rates: burn rate = budget fraction consumed times period over window, so burn 14.4 means a 30-day budget gone in 50 hours. The Workbook's recommended policy pairs each long window with a short confirmation window (long/12) so pages stop when the bleeding stops, and tiers page/ticket severity. This module implements that arithmetic exactly; the claim proves the published table and the multiwindow semantics, so your alerting rules inherit checked math instead of re-derived constants."
    },
    {
        "name": "ewma",
        "lang": "python",
        "claim_id": "CLAIM-LIB-EWMA-001",
        "references": ["roberts-1959", "nist-sematech"],
        "title": "EWMA + control-chart limits (Roberts / NIST)",
        "area": "Observability / Statistical Process Control",
        "evidence_level": "benchmarked",
        "code_files": ["ewma.py"],
        "artifact": "ewma.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "fraction_matched", "nist_values_matched"],
        "bind_field": "checks_matched",
        "statement": "The vendored EWMA library passes all 150 checks with 0 mismatches: the float recursion matches exact rational (Fraction) recomputation to 12 decimal places on all 76 points, the control-limit width factors match on all 50, and it reproduces the NIST/SEMATECH e-Handbook's published worked example -- all 21 EWMA values of the 20-point dataset (lambda 0.3, target 50) and the published steady-state control limits.",
        "caveat": "EWMA smoothing and control-limit arithmetic only: choosing lambda and L, estimating sigma, and acting on out-of-control signals are process decisions. The NIST example is reproduced at its published rounding; the exact-rational oracle proves the arithmetic, not the statistical appropriateness of EWMA for a given signal.",
        "knowledge": "The EWMA z_i = lambda*x_i + (1-lambda)*z_{i-1} weights recent observations geometrically and is both the standard smoother behind latency/utilization dashboards and Roberts' control chart for detecting small process shifts, with limits that widen as sqrt(lambda/(2-lambda)*(1-(1-lambda)^(2i))) toward steady state. This module implements the recursion and the chart limits; the claim proves exact-rational agreement and the published NIST example, so you inherit checked smoothing math for monitoring pipelines."
    },
    {
        "name": "cis_controls",
        "lang": "python",
        "claim_id": "CLAIM-LIB-CIS-001",
        "references": ["cis-controls-v8-1"],
        "title": "CIS Critical Security Controls v8.1 taxonomy + IG coverage",
        "area": "Compliance / Security Frameworks",
        "evidence_level": "measured",
        "code_files": ["cis_controls.py"],
        "artifact": "cis_controls.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "n_controls", "n_safeguards", "ig1_safeguards"],
        "bind_field": "checks_matched",
        "statement": "The vendored CIS Controls library passes all 38 checks with 0 mismatches: the encoded taxonomy carries the published shape of CIS Critical Security Controls v8.1 -- 18 Controls and 153 Safeguards with the Implementation Group cumulative counts IG1 = 56, IG2 = 130, IG3 = 153 -- verified control-by-control (18 checks) and total-by-total (6), with coverage arithmetic exact on all 13 assessment cases.",
        "caveat": "A faithful encoding of the framework's structure and counts, not the safeguard texts (vendor those from CIS directly under their license) and not an assessment: coverage scoring reports what the caller declares implemented. Framework versions matter -- these counts are v8.1 (2024); v8.0 distributed safeguards differently.",
        "knowledge": "The CIS Critical Security Controls are the most widely used prioritized baseline of defensive practices, organized since v8 into 18 Controls containing 153 Safeguards, tiered into Implementation Groups: IG1 (56 safeguards) as essential cyber hygiene for every enterprise, IG2 (cumulative 130) and IG3 (all 153) as resources and risk grow. This module encodes that structure and scores declared coverage per IG; the claim proves the encoded counts match the published framework and the arithmetic is exact, so a security program inherits a checked assessment skeleton."
    },
    {
        "name": "gdpr",
        "lang": "python",
        "claim_id": "CLAIM-LIB-GDPR-001",
        "references": ["gdpr-2016-679"],
        "title": "GDPR structure, Art. 5 principles + Art. 32 measures",
        "area": "Compliance / Privacy (GDPR)",
        "evidence_level": "measured",
        "code_files": ["gdpr.py"],
        "artifact": "gdpr.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "articles", "chapters", "partition_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored GDPR library passes all 14 checks with 0 mismatches: the encoded 11 chapter ranges PARTITION the Regulation's 99 articles exactly (verified article-by-article, exhaustively), 7 published anchor articles resolve to their correct chapters (Art. 5 to II, Art. 17 to III, Art. 33 to IV, Art. 83 to VIII, ...), the principle and measure sets match Article 5 (six lettered principles plus accountability) and Article 32(1) (four measures), and coverage percentages agree with exact Fraction arithmetic.",
        "caveat": "An encoding of the Regulation's published structure and enumerations, not legal advice: implementing all Article 32 measures does not make processing lawful, and coverage scoring reports what the caller declares. Article texts are not embedded -- read them at EUR-Lex; national implementations add member-state specifics on top.",
        "knowledge": "The GDPR -- Regulation (EU) 2016/679 -- is the backbone of European privacy law: 99 articles in 11 chapters, with Article 5 stating the processing principles (lawfulness, purpose limitation, data minimisation, accuracy, storage limitation, integrity/confidentiality, accountability) and Article 32 the security-of-processing measures every controller and processor must weigh. This module encodes that structure with fail-closed lookups and coverage scoring; the claim proves the chapter ranges partition all 99 articles and the enumerations match the Regulation, so a compliance tool inherits a checked map of the law's shape."
    },
    {
        "name": "mus_sampling",
        "lang": "python",
        "claim_id": "CLAIM-LIB-MUS-001",
        "references": ["aicpa-audit-sampling"],
        "title": "Monetary-unit sampling: PPS selection + tainting projection",
        "area": "Audit / Monetary-Unit Sampling",
        "evidence_level": "benchmarked",
        "code_files": ["mus_sampling.py"],
        "artifact": "mus_sampling.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "starts_checked", "top_stratum_guarantee"],
        "bind_field": "checks_matched",
        "statement": "The vendored monetary-unit sampling library passes all 10 checks with 0 mismatches: the top-stratum guarantee -- an item at least as large as the sampling interval is selected -- holds for EVERY one of the 500000 possible selection starts of the fixed population (exhaustive, as does the selection-point count identity), zero-value items are never selected, the guide's worked projection reproduces ($3,000 item overstated 10% with a $5,000 interval projects $500), and all 4 projection cases match exact Fraction recomputation, including top-stratum actuals and understatements.",
        "caveat": "Fixed-interval (systematic) PPS selection and tainting projection in exact arithmetic -- not the full MUS evaluation: upper-misstatement limits with reliability factors, expansion factors for expected misstatement, and sample-size planning live in the audit_sampling module and the auditor's judgment. Negative book values are rejected (the guide samples credits separately), and the selection start is caller-supplied, not generated.",
        "knowledge": "Monetary-unit sampling treats every krone/dollar in a population as the sampling unit, so a NOK 700,000 invoice is 700,000 chances -- large items are selected with probability proportional to size, and anything at least one sampling interval big is selected with certainty (the top stratum). Misstatements found in sampled items project to the population by tainting: the misstatement fraction of the item times the interval. This module implements the selection and projection in exact Fraction arithmetic; the claim proves the selection guarantees exhaustively and the projection against independent recomputation, so an audit tool inherits checked PPS mechanics."
    },
    {
        "name": "fairness_metrics",
        "lang": "python",
        "claim_id": "CLAIM-LIB-FAIRNESS-001",
        "references": ["hardt-2016", "feldman-2015"],
        "title": "Group-fairness metrics (parity, four-fifths, equalized odds)",
        "area": "AI Governance / Fairness Metrics",
        "evidence_level": "benchmarked",
        "code_files": ["fairness_metrics.py"],
        "artifact": "fairness_metrics.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "hand_computed_ok", "property_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored fairness library passes all 73 checks as exact Fraction equalities with 0 mismatches: 10 hand-computed values on a fixed two-group audit (demographic-parity difference exactly 1/4, disparate-impact ratio exactly 1/2 failing the four-fifths rule, equalized-odds difference exactly 2/5), 60 property checks over a deterministic battery (relabel-invariance, [0,1] bounds, zeros on identical groups), the perfect-classifier equalized-odds zero, and the exact 4/5 threshold boundary.",
        "caveat": "Measurements, not verdicts: which fairness metric matters, at what threshold, over which population is a governance decision, and the metrics can conflict with each other and with calibration (the impossibility results). Rates are computed on the supplied sample; statistical uncertainty, intersectional subgroups and the choice of protected attribute are the caller's responsibility.",
        "knowledge": "When an enterprise audits a model for disparate treatment, three measurements carry most reviews: demographic parity (do groups get selected at the same rate), the EEOC four-fifths rule (is the lowest selection rate at least 4/5 of the highest — the classic adverse-impact screen Feldman et al. formalized), and Hardt et al.'s equalized odds (are true- and false-positive rates equal across groups). This module computes all three from per-group confusion counts in exact rational arithmetic; the claim proves the arithmetic and the defining properties, so an audit inherits checked numbers rather than a spreadsheet to re-derive."
    },
    {
        "name": "calibration_ece",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ECE-001",
        "references": ["guo-2017"],
        "title": "Expected Calibration Error (ECE/MCE) reliability binning",
        "area": "AI Governance / Model Calibration",
        "evidence_level": "benchmarked",
        "code_files": ["calibration_ece.py"],
        "artifact": "calibration_ece.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "independent_agreement_ok", "battery_pairs"],
        "bind_field": "checks_matched",
        "statement": "The vendored calibration library passes all 14 checks as exact Fraction equalities with 0 mismatches: 7 hand-computed values (two predictions at confidence 4/5 with one correct give ECE exactly 3/10; a perfectly calibrated fixture gives exactly 0; the right-closed bin edges place 0.0, 0.1 and 1.0 correctly), agreement with an independent first-principles re-derivation on a 240-pair battery for 5, 10 and 15 bins, and the estimator's bound and permutation-invariance properties.",
        "caveat": "ECE is an audit statistic, not a guarantee: it depends on the bin count, aggregates away per-class and per-slice effects, and a low ECE does not imply correct individual probabilities. Float confidences are converted to exact rationals via limit_denominator(1e12); the binning follows Guo et al.'s right-closed convention ((m-1)/M, m/M] with 0.0 in the first bin.",
        "knowledge": "A model that says '90% confident' should be right about 90% of the time — that property is calibration, and modern networks notoriously lack it (Guo et al. 2017). The standard audit measurement partitions predictions into M equal-width confidence bins and sums the gap between each bin's accuracy and its average confidence, weighted by bin size: ECE. This module computes the bins, ECE and worst-bin MCE in exact arithmetic; the claim proves the numbers against hand computation and an independent re-derivation, so a model-risk review inherits a checked calibration figure."
    },
    {
        "name": "dp_composition",
        "lang": "python",
        "claim_id": "CLAIM-LIB-DP-001",
        "references": ["dwork-roth-2014"],
        "title": "Differential-privacy budget composition + accountant",
        "area": "AI Governance / Privacy Budgets",
        "evidence_level": "benchmarked",
        "code_files": ["dp_composition.py"],
        "artifact": "dp_composition.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "property_ok", "accountant_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored DP-composition library passes all 49 checks as exact Fraction identities with 0 mismatches: 4 hand-computed compositions (0.5 and 0.25 compose sequentially to exactly 3/4 and in parallel to exactly 1/2), 40 theorem-shaped properties over a deterministic ledger battery (sequential additivity and permutation-invariance, parallel-equals-max never exceeding sequential, group privacy exactly k*epsilon), and 5 fail-closed accountant checks including refusal of a 1/10^12 overspend with the ledger state unchanged.",
        "caveat": "The BASIC composition bounds (Dwork-Roth Theorems 3.16 and parallel/McSherry): tight in the worst case but pessimistic for many mechanisms — advanced composition, RDP and zCDP accountants give smaller epsilons and are out of scope. Parallel composition is sound only when the caller guarantees disjoint data partitions, which the function cannot check. Epsilons say nothing about whether the underlying mechanism actually implements its claimed noise.",
        "knowledge": "An enterprise running differentially-private releases spends a privacy budget: each (epsilon, delta) mechanism consumes some, and the totals compose by theorem — sequential runs on the same data add up, runs on disjoint partitions cost only the maximum, and protecting groups of k individuals scales epsilon by k (Dwork & Roth 2014). This module computes those bounds in exact rational arithmetic and ships a fail-closed accountant that refuses any spend past the budget before recording it; the claim proves the theorem shapes and the refusal behaviour, so a privacy office inherits checked budget arithmetic."
    },
    {
        "name": "eu_ai_act",
        "lang": "python",
        "claim_id": "CLAIM-LIB-AI-ACT-001",
        "references": ["eu-ai-act-2024-1689"],
        "title": "EU AI Act structure (prohibitions, high-risk areas, tiers)",
        "area": "AI Governance / EU AI Act",
        "evidence_level": "measured",
        "code_files": ["eu_ai_act.py"],
        "artifact": "eu_ai_act.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "prohibitions", "high_risk_areas", "articles"],
        "bind_field": "checks_matched",
        "statement": "The vendored AI Act library passes all 9 checks with 0 mismatches: the encoded structure matches the final OJ text of Regulation (EU) 2024/1689 — 13 chapters, 113 articles, 13 annexes, exactly eight Article 5(1) prohibited practices (a)-(h) and exactly eight Annex III high-risk areas — the five operative tiers are anchored to their chapters/articles, membership logic is exact, screening verdicts fail on any prohibition hit, and coverage percentages match exact Fraction arithmetic.",
        "caveat": "An encoding of the enacted text's structure, verified against CELEX 32024R1689 — not legal advice: Annex III areas carry conditions and exceptions in the full text, classification of a real system belongs to counsel, and the popular 'unacceptable/limited/minimal risk' pyramid labels are Commission-communication vocabulary, not the Regulation's operative terms ('minimal risk' does not occur in the enacted text). Staged application dates and Level 2 acts are not encoded.",
        "knowledge": "The EU AI Act is the world's first comprehensive AI regulation: it prohibits eight practices outright (Article 5 — social scoring, untargeted face scraping, workplace emotion inference, ...), regulates high-risk systems in eight Annex III areas (employment, essential services, law enforcement, ...), imposes Article 50 transparency duties, and governs general-purpose AI models with a systemic-risk tier. An enterprise AI inventory needs exactly this map to triage systems. This module encodes the verified structure with fail-closed screening; the claim proves the encoded shape matches the OJ text, so a governance tool inherits a checked skeleton of the law."
    },
    {
        "name": "nist_ai_rmf",
        "lang": "python",
        "claim_id": "CLAIM-LIB-AI-RMF-001",
        "references": ["nist-ai-rmf-1-0-2023"],
        "title": "NIST AI RMF 1.0 Core taxonomy + coverage",
        "area": "AI Governance / NIST AI RMF",
        "evidence_level": "measured",
        "code_files": ["nist_ai_rmf.py"],
        "artifact": "nist_ai_rmf.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "categories_total", "subcategories_total"],
        "bind_field": "checks_matched",
        "statement": "The vendored AI RMF library passes all 18 checks with 0 mismatches: the encoded Core matches NIST AI 100-1 — four functions (GOVERN, MAP, MEASURE, MANAGE) with published category counts 6/5/4/4 totalling 19 and subcategory counts 19/18/22/13 totalling 72, plus the seven characteristics of trustworthy AI — and per-function coverage on three fixed programmes matches exact Fraction arithmetic.",
        "caveat": "Encodes the framework's SHAPE (functions, category identifiers and counts), not the category prose — pair it with the NIST AI RMF Playbook for actionable text. The RMF is voluntary and outcome-oriented; coverage of a category is the caller's declaration, not an assessment of adequacy, and subcategory-level tracking is not included.",
        "knowledge": "NIST's AI Risk Management Framework is the de facto shared vocabulary for enterprise AI governance programmes: GOVERN builds the organizational structures, MAP contextualizes systems and risks, MEASURE quantifies them, MANAGE acts — 19 categories and 72 subcategories articulating seven characteristics of trustworthy AI. A maturity assessment is at bottom a coverage map over that taxonomy. This module encodes the verified Core with exact coverage scoring; the claim proves the counts match the published framework, so an assessment tool inherits a checked skeleton."
    },
    {
        "name": "iso_42001",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ISO-42001-001",
        "references": ["iso-iec-42001-2023"],
        "title": "ISO/IEC 42001:2023 AIMS structure + SoA scoring",
        "area": "AI Governance / AI Management Systems",
        "evidence_level": "measured",
        "code_files": ["iso_42001.py"],
        "artifact": "iso_42001.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "annex_a_controls", "annex_a_groups"],
        "bind_field": "checks_matched",
        "statement": "The vendored AIMS library passes all 14 checks with 0 mismatches: the encoded structure matches ISO/IEC 42001:2023 — management-system clauses 4-10 with their official titles and normative Annex A's 38 controls in 9 control objectives (A.2-A.10), with per-group counts (3/2/5/4/9/5/4/3/3) matching two independent identifier-level listings — and Statement-of-Applicability accounting is Fraction-exact and fail-closed (a group cannot declare more controls applicable than it contains).",
        "caveat": "Encodes the standard's structure (clause titles, objective names, control counts), not its licensed control text — buy the standard for the prose. Clause and annex titles were verified against the standard's own table of contents; the per-group control counts come from two agreeing identifier-level secondary listings, not the paywalled text itself. SoA scoring reports a declaration; certification requires an accredited audit.",
        "knowledge": "ISO/IEC 42001 is the first certifiable AI management system standard — the ISO-27001 pattern applied to AI: harmonized clauses 4-10 (context, leadership, planning, support, operation, evaluation, improvement) plus a normative Annex A of 38 AI-specific controls in 9 objectives, applicability documented in a Statement of Applicability. Enterprises anchor their AI governance certification on exactly this skeleton. This module encodes it with fail-closed SoA arithmetic; the claim proves the encoded shape and the accounting, so a compliance tool inherits a checked frame."
    },
    {
        "name": "dora_eu",
        "lang": "python",
        "claim_id": "CLAIM-LIB-DORA-001",
        "references": ["eu-dora-2022-2554"],
        "title": "DORA structure + resilience-pillar coverage",
        "area": "AI Governance / Financial ICT Resilience (DORA)",
        "evidence_level": "measured",
        "code_files": ["dora_eu.py"],
        "artifact": "dora_eu.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "articles", "chapters", "pillars"],
        "bind_field": "checks_matched",
        "statement": "The vendored DORA library passes all 22 checks with 0 mismatches: the encoded 9 chapter ranges PARTITION the Regulation's 64 articles exactly (verified article-by-article), 11 anchor articles resolve to their chapters, the five resilience pillars (ICT risk management, incident reporting, resilience testing, third-party risk, information sharing) carry their official chapter titles and map to chapters II-VI, and pillar coverage matches exact Fraction arithmetic.",
        "caveat": "An encoding of Regulation (EU) 2022/2554's published structure, verified against CELEX 32022R2554 — not legal advice. DORA's Level 2 technical standards (RTS/ITS) add binding detail not encoded here; which entities are in scope (Art. 2) and proportionality carve-outs are the caller's analysis. Pillar coverage reports a declaration, not supervisory compliance.",
        "knowledge": "DORA harmonizes digital operational resilience across the EU financial sector — banks, insurers, investment firms and their critical ICT providers — applying from 17 January 2025. Its requirements organize into five pillars: ICT risk management (Ch. II), incident management and reporting (Ch. III), resilience testing incl. TLPT (Ch. IV), ICT third-party risk (Ch. V) and information sharing (Ch. VI). Any AI system a financial entity operates is ICT under DORA, which makes this the enterprise-architecture frame around AI governance in finance. This module encodes the verified structure; the claim proves the chapter partition and pillar anchoring, so a resilience programme inherits a checked map."
    },
    {
        "name": "model_card",
        "lang": "python",
        "claim_id": "CLAIM-LIB-MODEL-CARD-001",
        "references": ["mitchell-2019"],
        "title": "Model-card completeness (Mitchell et al. 2019)",
        "area": "AI Governance / Model Documentation",
        "evidence_level": "measured",
        "code_files": ["model_card.py"],
        "artifact": "model_card.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "sections"],
        "bind_field": "checks_matched",
        "statement": "The vendored model-card library passes all 8 checks with 0 mismatches: the encoded section taxonomy matches the nine sections of Mitchell et al.'s FAT* 2019 paper verbatim (Model Details through Caveats and Recommendations), and completeness scoring is Fraction-exact on full, empty and partial cards — whitespace-only sections count as empty and unknown section names fail closed rather than silently scoring as gaps.",
        "caveat": "Structural completeness only: a present section can still be vacuous prose, so 100% means 'all nine sections present and non-empty', never 'adequately disclosed'. The taxonomy is the paper's proposal — ecosystem model cards (e.g. Hugging Face's) extend or rename sections, and mapping those onto the paper's nine is the caller's decision.",
        "knowledge": "Model cards are the disclosure document of record for trained models: Mitchell et al. proposed nine sections covering what the model is, what it is for, how it behaves across factors, and what it must not be used for. Enterprise AI inventories increasingly REQUIRE a card per deployed model, which makes 'is the card structurally complete' a governance gate worth automating. This module scores exactly that, fail-closed on typoed section names; the claim proves the taxonomy matches the paper and the arithmetic is exact, so a review pipeline inherits a checked completeness gate."
    },
    {
        "name": "conformal_split",
        "lang": "python",
        "claim_id": "CLAIM-LIB-CONFORMAL-001",
        "references": ["gentle-conformal-2021"],
        "title": "Split conformal prediction (quantile + coverage theorem)",
        "area": "AI Assurance / Conformal Prediction",
        "evidence_level": "benchmarked",
        "code_files": ["conformal_split.py"],
        "artifact": "conformal_split.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "theorem_checks", "theorem_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored split-conformal library passes all 32 checks with 0 mismatches: the published quantile rule qhat = ceil((n+1)(1-alpha))-th smallest calibration score reproduces 6 hand-computed ranks (including the classic n=100, alpha=0.1 -> rank 91), and THE COVERAGE THEOREM IS ENUMERATED — over 15 pool-by-alpha combinations, exhaustive leave-one-out coverage lands inside [1-alpha, 1-alpha + 1/n] as an exact Fraction, ties never fall below 1-alpha, prediction sets shrink monotonically in alpha, and the too-few-calibration-points case honestly returns everything.",
        "caveat": "The guarantee is MARGINAL (on average over calibration draws, not per input) and rests on exchangeability: distribution shift between calibration and deployment voids it. Enumerated coverage verifies the mechanism on fixed pools; it cannot certify any particular deployed model's scores.",
        "knowledge": "Split conformal prediction turns ANY scoring model into prediction sets with a distribution-free, finite-sample coverage guarantee: calibrate nonconformity scores on held-out data, take the ceil((n+1)(1-alpha))-quantile, and include every candidate scoring at or below it — the true answer lands inside with probability at least 1-alpha (Angelopoulos & Bates 2021). It is the workhorse of AI uncertainty quantification, from classification to LLM factuality gating. This module implements the quantile, prediction sets and an exhaustive leave-one-out coverage enumerator; the claim proves the coverage theorem by enumeration, so an assurance case inherits checked conformal machinery."
    },
    {
        "name": "selective_risk",
        "lang": "python",
        "claim_id": "CLAIM-LIB-SELECTIVE-001",
        "references": ["selective-2017"],
        "title": "Selective classification (coverage, risk, risk-coverage curve)",
        "area": "AI Assurance / Selective Prediction",
        "evidence_level": "benchmarked",
        "code_files": ["selective_risk.py"],
        "artifact": "selective_risk.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "hand_ok", "property_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored selective-classification library passes all 15 checks as exact Fraction equalities with 0 mismatches: 6 hand-computed audit values (coverage exactly 1/2 at threshold 0.7 with selective risk exactly 1/4; full coverage reproducing the plain mean 3/8), 8 structural properties of the risk-coverage curve over a 40-point battery (last point coverage exactly 1 at the unconditional mean, monotone coverage, permutation invariance), and the zero-coverage case failing closed rather than reporting 0.",
        "caveat": "The curve describes the evaluated sample only: thresholds chosen on it are estimates, the confidence signal may be miscalibrated, and selective risk at coverage 0 is undefined by definition. Loss values are the caller's; the module never decides what counts as an error.",
        "knowledge": "A selective classifier may abstain: accept an input when confidence clears a threshold, and be judged only on what was accepted — coverage is the accept rate, selective risk the error rate among accepted (Geifman & El-Yaniv 2017). The risk-coverage curve is the menu of operating points an abstention policy can buy, and it is how 'the model defers to a human below X% confidence' becomes a measurable contract. This module computes all of it in exact rational arithmetic; the claim proves the definitions and their structural properties, so an escalation policy inherits checked numbers."
    },
    {
        "name": "shannon_entropy",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ENTROPY-001",
        "references": ["shannon-1948"],
        "title": "Shannon entropy, cross-entropy, KL and perplexity",
        "area": "AI Assurance / Information Measures",
        "evidence_level": "benchmarked",
        "code_files": ["shannon_entropy.py"],
        "artifact": "shannon_entropy.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "anchors_ok", "property_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored information-measures library passes all 40 checks with 0 mismatches: 10 exact anchors (a fair coin is exactly 1.0 bit; uniform 4/8/16/32-outcome distributions are exactly 2/3/4/5 bits; Shannon's own worked example H(1/2,1/4,1/4) is exactly 1.5 bits; perplexity of uniform-8 is exactly 8) and 30 theorem-shaped properties over a deterministic battery (uniform maximality, Gibbs' inequality KL >= 0, the chain identity H(p,q) = H(p) + KL(p||q) to 1e-12, permutation invariance).",
        "caveat": "Distributions are validated exactly (Fractions summing to exactly 1 — floats are read at their printed decimal value), but log arithmetic is float with documented 1e-12 tolerances on identities. Infinite KL (q zero where p is not) fails closed rather than returning a number. Entropy of a MODEL requires its true distribution; estimates from samples carry estimation error this module does not quantify.",
        "knowledge": "Shannon (1948) defined the units AI evaluation is written in: entropy measures a distribution's information in bits, cross-entropy is exactly the training loss of a language model, perplexity its exponential, and KL divergence the drift between model and reference. When an eval report states 'perplexity 12.3', this is the arithmetic behind it. This module implements the four measures with exact input validation and fail-closed infinities; the claim proves Shannon's identities including his own worked example, so evaluation code inherits checked information arithmetic."
    },
    {
        "name": "gsn_case",
        "lang": "python",
        "claim_id": "CLAIM-LIB-GSN-001",
        "references": ["gsn-standard", "safety-cases-2024"],
        "title": "GSN assurance-case structure validation",
        "area": "AI Assurance / Safety Cases",
        "evidence_level": "benchmarked",
        "code_files": ["gsn_case.py"],
        "artifact": "gsn_case.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "mutations", "mutations_caught", "mutations_missed"],
        "bind_field": "checks_matched",
        "statement": "The vendored GSN validator passes all 50 checks with 0 mismatches: a fixed exemplar exercising every legal edge type of the GSN Community Standard v3 validates clean, an honestly-undeveloped case validates, every one of 12 adversarial single mutations is caught (mutations_missed = 0 — illegal edge types in both relations, a circular argument, an unsupported goal, an undeveloped-with-support contradiction, a solution with outgoing edges, a disconnected argument island, a rootless cycle), and the exhaustive 36-pair supported_by enumeration admits exactly the standard's 4 legal pairs.",
        "caveat": "Structural validity only: the validator proves the argument GRAPH is well-formed (typed edges, acyclic, one root, no dangling goals), never that the argument is SOUND — a well-formed case can still rest on weak evidence or a bad decomposition. The single-root rule follows the GSN module convention; multi-rooted collections need one module per top-level claim.",
        "knowledge": "Safety and assurance cases — increasingly demanded for AI systems (Clymer et al. 2024) — are written in Goal Structuring Notation: goals decompose via strategies down to solutions (evidence), with context, assumptions and justifications attached. A circular argument, a dangling goal, or evidence in the wrong place invalidates the case before anyone reads the prose, and exactly that is machine-checkable. This module validates GSN structure fail-closed; the claim proves every rule via mutation testing and exhaustive edge-type enumeration, so an assurance workflow inherits a checked case linter."
    },
    {
        "name": "tool_guard",
        "lang": "python",
        "claim_id": "CLAIM-LIB-TOOL-GUARD-001",
        "references": ["saltzer-1975", "progent-2025"],
        "title": "Default-deny tool-call policy for LLM agents",
        "area": "AI Assurance / Agent Privilege Control",
        "evidence_level": "benchmarked",
        "code_files": ["tool_guard.py"],
        "artifact": "tool_guard.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "empty_policy_denies", "mutations", "mutations_denied", "mutations_missed"],
        "bind_field": "mutations_missed",
        "statement": "The vendored tool-call policy engine misses ZERO of 20 adversarial mutations: from a fixed policy and its 4 allowed exemplar calls, every single-field corruption (renamed tool, argument pushed outside its constraint type, injected extra argument, removed required argument) is DENIED; the empty policy denies all 40 calls of a fixed battery (fail-safe defaults, enumerated); and the constraint semantics are type-strict (True does not satisfy exact 1, max compares as exact Decimal so \"10.5\" is caught by max 10) — 72 checks, 0 mismatches.",
        "caveat": "Deterministic input-space restriction, not intent understanding: the policy cannot judge whether an ALLOWED call is wise, and prompt injection that stays inside the allowed envelope passes — scope envelopes tightly and pair with monitoring. The policy protects tool CALLS; it does not sandbox what a permitted tool then does.",
        "knowledge": "An agent with tools needs the two oldest rules in security applied per call: fail-safe defaults and least privilege (Saltzer & Schroeder 1975), the posture LLM privilege-control frameworks like Progent build on. A call is denied unless a rule explicitly allows it, and an argument the rule does not mention is denied too — so a prompt-injected 'also send the report to attacker@evil' dies on the unknown-argument rule, not on hope. This module implements that engine with typed, Decimal-exact constraints; the claim proves default-deny by exhaustive mutation, so an agent runtime inherits a checked policy gate."
    },
    {
        "name": "owasp_llm10",
        "lang": "python",
        "claim_id": "CLAIM-LIB-OWASP-LLM-001",
        "references": ["owasp-llm-top10-2025"],
        "title": "OWASP Top 10 for LLM Applications 2025 taxonomy",
        "area": "AI Assurance / LLM Application Security",
        "evidence_level": "measured",
        "code_files": ["owasp_llm10.py"],
        "artifact": "owasp_llm10.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "risks"],
        "bind_field": "checks_matched",
        "statement": "The vendored OWASP LLM Top 10 library passes all 9 checks with 0 mismatches: the encoded taxonomy matches the published Version 2025 list verbatim — ten entries LLM01..LLM10 with Prompt Injection ranked first, the 2025 additions System Prompt Leakage (LLM07) and Vector and Embedding Weaknesses (LLM08), and Unbounded Consumption as LLM10 — and mitigation-coverage arithmetic is Fraction-exact.",
        "caveat": "An encoding of the published list (verified against the official v2025 PDF), not the entry prose — read the document for mitigations. Coverage of a risk is the caller's declaration that mitigations exist, not an assessment of their strength; the Top 10 is a prioritized vocabulary, not a complete threat model.",
        "knowledge": "The OWASP Top 10 for LLM Applications is the shared vocabulary between AI engineering and security review: prompt injection, sensitive-information disclosure, supply chain, poisoning, improper output handling, excessive agency and the rest. A security review of an LLM product is at bottom a coverage map over this list. This module encodes the verified 2025 taxonomy with fail-closed coverage scoring; the claim proves the list matches the publication, so a review pipeline inherits a checked checklist skeleton."
    },
    {
        "name": "slsa_levels",
        "lang": "python",
        "claim_id": "CLAIM-LIB-SLSA-001",
        "references": ["slsa-v1-1"],
        "title": "SLSA v1.1 Build levels + cumulative assessment",
        "area": "AI Assurance / Supply-Chain Integrity",
        "evidence_level": "benchmarked",
        "code_files": ["slsa_levels.py"],
        "artifact": "slsa_levels.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "subsets_enumerated", "subsets_ok"],
        "bind_field": "checks_matched",
        "statement": "The vendored SLSA library passes all 26 checks with 0 mismatches: the four published v1.1 Build-track levels carry their published names, one-line requirements and focus rows (Build L0 No guarantees through Build L3 Hardened builds), and level assessment is verified EXHAUSTIVELY — all 16 subsets of the four capability flags yield exactly the level an independent re-derivation of the cumulative rule assigns, with gap-capping proven (a hardened platform without signed provenance assesses at L1, not L3).",
        "caveat": "A level describes the BUILD's integrity, never the code's quality, and assessment consumes the caller's declared capabilities — verifying provenance is a separate act. SLSA v1.1 (approved 2025-04-21) has been superseded by v1.2 with the same Build-track structure; the level definitions encoded here are v1.1's.",
        "knowledge": "SLSA grades how trustworthy an artifact's build is, on a cumulative ladder: provenance exists (L1), signed provenance from a hosted platform (L2), hardened isolated builds (L3). ML supply chains attach model artifacts to exactly this ladder — 'which level built this model file' is becoming a procurement question. This module encodes the verified v1.1 Build track and computes achieved levels fail-closed; the claim proves the ladder by exhaustive subset enumeration, so a supply-chain assessment inherits checked level logic."
    },
    {
        "name": "zta_tenets",
        "lang": "python",
        "claim_id": "CLAIM-LIB-ZTA-001",
        "references": ["nist-zta-2020"],
        "title": "NIST SP 800-207 Zero Trust tenets",
        "area": "AI Assurance / Zero Trust Architecture",
        "evidence_level": "measured",
        "code_files": ["zta_tenets.py"],
        "artifact": "zta_tenets.json",
        "register_metrics": ["checks", "checks_matched", "mismatches", "tenets"],
        "bind_field": "checks_matched",
        "statement": "The vendored Zero Trust library passes all 5 checks with 0 mismatches: the encoded seven tenets match NIST SP 800-207 section 2.1, anchored by their published phrases (all data sources and computing services are considered resources; per-session access; dynamic policy; posture monitoring; dynamic, strictly-enforced authentication; telemetry-driven improvement), and coverage arithmetic is Fraction-exact.",
        "caveat": "Short labels faithful to the published tenets, not the full SP 800-207 text; SP 800-207 itself notes a pure zero-trust implementation may not be achievable, and coverage is the caller's declaration. Tenet-level coverage says nothing about the quality of the policy engine enforcing it.",
        "knowledge": "NIST SP 800-207's seven tenets define zero trust: nothing is trusted by network location, every access is a per-session decision under dynamic policy, and the enterprise continuously measures what it owns. Agentic AI deployments inherit this frame wholesale — every agent, tool endpoint and memory store is a resource, every tool call an access decision. This module encodes the verified tenets with exact coverage scoring; the claim proves the encoding matches the publication, so an architecture review inherits a checked frame."
    },
]
