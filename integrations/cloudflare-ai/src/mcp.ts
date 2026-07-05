// Optional MCP server for the vericlaim claim index.
//
// Exposes read-only tools over the Model Context Protocol so an MCP client
// (Claude, an IDE, an agent) can search claims, get grounded answers, read the
// tamper-evident ledger, and verify evidence integrity.
//
// This whole file is optional: it is only wired up when ENABLE_MCP === "true".
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { type Env, searchClaims } from "./lib";
import { ask } from "./oracle";
import { history, verifyChain } from "./ledger";
import { verifyEvidence } from "./vault";
import { getBundle, searchLibrary } from "./library";
import { askResearch, searchResearch } from "./research";

const text = (t: string) => ({ content: [{ type: "text" as const, text: t }] });

export class VericlaimMCP extends McpAgent<Env> {
  server = new McpServer({ name: "vericlaim-claims", version: "0.2.0" });

  async init() {
    // 1. search — semantic discovery over claims
    this.server.tool(
      "search_claims",
      "Semantic search over a project's registered, gate-verified vericlaim " +
        "claims. Returns matches with evidence level and caveat. A search hit " +
        "is not proof — a claim is trustworthy because the gate verified it.",
      {
        query: z.string().describe("Natural-language description of the claim to find"),
        topK: z.number().int().min(1).max(20).default(5),
      },
      async ({ query, topK }) => {
        const hits = await searchClaims(this.env, query, topK);
        if (!hits.length) return text("No matching claims.");
        return text(hits.length + " claim(s):\n" + hits.map((h) =>
          `- [${h.id}] (${h.evidence_level}, score ${h.score.toFixed(3)})\n  ${h.statement}` +
          (h.caveat ? `\n  caveat: ${h.caveat}` : "") +
          (h.artifact ? `\n  artifact: ${h.artifact}` : "")).join("\n"));
      },
    );

    // 2. ask — grounded answer that refuses to overclaim
    this.server.tool(
      "ask_claims",
      "Ask a question and get an answer grounded ONLY in the project's " +
        "registered claims, with claim-id citations. If no claim supports an " +
        "answer, it refuses rather than guessing — mirror that: do not fill the " +
        "gap with your own assumptions.",
      { query: z.string().describe("The question to answer from registered claims") },
      async ({ query }) => {
        const a = await ask(this.env, query);
        if (a.refused) return text("REFUSED: " + a.answer);
        return text(a.answer + "\n\nCitations: " + a.citations.join(", "));
      },
    );

    // 3. history — the tamper-evident ledger timeline for a claim
    this.server.tool(
      "get_claim_history",
      "Return the append-only ledger timeline for a claim id: every recorded " +
        "change to its statement, evidence level, metrics and evidence hash.",
      { claim_id: z.string() },
      async ({ claim_id }) => {
        const events = await history(this.env, claim_id);
        if (!events.length) return text(`No ledger history for ${claim_id}.`);
        return text(events.map((e) =>
          `#${e.seq} ${e.ts.slice(0, 19)} — ${e.evidence_level}` +
          (e.artifact_sha256 ? ` — evidence ${e.artifact_sha256.slice(0, 12)}…` : "") +
          `\n  ${e.statement}`).join("\n"));
      },
    );

    // 4. verify — re-hash the claim's evidence and check the ledger chain
    this.server.tool(
      "verify_claim",
      "Integrity check: confirm the claim's evidence in the vault still hashes " +
        "to its recorded SHA-256, and that the ledger's hash chain is intact.",
      { claim_id: z.string() },
      async ({ claim_id }) => {
        const events = await history(this.env, claim_id);
        const latest = events[events.length - 1];
        const chain = await verifyChain(this.env);
        if (!latest) return text(`No such claim: ${claim_id}.`);
        const ev = latest.artifact_sha256
          ? await verifyEvidence(this.env, latest.artifact_sha256)
          : null;
        return text(
          `claim: ${claim_id}\n` +
          `evidence sha256: ${latest.artifact_sha256 ?? "(none stored)"}\n` +
          `evidence present/matches: ${ev ? `${ev.present}/${ev.matches} (${ev.size} bytes)` : "n/a"}\n` +
          `ledger chain intact: ${chain.ok}${chain.ok ? "" : ` (broken at #${chain.brokenAt})`}`);
      },
    );

    // 5. library search — cross-project bundle discovery
    this.server.tool(
      "search_library",
      "Semantic search over the cross-project claims LIBRARY: curated bundles " +
        "of claims + evidence + code + literature harvested from gate-verified " +
        "repos. Hits with status 'candidate' are quarantined, UNVERIFIED " +
        "assertions — never present them as verified claims. Reuse a bundle " +
        "via integrations/library/import_bundle.py, which verifies every hash " +
        "offline.",
      {
        query: z.string().describe("What you want a proven claim about"),
        topK: z.number().int().min(1).max(20).default(5),
      },
      async ({ query, topK }) => {
        const hits = await searchLibrary(this.env, query, topK);
        if (!hits.length) return text("No matching library bundles.");
        return text(hits.length + " bundle(s):\n" + hits.map((h) =>
          `- [${h.claim_id}] bundle ${h.bundle_id.slice(0, 12)}… ` +
          `(${h.status.toUpperCase()}, ${h.evidence_level}, score ${h.score.toFixed(3)}, ` +
          `from ${h.source_repo})\n  ${h.statement}` +
          (h.caveat ? `\n  caveat: ${h.caveat}` : "")).join("\n"));
      },
    );

    // 6. bundle detail — claim + manifest + provenance for local verification
    this.server.tool(
      "get_bundle",
      "Fetch a library bundle's claim, manifest (file sha256 map) and harvest " +
        "provenance by bundle id. Files are fetched by hash at " +
        "/library/file/<sha256> and MUST be verified locally against the " +
        "manifest — the library is distribution, not truth.",
      { bundle_id: z.string() },
      async ({ bundle_id }) => {
        const b = await getBundle(this.env, bundle_id);
        if (!b) return text(`No such bundle: ${bundle_id}.`);
        return text(JSON.stringify(b, null, 2));
      },
    );

    // 7. research search — chunk-level retrieval over the literature catalog
    this.server.tool(
      "search_literature_rag",
      "Semantic search over the vectorized research literature (the canonical " +
        "research map: uncertainty/conformal, agents, evaluation, agent " +
        "security, governance, MLOps, provenance/supply-chain, formal methods, " +
        "fairness, assurance cases). Every hit's text is hash-locked in the " +
        "git-anchored catalog. Retrieval, never evidence: tier='web-snapshot' " +
        "hits are NOT peer-reviewed — treat them accordingly.",
      {
        query: z.string().describe("What you want the literature to speak to"),
        topK: z.number().int().min(1).max(20).default(5),
      },
      async ({ query, topK }) => {
        const hits = await searchResearch(this.env, query, topK);
        if (!hits.length) return text("No matching literature chunks.");
        return text(hits.length + " chunk(s):\n" + hits.map((h) =>
          `- [${h.work_id}] ${h.title}` +
          `${h.section ? ` — ${h.section}` : ""} ` +
          `(${h.tier}${h.accredited ? ", peer-reviewed venue" : ""}, ` +
          `score ${h.score.toFixed(3)})\n  ${h.snippet}` +
          (h.linked_claims.length
            ? `\n  linked claims: ${h.linked_claims.join(", ")}` : ""))
          .join("\n"));
      },
    );

    // 8. research ask — grounded literature answer that refuses
    this.server.tool(
      "ask_research",
      "Ask a question answered ONLY from hash-locked excerpts of the cataloged " +
        "research literature, with work-id citations. Refuses when no cataloged " +
        "work supports an answer — mirror that: do not fill the gap from " +
        "model memory.",
      { question: z.string().describe("The question to answer from the literature") },
      async ({ question }) => {
        const a = await askResearch(this.env, question);
        if (a.refused) return text("REFUSED: " + a.answer);
        return text(a.answer + "\n\nCitations: " + a.citations.map((c) =>
          c.work_id + (c.section ? ` (${c.section})` : "")).join("; "));
      },
    );
  }
}
