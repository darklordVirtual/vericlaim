// The public trust surface: a shareable "claim passport" page and an SVG badge,
// rendered at the edge from the ledger. A nutrition label for what a project
// claims about itself — counts, evidence-level distribution, and whether the
// tamper-evident ledger still verifies.
import { type Env } from "./lib";
import { summary, verifyChainCached } from "./ledger";

const LEVEL_COLORS: Record<string, string> = {
  theoretical: "#9aa0b4", measured: "#4a86e8", benchmarked: "#7c4dff",
  reproduced: "#2a9d8f", externally_validated: "#2a8a2a",
};

function esc(s: string): string {
  return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]!));
}

export async function passportHTML(env: Env): Promise<string> {
  const s = await summary(env);
  const chain = await verifyChainCached(env);
  const levels = ["theoretical", "measured", "benchmarked", "reproduced", "externally_validated"];
  const bars = levels.map((lv) => {
    const n = s.by_level[lv] ?? 0;
    const w = s.claims ? Math.round((n / s.claims) * 100) : 0;
    return `<div class="bar"><span class="lbl">${lv}</span>
      <span class="track"><span class="fill" style="width:${w}%;background:${LEVEL_COLORS[lv]}"></span></span>
      <span class="num">${n}</span></div>`;
  }).join("");
  const rows = s.latest.map((c) =>
    `<tr><td class="mono">${esc(c.claim_id)}</td>
      <td><span class="pill" style="background:${LEVEL_COLORS[c.evidence_level] ?? "#999"}">${esc(c.evidence_level)}</span></td>
      <td class="mono sha">${c.artifact_sha256 ? esc(c.artifact_sha256).slice(0, 16) + "…" : "—"}</td>
      <td class="mono">${esc(c.ts).slice(0, 10)}</td></tr>`).join("");
  const integrity = chain.ok
    ? `<span class="ok">✔ Ledger internt konsistent</span> · ${chain.entries} hendelser, hash-kjeden re-walket (bevis mot delvise endringer; ikke mot en full omskriving — se ekstern-vitne/HMAC)`
    : `<span class="bad">✘ Ledger brutt ved #${chain.brokenAt}</span>`;

  return `<!DOCTYPE html><html lang="no"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>vericlaim — claim-pass</title><style>
:root{color-scheme:light}
body{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;max-width:820px;margin:0 auto;padding:28px 20px;color:#1a1a2e;background:#fafbff}
h1{font-size:22px;margin:0 0 2px}.sub{color:#556;margin:0 0 18px}
.cards{display:flex;gap:12px;margin:16px 0}
.card{flex:1;border:1px solid #dde;border-radius:10px;padding:14px;text-align:center;background:#fff}
.card .n{font-size:26px;font-weight:700;display:block}.card .l{font-size:11px;color:#667}
.bar{display:flex;align-items:center;gap:8px;margin:5px 0;font-size:13px}
.bar .lbl{width:150px;color:#445}.bar .track{flex:1;height:12px;background:#eef;border-radius:6px;overflow:hidden}
.bar .fill{display:block;height:100%}.bar .num{width:24px;text-align:right;color:#556}
table{border-collapse:collapse;width:100%;margin-top:8px;font-size:13px}
th,td{border-bottom:1px solid #e6e8f5;padding:6px 8px;text-align:left}
th{color:#556;font-weight:600;font-size:12px}
.mono{font-family:"SF Mono",Menlo,monospace;font-size:12px}.sha{color:#778}
.pill{color:#fff;padding:1px 8px;border-radius:9px;font-size:11px}
.ok{color:#1c7c1c;font-weight:700}.bad{color:#a22;font-weight:700}
.integrity{margin:14px 0;padding:10px 14px;background:#f2fbf2;border-left:4px solid #2a8a2a;border-radius:4px;font-size:13px}
.foot{margin-top:22px;color:#889;font-size:11px;border-top:1px solid #e6e8f5;padding-top:10px}
a{color:#4a6}
</style></head><body>
<h1>Claim-pass</h1>
<p class="sub">Hva dette prosjektet påstår om seg selv — og hva som backer det. Levert fra en append-only, hash-kjedet hovedbok på kanten (bevis mot delvise endringer; ekstern-vitne re-walk for full tamper-evidens).</p>
<div class="cards">
  <div class="card"><span class="n">${s.claims}</span><span class="l">registrerte claims</span></div>
  <div class="card"><span class="n">${s.events}</span><span class="l">hendelser i hovedboka</span></div>
  <div class="card"><span class="n">${(s.by_level.benchmarked ?? 0) + (s.by_level.reproduced ?? 0) + (s.by_level.externally_validated ?? 0)}</span><span class="l">benchmarked+</span></div>
</div>
<div class="integrity">${integrity}</div>
<h3>Evidensnivå-fordeling</h3>
${bars}
<h3>Claims</h3>
<table><thead><tr><th>ID</th><th>Evidensnivå</th><th>Artefakt (SHA-256)</th><th>Sist endret</th></tr></thead>
<tbody>${rows || '<tr><td colspan="4">Ingen claims ennå.</td></tr>'}</tbody></table>
<p class="foot">vericlaim · Claim-Oriented Programming av Stian Skogbrott ·
Evidensnivå er prosjektets egen ærlige påstand; søk/pass er et oppdagelseshjelpemiddel og
endrer ikke hva gaten beviser. · <a href="/badge.svg">badge</a></p>
</body></html>`;
}

export async function badgeSVG(env: Env): Promise<string> {
  const s = await summary(env);
  const chain = await verifyChainCached(env);
  const label = "vericlaim";
  const strong = (s.by_level.benchmarked ?? 0) + (s.by_level.reproduced ?? 0) +
    (s.by_level.externally_validated ?? 0);
  const msg = chain.ok ? `${s.claims} claims ✔` : `ledger broken`;
  const color = chain.ok ? (strong > 0 ? "#2a8a2a" : "#4a86e8") : "#c0392b";
  const lw = 62, mw = Math.max(70, msg.length * 7 + 16), w = lw + mw;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="20" role="img" aria-label="${label}: ${msg}">
<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<rect rx="3" width="${w}" height="20" fill="#555"/>
<rect rx="3" x="${lw}" width="${mw}" height="20" fill="${color}"/>
<rect rx="3" width="${w}" height="20" fill="url(#s)"/>
<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
<text x="${lw / 2}" y="14">${label}</text>
<text x="${lw + mw / 2}" y="14">${msg}</text>
</g></svg>`;
}
