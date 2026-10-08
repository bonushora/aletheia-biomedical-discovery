#!/usr/bin/env python3
"""Validate the exact-SHA first qualified consumer registry using stdlib only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "contracts/REGISTRY.json"
MATRIX_PATH = ROOT / "contracts/COMPATIBILITY-MATRIX.json"
CONTRACT = "aletheia.research-control-plane-descriptor"
VERSION = "0.1.0"
ALETHEIA_SHA = "01b275e5cc8d96f1c03540b24b581a2ae820f264"
CONSUMER_ID = "kidney-regeneration-research"
SUBJECT_SHA = "30ecd32f4639949755a0062670389913129321b4"
QUALIFICATION_SHA = "67c2f5699ce004d6e42eaf4352f37260b560c618"
DESCRIPTOR_SHA256 = "5f2eab8334fef6c7c227ed49904caa0dcf4d91b568e14f5f4e7ef1b29fcf64db"
LOCK_SHA256 = "3d6acb1a4ef9b03a1692062802e4164cc16a065d59b8c73666796a2faf0d59c0"
QUALIFICATION_STATE = "GREEN_KIDNEY_FIRST_RCP_CONSUMER"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")

REGISTRY_RECORD_KEYS = {
    "consumer_id", "consumer_subject_sha", "consumer_qualification_sha",
    "descriptor_sha256", "compatibility_lock_sha256", "qualification_state",
    "qualification_scope", "remote_publication", "scientific_validation",
    "clinical_validation",
}
MATRIX_RECORD_KEYS = REGISTRY_RECORD_KEYS | {
    "aletheia_contract_implementation_sha", "contract_version", "schema_version",
    "status", "qualification_branch_observed", "published",
}
AGREEMENT_KEYS = REGISTRY_RECORD_KEYS


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(root: Path, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(manifest_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as error:
        return [f"manifest unreadable: {type(error).__name__}: {error}"]
    if not isinstance(manifest, dict):
        return ["manifest root must be an object"]
    if manifest.get("schema") != "aletheia.first-qualified-consumer-manifest.v1":
        errors.append("manifest schema mismatch")
    if manifest.get("algorithm") != "sha256":
        errors.append("manifest algorithm must be sha256")
    records = manifest.get("files")
    if not isinstance(records, list):
        return sorted(set(errors + ["manifest files must be an array"]))
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != {"path", "sha256", "size"}:
            errors.append(f"manifest record {index} fields mismatch")
            continue
        relative = record.get("path")
        if not isinstance(relative, str):
            errors.append(f"manifest record {index} path must be a string")
            continue
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or relative in seen:
            errors.append(f"manifest record {index} path is unsafe or duplicate")
            continue
        seen.add(relative)
        path = root / relative
        if not path.is_file() or path.is_symlink():
            errors.append(f"manifest file missing or unsafe: {relative}")
            continue
        if type(record.get("size")) is not int or path.stat().st_size != record["size"]:
            errors.append(f"manifest size mismatch: {relative}")
        if not isinstance(record.get("sha256"), str) or not SHA64.fullmatch(record["sha256"]):
            errors.append(f"manifest hash format mismatch: {relative}")
        elif file_sha256(path) != record["sha256"]:
            errors.append(f"manifest hash mismatch: {relative}")
    return sorted(set(errors))


def validate_documents(registry: Any, matrix: Any) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(isinstance(registry, dict), "registry root must be an object")
    require(isinstance(matrix, dict), "matrix root must be an object")
    if not isinstance(registry, dict) or not isinstance(matrix, dict):
        return sorted(set(errors))

    require(registry.get("schema") == "aletheia.contract-registry.v1", "registry schema must remain v1")
    contracts = registry.get("contracts")
    require(isinstance(contracts, list), "registry contracts must be an array")
    if not isinstance(contracts, list):
        return sorted(set(errors))
    require(len(contracts) == 1, "registry must contain exactly one contract family")
    if len(contracts) != 1 or not isinstance(contracts[0], dict):
        if contracts and not isinstance(contracts[0], dict):
            errors.append("registry contract must be an object")
        return sorted(set(errors))

    contract = contracts[0]
    require(contract.get("name") == CONTRACT, "contract name mismatch")
    require(contract.get("version") == VERSION, "contract version must be 0.1.0")
    require(contract.get("schema_version") == VERSION, "registry schema version must be 0.1.0")
    require(contract.get("status") == "EXPERIMENTAL", "contract status must remain EXPERIMENTAL")
    require(contract.get("qualified") is True, "contract qualified state must remain true")
    require(contract.get("consumer_compatibility") == "ESTABLISHED_LOCAL", "registry compatibility must be ESTABLISHED_LOCAL")

    count = contract.get("qualified_consumers")
    records = contract.get("qualified_consumer_records")
    require(type(count) is int and count == 1, "registry qualified_consumers must equal 1")
    require(isinstance(records, list), "registry consumer records must be an array")
    if not isinstance(records, list):
        records = []
    require(len(records) == 1, "registry must contain exactly one qualified consumer record")
    registry_ids = [record.get("consumer_id") for record in records if isinstance(record, dict)]
    require(len(registry_ids) == len(records), "every registry consumer must be an object")
    require(len(registry_ids) == len(set(registry_ids)), "registry consumer IDs must be unique")
    require(count == len(records), "registry qualified consumer count does not match records")

    require(matrix.get("schema") == "aletheia.compatibility-matrix.v1", "matrix schema must remain v1")
    require(matrix.get("contract") == CONTRACT, "matrix contract name mismatch")
    require(matrix.get("contract_version") == VERSION, "matrix contract version must be 0.1.0")
    require(matrix.get("schema_version") == VERSION, "matrix schema version must be 0.1.0")
    require(matrix.get("consumer_compatibility") == "ESTABLISHED_LOCAL", "matrix compatibility must be ESTABLISHED_LOCAL")
    matrix_records = matrix.get("qualified_consumers")
    require(isinstance(matrix_records, list), "matrix qualified_consumers must be an array")
    if not isinstance(matrix_records, list):
        matrix_records = []
    require(len(matrix_records) == 1, "matrix must contain exactly one qualified consumer")
    matrix_ids = [record.get("consumer_id") for record in matrix_records if isinstance(record, dict)]
    require(len(matrix_ids) == len(matrix_records), "every matrix consumer must be an object")
    require(len(matrix_ids) == len(set(matrix_ids)), "matrix consumer IDs must be unique")
    require(count == len(matrix_records), "registry count does not match matrix")
    require(set(registry_ids) == set(matrix_ids), "registry and matrix consumer IDs disagree")

    expected_common = {
        "consumer_id": CONSUMER_ID,
        "consumer_subject_sha": SUBJECT_SHA,
        "consumer_qualification_sha": QUALIFICATION_SHA,
        "descriptor_sha256": DESCRIPTOR_SHA256,
        "compatibility_lock_sha256": LOCK_SHA256,
        "qualification_state": QUALIFICATION_STATE,
        "qualification_scope": "LOCAL",
        "remote_publication": "NOT_PERFORMED",
        "scientific_validation": "NOT_EXECUTED",
        "clinical_validation": "NOT_EXECUTED",
    }
    for label, items, expected_keys in (
        ("registry", records, REGISTRY_RECORD_KEYS),
        ("matrix", matrix_records, MATRIX_RECORD_KEYS),
    ):
        for index, record in enumerate(items):
            if not isinstance(record, dict):
                continue
            require(set(record) == expected_keys, f"{label} consumer {index} fields mismatch")
            for key, expected in expected_common.items():
                require(record.get(key) == expected, f"{label} consumer {index} {key} mismatch")
            require(bool(SHA40.fullmatch(str(record.get("consumer_subject_sha", "")))), f"{label} subject SHA must be lowercase immutable SHA-1")
            require(bool(SHA40.fullmatch(str(record.get("consumer_qualification_sha", "")))), f"{label} qualification SHA must be lowercase immutable SHA-1")
            require(bool(SHA64.fullmatch(str(record.get("descriptor_sha256", "")))), f"{label} descriptor hash must be lowercase SHA-256")
            require(bool(SHA64.fullmatch(str(record.get("compatibility_lock_sha256", "")))), f"{label} lock hash must be lowercase SHA-256")
            for key in ("consumer_subject_sha", "consumer_qualification_sha", "descriptor_sha256", "compatibility_lock_sha256"):
                require(str(record.get(key, "")).lower() not in {"main", "master", "head", "latest"}, f"{label} {key} cannot use a mutable label")

    for index, record in enumerate(matrix_records):
        if not isinstance(record, dict):
            continue
        require(record.get("aletheia_contract_implementation_sha") == ALETHEIA_SHA, f"matrix consumer {index} Aletheia SHA mismatch")
        require(bool(SHA40.fullmatch(str(record.get("aletheia_contract_implementation_sha", "")))), f"matrix consumer {index} Aletheia SHA must be lowercase immutable SHA-1")
        require(record.get("contract_version") == VERSION, f"matrix consumer {index} contract version mismatch")
        require(record.get("schema_version") == VERSION, f"matrix consumer {index} schema version mismatch")
        require(record.get("status") == "QUALIFIED_LOCAL", f"matrix consumer {index} status must be QUALIFIED_LOCAL")
        require(record.get("published") is False, f"matrix consumer {index} published must be false")
        require(record.get("qualification_branch_observed") == "feature/aletheia-rcp-descriptor-v0.1.0", f"matrix consumer {index} observed branch mismatch")

    if len(records) == 1 and len(matrix_records) == 1 and isinstance(records[0], dict) and isinstance(matrix_records[0], dict):
        for key in sorted(AGREEMENT_KEYS):
            require(records[0].get(key) == matrix_records[0].get(key), f"registry/matrix disagreement for {key}")

    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--matrix", type=Path, default=MATRIX_PATH)
    parser.add_argument("--verify-manifest", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    registry: Any = None
    matrix: Any = None
    try:
        registry = load_json(args.registry)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as error:
        errors.append(f"registry unreadable: {type(error).__name__}: {error}")
    try:
        matrix = load_json(args.matrix)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as error:
        errors.append(f"matrix unreadable: {type(error).__name__}: {error}")
    if not errors:
        errors.extend(validate_documents(registry, matrix))
    if args.verify_manifest:
        manifest_path = args.verify_manifest if args.verify_manifest.is_absolute() else ROOT / args.verify_manifest
        errors.extend(validate_manifest(ROOT, manifest_path))
    result = {
        "schema": "aletheia.consumer-registry-validation.v1",
        "contract": CONTRACT,
        "contract_version": VERSION,
        "qualified_consumers": 1 if not errors else None,
        "first_qualified_consumer": CONSUMER_ID if not errors else None,
        "state": "PASS" if not errors else "FAIL",
        "errors": sorted(errors),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
