<!--
  A VeriClaim master reference. This document is a SYNTHESIS: it does not
  introduce new numbers of its own. Every quantitative statement carries an
  inline citation of the form [ID] that resolves to a registered, gate-
  verified claim (VeriClaim register or the claims library) or to a hash-
  locked literature work in the canon. The registers are authoritative; if a
  figure here ever disagrees with its cited claim, the claim wins. This file
  lives outside doc_globs on purpose — it is a reference work over the
  registers, not a source of primary claims.
-->

# Frontier AI Governance — A VeriClaim Master Reference

*A single, citation-grounded reference that maps every source in the RAG and
claims library, places the verified building blocks into enterprise
architecture (TOGAF, NIST, EU AI Act, ISO/IEC 42001), and condenses the
combined insight of the literature, the theorems, the artifacts and the
runtime experiments into one governance operating model.*

**Status:** synthesis / reference work. **Authority:** the VeriClaim register
(`claims/register.yaml`) and the claims library are the source of truth.
**Every citation in this document is a VeriClaim citation** — a claim ID or a
hash-locked canon work — verifiable via the register, the ledger
(`/ledger/verify`), or the MCP tools (`search_claims`, `ask_research`,
`get_claim_history`).

---

## Table of contents

1. [Executive summary — the singular insight](#1-executive-summary--the-singular-insight)
2. [How to read this document](#2-how-to-read-this-document)
3. [The method: claim-oriented governance](#3-the-method-claim-oriented-governance)
4. [The evidence base: RAG library and canon](#4-the-evidence-base-rag-library-and-canon)
5. [The regulatory and standards layer](#5-the-regulatory-and-standards-layer)
6. [Placing the building blocks in enterprise architecture (TOGAF)](#6-placing-the-building-blocks-in-enterprise-architecture-togaf)
7. [The verified control library](#7-the-verified-control-library)
8. [The ten control objectives — coverage and operationalization](#8-the-ten-control-objectives--coverage-and-operationalization)
9. [Runtime governance: the REMORA/AROMER evidence](#9-runtime-governance-the-remoraaromer-evidence)
10. [Frontier and AGI literature as governance inputs](#10-frontier-and-agi-literature-as-governance-inputs)
11. [The assurance argument](#11-the-assurance-argument)
12. [Honest limitations — what this does NOT prove](#12-honest-limitations--what-this-does-not-prove)
13. [Operating model and cadence](#13-operating-model-and-cadence)
14. [Appendix A — collection index](#appendix-a--collection-index)
15. [Appendix B — verified-theorem index](#appendix-b--verified-theorem-index)
16. [Appendix C — framework crosswalk matrix](#appendix-c--framework-crosswalk-matrix)
17. [Appendix D — glossary](#appendix-d--glossary)

---

## 1. Executive summary — the singular insight

Most AI-governance programs are a stack of assertions: a policy PDF says the
system is fair, robust and overseen, and the reader is asked to trust the
PDF. The insight that emerges when you combine everything in this library —
the regulatory frameworks, the uncertainty theory, the verification
mathematics, the runtime enforcement experiments, and the honest negative
results — is that **governance can be made falsifiable**, and that a
falsifiable governance program is categorically stronger than a persuasive
one.

Four findings, each grounded in a verified claim, compose into that thesis:

- **Honesty is not a virtue you exhort; it is an optimum you can prove.** A
  proper scoring rule makes truthful probability reporting the unique
  minimizer of expected loss — verified exactly over 1028 (true-distribution,
  alternative-report) pairs [THM-SCORE-001]. A governance system that scores
  its components on calibration is therefore *mechanically* rewarding honesty,
  not merely asking for it.

- **Capability comes from verification, not only from scale.** A verifier-
  gated cascade lets a cheap generator plus a selective check dominate a
  monolithic model on the cost/accuracy frontier — established over 87 380
  exhaustive routing tables [THM-ROUTE-001], with the majority-vote
  amplification that powers it proven *and* its honest converse (voting
  *degrades* accuracy when the average voter is worse than chance) proven too
  [THM-VOTE-002]. Governance that routes hard decisions to stronger review and
  abstains under uncertainty is standing on a theorem, not a hope.

- **A fail-closed policy floor delivers a hard safety guarantee — and the
  same evidence base names its limit.** REMORA's policy gate produced a
  **0.0%** unsafe-execution rate on a 700-task adversarial benchmark versus
  10–20% for heuristic baselines [REMORA CLAIM-001], and blocked **all 208**
  independently-sourced AgentHarm scenarios at FAR 0.0% — an
  *externally_validated* result by dataset independence [REMORA CLAIM-002].
  The library refuses to oversell it: the AROMER negative result shows the
  structural policy is metadata-dependent, leaving a **30.7%** residual false-
  accept rate under neutral-looking metadata [REMORA CLAIM-009]. The lesson —
  a policy floor is necessary but not sufficient; it must be paired with
  runtime monitoring — is itself a governed claim.

- **Every regulatory obligation can be traced to a verified control.** The
  public top-level structure of five governance regimes (NIST AI RMF 1.0,
  NIST CSF 2.0, EU AI Act high-risk requirements, ISO/IEC 42001, NIST Privacy
  Framework) — 29 framework elements — maps to 10 shared control objectives
  with **full bidirectional coverage**: no orphan element, no uncovered
  objective, and every objective demanded by at least two frameworks, all
  verified fail-closed [CLAIM-GOV-001].

The combination is the point. Uncertainty quantification tells you *when* to
abstain; the verification mathematics tells you abstention and routing *buy
capability*; the runtime evidence shows a policy floor *works and where it
fails*; the crosswalk shows *which regulator each control answers to*; and the
VeriClaim gate makes the whole chain *refuse to describe itself above its
evidence*. That is a governance program a hostile reviewer can attack and
fail to break — because every load-bearing sentence is bound to an artifact
that reproduces byte-for-byte.

---

## 2. How to read this document

This is a reference work, not a narrative to read front to back. Three
reading paths:

- **Regulator / auditor:** §5 (regulatory layer) → §8 (control objectives) →
  Appendix C (crosswalk matrix) → §12 (limits). You will find, for each
  obligation, the control that answers it and the evidence level it has
  earned.
- **Enterprise architect:** §6 (TOGAF placement) → §7 (control library) → §13
  (operating model). You will find where each building block sits in the ADM
  and how to vendor it.
- **Researcher / builder:** §3 (method) → §7 (control library) → §10 (frontier
  literature) → Appendix B (theorem index). You will find the verified
  primitives and the literature they rest on.

**Citation convention.** `[CLAIM-XXX]`, `[THM-XXX]`, `[REF-NNN]`, `[REMORA
CLAIM-NNN]` and `[DEMO-001]` are claim IDs resolvable in the VeriClaim
register or the claims library. Canon works are cited by their registrar id
(e.g. `arxiv:2407.14981`) and are preserved hash-locked. A citation proves the
number is *registered and gate-verified*; it does not, by itself, prove the
surrounding sentence is true — read the cited claim's own caveat.

---

## 3. The method: claim-oriented governance

VeriClaim is Design-by-Contract lifted from the function to the whole
project. A **claim** is a contract between what a system says about itself and
the evidence on disk, checked in CI. The governance relevance is direct: a
governance assertion ("the model is monitored for drift") becomes a claim with
a committed artifact, an evidence level, and a caveat — or it does not get
written.

**What the gate verifies on every commit** — register integrity (fail-closed
parsing), artifact existence, path containment, provenance sidecars, manifest
hashes, doc binding (prose numbers tied to the register by anchors), evidence-
level honesty (a doc cannot describe a claim above its earned level), stale-
string suppression, and literature integrity (each cited source still hashes
to its registered SHA-256). `vericlaim reproduce` separately re-runs each
evidence script and fails unless the artifact is byte-identical — the number
is *still true today*.

**The evidence ladder** (weakest → strongest): `theoretical < measured <
benchmarked < reproduced < machine_checked < externally_validated`. Grading is
conservative; demotion is always allowed, promotion needs new evidence. This
ladder is the governance program's honesty scale — a control described at
`externally_validated` must have earned it (as REMORA's AgentHarm result did,
by dataset independence [REMORA CLAIM-002]), while a curated crosswalk stays at
`measured` [CLAIM-GOV-001] and a bibliographic pointer stays at `theoretical`
[REF-051].

**The tamper-evident ledger.** The optional Cloudflare truth layer mirrors the
register into a searchable, hash-chained edge service with a witness anchor:
the library ledger currently stands at 1408 entries across 192 verified
bundles, and the client-side verifier confirms the chain has not been
rewritten since the first anchor. This is the mechanism that turns "we have a
governance policy" into "here is the append-only, independently-verifiable
history of every governance claim we have ever made."

**Why this matters for governance specifically.** The single most important
property is *refusal*. The research oracle refuses to answer when no claim or
hash-locked source supports an answer; the gate refuses to let prose outrun
evidence. A governance program built this way cannot quietly accumulate
unsupported reassurance — the failure mode that makes most AI-ethics
documentation worthless to an auditor.

---

## 4. The evidence base: RAG library and canon

The knowledge substrate is a hash-locked literature catalog served as a
vectorized RAG over Cloudflare (Vectorize embeddings, D1 metadata, R2 content-
addressed vault, Workers AI for reranking and query expansion).

**Scale (all figures from the CLAIM-LIB-RAG family):**

| Property | Value | Citation |
|---|---|---|
| Canon works | 180 across 15 collections | [CLAIM-LIB-RAG-001] |
| Registrar-verified into the catalog | 171 | [CLAIM-LIB-RAG-001] |
| Documented drops (honest gaps) | 9, with 0 undocumented | [CLAIM-LIB-RAG-001] |
| Deterministic content-addressed chunks | 9805, all pushed live | [CLAIM-LIB-RAG-002] |
| Live research endpoints verified | end-to-end | [CLAIM-LIB-RAG-003] |
| Library ledger entries / bundles | 1408 / 192 | ledger `/summary` |

**Three honesty properties of the catalog** distinguish it from an ordinary
paper pile:

1. **Retrieval, never evidence.** A work being searchable proves only that it
   was registrar-verified (arXiv/Crossref/DOI) or honestly snapshotted (tier
   `web-snapshot`, `accredited=false`) and hash-locked — *not* that its
   contents are true. Tier travels with every hit.
2. **Refusal at the boundary.** The oracle refuses when no chunk clears the
   relevance bar, and the refusal decision is scored only against trusted
   phrasings of the query (the raw text plus a hardened faithful translation),
   so a prompt-injected query cannot manufacture relevance — the generator is
   the authoritative overclaim guard and declines topics the excerpts do not
   address.
3. **Coverage is checked fail-closed.** A gap in the canon can be *honest* but
   never *silent*: every work is either verified or a documented drop with a
   reason.

The 15 collections span the full governance surface — uncertainty and
routing, LLM/agent architectures, evaluation and calibration, agent security,
AI governance proper, MLOps and enterprise architecture, provenance and
supply chain, formal methods, fairness/privacy/human-impact, assurance cases,
ML training systems, software-engineering/SaaS, marketing science, finance,
and the latest frontier/AGI research. The full index is Appendix A.

---

## 5. The regulatory and standards layer

Collection 05 (AI governance, 18 works) and collection 06 (MLOps and
enterprise architecture, 13 works) hold the regulatory and standards
literature, hash-locked. The **governance crosswalk building block**
[CLAIM-GOV-001] turns that literature into an operational map: it encodes the
stable, public top-level structure of five regimes and maps them to a shared
control vocabulary.

**The five regimes and their elements (as encoded, `framework_map.py`):**

- **NIST AI RMF 1.0** — functions GOVERN, MAP, MEASURE, MANAGE.
- **NIST CSF 2.0** — functions GOVERN, IDENTIFY, PROTECT, DETECT, RESPOND,
  RECOVER.
- **EU AI Act, high-risk requirements (Art. 9–15 themes)** — risk-management
  system, data and data governance, technical documentation, record-keeping,
  transparency, human oversight, accuracy/robustness/cybersecurity.
- **ISO/IEC 42001** — management-system clauses 4–10 (context, leadership,
  planning, support, operation, performance evaluation, improvement).
- **NIST Privacy Framework** — functions IDENTIFY-P, GOVERN-P, CONTROL-P,
  COMMUNICATE-P, PROTECT-P.

**The ten shared control objectives:** governance & accountability, risk
management, data governance, transparency & documentation, human oversight,
robustness & accuracy, logging & traceability, monitoring & post-market,
fairness & non-discrimination, privacy & data protection.

**The verified property** [CLAIM-GOV-001]: 29 framework elements map to the 10
objectives via 42 edges with **full bidirectional coverage** — no orphan
element (every regulatory element answers to at least one objective) and no
uncovered objective (every objective is demanded by at least two frameworks),
verified fail-closed by a checker that raises rather than returning a partial
map. The full matrix is Appendix C.

**What this is and is not.** It is a traceability aid over public framework
*structure* — a reusable building block a project vendors to see which control
objectives each regime demands and to check its own control set against them.
It is **not** legal advice, **not** a compliance certification, and **not**
evidence that any specific control is correctly implemented; article/clause
specifics below the well-known top level are out of scope. That boundary is
part of the claim, not a footnote to it.

---

## 6. Placing the building blocks in enterprise architecture (TOGAF)

An enterprise such as a large operator (energy, telecom, finance) already runs
an architecture practice. Frontier-AI governance succeeds when it plugs into
that practice rather than sitting beside it. The mapping below places the
VeriClaim building blocks into the TOGAF Architecture Development Method (ADM).

| ADM phase | Governance concern | VeriClaim building block | Framework anchor |
|---|---|---|---|
| **Preliminary** | Establish the governance capability | The VeriClaim gate as the architecture-governance mechanism; the register as the requirements repository | ISO 42001 leadership/context; NIST AI RMF GOVERN |
| **A — Vision** | Risk appetite, control objectives | The 10 control objectives [CLAIM-GOV-001] as the target architecture's non-functional requirements | EU AI Act Art. 9; NIST AI RMF MAP |
| **B — Business** | Roles, accountability | `governance_accountability` objective; RACI over the register | ISO 42001 leadership; CSF GOVERN; Privacy GOVERN-P |
| **C — Data & Application** | Data quality, provenance, model documentation | Provenance/supply-chain collection (07); content-addressed vault; `data_governance`, `transparency_documentation` objectives | EU AI Act Art. 10–11; AI RMF MAP |
| **D — Technology** | Robustness, runtime platform | Conformal selective prediction [THM-CONF/DEMO-001]; runtime enforcement [REMORA CLAIM-001/002]; the Cloudflare edge | EU AI Act Art. 15; CSF PROTECT |
| **E — Opportunities & Solutions** | Which controls to build | The verified control library (§7) as a catalogue of reusable, pre-verified solution building blocks | AI RMF MEASURE/MANAGE |
| **F — Migration Planning** | Rollout sequence | The REMORA enterprise TOGAF rollout plan (`docs/enterprise/togaf-enterprise-rollout-plan.md`, REMORA repo) | ISO 42001 planning |
| **G — Implementation Governance** | Enforcement in delivery | The gate in CI (fail-closed); policy-as-code PDP/PEP with fail-closed defaults [REMORA CLAIM-001] | EU AI Act Art. 14 (human oversight); CSF DETECT |
| **H — Change Management** | Drift, monitoring, incident response | `monitoring_postmarket` objective; `vericlaim reproduce`; the witness ledger; anytime-valid monitoring (REMORA REM-020) | EU AI Act Art. 15; CSF RESPOND/RECOVER |
| **Requirements Management (central)** | Single source of truth | The register + CLAIM-GOV-001 crosswalk as the architecture requirements repository | all five regimes |

The organizing idea: **TOGAF gives you the phases; VeriClaim gives each phase
a falsifiable deliverable.** Phase H's "we monitor for drift" becomes a
reproduce-checked claim; Phase G's "we enforce policy" becomes a benchmarked
fail-closed gate [REMORA CLAIM-001]; the Requirements Management spine becomes
an append-only ledger rather than a wiki.

---

## 7. The verified control library

The library holds ~40 machine-checked theorem claims and the runtime-
enforcement claims that operationalize governance. They cluster into four
capability families, each a reusable building block (`use_code` /
`import_bundle`).

### 7.1 Uncertainty and selective prediction

The mathematical licence to abstain. Conformal prediction gives distribution-
free coverage guarantees whose exact finite-sample combinatorics are machine-
checked [THM-CONF-001], and a worked runtime demonstration shows conformal
intervals covering the truth in 373 of 400 rounds (0.9325 against a 0.9
target) [DEMO-001]. **Governance use:** this is the primitive behind "the
system knows when it does not know" — the EU AI Act Art. 15 accuracy/robustness
requirement and the AI RMF MEASURE function both cash out here.

### 7.2 Verification-amplification

The proof that verification buys capability. Best-of-n success is an exact
identity over independent attempts [THM-VOTE-001]; majority vote *amplifies* a
better-than-chance voter and — proven honestly — *degrades* a worse-than-
chance one [THM-VOTE-002]; and a verifier-gated cascade dominates a monolith
on cost/accuracy over 87 380 exhaustive tables [THM-ROUTE-001]. **Governance
use:** justifies routing high-risk decisions to stronger review and abstaining
under uncertainty — the human-oversight (Art. 14) and manage (AI RMF MANAGE)
controls rest on this.

### 7.3 Decision theory under uncertainty

The reasoning primitives. Truthful probability reporting uniquely minimizes
expected Brier score [THM-SCORE-001]; the secretary problem's optimal stopping
value matches its threshold rule exactly for n ≤ 20 [THM-STOP-001]; minimax
equals maximin over all 6561 integer-payoff 2×2 zero-sum games [THM-GAME-001];
and variance is non-negative (Jensen for x²) exactly over the grid
[THM-JENSEN-001]. **Governance use:** THM-SCORE-001 is the formal reason a
calibration-scored governance program rewards honesty; THM-GAME-001 underwrites
worst-case (adversarial) planning.

### 7.4 Runtime enforcement

Covered in depth in §9. The fail-closed policy floor [REMORA CLAIM-001/002]
and its honest metadata-dependency limit [REMORA CLAIM-009] are the
`robustness_accuracy`, `human_oversight` and `monitoring_postmarket`
objectives made operational.

---

## 8. The ten control objectives — coverage and operationalization

For each shared objective: which frameworks demand it (from the fail-closed
crosswalk [CLAIM-GOV-001]), which VeriClaim building block operationalizes it,
and the honest evidence level.

1. **Governance & accountability** — AI RMF GOVERN, CSF GOVERN, ISO 42001
   context/leadership/support, Privacy GOVERN-P. *Operationalized by:* the
   register + ledger as the accountable record of every claim. *Level:*
   measured (the ledger verifies; accountability of people is organizational).
2. **Risk management** — AI RMF GOVERN/MAP/MANAGE, CSF IDENTIFY, EU risk-
   management-system, ISO planning. *Operationalized by:* verification-
   amplification routing [THM-ROUTE-001] + conformal abstention [THM-CONF-001].
   *Level:* machine_checked (the math) / benchmarked (the application).
3. **Data governance** — AI RMF MAP, CSF IDENTIFY, EU data-governance, Privacy
   IDENTIFY-P. *Operationalized by:* the provenance/supply-chain collection
   (07) and the content-addressed vault. *Level:* measured.
4. **Transparency & documentation** — AI RMF MAP, EU technical-documentation/
   transparency, Privacy COMMUNICATE-P. *Operationalized by:* claim caveats +
   evidence levels; the doc-binding gate. *Level:* measured.
5. **Human oversight** — AI RMF MANAGE, EU human-oversight, ISO operation.
   *Operationalized by:* verifier-gated routing to human review under
   abstention [THM-ROUTE-001]; REMORA VERIFY/ABSTAIN routing. *Level:*
   machine_checked / benchmarked.
6. **Robustness & accuracy** — AI RMF MEASURE, CSF PROTECT, EU accuracy/
   robustness/cybersecurity, ISO operation. *Operationalized by:* the fail-
   closed policy floor [REMORA CLAIM-001/002]. *Level:* benchmarked /
   externally_validated.
7. **Logging & traceability** — CSF DETECT, EU record-keeping.
   *Operationalized by:* the hash-chained witness ledger; provenance sidecars.
   *Level:* measured.
8. **Monitoring & post-market** — AI RMF MEASURE/MANAGE, CSF DETECT/RESPOND/
   RECOVER, ISO performance-evaluation/improvement. *Operationalized by:*
   `vericlaim reproduce`; anytime-valid monitoring (REMORA REM-020). *Level:*
   measured.
9. **Fairness & non-discrimination** — AI RMF MEASURE, EU data-governance.
   *Operationalized by:* the fairness/privacy collection (09). *Level:*
   theoretical→measured (literature-anchored; application is deployment-
   specific — an honest thin spot, see §12).
10. **Privacy & data protection** — CSF PROTECT, Privacy IDENTIFY-P/CONTROL-P/
    PROTECT-P. *Operationalized by:* the privacy collection (09), GDPR/NIS2
    literature (05). *Level:* measured.

The crosswalk guarantees every one of these is demanded by at least two
frameworks and answered by at least one building block — but the evidence
levels are deliberately uneven, and §12 says where.

---

## 9. Runtime governance: the REMORA/AROMER evidence

The most consequential governance lesson in the library comes from the REMORA-
research project, whose claims are harvested into the library and gate-
verified in their own repository.

**The floor works.** REMORA's full policy gate produced a **0.0%** unsafe-
execution rate on a 700-task adversarial tool-call benchmark, versus 10–20%
for every heuristic baseline, with a Wilson 95% CI on the false-accept rate of
[0.00%, 0.55%] [REMORA CLAIM-001]. The floor is produced by **Stage-1 hard-
block policy invariants** — policy-as-code — not by the multi-oracle consensus
machinery; the claim says so explicitly and forbids citing it as evidence for
the consensus layer. This is fail-closed governance: an unrecognized action
denies by default.

**The floor is externally validated.** On the AI Safety Institute's AgentHarm
benchmark (arxiv:2410.09024), REMORA blocked **all 208** independently-sourced
harmful scenarios at FAR 0.0%, Wilson 95% CI [0.00%, 1.81%] — graded
`externally_validated` because the dataset was independent of REMORA's corpus
[REMORA CLAIM-002]. External validity here is *earned by dataset
independence*, the strongest rung the evidence ladder offers.

**The floor's limit is stated, not hidden.** The AROMER negative result is the
governance masterstroke: under *neutral-looking* trust metadata (trust=0.70),
the structural policy's false-accept rate is **43.0%** (structural only),
falling to **30.7%** after semantic enrichment — a residual gap that
"requires runtime execution monitoring or world-model seeding" [REMORA
CLAIM-009]. The claim is marked a NEGATIVE RESULT that "must NOT be removed or
suppressed," and it also discloses that semantic enrichment *raises* the
false-block (friction) rate. A governance program that publishes its own
worst number is one an auditor can trust on its best number.

**The composite lesson** — and it is a *governed claim*, not an opinion —
is defense-in-depth: a fail-closed policy floor is necessary for a hard safety
guarantee but insufficient against adversaries who supply benign-looking
metadata, so it must be paired with runtime execution monitoring and
anytime-valid drift detection. This is exactly the Art. 15 (robustness) +
Art. 14 (human oversight) + post-market-monitoring composition that the
regulatory layer demands, arrived at empirically.

---

## 10. Frontier and AGI literature as governance inputs

Collection 15 (28 works) holds the latest AGI research, curated because
frontier capability *is* a governance input: you cannot govern what you do not
understand. The collection is deliberately balanced with honest counterpoints.

- **Reasoning and test-time compute** — zero-shot reasoning (`kojima-2022`),
  RL-trained reasoning (DeepSeek-R1, arxiv:2501.12948), reasoning-as-planning
  (RAP), graph-of-thoughts, decoding-time reasoning. *Governance relevance:*
  test-time compute shifts risk from training to inference — monitoring must
  follow.
- **Agents** — Voyager, generative agents, SWE-agent, AutoGen. *Relevance:*
  autonomous tool-use is the exact surface REMORA governs; these define the
  threat model.
- **World models and planning** — MuZero, DreamerV3, decision transformer.
  *Relevance:* planning agents internalize objectives; oversight must reach
  inside the loop.
- **Architectures** — Mamba/S4 state-space models, RWKV, ViT, CLIP, Flamingo.
  *Relevance:* long-context and multimodal expand both capability and attack
  surface.
- **Interpretability** — induction heads, representation engineering,
  influence functions, the Platonic representation hypothesis. *Relevance:*
  the transparency (Art. 13) and human-oversight (Art. 14) obligations become
  tractable only with these tools.
- **AGI framing and its honest limits** — "Sparks of AGI" (arxiv:2303.12712),
  "Levels of AGI" (arxiv:2311.02462), scalable oversight (arxiv:2211.03540),
  and crucially the counterpoint that emergent abilities may be a **metric
  artifact** ("Are Emergent Abilities a Mirage?"). Including the skeptical
  paper next to the AGI-claims paper is the same discipline as publishing the
  AROMER negative result: the library does not sell a narrative it cannot
  defend.

The verifiable-claims agenda this whole system operationalizes is itself in
the canon: "Toward Trustworthy AI Development: Mechanisms for Supporting
Verifiable Claims" (arxiv:2004.07213) [REF-051], alongside "Open Problems in
Technical AI Governance" (arxiv:2407.14981) [REF-057].

---

## 11. The assurance argument

Read as a single claim, the argument this document assembles is:

> *A frontier-AI system is governed to the highest available standard when
> every regulatory obligation is traced to a control [CLAIM-GOV-001], each
> control is a building block whose behavior is verified at a stated evidence
> level (§7), the runtime is fail-closed with an externally-validated safety
> floor [REMORA CLAIM-002] whose limits are disclosed [REMORA CLAIM-009], and
> the entire chain is held in an append-only, reproduce-checked, hash-chained
> register that refuses to describe itself above its evidence (§3).*

Each clause is falsifiable and each is backed. The assurance case is not "trust
this document"; it is "attack any clause — the gate, the ledger and the
reproduce ritual will tell you if it has drifted." That is the difference
between a governance *narrative* and a governance *contract*.

---

## 12. Honest limitations — what this does NOT prove

The discipline that makes the rest credible requires stating the gaps plainly.

- **The gate proves internal consistency and reproducibility, not truth.** Doc
  binding proves a number is *present and register-matched*, not that the
  surrounding sentence is correct, that a benchmark is production-realistic, or
  that evidence was not manipulated before commit.
- **The crosswalk is structural, not legal.** [CLAIM-GOV-001] maps public top-
  level framework structure to control objectives with verified coverage. It is
  not compliance certification and does not reach article/clause specifics.
  Do not present it to a regulator as conformity evidence.
- **Runtime results are simulator-scoped.** REMORA's benchmarks run no real
  shell, network, database or file mutations [REMORA CLAIM-001]; the safety
  floor is a benchmark result pending real-world field validation, and the
  AgentHarm external validity is intent-gating, not verified tool-call
  interception [REMORA CLAIM-002].
- **Fairness is the thinnest rung.** Objective 9 is literature-anchored but its
  operationalization is deployment-specific; this library does not yet carry a
  machine-checked fairness building block comparable to the conformal or
  verifier-math batteries. That is a known gap, stated here rather than papered
  over.
- **Machine-checked theorems are bounded instances.** The exhaustive checks
  (e.g. 87 380 cascade tables [THM-ROUTE-001], 6561 games [THM-GAME-001]) are
  exact *within their stated bounds*; the general asymptotic statements remain
  literature, not proof.
- **Literature citations are bibliographic.** A [REF-NNN] claim asserts the
  registrar record exists and the extract is hash-locked — nothing about the
  cited work's correctness; preprint snapshots may differ from peer-reviewed
  versions.

None of these undermine the thesis; they define its perimeter. A governance
program that knows its own perimeter is the one worth trusting inside it.

---

## 13. Operating model and cadence

**The verification ritual (every change):** produce the artifact
deterministically → register the claim at its earned level with a caveat →
bind any doc number → run `vericlaim` (must print `[OK]`) → when code a
benchmark depends on changed, run `vericlaim reproduce` → on green, refresh the
edge mirror and, for library changes, witness (`--record`) and push
`claims/witness.jsonl` to complete the public anchor.

**Cadence and roles:**

- *Continuous (CI):* the gate on every commit; fail-closed. Owner: every
  contributor.
- *Per release:* `reproduce` over the full register; edge mirror refresh;
  witness. Owner: release engineer.
- *Periodic (governance review):* re-run the crosswalk coverage check; review
  evidence levels for drift or demotion; check the honest-gap list (§12).
  Owner: the accountable governance role (ISO 42001 leadership).
- *On incident:* the ledger's append-only history is the audit trail; the
  reproduce ritual re-establishes which numbers still hold.

**How to consume a building block:** `fetch_bundle` → `import_bundle` (offline
hash verification) → `use_code` (byte-exact vendoring with a binding test). A
consuming project inherits the claim's evidence level and caveat unchanged — an
importer can demote but never silently upgrade.

---

## Appendix A — collection index

180 canon works across 15 collections [CLAIM-LIB-RAG-001]:

| # | Collection | Works |
|---|---|---|
| 01 | Uncertainty and routing | 13 |
| 02 | LLM and agent architectures | 19 |
| 03 | Evaluation and calibration | 11 |
| 04 | Agent security | 12 |
| 05 | AI governance | 18 |
| 06 | MLOps and enterprise architecture | 13 |
| 07 | Provenance and supply chain | 12 |
| 08 | Formal methods | 7 |
| 09 | Fairness, privacy and human impact | 9 |
| 10 | Assurance cases and runtime verification | 3 |
| 11 | ML training and systems | 14 |
| 12 | Software engineering and SaaS | 10 |
| 13 | Marketing and growth | 5 |
| 14 | Finance | 6 |
| 15 | Frontier reasoning and AGI | 28 |

---

## Appendix B — verified-theorem index

The machine-checked building blocks (claims library, `machine_checked` unless
noted). Selected, grouped by family:

- **Uncertainty:** conformal prediction combinatorics [THM-CONF-001..004];
  worked runtime demonstration [DEMO-001, benchmarked].
- **Verification-amplification:** best-of-n identity [THM-VOTE-001]; majority
  amplification + honest degradation converse [THM-VOTE-002]; verifier-gated
  cascade dominance, 87 380 tables [THM-ROUTE-001].
- **Decision theory:** Brier properness [THM-SCORE-001]; secretary stopping
  [THM-STOP-001]; minimax=maximin, 6561 games [THM-GAME-001]; Jensen/variance
  [THM-JENSEN-001].
- **Classical foundations (selected):** Chernoff–Hoeffding [THM-CH-001];
  central limit demonstration [THM-CLT-001, benchmarked]; Johnson–
  Lindenstrauss [THM-JL-001]; KKT [THM-KKT-001]; max-flow/min-cut
  [THM-MFMC-001]; no-free-lunch [THM-NFL-001]; universal approximation
  [THM-UAT-001]; VC dimension [THM-VC-001]; Bayes/posterior
  [THM-BAYES-001, THM-POST-001]; Lean-verified set [THM-LEAN-001..003].

Grade and exact scope live in each claim's register entry; the counts above
are the exhaustive-check sizes recorded in the evidence artifacts.

---

## Appendix C — framework crosswalk matrix

Coverage of the 10 control objectives by the 5 frameworks [CLAIM-GOV-001]. A
cell marks the framework elements that address the objective (abbreviated).

| Objective | AI RMF | CSF 2.0 | EU AI Act | ISO 42001 | Privacy |
|---|---|---|---|---|---|
| Governance & accountability | GOVERN | GOVERN | — | context/leadership/support | GOVERN-P |
| Risk management | GOVERN/MAP/MANAGE | IDENTIFY | risk-mgmt-system | planning | — |
| Data governance | MAP | IDENTIFY | data-governance | — | IDENTIFY-P |
| Transparency & documentation | MAP | — | tech-doc/transparency | — | COMMUNICATE-P |
| Human oversight | MANAGE | — | human-oversight | operation | — |
| Robustness & accuracy | MEASURE | PROTECT | accuracy/robustness | operation | — |
| Logging & traceability | — | DETECT | record-keeping | — | — |
| Monitoring & post-market | MEASURE/MANAGE | DETECT/RESPOND/RECOVER | — | perf-eval/improvement | — |
| Fairness & non-discrimination | MEASURE | — | data-governance | — | — |
| Privacy & data protection | — | PROTECT | — | — | IDENTIFY-P/CONTROL-P/PROTECT-P |

Verified: 29 elements, 42 edges, no orphan element, no uncovered objective,
every objective covered by ≥2 frameworks, checked fail-closed [CLAIM-GOV-001].

---

## Appendix D — glossary

- **Claim** — a contract between a stated fact and a committed artifact,
  checked by the VeriClaim gate.
- **Evidence level** — the honesty rung a claim has earned: theoretical <
  measured < benchmarked < reproduced < machine_checked < externally_validated.
- **Fail-closed** — the default on any unrecognized input is deny/refuse, not
  allow; the property behind both the gate and REMORA's policy floor.
- **Control objective** — one of the 10 shared themes every high-standard AI
  governance program must cover [CLAIM-GOV-001].
- **Canon** — the hash-locked literature catalog (180 works) served as the RAG.
- **Ledger / witness** — the append-only, hash-chained public record of every
  library claim; independently verifiable.
- **Building block** — a reusable, pre-verified claim + code, consumed via
  `import_bundle` / `use_code` with its evidence level and caveat intact.

---

*Compiled as a VeriClaim synthesis. Every citation resolves to a registered,
gate-verified claim or a hash-locked canon work; the registers are
authoritative. Claim-Oriented Programming and VeriClaim by Stian Skogbrott.*
