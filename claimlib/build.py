# SPDX-License-Identifier: Apache-2.0
"""Build the claimlib workspace: run every module's evidence, aggregate the
claim register + docs, and package one vendorable bundle_v1 per module.

    python claimlib/build.py            # regenerate everything
    python -m vericlaim --root claimlib  # then verify the gate is green

Pipeline per module (see MODULES.py):
  1. run modules/<name>/evidence.py  -> artifacts/<artifact> (+ provenance)
  2. read the artifact's metrics
  3. emit a register claim + a bound doc
  4. build bundles/<bundle_id>/ with code/<file> + artifacts/<artifact>,
     claim.json, provenance.json (via bundlefmt.build_bundle)
Bundles are then vendorable into any project:
  python integrations/library/use_code.py --bundle claimlib/bundles/<id> --target .
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "integrations" / "library"))

sys.path.insert(0, str(HERE / "literature"))

from MODULES import MODULES  # noqa: E402
from bundlefmt import build_bundle  # noqa: E402
from vericlaim.provenance import stamp  # noqa: E402
try:
    from SOURCES import SOURCES  # noqa: E402
    LITERATURE = {s["id"]: s for s in SOURCES}
except ImportError:                                  # literature layer optional
    LITERATURE = {}

# Language dispatch: where each module lives and how its evidence runs.
LANGS = {
    "python": {"subdir": "modules", "evidence": "evidence.py", "runner": [sys.executable]},
    "typescript": {"subdir": "ts", "evidence": "evidence.ts", "runner": ["node"]},
    "react": {"subdir": "react", "evidence": "evidence.ts", "runner": ["node"]},
}


def lang_of(mod: dict) -> dict:
    return LANGS[mod.get("lang", "python")]


def module_dir(mod: dict) -> Path:
    return HERE / lang_of(mod)["subdir"] / mod["name"]


def artifact_rel(mod: dict) -> str:
    return f"{lang_of(mod)['subdir']}/{mod['name']}/artifacts/{mod['artifact']}"


def reproduce_cmd(mod: dict) -> str:
    lg = lang_of(mod)
    runner = "python3" if mod.get("lang", "python") == "python" else "node"
    return f"{runner} claimlib/{lg['subdir']}/{mod['name']}/{lg['evidence']}"


def write_lf(path: Path, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, cwd=REPO_ROOT, check=True)
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


CONFIG = """\
# claimlib gate — a curated standard library of pre-verified, vendorable code
# artifacts. Every module's key property is a claim backed by committed evidence.
# Regenerate: python claimlib/build.py
[vericlaim]
profile             = "adopt"
register            = "claims/register.yaml"
baseline            = "claims/baseline.json"
doc_globs           = ["docs/*.md", "README.md"]
# Bind numbers stated in module source comments too (evidence scripts anchor
# their measured counts). Pure library files carry no anchors and just pass.
code_globs          = ["modules/*/*.py"]
required_fields     = ["id", "statement", "evidence_level", "artifact", "caveat"]
evidence_levels     = ["theoretical", "measured", "benchmarked", "reproduced", "machine_checked", "externally_validated"]
require_provenance  = true
require_git_tracked = false

