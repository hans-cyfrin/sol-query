import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from sol_query.query.engine_v2 import SolidityQueryEngineV2


@pytest.fixture(scope="session")
def fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture(scope="session")
def engine(fixtures_root: Path) -> SolidityQueryEngineV2:
    engine = SolidityQueryEngineV2()
    # Prefer absolute paths
    sources: List[os.PathLike] = [
        fixtures_root / "composition_and_imports",
        fixtures_root / "detailed_scenarios",
        fixtures_root / "sample_contract.sol",
    ]
    engine.load_sources([str(p) for p in sources])
    return engine


def assert_success_response(resp: Dict[str, Any]) -> None:
    assert isinstance(resp, dict)
    assert resp.get("success") in (True, False)
    # query_info must exist and be well-formed
    q = resp.get("query_info", {})
    assert "function" in q
    assert "parameters" in q


def assert_query_results_shape(resp: Dict[str, Any], expected_type: Optional[str] = None) -> List[Dict[str, Any]]:
    assert_success_response(resp)
    assert resp.get("success") is True
    data = resp.get("data")
    assert isinstance(data, dict)
    results = data.get("results")
    assert isinstance(results, list)
    # Summary presence
    summary = data.get("summary")
    assert isinstance(summary, dict)
    assert "total_count" in summary
    # Optional type check
    if expected_type is not None and len(results) > 0:
        for item in results:
            assert item.get("type") == expected_type
    return results


def assert_includes_fields_if_present(item: Dict[str, Any], fields: List[str]) -> None:
    for f in fields:
        assert f in item


def assert_if_non_empty_all(results: List[Dict[str, Any]], predicate) -> None:
    if results:
        for r in results:
            assert predicate(r)


def ensure_location_present(results: List[Dict[str, Any]]) -> None:
    for r in results:
        loc = r.get("location", {})
        assert "file" in loc
        assert "contract" in loc


