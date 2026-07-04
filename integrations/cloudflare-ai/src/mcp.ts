// Optional MCP server for the vericlaim claim index.
//
// Exposes one read-only tool, `search_claims`, over the Model Context Protocol
// so an MCP client (Claude, an IDE, an agent) can ask "what has this project
// actually proven about X?" and get back registered, gate-verified claims.
//
// This whole file is optional: it is only wired up when ENABLE_MCP === "true".
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { type Env, searchClaims } from "./lib";

export class VericlaimMCP extends McpAgent<Env> {
  server = new McpServer({ name: "vericlaim-claims", version: "0.1.5" });

  async init() {
    this.server.tool(
      "search_claims",
      "Semantic search over a project's registered, gate-verified vericlaim " +
        "claims. Returns the matching claims with their evidence level and " +
        "caveat. Use it to find what a project has actually proven — never " +
        "treat a search hit as proof in itself; the claim is trustworthy " +
        "because the vericlaim gate verified it, not because it was found here.",
      {
        query: z.string().describe("Natural-language description of the claim to find"),
        topK: z.number().int().min(1).max(20).default(5)
          .describe("How many claims to return"),
      },
      async ({ query, topK }) => {
        const hits = await searchClaims(this.env, query, topK);
        if (hits.length === 0) {
          return { content: [{ type: "text", text: "No matching claims." }] };
        }
        const lines = hits.map(
          (h) => `- [${h.id}] (${h.evidence_level}, score ${h.score.toFixed(3)})\n` +
            `  ${h.statement}\n` +
            (h.caveat ? `  caveat: ${h.caveat}\n` : "") +
            (h.artifact ? `  artifact: ${h.artifact}` : ""),
        );
        return { content: [{ type: "text", text: hits.length + " claim(s):\n" + lines.join("\n") }] };
      },
    );
  }
}
