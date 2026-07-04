#!/usr/bin/env bash
# One-command setup for the vericlaim Cloudflare add-on.
#
# Creates the three data resources on YOUR Cloudflare account, applies the
# ledger schema, and writes your D1 id into wrangler.toml. Idempotent: safe to
# re-run (existing resources are left alone). After it finishes, set the write
# secret and deploy, then push your register — the exact commands are printed.
#
# Prereqs: Node.js + npm, and a Cloudflare API token in $CLOUDFLARE_API_TOKEN
# (or run `npx wrangler login` first).
set -euo pipefail
cd "$(dirname "$0")"

VECTORIZE="vericlaim-claims"
D1="vericlaim-ledger"
R2="vericlaim-evidence"

echo "==> installing dependencies"
npm install --silent

echo "==> Vectorize index ($VECTORIZE, 768-dim cosine)"
npx wrangler vectorize create "$VECTORIZE" --dimensions=768 --metric=cosine 2>/dev/null \
  || echo "    (already exists)"

echo "==> D1 ledger ($D1)"
CREATE_OUT="$(npx wrangler d1 create "$D1" 2>/dev/null || true)"
D1_ID="$(printf '%s' "$CREATE_OUT" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1 || true)"
if [ -z "$D1_ID" ]; then
  # already existed — look it up
  D1_ID="$(npx wrangler d1 list --json 2>/dev/null \
    | python3 -c "import json,sys; print(next((d['uuid'] for d in json.load(sys.stdin) if d['name']=='$D1'),''))")"
fi
if [ -z "$D1_ID" ]; then echo "!! could not determine D1 id"; exit 1; fi
echo "    database_id = $D1_ID"

echo "==> writing D1 id into wrangler.toml"
python3 - "$D1_ID" <<'PY'
import re, sys
p = "wrangler.toml"; t = open(p).read(); did = sys.argv[1]
t = re.sub(r'(database_name = "vericlaim-ledger"\ndatabase_id = ")[^"]*(")',
           lambda m: m.group(1) + did + m.group(2), t)
open(p, "w").write(t)
print("    updated wrangler.toml")
PY

echo "==> applying ledger schema (remote D1)"
npx wrangler d1 execute "$D1" --remote --file schema.sql >/dev/null
echo "    schema applied"

echo "==> R2 evidence vault ($R2)"
npx wrangler r2 bucket create "$R2" 2>/dev/null || echo "    (already exists)"

cat <<'NEXT'

✅ Resources ready. Finish in 3 steps:

  1. Set the write token (any strong secret; you reuse it when pushing):
       npx wrangler secret put INDEX_TOKEN

  2. Deploy (add --var ENABLE_MCP:true if you want the MCP endpoint):
       npx wrangler deploy --var ENABLE_MCP:true

  3. Push your register through the pipeline (run from the repo root):
       python3 integrations/cloudflare-ai/export_claims.py \
         --push https://vericlaim-claims.<your-subdomain>.workers.dev \
         --token "<the INDEX_TOKEN you set>"

Then verify everything live:
       python3 integrations/cloudflare-ai/test/live_test.py \
         --url https://vericlaim-claims.<your-subdomain>.workers.dev
NEXT
