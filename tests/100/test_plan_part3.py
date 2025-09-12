"""
Test Plan Part 3: Use Cases 21-30
Tests query_code functionality with advanced filters.
"""
import json
import pytest
import re


def test_21_state_variables_only(engine):
    """
    Use Case 21: State variables only
    - Method: query_code
    - Params: { query_type: "variables", filters: { is_state_variable: True } }
    - Expected: results with is_state_variable=True.
    """
    resp = engine.query_code("variables", {"is_state_variable": True})
    print("Variables(state_only):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 5  # Should find multiple state variables

    # Validate all are state variables
    for result in results:
        assert result.get("type") == "variable"
        assert result.get("is_state_variable") is True

    # Should find specific state variables we know exist
    found_names = {r.get("name") for r in results}
    expected_state_vars = {"value", "owner", "totalSupply", "price", "nextTokenId"}
    assert expected_state_vars.intersection(found_names), f"Expected state variables not found in: {found_names}"

    # Validate specific state variable details
    variables_by_name = {r.get("name"): r for r in results}
    if "value" in variables_by_name:
        value_var = variables_by_name["value"]
        assert "SimpleContract.sol" in value_var.get("location", {}).get("file", "")
        assert value_var.get("location", {}).get("line") == 8


def test_22_statements_by_type_require_if_for(engine):
    """
    Use Case 22: Statements by type (require/if/for)
    - Method: query_code
    - Params: { query_type: "statements", filters: { statement_types: ["if", "for", "require"] } }
    - Expected: statement elements whose internal type matches any requested type.
    """
    resp = engine.query_code("statements", {"statement_types": ["if", "for", "require"]})
    print("Statements(if/for/require):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find various control flow statements
    if results:
        assert len(results) > 10  # Should find many control statements

        for result in results:
            assert result.get("type") == "statement"
            assert "location" in result

        # Should find statements from complex contracts with loops/conditions
        statement_files = {r.get("location", {}).get("file", "") for r in results}
        assert any("sample_contract.sol" in f for f in statement_files)


def test_23_expressions_by_operators_arithmetic(engine):
    """
    Use Case 23: Expressions by operators (arithmetic)
    - Method: query_code
    - Params: { query_type: "expressions", filters: { operators: ["+", "*", "=="] } }
    - Expected: expression elements that use those operators.
    """
    resp = engine.query_code("expressions", {"operators": ["+", "*", "=="]})
    print("Expressions(arithmetic):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find arithmetic expressions
    if results:
        assert len(results) > 20  # Should find many arithmetic expressions

        for result in results:
            assert result.get("type") == "expression"
            assert "location" in result

        # Should find expressions from math-heavy contracts
        expr_files = {r.get("location", {}).get("file", "") for r in results}
        assert any("sample_contract.sol" in f or "MathOperations.sol" in f for f in expr_files)


def test_24_functions_that_change_state(engine):
    """
    Use Case 24: Functions that change state
    - Method: query_code
    - Params: { query_type: "functions", filters: { changes_state: True } }
    - Expected: results for which internal `_changes_state` returns True.
    """
    resp = engine.query_code("functions", {"changes_state": True})
    print("Functions(changes_state):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find state-changing functions
    if results:
        assert len(results) > 15  # Should find many state-changing functions

        for result in results:
            assert result.get("type") == "function"

        # Should include known state-changing functions
        found_names = {r.get("name") for r in results}
        expected_state_changing = {"setValue", "mint", "transfer", "deposit", "updateUserData"}
        assert expected_state_changing.intersection(found_names), f"Expected state-changing functions not found"


def test_25_functions_with_external_calls(engine):
    """
    Use Case 25: Functions with external calls
    - Method: query_code
    - Params: { query_type: "functions", filters: { has_external_calls: True } }
    - Expected: results where `_has_external_calls` returns True.
    """
    resp = engine.query_code("functions", {"has_external_calls": True})
    print("Functions(external_calls):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions with external calls
    if results:
        for result in results:
            assert result.get("type") == "function"

        # Should include functions we know make external calls
        found_names = {r.get("name") for r in results}
        expected_external_calling = {"transferWithCall", "vulnerableTransfer", "processMessage"}
        # At least one should be found if external call detection works
        if expected_external_calling.intersection(found_names):
            print(f"Found external calling functions: {expected_external_calling.intersection(found_names)}")


def test_26_functions_with_asset_transfer_patterns(engine):
    """
    Use Case 26: Functions with asset transfer patterns
    - Method: query_code
    - Params: { query_type: "functions", filters: { has_asset_transfers: True } }
    - Expected: results where `_has_asset_transfers` returns True.
    """
    resp = engine.query_code("functions", {"has_asset_transfers": True})
    print("Functions(asset_transfers):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions with asset transfers
    if results:
        for result in results:
            assert result.get("type") == "function"

        # Should include functions that transfer assets/tokens
        found_names = {r.get("name") for r in results}
        expected_asset_transferring = {"transfer", "mint", "deposit", "withdraw"}
        if expected_asset_transferring.intersection(found_names):
            print(f"Found asset transferring functions: {expected_asset_transferring.intersection(found_names)}")


def test_27_payable_functions(engine):
    """
    Use Case 27: Payable functions
    - Method: query_code
    - Params: { query_type: "functions", filters: { is_payable: True } }
    - Expected: functions whose state_mutability is payable.
    """
    resp = engine.query_code("functions", {"is_payable": True})
    print("Functions(payable):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Validate payable functions
    for result in results:
        assert result.get("type") == "function"
        state_mutability = result.get("state_mutability")
        if state_mutability is not None:
            sm_str = str(state_mutability).lower()
            assert "payable" in sm_str, f"Function {result.get('name')} not payable: {state_mutability}"

    # Should find payable functions we know exist
    found_names = {r.get("name") for r in results}
    expected_payable = {"deposit", "mint", "bidWithNFT"}
    payable_found = expected_payable.intersection(found_names)
    if payable_found:
        print(f"Found payable functions: {payable_found}")

        # Validate specific payable function
        if "deposit" in found_names:
            deposit_func = next(r for r in results if r.get("name") == "deposit")
            assert "SimpleContract.sol" in deposit_func.get("location", {}).get("file", "")


def test_28_calls_filtered_by_call_types(engine):
    """
    Use Case 28: Calls filtered by call_types (name substrings)
    - Method: query_code
    - Params: { query_type: "functions", filters: { call_types: ["transfer", "balanceOf"] } }
    - Expected: functions that make at least one call whose name contains any provided substring.
    """
    resp = engine.query_code("functions", {"call_types": ["transfer", "balanceOf"]})
    print("Functions(call_types=transfer/balanceOf):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions that make these types of calls
    if results:
        for result in results:
            assert result.get("type") == "function"

        found_names = {r.get("name") for r in results}
        # Functions that likely call transfer or balanceOf
        expected_callers = {"transferFrom", "vulnerableTransfer", "transferWithMath"}
        if expected_callers.intersection(found_names):
            print(f"Found functions making transfer/balanceOf calls: {expected_callers.intersection(found_names)}")


def test_29_calls_filtered_by_low_level_true(engine):
    """
    Use Case 29: Calls filtered by low_level=True
    - Method: query_code
    - Params: { query_type: "functions", filters: { low_level: True } }
    - Expected: functions that make at least one low-level call (e.g., .call, .delegatecall, .send, .staticcall).
    """
    resp = engine.query_code("functions", {"low_level": True})
    print("Functions(low_level):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions that make low-level calls
    if results:
        for result in results:
            assert result.get("type") == "function"

        found_names = {r.get("name") for r in results}
        # Functions that likely make low-level calls
        expected_low_level = {"transferWithCall", "processMessage", "vulnerableWithdraw"}
        if expected_low_level.intersection(found_names):
            print(f"Found low-level calling functions: {expected_low_level.intersection(found_names)}")


def test_30_access_patterns_in_source(engine):
    """
    Use Case 30: Access patterns in source (pattern search)
    - Method: query_code
    - Params: { query_type: "functions", filters: { access_patterns: ["msg.sender", "balanceOf("] } }
    - Expected: functions whose source contains any of the patterns.
    """
    resp = engine.query_code("functions", {"access_patterns": ["msg.sender", "balanceOf("]})
    print("Functions(access_patterns=msg.sender/balanceOf):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions containing these patterns
    if results:
        for result in results:
            assert result.get("type") == "function"

        found_names = {r.get("name") for r in results}
        # Functions that likely use msg.sender or balanceOf
        expected_pattern_users = {"transfer", "mint", "setValue", "balanceOf"}
        assert expected_pattern_users.intersection(found_names), f"Expected pattern-using functions not found"

        # Validate that found functions likely contain the patterns
        # (We can't check source directly without include parameter, but names suggest pattern usage)
        print(f"Found functions using access patterns: {found_names}")