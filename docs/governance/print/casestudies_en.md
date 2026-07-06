# Appendix G — Five worked case studies

Each case follows the same arc: what is *claimed*, what *evidence* the claim
needs, how the claim is *registered*, how the *gate* would fail on drift, how it
is *fixed*, and what remains *unproven*. They are illustrative composites, not
reports on named deployments — the discipline is the point, not the numbers.

## Case 1 — A bank's AI customer-service agent

- **Claimed.** "The agent never discloses another customer's data."
- **Evidence needed.** A red-team benchmark of cross-account probes with a
  measured leak rate, plus the retrieval filter that enforces account scoping.
- **Registered.** `CLAIM` at `benchmarked`: leak rate 0/N on the probe set,
  with the caveat that the benchmark is adversarial-but-finite and does not cover
  novel phrasing.
- **Gate fails when.** Someone edits the marketing page to say "provably cannot
  leak data" — a claim above the evidence. The gate flags the sentence: the
  benchmark earns *benchmarked*, not a proof.
- **Fixed by.** Restating as "no leak observed across N adversarial probes
  (see the caveat)", or producing stronger evidence.
- **Still unproven.** That the benchmark reflects real attacker behaviour; that
  the model will behave the same on inputs outside the probe distribution.

## Case 2 — An internal developer agent with shell access

- **Claimed.** "The agent cannot run a destructive command without human
  approval."
- **Evidence needed.** A runtime policy layer that fails closed, and a benchmark
  of unsafe-action attempts with the blocked rate (the REMORA-style result).
- **Registered.** `CLAIM` at `benchmarked`: 0.0% unsafe-execution on a 700-task
  adversarial set, caveat naming the benchmark and the residual false-accept
  rate honestly.
- **Gate fails when.** The residual false-accept figure is quietly dropped to
  make the control look perfect. The gate's "no deleted negative results" rule
  and the stale-string check catch the omission.
- **Fixed by.** Keeping the negative result in the claim — a control that names
  its own failure rate is more trustworthy than one that hides it.
- **Still unproven.** Safety against attacks not represented in the benchmark;
  correct configuration in a specific environment.

## Case 3 — A high-risk clinical decision-support system

- **Claimed.** "Every regulatory obligation for this high-risk system is
  addressed by a named control."
- **Evidence needed.** A crosswalk from the regime's requirements to control
  objectives to concrete controls with owners and tests.
- **Registered.** `CLAIM` at `measured`: full bidirectional coverage, verified
  fail-closed; caveat that the crosswalk maps *public structure*, not clause
  specifics, and is not certification.
- **Gate fails when.** A control is removed but the coverage claim is not
  updated — the coverage checker reports an uncovered objective and the build
  stops.
- **Fixed by.** Restoring the control or honestly narrowing the claim.
- **Still unproven.** That each control is correctly *implemented* in the
  clinical setting — that is per-deployment evidence (an assurance case), and
  clinical validation is a separate, higher bar.

## Case 4 — A multi-cloud enterprise AI control plane

- **Claimed.** "Our identity and policy governance ports across AWS, Azure, GCP
  and OpenShift without lock-in."
- **Evidence needed.** A coupling crosswalk showing each cloud's mechanism
  coupling on shared open standards, checked so every seam is vendor-neutral.
- **Registered.** `CLAIM` at `measured`: 4 clouds x 6 dimensions on 13 open
  standards, every dimension anchored by a standard shared across at least two
  clouds; caveat that native service names are current at authoring time.
- **Gate fails when.** A dimension is wired to a single-cloud proprietary
  mechanism with no shared standard — the checker reports a non-portable seam.
- **Fixed by.** Coupling that seam on an open standard (OIDC, SPIFFE, OPA/Rego)
  and treating the native service as an adapter.
- **Still unproven.** That a given deployment is configured correctly; the
  crosswalk is an architecture-traceability aid, not a security review.

## Case 5 — A RAG assistant over regulatory documents

- **Claimed.** "The assistant answers only from cited internal sources and
  refuses when unsupported."
- **Evidence needed.** A live test of grounded answers and of refusals on
  off-corpus questions, plus the retrieval-and-citation check that enforces it.
- **Registered.** `CLAIM` at `measured`: grounded-answer and correct-refusal
  behaviour verified end-to-end; caveat that grounding is enforced by retrieval
  plus a citation check, not a proof that every sentence is entailed by its
  source.
- **Gate fails when.** The README claims the assistant "answers only from
  claims" as a guarantee. The honest wording — *designed to* answer from sources,
  with grounding *enforced by* retrieval and a citation check — is what passes.
- **Fixed by.** Matching the wording to the mechanism.
- **Still unproven.** That retrieval never misses a relevant source; that a
  determined prompt-injection cannot influence an answer.

---

*Across all five, the pattern is identical: the claim carries its evidence level
and its limit, the gate refuses drift and refuses description above evidence, and
what remains unproven is stated rather than hidden. That refusal — to accumulate
unsupported reassurance — is the whole method.*
