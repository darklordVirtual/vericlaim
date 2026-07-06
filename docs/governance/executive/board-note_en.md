# Board note — Falsifiable AI governance

*One page for the board, risk committee, or steering group. No tooling, no
jargon.*

## The problem

Most of our AI governance lives in documents that *assert* good properties —
"monitored for drift", "human in the loop", "bias assessed". A reader cannot tell
whether the words point to anything real; the document reads the same whether the
program is diligent or cosmetic. The exposure is not the wording — it is the day a
regulator, auditor, or customer asks us to **prove** a decision was sound and the
trail is a policy binder, not evidence.

## The solution

Treat every factual statement we make about an AI system as a **claim**: a
statement bound to evidence, graded by how strong that evidence is, and stated
with its own limits — and refuse to make a claim we cannot back. Weak areas are
named, not hidden. Governance becomes something an auditor can attack and find
holds, rather than something they are asked to trust.

## The business value

- **Defensible audit position.** When challenged, we answer with a claim and its
  evidence, not a shrug.
- **Honest risk visibility.** Weak evidence is graded as weak, so leadership sees
  the real risk surface instead of a uniformly green dashboard.
- **Faster, safer reuse.** One shared register of what is actually known lets
  teams reuse verified building blocks instead of re-arguing the same questions.
- **Vendor independence.** The method is portable across clouds and tools, so
  governance is not rebuilt each time the platform changes.

*It is not legal advice, a certification, or a guarantee a system is safe. It
makes our **account** of the system defensible — that is precisely its value.*

## The first three steps (this quarter, no new tooling)

1. **Grade what we already claim.** Put an evidence level beside each factual
   statement in our current AI documentation. The confident sentences with no
   backing file are our risk list.
2. **Attach an artifact to every number.** For each metric we state, point to the
   file that establishes it. No number without an artifact — otherwise produce it
   or stop stating it.
3. **Adopt one register as the source of truth.** Keep a single list of claims;
   when a document and the register disagree, the register wins.

Steps 1–3 cost only honesty. Automated enforcement (a build-time gate) comes
later, once the discipline is real.

## The ask

Endorse a pilot on one high-visibility AI system (e.g. a customer-facing agent or
a regulated decision-support tool), applying steps 1–3 this quarter and reporting
the resulting claim register and risk list to this body.
