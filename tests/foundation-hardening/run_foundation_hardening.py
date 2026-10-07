#!/usr/bin/env python3
"""Run the bounded Aletheia foundation adversarial hardening corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = SOURCE_ROOT / "scripts" / "validate_foundation.py"
HISTORY = SOURCE_ROOT / "scripts" / "validate_accepted_adr_history.py"
ZIP_VERIFIER = SOURCE_ROOT / "scripts" / "verify_evidence_zip.py"
BASE_REVISION = "efe611728229ab4abeb92bc33d857ec8760ce8a1"
ADR_0016 = Path("docs/adr/0016-repository-topology-and-module-integration-model.md")
ADR_0017 = Path("docs/adr/0017-adversarial-hardening-and-qualification-model.md")

CASES = {
    "H01": ("NOMINAL_CONTROL", "PASS"),
    "H02": ("UNAUTHORIZED_ADR_PROMOTION", "REJECT"),
    "H03": ("ACCEPTED_ADR_DEMOTION", "REJECT"),
    "H04": ("ACCEPTED_ADR_SILENT_REWRITE", "REJECT"),
    "H05": ("ACCEPTED_ADR_REWRITE_PLUS_REGISTER_REHASH", "REJECT"),
    "H06": ("REGISTER_HASH_DRIFT", "REJECT"),
    "H07": ("STALE_MANIFEST", "REJECT"),
    "H08": ("SYMLINK_ESCAPE", "REJECT"),
    "H09": ("MARKDOWN_ABSOLUTE_LOCAL_LINK", "REJECT"),
    "H10": ("MARKDOWN_REPOSITORY_ESCAPE", "REJECT"),
    "H11": ("RAW_EXPRESSION_PAYLOAD", "REJECT"),
    "H12": ("EMBEDDED_KIDNEY_REPOSITORY", "REJECT"),
    "H13": ("MERGE_CONFLICT_MARKER", "REJECT"),
    "H14": ("INVALID_UTF8", "REJECT"),
    "H15": ("FEDERATION_GUARD_REMOVAL", "REJECT"),
    "H16": ("CASEFOLD_PATH_COLLISION", "REJECT"),
    "H17": ("WINDOWS_RESERVED_PATH", "REJECT"),
    "H18": ("TRAILING_DOT_OR_SPACE_COLLISION", "REJECT"),
    "H19": ("ZIP_PARENT_TRAVERSAL", "REJECT"),
    "H20": ("ZIP_ABSOLUTE_PATH", "REJECT"),
    "H21": ("ZIP_DUPLICATE_MEMBER", "REJECT"),
    "H22": ("ZIP_CASEFOLD_COLLISION", "REJECT"),
    "H23": ("ZIP_SYMLINK_MEMBER", "REJECT"),
    "H24": ("ZIP_SAFE_CONTROL", "PASS"),
    "H25": ("VALIDATOR_FIXTURE_SUBSTITUTION", "REJECT"),
    "H26": ("DUPLICATE_ADR_IDENTIFIER", "REJECT"),
}


def copy_source(destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {".git", "__pycache__"} or name.endswith(".pyc")}
    shutil.copytree(SOURCE_ROOT, destination, ignore=ignore)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def validator(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return run([sys.executable, str(VALIDATOR), "--root", str(root), *extra])


def history(root: Path) -> subprocess.CompletedProcess[str]:
    return run([
        sys.executable, str(HISTORY), "--base", BASE_REVISION,
        "--root", str(root), "--repository", str(SOURCE_ROOT),
    ])


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"mutation anchor missing in {path.name}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def zip_case(case_id: str, work: Path) -> subprocess.CompletedProcess[str]:
    archive = work / f"{case_id}.zip"
    with zipfile.ZipFile(archive, "w") as package:
        if case_id == "H19":
            package.writestr("package/../escape", "synthetic")
        elif case_id == "H20":
            package.writestr("/absolute", "synthetic")
        elif case_id == "H21":
            package.writestr("package/value", "one")
            package.writestr("package/value", "two")
        elif case_id == "H22":
            package.writestr("package/README.md", "one")
            package.writestr("package/readme.md", "two")
        elif case_id == "H23":
            member = zipfile.ZipInfo("package/link")
            member.create_system = 3
            member.external_attr = (stat.S_IFLNK | 0o777) << 16
            package.writestr(member, "outside")
        elif case_id == "H24":
            package.writestr("package/README.md", "safe synthetic control\n")
    return run([sys.executable, str(ZIP_VERIFIER), str(archive)])


def execute_case(case_id: str, fixture: Path, work: Path) -> subprocess.CompletedProcess[str]:
    if case_id in {"H19", "H20", "H21", "H22", "H23", "H24"}:
        return zip_case(case_id, work)
    if case_id == "H01":
        return validator(fixture)
    if case_id == "H02":
        replace(fixture / "docs/adr/0015-ai-model-agent-non-authority-and-reproducible-inference.md", "**Status:** Proposed", "**Status:** Accepted")
    elif case_id == "H03":
        replace(fixture / ADR_0016, "**Status:** Accepted", "**Status:** Proposed")
    elif case_id == "H04":
        with (fixture / ADR_0016).open("a", encoding="utf-8") as stream:
            stream.write("\nSilent substantive rewrite.\n")
        return history(fixture)
    elif case_id == "H05":
        target = fixture / ADR_0016
        with target.open("a", encoding="utf-8") as stream:
            stream.write("\nSilent rewrite with coordinated register edit.\n")
        register_path = fixture / "ADR-REGISTER.json"
        register = json.loads(register_path.read_text(encoding="utf-8"))
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        for record in register["records"]:
            if record["path"] == ADR_0016.as_posix():
                record["sha256"] = digest
        register_path.write_text(json.dumps(register, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return history(fixture)
    elif case_id == "H06":
        with (fixture / ADR_0017).open("a", encoding="utf-8") as stream:
            stream.write("\nUnregistered drift.\n")
    elif case_id == "H07":
        with (fixture / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\nPost-manifest drift.\n")
        return validator(fixture, "--verify-manifest", "evidence/foundation-v01/MANIFEST.json")
    elif case_id == "H08":
        outside = work / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        os.symlink(outside, fixture / "escape-link")
    elif case_id == "H09":
        with (fixture / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\n[unsafe local path](/etc/passwd)\n")
    elif case_id == "H10":
        with (fixture / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\n[escape](../outside.txt)\n")
    elif case_id == "H11":
        (fixture / "synthetic.h5ad").write_bytes(b"synthetic-not-biomedical")
    elif case_id == "H12":
        (fixture / "modules/kidney/runtime.py").write_text("# synthetic\n", encoding="utf-8")
    elif case_id == "H13":
        with (fixture / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\n<<<<<<< local\nconflict\n=======\nother\n>>>>>>> remote\n")
    elif case_id == "H14":
        (fixture / "invalid.md").write_bytes(b"invalid-utf8:\xff\xfe")
    elif case_id == "H15":
        replace(fixture / ADR_0016, "No Control Plane may depend implicitly on mutable `main` state.", "Mutable branch state may be consumed.")
    elif case_id == "H16":
        directory = fixture / "collision"
        directory.mkdir()
        (directory / "README.md").write_text("one\n", encoding="utf-8")
        (directory / "readme.md").write_text("two\n", encoding="utf-8")
    elif case_id == "H17":
        (fixture / "CON.txt").write_text("synthetic\n", encoding="utf-8")
    elif case_id == "H18":
        (fixture / "portable-name").write_text("one\n", encoding="utf-8")
        (fixture / "portable-name.").write_text("two\n", encoding="utf-8")
    elif case_id == "H25":
        copied_validator = fixture / "scripts/validate_foundation.py"
        copied_validator.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
        (fixture / "synthetic.fastq").write_text("synthetic\n", encoding="utf-8")
    elif case_id == "H26":
        duplicate = fixture / "docs/adr/0018-duplicate-identifier.md"
        duplicate.write_text("# ADR-0017 — Duplicate identifier\n\n- **Status:** Proposed\n\n## Decision\n\nSynthetic duplicate.\n", encoding="utf-8")
    else:
        raise RuntimeError(f"unimplemented case {case_id}")
    return validator(fixture)


def sanitize(value: str, fixture: Path, work: Path) -> str:
    return value.replace(str(fixture), "<FIXTURE>").replace(str(work), "<WORK>").replace(str(SOURCE_ROOT), "<SOURCE>")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--case", action="append", choices=sorted(CASES))
    args = parser.parse_args()
    selected = args.case or sorted(CASES)
    results = []
    harness_errors = 0
    with tempfile.TemporaryDirectory(prefix="aletheia-hardening-") as temporary:
        work = Path(temporary)
        for case_id in selected:
            name, expected = CASES[case_id]
            fixture = work / f"fixture-{case_id}"
            try:
                copy_source(fixture)
                completed = execute_case(case_id, fixture, work)
                observed = "PASS" if completed.returncode == 0 else "REJECT"
                expected_match = observed == expected
                classification = "ALREADY_PROTECTED" if expected_match else "NEW_TEST_EXPOSED_GAP"
                stdout = sanitize(completed.stdout.strip(), fixture, work)
                stderr = sanitize(completed.stderr.strip(), fixture, work)
                results.append({
                    "attack_id": case_id, "description": name, "expected": expected,
                    "observed": observed, "exit_code": completed.returncode,
                    "expected_match": expected_match, "classification": classification,
                    "reason": (stderr or stdout)[-2000:],
                    "fixture_identity": hashlib.sha256(f"{case_id}:{name}".encode()).hexdigest(),
                })
            except Exception as error:  # preserve a bounded harness failure as evidence
                harness_errors += 1
                results.append({
                    "attack_id": case_id, "description": name, "expected": expected,
                    "observed": "HARNESS_ERROR", "exit_code": None,
                    "expected_match": False, "classification": "HARNESS_ERROR",
                    "reason": f"{type(error).__name__}: {error}",
                    "fixture_identity": hashlib.sha256(f"{case_id}:{name}".encode()).hexdigest(),
                })
    unexpected_pass = sum(item["expected"] == "REJECT" and item["observed"] == "PASS" for item in results)
    unexpected_fail = sum(item["expected"] == "PASS" and item["observed"] != "PASS" for item in results)
    state = "PASS" if not unexpected_pass and not unexpected_fail and not harness_errors and len(results) == len(selected) else "FAIL"
    document = {
        "schema": "aletheia.foundation-hardening-results.v1", "state": state,
        "source_revision": BASE_REVISION, "cases_total": len(results),
        "expected_pass": sum(item["expected"] == "PASS" for item in results),
        "expected_reject": sum(item["expected"] == "REJECT" for item in results),
        "unexpected_pass": unexpected_pass, "unexpected_fail": unexpected_fail,
        "harness_errors": harness_errors, "environment_limitations": [], "results": results,
    }
    rendered = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps({key: document[key] for key in ("state", "cases_total", "expected_pass", "expected_reject", "unexpected_pass", "unexpected_fail", "harness_errors")}, sort_keys=True))
    return 0 if state == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
