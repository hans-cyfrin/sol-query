"""
Test contract-qualified function name support in get_details function.

This test verifies that get_details supports contract-qualified function names
like "ContractName.functionName" format.
"""

import pytest
import os
from sol_query.query.engine_v2 import SolidityQueryEngineV2


@pytest.fixture
def engine():
    """Create engine with test fixture contracts."""
    engine = SolidityQueryEngineV2()

    # Load the test fixtures using the same pattern as other tests
    engine.load_sources([
        "tests/fixtures/composition_and_imports/",
        "tests/fixtures/detailed_scenarios/",
        "tests/fixtures/sample_contract.sol",
    ])

    return engine


def test_contract_qualified_function_names(engine):
    """Test that get_details supports contract-qualified function names."""

    # Test 1: ERC721WithImports.mint - should find the mint function in ERC721WithImports contract
    resp = engine.get_details("function", ["ERC721WithImports.mint"])
    print("get_details(ERC721WithImports.mint):", resp)

    assert resp.get("success") is True
    assert "data" in resp
    assert "elements" in resp["data"]
    assert "ERC721WithImports.mint" in resp["data"]["elements"]

    element = resp["data"]["elements"]["ERC721WithImports.mint"]
    assert element.get("found") is True

    # Verify basic info
    basic_info = element.get("basic_info", {})
    assert basic_info.get("name") == "mint"
    assert basic_info.get("type") == "function"

    # Verify it found the correct contract
    location = basic_info.get("location", {})
    assert str(location.get("file")).endswith("ERC721WithImports.sol")
    assert location.get("contract") == "ERC721WithImports"

    # Verify function signature
    assert basic_info.get("signature") == "mint(address)"

    # Verify detailed info
    detailed_info = element.get("detailed_info", {})
    assert detailed_info.get("visibility") == "external"
    assert detailed_info.get("state_mutability") == "payable"
    assert "nonReentrant" in detailed_info.get("modifiers", [])


def test_multiple_contracts_same_function_name(engine):
    """Test distinguishing between functions with same name in different contracts."""

    # Both BaseToken and MultiInheritanceToken have 'mint' functions
    # Test BaseToken.mint vs MultiInheritanceToken.mint vs Mintable.mint

    # Test MultiInheritanceToken.mint (this should find the override version)
    resp = engine.get_details("function", ["MultiInheritanceToken.mint"])
    print("get_details(MultiInheritanceToken.mint):", resp)

    assert resp.get("success") is True
    element = resp["data"]["elements"]["MultiInheritanceToken.mint"]
    assert element.get("found") is True

    basic_info = element.get("basic_info", {})
    assert basic_info.get("name") == "mint"
    location = basic_info.get("location", {})
    assert str(location.get("file")).endswith("MultipleInheritance.sol")
    assert location.get("contract") == "MultiInheritanceToken"

    # This should be the overridden version with different parameters
    assert basic_info.get("signature") == "mint(address,uint256)"

    # Test Mintable.mint (abstract contract version)
    resp2 = engine.get_details("function", ["Mintable.mint"])
    print("get_details(Mintable.mint):", resp2)

    assert resp2.get("success") is True
    element2 = resp2["data"]["elements"]["Mintable.mint"]
    assert element2.get("found") is True

    basic_info2 = element2.get("basic_info", {})
    assert basic_info2.get("name") == "mint"
    location2 = basic_info2.get("location", {})
    assert str(location2.get("file")).endswith("MultipleInheritance.sol")
    assert location2.get("contract") == "Mintable"

    # Verify they are different functions by comparing line numbers
    assert location.get("line") != location2.get("line")


def test_contract_qualified_vs_unqualified(engine):
    """Test that contract-qualified names are more specific than unqualified names."""

    # First test unqualified 'mint' - should find first match
    resp_unqualified = engine.get_details("function", ["mint"])
    print("get_details(mint):", resp_unqualified)

    assert resp_unqualified.get("success") is True
    unqualified_element = resp_unqualified["data"]["elements"]["mint"]
    assert unqualified_element.get("found") is True

    # Now test qualified 'MultiInheritanceToken.mint' - should find specific one
    resp_qualified = engine.get_details("function", ["MultiInheritanceToken.mint"])
    print("get_details(MultiInheritanceToken.mint):", resp_qualified)

    assert resp_qualified.get("success") is True
    qualified_element = resp_qualified["data"]["elements"]["MultiInheritanceToken.mint"]
    assert qualified_element.get("found") is True

    # Compare the results - they might be different functions
    unqualified_location = unqualified_element["basic_info"]["location"]
    qualified_location = qualified_element["basic_info"]["location"]

    print(f"Unqualified mint contract: {unqualified_location.get('contract')}")
    print(f"Qualified mint contract: {qualified_location.get('contract')}")

    # The qualified version should definitely be from MultiInheritanceToken
    assert qualified_location.get("contract") == "MultiInheritanceToken"


