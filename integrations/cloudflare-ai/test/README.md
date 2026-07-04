# Live test — reproduce the whole add-on end to end

`live_test.py` points at *your* deployed Worker and checks every capability:
the REST layer, the grounded oracle (answer **and** refusal), the tamper-evident
ledger, the evidence vault, and the MCP protocol with all four tools.

It is **self-configuring** (reads a real claim id from `/summary`) and
**read-only** — safe to run against a live deployment. Zero dependencies.

```bash
python3 integrations/cloudflare-ai/test/live_test.py \
  --url https://vericlaim-claims.<your-subdomain>.workers.dev
```

Expected: `15/15 checks passed` (12/15 if you deployed without
`--var ENABLE_MCP:true`, since the three MCP tool checks are skipped). Exit code
0 means all passed.

## Prove the ledger is tamper-evident (manual, optional)

The live test is non-destructive, so it does not tamper with your ledger. To see
the tamper-detection for yourself, change one stored byte and watch the chain
break — then restore it:

```bash
# 1. it is intact
curl -s $URL/ledger/verify            # {"ok":true,...}

# 2. silently alter a past row
npx wrangler d1 execute vericlaim-ledger --remote \
  --command "UPDATE claim_events SET statement='tampered' WHERE seq=1;"
curl -s $URL/ledger/verify            # {"ok":false,"brokenAt":1}

# 3. only a byte-exact restore repairs the chain — re-push the register:
python3 integrations/cloudflare-ai/export_claims.py --push $URL --token $INDEX_TOKEN
#    (if the content is unchanged the ledger will not re-append; to fully reset,
#     recreate the D1 table with schema.sql and re-push.)
```

A single changed byte anywhere in a past entry breaks every hash after it — that
is the guarantee.
