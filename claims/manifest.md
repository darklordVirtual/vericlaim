# Artifact Manifest

SHA-256 over committed (LF) file bytes. The gate recomputes each hash and fails
on mismatch, so a silently-edited result artifact is caught in CI. On a Windows
(CRLF) working tree the LF-normalized form is matched with a note.

| File | SHA-256 |
|------|---------|
| `examples/rle/artifacts/rle_bench.json` | `78566810996df27fd5c3fb0772b4d3929c9663c9ab984ef04a0d918ef6f869c7` |
| `examples/greetings/artifacts/greetings.json` | `2759c18e03d9482e66e9a820ffd26dfd0b4811dabdeb214bd9f8f9619ad98fe2` |
| `examples/tipcalc/artifacts/tipcalc.json` | `65cdc526f3c0e3f973141ec1a732f13872af4e401e62ae1fa0a8738838311965` |
| `examples/theorem/artifacts/theorem.json` | `178ce1c1d30982e45e964bfa0430d2c76b01910e7bf41ea2f4fbb77126bbeed5` |
| `claims/version.json` | `da9da2c003b8eee13e6a8b295dadb7e37740a6616eadf890d60a353cc33d37d1` |
| `integrations/library/artifacts/research_layer.json` | `5ca046ba2c5f3914cdc9280fee76c1151f54bdcc4a87284199d56be726f558a9` |
| `domains/eval_harness/artifacts/eval_report.json` | `3a259bad982fd6e5969620d80aeec9c93109a46bec2576ab81e5900796a26708` |
| `domains/evidence_graph/artifacts/graph.json` | `b0cec0ac245d850be07e44c080663d33a3250ae173fb7988e967a3c11092aeb7` |
| `domains/multitenant/artifacts/isolation_report.json` | `106507742af9aa9323246c56920f20d0647e572bc1dbc8220daea6e15c962148` |
| `domains/ontologies/artifacts/ontology_conformance.json` | `381cdccac18af18a0346e5ca9b709fc10b4e232ac352bbb9cfcffc8bfe202622` |
| `domains/cost_routing/artifacts/routing_report.json` | `9cadc90077058792f31b8bb12c70a06be6d1da40be76b7c572ce6246f729006c` |
| `claims/selfimprove_envelope.json` | `3bb6fe76fdd276f52e768e0440768e42c95bd978bf8205ffc32348a366d86bfb` |
| `claims/autonomous_cycle.json` | `7efd2cbcec7ba1511e93d5d011cfd54e6a654e0f427d73844bb2dc7f432c1ab6` |
| `claims/ai_catalog.json` | `e10da6b014fed09ce24cda01e80c657e779a44e7bb3e2e7307c4e3526db030d1` |
| `claims/claimlib_index.json` | `ccc8b8c86df733dabbd7ac4579cc6b732aa546604391f8e5c8a90a00f07a23a6` |
