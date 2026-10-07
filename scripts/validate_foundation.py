#!/usr/bin/env python3
"""Validate the Aletheia ADR foundation using only the Python standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import unquote


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
FOUNDATION_MANIFEST_REL = PurePosixPath("evidence/foundation-v01/MANIFEST.json")
HARDENING_MANIFEST_REL = PurePosixPath("evidence/hardening/foundation-v01/MANIFEST.json")
CONTRACT_MANIFEST_REL = PurePosixPath("evidence/contracts/rcp-descriptor-v0.1.0/MANIFEST.json")
MANIFEST_EXCLUSIONS = {FOUNDATION_MANIFEST_REL, HARDENING_MANIFEST_REL, CONTRACT_MANIFEST_REL}
EXPECTED_CORE = {f"{number:04d}" for number in range(18)}
EXPECTED_KIDNEY = {f"{number:04d}" for number in range(1, 9)}
REQUIRED_FILES = {
    "README.md", "GOVERNANCE.md", "ARCHITECTURE.md", "docs/adr/README.md",
    "docs/architecture/FEDERATION-MODEL.md", "docs/architecture/COMPATIBILITY-MODEL.md",
    "docs/security/FOUNDATION-HARDENING-MODEL.md",
    "docs/security/FOUNDATION-HARDENING-ATTACK-MATRIX.md", "contracts/README.md",
    "contracts/VERSIONING.md", "schemas/README.md", "evidence-packages/README.md",
    "control-planes/README.md", "scripts/validate_foundation.py",
    "scripts/validate_accepted_adr_history.py", "scripts/verify_evidence_zip.py",
    "tests/foundation-hardening/run_foundation_hardening.py",
}
FORBIDDEN_DATA_SUFFIXES = (
    ".h5ad", ".h5ad.gz", ".loom", ".mtx", ".mtx.gz", ".fastq",
    ".fastq.gz", ".fq", ".fq.gz", ".bam", ".cram", ".rds",
)
WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul", *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_paths(root: Path) -> list[Path]:
    paths = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if ".git" in relative.parts or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(root).as_posix())


def repository_files(root: Path) -> list[Path]:
    return [path for path in repository_paths(root) if not path.is_symlink() and path.is_file()]


def manifest_records(root: Path) -> list[dict[str, object]]:
    records = []
    for path in repository_files(root):
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if relative in MANIFEST_EXCLUSIONS:
            continue
        records.append({"path": relative.as_posix(), "size": path.stat().st_size, "sha256": sha256(path)})
    return records


def manifest_document(root: Path, schema: str = "aletheia.foundation-manifest.v1") -> dict[str, object]:
    return {
        "schema": schema,
        "algorithm": "sha256",
        "exclusions": [".git/", "**/__pycache__/", "*.pyc", *sorted(path.as_posix() for path in MANIFEST_EXCLUSIONS)],
        "files": manifest_records(root),
    }


def is_windows_absolute(target: str) -> bool:
    return PureWindowsPath(target).is_absolute() or target.startswith(("\\\\", "//"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, help="physical foundation root to validate")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--verify-manifest", type=Path)
    parser.add_argument("--manifest-schema", default="aletheia.foundation-manifest.v1")
    args = parser.parse_args()
    try:
        root = (args.root or SCRIPT_ROOT).resolve(strict=True)
    except OSError as error:
        print(json.dumps({"state": "FAIL", "error": f"invalid root: {error}"}, sort_keys=True), file=sys.stderr)
        return 2
    if not root.is_dir():
        print(json.dumps({"state": "FAIL", "error": "root is not a directory"}, sort_keys=True), file=sys.stderr)
        return 2

    core = root / "docs" / "adr"
    kidney = root / "modules" / "kidney" / "docs" / "adr"
    checks: list[dict[str, object]] = []
    errors: list[str] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            errors.append(f"{name}: {detail}")

    core_files = sorted(path for path in core.glob("*.md") if path.name != "README.md")
    kidney_files = sorted(path for path in kidney.glob("*.md") if path.name != "README.md")
    all_adrs = core_files + kidney_files
    check("core_adr_count", len(core_files) == 18, len(core_files))
    check("kidney_adr_count", len(kidney_files) == 8, len(kidney_files))
    check("total_adr_count", len(all_adrs) == 26, len(all_adrs))
    core_ids = {path.name[:4] for path in core_files}
    kidney_ids = {path.name[:4] for path in kidney_files}
    check("core_ids_complete", core_ids == EXPECTED_CORE, sorted(core_ids))
    check("kidney_ids_complete", kidney_ids == EXPECTED_KIDNEY, sorted(kidney_ids))

    title_ids: list[str] = []
    statuses: dict[str, str] = {}
    for path in all_adrs:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = ""
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
    check("adr_0017_accepted", statuses.get("ADR-0017") == "Accepted", statuses.get("ADR-0017"))
    accepted = sorted(identifier for identifier, status in statuses.items() if status == "Accepted")
    check("accepted_set_exact", accepted == ["ADR-0016", "ADR-0017"], accepted)
    unexpected_status = sorted(identifier for identifier, status in statuses.items() if identifier not in {"ADR-0016", "ADR-0017"} and status != "Proposed")
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
    try:
        adr_0016_text = adr_0016.read_text(encoding="utf-8").lower() if adr_0016 else ""
    except UnicodeDecodeError:
        adr_0016_text = ""
    for name, phrase in safeguard_terms.items():
        check(f"adr_0016_safeguard:{name}", phrase in adr_0016_text, phrase)
    for relative in sorted(REQUIRED_FILES):
        check(f"required:{relative}", (root / relative).is_file(), relative)

    all_paths = repository_paths(root)
    unexpected_symlinks = sorted(path.relative_to(root).as_posix() for path in all_paths if path.is_symlink())
    check("no_unexpected_symlinks", not unexpected_symlinks, unexpected_symlinks)
    relative_paths = [path.relative_to(root).as_posix() for path in all_paths]
    folded: dict[str, list[str]] = {}
    trailing_components = []
    reserved_components = []
    for relative in relative_paths:
        normalized_parts = []
        for component in PurePosixPath(relative).parts:
            if component.endswith((".", " ")):
                trailing_components.append(relative)
            trimmed = component.rstrip(" .")
            stem = trimmed.split(".", 1)[0].casefold()
            if stem in WINDOWS_RESERVED:
                reserved_components.append(relative)
            normalized_parts.append(trimmed.casefold())
        folded.setdefault("/".join(normalized_parts), []).append(relative)
    casefold_collisions = sorted(values for values in folded.values() if len(set(values)) > 1)
    check("no_casefold_path_collisions", not casefold_collisions, casefold_collisions)
    check("no_windows_reserved_paths", not reserved_components, sorted(set(reserved_components)))
    check("no_trailing_dot_or_space_paths", not trailing_components, sorted(set(trailing_components)))

    forbidden_data = sorted(path.relative_to(root).as_posix() for path in repository_files(root) if path.name.lower().endswith(FORBIDDEN_DATA_SUFFIXES))
    check("no_raw_biomedical_payloads", not forbidden_data, forbidden_data)
    kidney_tree = root / "modules" / "kidney"
    embedded_git = sorted(path.relative_to(root).as_posix() for path in kidney_tree.rglob(".git")) if kidney_tree.exists() else []
    unexpected_kidney_files = sorted(path.relative_to(root).as_posix() for path in kidney_tree.rglob("*") if path.is_file() and path.suffix.lower() != ".md") if kidney_tree.exists() else []
    check("no_embedded_kidney_repository", not embedded_git, embedded_git)
    check("kidney_module_docs_only", not unexpected_kidney_files, unexpected_kidney_files)

    invalid_utf8 = []
    readable_text: dict[Path, str] = {}
    for path in repository_files(root):
        try:
            readable_text[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            invalid_utf8.append(path.relative_to(root).as_posix())
    check("utf8_valid", not invalid_utf8, invalid_utf8)
    review_text = "\n".join(text for path, text in readable_text.items() if path.suffix.lower() in {".md", ".json"})
    markdown_text = "\n".join(text for path, text in readable_text.items() if path.suffix.lower() == ".md")
    merge_markers = [marker for marker in ("<<<<<<<", "=======", ">>>>>>>") if marker in markdown_text]
    check("no_merge_markers", not merge_markers, merge_markers)

    broken_links = []
    absolute_links = []
    markdown_link = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for path, text in readable_text.items():
        if path.suffix.lower() != ".md":
            continue
        for raw_target in markdown_link.findall(text):
            target = unquote(raw_target.strip().split()[0].strip("<>"))
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target_path = target.split("#", 1)[0]
            if Path(target_path).is_absolute() or is_windows_absolute(target_path):
                absolute_links.append(f"{path.relative_to(root)} -> {target}")
                continue
            portable_target = target_path.replace("\\", "/")
            resolved = (path.parent / portable_target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                broken_links.append(f"{path.relative_to(root)} -> {target}")
                continue
            if not resolved.exists():
                broken_links.append(f"{path.relative_to(root)} -> {target}")
    check("no_absolute_local_links", not absolute_links, absolute_links)
    check("local_links_resolve", not broken_links, broken_links)
    prohibited_claims = [phrase for phrase in ("cure proven", "clinically validated", "fully validated") if phrase in review_text.lower()]
    check("no_unsupported_claims", not prohibited_claims, prohibited_claims)

    register_path = root / "ADR-REGISTER.json"
    try:
        register = json.loads(register_path.read_text(encoding="utf-8"))
        records = register["records"]
        check("register_record_count", len(records) == 26, len(records))
        register_status = {record["path"]: record["status"] for record in records}
        register_hash = {record["path"]: record["sha256"] for record in records}
        mismatched_hashes = []
        for path in all_adrs:
            relative = path.relative_to(root).as_posix()
            if register_hash.get(relative) != sha256(path):
                mismatched_hashes.append(relative)
        check("register_hashes_match", not mismatched_hashes, mismatched_hashes)
        accepted_records = sorted(path for path, status in register_status.items() if status == "Accepted")
        check("register_accepted_set_exact", accepted_records == ["docs/adr/0016-repository-topology-and-module-integration-model.md", "docs/adr/0017-adversarial-hardening-and-qualification-model.md"], accepted_records)
        path_0017 = "docs/adr/0017-adversarial-hardening-and-qualification-model.md"
        check("register_adr_0017_accepted", register_status.get(path_0017) == "Accepted", register_status.get(path_0017))
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        check("register_readable", False, error)

    first_manifest = json.dumps(manifest_document(root, args.manifest_schema), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    second_manifest = json.dumps(manifest_document(root, args.manifest_schema), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    check("manifest_deterministic", first_manifest == second_manifest, "two independent renders")
    if args.verify_manifest:
        manifest_path = args.verify_manifest if args.verify_manifest.is_absolute() else root / args.verify_manifest
        try:
            expected_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            actual_manifest = manifest_document(root, expected_manifest.get("schema", args.manifest_schema))
            check("manifest_verifies", expected_manifest == actual_manifest, manifest_path)
        except (OSError, AttributeError, json.JSONDecodeError) as error:
            check("manifest_verifies", False, error)

    result = {"schema": "aletheia.foundation-validation.v1", "state": "PASS" if not errors else "FAIL", "root": str(root), "adr_count": len(all_adrs), "checks": checks, "errors": errors}
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.write_manifest:
        output = args.write_manifest if args.write_manifest.is_absolute() else root / args.write_manifest
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(first_manifest, encoding="utf-8")
    print(json.dumps({"state": result["state"], "checks": len(checks), "errors": len(errors), "adrs": len(all_adrs), "root": str(root)}, ensure_ascii=False, sort_keys=True))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
