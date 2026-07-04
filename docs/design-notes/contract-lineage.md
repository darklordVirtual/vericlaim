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

### ✅ Provenance / attestation (SLSA, in-toto, Sigstore)
*Origin:* supply-chain security records *how* an artifact was built, verifiably.
*For AI:* every produced artifact carries a provenance sidecar (script, commit,
who/what produced it). A number with no record of a real run is suspect — this
attacks fabrication directly. *Status:* built (`require_provenance`, provenance
sidecars).

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