[vericlaim.stale_strings]
"""

BASELINE = json.dumps({
    "schema": "vericlaim_baseline_v1",
    "description": "claimlib starts green; no grandfathered violations.",
    "known_violations": [],
}, indent=2) + "\n"


def yaml_block(text: str, indent: str) -> str:
    return "\n".join(indent + line for line in text.split("\n"))


def fmt(v) -> str:
    if isinstance(v, bool):
        return str(int(v))
    return str(v)


def run_evidence(mod: dict) -> dict:
    """Run the module's evidence and return the parsed artifact.

    python: evidence.py writes the artifact + provenance itself.
    ts/react: evidence.ts prints the metrics JSON on stdout (node runs .ts
    natively, offline); build.py writes the artifact + stamps provenance so a
    single provenance/gate mechanism covers every language.
    """
    lg = lang_of(mod)
    mdir = module_dir(mod)
    art = mdir / "artifacts" / mod["artifact"]
    ev = mdir / lg["evidence"]
    proc = subprocess.run(lg["runner"] + [str(ev)], capture_output=True,
                          text=True, cwd=REPO_ROOT)
    if proc.returncode != 0:
        raise SystemExit(f"[FAIL] evidence for {mod['name']} exited "
                         f"{proc.returncode}:\n{proc.stdout}{proc.stderr}")
    if mod.get("lang", "python") != "python":
        # node printed the metrics JSON; persist it as the artifact (LF) + stamp.
        obj = json.loads(proc.stdout.strip().splitlines()[-1])
        art.parent.mkdir(parents=True, exist_ok=True)
        write_lf(art, json.dumps(obj, indent=2, sort_keys=True) + "\n")
        stamp(str(art), script=reproduce_cmd(mod), produced_by="claimlib")
    return json.loads(art.read_text(encoding="utf-8"))


def reproduce_argv(mod: dict) -> list:
    """Declarative reproduce: run the evidence with an isolated --output-dir
    (workspace-relative paths; the runner's cwd is the claimlib root). Python
    evidence honours --output-dir via _util.emit; node evidence goes through
    the reproduce_node.py shim so the artifact is CREATED from scratch."""
    lg = lang_of(mod)
    if mod.get("lang", "python") == "python":
        return ["python3", f"{lg['subdir']}/{mod['name']}/{lg['evidence']}",
                "--output-dir", "{output_dir}"]
    return ["python3", "reproduce_node.py", mod["name"],
            "--output-dir", "{output_dir}"]


def register_entry(mod: dict, metrics: dict) -> str:
    cid = mod["claim_id"]
    metric_lines = "\n".join(f"      {k}: {fmt(metrics[k])}"
                             for k in mod["register_metrics"])
    argv_lines = "\n".join(f'      - "{a}"' for a in reproduce_argv(mod))
    return f"""\
  - id: {cid}
    statement: >
{yaml_block(mod['statement'], "      ")}
    evidence_level: {mod['evidence_level']}
    artifact:
      - "{artifact_rel(mod)}"
    metrics:
{metric_lines}
    caveat: >
{yaml_block(mod['caveat'], "      ")}
    reproduce_argv:
{argv_lines}
    reproduce_outputs:
      - "{artifact_rel(mod)}"
"""


def references_section(mod: dict) -> str:
    """Render a ## References block from the module's hash-locked literature."""
    refs = mod.get("references", [])
    if not refs:
        return ""
    lines = ["", "## References", "",
             "The standards this module implements, as hash-locked entries in "
             "[the claimlib bibliography](../literature/BIBLIOGRAPHY.md):", ""]
    for ref in refs:
        lit = LITERATURE.get(ref)
        if lit is None:
            raise SystemExit(f"[FAIL] {mod['name']}: unknown literature reference {ref!r}")
        lines.append(f"- **{lit['identifier']}** — {lit['title']}. "
                     f"[{lit['url']}]({lit['url']})")
    return "\n".join(lines) + "\n"


def doc_for(mod: dict, metrics: dict, bundle_id: str) -> str:
    cid = mod["claim_id"]
    bf = mod["bind_field"]
    val = fmt(metrics[bf])
    art_rel = artifact_rel(mod)
    lang = mod.get("lang", "python")
    files = ", ".join(f"`{f}`" for f in mod["code_files"])
    return f"""\
# {mod['title']}

*Subject area: {mod['area']}. Language: {lang}. Vendorable bundle `{bundle_id[:12]}`.*

{mod['knowledge']}

## Claim

<!-- claim:{cid} {bf} -->
{mod['statement'].strip()} Verified value: <!-- v:{cid}.{bf} -->**{val}**
(`{bf}`), backed by [`{art_rel}`](../{art_rel}).

## Vendor it

Ships {files} into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/{bundle_id} --target .
```
{references_section(mod)}"""


def build_bundle_for(mod: dict, commit: str) -> str:
    mdir = module_dir(mod)
    files: dict[str, bytes] = {}
    for f in mod["code_files"]:
        files[f"code/{f}"] = (mdir / f).read_bytes()
    files[f"artifacts/{mod['artifact']}"] = (mdir / "artifacts" / mod["artifact"]).read_bytes()
    metrics = json.loads((mdir / "artifacts" / mod["artifact"]).read_text(encoding="utf-8"))
    claim = {
        "id": mod["claim_id"],
        "statement": " ".join(mod["statement"].split()),
        "evidence_level": mod["evidence_level"],
        "artifact": [f"artifacts/{mod['artifact']}"],
        "metrics": {k: metrics[k] for k in mod["register_metrics"]},
        "caveat": " ".join(mod["caveat"].split()),
    }
    provenance = {
        "source_repo": "github.com/darklordVirtual/vericlaim",
        "source_commit": commit,
        "source_claim_id": mod["claim_id"],
        "source_evidence_level": mod["evidence_level"],
        "level_mapping": "native (vericlaim register; no cross-taxonomy mapping)",
        "source_gate": "green",
    }
    bid, _ = build_bundle(HERE / "bundles", claim=claim, provenance=provenance,
                          files=files, status="verified")
    return bid


README_HEAD = """\
# claimlib — a standard library of pre-verified, vendorable code artifacts

*Generated by `claimlib/build.py`. Every module here is a small, dependency-free,
genuinely reusable building block — in **Python, TypeScript, or React** — whose
key property is a **claim** backed by a committed evidence artifact and packaged
as a content-addressed `bundle_v1`. Vendor one into your project and you inherit
a **checked** primitive — plus a test that fails the moment you edit the vendored
bytes — instead of another re-implementation to re-audit.*

Evidence runs offline with zero installs: Python via `python`, TypeScript and
React via `node` (v24 runs `.ts`/`.tsx` natively). React artifacts ship a
drop-in hook/component whose framework-agnostic **logic core** carries the claim.

This is Claim-Oriented Programming applied to code reuse: the library is
**distribution, not truth**. Vendoring proves the code is byte-exact to what
produced the evidence and traceable to its source; it does not re-validate the
claim in your context — read each module's caveat.

## Modules

{table}

Each module's page (linked above) states its claim, bound to the register, and
shows the exact vendor command. Bundle ids are in
[`bundles/INDEX.json`](bundles/INDEX.json).

## Vendor a module (program with the claim behind you)

Two ways to consume a bundle, both fail-closed and fully offline:

```bash
# 1) Vendor the byte-exact code + a generated binding test.
#    Editing the vendored code then fails YOUR OWN test suite (explicit fork).
python3 integrations/library/use_code.py \\
    --bundle claimlib/bundles/<bundle_id> --target .

# 2) Import it as a hash-locked claim into your register.
#    Your own offline gate re-verifies the provenance hash forever after.
python3 integrations/library/import_bundle.py \\
    --bundle claimlib/bundles/<bundle_id> --target .
```

## Build / verify

```bash
python3 claimlib/build.py            # run every evidence.py, aggregate register+docs, build bundles
python3 -m vericlaim --root claimlib # the gate: register <-> artifacts <-> docs <-> code comments all agree
python3 -m pytest claimlib/tests/    # per-module correctness tests
```

## Add a module (the contract)

Create `modules/<name>/<name>.py` (a pure, stdlib-only reusable library, no I/O,
no sibling imports — this is what gets vendored) and `modules/<name>/evidence.py`
(a deterministic script that exercises the library over a **fixed reference
battery whose expected values are independently known**, writes
`artifacts/<name>.json` via `_util.emit`, and carries a `# claim:<ID> <field>`
comment anchor). Add unit tests at `tests/test_<name>.py`, append an entry to
`MODULES.py`, and run `build.py`. The gate refuses anything that drifts.
"""


_LANG_LABEL = {"python": "Python", "typescript": "TypeScript", "react": "React"}


def write_readme(index: dict) -> None:
    rows = ["| Module | Lang | Subject area | Claim | Evidence |",
            "|--------|------|--------------|-------|----------|"]
    order = {"python": 0, "typescript": 1, "react": 2}
    for mod in sorted(MODULES, key=lambda m: (order.get(m.get("lang", "python"), 9), m["name"])):
        lang = _LANG_LABEL.get(mod.get("lang", "python"), mod.get("lang", "python"))
        rows.append(f"| [`{mod['name']}`](docs/{mod['name']}.md) | {lang} | {mod['area']} | "
                    f"`{mod['claim_id']}` | {mod['evidence_level']} |")
    write_lf(HERE / "README.md", README_HEAD.format(table="\n".join(rows)))


def main() -> int:
    (HERE / "claims").mkdir(exist_ok=True)
    (HERE / "docs").mkdir(exist_ok=True)
    bundles_dir = HERE / "bundles"
    # Clear stale bundle dirs (content-addressed; rebuilds may change ids).
    if bundles_dir.exists():
        for d in bundles_dir.iterdir():
            if d.is_dir():
                for p in sorted(d.rglob("*"), reverse=True):
                    p.unlink() if p.is_file() else p.rmdir()
                d.rmdir()
    bundles_dir.mkdir(exist_ok=True)

    write_lf(HERE / "vericlaim.toml", CONFIG)
    write_lf(HERE / "claims" / "baseline.json", BASELINE)
    commit = git_commit()

    reg = ["---\n",
           "# claimlib register — GENERATED by claimlib/build.py. Do not hand-edit.\n\n",
           'schema_version: "1"\n\n', "claims:\n\n"]
    index = {}
    for mod in MODULES:
        metrics = run_evidence(mod)
        for k in mod["register_metrics"] + [mod["bind_field"]]:
            if k not in metrics:
                raise SystemExit(f"[FAIL] {mod['name']}: artifact missing metric {k!r}")
        bid = build_bundle_for(mod, commit)
        index[mod["name"]] = bid
        reg.append(register_entry(mod, metrics))
        reg.append("\n")
        write_lf(HERE / "docs" / f"{mod['name']}.md", doc_for(mod, metrics, bid))

    write_lf(HERE / "claims" / "register.yaml", "".join(reg))
    write_lf(bundles_dir / "INDEX.json",
             json.dumps(index, indent=2, sort_keys=True) + "\n")
    write_readme(index)
    print(f"built {len(MODULES)} module(s): "
          + ", ".join(f"{n}={b[:12]}" for n, b in index.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
