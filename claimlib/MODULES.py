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
    }
]
