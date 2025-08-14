"""Tests for query composition enhancement features."""

import pytest
from pathlib import Path

from sol_query.query.engine import SolidityQueryEngine


class TestQueryComposition:
    """Test query composition operators and enhanced functionality."""

    @pytest.fixture
    def engine(self):
        """Set up engine with test fixtures."""
        engine = SolidityQueryEngine()
        fixtures_path = Path(__file__).parent / "fixtures" / "composition_and_imports"
        engine.load_sources(fixtures_path)
        return engine

    def test_where_predicate_filtering(self, engine):
        """Test where() method with custom predicates."""
        # Find functions with specific names (basic predicate test)
        mint_funcs = engine.functions.where(lambda f: f.name == "mint")

        assert len(mint_funcs) > 0
        for func in mint_funcs.list():
            assert func.name == "mint"

        # Find contracts with more than 5 functions
        large_contracts = engine.contracts.where(lambda c: len(c.functions) > 5)

        assert len(large_contracts) > 0
        for contract in large_contracts.list():
            assert len(contract.functions) > 5

    def test_and_filter_chaining(self, engine):
        """Test and_filter() method for chaining conditions."""
        # Find external functions that are also payable
        risky_funcs = (engine.functions
                      .external()
                      .and_filter(lambda f: f.is_payable()))

        for func in risky_funcs.list():
            assert func.is_external()
            assert func.is_payable()

    def test_and_not_exclusion(self, engine):
        """Test and_not() method for excluding conditions."""
        # Find functions with external calls but not view functions
        stateful_external_calls = (engine.functions
                                 .with_external_calls()
                                 .and_not(lambda f: f.is_view()))

        for func in stateful_external_calls.list():
            assert func.has_external_calls
            assert not func.is_view()

    def test_intersect_operation(self, engine):
        """Test intersect() method for finding common elements."""
        # Find functions that are both external and payable
        external_funcs = engine.functions.external()
        payable_funcs = engine.functions.payable()

        intersection = external_funcs.intersect(payable_funcs)

        for func in intersection.list():
            assert func.is_external()
            assert func.is_payable()
            assert func in external_funcs.list()
            assert func in payable_funcs.list()

    def test_union_operation(self, engine):
        """Test union() method for combining collections."""
        # Combine public and external functions
        public_funcs = engine.functions.public()
        external_funcs = engine.functions.external()

        combined = public_funcs.union(external_funcs)

        # Check that union contains all public and external functions
        public_count = len(public_funcs)
        external_count = len(external_funcs)

        assert len(combined) <= public_count + external_count  # <= because of possible overlaps

        for func in public_funcs.list():
            assert func in combined.list()
        for func in external_funcs.list():
            assert func in combined.list()

    def test_subtract_operation(self, engine):
        """Test subtract() method for removing elements."""
        # Find all functions except constructor functions
        all_funcs = engine.functions
        constructors = engine.functions.constructors()

        non_constructors = all_funcs.subtract(constructors)

        # Verify no constructors in result
        for func in non_constructors.list():
            assert not func.is_constructor

        # Verify constructors are indeed removed
        for constructor in constructors.list():
            assert constructor not in non_constructors.list()

    def test_or_with_alias(self, engine):
        """Test or_with() method as alias for union."""
        # Test that or_with is equivalent to union
        public_funcs = engine.functions.public()
        private_funcs = engine.functions.private()

        union_result = public_funcs.union(private_funcs)
        or_result = public_funcs.or_with(private_funcs)

        # Results should be identical
        assert len(union_result) == len(or_result)
        assert set(id(f) for f in union_result.list()) == set(id(f) for f in or_result.list())

    def test_complex_composition_chain(self, engine):
        """Test complex chaining of multiple composition operators."""
        # Complex query: Find external or public functions that:
        # 1. Have external calls OR asset transfers
        # 2. Are NOT view functions
        # 3. Do NOT have reentrancy guards

        # Step 1: Get base sets
        external_call_funcs = engine.functions.with_external_calls()
        asset_transfer_funcs = engine.functions.with_asset_transfers()
        guarded_funcs = engine.functions.with_modifiers(["nonReentrant"])

        # Step 2: Complex composition
        risky_functions = (engine.functions
                          .public()
                          .or_with(engine.functions.external())
                          .intersect(
                              external_call_funcs.or_with(asset_transfer_funcs)
                          )
                          .and_not(lambda f: f.is_view())
                          .subtract(guarded_funcs))

        # Verify results
        for func in risky_functions.list():
            # Must be public or external
            assert func.is_public() or func.is_external()

            # Must have external calls OR asset transfers
            assert func.has_external_calls or func.has_asset_transfers

            # Must NOT be view
            assert not func.is_view()

            # Must NOT have nonReentrant modifier
            assert "nonReentrant" not in func.modifiers

    def test_composition_with_contracts(self, engine):
        """Test composition operations with contract collections."""
        # Find contracts with inheritance but without specific imports
        inherited_contracts = engine.contracts.where(lambda c: len(c.inheritance) > 0)

        assert len(inherited_contracts) > 0

        for contract in inherited_contracts.list():
            assert len(contract.inheritance) > 0

    def test_composition_with_variables(self, engine):
        """Test composition operations with variable collections."""
        # Find state variables that are NOT constants
        state_vars = engine.variables.state_variables()
        non_constant_state = state_vars.and_not(lambda v: v.is_constant)

        for var in non_constant_state.list():
            assert var.is_state_variable()
            assert not var.is_constant

    def test_empty_collection_operations(self, engine):
        """Test operations on empty collections."""
        # Create an empty collection by filtering for non-existent functions
        empty_funcs = engine.functions.where(lambda f: f.name == "NonExistentFunction")

        assert len(empty_funcs) == 0
        assert empty_funcs.is_empty()

        # Operations on empty collections should work
        still_empty = empty_funcs.and_filter(lambda f: True)
        assert len(still_empty) == 0

        # Union with non-empty should return the non-empty collection
        all_funcs = engine.functions
        union_result = empty_funcs.union(all_funcs)
        assert len(union_result) == len(all_funcs)

    def test_nested_lambda_conditions(self, engine):
        """Test complex nested lambda conditions."""
        # Find functions with complex conditions
        complex_funcs = engine.functions.where(
            lambda f: (
                len(f.parameters) > 2 and
                f.visibility.value in ["public", "external"] and
                not f.is_view() and
                f.parent_contract is not None and
                len(f.parent_contract.inheritance) > 0
            )
        )

        for func in complex_funcs.list():
            assert len(func.parameters) > 2
            assert func.visibility.value in ["public", "external"]
            assert not func.is_view()
            assert func.parent_contract is not None
            assert len(func.parent_contract.inheritance) > 0

    def test_composition_preserves_types(self, engine):
        """Test that composition operations preserve collection types."""
        # Operations on FunctionCollection should return FunctionCollection
        func_result = engine.functions.where(lambda f: True)
        assert type(func_result).__name__ == "FunctionCollection"

        # Operations on ContractCollection should return ContractCollection
        contract_result = engine.contracts.where(lambda c: True)
        assert type(contract_result).__name__ == "ContractCollection"

        # Operations on VariableCollection should return VariableCollection
        var_result = engine.variables.where(lambda v: True)
        assert type(var_result).__name__ == "VariableCollection"

    def test_composition_performance(self, engine):
        """Test that composition operations are reasonably performant."""
        import time

        # Measure time for complex composition
        start_time = time.time()

        result = (engine.functions
                 .where(lambda f: len(f.parameters) >= 0)  # Should include all
                 .intersect(engine.functions.where(lambda f: True))
                 .subtract(engine.functions.where(lambda f: False))
                 .union(engine.functions.where(lambda f: f.is_view())))

        end_time = time.time()

        # Should complete in reasonable time (less than 1 second for small test set)
        assert end_time - start_time < 1.0
        assert len(result) > 0
