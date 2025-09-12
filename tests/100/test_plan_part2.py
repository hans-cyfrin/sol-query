"""
Test Plan Part 2: Use Cases 11-20
Tests query_code functionality with filters and basic filtering.
"""
import json
import pytest
import re


def test_11_query_calls(engine):
    """
    Use Case 11: Query calls
    - Method: query_code
    - Params: { query_type: "calls" }
    - Expected: results are call-like mock nodes with name/call_type when available; empty list allowed.
    """
    resp = engine.query_code("calls")
    print("Calls(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate call structure
    for result in results:
        assert result.get("type") == "call"
        assert "location" in result

    # Should find several calls across fixtures
    if results:
        assert len(results) > 10

        # Look for specific calls we know exist
        call_names = {r.get("name", "") for r in results}
        # Should find calls like transfer, mint, etc.
        expected_calls = {"transfer", "mint", "_safeMint"}
        found_calls = {name for name in call_names if any(exp in name.lower() for exp in expected_calls)}
        assert len(found_calls) > 0


def test_12_query_flow_placeholder(engine):
    """
    Use Case 12: Query flow (placeholder)
    - Method: query_code
    - Params: { query_type: "flow" }
    - Expected: success=True, may return empty results (supported as a valid type).
    """
    resp = engine.query_code("flow")
    print("Flow(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    # Empty list is allowed - this is a placeholder type


def test_13_functions_by_name_pattern_single(engine):
    """
    Use Case 13: Functions by name pattern (single)
    - Method: query_code
    - Params: { query_type: "functions", filters: { names: "transfer.*" } }
    - Expected: results where name matches the regex; zero or more matches.
    """
    resp = engine.query_code("functions", {"names": "transfer.*"})
    print("Functions(names=transfer.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find transfer-related functions
    expected_transfer_functions = {"transfer", "transferFrom", "transferOwnership", "transferWithMath", "transferWithCall"}
    found_functions = {r.get("name") for r in results}

    # Validate regex matching
    for result in results:
        name = result.get("name", "")
        assert re.search(r"transfer.*", name, re.IGNORECASE), f"Function '{name}' doesn't match pattern"

    # Should find some of the expected transfer functions
    assert expected_transfer_functions.intersection(found_functions), f"Expected some transfer functions, got: {found_functions}"

    # Validate specific functions exist with proper details
    if "transfer" in found_functions:
        transfer_func = next(r for r in results if r.get("name") == "transfer")
        assert transfer_func.get("type") == "function"
        assert "location" in transfer_func


def test_14_functions_by_name_patterns_multiple(engine):
    """
    Use Case 14: Functions by name patterns (multiple)
    - Method: query_code
    - Params: { query_type: "functions", filters: { names: ["approve", ".*mint.*"] } }
    - Expected: names in set; verify matching on both exact and regex.
    """
    resp = engine.query_code("functions", {"names": ["approve", ".*mint.*"]})
    print("Functions(names=approve|.*mint.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate that results match either pattern
    for result in results:
        name = result.get("name", "")
        matches_approve = name == "approve"
        matches_mint = re.search(r".*mint.*", name, re.IGNORECASE)
        assert matches_approve or matches_mint, f"Function '{name}' doesn't match either pattern"

    # Should find approve function and mint functions
    found_names = {r.get("name") for r in results}
    assert "approve" in found_names, "Should find exact 'approve' function"
    mint_functions = {name for name in found_names if "mint" in name.lower()}
    assert len(mint_functions) > 0, "Should find mint-related functions"


def test_15_functions_by_visibility_public_external(engine):
    """
    Use Case 15: Functions by visibility (public/external)
    - Method: query_code
    - Params: { query_type: "functions", filters: { visibility: ["public", "external"] } }
    - Expected: every result has visibility in provided list.
    """
    resp = engine.query_code("functions", {"visibility": ["public", "external"]})
    print("Functions(visibility=public|external):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many public/external functions

    # Validate visibility filtering
    for result in results:
        visibility = str(result.get("visibility", "")).lower()
        assert "public" in visibility or "external" in visibility, f"Function {result.get('name')} has invalid visibility: {visibility}"

    # Should find specific functions we know are public/external
    found_names = {r.get("name") for r in results}
    expected_functions = {"deposit", "viewFunction", "pureFunction", "mint", "transfer"}
    assert expected_functions.intersection(found_names), f"Expected public/external functions not found in: {found_names}"


def test_16_functions_by_state_mutability_view(engine):
    """
    Use Case 16: Functions by state mutability (view)
    - Method: query_code
    - Params: { query_type: "functions", filters: { state_mutability: "view" } }
    - Expected: each result has state_mutability "view".
    """
    resp = engine.query_code("functions", {"state_mutability": "view"})
    print("Functions(state_mutability=view):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate state mutability filtering
    for result in results:
        state_mutability = str(result.get("state_mutability", "")).lower()
        assert "view" in state_mutability, f"Function {result.get('name')} has invalid state_mutability: {state_mutability}"

    # Should find specific view functions
    found_names = {r.get("name") for r in results}
    expected_view_functions = {"viewFunction", "balanceOf", "totalSupply", "name", "symbol"}
    assert expected_view_functions.intersection(found_names), f"Expected view functions not found"


def test_17_functions_with_no_modifiers(engine):
    """
    Use Case 17: Functions with no modifiers
    - Method: query_code
    - Params: { query_type: "functions", filters: { modifiers: [] } }
    - Expected: results whose modifier list is empty or absent.
    """
    resp = engine.query_code("functions", {"modifiers": []})
    print("Functions(no modifiers):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions without modifiers
    assert len(results) > 30  # Many functions don't have modifiers

    # Should include functions we know don't have modifiers
    found_names = {r.get("name") for r in results}
    expected_no_modifier_functions = {"deposit", "viewFunction", "pureFunction"}
    assert expected_no_modifier_functions.intersection(found_names)


def test_18_functions_with_specific_modifiers(engine):
    """
    Use Case 18: Functions with specific modifiers
    - Method: query_code
    - Params: { query_type: "functions", filters: { modifiers: ["only.*"] } }
    - Expected: functions that include any modifier matching the regex.
    """
    resp = engine.query_code("functions", {"modifiers": ["only.*"]})
    print("Functions(modifiers=only.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions with onlyOwner, onlyMinter etc. modifiers
    found_names = {r.get("name") for r in results}
    expected_modifier_functions = {"setValue", "mint", "transferOwnership"}
    assert expected_modifier_functions.intersection(found_names), f"Expected functions with only* modifiers"


def test_19_functions_filtered_by_contract_names(engine):
    """
    Use Case 19: Functions filtered by contract names (filters)
    - Method: query_code
    - Params: { query_type: "functions", filters: { contracts: [".*Token.*", ".*NFT.*"] } }
    - Expected: results belong to contracts whose names match these regexes.
    """
    resp = engine.query_code("functions", {"contracts": [".*Token.*", ".*NFT.*"]})
    print("Functions(contracts=.*Token.*|.*NFT.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate contract filtering
    for result in results:
        location = result.get("location", {})
        contract = location.get("contract", "")
        file_path = location.get("file", "")

        # Should be from Token or NFT contracts
        matches_token = re.search(r".*Token.*", contract, re.IGNORECASE) if contract else False
        matches_nft = re.search(r".*NFT.*", contract, re.IGNORECASE) if contract else False

        # Also check file names if contract name is not available
        if not matches_token and not matches_nft:
            matches_token = "Token" in file_path
            matches_nft = "NFT" in file_path

        assert matches_token or matches_nft, f"Function {result.get('name')} from {contract} in {file_path} doesn't match filter"

    # Should find functions from Token contracts
    found_names = {r.get("name") for r in results}
    expected_token_functions = {"mint", "transfer", "approve", "balanceOf"}
    assert expected_token_functions.intersection(found_names)


def test_20_variables_by_type_uint_patterns(engine):
    """
    Use Case 20: Variables by type (uint patterns)
    - Method: query_code
    - Params: { query_type: "variables", filters: { types: ["uint.*", "mapping.*"] } }
    - Expected: variables whose type_name/var_type matches patterns.
    """
    resp = engine.query_code("variables", {"types": ["uint.*", "mapping.*"]})
    print("Variables(types=uint.*|mapping.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate type filtering
    for result in results:
        type_name = str(result.get("type_name", "")).lower()
        matches_uint = re.search(r"uint.*", type_name, re.IGNORECASE)
        matches_mapping = re.search(r"mapping.*", type_name, re.IGNORECASE)
        assert matches_uint or matches_mapping, f"Variable {result.get('name')} has type {type_name} which doesn't match patterns"

    # Should find variables with these types
    found_names = {r.get("name") for r in results}
    expected_variables = {"value", "totalSupply", "balances", "price", "nextTokenId"}
    assert expected_variables.intersection(found_names), f"Expected uint/mapping variables not found"

    # Validate specific variable types
    variables_by_name = {r.get("name"): r for r in results}

    if "value" in variables_by_name:
        value_var = variables_by_name["value"]
        assert "uint256" in str(value_var.get("type_name", "")).lower()

    if "balances" in variables_by_name:
        balances_var = variables_by_name["balances"]
        assert "mapping" in str(balances_var.get("type_name", "")).lower()