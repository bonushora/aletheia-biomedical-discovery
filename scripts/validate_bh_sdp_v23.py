#!/usr/bin/env python3
"""Validate BH-SDP v2.3 snapshots with the exact authoritative shape."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_VERSION = "BH-SDP v2.3"
TOP_LEVEL_KEYS = {
    "nome_do_projeto", "versao_do_protocolo", "tipo_de_arquitetura",
    "meta_de_custo", "fase_atual", "nivel_de_risco", "contagem_de_gates",
    "tentativas_equivalentes", "acoes_manuais", "ambiente", "destino_fisico",
    "estado_green", "itens_deferred", "ancoras_fisicas",
    "componentes_validados", "proximo_passo",
}
DESTINATION_KEYS = {"url", "branch", "sha_antes", "sha_depois"}
GREEN_KEYS = {
    "codigo", "backend", "interface", "operacao", "implantacao",
    "publicacao", "experiencia_humana",
}
ANCHOR_KEYS = {"hash_do_commit", "status_dos_testes", "ultimas_linhas_inspecionadas"}
RISK_VALUES = {"BAIXO", "MÉDIO", "ALTO"}
ENVIRONMENT_VALUES = {"localhost", "Preview", "Production"}
GREEN_VALUES = {"PASSOU", "FALHOU", "NÃO_EXECUTADO", "DEFERRED", "NOT_APPLICABLE"}
TEST_STATUS_VALUES = {"PASSOU", "FALHOU", "NÃO_EXECUTADO"}
PROTOCOL_CLAIM = re.compile(r'"versao_do_protocolo"\s*:\s*"BH-SDP v2\.3"')
SCALAR_STRING_KEYS = {
    "nome_do_projeto", "versao_do_protocolo", "tipo_de_arquitetura",
    "meta_de_custo", "fase_atual", "nivel_de_risco", "ambiente", "proximo_passo",
}


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains the same key more than once."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_text(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_unique_object)


def load_json(path: Path) -> Any:
    return parse_json_text(path.read_text(encoding="utf-8", errors="strict"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(root: Path, path: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as error:
        return [f"manifest unreadable: {type(error).__name__}: {error}"]
    if not isinstance(manifest, dict):
        return ["manifest root must be an object"]
    if manifest.get("schema") != "aletheia.bh-sdp-v2.3-conformance-repair-manifest.v1":
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
        target = root / relative
        if not target.is_file() or target.is_symlink():
            errors.append(f"manifest file missing or unsafe: {relative}")
            continue
        if type(record.get("size")) is not int or target.stat().st_size != record["size"]:
            errors.append(f"manifest size mismatch: {relative}")
        digest = record.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"manifest hash format mismatch: {relative}")
        elif file_sha256(target) != digest:
            errors.append(f"manifest hash mismatch: {relative}")
    return sorted(set(errors))


def validate_snapshot(document: Any) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(isinstance(document, dict), "root must be an object")
    if not isinstance(document, dict):
        return errors

    require(set(document) == TOP_LEVEL_KEYS, "top-level key set must be exact")
    for key in sorted(SCALAR_STRING_KEYS):
        require(isinstance(document.get(key), str), f"{key} must be a string")
    require(document.get("versao_do_protocolo") == PROTOCOL_VERSION, "protocol version must be BH-SDP v2.3")
    require(document.get("nivel_de_risco") in RISK_VALUES, "nivel_de_risco enum mismatch")
    require(document.get("ambiente") in ENVIRONMENT_VALUES, "ambiente enum mismatch")

    for key in ("contagem_de_gates", "tentativas_equivalentes"):
        value = document.get(key)
        require(type(value) is int and value >= 0, f"{key} must be a nonnegative integer")

    for key in ("acoes_manuais", "itens_deferred", "componentes_validados"):
        value = document.get(key)
        require(isinstance(value, list), f"{key} must be an array")
        if isinstance(value, list):
            require(all(isinstance(item, str) for item in value), f"{key} items must be strings")

    destination = document.get("destino_fisico")
    require(isinstance(destination, dict), "destino_fisico must be an object")
    if isinstance(destination, dict):
        require(set(destination) == DESTINATION_KEYS, "destino_fisico key set must be exact")
        for key in sorted(DESTINATION_KEYS):
            require(isinstance(destination.get(key), str), f"destino_fisico.{key} must be a string")

    green = document.get("estado_green")
    require(isinstance(green, dict), "estado_green must be an object")
    if isinstance(green, dict):
        require(set(green) == GREEN_KEYS, "estado_green key set must be exact")
        for key in sorted(GREEN_KEYS):
            value = green.get(key)
            require(isinstance(value, str), f"estado_green.{key} must be a string")
            require(value in GREEN_VALUES, f"estado_green.{key} enum mismatch")

    anchors = document.get("ancoras_fisicas")
    require(isinstance(anchors, dict), "ancoras_fisicas must be an object")
    if isinstance(anchors, dict):
        require(set(anchors) == ANCHOR_KEYS, "ancoras_fisicas key set must be exact")
        for key in sorted(ANCHOR_KEYS):
            require(isinstance(anchors.get(key), str), f"ancoras_fisicas.{key} must be a string")
        require(anchors.get("status_dos_testes") in TEST_STATUS_VALUES, "ancoras_fisicas.status_dos_testes enum mismatch")

    return sorted(set(errors))


def discover_paths(inputs: list[Path]) -> list[Path]:
    paths: set[Path] = set()
    for item in inputs or [ROOT]:
        if item.is_file():
            paths.add(item.resolve())
        elif item.is_dir():
            for path in item.rglob("sdp_snapshot.json"):
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="strict")
                except (OSError, UnicodeDecodeError):
                    continue
                if PROTOCOL_CLAIM.search(text):
                    paths.add(path.resolve())
        else:
            paths.add(item.resolve())
    return sorted(paths, key=lambda path: path.as_posix())


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="snapshot files or directories (directories are recursive)")
    parser.add_argument("--verify-manifest", type=Path)
    args = parser.parse_args()
    paths = discover_paths(args.paths)
    results: list[dict[str, Any]] = []
    for path in paths:
        errors: list[str] = []
        try:
            document = load_json(path)
            errors.extend(validate_snapshot(document))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as error:
            errors.append(f"{type(error).__name__}: {error}")
        results.append({"path": display_path(path), "state": "PASS" if not errors else "FAIL", "errors": sorted(errors)})
    if not paths:
        results.append({"path": "", "state": "FAIL", "errors": ["no snapshots discovered"]})
    failed = sum(item["state"] == "FAIL" for item in results)
    manifest_errors: list[str] = []
    if args.verify_manifest:
        manifest_path = args.verify_manifest if args.verify_manifest.is_absolute() else ROOT / args.verify_manifest
        manifest_errors = validate_manifest(ROOT, manifest_path)
    output = {
        "schema": "aletheia.bh-sdp-v2.3-validation.v1",
        "protocol_version": PROTOCOL_VERSION,
        "snapshots_discovered": len(paths),
        "snapshots_pass": len(paths) - failed,
        "manifest_state": "PASS" if args.verify_manifest and not manifest_errors else ("FAIL" if args.verify_manifest else "NOT_REQUESTED"),
        "manifest_errors": manifest_errors,
        "state": "PASS" if paths and not failed and not manifest_errors else "FAIL",
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0 if output["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
