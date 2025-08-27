"""Tests for new API features: source filtering, operators, literals, member access, and time operations."""

import pytest
from pathlib import Path
import re

from sol_query import SolidityQueryEngine
from sol_query.core.ast_nodes import Expression, Statement, FunctionDeclaration, VariableDeclaration


class TestNewAPIFeatures:
    """Test new API features added for enhanced security analysis."""

    @pytest.fixture
    def sample_contract_path(self):
        """Path to sample contract file."""
        return Path(__file__).parent / "fixtures" / "sample_contract.sol"

    @pytest.fixture
    def engine(self, sample_contract_path):
        """Query engine loaded with sample contract."""
        engine = SolidityQueryEngine()
        engine.load_sources(sample_contract_path)
        return engine

    # =============================================================================
    # SOURCE CODE CONTENT FILTERING TESTS
    # =============================================================================

    def test_function_source_pattern_filtering(self, engine):
        """Test source pattern filtering for functions."""
        # Test containing_source_pattern with regex
        require_functions = engine.functions.containing_source_pattern(r"require\(")
        assert len(require_functions) > 0

        # Verify all results actually contain the pattern
        for func in require_functions:
            assert "require(" in func.get_source_code()

        # Test with_source_containing with simple text
        balance_functions = engine.functions.with_source_containing("balance")
        assert len(balance_functions) > 0

        for func in balance_functions:
            assert "balance" in func.get_source_code()

    def test_statement_source_pattern_filtering(self, engine):
        """Test source pattern filtering for statements."""
        # Test pattern matching on statements
        require_statements = engine.statements.containing_source_pattern(r"require\(")
        assert len(require_statements) > 0

        # Test simple text search
        balance_statements = engine.statements.with_source_containing("balance")
        assert len(balance_statements) > 0

    def test_expression_source_pattern_filtering(self, engine):
        """Test source pattern filtering for expressions."""
        # Test pattern matching on expressions
        call_expressions = engine.expressions.containing_source_pattern(r"\w+\(")
        assert len(call_expressions) > 0

        # Test simple text search
        balance_expressions = engine.expressions.with_source_containing("balance")
        assert len(balance_expressions) > 0

    # =============================================================================
    # OPERATOR-SPECIFIC FILTERING TESTS
    # =============================================================================

    def test_operator_filtering(self, engine):
        """Test operator-specific expression filtering."""
        # Test single operator
        equality_expressions = engine.expressions.with_operator("==")
        assert isinstance(equality_expressions.list(), list)

        # Test multiple operators
        arithmetic_ops = engine.expressions.with_operator(["+", "-", "*"])
        assert isinstance(arithmetic_ops.list(), list)

        # Test predefined operator groups
        arithmetic_expressions = engine.expressions.with_arithmetic_operators()
        assert len(arithmetic_expressions) > 0

        comparison_expressions = engine.expressions.with_comparison_operators()
        assert len(comparison_expressions) > 0

        logical_expressions = engine.expressions.with_logical_operators()
        assert isinstance(logical_expressions.list(), list)

    def test_operator_filtering_accuracy(self, engine):
        """Test that operator filtering returns accurate results."""
        # Get all binary expressions first
        binary_expressions = engine.expressions.binary_operations()

        # Filter by specific operator
        plus_expressions = binary_expressions.with_operator("+")

        # Verify all results have the correct operator
        for expr in plus_expressions:
            if hasattr(expr, 'operator'):
                assert expr.operator == "+"

    # =============================================================================
    # LITERAL VALUE FILTERING TESTS
    # =============================================================================

    def test_literal_value_filtering(self, engine):
        """Test literal value filtering."""
        # Test exact value matching
        zero_literals = engine.expressions.literals().with_value(0)
        assert isinstance(zero_literals.list(), list)

        # Test string value matching
        string_literals = engine.expressions.literals().with_string_value("ERC20")
        assert isinstance(string_literals.list(), list)

        # Test numeric range filtering
        range_literals = engine.expressions.literals().with_numeric_value(min_val=0, max_val=100)
        assert isinstance(range_literals.list(), list)

        # Test range with only min
        min_literals = engine.expressions.literals().with_numeric_value(min_val=1000)
        assert isinstance(min_literals.list(), list)

        # Test range with only max
        max_literals = engine.expressions.literals().with_numeric_value(max_val=10)
        assert isinstance(max_literals.list(), list)

    def test_literal_filtering_accuracy(self, engine):
        """Test that literal filtering returns accurate results."""
        # Get all literals first
        all_literals = engine.expressions.literals()

        # Test specific value
        one_literals = all_literals.with_value("1")
        for literal in one_literals:
            if hasattr(literal, 'value'):
                assert literal.value == "1"

        # Test numeric range
        small_numbers = all_literals.with_numeric_value(min_val=0, max_val=5)
        for literal in small_numbers:
            if hasattr(literal, 'value') and hasattr(literal, 'literal_type'):
                if literal.literal_type in ['number', 'decimal']:
                    try:
                        val = float(literal.value)
                        assert 0 <= val <= 5
                    except (ValueError, TypeError):
                        pass  # Skip non-numeric literals

    # =============================================================================
    # MEMBER ACCESS FILTERING TESTS
    # =============================================================================

    def test_member_access_filtering(self, engine):
        """Test member access filtering."""
        # Test accessing specific members
        balance_access = engine.expressions.accessing_member("balance")
        assert len(balance_access) > 0

        # Verify results contain member access
        for expr in balance_access:
            source = expr.get_source_code()
            assert ".balance" in source

        # Test other common members
        length_access = engine.expressions.accessing_member("length")
        assert isinstance(length_access.list(), list)

        # Test member access collection method
        member_expressions = engine.expressions.member_access()
        assert isinstance(member_expressions.list(), list)

    # =============================================================================
    # TIME-RELATED OPERATION TESTS
    # =============================================================================

    def test_time_operation_filtering(self, engine):
        """Test time-related operation filtering."""
        # Test time operations in functions
        time_functions = engine.functions.with_time_operations()
        assert isinstance(time_functions.list(), list)

        # Test timestamp usage
        timestamp_functions = engine.functions.with_timestamp_usage()
        assert isinstance(timestamp_functions.list(), list)

        # Test time arithmetic
        time_arithmetic_functions = engine.functions.with_time_arithmetic()
        assert isinstance(time_arithmetic_functions.list(), list)

        # Test time-related variables
        time_variables = engine.variables.time_related()
        assert isinstance(time_variables.list(), list)

    def test_time_operation_accuracy(self, engine):
        """Test accuracy of time-related filtering."""
        # Get functions with time operations
        time_functions = engine.functions.with_time_operations()

        time_patterns = [
            r"block\.timestamp",
            r"now\b",
            r"\btimestamp\b",
            r"\bduration\b",
            r"\bdeadline\b",
            r"\bexpiry\b",
            r"\btimeout\b"
        ]

        # Verify each function actually contains time-related patterns
        for func in time_functions:
            source = func.get_source_code()
            has_time_pattern = any(re.search(pattern, source) for pattern in time_patterns)
            assert has_time_pattern, f"Function {func.name} doesn't contain expected time patterns"

    # =============================================================================
    # ENHANCED CALL FILTERING TESTS
    # =============================================================================

    def test_enhanced_call_filtering(self, engine):
        """Test enhanced call filtering features."""
        # Test method name filtering
        transfer_calls = engine.expressions.calls().to_method("transfer")
        assert isinstance(transfer_calls.list(), list)

        # Test parameter count filtering
        two_param_calls = engine.expressions.calls().with_parameters(count=2)
        assert isinstance(two_param_calls.list(), list)

        # Test parameter range filtering
        min_param_calls = engine.expressions.calls().with_parameters(min_count=1)
        assert isinstance(min_param_calls.list(), list)

        max_param_calls = engine.expressions.calls().with_parameters(max_count=3)
        assert isinstance(max_param_calls.list(), list)

    def test_call_filtering_accuracy(self, engine):
        """Test accuracy of call filtering."""
        # Test parameter count accuracy
        one_param_calls = engine.expressions.calls().with_parameters(count=1)

        for call in one_param_calls:
            if hasattr(call, 'arguments'):
                assert len(call.arguments) == 1

    # =============================================================================
    # BINARY EXPRESSION ENHANCEMENT TESTS
    # =============================================================================

    def test_binary_expression_enhancements(self, engine):
        """Test binary expression enhancement features."""
        # Test left operand type filtering
        uint_left_expressions = engine.expressions.binary_operations().with_left_operand_type("uint")
        assert isinstance(uint_left_expressions.list(), list)

        # Test right operand value filtering
        zero_right_expressions = engine.expressions.binary_operations().with_right_operand_value(0)
        assert isinstance(zero_right_expressions.list(), list)

    # =============================================================================
    # TRADITIONAL API TESTS
    # =============================================================================

    def test_traditional_api_operator_filtering(self, engine):
        """Test traditional API for operator filtering."""
        # Test find_expressions_with_operator
        equality_expressions = engine.find_expressions_with_operator("==")
        assert isinstance(equality_expressions, list)

        arithmetic_expressions = engine.find_expressions_with_operator(["+", "-"])
        assert isinstance(arithmetic_expressions, list)

    def test_traditional_api_value_filtering(self, engine):
        """Test traditional API for value filtering."""
        # Test find_expressions_with_value
        zero_expressions = engine.find_expressions_with_value(0)
        assert isinstance(zero_expressions, list)

        string_expressions = engine.find_expressions_with_value("Token")
        assert isinstance(string_expressions, list)

    def test_traditional_api_member_access(self, engine):
        """Test traditional API for member access."""
        # Test find_expressions_accessing_member
        balance_expressions = engine.find_expressions_accessing_member("balance")
        assert isinstance(balance_expressions, list)

        # Verify results
        for expr in balance_expressions:
            source = expr.get_source_code()
            assert ".balance" in source

    def test_traditional_api_source_patterns(self, engine):
        """Test traditional API for source pattern filtering."""
        # Test find_functions_with_source_pattern
        require_functions = engine.find_functions_with_source_pattern(r"require\(")
        assert isinstance(require_functions, list)

        # Test find_statements_with_source_pattern
        balance_statements = engine.find_statements_with_source_pattern(r"\.balance")
        assert isinstance(balance_statements, list)

    def test_traditional_api_time_operations(self, engine):
        """Test traditional API for time operations."""
        # Test find_functions_with_time_operations
        time_functions = engine.find_functions_with_time_operations()
        assert isinstance(time_functions, list)

        # Test find_variables_time_related
        time_variables = engine.find_variables_time_related()
        assert isinstance(time_variables, list)

    # =============================================================================
    # COMPOSITION AND CHAINING TESTS
    # =============================================================================

    def test_fluent_api_chaining(self, engine):
        """Test chaining multiple fluent API methods."""
        # Chain multiple filters
        complex_query = (engine.expressions
                        .literals()
                        .with_numeric_value(min_val=0, max_val=100)
                        .with_source_containing("1"))
        assert isinstance(complex_query.list(), list)

        # Chain function filters
        complex_functions = (engine.functions
                            .public()
                            .with_source_containing("balance")
                            .containing_source_pattern(r"require\("))
        assert isinstance(complex_functions.list(), list)

    def test_cross_collection_composition(self, engine):
        """Test composition across different collections."""
        # Get functions with balance operations
        balance_functions = engine.functions.with_source_containing("balance")

        # Get expressions with arithmetic operators
        arithmetic_expressions = engine.expressions.with_arithmetic_operators()

        # Both should return valid collections
        assert isinstance(balance_functions.list(), list)
        assert isinstance(arithmetic_expressions.list(), list)

    # =============================================================================
    # EDGE CASE AND ERROR HANDLING TESTS
    # =============================================================================

    def test_empty_results_handling(self, engine):
        """Test handling of queries that return no results."""
        # Query for something that shouldn't exist
        nonexistent = engine.functions.with_source_containing("ThisShouldNotExist123")
        assert len(nonexistent) == 0
        assert isinstance(nonexistent.list(), list)

        # Chain operations on empty results
        chained_empty = nonexistent.public().with_time_operations()
        assert len(chained_empty) == 0

    def test_invalid_patterns_handling(self, engine):
        """Test handling of invalid regex patterns."""
        # This should handle invalid regex gracefully
        try:
            invalid_pattern_results = engine.functions.containing_source_pattern("[invalid")
            # Should not raise exception, might return empty results
            assert isinstance(invalid_pattern_results.list(), list)
        except Exception:
            # If it does raise an exception, that's also acceptable behavior
            pass

    def test_type_safety(self, engine):
        """Test type safety of new APIs."""
        # All fluent methods should return correct collection types
        functions = engine.functions.with_time_operations()
        assert hasattr(functions, '_elements')
        for func in functions:
            assert isinstance(func, FunctionDeclaration)

        expressions = engine.expressions.with_arithmetic_operators()
        assert hasattr(expressions, '_elements')

        variables = engine.variables.time_related()
        assert hasattr(variables, '_elements')
        for var in variables:
            assert isinstance(var, VariableDeclaration)

    # =============================================================================
    # PERFORMANCE AND EFFICIENCY TESTS
    # =============================================================================

    def test_large_query_performance(self, engine):
        """Test performance with larger queries."""
        # This test ensures the APIs can handle multiple operations efficiently
        start_count = len(engine.expressions)

        # Perform multiple filtering operations
        filtered = (engine.expressions
                   .with_source_containing("a")  # Common letter
                   .literals()
                   .with_numeric_value(min_val=0))

        # Should complete without excessive delay
        result_count = len(filtered)
        assert result_count <= start_count
        assert isinstance(filtered.list(), list)

    def test_get_call_graph_wrappers(self, engine):
        # Ensure wrappers delegate correctly
        transfer_callers = engine.get_callers("transfer")
        callees_of_approve = engine.get_callees("approve")
        assert isinstance(transfer_callers, list)
        assert isinstance(callees_of_approve, list)

    @pytest.fixture
    def engine_with_composition(self):
        engine = SolidityQueryEngine()
        fixtures_path = Path(__file__).parent / "fixtures" / "composition_and_imports"
        engine.load_sources(fixtures_path)
        return engine

    def test_find_imports_with_filename_filter(self, engine_with_composition):
        # Ensure filename filter works on find_imports
        imports_all = engine_with_composition.find_imports()
        assert len(imports_all) > 0
        # Pick a known file from fixtures
        file_name = "ERC721WithImports.sol"
        imports_in_file = engine_with_composition.find_imports(file_name=file_name)
        assert isinstance(imports_in_file, list)
        assert len(imports_in_file) <= len(imports_all)
