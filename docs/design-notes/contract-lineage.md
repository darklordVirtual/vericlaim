# Design notes — the contract lineage

*Where vericlaim's ideas come from, and which ones we have built. Written plainly:
each idea gets one line of origin, one line of what it buys against AI-authored
code, and its status.*

vericlaim descends from **Bertrand Meyer's Design by Contract** (Eiffel). Meyer
gave *functions* pre-conditions, post-conditions, and invariants, checked at run
time. vericlaim lifts the same idea to the *whole project's claims about itself*,
checked in CI. This note tracks the other ideas from Eiffel — and its cousins in
provenance and testing — that make the tool fit AI-generated code, where the
failure modes are **fabrication**, **passing-the-demo-but-not-the-general-case**,
**silent drift**, and **untraceable origin**.

Legend: ✅ built · ○ proposed.

---

## Straight from Meyer / Eiffel

### ✅ Contracts as the source of truth
*Origin:* in Eiffel the contract IS the documentation — you cannot state a
guarantee the contract does not make. *For AI:* the claim register is the single
source of truth; docs quote it through anchors, so an assistant cannot write a
number the register does not hold. *Status:* the core of vericlaim.

### ✅ Contract variance / Liskov (evidence can only be earned)
*Origin:* Meyer formalized substitutability — a subtype may weaken pre-conditions
but must not weaken post-conditions. *For AI:* an `evidence_level` may be
*demoted* freely but *promoted* only with new evidence; an assistant cannot
quietly upgrade "measured once" to "externally validated." *Status:* enforced by
the evidence-level taxonomy ([`../evidence-levels.md`](../evidence-levels.md)).

### ✅ Contract as oracle → reproduce-as-oracle
*Origin:* Eiffel's *AutoTest* used the contract as the test oracle. *For AI:*
`vericlaim reproduce` re-runs each claim's evidence script and requires the
artifact to come out byte-identical — so a number is not just present but *still
true today*. Catches code that drifted away from a committed benchmark, and
non-deterministic scripts. *Status:* built (`vericlaim reproduce`).

### ✅ Assertion monitoring levels → gate vs reproduce
*Origin:* Eiffel let you choose how much contract checking to run (pre-conditions
only, all, none). *For AI:* the default gate is fast and side-effect-free
(reads files); `vericlaim reproduce` is the heavier, code-executing level you run
in CI. *Status:* two commands, two levels.

### ○ Class invariant → repository invariant
*Origin:* an Eiffel class invariant must hold at every stable point. *For AI:*
repo-wide properties checked every commit, beyond per-claim checks — e.g. "every
public symbol named in the docs exists in the code," "every claim has a runnable
reproduce." *Status:* proposed; the doc-binding check is a first instance.

---

## Cousins that fit AI especially well

