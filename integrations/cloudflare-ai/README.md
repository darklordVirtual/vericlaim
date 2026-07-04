# vericlaim — Cloudflare AI add-on (optional)

> **Optional. Opt-in. Not part of the zero-dependency core.**
> The `vericlaim` gate needs none of this. Deploy it only if you want
> **AI semantic search** — and optionally an **MCP server** — over your
> registered claims.

It turns your claim register into a searchable vector index on Cloudflare's
edge, so you (or an AI agent) can ask *"what has this project actually proven
about X?"* and get back registered, **gate-verified** claims.

```
 claims/register.yaml ──export_claims.py──▶ POST /index
                                              │  embed each claim (Workers AI,
                                              │  @cf/baai/bge-base-en-v1.5, 768-dim)
                                              ▼
                                          Vectorize  ◀── GET /search?q=…   (REST)
                                          (cosine)   ◀── POST /mcp  search_claims (MCP, optional)
```

## What it is — and what it is not

- **Is:** a discovery aid. Semantic search + an optional MCP tool over the
  claims your project has registered.
- **Is not:** a change to what vericlaim proves. A claim is trustworthy because
  the **gate** verified its artifact, provenance and doc-binding — *never*
  because it surfaced in a search. The MCP tool description says exactly this to
  the model that calls it.

## Pieces

| File | Role |
|------|------|
| `src/lib.ts` | Embedding (Workers AI) + index/search over Vectorize |
| `src/index.ts` | Worker: `GET /`, `POST /index`, `GET /search`, `POST /mcp` |
| `src/mcp.ts` | Optional MCP server exposing one tool, `search_claims` |
| `export_claims.py` | Zero-dep exporter — reuses vericlaim's own loader |
| `wrangler.toml` | Bindings: Workers AI, Vectorize, Durable Object (for MCP) |

## Setup (5 steps)

```bash
cd integrations/cloudflare-ai
npm install

# 1. create the vector index (768 dims, cosine — matches the embedding model)
npm run create-index

# 2. set the write token used by POST /index
npx wrangler secret put INDEX_TOKEN

# 3. deploy the Worker
npm run deploy

# 4. push your register into the index (run from the repo root)
python3 integrations/cloudflare-ai/export_claims.py \
    --push https://vericlaim-claims.<your-subdomain>.workers.dev \
    --token "$INDEX_TOKEN"

# 5. search
curl "https://vericlaim-claims.<your-subdomain>.workers.dev/search?q=compression%20ratio"
```

Re-run step 4 whenever the register changes (a CI step, or the workflow below).

## Optional: enable MCP

MCP is **off by default**. To expose the `search_claims` tool at `POST /mcp`,
set `ENABLE_MCP = "true"` in `wrangler.toml` and redeploy. Then point an MCP
client (Claude, an IDE, an agent) at
`https://vericlaim-claims.<your-subdomain>.workers.dev/mcp` (Streamable HTTP).
For anything non-public, put it behind
[Cloudflare Access / OAuth](https://developers.cloudflare.com/agents/model-context-protocol/protocol/authorization/)
before enabling it.

## Cost & keys

Embeddings and search run on **Workers AI + Vectorize** — no third-party API
keys. `@cf/baai/bge-base-en-v1.5` is priced per input token; a claim register is
tiny, so indexing and search cost effectively nothing at this scale. See
[Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/).

## Keeping the index honest

The exporter reads claims through vericlaim's own loader, so the index can only
contain claims that are actually in the register. Run the **gate** first in CI
(`python -m vericlaim`) and only push the index when it is green — then search
results are, by construction, gate-verified claims.
