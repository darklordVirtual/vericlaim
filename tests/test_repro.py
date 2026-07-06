# SPDX-License-Identifier: Apache-2.0
"""Tests for the declarative reproduction oracle (vericlaim.repro).

The central property: a reproduction passes only when every declared output is
CREATED FROM SCRATCH in an empty output dir and matches the committed artifact.
A no-op fails — the weakness of the legacy "artifact unchanged" check.
"""
from __future__ import annotations

import sys

import pytest

from vericlaim.config import Config
from vericlaim.repro import ReproError, ReproSpec, run_declarative


def _cfg(tmp_path):
    return Config(root=tmp_path)


def _write_script(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(body)
    return p


def _spec(argv, outputs, **kw):
    return ReproSpec.parse({"argv": argv, "outputs": outputs, **kw}, allow_legacy_shell=False)


# ── spec parsing / profile ──────────────────────────────────────────────────

def test_legacy_string_rejected_in_strict():
    with pytest.raises(ReproError):
        ReproSpec.parse("python bench.py", allow_legacy_shell=False)


def test_legacy_string_allowed_when_permitted():
    spec = ReproSpec.parse("python bench.py", allow_legacy_shell=True)
    assert spec.is_legacy and spec.legacy_shell == "python bench.py"


def test_declarative_requires_argv_and_outputs():
    with pytest.raises(ReproError):
        ReproSpec.parse({"outputs": ["a.json"]}, allow_legacy_shell=False)
    with pytest.raises(ReproError):
        ReproSpec.parse({"argv": ["python"]}, allow_legacy_shell=False)


def test_unsafe_output_path_rejected():
    with pytest.raises(ReproError):
        ReproSpec.parse({"argv": ["x"], "outputs": ["../escape.json"]}, allow_legacy_shell=False)


# ── the runner ──────────────────────────────────────────────────────────────

def test_deterministic_output_passes(tmp_path):
    _write_script(tmp_path, "gen.py",
                  "import sys,pathlib\n"
                  "pathlib.Path(sys.argv[1], 'r.json').write_text('{\"n\": 1}')\n")
    (tmp_path / "r.json").write_text('{"n": 1}')
    spec = _spec([sys.executable, "gen.py", "{output_dir}"], ["r.json"])
    res = run_declarative(_cfg(tmp_path), spec)
    assert res.ok, res.reason
    assert res.output_sha256["r.json"]


def test_noop_command_fails(tmp_path):
    """The whole point: a command that writes nothing fails, even though the
    committed artifact is present and unchanged."""
    _write_script(tmp_path, "noop.py", "pass\n")
    (tmp_path / "r.json").write_text('{"n": 1}')
    spec = _spec([sys.executable, "noop.py", "{output_dir}"], ["r.json"])
    res = run_declarative(_cfg(tmp_path), spec)
    assert not res.ok
    assert "not created from scratch" in res.reason.lower() or "no-op" in res.reason.lower()


def test_stale_committed_artifact_fails(tmp_path):
    _write_script(tmp_path, "gen.py",
                  "import sys,pathlib\n"
                  "pathlib.Path(sys.argv[1], 'r.json').write_text('{\"n\": 2}')\n")
    (tmp_path / "r.json").write_text('{"n": 1}')  # committed value is stale
    spec = _spec([sys.executable, "gen.py", "{output_dir}"], ["r.json"])
    res = run_declarative(_cfg(tmp_path), spec)
    assert not res.ok and "stale" in res.reason.lower()


def test_nondeterministic_output_fails(tmp_path):
    _write_script(tmp_path, "gen.py",
                  "import sys,pathlib,random\n"
                  "pathlib.Path(sys.argv[1], 'r.json').write_text(str(random.random()))\n")
    (tmp_path / "r.json").write_text("0.5")
    spec = _spec([sys.executable, "gen.py", "{output_dir}"], ["r.json"])
    res = run_declarative(_cfg(tmp_path), spec)
    assert not res.ok


def test_undeclared_file_fails(tmp_path):
    _write_script(tmp_path, "gen.py",
                  "import sys,pathlib\n"
                  "d=pathlib.Path(sys.argv[1])\n"
                  "(d/'r.json').write_text('{}')\n(d/'sneaky.txt').write_text('x')\n")
    (tmp_path / "r.json").write_text("{}")
    spec = _spec([sys.executable, "gen.py", "{output_dir}"], ["r.json"])
    res = run_declarative(_cfg(tmp_path), spec)
    assert not res.ok and "undeclared" in res.reason.lower()


def test_missing_output_fails(tmp_path):
    _write_script(tmp_path, "gen.py",
                  "import sys,pathlib\n"
                  "pathlib.Path(sys.argv[1], 'other.json').write_text('{}')\n")
    (tmp_path / "r.json").write_text("{}")
    spec = _spec([sys.executable, "gen.py", "{output_dir}"], ["r.json"])
    res = run_declarative(_cfg(tmp_path), spec)
    assert not res.ok


def test_nonzero_exit_fails(tmp_path):
    _write_script(tmp_path, "boom.py", "import sys; sys.exit(3)\n")
    (tmp_path / "r.json").write_text("{}")
    spec = _spec([sys.executable, "boom.py", "{output_dir}"], ["r.json"])
    res = run_declarative(_cfg(tmp_path), spec)
    assert not res.ok and res.exit_code == 3


def test_timeout_kills_and_fails(tmp_path):
    _write_script(tmp_path, "slow.py", "import time; time.sleep(30)\n")
    (tmp_path / "r.json").write_text("{}")
    spec = _spec([sys.executable, "slow.py", "{output_dir}"], ["r.json"], timeout_seconds=1)
    res = run_declarative(_cfg(tmp_path), spec)
    assert not res.ok and "timed out" in res.reason.lower()


def test_command_not_found_fails(tmp_path):
    spec = _spec(["definitely-not-a-real-binary-xyz", "{output_dir}"], ["r.json"])
    res = run_declarative(_cfg(tmp_path), spec)
    assert not res.ok and "not found" in res.reason.lower()


def test_temp_workspace_is_cleaned_up(tmp_path):
    import tempfile
    before = set(pathlib_tmp())
    _write_script(tmp_path, "gen.py",
                  "import sys,pathlib\npathlib.Path(sys.argv[1],'r.json').write_text('{}')\n")
    (tmp_path / "r.json").write_text("{}")
    run_declarative(_cfg(tmp_path), _spec([sys.executable, "gen.py", "{output_dir}"], ["r.json"]))
    after = set(pathlib_tmp())
    leaked = [d for d in (after - before) if "vericlaim-repro-" in d]
    assert not leaked, f"leaked temp dirs: {leaked}"
    _ = tempfile  # keep import used


def pathlib_tmp():
    import glob
    import tempfile
    return glob.glob(str(tempfile.gettempdir()) + "/vericlaim-repro-*")


def test_result_json_shape(tmp_path):
    _write_script(tmp_path, "gen.py",
                  "import sys,pathlib\npathlib.Path(sys.argv[1],'r.json').write_text('{}')\n")
    (tmp_path / "r.json").write_text("{}")
    res = run_declarative(_cfg(tmp_path), _spec([sys.executable, "gen.py", "{output_dir}"], ["r.json"]))
    j = res.to_json()
    assert j["schema"] == "vericlaim_reproduction_v1"
    assert j["network_enforced"] is False  # honest: not sandboxed
    assert "output_sha256" in j
