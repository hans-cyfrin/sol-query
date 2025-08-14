"""Variable reference tracking for data flow analysis."""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass

from sol_query.core.ast_nodes import (
    ASTNode, FunctionDeclaration, Statement, Expression,
    VariableDeclaration, Identifier, CallExpression, BinaryExpression,
    ExpressionStatement, ArrayAccess
)


@dataclass
class VariableReference:
    """Represents a reference to a variable in the code."""
    variable_name: str
    statement: Statement
    expression_context: Optional[Expression]
    is_read: bool
    is_write: bool
    access_type: str  # 'direct', 'member', 'index', 'parameter'
    scope_function: Optional[FunctionDeclaration] = None

    def __post_init__(self):
        """Validate the reference."""
        if not self.is_read and not self.is_write:
            # Default to read if neither specified
            self.is_read = True

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            'variable_name': self.variable_name,
            'statement_type': type(self.statement).__name__,
            'statement_source': getattr(self.statement, 'source_code', lambda: "")() if hasattr(self.statement, 'source_code') else "",
            'is_read': self.is_read,
            'is_write': self.is_write,
            'access_type': self.access_type,
            'function_name': self.scope_function.name if self.scope_function and hasattr(self.scope_function, 'name') else None,
            'source_location': getattr(self.statement, 'source_location', None)
        }


