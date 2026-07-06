# SPDX-License-Identifier: Apache-2.0
"""Regression tests for the bundle DOWNLOAD path-traversal fix (P0-2).

fetch_bundle.py used to write manifest paths directly (`bdir / rel`) BEFORE
verifying, so a malicious/compromised library response could write outside the
bundle root with '../', absolute paths, backslashes, or a Windows drive prefix.
The fix validates the bundle id, stages in a private temp dir, safe-joins every
manifest path before writing, verifies, then atomically moves into place.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "integrations" / "library"))
import fetch_bundle  # noqa: E402

_VALID_ID = "a" * 64  # strict sha256 hex


def _serve(monkeypatch, manifest: dict):
    """Monkeypatch the network so _get returns our crafted bundle meta / files."""
    def fake_get(url: str) -> bytes:
        if "/library/bundle/" in url:
            return json.dumps({"manifest": manifest}).encode()
        return b"malicious-bytes"
    monkeypatch.setattr(fetch_bundle, "_get", fake_get)


def _manifest(files: dict) -> dict:
    return {"schema": "bundle_v1", "status": "verified", "files": files}


@pytest.mark.parametrize("evil", [
    "../escape.json",
    "../../escape.json",
    "/etc/passwd",
    "sub/../../escape.json",
    "a\\..\\..\\escape.json",  # backslash traversal
    "C:\\Windows\\evil.json",  # windows drive
])
def test_malicious_manifest_path_is_refused_before_writing(tmp_path, monkeypatch, evil):
    _serve(monkeypatch, _manifest({evil: "b" * 64}))
    out_root = tmp_path / "out"
    with pytest.raises((ValueError,)):
        fetch_bundle.fetch("https://example.invalid", _VALID_ID, out_root)
    # Nothing may have been written outside the intended bundle dir.
    assert not (tmp_path / "escape.json").exists()
    assert not (tmp_path.parent / "escape.json").exists()
    assert not (out_root.parent / "escape.json").exists()


def test_invalid_bundle_id_is_refused(tmp_path, monkeypatch):
    _serve(monkeypatch, _manifest({"claim.json": "c" * 64}))
    with pytest.raises(ValueError):
        fetch_bundle.fetch("https://example.invalid", "../evil", tmp_path / "out")
    with pytest.raises(ValueError):
        fetch_bundle.fetch("https://example.invalid", "not-hex", tmp_path / "out")


def test_missing_manifest_files_is_refused(tmp_path, monkeypatch):
    def fake_get(url: str) -> bytes:
        if "/library/bundle/" in url:
            return json.dumps({"manifest": {"schema": "bundle_v1"}}).encode()
        return b"x"
    monkeypatch.setattr(fetch_bundle, "_get", fake_get)
    with pytest.raises(ValueError):
        fetch_bundle.fetch("https://example.invalid", _VALID_ID, tmp_path / "out")
