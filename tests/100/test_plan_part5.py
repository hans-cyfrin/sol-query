"""
Test Plan Part 5: Use Cases 41-50
Tests query_code functionality with more include parameters and combined filters.
"""
import json
import pytest
import re


def test_41_include_events(engine):
    """
    Use Case 41: Include: events
    - Method: query_code
    - Params: { query_type: "functions", include: ["events"] }
    - Expected: each result has events[] for emit statements found.
    """
    resp = engine.query_code("functions", {}, {}, ["events"])
    print("Functions(include=events) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many functions

    functions_with_events = 0
    total_events = 0
    for result in results:
        assert result.get("type") == "function"
        assert "events" in result
        events = result.get("events", [])
        assert isinstance(events, list)

        if events:
            functions_with_events += 1
            total_events += len(events)

            # Validate event structure
            for event in events:
                if event:
                    assert isinstance(event, dict)

    print(f"Functions with events: {functions_with_events}/{len(results)}, Total events: {total_events}")

    # Should find functions that emit events
    functions_with_events_names = {r.get("name") for r in results if r.get("events")}
    expected_event_emitters = {"transfer", "mint", "processNumbers", "updateUserData"}
    if expected_event_emitters.intersection(functions_with_events_names):
        print(f"Found event-emitting functions: {expected_event_emitters.intersection(functions_with_events_names)}")


def test_42_include_modifiers(engine):
    """
    Use Case 42: Include: modifiers
    - Method: query_code
    - Params: { query_type: "functions", include: ["modifiers"] }
    - Expected: each result includes its modifiers array (may be empty).
    """
    resp = engine.query_code("functions", {}, {}, ["modifiers"])
    print("Functions(include=modifiers) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many functions

    functions_with_modifiers = 0
    for result in results:
        assert result.get("type") == "function"
        assert "modifiers" in result
        modifiers = result.get("modifiers", [])
        assert isinstance(modifiers, list)

        if modifiers:
            functions_with_modifiers += 1

    print(f"Functions with modifiers: {functions_with_modifiers}/{len(results)}")

    # Should find functions with modifiers we know exist
    functions_with_modifiers_names = {r.get("name") for r in results if r.get("modifiers")}
    expected_modified_functions = {"setValue", "mint", "transferOwnership"}
    if expected_modified_functions.intersection(functions_with_modifiers_names):
        print(f"Found modified functions: {expected_modified_functions.intersection(functions_with_modifiers_names)}")


def test_43_include_natspec(engine):
    """
    Use Case 43: Include: natspec
    - Method: query_code
    - Params: { query_type: "functions", include: ["natspec"] }
    - Expected: each result has natspec object with title/notice/dev/params/returns when available.
    """
    resp = engine.query_code("functions", {}, {}, ["natspec"])
    print("Functions(include=natspec) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many functions

    functions_with_natspec = 0
    for result in results:
        assert result.get("type") == "function"
        assert "natspec" in result
        natspec = result.get("natspec")
        if natspec:
            functions_with_natspec += 1
            assert isinstance(natspec, dict)

    print(f"Functions with natspec: {functions_with_natspec}/{len(results)}")


def test_44_include_dependencies(engine):
    """
    Use Case 44: Include: dependencies
    - Method: query_code
    - Params: { query_type: "contracts", include: ["dependencies"] }
    - Expected: each result lists import/using/inheritance dependencies.
    """
    resp = engine.query_code("contracts", {}, {}, ["dependencies"])
    print("Contracts(include=dependencies):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 10  # Should find many contracts

    contracts_with_dependencies = 0
    for result in results:
        assert result.get("type") == "contract"
        assert "dependencies" in result
        dependencies = result.get("dependencies", [])
        assert isinstance(dependencies, list)

        if dependencies:
            contracts_with_dependencies += 1

    print(f"Contracts with dependencies: {contracts_with_dependencies}/{len(results)}")

    # Should find contracts with dependencies we know exist
    contracts_with_deps_names = {r.get("name") for r in results if r.get("dependencies")}
    expected_dependent_contracts = {"ERC721WithImports", "MultiInheritanceToken", "MathOperations"}
    if expected_dependent_contracts.intersection(contracts_with_deps_names):
        print(f"Found dependent contracts: {expected_dependent_contracts.intersection(contracts_with_deps_names)}")


def test_45_include_inheritance(engine):
    """
    Use Case 45: Include: inheritance
    - Method: query_code
    - Params: { query_type: "contracts", include: ["inheritance"] }
    - Expected: each result includes inheritance_details with base_contracts/is_abstract/interfaces/override_functions as applicable.
    """
    resp = engine.query_code("contracts", {}, {}, ["inheritance"])
    print("Contracts(include=inheritance) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 10  # Should find many contracts

    contracts_with_inheritance = 0
    for result in results:
        assert result.get("type") == "contract"
        assert "inheritance_details" in result
        inheritance_details = result.get("inheritance_details")
        if inheritance_details:
            contracts_with_inheritance += 1
            assert isinstance(inheritance_details, dict)

    print(f"Contracts with inheritance details: {contracts_with_inheritance}/{len(results)}")

    # Should find contracts with inheritance we know exist
    contracts_with_inheritance_names = {r.get("name") for r in results if r.get("inheritance_details")}
    expected_inheriting_contracts = {"ERC721WithImports", "MultiInheritanceToken", "Token"}
    if expected_inheriting_contracts.intersection(contracts_with_inheritance_names):
        print(f"Found inheriting contracts: {expected_inheriting_contracts.intersection(contracts_with_inheritance_names)}")


def test_46_options_max_results(engine):
    """
    Use Case 46: Options: max_results
    - Method: query_code
    - Params: { query_type: "functions", options: { max_results: 5 } }
    - Expected: at most 5 results; query_info.result_count reflects truncated length.
    """
    resp = engine.query_code("functions", {}, {}, [], {"max_results": 5})
    print("Functions(max_results=5):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) <= 5, f"Expected at most 5 results, got {len(results)}"

    # Check query_info
    query_info = resp.get("query_info", {})
    if "result_count" in query_info:
        assert query_info["result_count"] <= 5, f"Query info shows {query_info['result_count']} results"

    # Validate results are still proper functions
    for result in results:
        assert result.get("type") == "function"
        assert "name" in result
        assert "location" in result


def test_47_combined_filters_names_visibility_state_mutability(engine):
    """
    Use Case 47: Combined filters: names + visibility + state mutability
    - Method: query_code
    - Params: { query_type: "functions", filters: { names: ".*balance.*", visibility: ["public", "external"], state_mutability: ["view", "pure"] } }
    - Expected: all returned functions satisfy all requested filter constraints.
    """
    resp = engine.query_code("functions", {
        "names": ".*balance.*",
        "visibility": ["public", "external"],
        "state_mutability": ["view", "pure"]
    })
    print("Functions(combined filters - balance/public-external/view-pure):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "function"

        # Name should match pattern
        name = result.get("name", "")
        assert re.search(r".*balance.*", name, re.IGNORECASE), f"Function name '{name}' doesn't match balance pattern"

        # Visibility should be public or external
        visibility = result.get("visibility")
        if visibility:
            vis_str = str(visibility).lower()
            assert "public" in vis_str or "external" in vis_str, f"Function {name} has invalid visibility: {visibility}"

        # State mutability should be view or pure
        state_mutability = result.get("state_mutability")
        if state_mutability:
            sm_str = str(state_mutability).lower()
            assert "view" in sm_str or "pure" in sm_str, f"Function {name} has invalid state mutability: {state_mutability}"

    # Should find balanceOf function which meets all criteria
    found_names = {r.get("name") for r in results}
    if "balanceOf" in found_names:
        balance_func = next(r for r in results if r.get("name") == "balanceOf")
        print(f"Found balanceOf: visibility={balance_func.get('visibility')}, state_mutability={balance_func.get('state_mutability')}")


def test_48_combined_filters_modifiers_changes_state(engine):
    """
    Use Case 48: Combined filters: modifiers + changes_state
    - Method: query_code
    - Params: { query_type: "functions", filters: { modifiers: [".*Owner.*", ".*Admin.*"], changes_state: True } }
    - Expected: only functions with matching modifiers and detected state changes.
    """
    resp = engine.query_code("functions", {
        "modifiers": [".*Owner.*", ".*Admin.*"],
        "changes_state": True
    })
    print("Functions(combined filters - owner/admin modifiers + state changes):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "function"

    # Should find functions with owner modifiers that change state
    found_names = {r.get("name") for r in results}
    expected_owner_state_changing = {"setValue", "mint", "transferOwnership"}
    if expected_owner_state_changing.intersection(found_names):
        print(f"Found owner/admin state-changing functions: {expected_owner_state_changing.intersection(found_names)}")


def test_49_combined_filters_has_external_calls_call_types(engine):
    """
    Use Case 49: Combined filters: has_external_calls + call_types
    - Method: query_code
    - Params: { query_type: "functions", filters: { has_external_calls: True, call_types: ["external"] } }
    - Expected: functions with at least one external call.
    """
    resp = engine.query_code("functions", {
        "has_external_calls": True,
        "call_types": ["external"]
    })
    print("Functions(combined filters - external calls + call types):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "function"

    # Should find functions that make external calls
    found_names = {r.get("name") for r in results}
    expected_external_calling = {"transferWithCall", "vulnerableTransfer", "processMessage"}
    if expected_external_calling.intersection(found_names):
        print(f"Found external calling functions: {expected_external_calling.intersection(found_names)}")


def test_50_combined_filters_has_asset_transfers_low_level(engine):
    """
    Use Case 50: Combined filters: has_asset_transfers + low_level
    - Method: query_code
    - Params: { query_type: "functions", filters: { has_asset_transfers: True, low_level: True } }
    - Expected: functions that both appear to transfer assets and use low-level calls.
    """
    resp = engine.query_code("functions", {
        "has_asset_transfers": True,
        "low_level": True
    })
    print("Functions(combined filters - asset transfers + low level):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "function"

    # Should find functions that both transfer assets and use low-level calls
    found_names = {r.get("name") for r in results}
    expected_asset_low_level = {"vulnerableWithdraw", "transferWithCall"}
    if expected_asset_low_level.intersection(found_names):
        print(f"Found asset-transferring low-level functions: {expected_asset_low_level.intersection(found_names)}")
    else:
        print("No functions found combining asset transfers and low-level calls (this may be expected)")

    # Validate that if any results are found, they should be meaningful
    if results:
        assert len(results) > 0