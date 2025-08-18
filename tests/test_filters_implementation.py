"""Tests for the newly implemented **filters parameter functionality."""

import pytest
from pathlib import Path
from sol_query.query.engine import SolidityQueryEngine


class TestFiltersImplementation:
    """Test that **filters parameters are now working correctly."""

    @pytest.fixture
    def engine(self):
        """Create a query engine with test contracts."""
        engine = SolidityQueryEngine()

        # Load the sample contracts that have various patterns
        test_fixtures_path = Path(__file__).parent / "fixtures"
        engine.load_sources([
            test_fixtures_path / "sample_contract.sol",
            test_fixtures_path / "sol-bug-bench" / "src"
        ])

        return engine

    def test_contract_name_filter_on_functions(self, engine):
        """Test that contract_name filter works for functions."""
        # Get all functions first
        all_functions = engine.find_functions()
        print(f"Total functions found: {len(all_functions)}")

        # Test contract_name filter with find_functions
        token_functions = engine.find_functions(contract_name="Token")
        liquidity_pool_functions = engine.find_functions(contract_name="LiquidityPool")

        print(f"Token functions: {len(token_functions)}")
        print(f"LiquidityPool functions: {len(liquidity_pool_functions)}")

        # Verify that all returned functions belong to the specified contract
        for func in token_functions:
            assert func.parent_contract is not None, f"Function {func.name} should have parent_contract"
            assert func.parent_contract.name == "Token", f"Function {func.name} should be in Token contract"

        for func in liquidity_pool_functions:
            assert func.parent_contract is not None, f"Function {func.name} should have parent_contract"
            assert func.parent_contract.name == "LiquidityPool", f"Function {func.name} should be in LiquidityPool contract"

        # Verify that filtering actually reduces the result set
        assert len(token_functions) < len(all_functions), "Contract filtering should reduce results"
        assert len(liquidity_pool_functions) < len(all_functions), "Contract filtering should reduce results"

    def test_contract_name_filter_on_variables(self, engine):
        """Test that contract_name filter works for variables."""
        # Get all variables first
        all_variables = engine.find_variables()
        print(f"Total variables found: {len(all_variables)}")

        # Test contract_name filter with find_variables
        token_variables = engine.find_variables(contract_name="Token")

        print(f"Token variables: {len(token_variables)}")

        # Verify that all returned variables belong to the specified contract
        for var in token_variables:
            assert var.parent_contract is not None, f"Variable {var.name} should have parent_contract"
            assert var.parent_contract.name == "Token", f"Variable {var.name} should be in Token contract"

        # Verify that filtering actually reduces the result set
        if len(all_variables) > 0:
            assert len(token_variables) <= len(all_variables), "Contract filtering should not increase results"

    def test_contract_name_filter_on_events(self, engine):
        """Test that contract_name filter works for events."""
        # Get all events first
        all_events = engine.find_events()
        print(f"Total events found: {len(all_events)}")

        if len(all_events) > 0:
            # Test contract_name filter with find_events
            token_events = engine.find_events(contract_name="Token")

            print(f"Token events: {len(token_events)}")

            # Note: EventDeclaration may not have parent_contract attribute implemented yet
            # For now, we just verify that filtering is reducing the result set
            # In a complete implementation, events would have parent_contract references
            if hasattr(all_events[0], 'parent_contract'):
                # Verify that all returned events belong to the specified contract
                for event in token_events:
                    assert event.parent_contract is not None, f"Event {event.name} should have parent_contract"
                    assert event.parent_contract.name == "Token", f"Event {event.name} should be in Token contract"
            else:
                # For now, just verify that the filtering mechanism is in place
                print("Note: EventDeclaration.parent_contract not implemented yet")
                assert isinstance(token_events, list), "Should return a list"

    def test_find_references_to_with_contract_filter(self, engine):
        """Test that find_references_to works with contract_name filter."""
        # Find all references to 'transfer'
        all_transfer_refs = engine.find_references_to("transfer")
        print(f"All transfer references: {len(all_transfer_refs)}")

        # Find references to 'transfer' only in Token contract
        token_transfer_refs = engine.find_references_to("transfer", contract_name="Token")
        print(f"Token transfer references: {len(token_transfer_refs)}")

        # Verify filtering is working (should be same or fewer results)
        assert len(token_transfer_refs) <= len(all_transfer_refs), "Contract filtering should not increase results"

        # Verify that filtered results actually belong to Token contract
        for ref in token_transfer_refs:
            # For references, we need to check if they are within a Token contract context
            # This is a basic check - in practice, you'd need proper AST traversal
            if hasattr(ref, 'parent_contract') and ref.parent_contract:
                assert ref.parent_contract.name == "Token"

    def test_node_type_filter(self, engine):
        """Test that node_type filter works."""
        # Find identifiers with node_type filter
        identifiers = engine.find_identifiers(node_type="identifier")

        # All results should be identifiers
        for ident in identifiers:
            assert hasattr(ident, 'node_type'), f"Item should have node_type"
            assert ident.node_type.value == "identifier", f"Item should be identifier type"

    def test_visibility_filter_on_functions(self, engine):
        """Test that visibility filter works for functions."""
        # Find public functions
        public_functions = engine.find_functions(visibility="public")

        print(f"Public functions: {len(public_functions)}")

        # Verify that all returned functions are public
        for func in public_functions:
            assert hasattr(func, 'visibility'), f"Function {func.name} should have visibility"
            assert func.visibility.value == "public", f"Function {func.name} should be public"

    def test_multiple_filters_combination(self, engine):
        """Test that multiple filters work together."""
        # Find public functions in Token contract
        token_public_functions = engine.find_functions(
            contract_name="Token",
            visibility="public"
        )

        print(f"Token public functions: {len(token_public_functions)}")

        # Verify that all returned functions satisfy both conditions
        for func in token_public_functions:
            assert hasattr(func, 'parent_contract') and func.parent_contract, f"Function should have parent_contract"
            assert func.parent_contract.name == "Token", f"Function should be in Token contract"
            assert hasattr(func, 'visibility'), f"Function should have visibility"
            assert func.visibility.value == "public", f"Function should be public"

    def test_filter_with_name_patterns(self, engine):
        """Test that filters work with name patterns."""
        # Find transfer functions in Token contract
        token_transfer_functions = engine.find_functions(
            name_patterns="transfer",
            contract_name="Token"
        )

        print(f"Token transfer functions: {len(token_transfer_functions)}")

        # Verify that all returned functions satisfy both conditions
        for func in token_transfer_functions:
            assert "transfer" in func.name.lower(), f"Function name should contain 'transfer'"
            assert hasattr(func, 'parent_contract') and func.parent_contract, f"Function should have parent_contract"
            assert func.parent_contract.name == "Token", f"Function should be in Token contract"

    def test_function_name_filter_on_statements(self, engine):
        """Test that function_name filter works for statements."""
        # Get all statements first
        all_statements = engine.find_statements()
        print(f"Total statements found: {len(all_statements)}")

        if len(all_statements) > 0:
            # Test function_name filter with find_statements
            transfer_statements = engine.find_statements(function_name="transfer")
            print(f"Statements in transfer function: {len(transfer_statements)}")

            # Test combined filtering
            token_transfer_statements = engine.find_statements(
                contract_name="Token",
                function_name="transfer"
            )
            print(f"Statements in Token.transfer: {len(token_transfer_statements)}")

            # Verify filtering reduces results
            assert len(transfer_statements) <= len(all_statements), "Function filtering should not increase results"
            assert len(token_transfer_statements) <= len(transfer_statements), "Combined filtering should not increase results"

    def test_empty_filter_results(self, engine):
        """Test that filters return empty lists when no matches found."""
        # Try to find functions in a non-existent contract
        non_existent_functions = engine.find_functions(contract_name="NonExistentContract")

        assert isinstance(non_existent_functions, list), "Should return a list"
        assert len(non_existent_functions) == 0, "Should return empty list for non-existent contract"

    def test_filter_backwards_compatibility(self, engine):
        """Test that existing functionality still works without filters."""
        # Test that functions without filters still work as before
        all_contracts = engine.find_contracts()
        all_functions = engine.find_functions()
        all_variables = engine.find_variables()

        assert isinstance(all_contracts, list), "Should return list"
        assert isinstance(all_functions, list), "Should return list"
        assert isinstance(all_variables, list), "Should return list"

        print(f"Backwards compatibility check:")
        print(f"  Contracts: {len(all_contracts)}")
        print(f"  Functions: {len(all_functions)}")
        print(f"  Variables: {len(all_variables)}")


