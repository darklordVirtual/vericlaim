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

## Setup

```bash
cd integrations/cloudflare-ai
npm install

# create the three data resources
npm run create-index                                   # Vectorize (768/cosine)
npx wrangler d1 create vericlaim-ledger                # D1 ledger  -> paste id into wrangler.toml
npx wrangler d1 execute vericlaim-ledger --remote --file schema.sql
npx wrangler r2 bucket create vericlaim-evidence       # R2 vault

npx wrangler secret put INDEX_TOKEN                    # write token for POST /index
npm run deploy

# push the register through the full pipeline (from the repo root)
python3 integrations/cloudflare-ai/export_claims.py \
    --push https://vericlaim-claims.<subdomain>.workers.dev --token "$INDEX_TOKEN"
```

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

- **Proves:** the ledger is tamper-evident (a single changed byte breaks the
  chain); the vaulted evidence is retrievable and re-hashable; the oracle answers
  only from registered claims or refuses.
- **Does not:** change what the gate proves. Search and answers are **discovery
  aids** over already-verified claims. Evidence level is the project's own honest
  assertion. A claim is trustworthy because the gate verified it — not because it
  was found, answered, or vaulted here.

## Security

`POST /index` is bearer-token protected and fails closed. `/search`, `/ask`,
`/passport`, `/badge.svg` and `/mcp` are public reads over already-public claims.
For non-public projects put the Worker behind
[Cloudflare Access](https://developers.cloudflare.com/agents/model-context-protocol/protocol/authorization/).
Committed default is `ENABLE_MCP=false`.
