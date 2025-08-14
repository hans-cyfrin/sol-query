#!/usr/bin/env python3
"""
Test negation filters for all collection types.
"""

import pytest
from pathlib import Path
from sol_query import SolidityQueryEngine
from sol_query.core.ast_nodes import Visibility


class TestNegationFilters:
    """Test negation filter functionality across all collection types."""

    @pytest.fixture
    def engine(self):
        """Create query engine with sample contract."""
        engine = SolidityQueryEngine()
        sample_path = Path("tests/fixtures/sample_contract.sol")
        if sample_path.exists():
            engine.load_sources(sample_path)
        return engine

    def test_function_visibility_negation(self, engine):
        """Test function visibility negation filters."""
        all_functions = engine.functions

        # Test not_external
        not_external = engine.functions.not_external()
        external = engine.functions.external()

        # Verify that not_external + external = all functions
        assert len(not_external) + len(external) == len(all_functions)

        # Verify no overlap at function object level (not just names)
        external_ids = {id(f) for f in external._elements}
        not_external_ids = {id(f) for f in not_external._elements}
        assert len(external_ids.intersection(not_external_ids)) == 0

    def test_function_constructor_negation(self, engine):
        """Test constructor negation filters."""
        all_functions = engine.functions

        constructors = engine.functions.constructors()
        not_constructors = engine.functions.not_constructors()

        # Verify that constructors + not_constructors = all functions
        assert len(constructors) + len(not_constructors) == len(all_functions)

        # Verify no overlap
        constructor_names = {f.name for f in constructors}
        not_constructor_names = {f.name for f in not_constructors}
        assert len(constructor_names.intersection(not_constructor_names)) == 0

    def test_function_state_mutability_negation(self, engine):
        """Test state mutability negation filters."""
        all_functions = engine.functions

        view_functions = engine.functions.view()
        not_view_functions = engine.functions.not_view()

        # Verify that view + not_view = all functions
        assert len(view_functions) + len(not_view_functions) == len(all_functions)

        # Test pure functions
        pure_functions = engine.functions.pure()
        not_pure_functions = engine.functions.not_pure()

        assert len(pure_functions) + len(not_pure_functions) == len(all_functions)

    def test_function_modifier_negation(self, engine):
        """Test modifier negation filters."""
        all_functions = engine.functions

        with_modifiers = engine.functions.with_modifiers("onlyOwner")
        without_modifier = engine.functions.without_modifier("onlyOwner")

        # These should be complementary (though some functions might have other modifiers)
        assert len(with_modifiers) + len(without_modifier) == len(all_functions)

    def test_variable_visibility_negation(self, engine):
        """Test variable visibility negation filters."""
        all_variables = engine.variables

        public_vars = engine.variables.public()
        not_public_vars = engine.variables.not_public()

        # Verify complementary sets
        assert len(public_vars) + len(not_public_vars) == len(all_variables)

        # Test private variables
        private_vars = engine.variables.private()
        not_private_vars = engine.variables.not_private()

        assert len(private_vars) + len(not_private_vars) == len(all_variables)

    def test_variable_type_negation(self, engine):
        """Test variable type negation filters."""
        all_variables = engine.variables

        constants = engine.variables.constants()
        not_constants = engine.variables.not_constants()

        # Verify complementary sets
        assert len(constants) + len(not_constants) == len(all_variables)

        # Test immutable variables
        immutable_vars = engine.variables.immutable()
        not_immutable_vars = engine.variables.not_immutable()

        assert len(immutable_vars) + len(not_immutable_vars) == len(all_variables)

    def test_contract_type_negation(self, engine):
        """Test contract type negation filters."""
        all_contracts = engine.contracts

        interfaces = engine.contracts.interfaces()
        not_interfaces = engine.contracts.not_interfaces()

        # Verify complementary sets
        assert len(interfaces) + len(not_interfaces) == len(all_contracts)

        # Test libraries
        libraries = engine.contracts.libraries()
        not_libraries = engine.contracts.not_libraries()

        assert len(libraries) + len(not_libraries) == len(all_contracts)

    def test_contract_inheritance_negation(self, engine):
        """Test contract inheritance negation filters."""
        all_contracts = engine.contracts

        # Test with a common base contract (if any exist)
        with_ownable = engine.contracts.with_inheritance("Ownable")
        without_ownable = engine.contracts.not_with_inheritance("Ownable")

        # These should be complementary
        assert len(with_ownable) + len(without_ownable) == len(all_contracts)

    def test_chained_negation_filters(self, engine):
        """Test chaining negation filters."""
        # Find external functions that are NOT view (external state-changing)
        external_state_changing = engine.functions.external().not_view()

        # Verify all results are external
        for func in external_state_changing:
            assert func.visibility == Visibility.EXTERNAL
            assert not func.is_view()

        # Find contracts that are NOT interfaces and do NOT inherit from anything
        standalone_contracts = engine.contracts.not_interfaces().not_with_inheritance("*")

        # Verify all results are not interfaces
        for contract in standalone_contracts:
            assert not contract.is_interface()

    def test_generic_negation_filters(self, engine):
        """Test generic negation filter methods."""
        # Test generic visibility negation
        not_external_generic = engine.functions.not_with_visibility(Visibility.EXTERNAL)
        not_external_specific = engine.functions.not_external()

        # Should be equivalent
        assert len(not_external_generic) == len(not_external_specific)

        # Test variable visibility negation
        not_public_vars_generic = engine.variables.not_with_visibility(Visibility.PUBLIC)
        not_public_vars_specific = engine.variables.not_public()

        assert len(not_public_vars_generic) == len(not_public_vars_specific)

    def test_complex_negation_scenarios(self, engine):
        """Test complex negation scenarios for security analysis."""
        # Find functions that are external but NOT protected by modifiers
        unprotected_external = (engine.functions
                               .external()
                               .without_any_modifiers_matching(["onlyOwner", "onlyAdmin"]))

        # All results should be external
        for func in unprotected_external:
            assert func.visibility == Visibility.EXTERNAL
            assert "onlyOwner" not in func.modifiers
            assert "onlyAdmin" not in func.modifiers

        # Find state variables that are NOT constants and NOT immutable (mutable state)
        mutable_state = engine.variables.not_constants().not_immutable()

        # All results should be mutable
        for var in mutable_state:
            assert not var.is_constant
            assert not var.is_immutable

    def test_negation_filter_edge_cases(self, engine):
        """Test edge cases for negation filters."""
        # Test with empty results
        non_existent_modifier = engine.functions.without_modifier("nonExistentModifier")
        all_functions = engine.functions

        # Should return all functions since none have the non-existent modifier
        assert len(non_existent_modifier) == len(all_functions)

        # Test double negation (should be equivalent to original positive filter)
        external_functions = engine.functions.external()
        not_not_external = engine.functions.not_external().not_external()

        # Note: This is a conceptual test - double negation isn't directly implemented
        # but we can verify the logic by checking that not_external excludes external functions
        not_external = engine.functions.not_external()
        external_ids = {id(f) for f in external_functions._elements}
        not_external_ids = {id(f) for f in not_external._elements}

        # Verify no overlap between external and not_external at function object level
        assert len(external_ids.intersection(not_external_ids)) == 0
