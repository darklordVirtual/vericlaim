# Claim-Oriented Programming

*A methodology for building software — and its documentation — that cannot lie
about itself, enforced by CI. Design by Contract for the whole repository, for
the age of AI-authored code.*

---

## 1. The problem

Two things are true at once in modern software:

1. **We make claims everywhere.** READMEs quote benchmark numbers. Papers state
   accuracy. Docs describe capabilities. Comments assert invariants. Marketing
   pages cite percentages. Every one of these is an assertion about the
   artifact — and every one can be wrong, stale, or fabricated.

2. **AI now writes much of the code and most of the prose** — fast, fluent, and
   with no memory of what was true yesterday. An assistant will happily update a
   number in the README and not the paper, invent a citation that looks real,
   or restate a corrected claim in its old form three files away. The result is
   **drift**: the documentation and the code slowly, silently disagree, and no
   human notices until a reviewer, an auditor, or a customer does.

Testing catches code that misbehaves. Nothing conventional catches a *project
that misdescribes itself*. That gap is what Claim-Oriented Programming closes.

## 2. The idea, in one sentence

> **A claim is a contract between what the project says about itself and the
> evidence on disk — and the contract is checked, mechanically, on every
> commit.**

If the README says "2.5× compression," there must be a committed artifact that
measures 2.5×, and a machine must verify that the README, the register, and the
artifact all agree. Change one without the others and the build goes red.

## 3. Lineage: from Meyer's contracts to claim contracts

Bertrand Meyer's **Design by Contract** (Eiffel, 1986) gave functions
*preconditions*, *postconditions*, and *invariants* — assertions about code,
checked at **run time**. It made correctness a first-class, executable property
of a program.

Claim-Oriented Programming lifts the same discipline up two levels:

| | Design by Contract (Eiffel) | Claim-Oriented Programming |
|---|---|---|
| Subject | a function / class | the whole project |
| Assertion | pre/post-conditions, invariants | claims: numbers, capabilities, docs |
| Proof obligation | the code satisfies the contract | a committed **artifact** backs the claim |
| Checked | at run time | in **CI**, on every commit |
| Failure mode it prevents | wrong behavior | **drift and self-misdescription** |

Where DbC asks *"does this code do what it promises?"*, COP asks *"does this
project's account of itself match reality, still, today?"* The artifact is the
proof obligation; the CI gate is the runtime.

## 4. The seven principles

1. **No claim without an artifact.** Every number or capability the project
   asserts points to a committed file that establishes it. If you can't produce
   the artifact, downgrade the claim or delete it.

2. **One source of truth: the claim register.** All claims live in a single
   machine-readable register — id, statement, evidence level, artifact(s),
   caveat. Prose *references* the register; it never re-states numbers freely.

3. **The caveat is part of the claim.** A number without its scope and
   limitation is a liability. Quote the caveat with the number or quote
   neither.

4. **Evidence has levels, and they can only be earned.** A claim is graded
   (theoretical → measured → benchmarked → reproduced → machine-checked →
   externally-validated).
   You may not describe a claim above its earned level, and a demotion is
   always allowed.

5. **Documentation binds to the register.** Numbers appear in docs behind
   anchors that tie them to a specific claim field. Drift between prose and
   register fails the gate — the human doesn't have to notice.

6. **Negative results are first-class.** What didn't work is committed, not
   deleted. A register that only contains wins is not trustworthy.

7. **The gate is executable, and adoption is incremental.** Every principle
   above is enforced by a CI gate, not a style guide. Existing violations are
   grandfathered in a baseline so a real project can adopt COP without a
   big-bang cleanup; new violations fail immediately.

## 5. Why this matters more now

An AI assistant is a superb *producer* of claims and a poor *keeper* of them.
It will generate a plausible number, a confident capability statement, a
citation — and it has no stake in whether they stay true. COP makes the
environment, not the author, responsible for truth: the assistant can write
whatever it likes, but the gate will not let a claim survive that its evidence
does not support. This is how you let AI move fast on code and docs **without**
accumulating a fog of quietly-false assertions.

It is also what makes a project *reviewable*. An external reviewer who sees a
green claim gate knows, without re-checking by hand, that every stated number
is backed by a committed artifact and that the docs have not drifted. The gate
turns "trust me" into "verify it yourself, cheaply."

## 6. What this framework gives you

`vericlaim` is a zero-dependency implementation of the gate (Python 3.11+):

- a **claim register** format and parser (`claims/register.yaml`);
- a **gate** that checks register integrity, artifact existence, manifest
  hashes, doc-to-register binding, evidence-level consistency, and a
  configurable stale-string denylist;
- **provenance sidecars** so every produced artifact records how it was made,
  and a **reproduce oracle** (`vericlaim reproduce`) that re-runs each evidence
  script and proves the number still holds (see
  [`design-notes/contract-lineage.md`](design-notes/contract-lineage.md));
- a **baseline** mechanism for incremental adoption;
- a **GitHub Actions** workflow that runs it on every push and PR;
- a worked **example** in a domain (lossless compression) deliberately
  unrelated to where the method was distilled — because the method is
  domain-independent.

Start with [`getting-started.md`](getting-started.md).

## 7. What it is not

COP does not verify that your claims are *true in the world* — only that they
are backed by the artifact you committed and consistently stated everywhere.
Garbage in, consistently-cited garbage out. Its guarantees are: *no unsourced
claim, no silent drift, no claim above its evidence level.* Those three,
enforced, are most of what separates a trustworthy repository from a hopeful
one.

---

*Claim-Oriented Programming and vericlaim are by Stian Skogbrott. Please cite as
in [`../CITATION.cff`](../CITATION.cff).*
