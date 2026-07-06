# Reproduction model

**Purpose.** Explain how `vericlaim reproduce` proves a claim's number is *still
true today*, the difference between the legacy and declarative forms, and the
honest limits of the isolation. Scope: the `vericlaim/repro.py` runner.

## The problem with "artifact unchanged"

The legacy check runs a shell command in the repo, then verifies the artifact is
byte-identical. A command that does **nothing** passes — the old artifact is
still on disk. That is a false guarantee: it cannot distinguish "the number
reproduces" from "the file wasn't touched."

## The declarative oracle

The declarative form makes reproduction produce its outputs into an **empty,
isolated directory**, so nothing stale can carry a pass:

```yaml
reproduce:
  argv: ["python3", "bench/parse.py", "--output", "{output_dir}/parse_bench.json"]
  outputs: ["results/parse_bench.json"]
  timeout_seconds: 300
  network: disabled
  environment: { PYTHONHASHSEED: "0", TZ: "UTC", LC_ALL: "C.UTF-8" }
```

Runner behavior (all fail-closed):

1. Create a fresh empty output directory; substitute `{output_dir}` in `argv`.
2. Execute with `shell=False` — no shell parsing, no injection, argv is a list.
3. `start_new_session=True` so a timeout SIGKILLs the whole **process group**
   (child + grandchildren). stdout/stderr captured with a bounded tail.
4. Require every declared output to have been **created** in the output dir. A
   no-op fails: the output is absent. A missing declared output fails.
5. Reject **undeclared** files in the output dir (the command wrote something it
   didn't declare).
6. Compare each produced output to the committed artifact byte-for-byte. A
   mismatch means the committed number is stale or the script is
   non-deterministic — both fail.
7. Emit a machine-readable `ReproductionResult` (exit code, elapsed, output
   SHA-256s, env profile).
8. Always clean up the temporary directory.

See the sequence diagram:
[`../diagrams/reproduction-sandbox-sequence.md`](../diagrams/reproduction-sandbox-sequence.md).

## Profiles

- **adopt** — legacy string `reproduce` commands are allowed behind the explicit
  `allow_legacy_shell` migration flag (weaker: no-op can pass).
- **strict / enterprise** — legacy shell is rejected outright; only declarative
  specs run. Secure by default.

## Honest limits

The runner isolates **outputs** and blocks shell parsing. It does **not** provide
OS-level filesystem or network sandboxing: a determined command could still read
or write elsewhere on the host, or use the network. Therefore:

- `network: disabled` is recorded as *requested*, not *enforced*.
  `network_enforced` in the result is **always false**.
- Detection of "writes outside approved outputs" is limited to inspecting the
  output directory for undeclared files; it is not a syscall sandbox.

Run reproduction only on **trusted** registers — the same trust level as running
your own test suite. True sandboxed runners (containers / seccomp / network
namespaces) are a deferred enterprise-tier item (see `../../ROADMAP.md`).
