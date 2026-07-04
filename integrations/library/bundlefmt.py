# SPDX-License-Identifier: Apache-2.0
"""The claim-bundle format — the library's unit of preservation.

A bundle is a self-contained, content-addressed directory:

    <bundle_id>/
      claim.json          the claim in vericlaim schema (mapped level, extended caveat)
      provenance.json     source repo+commit, source gate status, mapping decision
      MANIFEST.json       sha256 per file; bundle_id = sha256(canonical manifest)
      artifacts/ code/ literature/    byte-exact payload files

The bundle_id is the sha256 of the canonical manifest (sorted keys, no
whitespace variance), which itself lists the sha256 of every file — so the id
commits to every byte, and any change is a *new* bundle. Verification is
fail-closed: tampered, missing, extra, or re-labeled content raises.

Stdlib only, offline — the library distributes bundles, but trust comes from
verifying them locally, never from where they were fetched.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCHEMA = "bundle_v1"
_META = ("claim.json", "provenance.json")


class BundleError(ValueError):
    """The bundle does not verify. Fail closed: do not use its contents."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _manifest_dict(files: dict[str, str], status: str) -> dict:
    return {"schema": SCHEMA, "status": status, "files": files}


def _bundle_id(files: dict[str, str], status: str) -> str:
    return _sha256(_canonical(_manifest_dict(files, status)))


def build_bundle(out_root: Path, *, claim: dict, provenance: dict,
                 files: dict[str, bytes], status: str = "verified") -> tuple[str, Path]:
    """Write a bundle under *out_root*/<bundle_id>/ and return (id, dir).

    *files* maps bundle-relative paths (artifacts/..., code/..., literature/...)
    to their exact bytes. claim.json and provenance.json are serialized
    canonically so the same logical content always yields the same id.
    """
    payload = dict(files)
    payload["claim.json"] = _canonical(claim)
    payload["provenance.json"] = _canonical(provenance)
    hashes = {rel: _sha256(data) for rel, data in payload.items()}
    bid = _bundle_id(hashes, status)

    bdir = Path(out_root) / bid
    bdir.mkdir(parents=True, exist_ok=True)
    for rel, data in payload.items():
        dest = bdir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    (bdir / "MANIFEST.json").write_text(
        json.dumps(_manifest_dict(hashes, status), sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    return bid, bdir


def _load_manifest(bdir: Path) -> dict:
    mpath = bdir / "MANIFEST.json"
    if not mpath.exists():
        raise BundleError(f"{bdir.name}: MANIFEST.json missing")
    try:
        man = json.loads(mpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BundleError(f"{bdir.name}: MANIFEST.json is not valid JSON: {exc}") from exc
    if man.get("schema") != SCHEMA or not isinstance(man.get("files"), dict):
        raise BundleError(f"{bdir.name}: unsupported or malformed manifest")
    return man


def bundle_id_of(bdir: Path) -> str:
    """The id implied by the manifest on disk (not the directory name)."""
    man = _load_manifest(Path(bdir))
    return _bundle_id(man["files"], man.get("status", "verified"))


def verify_bundle(bdir: Path) -> dict:
    """Fail-closed verification: every byte matches the manifest, the manifest
    matches the id, and the id matches the directory name. Returns a report."""
    bdir = Path(bdir)
    man = _load_manifest(bdir)
    files: dict[str, str] = man["files"]
    for rel in _META:
        if rel not in files:
            raise BundleError(f"{bdir.name}: manifest does not list {rel}")
    for rel, expected in sorted(files.items()):
        p = bdir / rel
        if not p.is_file():
            raise BundleError(f"{bdir.name}: listed file missing: {rel}")
        actual = _sha256(p.read_bytes())
        if actual != expected:
            raise BundleError(
                f"{bdir.name}: {rel} does not match its manifested sha256 "
                f"(content was altered after the bundle was built)")
    on_disk = {p.relative_to(bdir).as_posix()
               for p in bdir.rglob("*") if p.is_file()}
    extra = on_disk - set(files) - {"MANIFEST.json"}
    if extra:
        raise BundleError(
            f"{bdir.name}: files present but not in manifest: {sorted(extra)} "
            f"— a bundle's content is exactly its manifest, nothing more")
    bid = _bundle_id(files, man.get("status", "verified"))
    if bdir.name != bid:
        raise BundleError(
            f"{bdir.name}: directory name does not equal the content bundle_id "
            f"{bid} — a bundle cannot be re-labeled")
    return {"ok": True, "bundle_id": bid, "status": man.get("status", "verified"),
            "n_files": len(files)}


def load_bundle(bdir: Path) -> dict:
    """Verify, then return the parsed claim/provenance and the manifest."""
    report = verify_bundle(bdir)
    bdir = Path(bdir)
    return {
        "bundle_id": report["bundle_id"],
        "status": report["status"],
        "claim": json.loads((bdir / "claim.json").read_text(encoding="utf-8")),
        "provenance": json.loads((bdir / "provenance.json").read_text(encoding="utf-8")),
        "manifest": _load_manifest(bdir),
    }
