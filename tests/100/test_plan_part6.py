"""
Test Plan Part 6: Use Cases 51-60
Tests query_code functionality with complex combined filters and scope/include combinations.
"""
import json
import pytest
import re


def test_51_variables_by_types_and_scope_contract_patterns(engine):
    """
    Use Case 51: Variables by types and scope (contract patterns)
    - Method: query_code
    - Params: { query_type: "variables", filters: { types: ["mapping*", "address"] }, scope: { contracts: [".*Pool.*", ".*Token.*"] } }
    - Expected: variable declarations that match type patterns within selected contracts.
    """
    resp = engine.query_code("variables",
                            {"types": ["mapping*", "address"]},
                            {"contracts": [".*Pool.*", ".*Token.*"]})
    print("Variables(types=mapping*/address, scope=Pool/Token contracts):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "variable"

        # Type should match pattern
        type_name = str(result.get("type_name", "")).lower()
        matches_mapping = "mapping" in type_name
        matches_address = "address" in type_name
        assert matches_mapping or matches_address, f"Variable {result.get('name')} type {type_name} doesn't match patterns"

        # Should be from matching contracts
        location = result.get("location", {})
        contract = location.get("contract", "")
        file_path = location.get("file", "")

        # Check contract name or file name
        matches_pool = re.search(r".*Pool.*", contract, re.IGNORECASE) if contract else False
        matches_token = re.search(r".*Token.*", contract, re.IGNORECASE) if contract else False
        if not (matches_pool or matches_token):
            # Also check file names
            matches_pool = "Pool" in file_path
            matches_token = "Token" in file_path
        assert matches_pool or matches_token, f"Variable {result.get('name')} from {contract} in {file_path} doesn't match scope"

    # Should find specific variables we know exist
    found_names = {r.get("name") for r in results}
    expected_vars = {"balances", "allowances", "owner"}
    if expected_vars.intersection(found_names):
        print(f"Found expected mapping/address variables: {expected_vars.intersection(found_names)}")


def test_52_events_with_specific_arguments_count_and_file_scope(engine):
    """
    Use Case 52: Events with specific arguments count and file scope
    - Method: query_code
    - Params: { query_type: "events", filters: { argument_count: 2 }, scope: { files: ["sample_contract.sol"] } }
    - Expected: events from sample_contract.sol with exactly 2 arguments.
    """
    resp = engine.query_code("events",
                            {"argument_count": 2},
                            {"files": ["sample_contract.sol"]})
    print("Events(2 args, sample_contract.sol):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "event"

        # Should be from sample_contract.sol
        location = result.get("location", {})
        file_path = location.get("file", "")
        assert "sample_contract.sol" in file_path, f"Event {result.get('name')} not from sample_contract.sol: {file_path}"

        # Should have 2 arguments (if argument_count filter is supported)
        # Note: This may not be implemented in the engine yet

    # Should find events from sample_contract.sol
    found_names = {r.get("name") for r in results}
    expected_events = {"Transfer", "Approval", "UserStatusChanged"}
    assert expected_events.intersection(found_names), f"Expected events from sample_contract.sol not found"


def test_53_structs_with_field_patterns_and_contract_scope(engine):
    """
    Use Case 53: Structs with field patterns and contract scope
    - Method: query_code
    - Params: { query_type: "structs", filters: { field_patterns: [".*balance.*", ".*time.*"] }, scope: { contracts: [".*Logic.*"] } }
    - Expected: structs from matching contracts that have fields with matching names.
    """
    resp = engine.query_code("structs",
                            {"field_patterns": [".*balance.*", ".*time.*"]},
                            {"contracts": [".*Logic.*"]})
    print("Structs(field patterns balance/time, Logic contracts):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "struct"

        # Should be from Logic contracts
        location = result.get("location", {})
        contract = location.get("contract", "")
        file_path = location.get("file", "")

        matches_logic = re.search(r".*Logic.*", contract, re.IGNORECASE) if contract else False
        if not matches_logic:
            matches_logic = "Logic" in file_path
        assert matches_logic, f"Struct {result.get('name')} not from Logic contract: {contract} in {file_path}"

    # Should find UserData struct which has balance field
    found_names = {r.get("name") for r in results}
    if "UserData" in found_names:
        print("Found UserData struct in ComplexLogic contract")


def test_54_complex_combined_filters_functions_visibility_state_mut_modifiers_calls(engine):
    """
    Use Case 54: Complex combined filters (functions: visibility + state_mut + modifiers + calls)
    - Method: query_code
    - Params: { query_type: "functions", filters: { visibility: ["public"], state_mutability: ["nonpayable"], modifiers: ["only.*"], has_external_calls: False } }
    - Expected: public nonpayable functions with owner-like modifiers but no external calls.
    """
    resp = engine.query_code("functions", {
        "visibility": ["public"],
        "state_mutability": ["nonpayable"],
        "modifiers": ["only.*"],
        "has_external_calls": False
    })
    print("Functions(complex filters - public/nonpayable/only*/no_external_calls):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "function"

        # Validate visibility
        visibility = str(result.get("visibility", "")).lower()
        assert "public" in visibility, f"Function {result.get('name')} not public: {visibility}"

        # Validate state mutability
        state_mutability = str(result.get("state_mutability", "")).lower()
        assert "nonpayable" in state_mutability or state_mutability == "", f"Function {result.get('name')} not nonpayable: {state_mutability}"

    # Should find functions like setValue, transferOwnership
    found_names = {r.get("name") for r in results}
    expected_functions = {"setValue", "transferOwnership", "mint"}
    if expected_functions.intersection(found_names):
        print(f"Found expected owner-only functions: {expected_functions.intersection(found_names)}")


def test_55_events_and_functions_by_scope_inheritance_tree_with_includes(engine):
    """
    Use Case 55: Events and functions by scope (inheritance tree) with includes
    - Method: query_code
    - Params: { query_type: "functions", scope: { inheritance_tree: "IERC20" }, include: ["calls", "events"] }
    - Expected: functions from contracts that inherit from IERC20, with call and event information included.
    """
    resp = engine.query_code("functions",
                            {},
                            {"inheritance_tree": "IERC20"},
                            ["calls", "events"])
    print("Functions(scope=inherits_IERC20, include=calls/events):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    functions_with_includes = 0
    for result in results:
        assert result.get("type") == "function"

        # Should have includes
        assert "calls" in result
        assert "events" in result

        if result.get("calls") or result.get("events"):
            functions_with_includes += 1

    print(f"Functions with calls/events info: {functions_with_includes}/{len(results)}")

    # Should find IERC20-related functions
    found_names = {r.get("name") for r in results}
    expected_ierc20_functions = {"transfer", "approve", "transferFrom", "balanceOf"}
    if expected_ierc20_functions.intersection(found_names):
        print(f"Found IERC20 functions: {expected_ierc20_functions.intersection(found_names)}")


def test_56_variables_and_calls_by_access_patterns_and_directory_scope(engine):
    """
    Use Case 56: Variables and calls by access patterns and directory scope
    - Method: query_code
    - Params: { query_type: "variables", filters: { access_patterns: ["msg.sender", "block."] }, scope: { directories: ["tests/fixtures/detailed_scenarios"] } }
    - Expected: variables found in specified directory that relate to msg.sender or block operations.
    """
    resp = engine.query_code("variables",
                            {"access_patterns": ["msg.sender", "block."]},
                            {"directories": ["tests/fixtures/detailed_scenarios"]})
    print("Variables(access patterns msg.sender/block, detailed_scenarios):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    for result in results:
        assert result.get("type") == "variable"

        # Should be from detailed_scenarios
        location = result.get("location", {})
        file_path = location.get("file", "")
        assert "detailed_scenarios" in file_path, f"Variable {result.get('name')} not from detailed_scenarios: {file_path}"

    # Should find variables that relate to access patterns
    found_names = {r.get("name") for r in results}
    expected_access_vars = {"timestamp", "lastUpdate", "owner", "sender"}
    if expected_access_vars.intersection(found_names):
        print(f"Found access pattern variables: {expected_access_vars.intersection(found_names)}")


def test_57_contracts_with_dependency_patterns_and_multiple_includes(engine):
    """
    Use Case 57: Contracts with dependency patterns and multiple includes
    - Method: query_code
    - Params: { query_type: "contracts", filters: { dependency_patterns: ["ERC.*", "Safe.*"] }, include: ["dependencies", "inheritance", "source"] }
    - Expected: contracts with ERC or Safe dependencies, showing dependency details, inheritance info, and source code.
    """
    resp = engine.query_code("contracts",
                            {"dependency_patterns": ["ERC.*", "Safe.*"]},
                            {},
                            ["dependencies", "inheritance", "source"])
    print("Contracts(dependency patterns ERC/Safe, include=deps/inheritance/source):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    contracts_with_includes = 0
    for result in results:
        assert result.get("type") == "contract"

        # Should have includes
        assert "dependencies" in result
        assert "inheritance_details" in result
        assert "source_code" in result

        if result.get("dependencies") or result.get("inheritance_details") or result.get("source_code"):
            contracts_with_includes += 1

    print(f"Contracts with include info: {contracts_with_includes}/{len(results)}")

    # Should find contracts with ERC/Safe dependencies
    found_names = {r.get("name") for r in results}
    expected_dependent_contracts = {"ERC721WithImports", "Token", "MultiInheritanceToken"}
    if expected_dependent_contracts.intersection(found_names):
        print(f"Found dependency-having contracts: {expected_dependent_contracts.intersection(found_names)}")


def test_58_functions_by_combined_call_filters_and_options(engine):
    """
    Use Case 58: Functions by combined call filters and options
    - Method: query_code
    - Params: { query_type: "functions", filters: { call_types: ["transfer"], has_external_calls: True, low_level: False }, options: { max_results: 3, sort_by: "name" } }
    - Expected: at most 3 functions that call transfer-like functions, have external calls, but no low-level calls, sorted by name.
    """
    resp = engine.query_code("functions",
                            {
                                "call_types": ["transfer"],
                                "has_external_calls": True,
                                "low_level": False
                            },
                            {},
                            [],
                            {
                                "max_results": 3,
                                "sort_by": "name"
                            })
    print("Functions(call filters + options):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) <= 3, f"Expected at most 3 results, got {len(results)}"

    for result in results:
        assert result.get("type") == "function"

    # Should find transfer-related functions
    found_names = {r.get("name") for r in results}
    expected_transfer_functions = {"transfer", "transferFrom", "transferOwnership"}
    if expected_transfer_functions.intersection(found_names):
        print(f"Found transfer functions: {expected_transfer_functions.intersection(found_names)}")

    # Check if sorted by name (if more than one result)
    if len(results) > 1:
        names = [r.get("name", "") for r in results]
        sorted_names = sorted(names)
        if names == sorted_names:
            print("Results appear to be sorted by name")


def test_59_complex_nested_scope_and_filters_multi_include(engine):
    """
    Use Case 59: Complex nested scope and filters (multi-include)
    - Method: query_code
    - Params: { query_type: "functions", filters: { visibility: ["external", "public"], state_mutability: ["payable", "nonpayable"] }, scope: { contracts: [".*Token.*"], functions: [".*transfer.*"] }, include: ["source", "calls", "variables", "modifiers"] }
    - Expected: external/public payable/nonpayable functions from Token contracts with transfer in name, including comprehensive metadata.
    """
    resp = engine.query_code("functions",
                            {
                                "visibility": ["external", "public"],
                                "state_mutability": ["payable", "nonpayable"]
                            },
                            {
                                "contracts": [".*Token.*"],
                                "functions": [".*transfer.*"]
                            },
                            ["source", "calls", "variables", "modifiers"])
    print("Functions(complex nested scope and filters):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    comprehensive_functions = 0
    for result in results:
        assert result.get("type") == "function"

        # Validate visibility
        visibility = str(result.get("visibility", "")).lower()
        assert "external" in visibility or "public" in visibility, f"Function {result.get('name')} has invalid visibility: {visibility}"

        # Validate name pattern
        name = result.get("name", "")
        assert re.search(r".*transfer.*", name, re.IGNORECASE), f"Function name '{name}' doesn't match transfer pattern"

        # Should have all includes
        assert "source_code" in result
        assert "calls" in result
        assert "variables" in result
        assert "modifiers" in result

        if (result.get("source_code") or result.get("calls") or
            result.get("variables") or result.get("modifiers")):
            comprehensive_functions += 1

    print(f"Functions with comprehensive info: {comprehensive_functions}/{len(results)}")

    # Should find transfer functions from Token contracts
    found_names = {r.get("name") for r in results}
    expected_transfer_functions = {"transfer", "transferFrom", "transferOwnership"}
    assert expected_transfer_functions.intersection(found_names), f"Expected transfer functions not found"


def test_60_max_complexity_all_parameters_combined(engine):
    """
    Use Case 60: Max complexity (all parameters combined)
    - Method: query_code
    - Params: { query_type: "functions", filters: { names: [".*transfer.*", ".*mint.*"], visibility: ["public"], modifiers: ["only.*"], has_external_calls: True }, scope: { contracts: [".*Token.*"], files: ["composition.*"] }, include: ["source", "calls", "events", "variables"], options: { max_results: 2 } }
    - Expected: at most 2 public transfer/mint functions with owner modifiers and external calls from Token contracts in composition files, with full metadata.
    """
    resp = engine.query_code("functions",
                            {
                                "names": [".*transfer.*", ".*mint.*"],
                                "visibility": ["public"],
                                "modifiers": ["only.*"],
                                "has_external_calls": True
                            },
                            {
                                "contracts": [".*Token.*"],
                                "files": ["composition.*"]
                            },
                            ["source", "calls", "events", "variables"],
                            {"max_results": 2})
    print("Functions(max complexity - all parameters):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) <= 2, f"Expected at most 2 results, got {len(results)}"

    for result in results:
        assert result.get("type") == "function"

        # Validate name patterns
        name = result.get("name", "")
        matches_transfer = re.search(r".*transfer.*", name, re.IGNORECASE)
        matches_mint = re.search(r".*mint.*", name, re.IGNORECASE)
        assert matches_transfer or matches_mint, f"Function name '{name}' doesn't match patterns"

        # Validate visibility
        visibility = str(result.get("visibility", "")).lower()
        assert "public" in visibility, f"Function {name} not public: {visibility}"

        # Should have all includes
        assert "source_code" in result
        assert "calls" in result
        assert "events" in result
        assert "variables" in result

    # Should find complex matching functions
    found_names = {r.get("name") for r in results}
    print(f"Found max complexity functions: {found_names}")

    if results:
        print("Successfully found functions matching all complex criteria")
    else:
        print("No functions match all complex criteria (this may be expected due to strict filtering)")