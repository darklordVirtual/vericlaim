// Build stub for the Vercel `ai` package.
//
// The Agents SDK's *client* bundle contains a dynamic `import("ai")` for its
// AI-SDK integration. We only use `agents/mcp` (the MCP server), never that
// client path, so the import is dead code at runtime — but esbuild must still
// resolve it at build time. This stub satisfies the resolver with a harmless
// passthrough. If the unused code path ever ran, it would just return the
// schema unchanged.
export function jsonSchema(schema) {
  return schema;
}
export default { jsonSchema };
