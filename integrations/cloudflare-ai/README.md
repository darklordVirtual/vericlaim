# vericlaim — Cloudflare AI add-on (optional)

> **Optional. Opt-in. Not part of the zero-dependency core.**
> The `vericlaim` gate needs none of this. Deploy it only if you want a
> **verifiable, queryable, tamper-evident truth layer** for your claims on the edge.

The gate proves internal consistency at *one commit*. This add-on makes a
project's claims **durable, historical, tamper-evident, discoverable, and
conversational** — without ever weakening the honesty discipline.

```
 claims/register.yaml ─export_claims.py─▶ POST /index
     │                                       ├─▶ Workers AI embed ─▶ Vectorize   (search)
     │                                       ├─▶ hash-chained ledger ─▶ D1        (history)
     │                                       └─▶ content-addressed bytes ─▶ R2    (evidence vault)
     ▼
  GET /search   semantic search        GET /history  ledger timeline
  GET /ask      grounded answer +      GET /verify   re-hash evidence + chain
                REFUSES if unsupported GET /ledger/verify  tamper check
  GET /passport public trust page      GET /badge.svg      dynamic badge
  POST /mcp     search · ask · history · verify  (optional)
```

## The five capabilities

| Capability | Cloudflare | What it gives you |
|---|---|---|
| **Semantic search** | Workers AI + Vectorize | Find claims by meaning: *"what has this project proven about X?"* |
| **Claim ledger** | **D1** | Append-only, **hash-chained** history of every claim. Alter any past row and `GET /ledger/verify` reports exactly where the chain breaks. |
| **Evidence vault** | **R2** | Artifacts stored **content-addressed** (`sha256/<hash>`). Retrieve and re-hash the exact bytes that backed a claim — provably unchanged. |
| **Oracle that refuses to overclaim** | Workers AI (rerank + gen) | Answers **only** from registered claims, cites claim ids, carries caveats, and **refuses** when no claim supports an answer. |
| **Public trust surface** | Worker HTML/SVG | A shareable `/passport` page and a `/badge.svg` rendered live from the ledger. |

The oracle refusing to invent a claim is the point: a vericlaim oracle that
hallucinated would defeat the whole tool. Citations are the ids the answer
*actually* cites — never over-attributed.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | Health + capabilities + live ledger status |
| `POST /index` | (bearer auth) embed→Vectorize, append the ledger, vault the evidence bytes |
| `GET /search?q=&topK=` | Semantic search |
| `GET /ask?q=` | Grounded answer (`{answer, refused, citations, claims}`) |
| `GET /history?claim=ID` | The ledger timeline for a claim |
| `GET /verify?claim=ID` | Re-hash the claim's evidence in R2 + confirm chain integrity |
| `GET /ledger/verify` | Re-walk the whole hash chain (tamper check) |
| `GET /passport` | Public HTML trust page |
| `GET /badge.svg` | Dynamic SVG badge |
| `POST /mcp` | MCP (Streamable HTTP), optional — tools below |

## MCP tools (when `ENABLE_MCP=true`)

`search_claims` · `ask_claims` (grounded, refuses) · `get_claim_history` ·
`verify_claim`. Together they make the server a universal **"project truth" API**
for any agent.

## Setup — reproduce it in ~5 minutes

You need Node.js + npm and a Cloudflare account (a token in
`$CLOUDFLARE_API_TOKEN`, or run `npx wrangler login`). One script creates the
three data resources on **your** account, applies the ledger schema, and writes
your D1 id into `wrangler.toml`:

```bash
cd integrations/cloudflare-ai
./setup.sh                 # creates Vectorize + D1 + R2, applies schema (idempotent)
```

Then the three steps it prints:

