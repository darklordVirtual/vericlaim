# Stop shipping documentation that lies.

[![Claim Gate](https://github.com/darklordVirtual/vericlaim/actions/workflows/claim-gate.yml/badge.svg)](https://github.com/darklordVirtual/vericlaim/actions/workflows/claim-gate.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

Ever caught your README still saying **180 ms** while the benchmark now
measures 900? A citation nobody can find? A "supports X" that stopped being
true two releases ago? Every developer has — and with AI writing code and
prose faster than anyone reviews it, it happens silently, everywhere.

**vericlaim makes documentation, benchmarks and published results mechanically
agree with the evidence that produced them.** Bind a number to its evidence
once; from then on, any drift — in docs, code comments or papers — fails the
build with the exact file and line. Not a convention. A CI gate that fails
closed.

And it is not just prose: the same contract covers **code and reusable
parts**. Comment anchors hold source files to the register, machine-checked
theorems ship as claims, and modules vendored from the claims library carry
binding tests — edit one vendored line and your own suite fails.

Think of it as **CI/CD for claims**: type checking for documentation,
Git-grade integrity for the things your project says about itself.

vericlaim is two halves of one discipline:

1. **The gate** — a zero-dependency CI check that makes every claim, artifact,
   doc and citation mechanically agree, forever.
2. **The knowledge register** — [`claimlib/`](#the-knowledge-register-claimlib):
   reusable, vendorable modules whose key property *is* a claim, each citing
   the hash-locked literature it implements. Not documentation about programs —
   **claims turned into programs**.

Zero runtime dependencies · Python 3.11+ · one command to adopt · built for
AI-authored code and prose (that is the point).

**Contents** ·
[60-second demo](#watch-it-stop-a-lie-60-seconds) ·
[How it works](#how-it-works) ·
[What the gate checks](#what-the-gate-checks) ·
[Proof boundary](#what-vericlaim-proves--and-what-it-does-not) ·
[Worked examples](#worked-examples--four-claim-shapes-four-domains) ·
[**The knowledge register**](#the-knowledge-register-claimlib) ·
[Layout](#layout) ·
[Ecosystem](#beyond-the-gate-the-claim-ecosystem) ·
[Citation](#citation)

---

## Watch it stop a lie (60 seconds)

```bash
pip install git+https://github.com/darklordVirtual/vericlaim   # or copy the zero-dependency vericlaim/ folder in
cd your-project
vericlaim init               # scaffolds config + register + baseline; overwrites nothing
vericlaim                    # runs the gate — a fresh project passes immediately
```

Then make your first claim in three small edits:

**1. Register the number** — `claims/register.yaml`:
```yaml
claims:
  - id: CLAIM-PERF-001
    statement: "The parser handles the 10k-line fixture under 200 ms."
    evidence_level: benchmarked
    artifact: [results/parse_bench.json]   # a committed file that proves it
    metrics: { p95_ms: 180 }
    caveat: "CI hardware, single fixture; not a guarantee under load."
```

**2. Bind a doc to it** — in any file matched by `doc_globs`:
```markdown
<!-- claim:CLAIM-PERF-001 p95_ms -->
The parser runs the 10k-line fixture with a p95 latency of **180 ms**.
```

**3. Run the gate** — `vericlaim`. Green. Now change `180` to `190` in the doc
only and run it again: it **fails with the exact file:line**. That is the entire
product.

Full walkthrough: [`docs/getting-started.md`](docs/getting-started.md).

---

## How it works

One picture. A **claim register** is the single source of truth. Each claim is
backed by a committed **artifact** (produced by a deterministic script, never
typed by hand). Your **docs** quote the numbers through small anchors that bind
them to the register. The **gate** runs in CI and fails the build the moment any
of the three drift apart.

```mermaid
flowchart TD
    S["Deterministic script<br/>(measure / benchmark)"] -->|produces + stamps| A["Artifact<br/>results/bench.json<br/><i>+ provenance sidecar</i>"]
    A -->|cited by| R[("Claim register<br/><b>single source of truth</b><br/>id · number · evidence level · caveat")]
    R -->|number bound by a claim anchor| D["Docs · README · paper"]

    R --> G{{"vericlaim gate<br/>runs in CI, every commit"}}
    A --> G
    D --> G

    G -->|register + artifact + docs agree,<br/>every artifact has provenance| PASS(["Build green ✔"])
    G -->|drift · missing artifact · no provenance · over-stated| FAIL(["Build red - exact file:line"])

    R -.->|vericlaim reproduce| RE{{"re-run each script:<br/>is the artifact still identical?"}}
    RE -.->|yes - the number is still true today| PASS
    RE -.->|no - stale or non-deterministic| FAIL

    classDef truth fill:#eef,stroke:#446,stroke-width:2px;
    classDef ok fill:#e7f7e7,stroke:#2a2;
    classDef bad fill:#fbe7e7,stroke:#a22;
    class R truth;
    class PASS ok;
    class FAIL bad;
```

**Read it as a rule:** *no claim without an artifact; no artifact without
provenance; no doc number that isn't bound to the register; no claim described
above the evidence it has — and every number still reproduces today.* All
enforced automatically.

---

## Why it exists

AI writes code and prose fast, and forgets what was true yesterday. Numbers in
the README stop matching the paper; a corrected claim reappears in its old form
three files away; a citation is invented. **Testing catches misbehaving code.
Nothing conventional catches a project that misdescribes itself.**

Where Bertrand Meyer's **Design by Contract** put pre/post-conditions on
*functions*, checked at *run time*, vericlaim puts contracts on the *project's
claims about itself*, checked in *CI*. Same discipline, lifted a level, for a new
era. The full argument: [`docs/manifesto.md`](docs/manifesto.md) (5-minute read).

---

## What the gate checks

| Check | Guarantee |
|-------|-----------|
| **Artifact existence** | Every file a claim cites exists — *no claim without an artifact.* |
| **Path containment** | Artifacts must live inside the repo (no absolute paths, `..`, or symlink escapes); optionally, must be git-tracked. |
| **Provenance** | Every produced artifact records *how it was made* (script, commit, its own SHA-256), and that recorded hash must still match the file — *no anonymous, no stale number.* |
| **Register ↔ evidence** | A register metric whose key appears in the claim's JSON artifact must equal the stored value — a mistyped number is caught even when the artifact reproduces byte-for-byte. Under `strict`, a metric absent from the evidence fails too. Schema-v2 `metric_bindings` pin a metric to an exact JSON-Pointer location with typed, Decimal-safe comparators. |
| **Register integrity** | Required fields present, valid evidence level, no duplicate ids. |
| **Manifest hashes** | Result artifacts match their SHA-256 — a silently edited number is caught — and every reproduce-backed artifact must be listed (no uncovered evidence). |
| **Doc binding** | Claim anchors tie prose numbers to the register; drift fails the build. |
| **Code binding** | Comment anchors (`# claim:ID field`) bind claims stated in source comments the same way — code that describes itself is held to the register too. |
| **Literature integrity** | Each `literature` entry's committed source must still hash to its registered SHA-256 — a citation can be proven intact, and can never be fabricated or silently swapped. |
| **Evidence levels** | A doc cannot describe a claim above the level it has earned. |
| **Stale-string denylist** | A wording you corrected can never quietly reappear. |

Adoption is **incremental**: pre-existing violations are grandfathered in a
baseline (reported as warnings); new violations fail immediately.

### Continuous verification: `vericlaim reproduce`

The gate above is side-effect-free — it reads files. One command goes further:

```bash
vericlaim reproduce      # re-runs each claim's `reproduce` script and checks
                         # the artifact is byte-identical — the number still holds
```

This is [Eiffel's "contract as oracle" idea](docs/design-notes/contract-lineage.md):
the reproduce command *is* the oracle, run in CI, so a registered number is not
just present but **still true today**. If the code moved on and a benchmark
result silently changed, or a script is non-deterministic, `reproduce` fails and
names the artifact. Because it executes your `reproduce` commands (same trust
level as running your test suite), it is a **separate** command from the default
side-effect-free gate — run it in its own CI job, without deploy secrets.

Two design ideas from Bertrand Meyer's Eiffel drive this — provenance
(attestation) and reproduce-as-oracle — with more catalogued in
[`docs/design-notes/contract-lineage.md`](docs/design-notes/contract-lineage.md).

---

## What vericlaim proves — and what it does not

Precision matters more than a big promise (it is, after all, an anti-overclaim
tool). vericlaim **proves that** the claims you register, the evidence files you
cite, the documentation you bind, and the reproduce scripts you name stay
**internally consistent and reproducible** inside the repository — on every
commit.

It does **not** prove that:

- the benchmark reflects real production load;
- the evidence was not manipulated before it was committed;
- an `externally_validated` claim was actually validated by an outside party
  (the level is your honest assertion; vericlaim only checks it is stated
  consistently);
- *all* documentation is covered — only the docs and numbers you bind;
- a sentence is *semantically* true. A paragraph anchor proves the registered
  number is **present** in the paragraph ("target is 180 ms; actual is 900 ms"
  contains 180 and passes). **Value tokens** close exactly that gap for the
  literals you pin — `<!-- v:CLAIM-X.p95_ms -->**180 ms**` binds *that*
  number, and a drifted pinned literal fails even when the correct value
  appears nearby — but the prose *around* a pinned number can still lie, and
  no gate reads meaning. See
  [`docs/design-notes/contract-lineage.md`](docs/design-notes/contract-lineage.md).

That boundary is the point: *no unsourced claim, no silent numeric drift, no
claim above its stated evidence level, and every number still reproduces.* Those,
enforced, are most of what separates a trustworthy repository from a hopeful one
— and nothing more is claimed.

## Worked examples — four claim shapes, four domains

Claims are not just benchmark numbers. The [`examples/`](examples/) gallery shows
the same discipline for four different kinds of assertion, smallest first:

| Example | Claim shape | Claim |
|---------|-------------|-------|
| [`greetings/`](examples/greetings/) | **capability count** | supports 6 languages |
| [`tipcalc/`](examples/tipcalc/) | **correctness** | all 12 reference cases pass |
| [`rle/`](examples/rle/) | **benchmark ratio** | 8.0584× compression, lossless |
| [`theorem/`](examples/theorem/) | **proved theorem** | p → p machine-checks in 5 steps, from a committed proof object with a hash-verified literature citation |

Each is tiny: a small library, a deterministic script that writes an artifact, a
registered claim, and a doc bound by an anchor. For instance, the compression
one:

<!-- claim:CLAIM-EX-001 overall_ratio -->
A run-length encoder achieves <!-- v:CLAIM-EX-001.overall_ratio -->**8.0584×** overall compression on a fixed corpus,
registered as `CLAIM-EX-001`, backed by
[`examples/rle/artifacts/rle_bench.json`](examples/rle/artifacts/rle_bench.json),
and bound to [`examples/rle/docs/results.md`](examples/rle/docs/results.md). Edit
`8.0584` in either the doc or the register without the other, and the gate fails.

### Applied domain modules

Beyond the toy examples, [`domains/`](domains/) holds five larger, self-contained
modules — each a real, deterministic, `reproduce`-backed artifact that
demonstrates a technique, not roadmap prose. Every number they state is computed
by the code, written to a JSON artifact, and bound to the register (evidence
levels `measured`/`benchmarked`).

| Domain | What it demonstrates | Claim |
|--------|----------------------|-------|
| [`eval_harness/`](domains/eval_harness/) | grounding precision/recall/F1 + refusal accuracy for a cited-answer system, over a fixed gold set | `CLAIM-EVAL-001` |
| [`evidence_graph/`](domains/evidence_graph/) | register-as-a-graph integrity (orphan-claim detection, evidence depth) | `CLAIM-GRAPH-001` |
| [`multitenant/`](domains/multitenant/) | tenant-isolation invariant: no cross-tenant reads, no ledger interleave | `CLAIM-TENANT-001` |
| [`ontologies/`](domains/ontologies/) | a machine-readable claim ontology + register conformance | `CLAIM-ONTO-001` |
| [`cost_routing/`](domains/cost_routing/) | cost-aware model routing under per-request quality floors | `CLAIM-ROUTE-001` |

Their fixtures are synthetic (each module's `docs/results.md` states the scope):
they grade the *method*, not any live model — but the pipeline (evidence →
artifact → claim → bound doc, verified by `reproduce`) is the real thing.

---

## The knowledge register: claimlib

vericlaim is not only a guard against drifting documentation. Its second half,
[`claimlib/`](claimlib/README.md), is a **knowledge register**: a standard
library of small, dependency-free, genuinely reusable modules — in Python,
TypeScript and React — whose key property is a **claim** backed by committed
evidence, and whose claim cites the **hash-locked literature** it implements.
Every layer is machine-verified, so what you vendor is not a snippet but a
checked unit of knowledge:

```
literature/<id>.json   the work (RFC · standard · paper · book), summary hash-locked
        ↑ cited by (`references` — the build refuses an id that does not resolve)
MODULES.py             the claim: statement · evidence level · caveat · citations
        ↑ proven by
evidence.py            a fixed reference battery whose expected values are independently known
        ↑ emits
artifacts/<name>.json  the committed evidence (+ provenance sidecar)
        ↑ packaged as
bundles/<sha256>       content-addressed bundle_v1 — vendor it; edit one byte and your own tests fail
```

<!-- claim:CLAIM-LIB-INDEX-001 modules_total modules_python modules_typescript modules_react literature_works modules_cited modules_uncited citations_total -->
The register holds <!-- v:CLAIM-LIB-INDEX-001.modules_total -->**99** modules —
<!-- v:CLAIM-LIB-INDEX-001.modules_python -->**87** Python,
<!-- v:CLAIM-LIB-INDEX-001.modules_typescript -->**7** TypeScript,
<!-- v:CLAIM-LIB-INDEX-001.modules_react -->**5** React — and a hash-locked
bibliography of <!-- v:CLAIM-LIB-INDEX-001.literature_works -->**116** works;
<!-- v:CLAIM-LIB-INDEX-001.modules_cited -->**90** modules cite the standard,
RFC or paper they implement through
<!-- v:CLAIM-LIB-INDEX-001.citations_total -->**127** resolved references, and
the remaining <!-- v:CLAIM-LIB-INDEX-001.modules_uncited -->**9** are generic
utilities honestly documented as having no canonical authoritative work.
These counts are themselves a claim (`CLAIM-LIB-INDEX-001`): add a module or a
work without regenerating the evidence and this paragraph fails the build.

### What is in the library

| Subject area | Modules |
|--------------|---------|
| **Security & cryptography** | [`sha256`](claimlib/docs/sha256.md) · [`hmac_sha256`](claimlib/docs/hmac_sha256.md) · [`hotp`](claimlib/docs/hotp.md) · [`totp`](claimlib/docs/totp.md) · [`pbkdf2`](claimlib/docs/pbkdf2.md) · [`hkdf`](claimlib/docs/hkdf.md) · [`chacha20`](claimlib/docs/chacha20.md) · [`jwt_hs256`](claimlib/docs/jwt_hs256.md) · [`pem`](claimlib/docs/pem.md) · [`spki_pin`](claimlib/docs/spki_pin.md) · [`lamport`](claimlib/docs/lamport.md) · [`cvss`](claimlib/docs/cvss.md) · [`hashchain`](claimlib/docs/hashchain.md) · [`merkle`](claimlib/docs/merkle.md) · [`rbac`](claimlib/docs/rbac.md) |
| **AI assurance & uncertainty** | [`conformal_split`](claimlib/docs/conformal_split.md) · [`conformal_risk`](claimlib/docs/conformal_risk.md) · [`selective_risk`](claimlib/docs/selective_risk.md) · [`shannon_entropy`](claimlib/docs/shannon_entropy.md) · [`gsn_case`](claimlib/docs/gsn_case.md) · [`tool_guard`](claimlib/docs/tool_guard.md) · [`owasp_llm10`](claimlib/docs/owasp_llm10.md) · [`slsa_levels`](claimlib/docs/slsa_levels.md) · [`zta_tenets`](claimlib/docs/zta_tenets.md) · [`prov_dm`](claimlib/docs/prov_dm.md) · [`runtime_rules`](claimlib/docs/runtime_rules.md) |
| **AI governance (enterprise)** | [`eu_ai_act`](claimlib/docs/eu_ai_act.md) · [`nist_ai_rmf`](claimlib/docs/nist_ai_rmf.md) · [`iso_42001`](claimlib/docs/iso_42001.md) · [`dora_eu`](claimlib/docs/dora_eu.md) · [`fairness_metrics`](claimlib/docs/fairness_metrics.md) · [`calibration_ece`](claimlib/docs/calibration_ece.md) · [`dp_composition`](claimlib/docs/dp_composition.md) · [`model_card`](claimlib/docs/model_card.md) |
| **Governance & compliance** | [`nist_csf`](claimlib/docs/nist_csf.md) · [`nis2`](claimlib/docs/nis2.md) · [`soc2`](claimlib/docs/soc2.md) · [`iso27001`](claimlib/docs/iso27001.md) · [`pci_dss`](claimlib/docs/pci_dss.md) · [`cis_controls`](claimlib/docs/cis_controls.md) · [`gdpr`](claimlib/docs/gdpr.md) |
| **Audit & forensic analytics** | [`benford`](claimlib/docs/benford.md) · [`double_entry`](claimlib/docs/double_entry.md) · [`audit_sampling`](claimlib/docs/audit_sampling.md) · [`mus_sampling`](claimlib/docs/mus_sampling.md) |
| **Finance & payments** | [`iban`](claimlib/docs/iban.md) · [`money`](claimlib/docs/money.md) · [`mod11`](claimlib/docs/mod11.md) · [`luhn`](claimlib/docs/luhn.md) · [`kid`](claimlib/docs/kid.md) · [`annuity`](claimlib/docs/annuity.md) |
| **Telecom & networking** | [`cidr`](claimlib/docs/cidr.md) · [`ipv6`](claimlib/docs/ipv6.md) · [`macaddr`](claimlib/docs/macaddr.md) · [`aspath`](claimlib/docs/aspath.md) · [`ipchecksum`](claimlib/docs/ipchecksum.md) · [`vlan`](claimlib/docs/vlan.md) · [`e164`](claimlib/docs/e164.md) · [`imei`](claimlib/docs/imei.md) · [`hamming74`](claimlib/docs/hamming74.md) · [`dns_name`](claimlib/docs/dns_name.md) · [`punycode`](claimlib/docs/punycode.md) · [`erlang_b`](claimlib/docs/erlang_b.md) |
| **Industrial & telemetry** | [`modbus_crc`](claimlib/docs/modbus_crc.md) · [`nmea`](claimlib/docs/nmea.md) · [`oee`](claimlib/docs/oee.md) · [`pt100`](claimlib/docs/pt100.md) |
| **Data: encoding & serialization** | [`base32`](claimlib/docs/base32.md) · [`base58`](claimlib/docs/base58.md) · [`crc32`](claimlib/docs/crc32.md) · [`csv_rfc4180`](claimlib/docs/csv_rfc4180.md) · [`jsonpointer`](claimlib/docs/jsonpointer.md) · [`rle`](claimlib/docs/rle.md) · [`varint`](claimlib/docs/varint.md) · [`uuid_tools`](claimlib/docs/uuid_tools.md) |
| **Reliability & SRE** | [`tokenbucket`](claimlib/docs/tokenbucket.md) · [`retry`](claimlib/docs/retry.md) · [`errorbudget`](claimlib/docs/errorbudget.md) · [`percentile`](claimlib/docs/percentile.md) · [`apdex`](claimlib/docs/apdex.md) · [`slo_burnrate`](claimlib/docs/slo_burnrate.md) · [`ewma`](claimlib/docs/ewma.md) |
| **Algorithms & data structures** | [`levenshtein`](claimlib/docs/levenshtein.md) · [`topo_sort`](claimlib/docs/topo_sort.md) · [`lru`](claimlib/docs/lru.md) · [`semver`](claimlib/docs/semver.md) · [`bloom_filter`](claimlib/docs/bloom_filter.md) |
| **TypeScript utilities** | [`result`](claimlib/docs/result.md) · [`deepEqual`](claimlib/docs/deepEqual.md) · [`cx`](claimlib/docs/cx.md) · [`groupBy`](claimlib/docs/groupBy.md) · [`chunk`](claimlib/docs/chunk.md) · [`parseQuery`](claimlib/docs/parseQuery.md) · [`formatDuration`](claimlib/docs/formatDuration.md) |
| **React hooks** | [`useAsync`](claimlib/docs/useAsync.md) · [`useDebouncedValue`](claimlib/docs/useDebouncedValue.md) · [`usePagination`](claimlib/docs/usePagination.md) · [`useStepper`](claimlib/docs/useStepper.md) · [`useUndoRedo`](claimlib/docs/useUndoRedo.md) |

Every module's page states its claim, caveat, evidence and — where one exists —
the hash-locked works it implements. The full module table with claim ids and
evidence levels is in [`claimlib/README.md`](claimlib/README.md); the
bibliography, with every work's `summary_sha256` and which modules cite it, is
in [`claimlib/literature/BIBLIOGRAPHY.md`](claimlib/literature/BIBLIOGRAPHY.md).

### Vendor a module — inherit a checked primitive

```bash
# Byte-exact code + a generated binding test (editing the vendored bytes
# then fails YOUR test suite — forking becomes an explicit act):
python3 integrations/library/use_code.py --bundle claimlib/bundles/<id> --target .

# Or import it as a hash-locked claim into your own register:
python3 integrations/library/import_bundle.py --bundle claimlib/bundles/<id> --target .
```

### Turn a claim into a program — the scaffolder

The register is generative, not just archival. `scaffold.py` takes a claim
shape (validator, checksum, codec, calculator) and emits a ready-to-fill
module + evidence + test that follow the contract — and it **never fabricates
numbers**: the generated evidence refuses to run until the TODO reference
battery is replaced with independently-known values.

```bash
python claimlib/scaffold.py iban_check --template validator --domain "Finance / Payments"
# → modules/iban_check/{iban_check.py, evidence.py} + tests/test_iban_check.py
python claimlib/build.py && python -m vericlaim --root claimlib   # the gate refuses drift
```

### The literature layer — citations that cannot rot

Each work in [`claimlib/literature/`](claimlib/literature/) is a bibliographic
record whose summary is hash-locked (`summary_sha256`, re-verified by tests);
a module's `references` field must resolve to a real entry or the build fails.
The same integrity rule the gate applies to numbers, applied to citations: a
reference can be proven intact, and can never be fabricated or silently
swapped.

---

## Explore this repo (it dogfoods itself)

```bash
git clone https://github.com/darklordVirtual/vericlaim && cd vericlaim
python3 -m vericlaim           # the gate, run on vericlaim's own claims
python3 examples/rle/bench.py  # regenerate the example's evidence artifact
pytest -q                     # tests, including the drift-detection guarantee
```

## Layout

```
vericlaim/            the zero-dependency gate (register parser, checks, CLI)
claims/               register.yaml (source of truth) · baseline.json · manifest.md
claimlib/             the knowledge register: claim-bound vendorable modules + hash-locked literature + scaffolder
docs/                 manifesto · getting-started · register spec · evidence levels
examples/             four tiny worked examples (capability, correctness, benchmark, proof)
domains/              five larger applied modules (eval-harness, evidence-graph, multi-tenant, ontologies, cost-routing)
seed/                 regenerable stress-test corpora (gate at scale · 16 enterprise domains)
tools/                evidence scripts for the repo's own claims (version, self-improvement, claimlib index)
tests/                tests for the gate, the examples, and the domain modules
.claude/skills/       a Claude skill that enforces the discipline while you work
integrations/         optional add-ons (not part of the zero-dep core)
.github/workflows/    claim-gate.yml — the gate in CI
vericlaim.toml        gate configuration
```

## Claude skill

This repo ships a Claude skill at
[`.claude/skills/claim-oriented-programming/`](.claude/skills/claim-oriented-programming/SKILL.md).
When Claude works in a project that uses vericlaim, the skill makes it follow the
discipline automatically: produce evidence first, register every number as an
artifact-backed claim, bind docs with anchors, run the gate, and never state a
figure it cannot source.

## Beyond the gate: the claim ecosystem

The zero-dependency gate above is the whole product — it needs no network and
stands alone. Three **optional, additive** layers build on it; none changes
what the gate proves, and each has its own README.

1. **The Cloudflare truth layer** — [`integrations/cloudflare-ai/`](integrations/cloudflare-ai/).
   Mirrors your register to the edge: semantic **search** over claims, a
   tamper-evident **ledger** (`/ledger/verify` names where a chain breaks), a
   content-addressed evidence **vault**, a retrieval-grounded **oracle**
   designed to answer from registered claims and refuse unsupported questions
   (grounding is enforced by retrieval + a citation check, not a proof that
   every sentence is claim-bound — see the add-on README), and a public
   `/passport` + MCP server (`search_claims`, `ask_claims`, `verify_claim`).

2. **The research RAG** — a literature corpus that *refuses to guess*. Every
   work enters only through a registrar guard or an explicit hash-locked
   snapshot; the oracle refuses when no cataloged excerpt supports an answer.
   <!-- claim:CLAIM-LIB-RAG-001 canon_total canon_verified canon_dropped -->
   It holds <!-- v:CLAIM-LIB-RAG-001.canon_total -->**180** works across 15
   collections, of which <!-- v:CLAIM-LIB-RAG-001.canon_verified -->**171** are
   verified into the hash-locked catalog and
   <!-- v:CLAIM-LIB-RAG-001.canon_dropped -->**9** are documented drops —
   coverage is checked fail-closed, so a gap can be honest but never silent.
   <!-- claim:CLAIM-LIB-RAG-002 catalog_works chunks_total -->
   All <!-- v:CLAIM-LIB-RAG-002.catalog_works -->**180** works are chunked into
   <!-- v:CLAIM-LIB-RAG-002.chunks_total -->**9805** content-addressed chunks
   (ask it via `/research/ask` or MCP `ask_research`). Retrieval is never
   evidence: a hit proves the text was cataloged, not that it is true.

3. **The claims library + governance handbook** — the vendoring tooling behind
   [the knowledge register](#the-knowledge-register-claimlib): reusable,
   pre-verified claims (machine-checked theorems, runtime controls, the
   claimlib modules) that other projects vendor via `import_bundle` /
   `use_code` with the evidence level and caveat intact, plus a
   citation-grounded governance reference at
   [`docs/governance/`](docs/governance/) (English + Norwegian).

## Citation

Claim-Oriented Programming and vericlaim are by **Stian Skogbrott**. Please cite
it — see [`CITATION.cff`](CITATION.cff) (GitHub renders a "Cite this repository"
button from it):

> Skogbrott, S. (2026). *vericlaim: A Claim-Oriented Programming gate* (v0.4.0).
> https://github.com/darklordVirtual/vericlaim

<sub>The version above is held equal to `vericlaim/__init__.__version__`
(single source of truth) by `tests/test_version_consistency.py` and recorded as
`CLAIM-META-001` — vericlaim refuses to let its own version drift.</sub>

## License

Apache-2.0. See [LICENSE](LICENSE). Author: Stian Skogbrott.
