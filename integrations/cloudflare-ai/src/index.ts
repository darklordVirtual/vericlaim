// vericlaim Cloudflare AI add-on — Worker entrypoint.
//
// The "legendary MVP": search + a tamper-evident claim ledger (D1) + a
// content-addressed evidence vault (R2) + an AI oracle that refuses to
// overclaim + a public claim passport & badge + MCP. All optional; the
// zero-dependency vericlaim core depends on none of it.
//
// Endpoints:
//   GET  /                 health + config
//   POST /index            (auth) embed+upsert, append the ledger, vault evidence
//   GET  /search?q=&topK=  semantic search over the indexed claims
//   GET  /ask?q=           grounded answer from claims only (refuses otherwise)
//   GET  /history?claim=   the ledger timeline for a claim
//   GET  /verify?claim=    re-hash the claim's evidence in R2 + check the chain
//   GET  /ledger/verify    re-walk the whole hash chain (tamper check)
//   GET  /passport         public HTML trust page
//   GET  /badge.svg        dynamic SVG badge
//   POST /mcp              MCP (Streamable HTTP) — only when ENABLE_MCP=true
import { type Claim, type Env, indexClaims, searchClaims } from "./lib";
import { getEvidence, putEvidence, verifyEvidence } from "./vault";
import { appendClaim, history, summary, verifyChain } from "./ledger";
import {
  type BundleIn, getBundle, indexBundles, librarySummary, pruneSuperseded,
  searchLibrary, verifyBundle as verifyLibraryBundle, verifyLibraryChain,
  versionChain,
} from "./library";
import { ask } from "./oracle";
import {
  type ChunkIn, type WorkIn, askResearch, getWork, ingestLiterature,
  researchSummary, searchResearch,
} from "./research";
import { badgeSVG, passportHTML } from "./passport";
import { VericlaimMCP } from "./mcp";

export { VericlaimMCP };

const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data, null, 2), {
    status, headers: { "content-type": "application/json", "access-control-allow-origin": "*" },
  });

function authorized(req: Request, env: Env): boolean {
  if (!env.INDEX_TOKEN) return false; // fail closed
  return req.headers.get("authorization") === `Bearer ${env.INDEX_TOKEN}`;
}