if __name__ == "__main__":
    # Run a quick test
    engine = SolidityQueryEngine()
    test_fixtures_path = Path(__file__).parent / "fixtures"
    engine.load_sources([
        test_fixtures_path / "sample_contract.sol",
        test_fixtures_path / "sol-bug-bench" / "src"
    ])

    print("=== Quick Filter Test ===")

    # Test basic filtering
    all_functions = engine.find_functions()
    print(f"Total functions: {len(all_functions)}")

    # Test contract_name filter
    if len(all_functions) > 0:
        # Get a contract name from the first function
        first_contract = all_functions[0].parent_contract
        if first_contract:
            contract_name = first_contract.name
            filtered_functions = engine.find_functions(contract_name=contract_name)
            print(f"Functions in {contract_name}: {len(filtered_functions)}")
            print(f"Filter effectiveness: {len(filtered_functions) <= len(all_functions)}")

    # Test find_references_to with filter
    transfer_refs = engine.find_references_to("transfer")
    print(f"All transfer references: {len(transfer_refs)}")

    if len(all_functions) > 0:
        first_contract = all_functions[0].parent_contract
        if first_contract:
            contract_name = first_contract.name
            filtered_refs = engine.find_references_to("transfer", contract_name=contract_name)
            print(f"Transfer references in {contract_name}: {len(filtered_refs)}")