### ✅ Provenance recording (a lightweight cousin of SLSA / in-toto)
*Origin:* supply-chain security records *how* an artifact was built. *For AI:*
every produced artifact carries a provenance sidecar (script, commit, the
artifact's own SHA-256, producer). A number with no record of a real run is
suspect — this attacks fabrication directly. *Status:* built
(`require_provenance`). *Honest scope:* this is provenance **logging**, not
cryptographic attestation — the sidecar is unsigned and `git_commit` is
best-effort. Signed DSSE envelopes (Sigstore / GitHub OIDC) are the enterprise
tier, deliberately not claimed today (see ○ below).

### ○ Signed attestation (DSSE, Sigstore, GitHub OIDC)
*Origin:* verifiable, tamper-evident build provenance. *For AI/enterprise:* sign
the provenance so a reviewer trusts the origin even against a malicious writer.
*Status:* proposed enterprise tier; the v2 sidecar (with artifact/script hashes)
is the substrate a DSSE envelope would wrap.

### ✅ Structured claim tokens (bind value *in place*, not just present)
*Origin:* templating / single-sourced docs. *For AI:* an anchor proves the
number is *somewhere* in the paragraph; a **value token** `<!-- v:CLAIM.field -->`
pins the NEXT literal to the exact position, so "target is 180; actual is 900"
cannot pass by containing 180 elsewhere — closing the
"number-present-but-prose-wrong" gap. *Status:* built and enforced
(`check_value_tokens` in `gate.py`; see the register spec). The richer
generate/substitute-in-CI form remains future work.

### ○ Property-based & metamorphic claims (QuickCheck / Hypothesis)
*Origin:* instead of one example, assert a property over *generated* inputs; when
there is no oracle, assert a *relation* (e.g. `decode(encode(x)) == x`). *For AI:*
the single most useful guard against "looks right on the demo, wrong in general"
— an AI passes the four corpus files but a fuzzed property would catch the fifth.
*Status:* proposed; a claim could carry a `property` to fuzz.

### ○ Per-commit claim diff (semantic versioning for claims)
*Origin:* API contracts classify a change as compatible or breaking. *For AI:*
classify each register change across git history — *strengthened* (fine),
*weakened* (needs sign-off), *evidence demoted/promoted* — so an assistant cannot
silently weaken a guarantee in a large diff. *Status:* proposed.

### ○ Mutation testing of the gate
*Origin:* verify the tests actually catch bugs by mutating the code. *For AI:*
mutate a registered number and confirm the gate goes red — proof the gate is not
asleep. *Status:* the drift demo is a manual instance; automatable.

---

## What we deliberately do not do

- **Full formal specification** (TLA+, Dafny). Powerful, but heavy; a proof can
  be a `theoretical`-level claim pointing at a checked artifact, without vericlaim
  becoming a proof assistant.
- **Runtime contracts on the application code.** vericlaim works at the
  project/claim level. Literal Design-by-Contract on functions (asserts,
  refinement types) is complementary and lives in your code, not this gate.

The guiding rule, in the spirit of the method itself: *add a mechanism only when
it turns a hopeful claim into a checked one.* Everything marked ✅ above does;
the ○ items are honest roadmap, not shipped features.

---

## v0.1 credibility hardening (2026-07)

An external review found three real gaps that were fixed, because a checker you
cannot trust is worse than none:

- **Fail-closed register parsing.** A misparsed register used to return zero
  claims, which the gate read as a valid empty project — silently disabling all
  protection. Now a register that contains `- id:` items but parses to fewer
  raises a hard error (and an unsupported `schema_version` is rejected).
- **Multi-segment claim ids.** The evidence-level check matched claim ids with a
  regex that truncated `CLAIM-EX-001` to `EX-001` and then found nothing —
  silently skipping the check. It now matches the *registered* ids exactly.
- **Path containment.** "Committed artifact" is now enforced: an artifact path
  may not be absolute, use `..`, or symlink out of the repo, and (optionally)
  must be git-tracked.

Each has negative tests. The lesson is the method applied to itself: state only
what you enforce, and enforce what you state.

## v0.1.1 — the baseline fails closed too (2026-07)

A capability demonstration of the Claude skill surfaced a fourth gap in the same
spirit: the register parsed fail-closed, but the **baseline** loader did not. A
malformed `baseline.json` (e.g. a list of bare strings instead of objects with an
`error_id`) raised an uncaught `TypeError` and crashed the gate with a Python
traceback — the one failure mode a trust tool cannot have. `_load_baseline` now
validates structure and raises `RegisterError` on bad JSON, a non-list
`known_violations`, or an entry missing `error_id`; the runner catches it and
prints a clean `[FAIL] claims/baseline.json: …`. Six negative/positive tests
cover it. Fail-closed is now uniform across *every* file the gate reads.

## v0.1.2 — linear-time evidence check (2026-07)

A comprehensive stress campaign (scaling the register to 1000 claims) exposed a
**performance cliff**: the gate took 1.5 s at 500 claims but 102 s at 1000. Root
cause: the evidence-level check ran one `re.search` per registered id per doc
line — O(lines × claims) — and each id produced a distinct pattern, so once the
register passed ~500 claims it overflowed CPython's 512-entry regex cache and
recompiled on every call. The fix compiles **one** boundary-anchored alternation
of all ids a single time and reuses it, and tests the cheap evidence-level
substring first so the id scan only runs on lines that could actually drift.
Whole-token semantics (including token-prefix ids) are unchanged and covered by
two new tests. Result: **1000 claims now verify in 0.33 s instead of 102 s
(~300×)**, and the gate scales linearly through 2000+ claims. The lesson, again
the method applied to itself: an anti-drift tool must not itself fall over at
scale — and only a test at scale finds it.

> These timings are from a one-off local stress run (machine-dependent) and are
> **not** gate-bound claims like the numbers in the register — `docs/design-notes/`
> sits outside `doc_globs` by design (it is narrative, not a result surface).
> Treat them as illustrative of the fix's order of magnitude, not a benchmarked
> claim.
