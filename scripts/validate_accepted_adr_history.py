#!/usr/bin/env python3
"""Guard accepted ADR content against silent history rewrites."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]


def git_bytes(repository: Path, revision: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repository), "show", f"{revision}:{relative}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def explicit_governance(root: Path, adr_id: str, old_hash: str, new_hash: str, base_paths: set[str]) -> str | None:
    for path in sorted((root / "docs" / "adr").glob("*.md")):
        relative = path.relative_to(root).as_posix()
        if relative in base_paths:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        status = re.search(r"^- \*\*Status:\*\* ([A-Za-z]+)\s*$", text, re.MULTILINE)
        if adr_id in text and "supersed" in text.lower() and status and status.group(1) == "Accepted":
            return relative
    amendments = root / "docs" / "adr" / "amendments"
    if amendments.exists():
        for path in sorted(item for item in amendments.rglob("*") if item.is_file()):
            text = path.read_text(encoding="utf-8", errors="replace")
            required = (adr_id, old_hash, new_hash)
            decision_accepted = re.search(r"human(?:_| )decision(?:_| )state\s*[:=]\s*Accepted\b", text, re.IGNORECASE)
            if all(value in text for value in required) and decision_accepted:
                return path.relative_to(root).as_posix()
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--root", type=Path, default=SCRIPT_ROOT)
    parser.add_argument("--repository", type=Path, default=SCRIPT_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        repository = args.repository.resolve(strict=True)
        base_register = json.loads(git_bytes(repository, args.base, "ADR-REGISTER.json"))
        base_paths = {record["path"] for record in base_register["records"]}
        accepted = [record for record in base_register["records"] if record.get("status") == "Accepted"]
        observations = []
        failures = []
        for record in accepted:
            relative = record["path"]
            identifier = re.search(r"ADR-(?:KR-)?\d{4}", record.get("title", ""))
            adr_id = identifier.group(0) if identifier else relative
            before = git_bytes(repository, args.base, relative)
            current_path = root / relative
            after = current_path.read_bytes() if current_path.is_file() else b""
            before_hash = sha256(before)
            after_hash = sha256(after)
            unchanged = before == after
            governance = None if unchanged else explicit_governance(root, adr_id, before_hash, after_hash, base_paths)
            passed = unchanged or governance is not None
            observation = {
                "adr": adr_id, "path": relative, "base_sha256": before_hash,
                "current_sha256": after_hash, "unchanged": unchanged,
                "governance_evidence": governance, "pass": passed,
            }
            observations.append(observation)
            if not passed:
                failures.append(f"{adr_id} changed without accepted supersession or amendment")
        result = {
            "schema": "aletheia.accepted-adr-history.v1", "base": args.base,
            "root": str(root), "accepted_adrs": len(accepted),
            "state": "PASS" if not failures else "FAIL", "observations": observations,
            "errors": failures,
        }
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, RuntimeError) as error:
        result = {"schema": "aletheia.accepted-adr-history.v1", "base": args.base, "state": "FAIL", "errors": [str(error)]}
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": result["state"], "base": args.base, "accepted_adrs": result.get("accepted_adrs", 0), "errors": len(result["errors"])}, sort_keys=True))
    if result["state"] != "PASS":
        print("\n".join(result["errors"]), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
