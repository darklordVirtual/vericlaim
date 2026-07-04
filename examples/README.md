# Examples

Claim-Oriented Programming applies to any kind of claim, not just benchmark
numbers. Each example below is deliberately tiny and shows a **different claim
shape**, so you can find the one closest to what you need to state.

| Example | Domain | Claim shape | Claim |
|---------|--------|-------------|-------|
| [`greetings/`](greetings/) | i18n greetings | **capability count** | supports 6 languages (`CLAIM-GREET-001`) |
| [`tipcalc/`](tipcalc/) | tip calculator | **correctness** | all 12 reference cases pass (`CLAIM-TIP-001`) |
| [`rle/`](rle/) | lossless compression | **benchmark ratio** | 8.0584× overall (`CLAIM-EX-001`), lossless (`CLAIM-EX-002`) |

Each example follows the same loop:

1. **Code** — the small library (`src/`).
2. **Evidence** — a deterministic script writes an artifact (`artifacts/*.json`).
   Never hand-typed.
3. **Claim** — registered in [`../claims/register.yaml`](../claims/register.yaml)
   and hashed in [`../claims/manifest.md`](../claims/manifest.md).
4. **Doc** — `docs/results.md` states the number behind a `<!-- claim:ID ... -->`
   anchor bound to the register.
5. **Gate** — `python3 -m vericlaim` verifies all of the above agree.

Pick any one, edit the number in its doc (or its code, then re-run the
evidence), and run `python3 -m vericlaim` from the repo root — the gate points at
the exact drift. That is the whole idea, in three domains.
