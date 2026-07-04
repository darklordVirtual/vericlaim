#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproducible live test for the vericlaim Cloudflare add-on.

Point it at YOUR deployed Worker and it exercises every capability end to end:
the REST layer, the grounded oracle (answer + refusal), the tamper-evident
ledger, the evidence vault, and the MCP protocol (all four tools). It is
self-configuring — it reads a real claim id from /summary — and **read-only**,
so it is safe to run against a live deployment.

    python3 live_test.py --url https://vericlaim-claims.<subdomain>.workers.dev

Exit code 0 means every check passed. Zero third-party dependencies (stdlib).
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "vericlaim-live-test/1.0"
MCP_HEADERS = {"accept": "application/json, text/event-stream"}
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))
    return ok


def http(method: str, url: str, body=None, headers=None, timeout=25):
    data = json.dumps(body).encode() if body is not None else None
    h = {"user-agent": UA, **(headers or {})}
    if data is not None:
        h.setdefault("content-type", "application/json")
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()


def parse_mcp(text: str):
    obj = None
    for line in text.splitlines():
        if line.startswith("data:"):
            obj = json.loads(line[5:].strip())
    if obj is None and text.strip():
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            pass
    return obj


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True, help="base Worker URL (no trailing slash)")
    args = ap.parse_args()
    base = args.url.rstrip("/")
    mcp = base + "/mcp"

    # --- discover a real claim + topic from the deployment -------------------
    st, _, body = http("GET", base + "/summary")
    summary = json.loads(body) if st == 200 else {}
    latest = summary.get("latest", [])
    if not latest:
        print("No claims indexed yet — push your register first "
              "(export_claims.py --push). Aborting.")
        return 2
    claim_id = latest[0]["claim_id"]

    # --- REST ----------------------------------------------------------------
    st, _, body = http("GET", base + "/")
    d = json.loads(body)
    check("health", st == 200 and "capabilities" in d,
          f"caps={len(d.get('capabilities', []))}, ledger={d.get('ledger', {}).get('ok')}")

    q = urllib.parse.quote(latest[0].get("claim_id", "result"))
    st, _, body = http("GET", f"{base}/search?q={q}&topK=3")
    check("search", st == 200 and len(json.loads(body).get("hits", [])) >= 1)

    # --- oracle: grounded answer + refusal -----------------------------------
    st, _, body = http("GET", f"{base}/ask?q=" + urllib.parse.quote(
        "what has this project measured or proven"))
    a = json.loads(body)
    check("oracle grounds an answer", st == 200 and not a["refused"] and a["citations"],
          f"cites {a.get('citations')}")

    st, _, body = http("GET", f"{base}/ask?q=" + urllib.parse.quote(
        "what is the boiling point of mercury on Jupiter"))
    a = json.loads(body)
    check("oracle refuses the unsupported", a.get("refused") is True,
          "refused as designed")

    # --- ledger + vault ------------------------------------------------------
    st, _, body = http("GET", f"{base}/history?claim={urllib.parse.quote(claim_id)}")
    check("ledger history", st == 200 and len(json.loads(body).get("events", [])) >= 1,
          f"{claim_id}")

    st, _, body = http("GET", f"{base}/verify?claim={urllib.parse.quote(claim_id)}")
    v = json.loads(body)
    ev = v.get("evidence", {})
    check("evidence vault verify", v.get("found") and v.get("ledger_intact")
          and (ev.get("matches") or not v.get("evidence_sha256")),
          f"matches={ev.get('matches')}, size={ev.get('size')}")

    st, _, body = http("GET", base + "/ledger/verify")
    lv = json.loads(body)
    check("ledger hash-chain intact", lv.get("ok") is True, f"{lv.get('entries')} entries")

    # --- public surface ------------------------------------------------------
    st, _, body = http("GET", base + "/badge.svg")
    check("badge.svg", st == 200 and "<svg" in body)
    st, _, body = http("GET", base + "/passport")
    check("passport page", st == 200 and "<title>" in body)

    # --- MCP -----------------------------------------------------------------
    st, hdr, body = http("POST", mcp, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "live-test", "version": "1.0"}}}, MCP_HEADERS)
    sid = hdr.get("mcp-session-id")
    init = parse_mcp(body) or {}
    mcp_on = st == 200 and bool(sid)
    check("mcp initialize", mcp_on,
          f"server={init.get('result', {}).get('serverInfo', {}).get('name')}"
          if mcp_on else "MCP not enabled (ENABLE_MCP=false) — skipping tool checks")

    if mcp_on:
        http("POST", mcp, {"jsonrpc": "2.0", "method": "notifications/initialized"},
             {**MCP_HEADERS, "mcp-session-id": sid})

        def call(method, params):
            _, _, b = http("POST", mcp, {"jsonrpc": "2.0", "id": 2, "method": method,
                                         "params": params}, {**MCP_HEADERS, "mcp-session-id": sid})
            return parse_mcp(b) or {}

        tools = [t["name"] for t in call("tools/list", {}).get("result", {}).get("tools", [])]
        want = {"search_claims", "ask_claims", "get_claim_history", "verify_claim"}
        check("mcp exposes 4 tools", want.issubset(set(tools)), f"{tools}")

        for tool, arg in [("search_claims", {"query": "result", "topK": 2}),
                          ("ask_claims", {"query": "what has this project proven"}),
                          ("get_claim_history", {"claim_id": claim_id}),
                          ("verify_claim", {"claim_id": claim_id})]:
            r = call("tools/call", {"name": tool, "arguments": arg})
            txt = (r.get("result", {}).get("content") or [{}])[0].get("text", "")
            check(f"mcp {tool}", bool(txt) and "error" not in r, f"{len(txt)} chars")

    # --- summary -------------------------------------------------------------
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    print("=" * 60)
    print(f"{passed}/{total} checks passed against {base}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
