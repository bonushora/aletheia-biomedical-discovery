#!/usr/bin/env python3
"""Unit tests for the exact-SHA qualified consumer registry."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_consumer_registry import DuplicateKeyError, load_json, validate_documents


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "contracts/REGISTRY.json"
MATRIX = ROOT / "contracts/COMPATIBILITY-MATRIX.json"


class ConsumerRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

    @property
    def registry_contract(self) -> dict:
        return self.registry["contracts"][0]

    @property
    def registry_consumer(self) -> dict:
        return self.registry_contract["qualified_consumer_records"][0]

    @property
    def matrix_consumer(self) -> dict:
        return self.matrix["qualified_consumers"][0]

    def rejected(self, mutation) -> list[str]:
        registry = copy.deepcopy(self.registry)
        matrix = copy.deepcopy(self.matrix)
        mutation(registry, matrix)
        errors = validate_documents(registry, matrix)
        self.assertTrue(errors)
        return errors

    def test_valid_registration(self):
        self.assertEqual(validate_documents(self.registry, self.matrix), [])

    def test_validation_is_deterministic(self):
        first = validate_documents(self.registry, self.matrix)
        second = validate_documents(copy.deepcopy(self.registry), copy.deepcopy(self.matrix))
        self.assertEqual(first, second)

    def test_count_mismatch_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"][0].update({"qualified_consumers": 2}))

    def test_duplicate_registry_consumer_rejected(self):
        def mutate(registry, matrix):
            contract = registry["contracts"][0]
            contract["qualified_consumer_records"].append(copy.deepcopy(contract["qualified_consumer_records"][0]))
            contract["qualified_consumers"] = 2
        self.rejected(mutate)

    def test_duplicate_matrix_consumer_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"].append(copy.deepcopy(matrix["qualified_consumers"][0])))

    def test_missing_matrix_entry_rejected(self):
        self.rejected(lambda registry, matrix: matrix.update({"qualified_consumers": []}))

    def test_wrong_contract_version_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"][0].update({"version": "0.2.0"}))

    def test_wrong_schema_version_rejected(self):
        self.rejected(lambda registry, matrix: matrix.update({"schema_version": "0.2.0"}))

    def test_wrong_aletheia_sha_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"aletheia_contract_implementation_sha": "a" * 40}))

    def test_wrong_kidney_subject_sha_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"][0]["qualified_consumer_records"][0].update({"consumer_subject_sha": "a" * 40}))

    def test_wrong_qualification_sha_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"consumer_qualification_sha": "b" * 40}))

    def test_swapped_subject_and_qualification_roles_rejected(self):
        def mutate(registry, matrix):
            for record in (registry["contracts"][0]["qualified_consumer_records"][0], matrix["qualified_consumers"][0]):
                record["consumer_subject_sha"], record["consumer_qualification_sha"] = record["consumer_qualification_sha"], record["consumer_subject_sha"]
        self.rejected(mutate)

    def test_wrong_descriptor_hash_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"descriptor_sha256": "a" * 64}))

    def test_wrong_lock_hash_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"][0]["qualified_consumer_records"][0].update({"compatibility_lock_sha256": "b" * 64}))

    def test_uppercase_hash_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"descriptor_sha256": "A" * 64}))

    def test_mutable_main_as_identity_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"consumer_subject_sha": "main"}))

    def test_forged_publication_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"published": True, "remote_publication": "PERFORMED"}))

    def test_scientific_promotion_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"][0]["qualified_consumer_records"][0].update({"scientific_validation": "PASS"}))

    def test_clinical_promotion_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"clinical_validation": "PASS"}))

    def test_unknown_consumer_rejected(self):
        def mutate(registry, matrix):
            registry["contracts"][0]["qualified_consumer_records"][0]["consumer_id"] = "unknown-consumer"
            matrix["qualified_consumers"][0]["consumer_id"] = "unknown-consumer"
        self.rejected(mutate)

    def test_non_green_qualification_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"qualification_state": "PENDING"}))

    def test_non_local_scope_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"][0]["qualified_consumer_records"][0].update({"qualification_scope": "REMOTE"}))

    def test_changed_contract_status_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"][0].update({"status": "STABLE"}))

    def test_zero_count_with_matrix_entry_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"][0].update({"qualified_consumers": 0}))

    def test_matrix_status_must_be_qualified_local(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"status": "QUALIFIED_REMOTE"}))

    def test_registry_matrix_disagreement_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"remote_publication": "UNKNOWN"}))

    def test_extra_consumer_field_rejected(self):
        self.rejected(lambda registry, matrix: matrix["qualified_consumers"][0].update({"identity": "main"}))

    def test_contract_family_count_rejected(self):
        self.rejected(lambda registry, matrix: registry["contracts"].append(copy.deepcopy(registry["contracts"][0])))

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory(prefix="aletheia-registry-unit-") as directory:
            temporary = Path(directory) / "duplicate.json"
            temporary.write_text('{"schema":"one","schema":"two"}\n', encoding="utf-8")
            with self.assertRaises(DuplicateKeyError):
                load_json(temporary)


if __name__ == "__main__":
    unittest.main()
