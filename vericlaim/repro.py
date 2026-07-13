# SPDX-License-Identifier: Apache-2.0
"""Declarative reproduction: prove a claim's artifact is re-creatable *from
scratch*, not merely that a stale file is unchanged.

The weakness of the legacy `reproduce: "python bench.py"` form is that it runs in
the repo, then checks the artifact is byte-identical — so a command that does
NOTHING passes (the old artifact is still there). The declarative form fixes this:

    reproduce:
      argv: ["python3", "bench/parse.py", "--output", "{output_dir}/parse_bench.json"]
      outputs: ["results/parse_bench.json"]
      timeout_seconds: 300
      network: disabled
      environment: { PYTHONHASHSEED: "0", TZ: "UTC", LC_ALL: "C.UTF-8" }

The runner creates an EMPTY output directory, substitutes ``{output_dir}`` in
argv, executes with ``shell=False`` (no shell parsing, no injection), and then
requires every declared output to have been *created* in that directory and to
match the committed artifact byte-for-byte. A no-op fails because the output is
absent. An undeclared file in the output directory fails. Timeout kills the whole
process group.

HONESTY: this isolates OUTPUTS (a fresh dir the command must populate) and blocks
shell parsing. It does NOT provide OS-level filesystem/network sandboxing — a
determined command could still read/write elsewhere on the host or use the
network. ``network: disabled`` is recorded as *requested*, not enforced;
``network_enforced`` is always False here. True sandboxing is a deferred
enterprise-tier runner. Run reproduction only on trusted registers (same trust
as your test suite).
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .pathsafe import PathSafetyError, check_relpath

_OUTPUT_TOKEN = "{output_dir}"
_MAX_CAPTURE = 64 * 1024  # bytes of stdout/stderr retained in the report


class ReproError(ValueError):
    """A reproduction spec is malformed or forbidden by the active profile."""


@dataclass(frozen=True)
class ReproSpec:
    """A parsed reproduction specification (declarative or legacy shell)."""
    outputs: tuple[str, ...] = ()
    argv: tuple[str, ...] = ()
    timeout_seconds: int = 300
    network: str = "disabled"
    environment: tuple[tuple[str, str], ...] = ()
    legacy_shell: str | None = None  # set only for the legacy string form

    @property
    def is_legacy(self) -> bool:
        return self.legacy_shell is not None

    @classmethod
    def parse(cls, raw: object, *, allow_legacy_shell: bool) -> ReproSpec:
        """Parse a register `reproduce` value. Fail closed on anything unexpected.

        A string is the LEGACY shell form — allowed only when *allow_legacy_shell*
        (the `adopt` profile); rejected otherwise so strict repos cannot run an
        unstructured shell command.
        """
        if isinstance(raw, str):
            if not allow_legacy_shell:
                raise ReproError(
                    "legacy string `reproduce` command is not allowed under this "
                    "profile — use the declarative form (argv + outputs), or set "
                    "allow_legacy_shell under the adopt profile")
            return cls(legacy_shell=raw.strip())
        if not isinstance(raw, dict):
            raise ReproError(f"reproduce must be a string or a mapping, got {type(raw).__name__}")
        argv = raw.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(a, str) for a in argv):
            raise ReproError("reproduce.argv must be a non-empty list of strings")
        outputs_raw = raw.get("outputs") or []
        if not isinstance(outputs_raw, list) or not outputs_raw:
            raise ReproError("reproduce.outputs must be a non-empty list of repo-relative paths")
        outputs: list[str] = []
        for o in outputs_raw:
            try:
                outputs.append(check_relpath(str(o)))
            except PathSafetyError as exc:
                raise ReproError(f"reproduce.outputs entry {o!r} is not a safe relative path: {exc}") from exc
        env_raw = raw.get("environment") or {}
        if not isinstance(env_raw, dict):
            raise ReproError("reproduce.environment must be a mapping of string->string")
        env = tuple((str(k), str(v)) for k, v in env_raw.items())
        timeout = int(raw.get("timeout_seconds", 300))
        if timeout <= 0:
            raise ReproError("reproduce.timeout_seconds must be positive")
        network = str(raw.get("network", "disabled"))
        # Outputs must be referenced by basename via {output_dir} so the runner
        # can map produced files back to committed artifacts unambiguously.
        basenames = [Path(o).name for o in outputs]
        if len(set(basenames)) != len(basenames):
            raise ReproError("reproduce.outputs basenames must be unique")
        return cls(tuple(outputs), tuple(argv), timeout, network, env)


@dataclass
class ReproductionResult:
    """Machine-readable outcome of one reproduction run."""
    ok: bool
    reason: str
    command: str
    outputs: list[str] = field(default_factory=list)
    exit_code: int | None = None
    elapsed_seconds: float = 0.0
    output_sha256: dict[str, str] = field(default_factory=dict)
    env_profile: dict[str, str] = field(default_factory=dict)
    network_requested: str = "disabled"
    network_enforced: bool = False  # honest: this runner does not sandbox network
    stdout_tail: str = ""
    stderr_tail: str = ""

    def to_json(self) -> dict:
        return {
            "schema": "vericlaim_reproduction_v1",
            "ok": self.ok,
            "reason": self.reason,
            "command": self.command,
            "outputs": self.outputs,
            "exit_code": self.exit_code,
            "elapsed_seconds": round(self.elapsed_seconds, 4),
            "output_sha256": self.output_sha256,
            "env_profile": self.env_profile,
            "network_requested": self.network_requested,
            "network_enforced": self.network_enforced,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tail(data: bytes) -> str:
    return data[-_MAX_CAPTURE:].decode("utf-8", "replace")


def run_declarative(cfg: Config, spec: ReproSpec) -> ReproductionResult:
    """Run a declarative spec in an isolated output directory and compare the
    freshly-produced outputs to the committed artifacts. from-scratch or fail."""
    assert not spec.is_legacy
    command = " ".join(spec.argv)
    env = dict(os.environ)
    env.update(dict(spec.environment))
    output_dir = Path(tempfile.mkdtemp(prefix="vericlaim-repro-"))
    try:
        # Substitute {output_dir}. The output dir starts EMPTY, so a no-op
        # command cannot leave a stale artifact behind to pass on.
        argv = [a.replace(_OUTPUT_TOKEN, str(output_dir)) for a in spec.argv]
        start = time.monotonic()
        try:
            # Put the child in its own process GROUP so a timeout can kill the
            # child AND any grandchildren it spawned. POSIX: start_new_session
            # (setsid). Windows: CREATE_NEW_PROCESS_GROUP (killed via taskkill /T).
            group_kwargs: dict = (
                {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                if os.name == "nt" else {"start_new_session": True})
            proc = subprocess.Popen(
                argv, cwd=cfg.root, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                **group_kwargs)
        except FileNotFoundError as exc:
            return ReproductionResult(False, f"command not found: {exc}", command)
        try:
            out, err = proc.communicate(timeout=spec.timeout_seconds)
        except subprocess.TimeoutExpired:
            _kill_group(proc)
            proc.communicate()  # reap
            return ReproductionResult(
                False, f"timed out after {spec.timeout_seconds}s", command,
                elapsed_seconds=time.monotonic() - start)
        elapsed = time.monotonic() - start
        res = ReproductionResult(
            ok=False, reason="", command=command, outputs=list(spec.outputs),
            exit_code=proc.returncode, elapsed_seconds=elapsed,
            env_profile=dict(spec.environment),
            network_requested=spec.network, network_enforced=False,
            stdout_tail=_tail(out or b""), stderr_tail=_tail(err or b""))
        if proc.returncode != 0:
            res.reason = f"command exited {proc.returncode}"
            return res

        # Every declared output must have been CREATED in the empty output
        # dir. Walk RECURSIVELY: a file hidden in a subdirectory is just as
        # undeclared as one at the top level, and a symlink could smuggle in
        # content from outside the isolated directory — both fail.
        produced: dict[str, Path] = {}
        for p in sorted(output_dir.rglob("*")):
            if p.is_symlink():
                res.reason = (f"command created a symlink in the output dir "
                              f"({p.relative_to(output_dir)}) — outputs must "
                              f"be regular files")
                return res
            if p.is_file():
                relname = p.relative_to(output_dir).as_posix()
                produced[relname] = p
        expected_basenames = {Path(o).name for o in spec.outputs}
        extra = set(produced) - expected_basenames
        if extra:
            res.reason = f"command wrote undeclared file(s) in the output dir: {sorted(extra)}"
            return res
        for out in spec.outputs:
            name = Path(out).name
            if name not in produced:
                res.reason = (f"declared output {out} was NOT created from scratch "
                              f"(a no-op or a command that does not write it fails here)")
                return res
            got = produced[name].read_bytes()
            res.output_sha256[out] = _sha256(got)
            committed_path = cfg.path(out)
            if not committed_path.exists():
                res.reason = f"no committed artifact to compare at {out}"
                return res
            committed = committed_path.read_bytes()
            if got != committed:
                res.reason = (f"{out}: freshly-produced output differs from the "
                              f"committed artifact — the committed number is stale "
                              f"or the script is non-deterministic")
                return res
        res.ok = True
        res.reason = "all declared outputs re-created from scratch and byte-identical"
        return res
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def _kill_group(proc: subprocess.Popen) -> None:
    """Kill the timed-out child's whole process group (child + grandchildren).

    POSIX kills the process group via SIGKILL; Windows uses ``taskkill /T`` to
    reach the whole tree (there is no os.killpg on Windows). Either path falls
    back to killing just the child if the group kill is unavailable.
    """
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True)
        except OSError:
            pass
        try:
            proc.kill()
        except OSError:
            pass
        return
    import signal
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except OSError:
            pass
