#!/usr/bin/env python3
"""Run the required 14-case qualified consumer registry attack corpus."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts/validate_consumer_registry.py"
REGISTRY = ROOT / "contracts/REGISTRY.json"
MATRIX = ROOT / "contracts/COMPATIBILITY-MATRIX.json"
CASES = {
    "A01": ("VALID_REGISTRATION", "PASS"),
    "A02": ("SUBJECT_SHA_TAMPER", "REJECT"),
    "A03": ("QUALIFICATION_SHA_TAMPER", "REJECT"),
    "A04": ("SUBJECT_QUALIFICATION_ROLE_SWAP", "REJECT"),
    "A05": ("DESCRIPTOR_HASH_TAMPER", "REJECT"),
    "A06": ("LOCK_HASH_TAMPER", "REJECT"),
    "A07": ("QUALIFIED_COUNT_TAMPER", "REJECT"),
    "A08": ("DUPLICATE_CONSUMER", "REJECT"),
    "A09": ("MATRIX_ENTRY_REMOVED", "REJECT"),
    "A10": ("MUTABLE_MAIN_IDENTITY", "REJECT"),
    "A11": ("SCIENTIFIC_VALIDATION_PROMOTION", "REJECT"),
    "A12": ("CLINICAL_VALIDATION_PROMOTION", "REJECT"),
    "A13": ("PUBLISHED_STATE_FORGED", "REJECT"),
    "A14": ("CONTRACT_VERSION_TAMPER", "REJECT"),
}


def mutate(case_id: str, registry: dict, matrix: dict) -> None:
    registry_consumer = registry["contracts"][0]["qualified_consumer_records"][0]
    matrix_consumer = matrix["qualified_consumers"][0]
    if case_id == "A01":
        return
    if case_id == "A02":
        registry_consumer["consumer_subject_sha"] = "a" * 40
    elif case_id == "A03":
        matrix_consumer["consumer_qualification_sha"] = "b" * 40
    elif case_id == "A04":
        for record in (registry_consumer, matrix_consumer):
            record["consumer_subject_sha"], record["consumer_qualification_sha"] = record["consumer_qualification_sha"], record["consumer_subject_sha"]
    elif case_id == "A05":
        matrix_consumer["descriptor_sha256"] = "c" * 64
    elif case_id == "A06":
        registry_consumer["compatibility_lock_sha256"] = "d" * 64
    elif case_id == "A07":
        registry["contracts"][0]["qualified_consumers"] = 0
    elif case_id == "A08":
        registry["contracts"][0]["qualified_consumer_records"].append(copy.deepcopy(registry_consumer))
        registry["contracts"][0]["qualified_consumers"] = 2
    elif case_id == "A09":
        matrix["qualified_consumers"] = []
    elif case_id == "A10":
        matrix_consumer["consumer_subject_sha"] = "main"
    elif case_id == "A11":
        registry_consumer["scientific_validation"] = "PASS"
    elif case_id == "A12":
        matrix_consumer["clinical_validation"] = "PASS"
    elif case_id == "A13":
        matrix_consumer["published"] = True
        matrix_consumer["remote_publication"] = "PERFORMED"
    elif case_id == "A14":
        matrix["contract_version"] = "0.2.0"
    else:
        raise RuntimeError(f"unimplemented case: {case_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--case", action="append", choices=sorted(CASES))
    args = parser.parse_args()
    selected = args.case or sorted(CASES)
    base_registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    base_matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    results = []
    harness_errors = 0
    with tempfile.TemporaryDirectory(prefix="aletheia-consumer-registry-hardening-") as temporary:
        work = Path(temporary)
        for case_id in selected:
            name, expected = CASES[case_id]
            try:
                registry = copy.deepcopy(base_registry)
                matrix = copy.deepcopy(base_matrix)
                mutate(case_id, registry, matrix)
                registry_path = work / f"{case_id}-registry.json"
                matrix_path = work / f"{case_id}-matrix.json"
                registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                matrix_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                completed = subprocess.run(
                    [sys.executable, str(VALIDATOR), "--registry", str(registry_path), "--matrix", str(matrix_path)],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
                )
                observed = "PASS" if completed.returncode == 0 else "REJECT"
                results.append({
                    "attack_id": case_id,
                    "description": name,
                    "expected": expected,
                    "observed": observed,
                    "exit_code": completed.returncode,
                    "expected_match": observed == expected,
                    "reason": (completed.stderr or completed.stdout).strip().replace(str(work), "<TMP>")[-1600:],
                    "fixture_identity": hashlib.sha256(f"{case_id}:{name}".encode()).hexdigest(),
                })
            except Exception as error:
                harness_errors += 1
                results.append({
                    "attack_id": case_id, "description": name, "expected": expected,
                    "observed": "HARNESS_ERROR", "exit_code": None, "expected_match": False,
                    "reason": f"{type(error).__name__}: {error}",
                    "fixture_identity": hashlib.sha256(f"{case_id}:{name}".encode()).hexdigest(),
                })
    unexpected_pass = sum(item["expected"] == "REJECT" and item["observed"] == "PASS" for item in results)
    unexpected_fail = sum(item["expected"] == "PASS" and item["observed"] != "PASS" for item in results)
    state = "PASS" if len(results) == len(selected) and not unexpected_pass and not unexpected_fail and not harness_errors else "FAIL"
    document = {
        "schema": "aletheia.consumer-registry-hardening-results.v1",
        "state": state,
        "cases_total": len(results),
        "expected_pass": sum(item["expected"] == "PASS" for item in results),
        "expected_reject": sum(item["expected"] == "REJECT" for item in results),
        "unexpected_pass": unexpected_pass,
        "unexpected_fail": unexpected_fail,
        "harness_errors": harness_errors,
        "results": results,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: document[key] for key in ("state", "cases_total", "expected_pass", "expected_reject", "unexpected_pass", "unexpected_fail", "harness_errors")}, sort_keys=True))
    return 0 if state == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
