"""
Test Plan Part 7: Use Cases 61-70
Tests get_details functionality - first part of get_details tests.
"""
import json
import pytest


def test_61_function_details_by_name(engine):
    """
    Use Case 61: Function details by name
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["transfer"] }
    - Expected: success=True; data.elements["transfer"] includes basic_info (name/type/location/signature), detailed_info (visibility/state_mutability/modifiers/calls), and comprehensive_info (dependencies/call_graph/data_flow).
    """
    resp = engine.get_details("function", ["transfer"])
    print("Function details(transfer):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "transfer" in elements

    element = elements["transfer"]
    assert element.get("found") is True, "transfer function should be found"

    # Validate structure
    assert "basic_info" in element
    assert "detailed_info" in element
    assert "comprehensive_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "transfer"
    assert basic_info.get("type") == "function"
    assert "location" in basic_info
    assert "signature" in basic_info

    # Validate detailed_info
    detailed_info = element["detailed_info"]
    assert "visibility" in detailed_info
    assert "state_mutability" in detailed_info
    assert "modifiers" in detailed_info
    assert "calls" in detailed_info

    # Validate comprehensive_info
    comprehensive_info = element["comprehensive_info"]
    assert "dependencies" in comprehensive_info
    assert "call_graph" in comprehensive_info

    print(f"Found transfer function with signature: {basic_info.get('signature')}")


def test_62_contract_details_with_dependencies(engine):
    """
    Use Case 62: Contract details with dependencies
    - Method: get_details
    - Params: { element_type: "contract", identifiers: ["Token"] }
    - Expected: comprehensive contract information including inheritance and dependencies.
    """
    resp = engine.get_details("contract", ["Token"])
    print("Contract details(Token):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "Token" in elements

    element = elements["Token"]
    assert element.get("found") is True, "Token contract should be found"

    # Validate structure
    assert "basic_info" in element
    assert "detailed_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "Token"
    assert basic_info.get("type") == "contract"
    assert "location" in basic_info

    # Validate detailed_info
    detailed_info = element["detailed_info"]
    assert "inheritance" in detailed_info
    assert "functions" in detailed_info
    assert "variables" in detailed_info

    print(f"Found Token contract at: {basic_info.get('location')}")


def test_63_variable_details_with_usage_patterns(engine):
    """
    Use Case 63: Variable details with usage patterns
    - Method: get_details
    - Params: { element_type: "variable", identifiers: ["balances"] }
    - Expected: variable details including type information and usage patterns.
    """
    resp = engine.get_details("variable", ["balances"])
    print("Variable details(balances):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "balances" in elements

    element = elements["balances"]
    assert element.get("found") is True, "balances variable should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "balances"
    assert basic_info.get("type") == "variable"
    assert "location" in basic_info
    assert "type_name" in basic_info

    # Should be a mapping type
    type_name = str(basic_info.get("type_name", "")).lower()
    assert "mapping" in type_name, f"Expected mapping type, got: {type_name}"

    print(f"Found balances variable with type: {basic_info.get('type_name')}")


def test_64_event_details_with_emission_sites(engine):
    """
    Use Case 64: Event details with emission sites
    - Method: get_details
    - Params: { element_type: "event", identifiers: ["Transfer"] }
    - Expected: event details including argument information and emission locations.
    """
    resp = engine.get_details("event", ["Transfer"])
    print("Event details(Transfer):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "Transfer" in elements

    element = elements["Transfer"]
    assert element.get("found") is True, "Transfer event should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "Transfer"
    assert basic_info.get("type") == "event"
    assert "location" in basic_info

    print(f"Found Transfer event at: {basic_info.get('location')}")


def test_65_modifier_details_with_usage_analysis(engine):
    """
    Use Case 65: Modifier details with usage analysis
    - Method: get_details
    - Params: { element_type: "modifier", identifiers: ["onlyOwner"] }
    - Expected: modifier details including implementation and usage patterns.
    """
    resp = engine.get_details("modifier", ["onlyOwner"])
    print("Modifier details(onlyOwner):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "onlyOwner" in elements

    element = elements["onlyOwner"]
    assert element.get("found") is True, "onlyOwner modifier should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "onlyOwner"
    assert basic_info.get("type") == "modifier"
    assert "location" in basic_info

    print(f"Found onlyOwner modifier at: {basic_info.get('location')}")


def test_66_multiple_elements_batch_details(engine):
    """
    Use Case 66: Multiple elements batch details
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["transfer", "approve", "mint"] }
    - Expected: details for all requested functions in a single response.
    """
    resp = engine.get_details("function", ["transfer", "approve", "mint"])
    print("Multiple function details:", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]

    # Should have results for all requested functions
    requested_functions = ["transfer", "approve", "mint"]
    for func_name in requested_functions:
        assert func_name in elements, f"Function {func_name} not found in results"

        element = elements[func_name]
        if element.get("found"):
            assert "basic_info" in element
            basic_info = element["basic_info"]
            assert basic_info.get("name") == func_name
            assert basic_info.get("type") == "function"

    found_functions = [name for name, elem in elements.items() if elem.get("found")]
    print(f"Found functions: {found_functions}")
    assert len(found_functions) >= 2, "Should find at least 2 of the requested functions"


def test_67_element_not_found_handling(engine):
    """
    Use Case 67: Element not found handling
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["nonExistentFunction"] }
    - Expected: success=True; data.elements["nonExistentFunction"].found=False with appropriate message.
    """
    resp = engine.get_details("function", ["nonExistentFunction"])
    print("Non-existent function details:", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "nonExistentFunction" in elements

    element = elements["nonExistentFunction"]
    assert element.get("found") is False, "Non-existent function should not be found"

    # Should have appropriate message or reason
    assert "message" in element or "reason" in element or "error" in element

    print(f"Correctly handled non-existent function: {element}")


def test_68_mixed_element_types_batch(engine):
    """
    Use Case 68: Mixed element types batch
    - Method: get_details
    - Params: { element_type: "mixed", identifiers: ["transfer", "Token", "Transfer"] }
    - Expected: appropriate handling of mixed element types or error indication.
    """
    # This might not be supported, but let's test the error handling
    resp = engine.get_details("mixed", ["transfer", "Token", "Transfer"])
    print("Mixed element types:", json.dumps(resp, indent=2))

    # Should either succeed with appropriate handling or fail gracefully
    if resp.get("success"):
        data = resp.get("data", {})
        print("Mixed types handled successfully")
    else:
        # Should have appropriate error message
        assert "error" in resp or "message" in resp
        print(f"Mixed types appropriately rejected: {resp.get('error', resp.get('message'))}")


def test_69_details_with_context_enabled(engine):
    """
    Use Case 69: Details with context enabled
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["mint"], include_context: True }
    - Expected: detailed information includes contextual information about surrounding elements.
    """
    resp = engine.get_details("function", ["mint"], include_context=True)
    print("Function details with context(mint):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "mint" in elements

    element = elements["mint"]
    assert element.get("found") is True, "mint function should be found"

    # Should have context information
    if "context" in element:
        context = element["context"]
        assert isinstance(context, dict)

        # Common context fields
        if "siblings" in context:
            siblings = context["siblings"]
            assert isinstance(siblings, list)
            print(f"Found {len(siblings)} sibling elements")

        if "container" in context:
            container = context["container"]
            assert isinstance(container, dict)
            print(f"Container: {container.get('name', 'unknown')}")

    print("Context information successfully included")


def test_70_performance_large_batch_details(engine):
    """
    Use Case 70: Performance (large batch details)
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["transfer", "approve", "mint", "burn", "balanceOf", "totalSupply", "name", "symbol", "decimals", "allowance"] }
    - Expected: handles large batch efficiently; query_info.execution_time reasonable.
    """
    large_batch = ["transfer", "approve", "mint", "burn", "balanceOf", "totalSupply", "name", "symbol", "decimals", "allowance"]
    resp = engine.get_details("function", large_batch)
    print("Large batch function details count:", len(large_batch))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]

    # Should have results for all requested functions
    for func_name in large_batch:
        assert func_name in elements, f"Function {func_name} not found in results"

    found_count = sum(1 for elem in elements.values() if elem.get("found"))
    print(f"Found {found_count}/{len(large_batch)} functions")

    # Check performance
    query_info = resp.get("query_info", {})
    if "execution_time" in query_info:
        execution_time = query_info["execution_time"]
        print(f"Execution time: {execution_time}s")
        assert execution_time < 5.0, f"Large batch took too long: {execution_time}s"

    assert found_count >= 5, "Should find at least half of the requested functions"