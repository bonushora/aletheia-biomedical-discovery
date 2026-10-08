#!/usr/bin/env python3
"""BH-SDP v2.3 exact-shape conformance tests."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_bh_sdp_v23 import DuplicateKeyError, discover_paths, parse_json_text, validate_snapshot


def canonical() -> dict:
    return {
        "nome_do_projeto": "Aletheia Biomedical Discovery",
        "versao_do_protocolo": "BH-SDP v2.3",
        "tipo_de_arquitetura": "federated biomedical discovery platform",
        "meta_de_custo": "Nenhum custo externo registrado nesta missão; execução local.",
        "fase_atual": "synthetic protocol conformance control",
        "nivel_de_risco": "ALTO",
        "contagem_de_gates": 1,
        "tentativas_equivalentes": 0,
        "acoes_manuais": [],
        "ambiente": "localhost",
        "destino_fisico": {"url": "", "branch": "main", "sha_antes": "before", "sha_depois": "after"},
        "estado_green": {
            "codigo": "PASSOU", "backend": "NOT_APPLICABLE", "interface": "PASSOU",
            "operacao": "PASSOU", "implantacao": "NOT_APPLICABLE",
            "publicacao": "NÃO_EXECUTADO", "experiencia_humana": "NÃO_EXECUTADO",
        },
        "itens_deferred": ["Validação científica não executada."],
        "ancoras_fisicas": {
            "hash_do_commit": "commit", "status_dos_testes": "PASSOU",
            "ultimas_linhas_inspecionadas": "synthetic evidence",
        },
        "componentes_validados": ["protocol shape"],
        "proximo_passo": "Aguardar autorização humana.",
    }


class BhSdpV23Tests(unittest.TestCase):
    def rejected(self, mutation) -> list[str]:
        document = copy.deepcopy(canonical())
        mutation(document)
        errors = validate_snapshot(document)
        self.assertTrue(errors)
        return errors

    def test_p01_canonical_valid_snapshot(self):
        self.assertEqual(validate_snapshot(canonical()), [])

    def test_p02_missing_top_level_key_rejected(self):
        self.rejected(lambda value: value.pop("meta_de_custo"))

    def test_p03_extra_top_level_key_rejected(self):
        self.rejected(lambda value: value.update({"extra": True}))

    def test_p04_estados_rejected(self):
        def mutate(value):
            value["estados"] = value.pop("estado_green")
        self.rejected(mutate)

    def test_p05_missing_estado_green_rejected(self):
        self.rejected(lambda value: value.pop("estado_green"))

    def test_p06_extra_estado_green_key_rejected(self):
        self.rejected(lambda value: value["estado_green"].update({"extra": "PASSOU"}))

    def test_p07_not_executado_rejected(self):
        self.rejected(lambda value: value["estado_green"].update({"publicacao": "NOT_EXECUTADO"}))

    def test_p08_nao_realizada_rejected(self):
        self.rejected(lambda value: value["estado_green"].update({"publicacao": "NAO_REALIZADA"}))

    def test_p09_exact_nao_executado_accepted(self):
        document = canonical()
        document["estado_green"]["publicacao"] = "NÃO_EXECUTADO"
        self.assertEqual(validate_snapshot(document), [])

    def test_p10_invalid_nivel_de_risco_rejected(self):
        self.rejected(lambda value: value.update({"nivel_de_risco": "MEDIO"}))

    def test_p11_invalid_ambiente_rejected(self):
        self.rejected(lambda value: value.update({"ambiente": "Localhost"}))

    def test_p12_negative_contagem_de_gates_rejected(self):
        self.rejected(lambda value: value.update({"contagem_de_gates": -1}))

    def test_p13_non_int_contagem_de_gates_rejected(self):
        self.rejected(lambda value: value.update({"contagem_de_gates": "1"}))

    def test_p14_negative_tentativas_equivalentes_rejected(self):
        self.rejected(lambda value: value.update({"tentativas_equivalentes": -1}))

    def test_p15_non_list_acoes_manuais_rejected(self):
        self.rejected(lambda value: value.update({"acoes_manuais": "none"}))

    def test_p16_non_string_action_rejected(self):
        self.rejected(lambda value: value.update({"acoes_manuais": [1]}))

    def test_p17_destino_fisico_missing_key_rejected(self):
        self.rejected(lambda value: value["destino_fisico"].pop("url"))

    def test_p18_destino_fisico_extra_key_rejected(self):
        self.rejected(lambda value: value["destino_fisico"].update({"remote": "none"}))

    def test_p19_ancoras_fisicas_missing_key_rejected(self):
        self.rejected(lambda value: value["ancoras_fisicas"].pop("hash_do_commit"))

    def test_p20_invalid_status_dos_testes_rejected(self):
        self.rejected(lambda value: value["ancoras_fisicas"].update({"status_dos_testes": "DEFERRED"}))

    def test_p21_non_list_itens_deferred_rejected(self):
        self.rejected(lambda value: value.update({"itens_deferred": "none"}))

    def test_p22_non_list_componentes_validados_rejected(self):
        self.rejected(lambda value: value.update({"componentes_validados": "protocol"}))

    def test_p23_duplicate_json_key_rejected(self):
        with self.assertRaises(DuplicateKeyError):
            parse_json_text('{"nome_do_projeto":"one","nome_do_projeto":"two"}')

    def test_p24_scientific_validation_extra_top_level_rejected(self):
        self.rejected(lambda value: value.update({"scientific_validation": "NÃO_EXECUTADO"}))

    def test_p25_clinical_validation_inside_estado_green_rejected(self):
        self.rejected(lambda value: value["estado_green"].update({"clinical_validation": "NÃO_EXECUTADO"}))

    def test_p26_deterministic_result(self):
        document = canonical()
        self.assertEqual(validate_snapshot(document), validate_snapshot(copy.deepcopy(document)))

    def test_p27_boolean_gate_count_rejected(self):
        self.rejected(lambda value: value.update({"contagem_de_gates": True}))

    def test_p28_non_string_deferred_item_rejected(self):
        self.rejected(lambda value: value.update({"itens_deferred": [False]}))

    def test_p29_root_array_rejected(self):
        self.assertTrue(validate_snapshot([]))

    def test_p30_invalid_green_enum_rejected(self):
        self.rejected(lambda value: value["estado_green"].update({"codigo": "GREEN"}))

    def test_p31_recursive_discovery_selects_only_v23_claims(self):
        with tempfile.TemporaryDirectory(prefix="aletheia-bh-sdp-discovery-") as directory:
            root = Path(directory)
            claimed = root / "claimed" / "sdp_snapshot.json"
            unrelated = root / "unrelated" / "sdp_snapshot.json"
            claimed.parent.mkdir()
            unrelated.parent.mkdir()
            claimed.write_text(json.dumps(canonical(), ensure_ascii=False), encoding="utf-8")
            unrelated.write_text('{"schema":"legacy"}\n', encoding="utf-8")
            self.assertEqual(discover_paths([root]), [claimed.resolve()])


if __name__ == "__main__":
    unittest.main()
