# vericlaim

**A Claim-Oriented Programming gate.** Verify that every claim your project
makes about itself is backed by a committed artifact — and that your docs never
drift from the truth. *Design by Contract for the whole repository, enforced in
CI, built for the age of AI-authored code.*

Zero runtime dependencies · Python 3.11+ · one command.

---

## The idea in 30 seconds

AI writes code and prose fast, and forgets what was true yesterday. Numbers in
the README stop matching the paper; a corrected claim reappears in its old form;
a citation is invented. Testing catches misbehaving code. Nothing conventional
catches a **project that misdescribes itself**.

Claim-Oriented Programming closes that gap with one rule, mechanically enforced:

> **A claim is a contract between what the project says and the evidence on
> disk — checked on every commit.**

If a doc says "8.0584× compression," there is a committed artifact measuring it,
and a machine verifies that the doc, the register, and the artifact all agree.
Change one without the others and the build goes red.

Where Bertrand Meyer's **Design by Contract** put pre/post-conditions on
*functions* and checked them at *run time*, vericlaim puts contracts on the
*project's claims about itself* and checks them in *CI*. See
[`docs/manifesto.md`](docs/manifesto.md).

## What the gate checks

- **No claim without an artifact** — every cited file must exist.
- **Register integrity** — required fields; valid evidence level; no duplicate ids.
- **Manifest hashes** — committed result artifacts match their SHA-256 (a
  silently-edited number is caught).
- **Doc binding** — `<!-- claim:ID metric -->` anchors tie prose numbers to the
  register; drift fails the build.
- **Evidence-level consistency** — a doc can't over-state a claim's level.
- **Stale-string denylist** — a corrected string can never quietly return.

Adoption is **incremental**: existing violations are grandfathered in a baseline;
new ones fail immediately.

## Quickstart

```bash
git clone https://github.com/darklordVirtual/vericlaim && cd vericlaim
python -m vericlaim          # run the gate on this repo (it dogfoods itself)
python examples/rle/bench.py # regenerate the example's evidence artifact
pytest -q                    # tests, including the drift-detection guarantee
```

To adopt it in your own project, see
[`docs/getting-started.md`](docs/getting-started.md) (about 15 minutes).

## Worked example (a different domain on purpose)

The method was distilled from an AI-governance codebase, but it is
domain-independent. The [`examples/rle/`](examples/rle/) directory applies it to
lossless compression:

<!-- claim:CLAIM-EX-001 overall_ratio -->
- a run-length encoder that achieves **8.0584×** overall compression on a fixed
  corpus — registered as `CLAIM-EX-001`, backed by
  `examples/rle/artifacts/rle_bench.json`, and bound to
  [`examples/rle/docs/results.md`](examples/rle/docs/results.md).

Edit that `8.0584` in either the doc or the register without the other and
`python -m vericlaim` fails — that is the whole point.

## Layout

```
vericlaim/            the zero-dependency gate (register parser, checks, CLI)
claims/               register.yaml (source of truth), baseline.json, manifest.md
docs/                 manifesto, getting-started, register spec, evidence levels
examples/rle/         a worked example in an unrelated domain
tests/                tests for the gate and the example
.github/workflows/    claim-gate.yml — the gate in CI
vericlaim.toml        gate configuration
```

## License

Apache-2.0. See [LICENSE](LICENSE).
