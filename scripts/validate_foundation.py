#!/usr/bin/env python3
"""Validate the Aletheia ADR foundation using only the Python standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "docs" / "adr"
KIDNEY = ROOT / "modules" / "kidney" / "docs" / "adr"
MANIFEST_REL = PurePosixPath("evidence/foundation-v01/MANIFEST.json")

EXPECTED_CORE = {
    f"{number:04d}" for number in range(17)
}
EXPECTED_KIDNEY = {
    f"{number:04d}" for number in range(1, 9)
}
REQUIRED_FILES = {
    "README.md",
    "GOVERNANCE.md",
    "ARCHITECTURE.md",
    "docs/adr/README.md",
    "docs/architecture/FEDERATION-MODEL.md",
    "docs/architecture/COMPATIBILITY-MODEL.md",
    "contracts/README.md",
    "contracts/VERSIONING.md",
    "schemas/README.md",
    "evidence-packages/README.md",
    "control-planes/README.md",
    "scripts/validate_foundation.py",
}
FORBIDDEN_DATA_SUFFIXES = (
    ".h5ad",
    ".h5ad.gz",
    ".mtx",
    ".mtx.gz",
    ".tsv",
    ".tsv.gz",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts or path.is_symlink() or not path.is_file():
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def manifest_records() -> list[dict[str, object]]:
    records = []
    for path in repository_files():
        relative = PurePosixPath(path.relative_to(ROOT).as_posix())
        if relative == MANIFEST_REL:
            continue
        records.append(
            {
                "path": relative.as_posix(),
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return records


def manifest_document() -> dict[str, object]:
    return {
        "schema": "aletheia.foundation-manifest.v1",
        "algorithm": "sha256",
        "exclusions": [".git/", MANIFEST_REL.as_posix()],
        "files": manifest_records(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--verify-manifest", type=Path)
    args = parser.parse_args()

    checks: list[dict[str, object]] = []
    errors: list[str] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            errors.append(f"{name}: {detail}")

    core_files = sorted(path for path in CORE.glob("*.md") if path.name != "README.md")
    kidney_files = sorted(path for path in KIDNEY.glob("*.md") if path.name != "README.md")
    all_adrs = core_files + kidney_files

    check("core_adr_count", len(core_files) == 17, len(core_files))
    check("kidney_adr_count", len(kidney_files) == 8, len(kidney_files))
    check("total_adr_count", len(all_adrs) == 25, len(all_adrs))
    core_ids = {path.name[:4] for path in core_files}
    kidney_ids = {path.name[:4] for path in kidney_files}
    check("core_ids_complete", core_ids == EXPECTED_CORE, sorted(core_ids))
    check("kidney_ids_complete", kidney_ids == EXPECTED_KIDNEY, sorted(kidney_ids))

    title_ids: list[str] = []
    statuses: dict[str, str] = {}
    for path in all_adrs:
        text = path.read_text(encoding="utf-8")
        title = re.search(r"^# (ADR-(?:KR-)?\d{4})\b", text, re.MULTILINE)
        status = re.search(r"^- \*\*Status:\*\* ([A-Za-z]+)\s*$", text, re.MULTILINE)
        check(f"title:{path.name}", title is not None, "ADR identifier in title")
        check(f"decision:{path.name}", "## Decision" in text, "Decision section")
        check(f"status:{path.name}", status is not None, "status metadata")
        if title:
            title_ids.append(title.group(1))
            if status:
                statuses[title.group(1)] = status.group(1)

    check("adr_ids_unique", len(title_ids) == len(set(title_ids)), title_ids)
    check("adr_0016_accepted", statuses.get("ADR-0016") == "Accepted", statuses.get("ADR-0016"))
    accepted = sorted(identifier for identifier, status in statuses.items() if status == "Accepted")
    check("only_adr_0016_accepted", accepted == ["ADR-0016"], accepted)
    unexpected_status = sorted(
        identifier
        for identifier, status in statuses.items()
        if identifier != "ADR-0016" and status != "Proposed"
    )
    check("other_adrs_remain_proposed", not unexpected_status, unexpected_status)

    adr_0016 = next((path for path in core_files if path.name.startswith("0016-")), None)
    safeguard_terms = {
        "own_repository": "has its own repository",
        "independent_control_planes": "control planes remain in independent repositories",
        "versioned_contracts": "explicitly versioned contracts",
        "versioned_schemas": "explicitly versioned schemas",
        "versioned_evidence_packages": "evidence packages are versioned",
        "no_mutable_main": "depend implicitly on mutable `main`",
        "no_cross_repo_mutation": "may not mutate a federated repository automatically",
        "compatibility_matrix": "compatibility matrix is required",
        "explicit_migration": "explicit migration mission",
        "no_primary_submodules": "git submodules are not the primary integration mechanism",
    }
    adr_0016_text = adr_0016.read_text(encoding="utf-8").lower() if adr_0016 else ""
    for name, phrase in safeguard_terms.items():
        check(f"adr_0016_safeguard:{name}", phrase in adr_0016_text, phrase)

    for relative in sorted(REQUIRED_FILES):
        check(f"required:{relative}", (ROOT / relative).is_file(), relative)

    all_paths = list(ROOT.rglob("*"))
    unexpected_symlinks = sorted(
        path.relative_to(ROOT).as_posix() for path in all_paths if ".git" not in path.relative_to(ROOT).parts and path.is_symlink()
    )
    check("no_unexpected_symlinks", not unexpected_symlinks, unexpected_symlinks)

    forbidden_data = sorted(
        path.relative_to(ROOT).as_posix()
        for path in repository_files()
        if path.name.lower().endswith(FORBIDDEN_DATA_SUFFIXES)
    )
    check("no_expression_data", not forbidden_data, forbidden_data)

    kidney_tree = ROOT / "modules" / "kidney"
    embedded_git = sorted(path.relative_to(ROOT).as_posix() for path in kidney_tree.rglob(".git"))
    unexpected_kidney_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in kidney_tree.rglob("*")
        if path.is_file() and path.suffix.lower() != ".md"
    )
    check("no_embedded_kidney_repository", not embedded_git, embedded_git)
    check("kidney_module_docs_only", not unexpected_kidney_files, unexpected_kidney_files)

    invalid_utf8 = []
    all_text_parts = []
    for path in repository_files():
        try:
            all_text_parts.append(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            invalid_utf8.append(path.relative_to(ROOT).as_posix())
    check("utf8_valid", not invalid_utf8, invalid_utf8)
    combined_text = "\n".join(all_text_parts)
    review_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in repository_files()
        if path.suffix.lower() in {".md", ".json"}
    )
    merge_markers = [marker for marker in ("<<<<<<<", "=======", ">>>>>>>") if marker in review_text]
    check("no_merge_markers", not merge_markers, merge_markers)

    broken_links = []
    absolute_links = []
    markdown_link = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for path in (item for item in repository_files() if item.suffix.lower() == ".md"):
        for raw_target in markdown_link.findall(path.read_text(encoding="utf-8")):
            target = unquote(raw_target.strip().split()[0].strip("<>"))
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target_path = target.split("#", 1)[0]
            if target_path.startswith("/"):
                absolute_links.append(f"{path.relative_to(ROOT)} -> {target}")
                continue
            resolved = (path.parent / target_path).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                broken_links.append(f"{path.relative_to(ROOT)} -> {target}")
                continue
            if not resolved.exists():
                broken_links.append(f"{path.relative_to(ROOT)} -> {target}")
    check("no_absolute_local_links", not absolute_links, absolute_links)
    check("local_links_resolve", not broken_links, broken_links)

    prohibited_claims = [
        phrase
        for phrase in ("cure proven", "clinically validated", "fully validated")
        if phrase in review_text.lower()
    ]
    check("no_unsupported_claims", not prohibited_claims, prohibited_claims)

    register_path = ROOT / "ADR-REGISTER.json"
    try:
        register = json.loads(register_path.read_text(encoding="utf-8"))
        records = register["records"]
        check("register_record_count", len(records) == 25, len(records))
        register_status = {record["path"]: record["status"] for record in records}
        register_hash = {record["path"]: record["sha256"] for record in records}
        mismatched_hashes = []
        for path in all_adrs:
            relative = path.relative_to(ROOT).as_posix()
            if register_hash.get(relative) != sha256(path):
                mismatched_hashes.append(relative)
        check("register_hashes_match", not mismatched_hashes, mismatched_hashes)
        accepted_records = sorted(path for path, status in register_status.items() if status == "Accepted")
        check(
            "register_only_adr_0016_accepted",
            accepted_records == ["docs/adr/0016-repository-topology-and-module-integration-model.md"],
            accepted_records,
        )
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        check("register_readable", False, error)

    first_manifest = json.dumps(manifest_document(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    second_manifest = json.dumps(manifest_document(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    check("manifest_deterministic", first_manifest == second_manifest, "two independent renders")

    if args.verify_manifest:
        try:
            expected_manifest = json.loads(args.verify_manifest.read_text(encoding="utf-8"))
            actual_manifest = manifest_document()
            check("manifest_verifies", expected_manifest == actual_manifest, args.verify_manifest)
        except (OSError, json.JSONDecodeError) as error:
            check("manifest_verifies", False, error)

    result = {
        "schema": "aletheia.foundation-validation.v1",
        "state": "PASS" if not errors else "FAIL",
        "adr_count": len(all_adrs),
        "checks": checks,
        "errors": errors,
    }

    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.write_manifest:
        output = args.write_manifest if args.write_manifest.is_absolute() else ROOT / args.write_manifest
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(first_manifest, encoding="utf-8")

    summary = {"state": result["state"], "checks": len(checks), "errors": len(errors), "adrs": len(all_adrs)}
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
