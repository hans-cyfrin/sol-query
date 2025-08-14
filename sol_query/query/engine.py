"""Unified query engine supporting both traditional and fluent query styles."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Pattern, Callable, Type

from sol_query.core.source_manager import SourceManager
from sol_query.core.ast_nodes import (
    ASTNode, ContractDeclaration, FunctionDeclaration, VariableDeclaration,
    ModifierDeclaration, EventDeclaration, ErrorDeclaration, StructDeclaration,
    EnumDeclaration, Statement, Expression, Visibility, StateMutability
)
from sol_query.query.collections import (
    ContractCollection, FunctionCollection, VariableCollection,
    ModifierCollection, EventCollection, StatementCollection, ExpressionCollection
)
from sol_query.utils.pattern_matching import PatternMatcher


class SolidityQueryEngine:
    """
    Unified query engine for Solidity code analysis.
    
    Provides both traditional finder methods and fluent collection-based access.
    Supports comprehensive querying of contracts, functions, variables, and other elements.
    """

    def __init__(self, source_paths: Optional[Union[str, Path, List[Union[str, Path]]]] = None):
        """
        Initialize the query engine.
        
        Args:
            source_paths: Optional path(s) to load initially. Can be:
                         - String or Path to a file or directory
                         - List of strings/Paths for multiple sources
        """
        self.source_manager = SourceManager()
        self.pattern_matcher = PatternMatcher()

        # Load initial sources if provided
        if source_paths:
            self.load_sources(source_paths)

    def load_sources(self, source_paths: Union[str, Path, List[Union[str, Path]]]) -> None:
        """
        Load source files or directories.
        
        Args:
            source_paths: Path(s) to load. Can be files, directories, or lists thereof.
        """
        if isinstance(source_paths, (str, Path)):
            source_paths = [source_paths]

        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                self.source_manager.add_file(path)
            elif path.is_dir():
                self.source_manager.add_directory(path, recursive=True)

    # Traditional finder methods
    def find_contracts(self,
                      name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                      inheritance: Optional[Union[str, List[str]]] = None,
                      kind: Optional[str] = None,
                      **filters: Any) -> List[ContractDeclaration]:
        """
        Find contracts matching the specified criteria.
        
        Args:
            name_patterns: Name patterns to match (string, regex, or list)
            inheritance: Base contracts/interfaces this contract inherits from
            kind: Contract kind ("contract", "interface", "library")
            **filters: Additional filter conditions
            
        Returns:
            List of matching contracts
        """
        contracts = self.source_manager.get_contracts()
        return self._filter_contracts(contracts, name_patterns, inheritance, kind, **filters)

    def find_functions(self,
                      name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                      visibility: Optional[Union[Visibility, List[Visibility]]] = None,
                      modifiers: Optional[Union[str, List[str]]] = None,
                      state_mutability: Optional[Union[StateMutability, List[StateMutability]]] = None,
                      contract_name: Optional[str] = None,
                      **filters: Any) -> List[FunctionDeclaration]:
        """
        Find functions matching the specified criteria.
        
        Args:
            name_patterns: Function name patterns to match
            visibility: Function visibility (public, private, internal, external)
            modifiers: Modifier names that must be present
            state_mutability: State mutability (pure, view, payable, nonpayable)
            contract_name: Name of contract containing the function
            **filters: Additional filter conditions
            
        Returns:
            List of matching functions
        """
        functions = self._get_all_functions(contract_name)
        return self._filter_functions(functions, name_patterns, visibility, modifiers,
                                    state_mutability, **filters)

    def find_variables(self,
                      name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                      type_patterns: Optional[Union[str, List[str], Pattern]] = None,
                      visibility: Optional[Union[Visibility, List[Visibility]]] = None,
                      is_state_variable: Optional[bool] = None,
                      contract_name: Optional[str] = None,
                      **filters: Any) -> List[VariableDeclaration]:
        """
        Find variables matching the specified criteria.
        
        Args:
            name_patterns: Variable name patterns to match
            type_patterns: Variable type patterns to match
            visibility: Variable visibility
            is_state_variable: Whether to find only state variables
            contract_name: Name of contract containing the variable
            **filters: Additional filter conditions
            
        Returns:
            List of matching variables
        """
        variables = self._get_all_variables(contract_name, is_state_variable)
        return self._filter_variables(variables, name_patterns, type_patterns,
                                    visibility, **filters)

    def find_modifiers(self,
                      name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                      contract_name: Optional[str] = None,
                      **filters: Any) -> List[ModifierDeclaration]:
        """
        Find modifiers matching the specified criteria.
        
        Args:
            name_patterns: Modifier name patterns to match
            contract_name: Name of contract containing the modifier
            **filters: Additional filter conditions
            
        Returns:
            List of matching modifiers
        """
        modifiers = self._get_all_modifiers(contract_name)
        return self._filter_modifiers(modifiers, name_patterns, **filters)

    def find_events(self,
                   name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                   contract_name: Optional[str] = None,
                   **filters: Any) -> List[EventDeclaration]:
        """
        Find events matching the specified criteria.
        
        Args:
            name_patterns: Event name patterns to match
            contract_name: Name of contract containing the event
            **filters: Additional filter conditions
            
        Returns:
            List of matching events
        """
        events = self._get_all_events(contract_name)
        return self._filter_events(events, name_patterns, **filters)

    def find_structs(self,
                    name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                    contract_name: Optional[str] = None,
                    **filters: Any) -> List[StructDeclaration]:
        """
        Find structs matching the specified criteria.
        
        Args:
            name_patterns: Struct name patterns to match
            contract_name: Name of contract containing the struct
            **filters: Additional filter conditions
            
        Returns:
            List of matching structs
        """
        structs = self._get_all_structs(contract_name)
        return self._filter_structs(structs, name_patterns, **filters)

    def find_enums(self,
                  name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                  contract_name: Optional[str] = None,
                  **filters: Any) -> List[EnumDeclaration]:
        """
        Find enums matching the specified criteria.
        
        Args:
            name_patterns: Enum name patterns to match
            contract_name: Name of contract containing the enum
            **filters: Additional filter conditions
            
        Returns:
            List of matching enums
        """
        enums = self._get_all_enums(contract_name)
        return self._filter_enums(enums, name_patterns, **filters)

    def find_errors(self,
                   name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                   contract_name: Optional[str] = None,
                   **filters: Any) -> List[ErrorDeclaration]:
        """
        Find custom errors matching the specified criteria.
        
        Args:
            name_patterns: Error name patterns to match
            contract_name: Name of contract containing the error
            **filters: Additional filter conditions
            
        Returns:
            List of matching errors
        """
        errors = self._get_all_errors(contract_name)
        return self._filter_errors(errors, name_patterns, **filters)

    def find_statements(self,
                       statement_types: Optional[Union[str, List[str]]] = None,
                       contract_name: Optional[str] = None,
                       function_name: Optional[str] = None,
                       **filters: Any) -> List[Statement]:
        """
        Find statements matching the specified criteria.
        
        Args:
            statement_types: Types of statements to find
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching statements
        """
        statements = self._get_all_statements(contract_name, function_name)
        return self._filter_statements(statements, statement_types, **filters)

    def find_expressions(self,
                        expression_types: Optional[Union[str, List[str]]] = None,
                        contract_name: Optional[str] = None,
                        function_name: Optional[str] = None,
                        **filters: Any) -> List[Expression]:
        """
        Find expressions matching the specified criteria.
        
        Args:
            expression_types: Types of expressions to find
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching expressions
        """
        expressions = self._get_all_expressions(contract_name, function_name)
        return self._filter_expressions(expressions, expression_types, **filters)

    def find_calls(self,
                  target_patterns: Optional[Union[str, List[str], Pattern]] = None,
                  contract_name: Optional[str] = None,
                  function_name: Optional[str] = None,
                  **filters: Any) -> List:
        """
        Find function calls matching the specified criteria.
        
        Args:
            target_patterns: Patterns for called function names
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching call expressions
        """
        expressions = self._get_all_expressions(contract_name, function_name)
        calls = [e for e in expressions if hasattr(e, 'node_type') and
                e.node_type.value == "call_expression"]
        return self._filter_calls(calls, target_patterns, **filters)

    def find_literals(self,
                     literal_types: Optional[Union[str, List[str]]] = None,
                     contract_name: Optional[str] = None,
                     function_name: Optional[str] = None,
                     **filters: Any) -> List:
        """
        Find literals matching the specified criteria.
        
        Args:
            literal_types: Types of literals to find (string, number, bool)
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching literals
        """
        expressions = self._get_all_expressions(contract_name, function_name)
        literals = [e for e in expressions if hasattr(e, 'node_type') and
                   e.node_type.value == "literal"]
        return self._filter_literals(literals, literal_types, **filters)

    def find_identifiers(self,
                        name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                        contract_name: Optional[str] = None,
                        function_name: Optional[str] = None,
                        **filters: Any) -> List:
        """
        Find identifiers matching the specified criteria.
        
        Args:
            name_patterns: Identifier name patterns to match
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching identifiers
        """
        expressions = self._get_all_expressions(contract_name, function_name)
        identifiers = [e for e in expressions if hasattr(e, 'node_type') and
                      e.node_type.value == "identifier"]
        return self._filter_identifiers(identifiers, name_patterns, **filters)

    # Statement-specific finders
    def find_loops(self,
                   loop_types: Optional[Union[str, List[str]]] = None,
                   contract_name: Optional[str] = None,
                   function_name: Optional[str] = None,
                   **filters: Any) -> List[Statement]:
        """
        Find loop statements matching the specified criteria.
        
        Args:
            loop_types: Types of loops to find (for, while, do-while)
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching loop statements
        """
        statements = self._get_all_statements(contract_name, function_name)
        loop_types_set = {"for_statement", "while_statement", "do_while_statement"}
        if loop_types:
            type_list = [loop_types] if isinstance(loop_types, str) else loop_types
            loop_types_set = {f"{t}_statement" for t in type_list}

        loops = [s for s in statements if hasattr(s, 'node_type') and
                s.node_type.value in loop_types_set]
        return self._filter_statements(loops, None, **filters)

    def find_conditionals(self,
                         contract_name: Optional[str] = None,
                         function_name: Optional[str] = None,
                         **filters: Any) -> List[Statement]:
        """
        Find conditional statements (if/else) matching the specified criteria.
        
        Args:
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching conditional statements
        """
        statements = self._get_all_statements(contract_name, function_name)
        conditionals = [s for s in statements if hasattr(s, 'node_type') and
                       s.node_type.value == "if_statement"]
        return self._filter_statements(conditionals, None, **filters)

    def find_assignments(self,
                        contract_name: Optional[str] = None,
                        function_name: Optional[str] = None,
                        **filters: Any) -> List[Statement]:
        """
        Find assignment statements matching the specified criteria.
        
        Args:
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching assignment statements
        """
        statements = self._get_all_statements(contract_name, function_name)
        assignments = [s for s in statements if hasattr(s, 'node_type') and
                      s.node_type.value in {"assignment_statement", "expression_statement"}]
        return self._filter_statements(assignments, None, **filters)

    def find_returns(self,
                    contract_name: Optional[str] = None,
                    function_name: Optional[str] = None,
                    **filters: Any) -> List[Statement]:
        """
        Find return statements matching the specified criteria.
        
        Args:
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching return statements
        """
        statements = self._get_all_statements(contract_name, function_name)
        returns = [s for s in statements if hasattr(s, 'node_type') and
                  s.node_type.value == "return_statement"]
        return self._filter_statements(returns, None, **filters)

    def find_requires(self,
                     contract_name: Optional[str] = None,
                     function_name: Optional[str] = None,
                     **filters: Any) -> List[Statement]:
        """
        Find require statements matching the specified criteria.
        
        Args:
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching require statements
        """
        # Look for call expressions with "require" function name
        expressions = self._get_all_expressions(contract_name, function_name)
        requires = []
        for expr in expressions:
            if (hasattr(expr, 'node_type') and expr.node_type.value == "call_expression" and
                hasattr(expr, 'function') and hasattr(expr.function, 'name') and
                expr.function.name == "require"):
                requires.append(expr)
        return requires

    def find_emits(self,
                  contract_name: Optional[str] = None,
                  function_name: Optional[str] = None,
                  **filters: Any) -> List[Statement]:
        """
        Find emit statements matching the specified criteria.
        
        Args:
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching emit statements
        """
        statements = self._get_all_statements(contract_name, function_name)
        emits = [s for s in statements if hasattr(s, 'node_type') and
                s.node_type.value == "emit_statement"]
        return self._filter_statements(emits, None, **filters)

    # Expression-specific finders
    def find_binary_operations(self,
                              operators: Optional[Union[str, List[str]]] = None,
                              contract_name: Optional[str] = None,
                              function_name: Optional[str] = None,
                              **filters: Any) -> List[Expression]:
        """
        Find binary operations matching the specified criteria.
        
        Args:
            operators: Operators to match (+, -, *, /, ==, !=, etc.)
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching binary expressions
        """
        expressions = self._get_all_expressions(contract_name, function_name)
        binary_ops = [e for e in expressions if hasattr(e, 'node_type') and
                     e.node_type.value == "binary_expression"]

        if operators:
            op_list = [operators] if isinstance(operators, str) else operators
            binary_ops = [e for e in binary_ops if hasattr(e, 'operator') and
                         e.operator in op_list]

        return self._filter_expressions(binary_ops, None, **filters)

    def find_unary_operations(self,
                             operators: Optional[Union[str, List[str]]] = None,
                             contract_name: Optional[str] = None,
                             function_name: Optional[str] = None,
                             **filters: Any) -> List[Expression]:
        """
        Find unary operations matching the specified criteria.
        
        Args:
            operators: Operators to match (!, -, +, ++, --, etc.)
            contract_name: Name of contract to search in
            function_name: Name of function to search in
            **filters: Additional filter conditions
            
        Returns:
            List of matching unary expressions
        """
        expressions = self._get_all_expressions(contract_name, function_name)
        unary_ops = [e for e in expressions if hasattr(e, 'node_type') and
                    e.node_type.value == "unary_expression"]

        if operators:
            op_list = [operators] if isinstance(operators, str) else operators
            unary_ops = [e for e in unary_ops if hasattr(e, 'operator') and
                        e.operator in op_list]

        return self._filter_expressions(unary_ops, None, **filters)

    # Fluent collection access points (Glider-inspired)
    @property
    def contracts(self) -> ContractCollection:
        """Entry point for fluent contract queries."""
        contracts = self.source_manager.get_contracts()
        return ContractCollection(contracts, self)

    @property
    def functions(self) -> FunctionCollection:
        """Entry point for fluent function queries."""
        functions = self._get_all_functions()
        return FunctionCollection(functions, self)

    @property
    def variables(self) -> VariableCollection:
        """Entry point for fluent variable queries."""
        variables = self._get_all_variables()
        return VariableCollection(variables, self)

    @property
    def modifiers(self) -> ModifierCollection:
        """Entry point for fluent modifier queries."""
        modifiers = self._get_all_modifiers()
        return ModifierCollection(modifiers, self)

    @property
    def events(self) -> EventCollection:
        """Entry point for fluent event queries."""
        events = self._get_all_events()
        return EventCollection(events, self)

    @property
    def statements(self) -> StatementCollection:
        """Entry point for fluent statement queries."""
        statements = self._get_all_statements()
        return StatementCollection(statements, self)

    @property
    def expressions(self) -> ExpressionCollection:
        """Entry point for fluent expression queries."""
        expressions = self._get_all_expressions()
        return ExpressionCollection(expressions, self)

    # Advanced analysis methods
    def find_references_to(self, target: Union[str, ASTNode], **filters: Any) -> List[ASTNode]:
        """Find all references to a target symbol or node."""
        target_name = target if isinstance(target, str) else getattr(target, 'name', str(target))

        # Find all identifiers that match the target name
        identifiers = self.find_identifiers(name_patterns=target_name, **filters)

        # Also look for call expressions that target this function
        calls = self.find_calls(target_patterns=target_name, **filters)

        # Combine results
        references = []
        references.extend(identifiers)
        references.extend(calls)

        return references

    def find_callers_of(self, target: Union[str, FunctionDeclaration],
                       depth: int = 1, **filters: Any) -> List[FunctionDeclaration]:
        """Find functions that call the target function."""
        target_name = target if isinstance(target, str) else target.name

        # Find all call expressions that target this function
        target_calls = self.find_calls(target_patterns=target_name, **filters)

        # Find the functions that contain these calls
        callers = []
        all_functions = self._get_all_functions()

        for function in all_functions:
            if function.body:
                # Check if this function contains any of the target calls
                function_statements = self._extract_statements_from_block(function.body)
                function_expressions = []
                for stmt in function_statements:
                    function_expressions.extend(self._extract_expressions_from_statement(stmt))

                # Check if any target calls are in this function
                for call in target_calls:
                    if any(self._expressions_match(call, expr) for expr in function_expressions):
                        if function not in callers:
                            callers.append(function)
                        break

        return callers

    def find_callees_of(self, source: Union[str, FunctionDeclaration],
                       depth: int = 1, **filters: Any) -> List[FunctionDeclaration]:
        """Find functions called by the source function."""
        source_name = source if isinstance(source, str) else source.name

        # Get the source function
        source_functions = self.find_functions(name_patterns=source_name)
        if not source_functions:
            return []

        source_function = source_functions[0]  # Take the first match
        if not source_function.body:
            return []

        # Extract all call expressions from the source function
        function_statements = self._extract_statements_from_block(source_function.body)
        function_calls = []

        for stmt in function_statements:
            expressions = self._extract_expressions_from_statement(stmt)
            for expr in expressions:
                if hasattr(expr, 'node_type') and expr.node_type.value == "call_expression":
                    function_calls.append(expr)

        # Find the functions being called
        callees = []
        all_functions = self._get_all_functions()

        for call in function_calls:
            if hasattr(call, 'function') and hasattr(call.function, 'name'):
                call_target = call.function.name
                # Find matching functions
                matching_functions = [f for f in all_functions if f.name == call_target]
                callees.extend(matching_functions)

        # Remove duplicates
        unique_callees = []
        for callee in callees:
            if callee not in unique_callees:
                unique_callees.append(callee)

        return unique_callees

    def find_call_chains(self, from_element: Union[str, FunctionDeclaration],
                        to_element: Union[str, FunctionDeclaration],
                        max_depth: int = 10) -> List[List[FunctionDeclaration]]:
        """
        Find call chains from one function to another.
        
        Args:
            from_element: Starting function (name or declaration)
            to_element: Target function (name or declaration)
            max_depth: Maximum chain depth to search
            
        Returns:
            List of call chains (each chain is a list of functions)
        """
        from_name = from_element if isinstance(from_element, str) else from_element.name
        to_name = to_element if isinstance(to_element, str) else to_element.name

        # Get all functions for reference
        all_functions = self._get_all_functions()
        func_by_name = {f.name: f for f in all_functions}

        # Find starting function
        if from_name not in func_by_name:
            return []

        start_func = func_by_name[from_name]
        chains = []

        def find_chains_recursive(current_func, target_name, path, depth):
            if depth > max_depth:
                return

            if current_func.name == target_name:
                chains.append(path + [current_func])
                return

            # Find functions called by current function
            callees = self.find_callees_of(current_func.name, depth=1)

            for callee in callees:
                if callee not in path:  # Avoid cycles
                    find_chains_recursive(callee, target_name, path + [current_func], depth + 1)

        find_chains_recursive(start_func, to_name, [], 0)
        return chains

    def find_by_pattern(self, pattern: Union[str, Pattern], **filters: Any) -> List[ASTNode]:
        """Find nodes matching a regex pattern in their source code."""
        all_nodes = self._get_all_nodes()
        matching_nodes = []

        for node in all_nodes:
            if self.pattern_matcher.matches_text_pattern(node.get_source_code(), pattern):
                matching_nodes.append(node)

        return matching_nodes

    def find_by_custom_predicate(self, predicate: Callable[[ASTNode], bool],
                                element_types: Optional[List[Type[ASTNode]]] = None,
                                **filters: Any) -> List[ASTNode]:
        """Find nodes matching a custom predicate function."""
        all_nodes = self._get_all_nodes()

        if element_types:
            all_nodes = [node for node in all_nodes
                        if any(isinstance(node, t) for t in element_types)]

        return [node for node in all_nodes if predicate(node)]

    # Statistics and metadata
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the loaded codebase."""
        stats = self.source_manager.get_statistics()

        # Add element counts
        contracts = self.source_manager.get_contracts()
        total_functions = sum(len(c.functions) for c in contracts)
        total_modifiers = sum(len(c.modifiers) for c in contracts)
        total_events = sum(len(c.events) for c in contracts)
        total_variables = sum(len(c.variables) for c in contracts)

        stats.update({
            "total_functions": total_functions,
            "total_modifiers": total_modifiers,
            "total_events": total_events,
            "total_state_variables": total_variables,
            "contracts_by_type": self._get_contract_type_counts()
        })

        return stats

    def get_contract_names(self) -> List[str]:
        """Get names of all loaded contracts."""
        return [contract.name for contract in self.source_manager.get_contracts()]

    # Internal helper methods
    def _get_all_functions(self, contract_name: Optional[str] = None) -> List[FunctionDeclaration]:
        """Get all functions, optionally filtered by contract."""
        functions = []
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if contract_name is None or contract.name == contract_name:
                functions.extend(contract.functions)

        return functions

    def _get_all_variables(self, contract_name: Optional[str] = None,
                          is_state_variable: Optional[bool] = None) -> List[VariableDeclaration]:
        """Get all variables, optionally filtered by contract and type."""
        variables = []
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if contract_name is None or contract.name == contract_name:
                contract_vars = contract.variables
                if is_state_variable is not None:
                    contract_vars = [v for v in contract_vars
                                   if v.is_state_variable() == is_state_variable]
                variables.extend(contract_vars)

        return variables

    def _get_all_modifiers(self, contract_name: Optional[str] = None) -> List[ModifierDeclaration]:
        """Get all modifiers, optionally filtered by contract."""
        modifiers = []
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if contract_name is None or contract.name == contract_name:
                modifiers.extend(contract.modifiers)

        return modifiers

    def _get_all_events(self, contract_name: Optional[str] = None) -> List[EventDeclaration]:
        """Get all events, optionally filtered by contract."""
        events = []
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if contract_name is None or contract.name == contract_name:
                events.extend(contract.events)

        return events

    def _get_all_nodes(self) -> List[ASTNode]:
        """Get all AST nodes from all loaded files."""
        nodes = []
        for source_file in self.source_manager.get_all_files():
            if source_file.ast:
                nodes.extend(source_file.ast)
        return nodes

    def _filter_contracts(self, contracts: List[ContractDeclaration],
                         name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                         inheritance: Optional[Union[str, List[str]]] = None,
                         kind: Optional[str] = None,
                         **filters: Any) -> List[ContractDeclaration]:
        """Filter contracts based on criteria."""
        result = contracts

        if name_patterns:
            result = [c for c in result
                     if self.pattern_matcher.matches_name_pattern(c.name, name_patterns)]

        if inheritance:
            inheritance_list = [inheritance] if isinstance(inheritance, str) else inheritance
            result = [c for c in result
                     if any(base in c.inheritance for base in inheritance_list)]

        if kind:
            result = [c for c in result if c.kind == kind]

        return result

    def _filter_functions(self, functions: List[FunctionDeclaration],
                         name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                         visibility: Optional[Union[Visibility, List[Visibility]]] = None,
                         modifiers: Optional[Union[str, List[str]]] = None,
                         state_mutability: Optional[Union[StateMutability, List[StateMutability]]] = None,
                         **filters: Any) -> List[FunctionDeclaration]:
        """Filter functions based on criteria."""
        result = functions

        if name_patterns:
            result = [f for f in result
                     if self.pattern_matcher.matches_name_pattern(f.name, name_patterns)]

        if visibility:
            visibility_list = [visibility] if isinstance(visibility, Visibility) else visibility
            result = [f for f in result if f.visibility in visibility_list]

        if state_mutability:
            mutability_list = ([state_mutability] if isinstance(state_mutability, StateMutability)
                             else state_mutability)
            result = [f for f in result if f.state_mutability in mutability_list]

        if modifiers:
            modifier_list = [modifiers] if isinstance(modifiers, str) else modifiers
            result = [f for f in result
                     if any(mod in f.modifiers for mod in modifier_list)]

        return result

    def _filter_variables(self, variables: List[VariableDeclaration],
                         name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                         type_patterns: Optional[Union[str, List[str], Pattern]] = None,
                         visibility: Optional[Union[Visibility, List[Visibility]]] = None,
                         **filters: Any) -> List[VariableDeclaration]:
        """Filter variables based on criteria."""
        result = variables

        if name_patterns:
            result = [v for v in result
                     if self.pattern_matcher.matches_name_pattern(v.name, name_patterns)]

        if type_patterns:
            result = [v for v in result
                     if self.pattern_matcher.matches_name_pattern(v.type_name, type_patterns)]

        if visibility:
            visibility_list = [visibility] if isinstance(visibility, Visibility) else visibility
            result = [v for v in result
                     if v.visibility and v.visibility in visibility_list]

        return result

    def _filter_modifiers(self, modifiers: List[ModifierDeclaration],
                         name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                         **filters: Any) -> List[ModifierDeclaration]:
        """Filter modifiers based on criteria."""
        result = modifiers

        if name_patterns:
            result = [m for m in result
                     if self.pattern_matcher.matches_name_pattern(m.name, name_patterns)]

        return result

    def _filter_events(self, events: List[EventDeclaration],
                      name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                      **filters: Any) -> List[EventDeclaration]:
        """Filter events based on criteria."""
        result = events

        if name_patterns:
            result = [e for e in result
                     if self.pattern_matcher.matches_name_pattern(e.name, name_patterns)]

        return result

    def _get_contract_type_counts(self) -> Dict[str, int]:
        """Get counts of contracts by type."""
        contracts = self.source_manager.get_contracts()
        counts = {"contract": 0, "interface": 0, "library": 0, "abstract": 0}

        for contract in contracts:
            if contract.kind in counts:
                counts[contract.kind] += 1
            else:
                counts["contract"] += 1  # Default to contract

        return counts

    # Additional helper methods for new finders
    def _get_all_structs(self, contract_name: Optional[str] = None) -> List[StructDeclaration]:
        """Get all structs, optionally filtered by contract."""
        structs = []
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if contract_name is None or contract.name == contract_name:
                structs.extend(contract.structs)

        return structs

    def _get_all_enums(self, contract_name: Optional[str] = None) -> List[EnumDeclaration]:
        """Get all enums, optionally filtered by contract."""
        enums = []
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if contract_name is None or contract.name == contract_name:
                enums.extend(contract.enums)

        return enums

    def _get_all_errors(self, contract_name: Optional[str] = None) -> List[ErrorDeclaration]:
        """Get all errors, optionally filtered by contract."""
        errors = []
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if contract_name is None or contract.name == contract_name:
                errors.extend(contract.errors)

        return errors

    def _get_all_statements(self, contract_name: Optional[str] = None,
                           function_name: Optional[str] = None) -> List[Statement]:
        """Get all statements, optionally filtered by contract and function."""
        statements = []
        functions = self._get_all_functions(contract_name)

        for function in functions:
            if function_name is None or function.name == function_name:
                if function.body:
                    statements.extend(self._extract_statements_from_block(function.body))

        return statements

    def _get_all_expressions(self, contract_name: Optional[str] = None,
                            function_name: Optional[str] = None) -> List[Expression]:
        """Get all expressions, optionally filtered by contract and function."""
        expressions = []
        statements = self._get_all_statements(contract_name, function_name)

        for statement in statements:
            # Include expression statements as expressions too (Fix #1)
            if hasattr(statement, 'node_type') and statement.node_type.value == 'expression_statement':
                if hasattr(statement, 'expression') and statement.expression:
                    expressions.append(statement.expression)

            expressions.extend(self._extract_expressions_from_statement(statement))

        return expressions

    def _extract_statements_from_block(self, block) -> List[Statement]:
        """Extract all statements from a block recursively."""
        statements = []
        if hasattr(block, 'statements'):
            for stmt in block.statements:
                statements.append(stmt)
                # Recursively extract from nested blocks
                if hasattr(stmt, 'body') and stmt.body:
                    statements.extend(self._extract_statements_from_block(stmt.body))
        return statements

    def _extract_expressions_from_statement(self, statement: Statement) -> List[Expression]:
        """Extract all expressions from a statement by traversing the already-built AST."""
        expressions = []

        # Extract expressions from ExpressionStatement
        if hasattr(statement, 'expression') and statement.expression:
            expressions.append(statement.expression)

        # Recursively traverse child nodes to find expressions
        expressions.extend(self._extract_expressions_from_ast_node(statement))

        return expressions

    def _extract_expressions_from_ast_node(self, node: ASTNode) -> List[Expression]:
        """Extract expressions from an AST node by traversing the already-built AST."""
        expressions = []

        # If this node is an expression, add it
        if isinstance(node, Expression):
            expressions.append(node)

        # Include nested expressions from statements
        if hasattr(node, '_nested_expressions'):
            expressions.extend(node._nested_expressions)

        # Recursively traverse child nodes
        for child in node.get_children():
            expressions.extend(self._extract_expressions_from_ast_node(child))

        return expressions

    # Filter methods for new finders
    def _filter_structs(self, structs: List[StructDeclaration],
                       name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                       **filters: Any) -> List[StructDeclaration]:
        """Filter structs based on criteria."""
        result = structs

        if name_patterns:
            result = [s for s in result
                     if self.pattern_matcher.matches_name_pattern(s.name, name_patterns)]

        return result

    def _filter_enums(self, enums: List[EnumDeclaration],
                     name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                     **filters: Any) -> List[EnumDeclaration]:
        """Filter enums based on criteria."""
        result = enums

        if name_patterns:
            result = [e for e in result
                     if self.pattern_matcher.matches_name_pattern(e.name, name_patterns)]

        return result

    def _filter_errors(self, errors: List[ErrorDeclaration],
                      name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                      **filters: Any) -> List[ErrorDeclaration]:
        """Filter errors based on criteria."""
        result = errors

        if name_patterns:
            result = [e for e in result
                     if self.pattern_matcher.matches_name_pattern(e.name, name_patterns)]

        return result

    def _filter_statements(self, statements: List[Statement],
                          statement_types: Optional[Union[str, List[str]]] = None,
                          **filters: Any) -> List[Statement]:
        """Filter statements based on criteria."""
        result = statements

        if statement_types:
            type_list = [statement_types] if isinstance(statement_types, str) else statement_types
            result = [s for s in result
                     if hasattr(s, 'node_type') and s.node_type.value in type_list]

        return result

    def _filter_expressions(self, expressions: List[Expression],
                           expression_types: Optional[Union[str, List[str]]] = None,
                           **filters: Any) -> List[Expression]:
        """Filter expressions based on criteria."""
        result = expressions

        if expression_types:
            type_list = [expression_types] if isinstance(expression_types, str) else expression_types
            result = [e for e in result
                     if hasattr(e, 'node_type') and e.node_type.value in type_list]

        return result

    def _filter_calls(self, calls: List,
                     target_patterns: Optional[Union[str, List[str], Pattern]] = None,
                     **filters: Any) -> List:
        """Filter call expressions based on criteria."""
        result = calls

        if target_patterns:
            result = [c for c in result
                     if hasattr(c, 'function') and hasattr(c.function, 'name') and
                     self.pattern_matcher.matches_name_pattern(c.function.name, target_patterns)]

        return result

    def _filter_literals(self, literals: List,
                        literal_types: Optional[Union[str, List[str]]] = None,
                        **filters: Any) -> List:
        """Filter literals based on criteria."""
        result = literals

        if literal_types:
            type_list = [literal_types] if isinstance(literal_types, str) else literal_types
            result = [l for l in result
                     if hasattr(l, 'literal_type') and l.literal_type in type_list]

        return result

    def _filter_identifiers(self, identifiers: List,
                           name_patterns: Optional[Union[str, List[str], Pattern]] = None,
                           **filters: Any) -> List:
        """Filter identifiers based on criteria."""
        result = identifiers

        if name_patterns:
            result = [i for i in result
                     if hasattr(i, 'name') and
                     self.pattern_matcher.matches_name_pattern(i.name, name_patterns)]

        return result

    def _expressions_match(self, expr1, expr2) -> bool:
        """Check if two expressions are equivalent."""
        # Simple heuristic: check if they have the same source location or text
        if hasattr(expr1, 'source_location') and hasattr(expr2, 'source_location'):
            return (expr1.source_location.start_byte == expr2.source_location.start_byte and
                    expr1.source_location.end_byte == expr2.source_location.end_byte)
        return False

    # ===== UTILITY FUNCTIONS =====

    def intersect(self, *element_sets) -> List[ASTNode]:
        """
        Find intersection of multiple element sets.
        
        Args:
            *element_sets: Variable number of element lists/sets to intersect
            
        Returns:
            List of elements present in all sets
        """
        if not element_sets:
            return []

        # Convert all sets to lists of elements with IDs for comparison
        element_lists = []
        for element_set in element_sets:
            elements = []
            if hasattr(element_set, 'list'):
                # Collection object
                elements = element_set.list()
            elif isinstance(element_set, (list, tuple)):
                elements = list(element_set)
            else:
                elements = [element_set]
            element_lists.append(elements)

        if not element_lists:
            return []

        # Find intersection by comparing element IDs
        result = []
        first_set_ids = {id(elem): elem for elem in element_lists[0]}

        for element_id, element in first_set_ids.items():
            # Check if this element is in all other sets
            in_all_sets = True
            for other_list in element_lists[1:]:
                other_ids = {id(elem) for elem in other_list}
                if element_id not in other_ids:
                    in_all_sets = False
                    break

            if in_all_sets:
                result.append(element)

        return result

    def union(self, *element_sets) -> List[ASTNode]:
        """
        Find union of multiple element sets.
        
        Args:
            *element_sets: Variable number of element lists/sets to union
            
        Returns:
            List of elements present in any set (no duplicates)
        """
        if not element_sets:
            return []

        result_list = []
        seen_ids = set()

        for element_set in element_sets:
            elements = []
            if hasattr(element_set, 'list'):
                # Collection object
                elements = element_set.list()
            elif isinstance(element_set, (list, tuple)):
                elements = list(element_set)
            else:
                elements = [element_set]

            # Add elements that haven't been seen yet (using id for uniqueness)
            for element in elements:
                element_id = id(element)
                if element_id not in seen_ids:
                    seen_ids.add(element_id)
                    result_list.append(element)

        return result_list

    def difference(self, base_set, subtract_set) -> List[ASTNode]:
        """
        Find difference between two element sets.
        
        Args:
            base_set: The base set of elements
            subtract_set: Elements to subtract from base set
            
        Returns:
            List of elements in base_set but not in subtract_set
        """
        # Convert to lists
        base_elements = []
        if hasattr(base_set, 'list'):
            base_elements = base_set.list()
        elif isinstance(base_set, (list, tuple)):
            base_elements = list(base_set)
        else:
            base_elements = [base_set]

        subtract_elements = []
        if hasattr(subtract_set, 'list'):
            subtract_elements = subtract_set.list()
        elif isinstance(subtract_set, (list, tuple)):
            subtract_elements = list(subtract_set)
        else:
            subtract_elements = [subtract_set]

        # Create set of IDs to subtract
        subtract_ids = {id(elem) for elem in subtract_elements}

        # Return elements from base that are not in subtract
        result = []
        for elem in base_elements:
            if id(elem) not in subtract_ids:
                result.append(elem)

        return result

    def filter_elements(self, elements, **filter_conditions) -> List[ASTNode]:
        """
        Filter elements based on arbitrary conditions.
        
        Args:
            elements: List or collection of elements to filter
            **filter_conditions: Filter conditions as key-value pairs
            
        Returns:
            List of elements matching all filter conditions
        """
        # Convert to list if collection
        if hasattr(elements, 'list'):
            element_list = elements.list()
        elif isinstance(elements, (list, tuple)):
            element_list = list(elements)
        else:
            element_list = [elements]

        filtered = element_list
        for condition, value in filter_conditions.items():
            if callable(value):
                # Predicate function
                filtered = [e for e in filtered if value(e)]
            else:
                # Attribute matching
                filtered = [e for e in filtered if
                           hasattr(e, condition) and getattr(e, condition) == value]

        return filtered

    def group_elements(self, elements, group_by_attribute: str) -> Dict[str, List[ASTNode]]:
        """
        Group elements by a specific attribute.
        
        Args:
            elements: List or collection of elements to group
            group_by_attribute: Attribute name to group by
            
        Returns:
            Dictionary mapping attribute values to lists of elements
        """
        # Convert to list if collection
        if hasattr(elements, 'list'):
            element_list = elements.list()
        elif isinstance(elements, (list, tuple)):
            element_list = list(elements)
        else:
            element_list = [elements]

        groups = {}
        for element in element_list:
            if hasattr(element, group_by_attribute):
                key = str(getattr(element, group_by_attribute))
                if key not in groups:
                    groups[key] = []
                groups[key].append(element)
            else:
                # Elements without the attribute go to 'unknown' group
                if 'unknown' not in groups:
                    groups['unknown'] = []
                groups['unknown'].append(element)

        return groups

    def sort_elements(self, elements, sort_by_attribute: str, reverse: bool = False) -> List[ASTNode]:
        """
        Sort elements by a specific attribute.
        
        Args:
            elements: List or collection of elements to sort
            sort_by_attribute: Attribute name to sort by
            reverse: Whether to sort in descending order
            
        Returns:
            Sorted list of elements
        """
        # Convert to list if collection
        if hasattr(elements, 'list'):
            element_list = elements.list()
        elif isinstance(elements, (list, tuple)):
            element_list = list(elements)
        else:
            element_list = [elements]

        def sort_key(element):
            if hasattr(element, sort_by_attribute):
                return getattr(element, sort_by_attribute)
            else:
                return ""  # Elements without attribute sort to beginning/end

        return sorted(element_list, key=sort_key, reverse=reverse)

    # ===== PATTERN MATCHING AND COMPOSITE QUERIES =====

    def find_by_ast_pattern(self, pattern, **filters: Any) -> List[ASTNode]:
        """
        Find nodes matching an AST pattern.
        
        Args:
            pattern: AST pattern to match (simplified implementation)
            **filters: Additional filter conditions
            
        Returns:
            List of matching AST nodes
        """
        # Simplified implementation - match by node type
        all_nodes = self._get_all_nodes()
        matching_nodes = []

        # If pattern is a string, match by node type
        if isinstance(pattern, str):
            for node in all_nodes:
                if hasattr(node, 'node_type') and node.node_type.value == pattern:
                    matching_nodes.append(node)

        return matching_nodes

    def find_elements_matching_all(self, conditions: List[Callable[[ASTNode], bool]], **filters: Any) -> List[ASTNode]:
        """
        Find elements that match ALL of the provided conditions.
        
        Args:
            conditions: List of predicate functions that elements must satisfy
            **filters: Additional filter conditions
            
        Returns:
            List of elements matching all conditions
        """
        all_nodes = self._get_all_nodes()
        matching_nodes = []

        for node in all_nodes:
            if all(condition(node) for condition in conditions):
                matching_nodes.append(node)

        return matching_nodes

    def find_elements_matching_any(self, conditions: List[Callable[[ASTNode], bool]], **filters: Any) -> List[ASTNode]:
        """
        Find elements that match ANY of the provided conditions.
        
        Args:
            conditions: List of predicate functions that elements may satisfy
            **filters: Additional filter conditions
            
        Returns:
            List of elements matching at least one condition
        """
        all_nodes = self._get_all_nodes()
        matching_nodes = []

        for node in all_nodes:
            if any(condition(node) for condition in conditions):
                matching_nodes.append(node)

        return matching_nodes

    # ===== REFERENCE TRACKING METHODS =====

    def find_definitions_of(self, name: str, scope=None, **filters: Any) -> List[ASTNode]:
        """
        Find definitions of a symbol by name.
        
        Args:
            name: Symbol name to find definitions for
            scope: Scope to search in (optional)
            **filters: Additional filter conditions
            
        Returns:
            List of definition nodes
        """
        definitions = []

        # Find variable declarations with matching name
        variables = self.find_variables(name_patterns=name)
        definitions.extend(variables)

        # Find function declarations with matching name
        functions = self.find_functions(name_patterns=name)
        definitions.extend(functions)

        # Find contract declarations with matching name
        contracts = self.find_contracts(name_patterns=name)
        definitions.extend(contracts)

        # Find modifier declarations with matching name
        modifiers = self.find_modifiers(name_patterns=name)
        definitions.extend(modifiers)

        # Find event declarations with matching name
        events = self.find_events(name_patterns=name)
        definitions.extend(events)

        # Find struct declarations with matching name
        structs = self.find_structs(name_patterns=name)
        definitions.extend(structs)

        # Find enum declarations with matching name
        enums = self.find_enums(name_patterns=name)
        definitions.extend(enums)

        # Find error declarations with matching name
        errors = self.find_errors(name_patterns=name)
        definitions.extend(errors)

        return definitions

    def find_usages_of(self, element: Union[str, ASTNode], usage_types=None, **filters: Any) -> List[ASTNode]:
        """
        Find all usages of an element.
        
        Args:
            element: Element to find usages of (name or AST node)
            usage_types: Types of usages to find (optional)
            **filters: Additional filter conditions
            
        Returns:
            List of usage nodes
        """
        # This is similar to find_references_to but focuses on usage rather than references
        return self.find_references_to(element, **filters)

    def find_assignments_to(self, target: Union[str, ASTNode], **filters: Any) -> List[ASTNode]:
        """
        Find assignments to a target variable.
        
        Args:
            target: Target variable (name or AST node)
            **filters: Additional filter conditions
            
        Returns:
            List of assignment nodes
        """
        target_name = target if isinstance(target, str) else getattr(target, 'name', str(target))

        # Find assignment statements that target this variable
        assignments = self.find_assignments()

        # Filter for assignments to our target (simplified implementation)
        matching_assignments = []
        for assignment in assignments:
            # This is a simplified check - would need more sophisticated AST analysis
            if hasattr(assignment, 'get_source_code') and target_name in assignment.get_source_code():
                matching_assignments.append(assignment)

        return matching_assignments

    def find_reads_of(self, target: Union[str, ASTNode], **filters: Any) -> List[ASTNode]:
        """
        Find read operations of a target variable.
        
        Args:
            target: Target variable (name or AST node)
            **filters: Additional filter conditions
            
        Returns:
            List of read operation nodes
        """
        target_name = target if isinstance(target, str) else getattr(target, 'name', str(target))

        # Find identifier references that are reads (not assignments)
        identifiers = self.find_identifiers(name_patterns=target_name)

        # This is a simplified implementation - in practice would need to distinguish
        # reads from writes by analyzing the AST context
        return identifiers

    def find_modifications_of(self, target: Union[str, ASTNode], **filters: Any) -> List[ASTNode]:
        """
        Find modifications of a target variable.
        
        Args:
            target: Target variable (name or AST node)
            **filters: Additional filter conditions
            
        Returns:
            List of modification nodes
        """
        # Modifications include assignments and other write operations
        assignments = self.find_assignments_to(target, **filters)
        return assignments

    # ===== MISSING STATEMENT AND EXPRESSION FINDERS =====

    def find_loops(self, loop_types: Optional[Union[str, List[str]]] = None, **filters: Any) -> List[Statement]:
        """Find loop statements (for, while, do-while)."""
        if loop_types is None:
            loop_types = ["for_statement", "while_statement", "do_while_statement"]
        elif isinstance(loop_types, str):
            loop_types = [loop_types]

        return self.find_statements(statement_types=loop_types, **filters)

    def find_conditionals(self, **filters: Any) -> List[Statement]:
        """Find conditional statements (if, if-else)."""
        return self.find_statements(statement_types=["if_statement"], **filters)

    def find_assignments(self, **filters: Any) -> List[Statement]:
        """Find assignment statements."""
        return self.find_statements(statement_types=["assignment"], **filters)

    def find_returns(self, **filters: Any) -> List[Statement]:
        """Find return statements."""
        return self.find_statements(statement_types=["return_statement"], **filters)

    def find_requires(self, **filters: Any) -> List[Statement]:
        """Find require statements."""
        return self.find_statements(statement_types=["require_statement"], **filters)

    def find_emits(self, **filters: Any) -> List[Statement]:
        """Find emit statements."""
        return self.find_statements(statement_types=["emit_statement"], **filters)

    def find_binary_operations(self, **filters: Any) -> List[Expression]:
        """Find binary operation expressions."""
        return self.find_expressions(expression_types=["binary_expression"], **filters)

    def find_unary_operations(self, **filters: Any) -> List[Expression]:
        """Find unary operation expressions."""
        return self.find_expressions(expression_types=["unary_expression"], **filters)

    # ===== CONTEXT AND CONTAINMENT METHODS =====

    def find_containing_elements(self, element: ASTNode, container_types=None, **filters: Any) -> List[ASTNode]:
        """
        Find elements that contain the given element.
        
        Args:
            element: Element to find containers for
            container_types: Types of containers to find
            **filters: Additional filter conditions
            
        Returns:
            List of containing elements
        """
        # Simplified implementation - find by source location containment
        all_nodes = self._get_all_nodes()
        containing_elements = []

        if not hasattr(element, 'source_location'):
            return containing_elements

        element_start = element.source_location.start_byte
        element_end = element.source_location.end_byte

        for node in all_nodes:
            if (hasattr(node, 'source_location') and node != element and
                node.source_location.start_byte <= element_start and
                node.source_location.end_byte >= element_end):
                containing_elements.append(node)

        return containing_elements

    def find_contained_elements(self, container: ASTNode, element_types=None, **filters: Any) -> List[ASTNode]:
        """
        Find elements contained within the given container.
        
        Args:
            container: Container element to search within
            element_types: Types of elements to find
            **filters: Additional filter conditions
            
        Returns:
            List of contained elements
        """
        # Simplified implementation - find by source location containment
        all_nodes = self._get_all_nodes()
        contained_elements = []

        if not hasattr(container, 'source_location'):
            return contained_elements

        container_start = container.source_location.start_byte
        container_end = container.source_location.end_byte

        for node in all_nodes:
            if (hasattr(node, 'source_location') and node != container and
                node.source_location.start_byte >= container_start and
                node.source_location.end_byte <= container_end):
                contained_elements.append(node)

        return contained_elements

    def find_sibling_elements(self, element: ASTNode, sibling_types=None, **filters: Any) -> List[ASTNode]:
        """
        Find sibling elements of the given element.
        
        Args:
            element: Element to find siblings for
            sibling_types: Types of siblings to find
            **filters: Additional filter conditions
            
        Returns:
            List of sibling elements
        """
        # Find containing element first
        containers = self.find_containing_elements(element)
        if not containers:
            return []

        # Get the immediate parent (smallest container)
        immediate_parent = min(containers, key=lambda c:
                             c.source_location.end_byte - c.source_location.start_byte)

        # Find all elements in the same parent
        siblings = self.find_contained_elements(immediate_parent)

        # Remove the element itself
        return [s for s in siblings if s != element]

    def get_surrounding_context(self, element: ASTNode, context_radius: int = 1, **filters: Any) -> Dict[str, Any]:
        """
        Get surrounding context for an element.
        
        Args:
            element: Element to get context for
            context_radius: How much context to include
            **filters: Additional filter conditions
            
        Returns:
            Dictionary with context information
        """
        context = {
            'element': element,
            'containers': self.find_containing_elements(element),
            'contained': self.find_contained_elements(element),
            'siblings': self.find_sibling_elements(element)
        }

        return context

    # ===== ANALYSIS AND EXTRACTION METHODS =====

    def extract_properties(self, elements: List[ASTNode], property_names: List[str]) -> List[Dict]:
        """
        Extract specified properties from elements.
        
        Args:
            elements: Elements to extract properties from
            property_names: Names of properties to extract
            
        Returns:
            List of dictionaries with extracted properties
        """
        results = []

        for element in elements:
            properties = {}
            for prop_name in property_names:
                if hasattr(element, prop_name):
                    properties[prop_name] = getattr(element, prop_name)
                else:
                    properties[prop_name] = None
            results.append(properties)

        return results

    def extract_conditions(self, conditional_elements: List[ASTNode]) -> List[Dict]:
        """
        Extract conditions from conditional elements.
        
        Args:
            conditional_elements: Conditional statements to analyze
            
        Returns:
            List of condition information
        """
        conditions = []

        for element in conditional_elements:
            condition_info = {
                'element': element,
                'type': getattr(element, 'node_type', None),
                'source': element.get_source_code() if hasattr(element, 'get_source_code') else None
            }
            conditions.append(condition_info)

        return conditions

    def get_metrics(self, elements: List[ASTNode], metric_types=None) -> Dict[str, Any]:
        """
        Get metrics for a collection of elements.
        
        Args:
            elements: Elements to analyze
            metric_types: Types of metrics to calculate
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'total_count': len(elements),
            'types': {},
            'complexity': 0
        }

        # Count by type
        for element in elements:
            element_type = type(element).__name__
            if element_type not in metrics['types']:
                metrics['types'][element_type] = 0
            metrics['types'][element_type] += 1

        # Basic complexity metric (number of nested elements)
        for element in elements:
            if hasattr(element, 'body') and element.body:
                metrics['complexity'] += 1

        return metrics

    def analyze_complexity(self, elements: List[ASTNode], metrics=None) -> Dict[str, Any]:
        """
        Analyze complexity of elements.
        
        Args:
            elements: Elements to analyze
            metrics: Specific metrics to calculate
            
        Returns:
            Complexity analysis results
        """
        analysis = {
            'cyclomatic_complexity': 0,
            'nesting_depth': 0,
            'total_statements': 0,
            'elements_analyzed': len(elements)
        }

        for element in elements:
            # Basic complexity metrics
            if hasattr(element, 'body') and element.body:
                # Count nested statements for complexity
                nested = self.find_contained_elements(element)
                analysis['total_statements'] += len(nested)
                analysis['cyclomatic_complexity'] += max(1, len(nested) // 10)

        return analysis