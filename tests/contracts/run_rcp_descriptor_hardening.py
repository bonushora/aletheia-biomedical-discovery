#!/usr/bin/env python3
"""Run the 20-case synthetic RCP Descriptor adversarial corpus."""

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
VALIDATOR = ROOT / "scripts" / "validate_rcp_descriptor.py"
EXAMPLE = ROOT / "schemas/research-control-plane-descriptor/0.1.0/examples/valid-minimal.json"
CASES = {
    "C01": ("VALID_CONTROL", "PASS"),
    "C02": ("DUPLICATE_KEY_BYPASS", "REJECT"),
    "C03": ("UNKNOWN_FIELD_INJECTION", "REJECT"),
    "C04": ("AUTHORITY_WIDENING", "REJECT"),
    "C05": ("CLINICAL_ESCALATION", "REJECT"),
    "C06": ("HUMAN_GATE_REMOVAL", "REJECT"),
    "C07": ("MAIN_DEPENDENCY", "REJECT"),
    "C08": ("LATEST_DEPENDENCY", "REJECT"),
    "C09": ("WILDCARD_DEPENDENCY", "REJECT"),
    "C10": ("URL_AS_VERSION", "REJECT"),
    "C11": ("DUPLICATE_DEPENDENCY_NAME", "REJECT"),
    "C12": ("DUPLICATE_COMPATIBLE_VERSION", "REJECT"),
    "C13": ("BAD_SHA", "REJECT"),
    "C14": ("UPPERCASE_SHA", "REJECT"),
    "C15": ("FILE_REPOSITORY_URL", "REJECT"),
    "C16": ("PATH_AS_REPOSITORY_URL", "REJECT"),
    "C17": ("WRONG_SCHEMA_VERSION", "REJECT"),
    "C18": ("WRONG_CONTRACT_VERSION", "REJECT"),
    "C19": ("WRONG_CONTRACT_NAME", "REJECT"),
    "C20": ("KIDNEY_SPECIFIC_ROOT_FIELD", "REJECT"),
}


def dependency(version: str = "1.0.0") -> dict[str, object]:
    return {"name": "aletheia.synthetic-dependency", "compatible_versions": [version]}


def mutated(case_id: str, base: dict[str, object]) -> str:
    if case_id == "C02":
        return '{"descriptor_contract":{},"descriptor_contract":{}}'
    document = copy.deepcopy(base)
    if case_id == "C01":
        pass
    elif case_id == "C03":
        document["repository"]["unknown"] = True
    elif case_id == "C04":
        document["authority"]["research_only"] = False
    elif case_id == "C05":
        document["authority"]["clinical_authority"] = True
    elif case_id == "C06":
        document["authority"]["human_scientific_authority_required"] = False
    elif case_id == "C07":
        document["consumes"] = [dependency("main")]
    elif case_id == "C08":
        document["consumes"] = [dependency("latest")]
    elif case_id == "C09":
        document["consumes"] = [dependency("*")]
    elif case_id == "C10":
        document["consumes"] = [dependency("https://example.test/v1")]
    elif case_id == "C11":
        document["consumes"] = [dependency("1.0.0"), dependency("2.0.0")]
    elif case_id == "C12":
        item = dependency("1.0.0")
        item["compatible_versions"].append("1.0.0")
        document["consumes"] = [item]
    elif case_id == "C13":
        document["repository"]["commit_sha"] = "bad-sha"
    elif case_id == "C14":
        document["repository"]["commit_sha"] = "A" * 40
    elif case_id == "C15":
        document["repository"]["url"] = "file:///tmp/repository"
    elif case_id == "C16":
        document["repository"]["url"] = "/tmp/repository"
    elif case_id == "C17":
        document["descriptor_contract"]["schema_version"] = "0.2.0"
    elif case_id == "C18":
        document["descriptor_contract"]["version"] = "0.2.0"
    elif case_id == "C19":
        document["descriptor_contract"]["name"] = "aletheia.other-contract"
    elif case_id == "C20":
        document["kidney_specific"] = {"qualified": True}
    else:
        raise RuntimeError(f"unimplemented case {case_id}")
    return json.dumps(document, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--case", action="append", choices=sorted(CASES))
    args = parser.parse_args()
    selected = args.case or sorted(CASES)
    base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    results = []
    harness_errors = 0
    with tempfile.TemporaryDirectory(prefix="aletheia-rcp-hardening-") as temporary:
        work = Path(temporary)
        for case_id in selected:
            name, expected = CASES[case_id]
            fixture = work / f"{case_id}.json"
            try:
                fixture.write_text(mutated(case_id, base), encoding="utf-8")
                completed = subprocess.run(
                    [sys.executable, str(VALIDATOR), str(fixture)],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
                )
                observed = "PASS" if completed.returncode == 0 else "REJECT"
                expected_match = observed == expected
                classification = "ALREADY_PROTECTED" if expected_match else "NEW_TEST_EXPOSED_GAP"
                output = (completed.stderr or completed.stdout).strip().replace(str(work), "<TMP>")
                results.append({
                    "attack_id": case_id, "description": name, "expected": expected,
                    "observed": observed, "exit_code": completed.returncode,
                    "expected_match": expected_match, "classification": classification,
                    "reason": output[-1600:],
                    "fixture_identity": hashlib.sha256(f"{case_id}:{name}".encode()).hexdigest(),
                })
            except Exception as error:
                harness_errors += 1
                results.append({
                    "attack_id": case_id, "description": name, "expected": expected,
                    "observed": "HARNESS_ERROR", "exit_code": None, "expected_match": False,
                    "classification": "HARNESS_ERROR", "reason": f"{type(error).__name__}: {error}",
                    "fixture_identity": hashlib.sha256(f"{case_id}:{name}".encode()).hexdigest(),
                })
    unexpected_pass = sum(item["expected"] == "REJECT" and item["observed"] == "PASS" for item in results)
    unexpected_fail = sum(item["expected"] == "PASS" and item["observed"] != "PASS" for item in results)
    state = "PASS" if len(results) == len(selected) and not unexpected_pass and not unexpected_fail and not harness_errors else "FAIL"
    document = {
        "schema": "aletheia.rcp-descriptor-hardening-results.v1",
        "contract": "aletheia.research-control-plane-descriptor", "version": "0.1.0",
        "state": state, "cases_total": len(results),
        "expected_pass": sum(item["expected"] == "PASS" for item in results),
        "expected_reject": sum(item["expected"] == "REJECT" for item in results),
        "unexpected_pass": unexpected_pass, "unexpected_fail": unexpected_fail,
        "harness_errors": harness_errors, "results": results,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: document[key] for key in ("state", "cases_total", "expected_pass", "expected_reject", "unexpected_pass", "unexpected_fail", "harness_errors")}, sort_keys=True))
    return 0 if state == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