function b64ToBytes(b64: string): Uint8Array {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

const mcpHandler = VericlaimMCP.serve("/mcp", { binding: "VERICLAIM_MCP" });

export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(req.url);
    const p = url.pathname;

    if (p === "/mcp") {
      if (env.ENABLE_MCP !== "true") return json({ error: "MCP disabled" }, 404);
      return mcpHandler.fetch(req, env, ctx);
    }

    if (p === "/") {
      const chain = await verifyChain(env).catch(() => ({ ok: null, entries: 0 }));
      return json({
        service: "vericlaim-cloudflare-ai",
        capabilities: ["search", "ask", "ledger", "evidence-vault", "passport", "badge",
          "library", env.ENABLE_MCP === "true" ? "mcp" : null].filter(Boolean),
        ledger: chain,
        note: "Search/ask are discovery aids over registered claims. They do not " +
              "change what the vericlaim gate proves. The oracle refuses when no " +
              "claim supports an answer.",
      });
    }

    // --- write: index + ledger + vault --------------------------------------
    if (p === "/index" && req.method === "POST") {
      if (!authorized(req, env)) return json({ error: "unauthorized" }, 401);
      let payload: { claims?: Claim[] };
      try { payload = await req.json(); } catch { return json({ error: "invalid JSON" }, 400); }
      const claims = (payload.claims ?? []).filter((c) => c && c.id && c.statement && c.evidence_level);
      const ts = new Date().toISOString();
      let appended = 0, unchanged = 0, vaulted = 0;
      for (const c of claims) {
        let artifact_sha256: string | null = null;
        if (c.artifact_b64) {
          const bytes = b64ToBytes(c.artifact_b64);
          artifact_sha256 = await putEvidence(env, bytes);
          vaulted++;
        }
        const r = await appendClaim(env, c, { git_commit: c.git_commit, artifact_sha256, ts });
        r === "appended" ? appended++ : unchanged++;
      }
      const indexed = await indexClaims(env, claims);
      return json({ indexed, ledger_appended: appended, ledger_unchanged: unchanged, vaulted });
    }

    if (p === "/search" && req.method === "GET") {
      const q = url.searchParams.get("q");
      if (!q) return json({ error: "missing query parameter 'q'" }, 400);
      const topK = Math.min(20, Math.max(1, Number(url.searchParams.get("topK")) || 5));
      return json({ query: q, hits: await searchClaims(env, q, topK) });
    }

    if (p === "/ask" && req.method === "GET") {
      const q = url.searchParams.get("q");
      if (!q) return json({ error: "missing query parameter 'q'" }, 400);
      return json(await ask(env, q));
    }

    if (p === "/history" && req.method === "GET") {
      const claim = url.searchParams.get("claim");
      if (!claim) return json({ error: "missing 'claim'" }, 400);
      return json({ claim, events: await history(env, claim) });
    }

    if (p === "/verify" && req.method === "GET") {
      const claim = url.searchParams.get("claim");
      if (!claim) return json({ error: "missing 'claim'" }, 400);
      const events = await history(env, claim);
      const latest = events[events.length - 1];
      const chain = await verifyChain(env);
      const evidence = latest?.artifact_sha256
        ? await verifyEvidence(env, latest.artifact_sha256)
        : { present: false, matches: false, size: 0 };
      return json({
        claim, found: !!latest,
        evidence_sha256: latest?.artifact_sha256 ?? null,
        evidence, ledger_intact: chain.ok,
      });
    }

    if (p === "/ledger/verify" && req.method === "GET") {
      return json(await verifyChain(env));
    }

    // --- external anchoring: heads + full export for CLIENT-side re-walking.
    // The point of /ledger/export is that a witness must not have to trust
    // this Worker: it downloads every row, recomputes every hash itself, and
    // checks the chain still extends previously witnessed heads.
    if (p === "/ledger/head" && req.method === "GET") {
      const claimsRows = await env.DB.prepare(
        "SELECT seq, entry_hash FROM claim_events ORDER BY seq DESC LIMIT 1").first();
      const claimsCount = await env.DB.prepare(
        "SELECT COUNT(*) AS c FROM claim_events").first();
      const libRows = await env.DB.prepare(
        "SELECT seq, entry_hash FROM library_bundles ORDER BY seq DESC LIMIT 1").first();
      const libCount = await env.DB.prepare(
        "SELECT COUNT(*) AS c FROM library_bundles").first();
      return json({
        ts: new Date().toISOString(),
        claims: {
          entries: Number((claimsCount as { c: number })?.c ?? 0),
          head: (claimsRows as { entry_hash: string } | null)?.entry_hash ?? "",
        },
        library: {
          entries: Number((libCount as { c: number })?.c ?? 0),
          head: (libRows as { entry_hash: string } | null)?.entry_hash ?? "",
        },
      });
    }

    if (p === "/ledger/export" && req.method === "GET") {
      const claims = await env.DB.prepare(
        "SELECT * FROM claim_events ORDER BY seq ASC").all();
      const library = await env.DB.prepare(
        "SELECT * FROM library_bundles ORDER BY seq ASC").all();
      return json({ claims: claims.results ?? [], library: library.results ?? [] });
    }

    // --- the research layer: vectorized literature (retrieval, not truth) ---
    if (p === "/research/index" && req.method === "POST") {
      if (!authorized(req, env)) return json({ error: "unauthorized" }, 401);
      let payload: { works?: WorkIn[]; chunks?: ChunkIn[] };
      try { payload = await req.json(); } catch { return json({ error: "invalid JSON" }, 400); }
      const result = await ingestLiterature(
        env, payload.works ?? [], payload.chunks ?? [], new Date().toISOString());
      return json(result);
    }

    if (p === "/research/search" && req.method === "GET") {
      const q = url.searchParams.get("q");
      if (!q) return json({ error: "missing query parameter 'q'" }, 400);
      const topK = Math.min(20, Math.max(1, Number(url.searchParams.get("topK")) || 5));
      return json({
        query: q, hits: await searchResearch(env, q, topK),
        note: "Retrieval, never evidence. tier='web-snapshot' hits are not " +
              "peer-reviewed; every hit's text is hash-locked in the catalog.",
      });
    }

    if (p === "/research/ask" && req.method === "GET") {
      const q = url.searchParams.get("q");
      if (!q) return json({ error: "missing query parameter 'q'" }, 400);
      return json(await askResearch(env, q));
    }

    if (p.startsWith("/research/work/") && req.method === "GET") {
      const fsid = p.slice("/research/work/".length);
      const w = await getWork(env, fsid);
      return w ? json(w) : json({ error: "no such work" }, 404);
    }

    if (p === "/research/summary" && req.method === "GET") {
      return json(await researchSummary(env));
    }

    // --- the claims library: cross-project bundle preservation & reuse ------
    if (p === "/library/index" && req.method === "POST") {
      if (!authorized(req, env)) return json({ error: "unauthorized" }, 401);
      let payload: { bundles?: BundleIn[] };
      try { payload = await req.json(); } catch { return json({ error: "invalid JSON" }, 400); }
      const result = await indexBundles(env, payload.bundles ?? [], new Date().toISOString());
      return json(result, result.rejected.length && !result.stored && !result.unchanged ? 400 : 200);
    }

    if (p === "/library/search" && req.method === "GET") {
      const q = url.searchParams.get("q");
      if (!q) return json({ error: "missing query parameter 'q'" }, 400);
      const topK = Math.min(20, Math.max(1, Number(url.searchParams.get("topK")) || 5));
      return json({
        query: q, hits: await searchLibrary(env, q, topK),
        note: "status='candidate' hits are quarantined, unverified assertions — " +
              "never treat them as gate-verified claims.",
      });
    }

    if (p.startsWith("/library/bundle/") && req.method === "GET") {
      const id = p.slice("/library/bundle/".length);
      const b = await getBundle(env, id);
      return b ? json(b) : json({ error: "no such bundle" }, 404);
    }

    if (p.startsWith("/library/file/") && req.method === "GET") {
      const sha = p.slice("/library/file/".length);
      if (!/^[0-9a-f]{64}$/.test(sha)) return json({ error: "bad sha256" }, 400);
      const bytes = await getEvidence(env, sha);
      if (!bytes) return json({ error: "not in vault" }, 404);
      return new Response(bytes, {
        headers: { "content-type": "application/octet-stream", "x-sha256": sha },
      });
    }

    if (p.startsWith("/library/verify/") && req.method === "GET") {
      const id = p.slice("/library/verify/".length);
      return json(await verifyLibraryBundle(env, id));
    }

    if (p === "/library/verify" && req.method === "GET") {
      return json(await verifyLibraryChain(env));
    }

    if (p === "/library/summary" && req.method === "GET") {
      return json(await librarySummary(env));
    }

    // Version chain for one logical claim: every immutable bundle version,
    // oldest first — supersession is DERIVED from the append-only registry.
    if (p === "/library/versions" && req.method === "GET") {
      const repo = url.searchParams.get("repo");
      const claim = url.searchParams.get("claim");
      if (!repo || !claim) return json({ error: "need 'repo' and 'claim'" }, 400);
      const chain = await versionChain(env, repo, claim);
      return json({
        source_repo: repo, source_claim_id: claim,
        versions: chain.map((r, i) => ({
          bundle_id: r.bundle_id, ts: r.ts, status: r.status, seq: r.seq,
          is_current: i === chain.length - 1,
        })),
      });
    }

    if (p === "/library/prune" && req.method === "POST") {
      if (!authorized(req, env)) return json({ error: "unauthorized" }, 401);
      return json(await pruneSuperseded(env));
    }

    if (p === "/passport") {
      return new Response(await passportHTML(env), {
        headers: { "content-type": "text/html; charset=utf-8" },
      });
    }

    if (p === "/badge.svg") {
      return new Response(await badgeSVG(env), {
        headers: { "content-type": "image/svg+xml", "cache-control": "max-age=300" },
      });
    }

    if (p === "/summary") return json(await summary(env));

    return json({ error: "not found" }, 404);
  },
};
