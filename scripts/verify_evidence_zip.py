#!/usr/bin/env python3
"""Verify ZIP container safety; this is not scientific evidence validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sha256", dest="expected_sha256")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    members: list[str] = []
    archive_hash = ""
    try:
        archive = args.archive.resolve(strict=True)
        archive_hash = file_sha256(archive)
        if args.expected_sha256 and archive_hash.lower() != args.expected_sha256.lower():
            errors.append("archive SHA-256 does not match the explicit expected value")
        with zipfile.ZipFile(archive) as package:
            infos = package.infolist()
            names = [info.filename for info in infos]
            members = names
            seen: set[str] = set()
            folded: dict[str, str] = {}
            roots: set[str] = set()
            for info in infos:
                name = info.filename
                if name in seen:
                    errors.append(f"duplicate member: {name}")
                seen.add(name)
                if "\\" in name:
                    errors.append(f"backslash path ambiguity: {name}")
                path = PurePosixPath(name)
                windows_path = PureWindowsPath(name)
                if path.is_absolute() or windows_path.is_absolute() or name.startswith(("/", "\\")):
                    errors.append(f"absolute member path: {name}")
                if ".." in path.parts or ".." in windows_path.parts:
                    errors.append(f"parent traversal: {name}")
                safe_parts = [part for part in path.parts if part not in ("", ".")]
                if safe_parts:
                    roots.add(safe_parts[0].casefold())
                normalized = "/".join(part.rstrip(" .").casefold() for part in safe_parts)
                previous = folded.get(normalized)
                if previous is not None and previous != name:
                    errors.append(f"case-fold or Windows path collision: {previous} <> {name}")
                folded[normalized] = name
                mode = info.external_attr >> 16
                file_type = stat.S_IFMT(mode)
                if file_type == stat.S_IFLNK:
                    errors.append(f"symlink member: {name}")
                elif file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                    errors.append(f"special member: {name}")
            if len(roots) != 1:
                errors.append(f"members do not share one logical package root: {sorted(roots)}")
    except (OSError, zipfile.BadZipFile) as error:
        errors.append(str(error))
    result = {
        "schema": "aletheia.evidence-zip-container-safety.v1",
        "archive": str(args.archive), "sha256": archive_hash, "members": len(members),
        "scope": "container-safety-only-not-scientific-validation",
        "state": "PASS" if not errors else "FAIL", "errors": errors,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
