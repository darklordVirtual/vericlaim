# Diagram: Reproduction sandbox sequence

**Purpose.** Show how the declarative reproduce runner proves an output is
re-created *from scratch*. One question: *why can't a no-op pass?*

**Assumptions.** The register is trusted (same trust as the test suite). The
runner isolates OUTPUTS and blocks shell parsing; it does not sandbox the OS —
see the reproduction model for that honest limit.

**Legend.** Solid arrow = call/return; note = a fail-closed decision point.

```mermaid
sequenceDiagram
    participant CLI as reproduce
    participant R as repro runner
    participant FS as temp output dir
    participant P as subprocess (argv, shell=false)
    participant A as committed artifact

    CLI->>R: run_declarative(spec)
    R->>FS: create EMPTY output dir
    R->>R: substitute {output_dir} in argv
    R->>P: Popen(argv), start_new_session
    Note over P: no shell parsing, own process group
    P->>FS: write declared outputs
    P-->>R: exit code, stdout/stderr tail
    Note over R: exit != 0 -> FAIL
    R->>FS: list produced files
    Note over R,FS: output absent -> FAIL (a no-op cannot pass)
    Note over R,FS: undeclared file present -> FAIL
    R->>A: byte-compare produced vs committed
    Note over R,A: differ -> FAIL (stale or non-deterministic)
    R->>FS: remove temp dir (always)
    R-->>CLI: ReproductionResult (ok, hashes, timings)
```

**Narrative (alt-text).** `reproduce` calls the runner, which creates an EMPTY
temporary output directory and substitutes `{output_dir}` into the argv. The
command runs as a real subprocess with `shell=False` in its own process group (so
a timeout kills the whole group). It must write its declared outputs into the
empty directory. The runner then fails closed at three gates: a non-zero exit
fails; a declared output that is absent fails — this is why a no-op cannot pass,
because there is no stale file to fall back on; and an undeclared file in the
directory fails. Finally it byte-compares each produced output to the committed
artifact — any difference (a stale committed number or a non-deterministic
script) fails. The temporary directory is always removed, and a machine-readable
result records the outcome.
