#!/usr/bin/env python3
"""Unit tests for the RCP Descriptor v0.1.0 validator and schema."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_rcp_descriptor import (
    CONTRACT_NAME,
    DRAFT,
    SCHEMA_ID,
    VERSION,
    DuplicateKeyError,
    parse_json_text,
    schema_self_check,
    validate_instance,
)


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "schemas/research-control-plane-descriptor/0.1.0/examples/valid-minimal.json"
SCHEMA = ROOT / "schemas/research-control-plane-descriptor/0.1.0/schema.json"


class RcpDescriptorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.valid = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def rejected(self, mutation) -> list[str]:
        document = copy.deepcopy(self.valid)
        mutation(document)
        errors = validate_instance(document)
        self.assertTrue(errors)
        return errors

    def test_valid_minimal(self):
        self.assertEqual(validate_instance(self.valid), [])

    def test_empty_consumes_is_valid(self):
        self.valid["consumes"] = []
        self.assertEqual(validate_instance(self.valid), [])

    def test_deterministic_result(self):
        self.assertEqual(validate_instance(self.valid), validate_instance(copy.deepcopy(self.valid)))

    def test_40_character_sha(self):
        self.valid["repository"]["commit_sha"] = "a" * 40
        self.assertEqual(validate_instance(self.valid), [])

    def test_64_character_sha(self):
        self.valid["repository"]["commit_sha"] = "b" * 64
        self.assertEqual(validate_instance(self.valid), [])

    def test_repository_branch_main_is_valid(self):
        self.valid["repository"]["branch"] = "main"
        self.assertEqual(validate_instance(self.valid), [])

    def test_exact_semver_dependency_is_valid(self):
        self.valid["consumes"] = [{"name": "aletheia.sample-contract", "compatible_versions": ["1.2.3"]}]
        self.assertEqual(validate_instance(self.valid), [])

    def test_semver_prerelease_dependency_is_valid(self):
        self.valid["consumes"] = [{"name": "aletheia.sample-contract", "compatible_versions": ["1.2.3-rc.1+build.5"]}]
        self.assertEqual(validate_instance(self.valid), [])

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(DuplicateKeyError):
            parse_json_text('{"consumes":[],"consumes":[]}')

    def test_non_object_root_rejected(self):
        self.assertTrue(validate_instance([]))

    def test_missing_root_field_rejected(self):
        self.rejected(lambda value: value.pop("authority"))

    def test_unknown_root_field_rejected(self):
        self.rejected(lambda value: value.update({"kidney": {}}))

    def test_unknown_descriptor_field_rejected(self):
        self.rejected(lambda value: value["descriptor_contract"].update({"extra": 1}))

    def test_wrong_contract_name_rejected(self):
        self.rejected(lambda value: value["descriptor_contract"].update({"name": "aletheia.other"}))

    def test_wrong_contract_version_rejected(self):
        self.rejected(lambda value: value["descriptor_contract"].update({"version": "0.2.0"}))

    def test_wrong_schema_version_rejected(self):
        self.rejected(lambda value: value["descriptor_contract"].update({"schema_version": "0.2.0"}))

    def test_bad_short_id_rejected(self):
        self.rejected(lambda value: value["control_plane"].update({"id": "ab"}))

    def test_uppercase_id_rejected(self):
        self.rejected(lambda value: value["control_plane"].update({"id": "Kidney"}))

    def test_trailing_hyphen_id_rejected(self):
        self.rejected(lambda value: value["control_plane"].update({"id": "kidney-"}))

    def test_empty_display_name_rejected(self):
        self.rejected(lambda value: value["control_plane"].update({"display_name": ""}))

    def test_whitespace_research_domain_rejected(self):
        self.rejected(lambda value: value["control_plane"].update({"research_domain": "   "}))

    def test_unknown_control_plane_field_rejected(self):
        self.rejected(lambda value: value["control_plane"].update({"extra": True}))

    def test_file_url_rejected(self):
        self.rejected(lambda value: value["repository"].update({"url": "file:///tmp/repository"}))

    def test_absolute_local_path_rejected(self):
        self.rejected(lambda value: value["repository"].update({"url": "/tmp/repository"}))

    def test_windows_local_path_rejected(self):
        self.rejected(lambda value: value["repository"].update({"url": "C:\\repository"}))

    def test_malformed_repository_url_rejected(self):
        self.rejected(lambda value: value["repository"].update({"url": "https:///missing-host"}))

    def test_empty_repository_url_rejected(self):
        self.rejected(lambda value: value["repository"].update({"url": ""}))

    def test_unknown_repository_field_rejected(self):
        self.rejected(lambda value: value["repository"].update({"tag": "v1"}))

    def test_empty_branch_rejected(self):
        self.rejected(lambda value: value["repository"].update({"branch": ""}))

    def test_bad_sha_rejected(self):
        self.rejected(lambda value: value["repository"].update({"commit_sha": "abc"}))

    def test_uppercase_sha_rejected(self):
        self.rejected(lambda value: value["repository"].update({"commit_sha": "A" * 40}))

    def test_41_character_sha_rejected(self):
        self.rejected(lambda value: value["repository"].update({"commit_sha": "a" * 41}))

    def test_research_only_widening_rejected(self):
        self.rejected(lambda value: value["authority"].update({"research_only": False}))

    def test_clinical_authority_escalation_rejected(self):
        self.rejected(lambda value: value["authority"].update({"clinical_authority": True}))

    def test_human_gate_removal_rejected(self):
        self.rejected(lambda value: value["authority"].update({"human_scientific_authority_required": False}))

    def test_authority_non_boolean_rejected(self):
        self.rejected(lambda value: value["authority"].update({"research_only": 1}))

    def test_unknown_authority_field_rejected(self):
        self.rejected(lambda value: value["authority"].update({"autonomous": True}))

    def test_consumes_non_array_rejected(self):
        self.rejected(lambda value: value.update({"consumes": {}}))

    def test_dependency_missing_name_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"compatible_versions": ["1.0.0"]}]}))

    def test_dependency_bad_namespace_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "contract", "compatible_versions": ["1.0.0"]}]}))

    def test_main_dependency_version_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": ["main"]}]}))

    def test_latest_dependency_version_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": ["latest"]}]}))

    def test_wildcard_dependency_version_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": ["*"]}]}))

    def test_url_dependency_version_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": ["https://example.test/v1"]}]}))

    def test_malformed_semver_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": ["1.2"]}]}))

    def test_leading_zero_semver_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": ["01.2.3"]}]}))

    def test_empty_compatible_versions_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": []}]}))

    def test_duplicate_compatible_version_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": ["1.0.0", "1.0.0"]}]}))

    def test_duplicate_dependency_name_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [
            {"name": "aletheia.sample", "compatible_versions": ["1.0.0"]},
            {"name": "aletheia.sample", "compatible_versions": ["2.0.0"]},
        ]}))

    def test_unknown_dependency_field_rejected(self):
        self.rejected(lambda value: value.update({"consumes": [{"name": "aletheia.sample", "compatible_versions": ["1.0.0"], "branch": "main"}]}))

    def test_schema_structural_self_check_passes(self):
        self.assertEqual(schema_self_check(self.schema), [])

    def test_schema_draft_is_exact(self):
        self.assertEqual(self.schema["$schema"], DRAFT)

    def test_schema_id_is_exact(self):
        self.assertEqual(self.schema["$id"], SCHEMA_ID)

    def test_schema_root_is_closed(self):
        self.assertIs(self.schema["additionalProperties"], False)

    def test_schema_descriptor_name_const(self):
        self.assertEqual(self.schema["properties"]["descriptor_contract"]["properties"]["name"]["const"], CONTRACT_NAME)

    def test_schema_descriptor_versions_const(self):
        descriptor = self.schema["properties"]["descriptor_contract"]["properties"]
        self.assertEqual((descriptor["version"]["const"], descriptor["schema_version"]["const"]), (VERSION, VERSION))

    def test_schema_authority_consts(self):
        authority = self.schema["properties"]["authority"]["properties"]
        self.assertEqual((authority["research_only"]["const"], authority["clinical_authority"]["const"], authority["human_scientific_authority_required"]["const"]), (True, False, True))

    def test_schema_mutated_required_rejected(self):
        schema = copy.deepcopy(self.schema)
        schema["required"].pop()
        self.assertTrue(schema_self_check(schema))

    def test_schema_mutated_closed_rule_rejected(self):
        schema = copy.deepcopy(self.schema)
        schema["properties"]["repository"]["additionalProperties"] = True
        self.assertTrue(schema_self_check(schema))

    def test_schema_mutated_sha_pattern_rejected(self):
        schema = copy.deepcopy(self.schema)
        schema["properties"]["repository"]["properties"]["commit_sha"]["pattern"] = ".*"
        self.assertTrue(schema_self_check(schema))


if __name__ == "__main__":
    unittest.main()
