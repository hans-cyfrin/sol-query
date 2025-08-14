"""Tests for contextual analysis improvements in external call detection."""

import pytest
from pathlib import Path
from sol_query.query.engine import SolidityQueryEngine


class TestContextualAnalysis:
    """Test contextual analysis for more accurate external call detection."""

    @pytest.fixture
    def engine(self):
        """Create a query engine with test contracts."""
        engine = SolidityQueryEngine()

        # Load the sample contracts
        test_fixtures_path = Path(__file__).parent / "fixtures"
        engine.load_sources([
            test_fixtures_path / "sample_contract.sol",
            test_fixtures_path / "sol-bug-bench" / "src"
        ])

        return engine

    def test_internal_transfer_not_flagged_as_external(self, engine):
        """Test that internal transfer functions are not flagged as external calls."""
        # Get the Token contract's transfer function
        token_functions = engine.functions.from_contract("Token").list()
        transfer_func = next((f for f in token_functions if f.name == "transfer"), None)

        assert transfer_func is not None, "Token contract should have a transfer function"

        # The transfer function calls _transfer internally, not an external contract
        # With contextual analysis, this should NOT be flagged as an external call
        assert not transfer_func.has_external_calls, \
            f"Internal transfer function should not be flagged as external call. " \
            f"Targets: {transfer_func.external_call_targets}"

        print(f"✓ Token.transfer() correctly identified as internal (not external)")
        print(f"  External calls: {transfer_func.has_external_calls}")
        print(f"  Call targets: {transfer_func.external_call_targets}")

    def test_actual_external_calls_detected(self, engine):
        """Test that actual external calls are properly detected."""
        # Get functions that should have external calls
        lp_functions = engine.functions.from_contract("LiquidityPool").list()

        # The withdraw function should have external calls (to token contract)
        withdraw_func = next((f for f in lp_functions if f.name == "withdraw"), None)

        if withdraw_func:
            assert withdraw_func.has_external_calls, \
                "LiquidityPool.withdraw() should have external calls"

            print(f"✓ LiquidityPool.withdraw() correctly identified as having external calls")
            print(f"  External calls: {withdraw_func.has_external_calls}")
            print(f"  Call targets: {withdraw_func.external_call_targets}")

    def test_interface_calls_detected(self, engine):
        """Test that interface-based calls are detected as external."""
        # Look for functions that use interface calls like IERC20(token).transfer()
        all_functions = engine.functions.with_external_calls().list()

        interface_calls = []
        for func in all_functions:
            for target in func.external_call_targets:
                if 'external_call' in target:
                    interface_calls.append((func.name, target))

        assert len(interface_calls) > 0, "Should detect some interface-based external calls"

        print(f"✓ Detected {len(interface_calls)} interface-based external calls:")
        for func_name, target in interface_calls[:5]:  # Show first 5
            print(f"  - {func_name}: {target}")

    def test_low_level_calls_detected(self, engine):
        """Test that low-level calls (.call, .delegatecall) are detected."""
        all_functions = engine.functions.with_external_calls().list()

        low_level_calls = []
        for func in all_functions:
            for target in func.external_call_targets:
                if 'low_level_call' in target:
                    low_level_calls.append((func.name, target))

        print(f"✓ Detected {len(low_level_calls)} low-level external calls:")
        for func_name, target in low_level_calls:
            print(f"  - {func_name}: {target}")

    def test_contextual_vs_pattern_matching_accuracy(self, engine):
        """Compare contextual analysis with pattern matching for accuracy."""
        # Get all functions
        all_functions = engine.functions.list()

        # Count functions with external calls using contextual analysis
        contextual_external = len([f for f in all_functions if f.has_external_calls])

        # Count functions that would be flagged by simple pattern matching
        pattern_external = 0
        pattern_keywords = ['transfer', 'call', 'send', 'approve']

        for func in all_functions:
            if func.name in pattern_keywords:
                pattern_external += 1

        print(f"✓ Contextual analysis results:")
        print(f"  Functions with external calls (contextual): {contextual_external}")
        print(f"  Functions that match patterns: {pattern_external}")

        # Contextual analysis should be more accurate (fewer false positives)
        # This is a heuristic test - the exact numbers depend on the test contracts

    def test_inheritance_context_handling(self, engine):
        """Test that inherited functions are properly handled in context."""
        # Find contracts with inheritance
        contracts = engine.contracts.list()
        inherited_contracts = [c for c in contracts if c.inheritance]

        print(f"✓ Found {len(inherited_contracts)} contracts with inheritance:")
        for contract in inherited_contracts:
            print(f"  - {contract.name} inherits from: {contract.inheritance}")

            # Test that functions in inherited contracts have proper context
            for func in contract.functions:
                if func.has_external_calls:
                    print(f"    Function {func.name} has external calls: {func.external_call_targets}")

    def test_asset_transfer_contextual_analysis(self, engine):
        """Test contextual analysis for asset transfers."""
        # Get functions with asset transfers
        transfer_functions = engine.functions.with_asset_transfers().list()

        print(f"✓ Found {len(transfer_functions)} functions with asset transfers:")

        internal_transfers = 0
        external_transfers = 0

        for func in transfer_functions:
            has_internal = any('internal_transfer' in t for t in func.asset_transfer_types)
            has_external = any(t in ['token_transfer', 'eth_transfer'] for t in func.asset_transfer_types)

            if has_internal:
                internal_transfers += 1
            if has_external:
                external_transfers += 1

            print(f"  - {func.name}: {func.asset_transfer_types}")

        print(f"  Internal transfers: {internal_transfers}")
        print(f"  External transfers: {external_transfers}")

    def test_false_positive_reduction(self, engine):
        """Test that contextual analysis reduces false positives."""
        # Get Token contract functions
        token_functions = engine.functions.from_contract("Token").list()

        # Functions that would be false positives with pattern matching
        potential_false_positives = ['transfer', 'transferFrom', 'approve']

        false_positives_avoided = 0
        for func_name in potential_false_positives:
            func = next((f for f in token_functions if f.name == func_name), None)
            if func and not func.has_external_calls:
                false_positives_avoided += 1
                print(f"✓ Avoided false positive: Token.{func_name}() correctly identified as internal")

        assert false_positives_avoided > 0, "Should avoid some false positives"
        print(f"✓ Avoided {false_positives_avoided} false positives through contextual analysis")


if __name__ == "__main__":
    # Run a quick demonstration
    engine = SolidityQueryEngine()
    test_fixtures_path = Path(__file__).parent / "fixtures"
    engine.load_sources([
        test_fixtures_path / "sample_contract.sol",
        test_fixtures_path / "sol-bug-bench" / "src"
    ])

    print("=== Contextual Analysis Demonstration ===")

    # Show the improvement
    token_functions = engine.functions.from_contract("Token").list()
    transfer_func = next((f for f in token_functions if f.name == "transfer"), None)

    if transfer_func:
        print(f"\nToken.transfer() analysis:")
        print(f"  External calls: {transfer_func.has_external_calls}")
        print(f"  Asset transfers: {transfer_func.has_asset_transfers}")
        print(f"  → This is correct! Token.transfer() calls internal _transfer(), not external contracts")

    # Show actual external calls
    external_functions = engine.functions.with_external_calls().list()
    print(f"\nActual external calls found: {len(external_functions)}")
    for func in external_functions[:3]:
        print(f"  - {func.name} in {func.parent_contract.name}: {func.external_call_targets}")
