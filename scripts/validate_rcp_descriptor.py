#!/usr/bin/env python3
"""Validate Aletheia RCP Descriptor v0.1.0 instances with the stdlib only."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


CONTRACT_NAME = "aletheia.research-control-plane-descriptor"
VERSION = "0.1.0"
SCHEMA_ID = "urn:aletheia:schema:research-control-plane-descriptor:0.1.0"
DRAFT = "https://json-schema.org/draft/2020-12/schema"
ROOT_FIELDS = {"descriptor_contract", "control_plane", "repository", "authority", "consumes"}
DESCRIPTOR_FIELDS = {"name", "version", "schema_version"}
CONTROL_PLANE_FIELDS = {"id", "display_name", "research_domain"}
REPOSITORY_FIELDS = {"url", "branch", "commit_sha"}
AUTHORITY_FIELDS = {"research_only", "clinical_authority", "human_scientific_authority_required"}
CONSUME_FIELDS = {"name", "compatible_versions"}
ID_PATTERN = r"^[a-z0-9](?:[a-z0-9-]{1,62}[a-z0-9])$"
SHA_PATTERN = r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$"
DEPENDENCY_NAME_PATTERN = r"^[a-z][a-z0-9]*(?:\.[a-z][a-z0-9-]*)+$"
SEMVER_PATTERN = r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"


class DuplicateKeyError(ValueError):
    """Raised when JSON contains a duplicate object key."""


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate object key: {key}")
        result[key] = value
    return result


def parse_json_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=reject_duplicate_keys)


def exact_object(value: object, location: str, fields: set[str], errors: list[str]) -> dict[str, object] | None:
    if not isinstance(value, dict):
        errors.append(f"{location}: expected object")
        return None
    actual = set(value)
    for name in sorted(fields - actual):
        errors.append(f"{location}: missing field {name}")
    for name in sorted(actual - fields):
        errors.append(f"{location}: unknown field {name}")
    return value


def bounded_string(value: object, location: str, maximum: int, errors: list[str]) -> str | None:
    if not isinstance(value, str):
        errors.append(f"{location}: expected string")
        return None
    if not value.strip():
        errors.append(f"{location}: must be non-empty")
    if len(value) > maximum:
        errors.append(f"{location}: exceeds maximum length {maximum}")
    return value


def validate_instance(document: object) -> list[str]:
    errors: list[str] = []
    root = exact_object(document, "$", ROOT_FIELDS, errors)
    if root is None:
        return errors

    descriptor = exact_object(root.get("descriptor_contract"), "$.descriptor_contract", DESCRIPTOR_FIELDS, errors)
    if descriptor is not None:
        expected = {"name": CONTRACT_NAME, "version": VERSION, "schema_version": VERSION}
        for key, value in expected.items():
            if descriptor.get(key) != value:
                errors.append(f"$.descriptor_contract.{key}: expected {value!r}")

    control_plane = exact_object(root.get("control_plane"), "$.control_plane", CONTROL_PLANE_FIELDS, errors)
    if control_plane is not None:
        identifier = bounded_string(control_plane.get("id"), "$.control_plane.id", 64, errors)
        if identifier is not None and (len(identifier) < 3 or re.fullmatch(ID_PATTERN, identifier) is None):
            errors.append("$.control_plane.id: expected lowercase kebab-case length 3..64")
        bounded_string(control_plane.get("display_name"), "$.control_plane.display_name", 160, errors)
        bounded_string(control_plane.get("research_domain"), "$.control_plane.research_domain", 160, errors)

    repository = exact_object(root.get("repository"), "$.repository", REPOSITORY_FIELDS, errors)
    if repository is not None:
        url = bounded_string(repository.get("url"), "$.repository.url", 512, errors)
        if url is not None and url.strip():
            parsed = urlsplit(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or any(character.isspace() for character in url):
                errors.append("$.repository.url: expected absolute http(s) repository URL; local paths and file:// are forbidden")
        bounded_string(repository.get("branch"), "$.repository.branch", 255, errors)
        commit_sha = repository.get("commit_sha")
        if not isinstance(commit_sha, str) or re.fullmatch(SHA_PATTERN, commit_sha) is None:
            errors.append("$.repository.commit_sha: expected 40 or 64 lowercase hexadecimal characters")

    authority = exact_object(root.get("authority"), "$.authority", AUTHORITY_FIELDS, errors)
    if authority is not None:
        expected_authority = {
            "research_only": True,
            "clinical_authority": False,
            "human_scientific_authority_required": True,
        }
        for key, value in expected_authority.items():
            if type(authority.get(key)) is not bool or authority.get(key) is not value:
                errors.append(f"$.authority.{key}: expected constant {str(value).lower()}")

    consumes = root.get("consumes")
    if not isinstance(consumes, list):
        errors.append("$.consumes: expected array")
    else:
        dependency_names: set[str] = set()
        for index, item in enumerate(consumes):
            location = f"$.consumes[{index}]"
            dependency = exact_object(item, location, CONSUME_FIELDS, errors)
            if dependency is None:
                continue
            name = bounded_string(dependency.get("name"), f"{location}.name", 160, errors)
            if name is not None:
                if len(name) < 3 or re.fullmatch(DEPENDENCY_NAME_PATTERN, name) is None:
                    errors.append(f"{location}.name: expected dot-namespaced lowercase contract name")
                if name in dependency_names:
                    errors.append(f"{location}.name: duplicate dependency name {name}")
                dependency_names.add(name)
            versions = dependency.get("compatible_versions")
            if not isinstance(versions, list):
                errors.append(f"{location}.compatible_versions: expected array")
                continue
            if not versions:
                errors.append(f"{location}.compatible_versions: must be non-empty")
            seen_versions: set[str] = set()
            for version_index, version in enumerate(versions):
                version_location = f"{location}.compatible_versions[{version_index}]"
                if not isinstance(version, str) or re.fullmatch(SEMVER_PATTERN, version) is None:
                    errors.append(f"{version_location}: expected exact SemVer")
                elif version in seen_versions:
                    errors.append(f"{version_location}: duplicate compatible version {version}")
                seen_versions.add(version) if isinstance(version, str) else None
    return errors


def schema_self_check(schema: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(schema, dict):
        return ["schema root: expected object"]
    if schema.get("$schema") != DRAFT:
        errors.append(f"$schema: expected {DRAFT}")
    if schema.get("$id") != SCHEMA_ID:
        errors.append(f"$id: expected {SCHEMA_ID}")
    if schema.get("type") != "object":
        errors.append("root type: expected object")
    if schema.get("additionalProperties") is not False:
        errors.append("root additionalProperties: expected false")
    if set(schema.get("required", [])) != ROOT_FIELDS:
        errors.append("root required fields do not match the contract")
    properties = schema.get("properties")
    if not isinstance(properties, dict) or set(properties) != ROOT_FIELDS:
        errors.append("root properties do not match the contract")
        return errors
    nested = {
        "descriptor_contract": DESCRIPTOR_FIELDS,
        "control_plane": CONTROL_PLANE_FIELDS,
        "repository": REPOSITORY_FIELDS,
        "authority": AUTHORITY_FIELDS,
    }
    for name, fields in nested.items():
        value = properties.get(name, {})
        if value.get("type") != "object" or value.get("additionalProperties") is not False:
            errors.append(f"{name}: expected closed object")
        if set(value.get("required", [])) != fields or set(value.get("properties", {})) != fields:
            errors.append(f"{name}: required/properties mismatch")
    descriptor_properties = properties["descriptor_contract"]["properties"]
    expected_descriptor = {"name": CONTRACT_NAME, "version": VERSION, "schema_version": VERSION}
    for key, value in expected_descriptor.items():
        if descriptor_properties.get(key, {}).get("const") != value:
            errors.append(f"descriptor_contract.{key}: const mismatch")
    authority_properties = properties["authority"]["properties"]
    expected_authority = {"research_only": True, "clinical_authority": False, "human_scientific_authority_required": True}
    for key, value in expected_authority.items():
        if authority_properties.get(key, {}).get("const") is not value:
            errors.append(f"authority.{key}: const mismatch")
    if properties["control_plane"]["properties"].get("id", {}).get("pattern") != ID_PATTERN:
        errors.append("control_plane.id: pattern mismatch")
    if properties["repository"]["properties"].get("commit_sha", {}).get("pattern") != SHA_PATTERN:
        errors.append("repository.commit_sha: pattern mismatch")
    consumes = properties.get("consumes", {})
    item = consumes.get("items", {}) if isinstance(consumes, dict) else {}
    if consumes.get("type") != "array" or item.get("type") != "object" or item.get("additionalProperties") is not False:
        errors.append("consumes: expected array of closed objects")
    if set(item.get("required", [])) != CONSUME_FIELDS or set(item.get("properties", {})) != CONSUME_FIELDS:
        errors.append("consumes item: required/properties mismatch")
    version_items = item.get("properties", {}).get("compatible_versions", {}).get("items", {})
    if version_items.get("pattern") != SEMVER_PATTERN:
        errors.append("compatible_versions: SemVer pattern mismatch")
    if item.get("properties", {}).get("compatible_versions", {}).get("uniqueItems") is not True:
        errors.append("compatible_versions: uniqueItems must be true")
    return errors


def load_json(path: Path) -> object:
    return parse_json_text(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", nargs="?", type=Path)
    parser.add_argument("--self-check-schema", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if (args.instance is None) == (args.self_check_schema is None):
        parser.error("provide exactly one instance or --self-check-schema")
    target = args.self_check_schema or args.instance
    mode = "schema-structural-self-check" if args.self_check_schema else "instance-validation"
    try:
        document = load_json(target)
        errors = schema_self_check(document) if args.self_check_schema else validate_instance(document)
    except UnicodeDecodeError as error:
        errors = [f"invalid UTF-8: {error}"]
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as error:
        errors = [str(error)]
    result = {
        "schema": "aletheia.rcp-descriptor-validation.v1",
        "contract": CONTRACT_NAME,
        "contract_version": VERSION,
        "schema_version": VERSION,
        "mode": mode,
        "state": "PASS" if not errors else "FAIL",
        "errors": errors,
        "json_schema_meta_validation": "NOT_EXECUTED_EXTERNAL_ENGINE",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
