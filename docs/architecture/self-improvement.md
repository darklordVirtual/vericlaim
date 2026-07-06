# Bounded self-improvement

**Purpose.** Explain the one form of recursive self-improvement that is
*defensible* for a verification tool, why it is bounded the way it is, and its
honest limits. Scope: `vericlaim/selfimprove.py` and `vericlaim improve`.

## Why this is deliberately not "RSI"

Anthropic's note on recursive self-improvement
([anthropic.com/institute/recursive-self-improvement](https://www.anthropic.com/institute/recursive-self-improvement))
is about a system that *fully autonomously designs and develops its own
successor*. Its two central risks are **loss of control** and **compounding
misalignment** — rare errors amplifying as each generation builds the next — and
its recommended posture is bounded change, transparent verification, and a
reliable ability to stop.

A repository-verification tool has no business building a successor. So the
defensible capability here is the *inverse* of autonomy: the tool may **propose**
improvements to its own claims, and it ships a guard that makes any
self-proposed change **provably non-weakening**. It ratchets its own quality up,
never down, and cannot edit its own checker. That is the whole design.

## Mapping the article's concerns to mechanisms

| Concern (article) | Mechanism (here) |
|-------------------|------------------|
| Loss of control | **Propose-only.** `vericlaim improve` prints suggestions and edits nothing. No apply, commit, push, or merge. A `STOP_SELF_IMPROVEMENT` kill-switch sentinel disables it entirely. |
| Compounding misalignment | **`check_non_weakening`.** A candidate is refused unless every guarantee is preserved or strengthened. A regression cannot pass the guard, so errors cannot compound across iterations. |
| Need for verification / inspection | Every proposal is deterministic and logged; the envelope re-checks a captured baseline against the candidate; the guarantee is itself a gated claim (`CLAIM-RSI-001`). |
| Ability to stop / slow | Kill-switch sentinel; propose-only means every step is a human decision, not an autonomous loop. |

## The non-weakening envelope

`check_non_weakening(before, after)` returns the list of ways `after` weakens
`before`. Empty means safe to *consider* (a human still applies it). It refuses:

1. **Red gate** — the candidate must itself pass the gate (fail-closed).
2. **Claim removal** — no registered claim may disappear.
3. **Evidence demotion** — no shared claim may drop on the evidence ladder.
4. **Test-count reduction** — coverage may not shrink.
5. **Baseline growth** — grandfathered-violation debt may not grow.
6. **Verifier-core edit** — the trusted core (`gate.py`, `pathsafe.py`,
   `repro.py`, `reproduce.py`, `register.py`, `provenance.py`, `config.py`,
   `selfimprove.py`) must be byte-unchanged: a self-improvement may not rewrite
   its own checker to pass.

Verified over a fixed adversarial battery in `tools/selfimprove_evidence.py`
(`CLAIM-RSI-001`): every weakening refused, every non-weakening accepted, zero
misclassifications.

## The proposer

`propose(cfg)` scans this repo's own claims and emits honest suggestions —
weak-rung claims that *could* be promoted **if** real evidence is produced,
claims missing a reproduce spec or metrics. It **never** fabricates evidence,
**never** auto-promotes an evidence level, and **never** suggests weakening
anything. Promotion always requires new evidence a human/agent produces in a
gated repo — the same COP rule as everywhere else.

## Running it regularly (the autonomous loop)

`tools/autonomous_loop.py [rounds] [interval_s]` runs the governance heartbeat
round after round: gate (adopt + strict), reproduce, the full test suite, the
autonomous-cycle safety test, then a `Snapshot` compared to the *previous* round
with `check_non_weakening`, then the propose-only improver — all verbose.

It is **bounded autonomy in waves**: the loop continues only while every round is
green **and** non-weakening vs the last. Any regression, red gate, or inter-round
weakening **halts** it ("autonomy withdrawn — a human must review"). It applies
nothing — development stays propose-only; a human acts on the proposals and the
envelope guards whatever they apply. `rounds=0` runs until stopped.

**Operator stop** (two ways): create `claims/STOP_SELF_IMPROVEMENT` (honored at
the top of every round, including on wake from the sleep interval), or interrupt
the process. For unattended cadence, use a large interval or a scheduled CI job;
raising autonomy to guarded auto-apply-to-a-PR (never `main`) is a deliberate,
separate opt-in.

## Honest limits

- Propose-only carries no autonomy risk to bound — that is the point. The apply
  loop is intentionally absent; the boundary is the safety mechanism.
- The envelope guards the repository's *declared guarantees*. It does not make
  the tool smarter and does not prove semantic truth.
- `CLAIM-RSI-001` is `measured`: the property is demonstrated on a fixed, finite
  battery, not proven for all inputs.
