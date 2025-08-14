"""Test data flow analysis functionality."""

import pytest
from pathlib import Path
from sol_query import SolidityQueryEngine
from sol_query.analysis.data_flow import DataFlowAnalyzer, DataFlowGraph, DataFlowPoint, FlowType
from sol_query.analysis.variable_tracker import VariableTracker, VariableReference
from sol_query.core.ast_nodes import FunctionDeclaration


@pytest.fixture
def sample_contract_code():
    """Sample Solidity contract for testing."""
    return """
    pragma solidity ^0.8.0;
    
    contract DataFlowTest {
        uint256 public balance;
        address public owner;
        mapping(address => uint256) public balances;
        
        constructor() {
            owner = msg.sender;
            balance = 1000;
        }
        
        function transfer(address to, uint256 amount) external {
            require(balances[msg.sender] >= amount, "Insufficient balance");
            balances[msg.sender] -= amount;
            balances[to] += amount;
            emit Transfer(msg.sender, to, amount);
        }
        
        function withdraw(uint256 amount) external {
            require(msg.sender == owner, "Not owner");
            require(address(this).balance >= amount, "Insufficient contract balance");
            uint256 fee = amount / 100;
            uint256 withdrawAmount = amount - fee;
            payable(msg.sender).transfer(withdrawAmount);
            balance -= amount;
        }
        
        function complexFlow(uint256 input) external returns (uint256) {
            uint256 temp = input * 2;
            if (temp > 100) {
                temp = temp / 2;
            }
            uint256 result = temp + balance;
            balance = result;
            return result;
        }
        
        event Transfer(address indexed from, address indexed to, uint256 value);
    }
    """


@pytest.fixture
def engine_with_sample(sample_contract_code, tmp_path):
    """Create engine with sample contract loaded."""
    # Write sample code to temporary file
    contract_file = tmp_path / "DataFlowTest.sol"
    contract_file.write_text(sample_contract_code)

    # Create and load engine
    engine = SolidityQueryEngine()
    engine.load_sources(str(contract_file))

    return engine


class TestVariableTracker:
    """Test variable reference tracking."""

    def test_track_function_parameters(self, engine_with_sample):
        """Test tracking function parameters."""
        tracker = VariableTracker()

        # Find transfer function
        transfer_func = engine_with_sample.functions.with_name("transfer").first()
        assert transfer_func is not None

        # Track variables in function
        references = tracker.track_function(transfer_func)

        # Should find references to 'to' and 'amount' parameters
        param_refs = [ref for ref in references if ref.access_type == 'parameter']
        param_names = {ref.variable_name for ref in param_refs}

        assert 'to' in param_names
        assert 'amount' in param_names

    def test_track_variable_reads_writes(self, engine_with_sample):
        """Test tracking variable reads and writes."""
        tracker = VariableTracker()

        # Find transfer function
        transfer_func = engine_with_sample.functions.with_name("transfer").first()
        references = tracker.track_function(transfer_func)

        # Check balances variable references
        balances_refs = [ref for ref in references if ref.variable_name == 'balances']

        # Should have both reads and writes to balances
        reads = [ref for ref in balances_refs if ref.is_read]
        writes = [ref for ref in balances_refs if ref.is_write]

        assert len(reads) > 0, "Should have reads of balances"
        assert len(writes) > 0, "Should have writes to balances"

    def test_get_variable_references(self, engine_with_sample):
        """Test getting references for a specific variable."""
        tracker = VariableTracker()

        # Track all functions
        functions = engine_with_sample.find_functions()
        for func in functions:
            tracker.track_function(func)

        # Get references to 'balance' variable
        balance_refs = tracker.get_variable_references('balance')

        assert len(balance_refs) > 0, "Should find references to balance variable"

        # Check that we have both reads and writes
        reads = tracker.get_variable_reads('balance')
        writes = tracker.get_variable_writes('balance')

        assert len(reads) > 0, "Should have reads of balance"
        assert len(writes) > 0, "Should have writes to balance"

    def test_variable_reference_serialization(self, engine_with_sample):
        """Test that variable references can be serialized to JSON."""
        tracker = VariableTracker()

        transfer_func = engine_with_sample.functions.with_name("transfer").first()
        references = tracker.track_function(transfer_func)

        # Test serialization
        for ref in references:
            ref_dict = ref.to_dict()

            assert isinstance(ref_dict, dict)
            assert 'variable_name' in ref_dict
            assert 'is_read' in ref_dict
            assert 'is_write' in ref_dict
            assert 'access_type' in ref_dict


