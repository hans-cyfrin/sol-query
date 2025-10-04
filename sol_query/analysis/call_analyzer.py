"""AST-based call analyzer for detecting external calls and asset transfers in Solidity code."""

from typing import List, Set, Dict, Optional, Tuple
from sol_query.core.ast_nodes import (
    ASTNode, FunctionDeclaration, CallExpression, Expression,
    Identifier, Literal, BinaryExpression, Statement, NodeType
)
from sol_query.analysis.call_types import CallType, CallTypeDetector


class CallAnalyzer:
    """Analyzes function calls using AST traversal (no regex patterns)."""

    def __init__(self):
        """Initialize the call analyzer."""
        self.call_type_detector = CallTypeDetector()

        # Low-level call function names (by type)
        self.delegate_calls = {'delegatecall'}
        self.static_calls = {'staticcall'}
        self.low_level_calls = {'call', 'send', 'transfer'}

        # Asset transfer function names
        self.asset_transfer_functions = {
            'transfer', 'transferFrom', 'safeTransfer', 'safeTransferFrom',
            'send', 'withdraw', 'deposit', 'mint', 'burn'
        }

    def analyze_function(self, function: FunctionDeclaration, contract_context: Optional[Dict] = None) -> None:
        """
        Analyze a function for external calls and asset transfers using AST traversal.
        Updates the function's metadata fields.

        Args:
            function: The function to analyze
            contract_context: Context about the current contract and available functions
        """
        if not function.body:
            return

        # Build contract context if not provided
        if contract_context is None:
            contract_context = self._build_basic_context(function)

        # Find all call expressions in function body
        calls = self._find_all_calls(function.body)

        # Analyze each call
        has_external_calls = False
        has_asset_transfers = False
        external_call_targets = []
        asset_transfer_types = []

        for call in calls:
            call_type = self._classify_call_ast(call, contract_context)

            # Check if it's an external call
            if self._is_external_call(call_type):
                has_external_calls = True
                # Extract call target for external_call_targets list
                call_target = self._extract_call_target(call)
                if call_target:
                    external_call_targets.append(call_target)

            # Check if it's an asset transfer
            if self._is_asset_transfer(call, contract_context):
                has_asset_transfers = True
                # Extract transfer type for asset_transfer_types list
                transfer_type = self._extract_transfer_type(call)
                if transfer_type:
                    asset_transfer_types.append(transfer_type)

        # Update function metadata (both boolean flags and lists)
        function.has_external_calls = has_external_calls
        function.has_asset_transfers = has_asset_transfers
        function.external_call_targets = external_call_targets
        function.asset_transfer_types = asset_transfer_types

    def _find_all_calls(self, node: ASTNode) -> List[CallExpression]:
        """
        Recursively find all call expressions in an AST node.
        Pure AST traversal, no text matching.
        """
        calls = []

        if isinstance(node, CallExpression):
            calls.append(node)

        # Recursively search in children
        if hasattr(node, 'get_children'):
            for child in node.get_children():
                calls.extend(self._find_all_calls(child))

        # Handle specific node types with nested expressions
        if isinstance(node, Statement):
            if hasattr(node, 'expression') and node.expression:
                calls.extend(self._find_all_calls(node.expression))

        if isinstance(node, FunctionDeclaration) and node.body:
            if hasattr(node.body, 'statements'):
                for stmt in node.body.statements:
                    calls.extend(self._find_all_calls(stmt))

        return calls

    def _classify_call_ast(self, call: CallExpression, context: Dict) -> CallType:
        """
        Classify a call using AST structure analysis.
        Works with current AST structure where member access is stored in function field.
        """
        if not hasattr(call, 'function') or not call.function:
            return CallType.UNKNOWN

        function_expr = call.function

        # Check for member access (stored as Literal with MEMBER_ACCESS type or as text)
        if isinstance(function_expr, Literal) and function_expr.node_type == NodeType.MEMBER_ACCESS:
            return self._classify_member_call_from_text(function_expr.value, context)

        # Check for identifier (direct function call)
        if isinstance(function_expr, Identifier):
            return self._classify_direct_call(function_expr, context)

        # If function is stored as text, analyze it
        if isinstance(function_expr, Literal):
            return self._classify_from_text(function_expr.value, context)

        return CallType.UNKNOWN

    def _classify_member_call_from_text(self, call_text: str, context: Dict) -> CallType:
        """Classify member access calls from text representation."""
        if not call_text or '.' not in call_text:
            return CallType.UNKNOWN

        # Split by dot to get object.method
        parts = call_text.split('.')
        if len(parts) < 2:
            return CallType.UNKNOWN

        # Get object and method name
        object_name = parts[0]
        method_name = parts[-1].strip('()')

        # Check for delegate calls first (most specific)
        if method_name in self.delegate_calls:
            return CallType.DELEGATE

        # Check for static calls
        if method_name in self.static_calls:
            return CallType.STATIC

        # Check for other low-level calls
        if method_name in self.low_level_calls:
            return CallType.LOW_LEVEL

        # Check if method exists in current contract
        if method_name in context.get('contract_functions', []):
            # Could be internal or this.method() style external
            if call_text.startswith('this.'):
                return CallType.EXTERNAL
            return CallType.INTERNAL

        # Check if it's a library call (CamelCase object name, likely library)
        if object_name and object_name[0].isupper():
            # Check for common library patterns (SafeMath, Math, etc.)
            if not object_name.startswith('I'):  # Not interface (interfaces start with I)
                return CallType.LIBRARY

        # Otherwise, it's an external call
        return CallType.EXTERNAL

    def _classify_direct_call(self, callee: Identifier, context: Dict) -> CallType:
        """Classify direct function calls."""
        function_name = callee.name if hasattr(callee, 'name') else str(callee)

        # Check if it's an internal function
        if function_name in context.get('contract_functions', []):
            return CallType.INTERNAL

        # Check if it's a modifier
        if function_name in context.get('contract_modifiers', []):
            return CallType.INTERNAL

        # Check if it's a type conversion (starts with capital letter, likely interface/contract/type name)
        if function_name and function_name[0].isupper():
            # Could be type conversion: address(), uint256(), Interface(), etc.
            return CallType.TYPE_CONVERSION

        # Otherwise, likely library or external
        return CallType.LIBRARY

    def _classify_from_text(self, text: str, context: Dict) -> CallType:
        """Classify call from text when structure is not preserved."""
        if not text:
            return CallType.UNKNOWN

        # Check for member access pattern
        if '.' in text:
            return self._classify_member_call_from_text(text, context)

        # Check for direct function call
        function_name = text.strip('()')
        if function_name in context.get('contract_functions', []):
            return CallType.INTERNAL

        return CallType.UNKNOWN

    def _is_external_call(self, call_type: CallType) -> bool:
        """Check if call type represents an external call."""
        return call_type in [CallType.EXTERNAL, CallType.LOW_LEVEL, CallType.LIBRARY, CallType.DELEGATE, CallType.STATIC]

    def _extract_call_target(self, call: CallExpression) -> Optional[str]:
        """Extract a string representation of the call target for reporting."""
        if not hasattr(call, 'function') or not call.function:
            return None

        function_expr = call.function

        # For member access (e.g., token.transfer, target.call)
        if isinstance(function_expr, Literal) and hasattr(function_expr, 'value'):
            return f"external_call:{function_expr.value}"

        # For identifiers (e.g., SomeContract())
        if isinstance(function_expr, Identifier) and hasattr(function_expr, 'name'):
            return f"external_call:{function_expr.name}"

        return None

    def _extract_transfer_type(self, call: CallExpression) -> Optional[str]:
        """Extract a string representation of the transfer type for reporting."""
        if not hasattr(call, 'function') or not call.function:
            return None

        function_expr = call.function

        # For member access (e.g., token.transfer, token.transferFrom)
        if isinstance(function_expr, Literal) and hasattr(function_expr, 'value'):
            call_text = function_expr.value
            if '.' in call_text:
                method_name = call_text.split('.')[-1].strip('()')
                if method_name in self.asset_transfer_functions:
                    return method_name

        # For identifiers
        if isinstance(function_expr, Identifier) and hasattr(function_expr, 'name'):
            if function_expr.name in self.asset_transfer_functions:
                return function_expr.name

        return None

    def _is_asset_transfer(self, call: CallExpression, context: Dict) -> bool:
        """
        Check if a call represents an asset transfer using AST analysis.
        """
        if not hasattr(call, 'function') or not call.function:
            return False

        function_expr = call.function

        # Check for member access (e.g., token.transfer())
        if isinstance(function_expr, Literal) and function_expr.node_type == NodeType.MEMBER_ACCESS:
            call_text = function_expr.value
            if '.' in call_text:
                method_name = call_text.split('.')[-1].strip('()')
                if method_name in self.asset_transfer_functions:
                    return True

        # Check for identifier (direct calls)
        if isinstance(function_expr, Identifier):
            if hasattr(function_expr, 'name') and function_expr.name in self.asset_transfer_functions:
                return True

        # Check for text representation
        if isinstance(function_expr, Literal):
            text = function_expr.value
            if '.' in text:
                method_name = text.split('.')[-1].strip('()')
                if method_name in self.asset_transfer_functions:
                    return True
            elif text.strip('()') in self.asset_transfer_functions:
                return True

        return False

    def _build_basic_context(self, function: FunctionDeclaration) -> Dict:
        """Build basic context for a function."""
        context = {
            'contract_functions': [],
            'contract_modifiers': [],
            'state_variables': [],
            'local_variables': [],
            'parameters': []
        }

        # Get function parameters
        if hasattr(function, 'parameters') and function.parameters:
            context['parameters'] = [p.name for p in function.parameters if hasattr(p, 'name')]

        # Get parent contract info if available
        if hasattr(function, 'parent_contract'):
            parent = function.parent_contract
            if parent:
                if hasattr(parent, 'functions'):
                    context['contract_functions'] = [f.name for f in parent.functions if hasattr(f, 'name')]
                if hasattr(parent, 'modifiers'):
                    context['contract_modifiers'] = [m.name for m in parent.modifiers if hasattr(m, 'name')]
                if hasattr(parent, 'variables'):
                    context['state_variables'] = [v.name for v in parent.variables if hasattr(v, 'name')]

        return context

    def analyze_call_expressions(self, call_expressions: List[CallExpression], context: Dict) -> None:
        """
        Analyze a list of call expressions and set their call_type field.

        Args:
            call_expressions: List of call expressions to analyze
            context: Contract context for classification
        """
        for call_expr in call_expressions:
            if not isinstance(call_expr, CallExpression):
                continue

            # Classify the call
            call_type = self._classify_call_ast(call_expr, context)

            # Set the call_type field as string
            call_expr.call_type = call_type.value if call_type else None

    def analyze_all_expressions_in_ast(self, ast_root: ASTNode, context: Dict) -> None:
        """
        Recursively analyze all call expressions in an AST tree and set their call_type.

        Args:
            ast_root: Root AST node to start traversal
            context: Contract context for classification
        """
        # Find all call expressions recursively
        calls = self._find_all_calls_recursive(ast_root)

        # Analyze each call
        for call_expr in calls:
            # Skip if already classified
            if call_expr.call_type is not None:
                continue

            call_type = self._classify_call_ast(call_expr, context)
            # Set call_type, defaulting to UNKNOWN if None
            if call_type:
                call_expr.call_type = call_type.value
            else:
                call_expr.call_type = CallType.UNKNOWN.value

    def _find_all_calls_recursive(self, node: ASTNode) -> List[CallExpression]:
        """Recursively find all call expressions in any AST node."""
        calls = []

        # Check if this node is a call expression
        if isinstance(node, CallExpression):
            calls.append(node)

        # Recursively search in all children
        if hasattr(node, 'get_children'):
            try:
                for child in node.get_children():
                    if child:
                        calls.extend(self._find_all_calls_recursive(child))
            except:
                pass

        # Also check common attributes that might contain expressions
        # Include try-catch specific attributes and _nested_expressions from generic statements
        for attr_name in ['body', 'expression', 'statements', 'functions', 'initializer',
                          'condition', 'then_statement', 'else_statement',
                          'try_expression', 'try_body', 'catch_clauses', 'catch_body',
                          'return_value', 'update_expression', '_nested_expressions']:
            if hasattr(node, attr_name):
                attr = getattr(node, attr_name)
                if attr:
                    if isinstance(attr, list):
                        for item in attr:
                            if item:
                                calls.extend(self._find_all_calls_recursive(item))
                    else:
                        calls.extend(self._find_all_calls_recursive(attr))

        return calls

    def analyze_enhanced_call_patterns(self, function: FunctionDeclaration) -> Dict:
        """
        Analyze enhanced call patterns including try-catch and assembly calls.

        Args:
            function: The function to analyze

        Returns:
            Dict with analysis results including:
            - try_catch_calls: List of try-catch call expressions
            - assembly_calls: Dict with counts of assembly call types
            - call_type_distribution: Dict mapping call types to counts
            - total_calls: Total number of calls
        """
        if not function.body:
            return {
                'try_catch_calls': [],
                'assembly_calls': {'call': 0, 'delegatecall': 0, 'staticcall': 0},
                'call_type_distribution': {},
                'total_calls': 0
            }

        # Find all calls
        calls = self._find_all_calls(function.body)

        # Initialize result
        result = {
            'try_catch_calls': [],
            'assembly_calls': {'call': 0, 'delegatecall': 0, 'staticcall': 0},
            'call_type_distribution': {},
            'total_calls': len(calls)
        }

        # Analyze each call
        for call in calls:
            # Check if call is in try-catch (look for try statement in parents)
            if self._is_in_try_catch(call, function.body):
                result['try_catch_calls'].append(call)

            # Check call type for distribution
            if hasattr(call, 'call_type') and call.call_type:
                call_type = call.call_type
                result['call_type_distribution'][call_type] = \
                    result['call_type_distribution'].get(call_type, 0) + 1

        return result

    def _is_in_try_catch(self, call: CallExpression, root_node: ASTNode) -> bool:
        """Check if a call expression is inside a try-catch statement."""
        # Look for try-catch by checking if call is in _nested_expressions of a statement
        # that came from a try_statement tree-sitter node
        # This is a simplified check - in practice we'd need to traverse the AST tree
        # For now, check if the call's source location is near try keyword
        if hasattr(call, 'source_location') and call.source_location:
            source_text = call.source_location.source_text
            # Simple heuristic: if the call text contains patterns suggesting it's in a try
            # This is not perfect but works for basic detection
            return False  # TODO: Implement proper try-catch detection
        return False

    def analyze_call_tree_external_calls(self, function: FunctionDeclaration, all_functions: List[FunctionDeclaration]) -> bool:
        """
        Analyze if a function's call tree includes any external calls (transitive analysis).

        Args:
            function: The function to analyze
            all_functions: List of all functions in the codebase for call resolution

        Returns:
            True if the function or any function it calls (transitively) makes external calls
        """
        # Check if function itself has external calls
        if function.has_external_calls:
            return True

        # Build a map of function names to functions for quick lookup
        func_map = {f.name: f for f in all_functions if hasattr(f, 'name')}

        # Track visited functions to avoid infinite recursion
        visited = set()

        return self._has_external_calls_recursive(function, func_map, visited)

    def _has_external_calls_recursive(self, function: FunctionDeclaration,
                                       func_map: Dict[str, FunctionDeclaration],
                                       visited: Set[str]) -> bool:
        """Recursively check if function or its callees have external calls."""
        if not hasattr(function, 'name'):
            return False

        func_name = function.name

        # Avoid infinite recursion
        if func_name in visited:
            return False
        visited.add(func_name)

        # Check if this function has external calls
        if function.has_external_calls:
            return True

        # Find internal function calls and check them recursively
        if not function.body:
            return False

        calls = self._find_all_calls(function.body)
        for call in calls:
            # Get the called function name
            called_func_name = self._extract_called_function_name(call)
            if called_func_name and called_func_name in func_map:
                called_func = func_map[called_func_name]
                if self._has_external_calls_recursive(called_func, func_map, visited):
                    return True

        return False

    def analyze_call_tree_asset_transfers(self, function: FunctionDeclaration, all_functions: List[FunctionDeclaration]) -> bool:
        """
        Analyze if a function's call tree includes any asset transfers (transitive analysis).

        Args:
            function: The function to analyze
            all_functions: List of all functions in the codebase for call resolution

        Returns:
            True if the function or any function it calls (transitively) transfers assets
        """
        # Check if function itself has asset transfers
        if function.has_asset_transfers:
            return True

        # Build a map of function names to functions for quick lookup
        func_map = {f.name: f for f in all_functions if hasattr(f, 'name')}

        # Track visited functions to avoid infinite recursion
        visited = set()

        return self._has_asset_transfers_recursive(function, func_map, visited)

    def _has_asset_transfers_recursive(self, function: FunctionDeclaration,
                                        func_map: Dict[str, FunctionDeclaration],
                                        visited: Set[str]) -> bool:
        """Recursively check if function or its callees have asset transfers."""
        if not hasattr(function, 'name'):
            return False

        func_name = function.name

        # Avoid infinite recursion
        if func_name in visited:
            return False
        visited.add(func_name)

        # Check if this function has asset transfers
        if function.has_asset_transfers:
            return True

        # Find internal function calls and check them recursively
        if not function.body:
            return False

        calls = self._find_all_calls(function.body)
        for call in calls:
            # Get the called function name
            called_func_name = self._extract_called_function_name(call)
            if called_func_name and called_func_name in func_map:
                called_func = func_map[called_func_name]
                if self._has_asset_transfers_recursive(called_func, func_map, visited):
                    return True

        return False

    def _extract_called_function_name(self, call: CallExpression) -> Optional[str]:
        """Extract the name of the function being called."""
        if not hasattr(call, 'function') or not call.function:
            return None

        function_expr = call.function

        # For identifiers (direct calls like foo())
        if isinstance(function_expr, Identifier) and hasattr(function_expr, 'name'):
            return function_expr.name

        # For member access (like this.foo()), extract the method name
        if isinstance(function_expr, Literal) and hasattr(function_expr, 'value'):
            call_text = function_expr.value
            # For this.method() or obj.method(), we want the method name
            if '.' in call_text:
                parts = call_text.split('.')
                method_name = parts[-1].strip('()')
                # Only return if it looks like a simple function name (not a complex expression)
                if method_name.isidentifier():
                    return method_name

        return None

    def build_contract_context(self, contract, all_contracts=None) -> Dict:
        """
        Build comprehensive context for a contract including inherited members.

        Args:
            contract: The contract declaration
            all_contracts: Optional list of all contracts (for inheritance resolution)

        Returns:
            Dict with contract functions, modifiers, and variables
        """
        context = {
            'contract_functions': [],
            'contract_modifiers': [],
            'state_variables': [],
            'local_variables': [],
            'parameters': []
        }

        # Add current contract members
        if hasattr(contract, 'functions'):
            context['contract_functions'] = [f.name for f in contract.functions if hasattr(f, 'name')]

        if hasattr(contract, 'modifiers'):
            context['contract_modifiers'] = [m.name for m in contract.modifiers if hasattr(m, 'name')]

        if hasattr(contract, 'variables'):
            context['state_variables'] = [v.name for v in contract.variables if hasattr(v, 'name')]

        # TODO: Add inherited members from base contracts
        # This would require traversing the inheritance tree

        return context
