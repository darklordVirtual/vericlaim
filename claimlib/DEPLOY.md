# claimlib registry — Cloudflare deployment

The whole `claimlib` claim registry is served as a small, **dependency-free**
Cloudflare Worker: no D1 / Vectorize / R2 bindings, just the baked-in claim data
(id, title, subject area, language, evidence level, bound metric value, bundle
id, statement, caveat). It is generated straight from the register, so what it
serves is exactly what the gate verified.

## Live

- **https://vericlaim-claimlib.razorsharp.workers.dev**

| Route | Returns |
|-------|---------|
| `GET /` | HTML index of every claim, grouped by subject area |
| `GET /claims` | JSON array of all claims |
| `GET /claims/<claim-id>` | one claim (by claim id or module name) |
| `GET /health` | `{ "ok": true, "claims": N }` |

## Regenerate + redeploy

The Worker is generated from `MODULES.py`, `bundles/INDEX.json`, and each
module's evidence artifact, so regenerate it after any `claimlib/build.py` run:

```bash
python claimlib/build.py                 # rebuild register + bundles
python claimlib/registry_worker.py       # -> registry_worker.js + registry.json
```

Then upload with the Cloudflare Workers API (module syntax, no wrangler needed):

```bash
curl -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/workers/scripts/vericlaim-claimlib" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -F 'metadata={"main_module":"worker.js","compatibility_date":"2025-06-01"};type=application/json' \
  -F 'worker.js=@claimlib/registry_worker.js;type=application/javascript+module'
```

Enable the `workers.dev` route once:

```bash
curl -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/workers/scripts/vericlaim-claimlib/subdomain" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" --data '{"enabled":true}'
```

## Note

This read-only registry Worker is distinct from the optional
`integrations/cloudflare-ai` Worker (`vericlaim-claims`), which adds AI embedding
search + MCP and requires Vectorize / D1 / R2 provisioning via its `setup.sh`.