class VariableTracker:
    """Tracks variable references and definitions across functions."""

    def __init__(self):
        self.references_by_variable: Dict[str, List[VariableReference]] = {}
        self.references_by_function: Dict[str, List[VariableReference]] = {}  # Use function name as key
        self.variable_definitions: Dict[str, List[VariableDeclaration]] = {}
        self.function_parameters: Dict[str, List[str]] = {}  # Use function name as key

    def track_function(self, function: FunctionDeclaration) -> List[VariableReference]:
        """Track all variable references in a function."""
        function_key = f"{function.name}_{id(function)}"  # Use function name + id as key
        if function_key in self.references_by_function:
            return self.references_by_function[function_key]

        references = []

        # Track function parameters
        if hasattr(function, 'parameters') and function.parameters:
            param_names = []
            for param in function.parameters:
                if hasattr(param, 'name') and param.name:
                    param_names.append(param.name)
                    # Parameters are implicitly read when the function is called
                    ref = VariableReference(
                        variable_name=param.name,
                        statement=function,  # The function itself as the statement
                        expression_context=None,
                        is_read=True,
                        is_write=False,
                        access_type='parameter',
                        scope_function=function
                    )
                    references.append(ref)
            self.function_parameters[function_key] = param_names

        # Track references in function body
        if hasattr(function, 'body') and function.body:
            if isinstance(function.body, list):
                for stmt in function.body:
                    references.extend(self._track_statement(stmt, function))
            else:
                references.extend(self._track_statement(function.body, function))

        # Store references
        self.references_by_function[function_key] = references
        for ref in references:
            if ref.variable_name not in self.references_by_variable:
                self.references_by_variable[ref.variable_name] = []
            self.references_by_variable[ref.variable_name].append(ref)

        return references

    def _track_statement(self, statement: Statement, function: FunctionDeclaration) -> List[VariableReference]:
        """Track variable references in a statement."""
        references = []

        # Handle specific statement types
        if isinstance(statement, ExpressionStatement):
            if hasattr(statement, 'expression') and statement.expression:
                references.extend(self._track_expression(statement.expression, statement, function, is_read=True))
        elif isinstance(statement, CallExpression):
            references.extend(self._track_call(statement, function))
        elif isinstance(statement, VariableDeclaration):
            references.extend(self._track_variable_declaration(statement, function))
        elif hasattr(statement, 'condition'):
            # If/while/for statements with conditions
            if statement.condition:
                references.extend(self._track_expression(statement.condition, statement, function, is_read=True))
        else:
            # Handle generic statements that may have nested expressions
            if hasattr(statement, '_nested_expressions') and statement._nested_expressions:
                for expr in statement._nested_expressions:
                    references.extend(self._track_expression(expr, statement, function, is_read=True))

        # Track nested statements
        if hasattr(statement, 'statements') and statement.statements:
            for nested_stmt in statement.statements:
                references.extend(self._track_statement(nested_stmt, function))
        elif hasattr(statement, 'body') and statement.body:
            if isinstance(statement.body, list):
                for nested_stmt in statement.body:
                    references.extend(self._track_statement(nested_stmt, function))
            else:
                references.extend(self._track_statement(statement.body, function))

        # Track then/else statements
        if hasattr(statement, 'then_statement') and statement.then_statement:
            if isinstance(statement.then_statement, list):
                for nested_stmt in statement.then_statement:
                    references.extend(self._track_statement(nested_stmt, function))
            else:
                references.extend(self._track_statement(statement.then_statement, function))

        if hasattr(statement, 'else_statement') and statement.else_statement:
            if isinstance(statement.else_statement, list):
                for nested_stmt in statement.else_statement:
                    references.extend(self._track_statement(nested_stmt, function))
            else:
                references.extend(self._track_statement(statement.else_statement, function))

        return references

    def _track_generic_expression(self, expression: Expression, statement: Statement, function: FunctionDeclaration) -> List[VariableReference]:
        """Track variable references in a generic expression."""
        references = []

        # For generic expressions, we'll treat most operations as reads
        references.extend(self._track_expression(expression, statement, function, is_read=True))

        return references

    def _track_call(self, call: CallExpression, function: FunctionDeclaration) -> List[VariableReference]:
        """Track variable references in a function call."""
        references = []

        # Function target
        if hasattr(call, 'function') and call.function:
            references.extend(self._track_expression(call.function, call, function, is_read=True))

        # Arguments
        if hasattr(call, 'arguments') and call.arguments:
            for arg in call.arguments:
                references.extend(self._track_expression(arg, call, function, is_read=True))

        return references

    def _track_variable_declaration(self, var_decl: VariableDeclaration, function: FunctionDeclaration) -> List[VariableReference]:
        """Track variable references in a variable declaration."""
        references = []

        # Store the declaration
        if hasattr(var_decl, 'name') and var_decl.name:
            if var_decl.name not in self.variable_definitions:
                self.variable_definitions[var_decl.name] = []
            self.variable_definitions[var_decl.name].append(var_decl)

            # Declaration is a write
            ref = VariableReference(
                variable_name=var_decl.name,
                statement=var_decl,
                expression_context=None,
                is_read=False,
                is_write=True,
                access_type='direct',
                scope_function=function
            )
            references.append(ref)

        # Initial value is a read
        if hasattr(var_decl, 'initial_value') and var_decl.initial_value:
            references.extend(self._track_expression(var_decl.initial_value, var_decl, function, is_read=True))

        return references

    def _track_expression(self, expression: Expression, statement: Statement,
                         function: FunctionDeclaration, is_read: bool = False,
                         is_write: bool = False) -> List[VariableReference]:
        """Track variable references in an expression."""
        references = []

        if isinstance(expression, Identifier):
            # Simple variable reference
            if hasattr(expression, 'name') and expression.name:
                ref = VariableReference(
                    variable_name=expression.name,
                    statement=statement,
                    expression_context=expression,
                    is_read=is_read,
                    is_write=is_write,
                    access_type='direct',
                    scope_function=function
                )
                references.append(ref)

        elif isinstance(expression, ArrayAccess):
            # Array[index] access
            # Index is always a read (to determine which element to access)
            if hasattr(expression, 'index') and expression.index:
                references.extend(self._track_expression(expression.index, statement, function, is_read=True))

            # The array base itself inherits the read/write from the context
            if hasattr(expression, 'base') and isinstance(expression.base, Identifier):
                if hasattr(expression.base, 'name'):
                    ref = VariableReference(
                        variable_name=expression.base.name,
                        statement=statement,
                        expression_context=expression,
                        is_read=is_read,
                        is_write=is_write,
                        access_type='index',
                        scope_function=function
                    )
                    references.append(ref)
            elif hasattr(expression, 'base') and expression.base:
                # Handle non-identifier base (e.g., nested array access)
                references.extend(self._track_expression(expression.base, statement, function, is_read=is_read, is_write=is_write))

        elif isinstance(expression, BinaryExpression):
            # Binary operations - handle assignment vs other operations
            if hasattr(expression, 'operator'):
                operator = expression.operator
                if operator == '=':
                    # Assignment: left side is write, right side is read
                    if hasattr(expression, 'left') and expression.left:
                        references.extend(self._track_expression(expression.left, statement, function, is_read=False, is_write=True))
                    if hasattr(expression, 'right') and expression.right:
                        references.extend(self._track_expression(expression.right, statement, function, is_read=True))
                elif operator in ['+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=']:
                    # Compound assignment: left side is both read and write, right side is read
                    if hasattr(expression, 'left') and expression.left:
                        references.extend(self._track_expression(expression.left, statement, function, is_read=True, is_write=True))
                    if hasattr(expression, 'right') and expression.right:
                        references.extend(self._track_expression(expression.right, statement, function, is_read=True))
                else:
                    # Other binary operations: both sides are reads
                    if hasattr(expression, 'left') and expression.left:
                        references.extend(self._track_expression(expression.left, statement, function, is_read=True))
                    if hasattr(expression, 'right') and expression.right:
                        references.extend(self._track_expression(expression.right, statement, function, is_read=True))
            else:
                # No operator detected, treat as reads
                if hasattr(expression, 'left') and expression.left:
                    references.extend(self._track_expression(expression.left, statement, function, is_read=True))
                if hasattr(expression, 'right') and expression.right:
                    references.extend(self._track_expression(expression.right, statement, function, is_read=True))

        # Handle assignment expressions (compound assignments like +=, -=, etc.)
        elif hasattr(expression, 'node_type') and str(expression.node_type) == 'NodeType.ASSIGNMENT_EXPRESSION':
            # For assignment expressions, we need to parse the source to understand the structure
            source = expression.get_source_code()
            # Look for patterns like "variable += value" or "array[index] -= value"
            if any(op in source for op in ['+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '++', '--']):
                # This is a compound assignment - the left side is both read and written
                # Try to extract the variable being assigned
                import re

                # Pattern for simple variable assignment: var += expr
                simple_match = re.match(r'(\w+)\s*[+\-*/%&|^<>]+?=', source)
                if simple_match:
                    var_name = simple_match.group(1)
                    ref = VariableReference(
                        variable_name=var_name,
                        statement=statement,
                        expression_context=expression,
                        is_read=True,
                        is_write=True,
                        access_type='direct',
                        scope_function=function
                    )
                    references.append(ref)

                # Pattern for array access assignment: array[index] += expr
                array_match = re.match(r'(\w+)\s*\[[^\]]+\]\s*[+\-*/%&|^<>]+?=', source)
                if array_match:
                    var_name = array_match.group(1)
                    ref = VariableReference(
                        variable_name=var_name,
                        statement=statement,
                        expression_context=expression,
                        is_read=True,
                        is_write=True,
                        access_type='index',
                        scope_function=function
                    )
                    references.append(ref)

        # Handle any expression with operands generically
        elif hasattr(expression, 'operand') and expression.operand:
            references.extend(self._track_expression(expression.operand, statement, function, is_read=True))

        elif isinstance(expression, CallExpression):
            # Nested function calls
            references.extend(self._track_call(expression, function))

        return references

    def get_variable_references(self, variable_name: str,
                               function: Optional[FunctionDeclaration] = None) -> List[VariableReference]:
        """Get all references to a variable."""
        if variable_name not in self.references_by_variable:
            return []

        references = self.references_by_variable[variable_name]

        if function:
            # Filter by function
            return [ref for ref in references if ref.scope_function == function]

        return references

    def get_variable_reads(self, variable_name: str,
                          function: Optional[FunctionDeclaration] = None) -> List[VariableReference]:
        """Get all read references to a variable."""
        references = self.get_variable_references(variable_name, function)
        return [ref for ref in references if ref.is_read]

    def get_variable_writes(self, variable_name: str,
                           function: Optional[FunctionDeclaration] = None) -> List[VariableReference]:
        """Get all write references to a variable."""
        references = self.get_variable_references(variable_name, function)
        return [ref for ref in references if ref.is_write]

    def get_function_variables(self, function: FunctionDeclaration) -> Set[str]:
        """Get all variables referenced in a function."""
        function_key = f"{function.name}_{id(function)}"
        if function_key not in self.references_by_function:
            self.track_function(function)

        variables = set()
        for ref in self.references_by_function[function_key]:
            variables.add(ref.variable_name)

        return variables

    def find_variables_by_pattern(self, pattern: str) -> List[str]:
        """Find variables matching a name pattern."""
        import re

        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        if not regex_pattern.startswith('^'):
            regex_pattern = '^' + regex_pattern
        if not regex_pattern.endswith('$'):
            regex_pattern = regex_pattern + '$'

        regex = re.compile(regex_pattern, re.IGNORECASE)

        matching_vars = []
        for var_name in self.references_by_variable.keys():
            if regex.match(var_name):
                matching_vars.append(var_name)

        return matching_vars

    def get_statistics(self) -> Dict:
        """Get statistics about tracked variables."""
        total_variables = len(self.references_by_variable)
        total_references = sum(len(refs) for refs in self.references_by_variable.values())
        total_functions = len(self.references_by_function)

        read_count = 0
        write_count = 0
        for refs in self.references_by_variable.values():
            for ref in refs:
                if ref.is_read:
                    read_count += 1
                if ref.is_write:
                    write_count += 1

        return {
            'total_variables': total_variables,
            'total_references': total_references,
            'total_functions': total_functions,
            'read_references': read_count,
            'write_references': write_count,
            'variables_with_definitions': len(self.variable_definitions)
        }
