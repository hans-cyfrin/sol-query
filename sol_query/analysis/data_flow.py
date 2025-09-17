"""Data flow analysis for Solidity code."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Union, Tuple, Any
from enum import Enum

from sol_query.core.ast_nodes import (
    ASTNode, Statement, Expression, FunctionDeclaration, VariableDeclaration,
    Identifier, CallExpression, BinaryExpression,
    ReturnStatement, ExpressionStatement
)
from sol_query.core.solidity_constants import is_solidity_keyword


class FlowType(str, Enum):
    """Types of data flow."""
    DIRECT = "direct"          # Direct assignment: a = b
    CONDITIONAL = "conditional"  # Flow through conditions: if (a) then b
    INDIRECT = "indirect"      # Flow through expressions: c = a + b
    PARAMETER = "parameter"    # Flow through function parameters
    RETURN = "return"         # Flow through return values
    DECLARATION = "declaration"  # Variable declaration: uint256 temp = value


@dataclass
class DataFlowPoint:
    """Represents a point in the data flow graph."""
    node: ASTNode
    variable_name: Optional[str] = None
    is_read: bool = False
    is_write: bool = False
    flow_type: FlowType = FlowType.DIRECT

    def __hash__(self):
        return hash((id(self.node), self.variable_name, self.is_read, self.is_write))

    def __eq__(self, other):
        if not isinstance(other, DataFlowPoint):
            return False
        return (self.node == other.node and
                self.variable_name == other.variable_name and
                self.is_read == other.is_read and
                self.is_write == other.is_write)


@dataclass
class DataFlowEdge:
    """Represents an edge in the data flow graph."""
    source: DataFlowPoint
    target: DataFlowPoint
    flow_type: FlowType = FlowType.DIRECT
    condition: Optional[Expression] = None  # For conditional flows


class DataFlowGraph:
    """Represents the data flow graph for a function or scope."""

    def __init__(self):
        self.points: Set[DataFlowPoint] = set()
        self.edges: List[DataFlowEdge] = []
        self.variable_points: Dict[str, List[DataFlowPoint]] = {}

    def add_point(self, point: DataFlowPoint):
        """Add a point to the graph."""
        self.points.add(point)
        if point.variable_name:
            if point.variable_name not in self.variable_points:
                self.variable_points[point.variable_name] = []
            self.variable_points[point.variable_name].append(point)

    def add_edge(self, edge: DataFlowEdge):
        """Add an edge to the graph."""
        self.edges.append(edge)
        self.add_point(edge.source)
        self.add_point(edge.target)

    def get_backward_flow(self, point: DataFlowPoint, max_depth: int = 5) -> List[DataFlowPoint]:
        """Get all points that influence this point (backward data flow)."""
        if max_depth <= 0:
            return []

        result = []
        visited = set()

        def traverse_backward(current_point: DataFlowPoint, depth: int):
            if depth <= 0 or current_point in visited:
                return
            visited.add(current_point)

            for edge in self.edges:
                if edge.target == current_point:
                    result.append(edge.source)
                    traverse_backward(edge.source, depth - 1)

        traverse_backward(point, max_depth)
        return result

    def get_forward_flow(self, point: DataFlowPoint, max_depth: int = 5) -> List[DataFlowPoint]:
        """Get all points influenced by this point (forward data flow)."""
        if max_depth <= 0:
            return []

        result = []
        visited = set()

        def traverse_forward(current_point: DataFlowPoint, depth: int):
            if depth <= 0 or current_point in visited:
                return
            visited.add(current_point)

            for edge in self.edges:
                if edge.source == current_point:
                    result.append(edge.target)
                    traverse_forward(edge.target, depth - 1)

        traverse_forward(point, max_depth)
        return result

    def find_flow_paths(self, source: DataFlowPoint, target: DataFlowPoint,
                       max_depth: int = 10) -> List[List[DataFlowPoint]]:
        """Find all data flow paths between two points."""
        paths = []
        visited = set()

        def find_paths_recursive(current: DataFlowPoint, path: List[DataFlowPoint], depth: int):
            if depth <= 0 or current in visited:
                return

            path.append(current)

            if current == target:
                paths.append(path.copy())
                path.pop()
                return

            visited.add(current)

            for edge in self.edges:
                if edge.source == current:
                    find_paths_recursive(edge.target, path, depth - 1)

            visited.remove(current)
            path.pop()

        find_paths_recursive(source, [], max_depth)
        return paths


class VariableReference:
    """Represents a reference to a variable (read or write)."""

    def __init__(self, variable_name: str, statement: Statement,
                 is_read: bool = False, is_write: bool = False,
                 expression_context: Optional[Expression] = None):
        self.variable_name = variable_name
        self.statement = statement
        self.is_read = is_read
        self.is_write = is_write
        self.expression_context = expression_context

    def __repr__(self):
        access_type = "read" if self.is_read else "write" if self.is_write else "unknown"
        return f"VariableReference({self.variable_name}, {access_type})"


class DataFlowAnalyzer:
    """Analyzes data flow within Solidity functions."""

    def __init__(self):
        self.function_graphs: Dict[str, DataFlowGraph] = {}  # Use function name as key
        self.variable_references: Dict[str, List[VariableReference]] = {}

    def analyze_function(self, function: FunctionDeclaration) -> DataFlowGraph:
        """Analyze data flow within a function."""
        function_key = f"{function.name}_{id(function)}"  # Use function name + id as key
        if function_key in self.function_graphs:
            return self.function_graphs[function_key]

        graph = DataFlowGraph()
        self._build_function_graph(function, graph)
        self.function_graphs[function_key] = graph
        return graph

    def _build_function_graph(self, function: FunctionDeclaration, graph: DataFlowGraph):
        """Build the data flow graph for a function."""
        # Add function parameters as initial points
        if function.parameters:
            for param in function.parameters:
                if hasattr(param, 'name') and param.name:
                    point = DataFlowPoint(
                        node=param,
                        variable_name=param.name,
                        is_read=True,
                        flow_type=FlowType.PARAMETER
                    )
                    graph.add_point(point)

        # Analyze function body
        if function.body:
            # Check if body is a Block object with statements attribute
            if hasattr(function.body, 'statements') and function.body.statements:
                self._analyze_statement_block(function.body.statements, graph)
            elif isinstance(function.body, list):
                # If body is already a list of statements
                self._analyze_statement_block(function.body, graph)

    def _analyze_statement_block(self, statements: List[Statement], graph: DataFlowGraph):
        """Analyze a block of statements."""
        for statement in statements:
            self._analyze_statement(statement, graph)

    def _analyze_statement(self, statement: Statement, graph: DataFlowGraph):
        """Analyze a single statement for data flow."""
        if isinstance(statement, VariableDeclaration):
            # Variable declaration - track as a write point
            if hasattr(statement, 'name') and statement.name:
                # The declaration itself is a write
                write_point = DataFlowPoint(
                    node=statement,
                    variable_name=statement.name,
                    is_write=True,
                    flow_type=FlowType.DECLARATION
                )
                graph.add_point(write_point)

                # If there's an initial value, analyze it and create a flow edge
                if hasattr(statement, 'initial_value') and statement.initial_value:
                    self._analyze_expression(statement.initial_value, graph)
        elif isinstance(statement, ExpressionStatement):
            # First, handle generic patterns (e.g., local variable declarations)
            self._analyze_generic_statement(statement, graph)

            # Then, analyze the contained expression if present
            if hasattr(statement, 'expression') and statement.expression:
                self._analyze_expression(statement.expression, graph)
        elif isinstance(statement, CallExpression):
            self._analyze_call(statement, graph)
        elif isinstance(statement, ReturnStatement):
            self._analyze_return(statement, graph)
        elif hasattr(statement, 'statements') and statement.statements:
            # Block statement
            self._analyze_statement_block(statement.statements, graph)

        # Also analyze any nested expressions
        if hasattr(statement, 'expressions') and statement.expressions:
            for expr in statement.expressions:
                self._analyze_expression(expr, graph)

        # Analyze expression if this statement has one
        if hasattr(statement, 'expression') and statement.expression:
            self._analyze_expression(statement.expression, graph)

    def _analyze_generic_statement(self, statement: ExpressionStatement, graph: DataFlowGraph):
        """Analyze a generic statement which might contain variable declarations."""
        source = statement.get_source_code()

        # Check if this is a variable declaration with assignment
        import re
        # Build pattern for variable declarations using centralized types
        from sol_query.core.solidity_constants import SOLIDITY_TYPES
        type_pattern = '|'.join(SOLIDITY_TYPES) + r'|bytes\d*'  # Include bytesN variants
        var_decl_pattern = rf'({type_pattern})\s+(\w+)\s*=\s*(.+);'
        match = re.match(var_decl_pattern, source.strip())

        if match:
            var_type, var_name, var_value = match.groups()

            # Create a write point for the variable declaration
            write_point = DataFlowPoint(
                node=statement,
                variable_name=var_name,
                is_write=True,
                flow_type=FlowType.DECLARATION
            )
            graph.add_point(write_point)

            # Try to find variables in the value expression and create read points
            # This is a simplified approach - we look for identifiers in the value
            identifier_pattern = r'\b(\w+)\b'
            identifiers = re.findall(identifier_pattern, var_value)

            for identifier in identifiers:
                # Skip Solidity keywords and literals using centralized constants
                if not is_solidity_keyword(identifier) and not identifier.isdigit():
                    read_point = DataFlowPoint(
                        node=statement,  # We use the statement as the node since we don't have the actual identifier node
                        variable_name=identifier,
                        is_read=True,
                        flow_type=FlowType.DIRECT
                    )
                    graph.add_point(read_point)

        # Also check for simple assignment statements: varname = value;
        else:
            assignment_pattern = rf'(\w+)\s*=\s*(.+);'
            assignment_match = re.match(assignment_pattern, source.strip())
            if assignment_match:
                var_name, var_value = assignment_match.groups()

                # Skip if this looks like a function call assignment or complex expression
                if not any(char in var_name for char in ['(', ')', '[', ']', '.']):
                    # Create a write point for the assignment
                    write_point = DataFlowPoint(
                        node=statement,
                        variable_name=var_name,
                        is_write=True,
                        flow_type=FlowType.DIRECT
                    )
                    graph.add_point(write_point)

                    # Find variables in the value expression
                    identifier_pattern = r'\b(\w+)\b'
                    identifiers = re.findall(identifier_pattern, var_value)

                    for identifier in identifiers:
                        if not is_solidity_keyword(identifier) and not identifier.isdigit():
                            read_point = DataFlowPoint(
                                node=statement,
                                variable_name=identifier,
                                is_read=True,
                                flow_type=FlowType.DIRECT
                            )
                            graph.add_point(read_point)

            # Handle if statements - analyze nested statements
            elif source.strip().startswith('if'):
                if hasattr(statement, 'body') and statement.body:
                    if hasattr(statement.body, 'statements'):
                        self._analyze_statement_block(statement.body.statements, graph)
                    elif isinstance(statement.body, list):
                        self._analyze_statement_block(statement.body, graph)

    def _analyze_assignment(self, assignment: Expression, graph: DataFlowGraph):
        """Analyze an assignment expression (simplified implementation)."""
        # For now, just track any variables in the assignment
        variables = self._extract_variables_from_expression(assignment)
        for var_name in variables:
            # Create a generic data flow point
            point = DataFlowPoint(
                node=assignment,
                variable_name=var_name,
                is_read=True,  # Default to read
                flow_type=FlowType.DIRECT
            )
            graph.add_point(point)

    def _analyze_call(self, call: CallExpression, graph: DataFlowGraph):
        """Analyze a function call expression."""
        # Function name/target is a read
        if hasattr(call, 'function') and call.function:
            func_vars = self._extract_variables_from_expression(call.function)
            for var_name in func_vars:
                read_point = DataFlowPoint(
                    node=call,
                    variable_name=var_name,
                    is_read=True,
                    flow_type=FlowType.DIRECT
                )
                graph.add_point(read_point)

        # Arguments are reads
        if hasattr(call, 'arguments') and call.arguments:
            for arg in call.arguments:
                arg_vars = self._extract_variables_from_expression(arg)
                for var_name in arg_vars:
                    read_point = DataFlowPoint(
                        node=call,
                        variable_name=var_name,
                        is_read=True,
                        flow_type=FlowType.PARAMETER
                    )
                    graph.add_point(read_point)

    def _analyze_return(self, return_stmt: ReturnStatement, graph: DataFlowGraph):
        """Analyze a return statement."""
        if hasattr(return_stmt, 'expression') and return_stmt.expression:
            ret_vars = self._extract_variables_from_expression(return_stmt.expression)
            for var_name in ret_vars:
                read_point = DataFlowPoint(
                    node=return_stmt,
                    variable_name=var_name,
                    is_read=True,
                    flow_type=FlowType.RETURN
                )
                graph.add_point(read_point)

    def _analyze_conditional_statement(self, stmt: Statement, graph: DataFlowGraph):
        """Analyze a conditional statement (generic implementation)."""
        # Look for condition-like expressions
        if hasattr(stmt, 'condition') and stmt.condition:
            cond_vars = self._extract_variables_from_expression(stmt.condition)
            for var_name in cond_vars:
                read_point = DataFlowPoint(
                    node=stmt,
                    variable_name=var_name,
                    is_read=True,
                    flow_type=FlowType.CONDITIONAL
                )
                graph.add_point(read_point)

        # Analyze nested statements
        if hasattr(stmt, 'then_statement') and stmt.then_statement:
            if isinstance(stmt.then_statement, list):
                self._analyze_statement_block(stmt.then_statement, graph)
            else:
                self._analyze_statement(stmt.then_statement, graph)

        if hasattr(stmt, 'else_statement') and stmt.else_statement:
            if isinstance(stmt.else_statement, list):
                self._analyze_statement_block(stmt.else_statement, graph)
            else:
                self._analyze_statement(stmt.else_statement, graph)

        # Analyze body if it exists
        if hasattr(stmt, 'body') and stmt.body:
            if isinstance(stmt.body, list):
                self._analyze_statement_block(stmt.body, graph)
            else:
                self._analyze_statement(stmt.body, graph)

    def _analyze_expression(self, expression: Expression, graph: DataFlowGraph):
        """Analyze an expression for data flow."""
        if isinstance(expression, Identifier):
            # Variable reference
            read_point = DataFlowPoint(
                node=expression,
                variable_name=expression.name if hasattr(expression, 'name') else str(expression),
                is_read=True,
                flow_type=FlowType.DIRECT
            )
            graph.add_point(read_point)
        elif isinstance(expression, BinaryExpression):
            # Binary operator expressions - analyze operands
            if hasattr(expression, 'left') and expression.left:
                self._analyze_expression(expression.left, graph)
            if hasattr(expression, 'right') and expression.right:
                self._analyze_expression(expression.right, graph)
        elif isinstance(expression, CallExpression):
            self._analyze_call(expression, graph)

        # Generic handling for any expression with nested expressions
        if hasattr(expression, 'operand') and expression.operand:
            self._analyze_expression(expression.operand, graph)

    def _extract_variables_from_expression(self, expression: Expression) -> Set[str]:
        """Extract variable names from an expression."""
        variables = set()

        if isinstance(expression, Identifier):
            if hasattr(expression, 'name') and expression.name:
                variables.add(expression.name)
        elif isinstance(expression, BinaryExpression):
            if hasattr(expression, 'left') and expression.left:
                variables.update(self._extract_variables_from_expression(expression.left))
            if hasattr(expression, 'right') and expression.right:
                variables.update(self._extract_variables_from_expression(expression.right))
        elif isinstance(expression, CallExpression):
            if hasattr(expression, 'function') and expression.function:
                variables.update(self._extract_variables_from_expression(expression.function))
            if hasattr(expression, 'arguments') and expression.arguments:
                for arg in expression.arguments:
                    variables.update(self._extract_variables_from_expression(arg))

        # Generic handling for operands
        if hasattr(expression, 'operand') and expression.operand:
            variables.update(self._extract_variables_from_expression(expression.operand))

        return variables

    def find_variable_references(self, variable_name: str,
                                function: Optional[FunctionDeclaration] = None) -> List[VariableReference]:
        """Find all references to a variable."""
        references = []

        if function:
            # Search within specific function
            graph = self.analyze_function(function)
            if variable_name in graph.variable_points:
                for point in graph.variable_points[variable_name]:
                    ref = VariableReference(
                        variable_name=variable_name,
                        statement=point.node,
                        is_read=point.is_read,
                        is_write=point.is_write
                    )
                    references.append(ref)
        else:
            # Search across all analyzed functions
            for func_graph in self.function_graphs.values():
                if variable_name in func_graph.variable_points:
                    for point in func_graph.variable_points[variable_name]:
                        ref = VariableReference(
                            variable_name=variable_name,
                            statement=point.node,
                            expression_context=None,
                            is_read=point.is_read,
                            is_write=point.is_write,
                            access_type='direct'
                        )
                        references.append(ref)

        return references

    def trace_variable_flow(self, variable_name: str, direction: str = 'forward',
                           function: Optional[FunctionDeclaration] = None,
                           max_depth: int = 5) -> List[DataFlowPoint]:
        """Trace how a variable flows through the code."""
        result = []

        if function:
            functions_to_search = [function]
        else:
            # Need to reconstruct functions from keys - simplified for now
            functions_to_search = []

        for func in functions_to_search:
            graph = self.analyze_function(func)
            if variable_name in graph.variable_points:
                for point in graph.variable_points[variable_name]:
                    if direction == 'forward':
                        result.extend(graph.get_forward_flow(point, max_depth))
                    elif direction == 'backward':
                        result.extend(graph.get_backward_flow(point, max_depth))
                    elif direction == 'both':
                        result.extend(graph.get_forward_flow(point, max_depth))
                        result.extend(graph.get_backward_flow(point, max_depth))

        return result