def test_contract_qualified_function_not_found(engine):
    """Test behavior when contract-qualified function doesn't exist."""

    # Test non-existent contract
    resp = engine.get_details("function", ["NonExistentContract.mint"])
    print("get_details(NonExistentContract.mint):", resp)

    assert resp.get("success") is True
    element = resp["data"]["elements"]["NonExistentContract.mint"]
    assert element.get("found") is False
    assert "not found" in element.get("error", "").lower()

    # Test non-existent function in existing contract
    resp2 = engine.get_details("function", ["ERC721WithImports.nonExistentFunction"])
    print("get_details(ERC721WithImports.nonExistentFunction):", resp2)

    assert resp2.get("success") is True
    element2 = resp2["data"]["elements"]["ERC721WithImports.nonExistentFunction"]
    assert element2.get("found") is False
    assert "not found" in element2.get("error", "").lower()


def test_multiple_qualified_functions_in_single_call(engine):
    """Test requesting multiple contract-qualified functions in one call."""

    identifiers = [
        "ERC721WithImports.mint",
        "MultiInheritanceToken.mint",
        "MultiInheritanceToken.transferWithCall",
        "Ownable.transferOwnership"
    ]

    resp = engine.get_details("function", identifiers)
    print("get_details(multiple qualified functions):", resp)

    assert resp.get("success") is True
    elements = resp["data"]["elements"]

    # All should be found
    for identifier in identifiers:
        assert identifier in elements
        element = elements[identifier]
        assert element.get("found") is True

        # Verify the contract matches what we expected
        expected_contract = identifier.split('.')[0]
        actual_contract = element["basic_info"]["location"]["contract"]
        assert actual_contract == expected_contract

        # Verify the function name matches
        expected_function = identifier.split('.')[1]
        actual_function = element["basic_info"]["name"]
        assert actual_function == expected_function


def test_contract_qualified_edge_cases(engine):
    """Test edge cases for contract-qualified function names."""

    # Test with empty string
    resp = engine.get_details("function", [""])
    assert resp.get("success") is True
    element = resp["data"]["elements"][""]
    assert element.get("found") is False

    # Test with malformed qualified name (multiple dots)
    resp2 = engine.get_details("function", ["Contract.Function.Extra"])
    assert resp2.get("success") is True
    element2 = resp2["data"]["elements"]["Contract.Function.Extra"]
    assert element2.get("found") is False

    # Test with just a dot
    resp3 = engine.get_details("function", ["."])
    assert resp3.get("success") is True
    element3 = resp3["data"]["elements"]["."]
    assert element3.get("found") is False


if __name__ == "__main__":
    # Run the tests directly for debugging
    import sys

    engine = None
    try:
        # Setup engine
        engine_instance = SolidityQueryEngineV2()
        engine_instance.load_sources([
            "tests/fixtures/composition_and_imports/",
            "tests/fixtures/detailed_scenarios/",
            "tests/fixtures/sample_contract.sol",
        ])

        engine = engine_instance

        # Run specific test
        print("Running contract-qualified function name tests...")
        test_contract_qualified_function_names(engine)
        print("✓ Basic contract-qualified function test passed")

        test_multiple_contracts_same_function_name(engine)
        print("✓ Multiple contracts same function name test passed")

        test_contract_qualified_vs_unqualified(engine)
        print("✓ Qualified vs unqualified test passed")

        test_contract_qualified_function_not_found(engine)
        print("✓ Not found test passed")

        test_multiple_qualified_functions_in_single_call(engine)
        print("✓ Multiple qualified functions test passed")

        test_contract_qualified_edge_cases(engine)
        print("✓ Edge cases test passed")

        print("\nAll tests passed! ✓")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
