"""Tests for external call and asset transfer filters."""

import pytest
from pathlib import Path
from sol_query.query.engine import SolidityQueryEngine


class TestExternalCallFilters:
    """Test external call and asset transfer filtering functionality."""

    @pytest.fixture
    def engine(self):
        """Create a query engine with test contracts."""
        engine = SolidityQueryEngine()

        # Load the sample contracts that have various call patterns
        test_fixtures_path = Path(__file__).parent / "fixtures"
        engine.load_sources([
            test_fixtures_path / "sample_contract.sol",
            test_fixtures_path / "sol-bug-bench" / "src"
        ])

        return engine

    def test_with_external_calls_shallow(self, engine):
        """Test filtering functions with direct external calls."""
        # Get all functions
        all_functions = engine.functions.list()
        print(f"Total functions found: {len(all_functions)}")

        # Filter functions with external calls
        functions_with_external_calls = engine.functions.with_external_calls().list()
        print(f"Functions with external calls: {len(functions_with_external_calls)}")

        # Verify that filtered functions have the external call flag set
        for func in functions_with_external_calls:
            assert func.has_external_calls, f"Function {func.name} should have external calls"
            print(f"  - {func.name}: {func.external_call_targets}")

    def test_without_external_calls_shallow(self, engine):
        """Test filtering functions without direct external calls."""
        functions_without_external_calls = engine.functions.without_external_calls().list()
        print(f"Functions without external calls: {len(functions_without_external_calls)}")

        # Verify that filtered functions don't have the external call flag set
        for func in functions_without_external_calls:
            assert not func.has_external_calls, f"Function {func.name} should not have external calls"

    def test_with_asset_transfers_shallow(self, engine):
        """Test filtering functions with direct asset transfers."""
        functions_with_asset_transfers = engine.functions.with_asset_transfers().list()
        print(f"Functions with asset transfers: {len(functions_with_asset_transfers)}")

        # Verify that filtered functions have the asset transfer flag set
        for func in functions_with_asset_transfers:
            assert func.has_asset_transfers, f"Function {func.name} should have asset transfers"
            print(f"  - {func.name}: {func.asset_transfer_types}")

    def test_without_asset_transfers_shallow(self, engine):
        """Test filtering functions without direct asset transfers."""
        functions_without_asset_transfers = engine.functions.without_asset_transfers().list()
        print(f"Functions without asset transfers: {len(functions_without_asset_transfers)}")

        # Verify that filtered functions don't have the asset transfer flag set
        for func in functions_without_asset_transfers:
            assert not func.has_asset_transfers, f"Function {func.name} should not have asset transfers"

    def test_with_external_calls_deep(self, engine):
        """Test filtering functions with external calls in their call tree."""
        functions_with_external_calls_deep = engine.functions.with_external_calls_deep().list()
        print(f"Functions with external calls (deep): {len(functions_with_external_calls_deep)}")

        # This should include functions that call other functions that make external calls
        for func in functions_with_external_calls_deep:
            print(f"  - {func.name} (deep external calls)")

    def test_with_asset_transfers_deep(self, engine):
        """Test filtering functions with asset transfers in their call tree."""
        functions_with_asset_transfers_deep = engine.functions.with_asset_transfers_deep().list()
        print(f"Functions with asset transfers (deep): {len(functions_with_asset_transfers_deep)}")

        # This should include functions that call other functions that transfer assets
        for func in functions_with_asset_transfers_deep:
            print(f"  - {func.name} (deep asset transfers)")

    def test_traditional_finder_methods(self, engine):
        """Test the traditional finder methods with new parameters."""
        # Test with_external_calls parameter
        external_call_functions = engine.find_functions(with_external_calls=True)
        print(f"Functions with external calls (traditional): {len(external_call_functions)}")

        # Test with_asset_transfers parameter
        asset_transfer_functions = engine.find_functions(with_asset_transfers=True)
        print(f"Functions with asset transfers (traditional): {len(asset_transfer_functions)}")

        # Test deep analysis parameters
        deep_external_functions = engine.find_functions(with_external_calls_deep=True)
        print(f"Functions with external calls deep (traditional): {len(deep_external_functions)}")

        deep_asset_functions = engine.find_functions(with_asset_transfers_deep=True)
        print(f"Functions with asset transfers deep (traditional): {len(deep_asset_functions)}")

    def test_combined_filters(self, engine):
        """Test combining the new filters with existing ones."""
        # Find external functions that make external calls
        external_functions_with_calls = (engine.functions
                                       .external()
                                       .with_external_calls()
                                       .list())
        print(f"External functions with external calls: {len(external_functions_with_calls)}")

        # Find payable functions with asset transfers
        payable_functions_with_transfers = (engine.functions
                                          .payable()
                                          .with_asset_transfers()
                                          .list())
        print(f"Payable functions with asset transfers: {len(payable_functions_with_transfers)}")

    def test_specific_call_targets(self, engine):
        """Test filtering by specific external call targets."""
        # Test filtering by specific call targets
        functions_with_call_targets = engine.functions.with_external_call_targets(['call', 'transfer']).list()
        print(f"Functions with specific call targets: {len(functions_with_call_targets)}")

        for func in functions_with_call_targets:
            print(f"  - {func.name}: targets {func.external_call_targets}")

    def test_specific_transfer_types(self, engine):
        """Test filtering by specific asset transfer types."""
        # Test filtering by specific transfer types
        functions_with_transfer_types = engine.functions.with_asset_transfer_types(['eth_transfer', 'token_transfer']).list()
        print(f"Functions with specific transfer types: {len(functions_with_transfer_types)}")

        for func in functions_with_transfer_types:
            print(f"  - {func.name}: types {func.asset_transfer_types}")

    def test_liquidity_pool_analysis(self, engine):
        """Test analysis of the LiquidityPool contract specifically."""
        # Focus on LiquidityPool contract functions
        liquidity_pool_functions = engine.functions.from_contract("LiquidityPool").list()
        print(f"LiquidityPool functions: {len(liquidity_pool_functions)}")

        # Check which functions have external calls
        lp_external_calls = engine.functions.from_contract("LiquidityPool").with_external_calls().list()
        print(f"LiquidityPool functions with external calls: {len(lp_external_calls)}")

        # Check which functions have asset transfers
        lp_asset_transfers = engine.functions.from_contract("LiquidityPool").with_asset_transfers().list()
        print(f"LiquidityPool functions with asset transfers: {len(lp_asset_transfers)}")

        # Analyze specific functions
        for func in liquidity_pool_functions:
            print(f"  - {func.name}:")
            print(f"    External calls: {func.has_external_calls} {func.external_call_targets}")
            print(f"    Asset transfers: {func.has_asset_transfers} {func.asset_transfer_types}")

    def test_token_contract_analysis(self, engine):
        """Test analysis of the Token contract specifically."""
        # Focus on Token contract functions
        token_functions = engine.functions.from_contract("Token").list()
        print(f"Token functions: {len(token_functions)}")

        # Check transfer-related functions
        transfer_functions = engine.functions.from_contract("Token").with_name("*transfer*").list()
        print(f"Token transfer functions: {len(transfer_functions)}")

        for func in transfer_functions:
            print(f"  - {func.name}:")
            print(f"    External calls: {func.has_external_calls} {func.external_call_targets}")
            print(f"    Asset transfers: {func.has_asset_transfers} {func.asset_transfer_types}")

    def test_deep_vs_shallow_comparison(self, engine):
        """Compare shallow vs deep analysis results."""
        shallow_external = engine.functions.with_external_calls().list()
        deep_external = engine.functions.with_external_calls_deep().list()

        shallow_transfers = engine.functions.with_asset_transfers().list()
        deep_transfers = engine.functions.with_asset_transfers_deep().list()

        print(f"External calls - Shallow: {len(shallow_external)}, Deep: {len(deep_external)}")
        print(f"Asset transfers - Shallow: {len(shallow_transfers)}, Deep: {len(deep_transfers)}")

        # Deep analysis should find at least as many as shallow
        assert len(deep_external) >= len(shallow_external), "Deep analysis should find at least as many external calls"
        assert len(deep_transfers) >= len(shallow_transfers), "Deep analysis should find at least as many asset transfers"

    def test_negation_filters(self, engine):
        """Test the negation filters."""
        all_functions = engine.functions.list()

        with_external = engine.functions.with_external_calls().list()
        without_external = engine.functions.without_external_calls().list()

        with_transfers = engine.functions.with_asset_transfers().list()
        without_transfers = engine.functions.without_asset_transfers().list()

        # Verify that with + without = all functions
        assert len(with_external) + len(without_external) == len(all_functions)
        assert len(with_transfers) + len(without_transfers) == len(all_functions)

        print(f"Total functions: {len(all_functions)}")
        print(f"With external calls: {len(with_external)}, Without: {len(without_external)}")
        print(f"With asset transfers: {len(with_transfers)}, Without: {len(without_transfers)}")


if __name__ == "__main__":
    # Run a quick test
    engine = SolidityQueryEngine()
    test_fixtures_path = Path(__file__).parent / "fixtures"
    engine.load_sources([
        test_fixtures_path / "sample_contract.sol",
        test_fixtures_path / "sol-bug-bench" / "src"
    ])

    print("=== Quick Test Results ===")

    # Test basic functionality
    all_functions = engine.functions.list()
    print(f"Total functions: {len(all_functions)}")

    external_call_functions = engine.functions.with_external_calls().list()
    print(f"Functions with external calls: {len(external_call_functions)}")

    asset_transfer_functions = engine.functions.with_asset_transfers().list()
    print(f"Functions with asset transfers: {len(asset_transfer_functions)}")

    # Show some examples
    print("\nFunctions with external calls:")
    for func in external_call_functions[:5]:  # Show first 5
        print(f"  - {func.name}: {func.external_call_targets}")

    print("\nFunctions with asset transfers:")
    for func in asset_transfer_functions[:5]:  # Show first 5
        print(f"  - {func.name}: {func.asset_transfer_types}")