```bash
npx wrangler secret put INDEX_TOKEN            # 1. your write token (pick any strong secret)
npx wrangler deploy --var ENABLE_MCP:true      # 2. deploy (drop the --var to keep MCP off)

# 3. push your register through the pipeline (from the repo root):
python3 integrations/cloudflare-ai/export_claims.py \
    --push https://vericlaim-claims.<subdomain>.workers.dev --token "<your INDEX_TOKEN>"
```

Verify the whole thing live (read-only, self-configuring):

```bash
python3 integrations/cloudflare-ai/test/live_test.py \
    --url https://vericlaim-claims.<subdomain>.workers.dev      # expect 15/15 checks passed
```

<details><summary>Manual setup (what <code>setup.sh</code> does)</summary>

```bash
npm install
npm run create-index                                       # Vectorize (768/cosine)
npx wrangler d1 create vericlaim-ledger                     # paste the id into wrangler.toml
npx wrangler d1 execute vericlaim-ledger --remote --file schema.sql
npx wrangler r2 bucket create vericlaim-evidence
```
</details>

The exporter reuses vericlaim's own loader and attaches each claim's artifact
bytes + git commit, so the ledger and vault can only contain what is actually in
the register. Run the gate first in CI and only push when it is green.

## Connect Claude Code

```bash
# enable MCP (off by default): set ENABLE_MCP="true" in wrangler.toml (or deploy --var), redeploy
claude mcp add --transport http --scope user \
  vericlaim-claims https://vericlaim-claims.<subdomain>.workers.dev/mcp
claude mcp get vericlaim-claims        # ✔ Connected
```

## What it proves — and what it does not

- **Proves:** the hash chain detects any **partial** edit to ledger history (a
  changed byte breaks the chain at that row); the vaulted evidence is retrievable
  and re-hashable; the oracle either grounds an answer in real claim ids or
  refuses. Grounding is **answer-level** — at least one valid cited id marks the
  answer grounded; it does not verify each individual sentence entails the claim
  beside it. The hard guarantee is the refusal: no valid citation → a constant
  refusal string, never the model's ungrounded text.
- **Does not:** change what the gate proves; and it does **not** prove history was
  never rewritten. The chain is unkeyed, so an actor who can write the whole D1
  table can rewrite it and recompute every hash — `/ledger/verify` would still
  pass. Internal consistency ≠ rewrite-proof. To close that gap: external
  witnesses re-walk `/ledger/export` and check the chain still **extends** a
  previously-seen head (`/ledger/head`), and/or set `LEDGER_HMAC_KEY` so
  `/ledger/head` returns an operator signature (`head_hmac_sha256`) no D1-only
  attacker can forge. Search and answers are **discovery aids**; a claim is
  trustworthy because the gate verified it — not because it was found here.

## Security

- `POST /index` (and the other writes) is bearer-token protected (`INDEX_TOKEN`)
  and fails closed.
- **`READ_TOKEN` (optional):** the generative endpoints `/ask` and
  `/research/ask` drive Workers AI on every call, so an anonymous caller can run
  up unbounded cost. Set `READ_TOKEN` to require a bearer token on those two
  endpoints (`INDEX_TOKEN` also satisfies it). Unset = they stay public. The
  cheap reads (`/search`, `/passport`, `/badge.svg`) stay open either way; add a
  Cloudflare rate-limit / WAF rule for hard limits.
- **`LEDGER_HMAC_KEY` (optional):** an operator secret (not stored in D1) used to
  sign the ledger head — see "What it proves" above.
- **Single-writer:** `/index` assumes one trusted, serial caller (the CI pusher).
  Do not fan it out across concurrent callers; a true multi-writer setup needs a
  single-writer serializer (Durable Object) in front of D1.
- The oracle treats the question as **untrusted** (ignores injected instructions)
  and returns a constant refusal — never the model's ungrounded text — when no
  claim supports an answer.

For non-public projects put the Worker behind
[Cloudflare Access](https://developers.cloudflare.com/agents/model-context-protocol/protocol/authorization/).
Committed default is `ENABLE_MCP=false`.