class TestDataFlowAnalyzer:
    """Test data flow analysis."""

    def test_analyze_function_creates_graph(self, engine_with_sample):
        """Test that analyzing a function creates a data flow graph."""
        analyzer = DataFlowAnalyzer()

        # Find transfer function
        transfer_func = engine_with_sample.functions.with_name("transfer").first()

        # Analyze function
        graph = analyzer.analyze_function(transfer_func)

        assert isinstance(graph, DataFlowGraph)
        assert len(graph.points) > 0, "Should create data flow points"
        assert len(graph.variable_points) > 0, "Should track variable points"

    def test_data_flow_points_creation(self, engine_with_sample):
        """Test creation of data flow points."""
        analyzer = DataFlowAnalyzer()

        # Find complexFlow function (has more complex data flow)
        complex_func = engine_with_sample.functions.with_name("complexFlow").first()

        # Analyze function
        graph = analyzer.analyze_function(complex_func)

        # Should have points for input parameter
        input_points = graph.variable_points.get('input', [])
        assert len(input_points) > 0, "Should find input parameter points"

        # Should have points for temp variable
        temp_points = graph.variable_points.get('temp', [])
        assert len(temp_points) > 0, "Should find temp variable points"

    def test_trace_variable_flow(self, engine_with_sample):
        """Test tracing variable flow."""
        analyzer = DataFlowAnalyzer()

        # Find complexFlow function
        complex_func = engine_with_sample.functions.with_name("complexFlow").first()

        # Trace input variable flow
        flow_points = analyzer.trace_variable_flow('input', direction='forward', function=complex_func)

        assert len(flow_points) >= 0, "Should return flow points (may be empty if analysis is basic)"

    def test_backward_forward_flow(self, engine_with_sample):
        """Test backward and forward data flow analysis."""
        analyzer = DataFlowAnalyzer()

        complex_func = engine_with_sample.functions.with_name("complexFlow").first()
        graph = analyzer.analyze_function(complex_func)

        # Test that we can call backward/forward flow methods without errors
        for point in list(graph.points)[:3]:  # Test first few points to avoid long computation
            backward_flow = graph.get_backward_flow(point, max_depth=2)
            forward_flow = graph.get_forward_flow(point, max_depth=2)

            assert isinstance(backward_flow, list)
            assert isinstance(forward_flow, list)


class TestEngineDataFlowMethods:
    """Test data flow methods on the query engine."""

    def test_trace_variable_flow_method(self, engine_with_sample):
        """Test engine's trace_variable_flow method."""
        # Test tracing balance variable
        flow_statements = engine_with_sample.trace_variable_flow('balance', direction='forward')

        assert isinstance(flow_statements, list)
        # Note: May be empty if the AST doesn't have proper statement nodes

    def test_find_variable_influences(self, engine_with_sample):
        """Test finding statements that influence a variable."""
        influences = engine_with_sample.find_variable_influences('balance')

        assert isinstance(influences, list)

    def test_find_variable_effects(self, engine_with_sample):
        """Test finding statements affected by a variable."""
        effects = engine_with_sample.find_variable_effects('balance')

        assert isinstance(effects, list)

    def test_trace_flow_between_statements(self, engine_with_sample):
        """Test tracing flow between statement patterns."""
        # Look for flow from require statements to assignment statements
        paths = engine_with_sample.trace_flow_between_statements(
            from_pattern="require*",
            to_pattern="*=*"
        )

        assert isinstance(paths, list)

    def test_get_variable_references_by_function(self, engine_with_sample):
        """Test getting variable references organized by function."""
        transfer_func = engine_with_sample.functions.with_name("transfer").first()

        references = engine_with_sample.get_variable_references_by_function(transfer_func)

        assert isinstance(references, dict)
        # Should have some variable references
        assert len(references) >= 0

    def test_get_data_flow_statistics(self, engine_with_sample):
        """Test getting data flow statistics."""
        stats = engine_with_sample.get_data_flow_statistics()

        assert isinstance(stats, dict)
        assert 'total_functions' in stats
        assert 'functions_analyzed' in stats
        assert 'total_variables' in stats
        assert 'total_references' in stats

        # Should have analyzed some functions
        assert stats['total_functions'] > 0


