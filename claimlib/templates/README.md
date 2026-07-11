# claimlib module templates

Domain-flavored scaffolds for new **claim-bound** modules. Each template is a set
of three files with `{{PLACEHOLDER}}` tokens that `claimlib/scaffold.py` fills in:

```
python claimlib/scaffold.py <name> --template <kind> --domain "<Area>" [--claim-id ID]
```

| Template | Shape it scaffolds | Bound field |
|----------|--------------------|-------------|
| `validator`  | classify inputs valid/invalid against a known rule | `correct` |
| `checksum`   | reproduce published check vectors + independent oracle | `reference_vectors_matched` |
| `codec`      | encode/decode round-trip + reference vectors | `roundtrip_lossless` |
| `calculator` | reproduce a published worked example / formula | `correct` |

Every scaffold is generated so the gate stays honest:

- the `evidence.py` reference battery starts as a single `TODO` row whose expected
  value is `NotImplementedError` — the module **cannot go green until you supply a
  real, independently-known reference**, so no number is ever fabricated;
- the scaffolder never edits `MODULES.py` or the register — it prints the
  `MODULES.py` entry for you to paste after the evidence is real.

Workflow: scaffold → implement `<name>.py` → replace the TODO battery in
`evidence.py` with genuine reference values → `python claimlib/build.py` →
`python -m vericlaim --root claimlib`. The gate refuses anything that drifts.

Placeholders: `{{NAME}}` module name, `{{CLAIM_ID}}`, `{{DOMAIN}}` subject area,
`{{TITLE}}`, `{{CLASS}}` error class name, `{{SCHEMA}}` artifact schema tag.
