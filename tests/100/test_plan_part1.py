"""
Test Plan Part 1: Use Cases 1-10
Tests basic query_code functionality for all element types.
"""
import json
import pytest


def test_01_query_all_contracts(engine):
    """
    Use Case 1: Query all contracts
    - Method: query_code
    - Params: { query_type: "contracts", filters: {}, scope: {}, include: [], options: {} }
    - Expected: success=True; data.results[] elements with type="ContractDeclaration"; each has location.file and location.contract.
    """
    resp = engine.query_code("contracts", {}, {}, [])
    print("Contracts(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) == 25  # Expected count from fixtures

    # Validate specific contracts with exact details
    found_contracts = {result.get("name"): result for result in results if result.get("type") == "contract"}

    # Test SimpleContract details
    simple_contract = found_contracts.get("SimpleContract")
    assert simple_contract is not None
    assert simple_contract["location"]["line"] == 7
    assert simple_contract["location"]["column"] == 1
    assert "SimpleContract.sol" in simple_contract["location"]["file"]
    assert simple_contract["kind"] == "contract"
    assert simple_contract["inheritance"] == []

    # Test ERC721WithImports details
    erc721_contract = found_contracts.get("ERC721WithImports")
    assert erc721_contract is not None
    assert erc721_contract["location"]["line"] == 13
    assert erc721_contract["inheritance"] == ["ERC721"]
    assert "ERC721WithImports.sol" in erc721_contract["location"]["file"]

    # Test MultiInheritanceToken details
    multi_contract = found_contracts.get("MultiInheritanceToken")
    assert multi_contract is not None
    assert multi_contract["location"]["line"] == 54
    assert multi_contract["inheritance"] == ["BaseToken"]
    assert "MultipleInheritance.sol" in multi_contract["location"]["file"]

    # Test interfaces are correctly identified
    ilzr_interface = next((r for r in results if r.get("name") == "ILayerZeroReceiver" and "interfaces" in r["location"]["file"]), None)
    assert ilzr_interface is not None
    assert ilzr_interface["kind"] == "interface"
    assert ilzr_interface["location"]["line"] == 4

    # Test libraries are correctly identified
    safemath_lib = next((r for r in results if r.get("name") == "SafeMath" and "libraries" in r["location"]["file"]), None)
    assert safemath_lib is not None
    assert safemath_lib["kind"] == "library"
    assert safemath_lib["location"]["line"] == 4


def test_02_query_all_functions(engine):
    """
    Use Case 2: Query all functions
    - Method: query_code
    - Params: { query_type: "functions" }
    - Expected: results contain type="FunctionDeclaration", each with name and visibility fields present.
    """
    resp = engine.query_code("functions")
    print("Functions(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 50  # Should find many functions across all contracts

    # Validate function structure
    for result in results:
        assert result.get("type") == "function"
        assert "name" in result
        assert "visibility" in result
        assert "location" in result

    # Test specific functions from SimpleContract
    simple_functions = [r for r in results if "SimpleContract.sol" in r.get("location", {}).get("file", "")]
    function_names = {f["name"] for f in simple_functions}
    expected_simple_functions = {"pureFunction", "viewFunction", "setValue", "deposit", "internalHelper", "privateHelper"}
    assert expected_simple_functions.issubset(function_names)

    # Test pureFunction details
    pure_func = next(f for f in simple_functions if f["name"] == "pureFunction")
    assert pure_func["location"]["line"] == 22
    assert "public" in str(pure_func["visibility"]).lower()
    assert "pure" in str(pure_func.get("state_mutability", "")).lower()

    # Test deposit function (payable)
    deposit_func = next(f for f in simple_functions if f["name"] == "deposit")
    assert deposit_func["location"]["line"] == 37
    assert "payable" in str(deposit_func.get("state_mutability", "")).lower()

    # Test private function
    private_func = next(f for f in simple_functions if f["name"] == "privateHelper")
    assert private_func["location"]["line"] == 47
    assert "private" in str(private_func["visibility"]).lower()


def test_03_query_all_variables(engine):
    """
    Use Case 3: Query all variables
    - Method: query_code
    - Params: { query_type: "variables" }
    - Expected: results contain type="VariableDeclaration", include visibility and is_state_variable when available.
    """
    resp = engine.query_code("variables")
    print("Variables(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many variables

    # Validate variable structure
    for result in results:
        assert result.get("type") == "variable"
        assert "name" in result
        assert "visibility" in result
        assert "is_state_variable" in result

    # Test SimpleContract variables
    simple_vars = [r for r in results if "SimpleContract.sol" in r.get("location", {}).get("file", "")]
    var_names = {v["name"] for v in simple_vars}
    expected_vars = {"value", "owner"}
    assert expected_vars.issubset(var_names)

    # Test value variable details
    value_var = next(v for v in simple_vars if v["name"] == "value")
    assert value_var["location"]["line"] == 8
    assert value_var["is_state_variable"] is True
    assert "uint256" in str(value_var.get("type_name", "")).lower()
    assert "public" in str(value_var["visibility"]).lower()

    # Test owner variable details
    owner_var = next(v for v in simple_vars if v["name"] == "owner")
    assert owner_var["location"]["line"] == 9
    assert owner_var["is_state_variable"] is True
    assert "address" in str(owner_var.get("type_name", "")).lower()


def test_04_query_all_events(engine):
    """
    Use Case 4: Query all events
    - Method: query_code
    - Params: { query_type: "events" }
    - Expected: elements of type="EventDeclaration" with location details.
    """
    resp = engine.query_code("events")
    print("Events(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 5  # Should find several events

    # Validate event structure
    for result in results:
        assert result.get("type") == "event"
        assert "name" in result
        assert "location" in result

    # Test specific events from ERC721WithImports
    erc721_events = [r for r in results if "ERC721WithImports.sol" in r.get("location", {}).get("file", "")]
    event_names = {e["name"] for e in erc721_events}
    expected_events = {"TokenMinted", "PriceUpdated"}
    assert expected_events.issubset(event_names)

    # Test TokenMinted event details
    token_minted = next(e for e in erc721_events if e["name"] == "TokenMinted")
    assert token_minted["location"]["line"] == 23
    assert "ERC721WithImports.sol" in token_minted["location"]["file"]

    # Test events from sample_contract.sol (Token contract area)
    token_events = [r for r in results if "sample_contract.sol" in r.get("location", {}).get("file", "")]
    token_event_names = {e["name"] for e in token_events}
    expected_token_events = {"Transfer", "Approval", "OwnershipTransferred"}
    # Verify these events exist in sample_contract.sol
    sample_events = [e for e in token_events if e["name"] in expected_token_events]
    assert len(sample_events) == 3  # Should find all 3 events


def test_05_query_all_modifiers(engine):
    """
    Use Case 5: Query all modifiers
    - Method: query_code
    - Params: { query_type: "modifiers" }
    - Expected: elements of type="ModifierDeclaration" with names.
    """
    resp = engine.query_code("modifiers")
    print("Modifiers(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 5  # Should find several modifiers

    # Validate modifier structure
    for result in results:
        assert result.get("type") == "modifier"
        assert "name" in result
        assert "location" in result

    # Test SimpleContract onlyOwner modifier
    simple_modifiers = [r for r in results if "SimpleContract.sol" in r.get("location", {}).get("file", "")]
    modifier_names = {m["name"] for m in simple_modifiers}
    assert "onlyOwner" in modifier_names

    only_owner = next(m for m in simple_modifiers if m["name"] == "onlyOwner")
    assert only_owner["location"]["line"] == 11

    # Test modifiers from sample_contract.sol
    token_modifiers = [r for r in results if "sample_contract.sol" in r.get("location", {}).get("file", "")]
    token_modifier_names = {m["name"] for m in token_modifiers}
    expected_modifiers = {"onlyOwner", "validAddress"}
    assert expected_modifiers.issubset(token_modifier_names)


def test_06_query_all_errors(engine):
    """
    Use Case 6: Query all errors
    - Method: query_code
    - Params: { query_type: "errors" }
    - Expected: elements of type="ErrorDeclaration" (if present); empty list allowed.
    """
    resp = engine.query_code("errors")
    print("Errors(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate error structure
    for result in results:
        assert result.get("type") == "error"
        assert "name" in result
        assert "location" in result

    # Test errors from sample_contract.sol
    if results:  # If errors exist
        token_errors = [r for r in results if "sample_contract.sol" in r.get("location", {}).get("file", "")]
        if token_errors:
            error_names = {e["name"] for e in token_errors}
            expected_errors = {"InsufficientBalance", "InsufficientAllowance"}
            assert expected_errors.issubset(error_names)

            # Test InsufficientBalance error details
            if "InsufficientBalance" in error_names:
                insuff_balance = next(e for e in token_errors if e["name"] == "InsufficientBalance")
                assert insuff_balance["location"]["line"] == 28


def test_07_query_all_structs(engine):
    """
    Use Case 7: Query all structs
    - Method: query_code
    - Params: { query_type: "structs" }
    - Expected: elements of type="StructDeclaration"; empty list allowed.
    """
    resp = engine.query_code("structs")
    print("Structs(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate struct structure
    for result in results:
        assert result.get("type") == "struct"
        assert "name" in result
        assert "location" in result

    # Test UserData struct from sample_contract.sol
    if results:
        sample_structs = [r for r in results if "sample_contract.sol" in r.get("location", {}).get("file", "")]
        if sample_structs:
            struct_names = {s["name"] for s in sample_structs}
            assert "UserData" in struct_names

            user_data = next(s for s in sample_structs if s["name"] == "UserData")
            assert 150 <= user_data["location"]["line"] <= 160  # Around line 153-157


def test_08_query_all_enums(engine):
    """
    Use Case 8: Query all enums
    - Method: query_code
    - Params: { query_type: "enums" }
    - Expected: elements of type="EnumDeclaration"; empty list allowed.
    """
    resp = engine.query_code("enums")
    print("Enums(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate enum structure (if any exist)
    for result in results:
        assert result.get("type") == "enum"
        assert "name" in result
        assert "location" in result

    # Current fixtures don't have enums, so empty list is expected
    # This test validates the API works correctly for enums


def test_09_query_statements(engine):
    """
    Use Case 9: Query statements
    - Method: query_code
    - Params: { query_type: "statements" }
    - Expected: elements of type="Statement"; empty list allowed.
    """
    resp = engine.query_code("statements")
    print("Statements(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate statement structure
    for result in results:
        assert result.get("type") == "statement"
        assert "location" in result

    # Should find many statements across all contracts
    if results:
        assert len(results) > 20


def test_10_query_expressions(engine):
    """
    Use Case 10: Query expressions
    - Method: query_code
    - Params: { query_type: "expressions" }
    - Expected: elements of type="Expression"; empty list allowed.
    """
    resp = engine.query_code("expressions")
    print("Expressions(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate expression structure
    for result in results:
        assert result.get("type") == "expression"
        assert "location" in result

    # Should find many expressions across all contracts
    if results:
        assert len(results) > 50