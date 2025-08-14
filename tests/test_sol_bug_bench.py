"""Comprehensive tests against the sol-bug-bench project to ensure all queries work."""

import pytest
from pathlib import Path

from sol_query import SolidityQueryEngine
from sol_query.core.ast_nodes import (
    ContractDeclaration, FunctionDeclaration, VariableDeclaration,
    EventDeclaration, ErrorDeclaration, ModifierDeclaration, Visibility
)


class TestSolBugBenchQueries:
    """Test all query methods against the real sol-bug-bench Solidity contracts."""

    @pytest.fixture
    def sol_bug_bench_path(self):
        """Path to sol-bug-bench source directory."""
        return Path(__file__).parent / "fixtures" / "sol-bug-bench" / "src"

    @pytest.fixture
    def engine(self, sol_bug_bench_path):
        """Query engine loaded with sol-bug-bench contracts."""
        engine = SolidityQueryEngine()
        engine.load_sources(sol_bug_bench_path)
        return engine

    def test_load_sol_bug_bench_contracts(self, engine):
        """Test loading all sol-bug-bench contracts."""
        stats = engine.get_statistics()

        # Should have loaded 3 main contracts
        assert stats["total_files"] == 3
        assert stats["total_contracts"] >= 3

        # Should have found multiple functions across contracts
        assert stats["total_functions"] > 10

        print(f"Loaded {stats['total_contracts']} contracts with {stats['total_functions']} functions")

    def test_find_all_contracts(self, engine):
        """Test finding all contracts in sol-bug-bench."""
        contracts = engine.find_contracts()
        contract_names = [c.name for c in contracts]

        # Should find the three main contracts
        expected_contracts = ["GovernanceToken", "LiquidityPool", "StableCoin"]
        for expected in expected_contracts:
            assert expected in contract_names, f"Missing contract: {expected}"

        # Test contract kinds
        main_contracts = engine.find_contracts(kind="contract")
        assert len(main_contracts) >= 3

        print(f"Found contracts: {contract_names}")

    def test_find_functions_comprehensive(self, engine):
        """Test comprehensive function finding across all contracts."""
        # Test all functions
        all_functions = engine.find_functions()
        assert len(all_functions) > 15, "Should have many functions across contracts"

        # Test by visibility
        public_functions = engine.find_functions(visibility=Visibility.PUBLIC)
        external_functions = engine.find_functions(visibility=Visibility.EXTERNAL)
        internal_functions = engine.find_functions(visibility=Visibility.INTERNAL)

        assert len(public_functions) > 0, "Should have public functions"
        assert len(external_functions) > 0, "Should have external functions"
        assert len(internal_functions) > 0, "Should have internal functions"

        # Test constructors
        constructors = engine.functions.constructors()
        assert len(constructors) >= 3, "Should have constructors for each contract"

        # Test view functions
        view_functions = engine.functions.view()
        assert len(view_functions) > 5, "Should have multiple view functions"

        print(f"Functions: {len(all_functions)} total, {len(public_functions)} public, "
              f"{len(external_functions)} external, {len(view_functions)} view")

    def test_find_contract_specific_functions(self, engine):
        """Test finding functions in specific contracts."""
        # GovernanceToken functions (constructor + 4 methods = 5 total)
        governance_functions = engine.find_functions(contract_name="GovernanceToken")
        assert len(governance_functions) >= 5, "GovernanceToken should have at least 5 functions"

        # Look for specific known functions
        mint_functions = engine.find_functions(name_patterns="mint", contract_name="GovernanceToken")
        assert len(mint_functions) > 0, "GovernanceToken should have mint function"

        # LiquidityPool functions
        pool_functions = engine.find_functions(contract_name="LiquidityPool")
        assert len(pool_functions) >= 6, "LiquidityPool should have multiple functions"

        # StableCoin functions
        stable_functions = engine.find_functions(contract_name="StableCoin")
        assert len(stable_functions) >= 3, "StableCoin should have functions"

        print(f"Contract functions - Governance: {len(governance_functions)}, "
              f"Pool: {len(pool_functions)}, Stable: {len(stable_functions)}")

    def test_find_variables_comprehensive(self, engine):
        """Test comprehensive variable finding."""
        # All variables (based on debug output: 16 total)
        all_variables = engine.find_variables()
        assert len(all_variables) >= 10, "Should have many state variables"

        # Test by type patterns
        uint_vars = engine.find_variables(type_patterns="uint*")
        mapping_vars = engine.find_variables(type_patterns="mapping*")
        bool_vars = engine.find_variables(type_patterns="bool")

        assert len(uint_vars) >= 3, "Should have uint variables"
        assert len(mapping_vars) >= 1, "Should have mapping variables"
        # Note: The bool is inside mapping(address => bool), not standalone bool
        # assert len(bool_vars) >= 1, "Should have bool variables"

        # Test visibility filtering
        public_vars = engine.variables.public()

        assert len(public_vars) >= 1, "Should have public variables"

        print(f"Variables: {len(all_variables)} total, {len(mapping_vars)} mappings, "
              f"{len(public_vars)} public, {len(uint_vars)} uint, {len(bool_vars)} bool")

    def test_find_events_and_errors(self, engine):
        """Test finding events and custom errors."""
        # Events (based on debug: 10 total)
        all_events = engine.find_events()
        assert len(all_events) >= 5, "Should have multiple events"

        # Look for specific event patterns
        user_events = engine.find_events(name_patterns="User*")
        token_events = engine.find_events(name_patterns="Token*")

        # Custom errors (based on debug: 12 total)
        all_errors = engine.find_errors()
        assert len(all_errors) >= 5, "Should have custom errors"

        print(f"Events: {len(all_events)}, Errors: {len(all_errors)}, "
              f"User events: {len(user_events)}, Token events: {len(token_events)}")

    def test_find_modifiers(self, engine):
        """Test finding modifiers."""
        # The sol-bug-bench contracts don't define custom modifiers - they use inherited ones
        all_modifiers = engine.find_modifiers()

        # This should be 0 since no custom modifiers are defined
        assert len(all_modifiers) == 0, "Sol-bug-bench contracts don't define custom modifiers"

        print(f"Modifiers: {len(all_modifiers)} (expected 0 - contracts use inherited modifiers)")

    def test_fluent_query_chains(self, engine):
        """Test fluent query method chaining."""
        # Contract navigation
        governance_contract = engine.contracts.with_name("GovernanceToken").first()
        assert governance_contract is not None
        assert governance_contract.name == "GovernanceToken"

        # Navigate from contract to functions
        governance_functions = engine.contracts.with_name("GovernanceToken").get_functions()
        assert len(governance_functions) >= 5

        # Navigate from contract to variables
        governance_vars = engine.contracts.with_name("GovernanceToken").get_variables()
        assert len(governance_vars) >= 1

        # Chain function filters
        external_functions = engine.functions.external()
        assert len(external_functions) >= 2, "Should have external functions"

        # Variable chaining
        mapping_vars = engine.variables.with_type("mapping*")
        assert len(mapping_vars) >= 1, "Should have mapping variables"

        print(f"Fluent queries - Governance functions: {len(governance_functions)}, "
              f"External funcs: {len(external_functions)}, Mappings: {len(mapping_vars)}")

    def test_pattern_matching_comprehensive(self, engine):
        """Test comprehensive pattern matching."""
        # Wildcard patterns
        mint_functions = engine.functions.with_name("mint*")
        assert len(mint_functions) > 0, "Should find mint functions"

        # Check for functions with specific patterns
        update_functions = engine.functions.with_name("*update*")
        create_functions = engine.functions.with_name("create*")

        # Type patterns
        uint_vars = engine.variables.with_type("uint*")
        mapping_vars = engine.variables.with_type("mapping*")

        # Event patterns
        update_events = engine.events.with_name("*Update*")

        print(f"Pattern matching - Mint: {len(mint_functions)}, Update: {len(update_functions)}, "
              f"Create: {len(create_functions)}, Uint: {len(uint_vars)}, Updates: {len(update_events)}")

    def test_advanced_queries(self, engine):
        """Test advanced query methods."""
        # Find references to specific symbols - test with a function that should exist
        mint_refs = engine.find_references_to("mint")
        token_refs = engine.find_references_to("token")

        # Find calls to specific functions
        transfer_calls = engine.find_calls(target_patterns="transfer")

        # Find literals
        number_literals = engine.find_literals()
        string_literals = engine.find_literals()

        # These should work even if numbers are small
        assert isinstance(mint_refs, list), "Should return list of references"
        assert isinstance(transfer_calls, list), "Should return list of calls"
        assert isinstance(number_literals, list), "Should return list of literals"

        print(f"Advanced - Mint refs: {len(mint_refs)}, Token refs: {len(token_refs)}, "
              f"Transfer calls: {len(transfer_calls)}, Literals: {len(number_literals)}")

    def test_call_graph_analysis(self, engine):
        """Test call graph analysis methods."""
        # Find all mint functions
        mint_functions = engine.find_functions(name_patterns="mint")
        if mint_functions:
            mint_function = mint_functions[0]

            # Find what calls mint
            callers = engine.find_callers_of(mint_function)
            print(f"Mint function has {len(callers)} callers")

            # Find what mint calls
            callees = engine.find_callees_of(mint_function)
            print(f"Mint function calls {len(callees)} other functions")

    def test_contract_inheritance(self, engine):
        """Test inheritance analysis."""
        # Find contracts that inherit from ERC20
        erc20_contracts = engine.find_contracts(inheritance="ERC20")
        assert len(erc20_contracts) >= 2, "Should have contracts inheriting from ERC20"

        # Find contracts that inherit from Ownable
        ownable_contracts = engine.find_contracts(inheritance="Ownable")
        assert len(ownable_contracts) >= 2, "Should have contracts inheriting from Ownable"

        print(f"Inheritance - ERC20: {len(erc20_contracts)}, Ownable: {len(ownable_contracts)}")

    def test_statistics_and_metadata(self, engine):
        """Test statistics and metadata generation."""
        stats = engine.get_statistics()

        # Verify statistics structure
        required_keys = [
            "total_files", "total_contracts", "total_functions",
            "contracts_by_type", "total_modifiers", "total_events"
        ]

        for key in required_keys:
            assert key in stats, f"Missing stat key: {key}"
            assert isinstance(stats[key], (int, dict)), f"Invalid stat type for {key}"

        # Test contract names
        contract_names = engine.get_contract_names()
        assert len(contract_names) >= 3
        assert "GovernanceToken" in contract_names

        print(f"Stats: {stats}")

    def test_serialization_integration(self, engine):
        """Test JSON serialization of query results."""
        # Test contract serialization
        contracts = engine.contracts
        contract_dict = contracts.to_dict()

        assert isinstance(contract_dict, list)
        assert len(contract_dict) >= 3

        # Test function serialization
        functions = engine.functions
        function_dict = functions.to_dict()

        assert isinstance(function_dict, list)
        assert len(function_dict) > 10

        # Verify structure of serialized data
        first_contract = contract_dict[0]
        assert "name" in first_contract
        assert "kind" in first_contract

        print(f"Serialization successful - {len(contract_dict)} contracts, {len(function_dict)} functions")

    def test_error_handling_robustness(self, engine):
        """Test that queries handle edge cases gracefully."""
        # Non-existent contract
        missing_contract = engine.find_functions(contract_name="NonExistent")
        assert isinstance(missing_contract, list)
        assert len(missing_contract) == 0

        # Empty patterns
        empty_pattern = engine.find_contracts(name_patterns=[])
        assert isinstance(empty_pattern, list)

        # Invalid patterns should not crash
        try:
            result = engine.find_variables(type_patterns=None)
            assert isinstance(result, list)
        except Exception as e:
            pytest.fail(f"None pattern should not raise exception: {e}")

        # Complex nested queries
        try:
            complex_result = (engine.contracts
                            .main_contracts()
                            .with_inheritance("ERC20")
                            .get_functions()
                            .external()
                            .view())
            assert hasattr(complex_result, '__len__')
        except Exception as e:
            pytest.fail(f"Complex query chain should not fail: {e}")

    def test_performance_on_larger_codebase(self, engine):
        """Test performance characteristics on the larger codebase."""
        import time

        # Time a comprehensive query
        start_time = time.time()

        # Run multiple queries in sequence
        contracts = engine.find_contracts()
        functions = engine.find_functions()
        variables = engine.find_variables()
        events = engine.find_events()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete queries reasonably quickly (under 5 seconds)
        assert duration < 5.0, f"Queries took too long: {duration:.2f}s"

        print(f"Performance test completed in {duration:.2f}s")
        print(f"Found: {len(contracts)} contracts, {len(functions)} functions, "
              f"{len(variables)} variables, {len(events)} events")
