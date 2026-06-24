"""Source manifest loading and integrity checks."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


def load_source_manifest(project_root: Path) -> dict[str, Any]:
    """Load the source manifest from the project."""
    path = project_root / "data" / "sources" / "source_manifest.yaml"
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if payload.get("schema") != "realizing_emptiness.source_manifest.v1":
        raise ValueError("source manifest schema mismatch")
    return payload


def sha256_file(path: Path) -> str:
    """Compute SHA-256 for a local file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_primary_source_hash(project_root: Path) -> dict[str, Any]:
    """Verify the attached PDF hash when the local source file is present."""
    manifest = load_source_manifest(project_root)
    source = manifest["primary_source"]
    pdf_path = Path(source["local_pdf"])
    if not pdf_path.is_absolute():
        pdf_path = project_root / pdf_path
    expected = source["sha256"]
    exists = pdf_path.exists()
    actual = sha256_file(pdf_path) if exists else None
    return {
        "schema": "realizing_emptiness.source_hash_check.v1",
        "path": str(pdf_path),
        "exists": exists,
        "expected_sha256": expected,
        "actual_sha256": actual,
        "ok": bool(exists and actual == expected),
    }

