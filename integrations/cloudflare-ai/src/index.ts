// vericlaim Cloudflare AI add-on — Worker entrypoint.
//
// Endpoints:
//   GET  /                health + config
//   POST /index           (auth) rebuild the vector index from a claims payload
//   GET  /search?q=&topK= semantic search over the indexed claims
//   POST /mcp             MCP (Streamable HTTP) — only when ENABLE_MCP=true
//
// OPTIONAL add-on. The zero-dependency vericlaim core does not depend on any of
// this; deploy it only if you want AI search / MCP over your claim register.
import { type Claim, type Env, indexClaims, searchClaims } from "./lib";
import { VericlaimMCP } from "./mcp";

export { VericlaimMCP }; // Durable Object export required by wrangler

const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data, null, 2), {
    status, headers: { "content-type": "application/json" },
  });

function authorized(req: Request, env: Env): boolean {
  if (!env.INDEX_TOKEN) return false; // fail closed: no token set => no writes
  return req.headers.get("authorization") === `Bearer ${env.INDEX_TOKEN}`;
}

// serve() defaults to a DO binding named MCP_OBJECT; ours is VERICLAIM_MCP.
const mcpHandler = VericlaimMCP.serve("/mcp", { binding: "VERICLAIM_MCP" });

export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(req.url);

    if (url.pathname === "/mcp") {
      if (env.ENABLE_MCP !== "true") return json({ error: "MCP disabled" }, 404);
      return mcpHandler.fetch(req, env, ctx);
    }

    if (url.pathname === "/" ) {
      return json({
        service: "vericlaim-cloudflare-ai",
        endpoints: ["POST /index", "GET /search?q=", env.ENABLE_MCP === "true" ? "POST /mcp" : null].filter(Boolean),
        mcp_enabled: env.ENABLE_MCP === "true",
        note: "Search is a discovery aid over registered claims. It does not " +
              "change what the vericlaim gate proves.",
      });
    }

    if (url.pathname === "/index" && req.method === "POST") {
      if (!authorized(req, env)) return json({ error: "unauthorized" }, 401);
      let payload: { claims?: Claim[] };
      try {
        payload = await req.json();
      } catch {
        return json({ error: "invalid JSON body" }, 400);
      }
      const claims = Array.isArray(payload.claims) ? payload.claims : [];
      const valid = claims.filter((c) => c && c.id && c.statement && c.evidence_level);
      const indexed = await indexClaims(env, valid);
      return json({ indexed, skipped: claims.length - valid.length });
    }

    if (url.pathname === "/search" && req.method === "GET") {
      const q = url.searchParams.get("q");
      if (!q) return json({ error: "missing query parameter 'q'" }, 400);
      const topK = Math.min(20, Math.max(1, Number(url.searchParams.get("topK")) || 5));
      const hits = await searchClaims(env, q, topK);
      return json({ query: q, hits });
    }

    return json({ error: "not found" }, 404);
  },
};
