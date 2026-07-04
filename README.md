# vericlaim

[![Claim Gate](https://github.com/darklordVirtual/vericlaim/actions/workflows/claim-gate.yml/badge.svg)](https://github.com/darklordVirtual/vericlaim/actions/workflows/claim-gate.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

> **Your docs can never quietly disagree with your evidence again.**

vericlaim checks, on every commit, that every number and capability your project
claims about itself is backed by a committed artifact — and that your README,
docs, and papers all still say the same thing. It is **Design by Contract for the
whole repository**, built for the age of AI-authored code, where prose and
numbers drift silently.

Zero runtime dependencies · Python 3.11+ · one command to adopt.

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

## Quickstart (60 seconds)

```bash
pip install vericlaim        # or copy the zero-dependency vericlaim/ folder in
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

## What the gate checks

| Check | Guarantee |
|-------|-----------|
| **Artifact existence** | Every file a claim cites exists — *no claim without an artifact.* |
| **Path containment** | Artifacts must live inside the repo (no absolute paths, `..`, or symlink escapes); optionally, must be git-tracked. |
| **Provenance** | Every produced artifact records *how it was made* (script, commit, its own SHA-256) — *no anonymous number.* |
| **Register integrity** | Required fields present, valid evidence level, no duplicate ids. |
| **Manifest hashes** | Result artifacts match their SHA-256 — a silently edited number is caught. |
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
docs/                 manifesto · getting-started · register spec · evidence levels
examples/             four tiny worked examples (capability, correctness, benchmark, proof)
tests/                tests for the gate and the example
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

## Optional: Cloudflare AI add-on

The core needs no network and no dependencies. If you *want* a verifiable,
queryable, tamper-evident **truth layer** for your claims on the edge, an
**optional** add-on lives in
[`integrations/cloudflare-ai/`](integrations/cloudflare-ai/). It gives you five
capabilities against your own Cloudflare account:

- **Semantic search** over claims (Workers AI + Vectorize) — *"what has this project proven about X?"*
- **A tamper-evident claim ledger** (D1) — append-only, hash-chained history; change any past entry and `/ledger/verify` names where the chain breaks.
- **A content-addressed evidence vault** (R2) — retrieve and re-hash the exact bytes that backed a claim.
- **An AI oracle that refuses to overclaim** (Workers AI) — answers only from registered claims, cites claim ids, and refuses when none support the answer.
- **A public trust surface** — a shareable `/passport` page and `/badge.svg`, plus an optional **MCP server** (`search_claims`, `ask_claims`, `get_claim_history`, `verify_claim`) for Claude Code and other agents.

It is opt-in and deploys to your own account; search and answers are discovery
aids and do **not** change what the gate proves. See its
[README](integrations/cloudflare-ai/README.md).

## Citation

Claim-Oriented Programming and vericlaim are by **Stian Skogbrott**. Please cite
it — see [`CITATION.cff`](CITATION.cff) (GitHub renders a "Cite this repository"
button from it):

> Skogbrott, S. (2026). *vericlaim: A Claim-Oriented Programming gate* (v0.2.0).
> https://github.com/darklordVirtual/vericlaim

## License

Apache-2.0. See [LICENSE](LICENSE). Author: Stian Skogbrott.