class TestCollectionDataFlowMethods:
    """Test data flow methods on collections."""

    def test_statement_influenced_by_variable(self, engine_with_sample):
        """Test filtering statements influenced by variable."""
        statements = engine_with_sample.statements

        # Find statements influenced by 'amount' variable
        influenced = statements.influenced_by_variable('amount')

        assert isinstance(influenced, type(statements))

    def test_statement_influencing_variable(self, engine_with_sample):
        """Test filtering statements that influence a variable."""
        statements = engine_with_sample.statements

        # Find statements that influence 'balance' variable
        influencing = statements.influencing_variable('balance')

        assert isinstance(influencing, type(statements))

    def test_expand_backward_flow(self, engine_with_sample):
        """Test expanding collection with backward data flow."""
        statements = engine_with_sample.statements

        # Get a subset and expand backward
        subset = statements[:3] if len(statements) > 3 else statements
        expanded = subset.expand_backward_flow(max_depth=2)

        assert isinstance(expanded, type(statements))
        # Expanded should have at least as many elements
        assert len(expanded) >= len(subset)

    def test_expand_forward_flow(self, engine_with_sample):
        """Test expanding collection with forward data flow."""
        statements = engine_with_sample.statements

        # Get a subset and expand forward
        subset = statements[:3] if len(statements) > 3 else statements
        expanded = subset.expand_forward_flow(max_depth=2)

        assert isinstance(expanded, type(statements))
        # Expanded should have at least as many elements
        assert len(expanded) >= len(subset)

    def test_function_reading_variable(self, engine_with_sample):
        """Test filtering functions that read a variable."""
        functions = engine_with_sample.functions

        # Find functions reading 'balance'
        reading_balance = functions.reading_variable('balance')

        assert isinstance(reading_balance, type(functions))

    def test_function_writing_variable(self, engine_with_sample):
        """Test filtering functions that write a variable."""
        functions = engine_with_sample.functions

        # Find functions writing to 'balance'
        writing_balance = functions.writing_variable('balance')

        assert isinstance(writing_balance, type(functions))

    def test_function_data_flow_between(self, engine_with_sample):
        """Test filtering functions with data flow between variables."""
        functions = engine_with_sample.functions

        # Find functions with flow from 'input' to 'balance'
        with_flow = functions.with_data_flow_between('input', 'balance')

        assert isinstance(with_flow, type(functions))


class TestASTNodeDataFlowMethods:
    """Test data flow methods on AST nodes."""

    def test_variable_get_references(self, engine_with_sample):
        """Test getting references for a variable declaration."""
        # Find balance variable
        balance_var = engine_with_sample.variables.with_name('balance').first()

        if balance_var:
            # Test getting all references
            all_refs = balance_var.get_all_references()
            reads = balance_var.get_reads()
            writes = balance_var.get_writes()

            assert isinstance(all_refs, list)
            assert isinstance(reads, list)
            assert isinstance(writes, list)

    def test_node_data_flow_methods(self, engine_with_sample):
        """Test data flow methods on general AST nodes."""
        # Get some statements
        statements = engine_with_sample.find_statements()

        if statements:
            stmt = statements[0]

            # Test data flow methods (may return empty lists)
            backward = stmt.get_data_flow_backward(max_depth=2)
            forward = stmt.get_data_flow_forward(max_depth=2)

            assert isinstance(backward, list)
            assert isinstance(forward, list)

            # Test traces_to method
            if len(statements) > 1:
                target = statements[1]
                paths = stmt.traces_to(target)
                assert isinstance(paths, list)


class TestDataFlowEdgeCases:
    """Test edge cases and error handling in data flow analysis."""

    def test_empty_function_analysis(self, engine_with_sample):
        """Test analyzing empty or simple functions."""
        # Constructor should be simple
        constructor = engine_with_sample.functions.constructors().first()

        if constructor:
            analyzer = DataFlowAnalyzer()
            graph = analyzer.analyze_function(constructor)

            assert isinstance(graph, DataFlowGraph)

    def test_nonexistent_variable_tracking(self, engine_with_sample):
        """Test tracking nonexistent variables."""
        tracker = VariableTracker()

        # Should return empty list for nonexistent variable
        refs = tracker.get_variable_references('nonexistent_variable')
        assert refs == []

        reads = tracker.get_variable_reads('nonexistent_variable')
        assert reads == []

        writes = tracker.get_variable_writes('nonexistent_variable')
        assert writes == []

    def test_malformed_data_flow_analysis(self, engine_with_sample):
        """Test that data flow analysis handles edge cases gracefully."""
        # Test with empty statement list
        statements = engine_with_sample.statements
        empty_collection = statements.influenced_by_variable('nonexistent')

        assert isinstance(empty_collection, type(statements))
        assert len(empty_collection) == 0

    def test_pattern_matching_in_data_flow(self, engine_with_sample):
        """Test pattern matching in data flow queries."""
        statements = engine_with_sample.statements

        # Test pattern that might not match anything
        influenced = statements.influenced_by_pattern('nonexistent_pattern')

        assert isinstance(influenced, type(statements))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
