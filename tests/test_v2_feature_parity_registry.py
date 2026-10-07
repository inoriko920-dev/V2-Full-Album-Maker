from __future__ import annotations

import ast
from pathlib import Path

from full_album_maker.feature_parity_registry import (
    CONTRACT_IDS,
    DEFAULT_FEATURE_PARITY_REGISTRY,
    FeatureStatus,
    REQUIRED_AREAS,
)


ROOT = Path(__file__).resolve().parents[1]
CHARACTERIZATION_MAP = (
    ROOT / "docs" / "implementation" / "M0_T1_FEATURE_PARITY_CHARACTERIZATION_MAP.md"
)


def _expected_feature_ids() -> set[str]:
    counts = {
        "HOME": 4,
        "MEDIA": 6,
        "ALBUM": 6,
        "TIMELINE": 7,
        "VISUAL": 5,
        "TEMPLATE": 4,
        "SPECTRUM": 5,
        "AI": 5,
        "RENDER": 6,
        "PORTABLE": 2,
        "OFFLINE": 1,
    }
    return {
        f"FP-{area}-{index:02d}"
        for area, count in counts.items()
        for index in range(1, count + 1)
    }


def _test_functions(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def test_m0_registry_structure_is_valid_and_complete() -> None:
    registry = DEFAULT_FEATURE_PARITY_REGISTRY

    assert registry.validate() == ()
    assert len(registry.all()) == 51
    assert {entry.feature_id for entry in registry.all()} == _expected_feature_ids()
    assert {entry.area for entry in registry.all()} == set(REQUIRED_AREAS)
    assert all(entry.status is FeatureStatus.MUST_KEEP for entry in registry.all())


def test_every_registry_test_reference_exists_and_names_a_real_test() -> None:
    missing_files: list[str] = []
    missing_nodes: list[str] = []

    for entry in DEFAULT_FEATURE_PARITY_REGISTRY.all():
        for evidence in entry.evidence:
            test_path = ROOT / evidence.file
            if not test_path.is_file():
                missing_files.append(f"{entry.feature_id}: {evidence.file}")
                continue

            available = _test_functions(test_path)
            for test_name in evidence.tests:
                if test_name not in available:
                    missing_nodes.append(
                        f"{entry.feature_id}: {evidence.file}::{test_name}"
                    )

    assert missing_files == []
    assert missing_nodes == []


def test_every_registry_workflow_reference_exists() -> None:
    missing: list[str] = []

    for entry in DEFAULT_FEATURE_PARITY_REGISTRY.all():
        for workflow in entry.workflow_evidence:
            if not (ROOT / workflow).is_file():
                missing.append(f"{entry.feature_id}: {workflow}")

    assert missing == []


def test_registry_contract_references_are_known_and_behavioral() -> None:
    used_contracts = {
        contract
        for entry in DEFAULT_FEATURE_PARITY_REGISTRY.all()
        for contract in entry.contracts
    }

    assert used_contracts <= CONTRACT_IDS
    # Runtime/user-facing parity intentionally covers C-02..C-20 where relevant.
    # C-01 (old repository read-only) is a repository-governance boundary rather
    # than an application feature and is verified outside this runtime registry.
    assert "C-01" not in used_contracts
    for required in ("C-02", "C-03", "C-04", "C-05", "C-06", "C-07", "C-08",
                     "C-09", "C-10", "C-11", "C-12", "C-13", "C-14", "C-15",
                     "C-16", "C-17", "C-18", "C-19", "C-20"):
        assert required in used_contracts


def test_characterization_map_contains_every_feature_id_and_governance_boundary() -> None:
    text = CHARACTERIZATION_MAP.read_text(encoding="utf-8")

    for entry in DEFAULT_FEATURE_PARITY_REGISTRY.all():
        assert entry.feature_id in text

    assert "C-01" in text
    assert "old repository read-only" in text.lower()
    assert "51" in text


def test_registry_is_read_only_from_callers_point_of_view() -> None:
    entries = DEFAULT_FEATURE_PARITY_REGISTRY.all()
    assert isinstance(entries, tuple)
    assert DEFAULT_FEATURE_PARITY_REGISTRY.get("FP-RENDER-05").feature.startswith(
        "ffprobe verification"
    )
    assert DEFAULT_FEATURE_PARITY_REGISTRY.by_area("home") == entries[:4]
