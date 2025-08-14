"""Call analyzer for detecting external calls and asset transfers in Solidity code."""

import re
from typing import List, Set, Dict, Optional, Tuple
from sol_query.core.ast_nodes import (
    ASTNode, FunctionDeclaration, CallExpression, Expression,
    Identifier, Literal, BinaryExpression
)


class CallAnalyzer:
    """Analyzes function calls to detect external calls and asset transfers."""

    def __init__(self):
        """Initialize the call analyzer."""
        # Patterns for detecting external calls
        self.external_call_patterns = {
            # Direct external contract calls
            'contract_call': [
                r'\.call\(',
                r'\.delegatecall\(',
                r'\.staticcall\(',
                r'\.send\(',
                r'\.transfer\(',
            ],
            # Interface calls (detected by pattern)
            'interface_call': [
                r'[A-Z][a-zA-Z0-9]*\([^)]*\)\.',  # Contract(address).method()
                r'I[A-Z][a-zA-Z0-9]*\([^)]*\)\.',  # IContract(address).method()
            ],
            # Common external contract patterns
            'known_external': [
                'IERC20', 'IERC721', 'IERC1155',
                'Uniswap', 'Sushiswap', 'Compound',
                'Aave', 'Chainlink', 'Oracle'
            ]
        }

        # Patterns for detecting asset transfers
        self.asset_transfer_patterns = {
            # ETH transfers
            'eth_transfer': [
                r'\.send\(',
                r'\.transfer\(',
                r'\.call\{value:',
                r'payable\([^)]+\)\.transfer\(',
                r'payable\([^)]+\)\.send\(',
            ],
            # Token transfers
            'token_transfer': [
                r'\.transfer\(',
                r'\.transferFrom\(',
                r'\.safeTransfer\(',
                r'\.safeTransferFrom\(',
                r'IERC20\([^)]+\)\.transfer',
                r'ERC20\([^)]+\)\.transfer',
            ],
            # NFT transfers
            'nft_transfer': [
                r'\.safeTransferFrom\(',
                r'\.transferFrom\(',
                r'IERC721\([^)]+\)\.transfer',
                r'IERC1155\([^)]+\)\.safeTransfer',
            ]
        }

        # Known function names that indicate external calls
        self.external_function_names = {
            'call', 'delegatecall', 'staticcall', 'send', 'transfer',
            'approve', 'transferFrom', 'safeTransfer', 'safeTransferFrom',
            'mint', 'burn', 'swap', 'deposit', 'withdraw',
            'flashLoan', 'borrow', 'repay', 'liquidate'
        }

        # Known function names that indicate asset transfers
        self.asset_transfer_function_names = {
            'send', 'transfer', 'transferFrom', 'safeTransfer', 'safeTransferFrom',
            'withdraw', 'deposit', 'mint', 'burn'
        }

    def analyze_function(self, function: FunctionDeclaration) -> None:
        """
        Analyze a function for external calls and asset transfers.
        Updates the function's metadata fields.
        
        Args:
            function: The function to analyze
        """
        if not function.body:
            return

        # Extract all expressions from the function
        expressions = self._extract_all_expressions(function)

        # Analyze for external calls
        external_calls = self._detect_external_calls(expressions, function)
        function.has_external_calls = len(external_calls) > 0
        function.external_call_targets = list(external_calls)

        # Analyze for asset transfers
        asset_transfers = self._detect_asset_transfers(expressions, function)
        function.has_asset_transfers = len(asset_transfers) > 0
        function.asset_transfer_types = list(asset_transfers)

    def _extract_all_expressions(self, function: FunctionDeclaration) -> List[Expression]:
        """Extract all expressions from a function recursively."""
        expressions = []

        def extract_from_node(node: ASTNode):
            if isinstance(node, Expression):
                expressions.append(node)

            # Handle nested expressions in statements
            if hasattr(node, '_nested_expressions'):
                expressions.extend(node._nested_expressions)

            # Recursively extract from children
            for child in node.get_children():
                extract_from_node(child)

        if function.body:
            extract_from_node(function.body)

        return expressions

    def _detect_external_calls(self, expressions: List[Expression], function: FunctionDeclaration) -> Set[str]:
        """
        Detect external calls in the given expressions.
        
        Args:
            expressions: List of expressions to analyze
            function: The function being analyzed (for context)
            
        Returns:
            Set of external call targets/types detected
        """
        external_calls = set()

        for expr in expressions:
            # Analyze call expressions
            if isinstance(expr, CallExpression):
                call_info = self._analyze_call_expression(expr)
                if call_info:
                    external_calls.add(call_info)

            # Check source code patterns
            if hasattr(expr, 'get_source_code'):
                source_code = expr.get_source_code()
                call_type = self._match_external_call_patterns(source_code)
                if call_type:
                    external_calls.add(call_type)

        return external_calls

    def _detect_asset_transfers(self, expressions: List[Expression], function: FunctionDeclaration) -> Set[str]:
        """
        Detect asset transfers in the given expressions.
        
        Args:
            expressions: List of expressions to analyze
            function: The function being analyzed (for context)
            
        Returns:
            Set of asset transfer types detected
        """
        asset_transfers = set()

        for expr in expressions:
            # Analyze call expressions for transfer methods
            if isinstance(expr, CallExpression):
                transfer_info = self._analyze_transfer_call(expr)
                if transfer_info:
                    asset_transfers.add(transfer_info)

            # Check for ETH value transfers in call expressions
            if self._is_eth_value_transfer(expr):
                asset_transfers.add('eth_transfer')

            # Check source code patterns
            if hasattr(expr, 'get_source_code'):
                source_code = expr.get_source_code()
                transfer_type = self._match_asset_transfer_patterns(source_code)
                if transfer_type:
                    asset_transfers.add(transfer_type)

        return asset_transfers

    def _analyze_call_expression(self, call: CallExpression) -> Optional[str]:
        """
        Analyze a call expression to determine if it's an external call.
        
        Args:
            call: The call expression to analyze
            
        Returns:
            String describing the external call type, or None if not external
        """
        if not call.function:
            return None

        # Get function name
        function_name = None
        if isinstance(call.function, Identifier):
            function_name = call.function.name
        elif hasattr(call.function, 'name'):
            function_name = call.function.name

        if function_name and function_name in self.external_function_names:
            return f'external_call_{function_name}'

        # Check for member access patterns (contract.method())
        if hasattr(call.function, 'get_source_code'):
            source = call.function.get_source_code()
            if '.' in source:
                # This might be a contract call
                parts = source.split('.')
                if len(parts) >= 2:
                    method_name = parts[-1]
                    if method_name in self.external_function_names:
                        return f'external_call_{method_name}'
                    # Check if it looks like a contract interface call
                    if any(pattern in parts[0] for pattern in self.external_call_patterns['known_external']):
                        return f'interface_call_{method_name}'

        return None

    def _analyze_transfer_call(self, call: CallExpression) -> Optional[str]:
        """
        Analyze a call expression to determine if it's an asset transfer.
        
        Args:
            call: The call expression to analyze
            
        Returns:
            String describing the transfer type, or None if not a transfer
        """
        if not call.function:
            return None

        # Get function name
        function_name = None
        if isinstance(call.function, Identifier):
            function_name = call.function.name
        elif hasattr(call.function, 'name'):
            function_name = call.function.name

        if function_name and function_name in self.asset_transfer_function_names:
            # Determine transfer type based on context
            if function_name in ['send', 'transfer'] and self._has_value_parameter(call):
                return 'eth_transfer'
            elif function_name in ['transfer', 'transferFrom', 'safeTransfer', 'safeTransferFrom']:
                return 'token_transfer'
            elif function_name in ['mint', 'burn']:
                return 'token_mint_burn'
            elif function_name in ['deposit', 'withdraw']:
                return 'asset_movement'

        return None

    def _is_eth_value_transfer(self, expr: Expression) -> bool:
        """
        Check if an expression represents an ETH value transfer.
        
        Args:
            expr: The expression to check
            
        Returns:
            True if this is an ETH value transfer
        """
        if hasattr(expr, 'get_source_code'):
            source = expr.get_source_code()
            # Look for {value: ...} patterns
            if re.search(r'\{value:\s*[^}]+\}', source):
                return True
            # Look for payable(...).transfer/send patterns
            if re.search(r'payable\([^)]+\)\.(transfer|send)\(', source):
                return True

        return False

    def _has_value_parameter(self, call: CallExpression) -> bool:
        """
        Check if a call expression has a value parameter (indicating ETH transfer).
        
        Args:
            call: The call expression to check
            
        Returns:
            True if the call has a value parameter
        """
        # This is a simplified check - in practice, we'd need to analyze
        # the call syntax more carefully
        if hasattr(call, 'get_source_code'):
            source = call.get_source_code()
            return '{value:' in source or 'msg.value' in source

        return False

    def _match_external_call_patterns(self, source_code: str) -> Optional[str]:
        """
        Match source code against external call patterns.
        
        Args:
            source_code: The source code to analyze
            
        Returns:
            String describing the external call type, or None if no match
        """
        for call_type, patterns in self.external_call_patterns.items():
            for pattern in patterns:
                if re.search(pattern, source_code):
                    return call_type

        return None

    def _match_asset_transfer_patterns(self, source_code: str) -> Optional[str]:
        """
        Match source code against asset transfer patterns.
        
        Args:
            source_code: The source code to analyze
            
        Returns:
            String describing the transfer type, or None if no match
        """
        for transfer_type, patterns in self.asset_transfer_patterns.items():
            for pattern in patterns:
                if re.search(pattern, source_code):
                    return transfer_type

        return None

    def analyze_call_tree_external_calls(self, function: FunctionDeclaration,
                                       all_functions: List[FunctionDeclaration],
                                       visited: Optional[Set[str]] = None) -> bool:
        """
        Analyze if a function has external calls in its call tree (deep analysis).
        
        Args:
            function: The function to analyze
            all_functions: All functions in the codebase
            visited: Set of visited function names to avoid cycles
            
        Returns:
            True if the function or any function it calls has external calls
        """
        if visited is None:
            visited = set()

        # Avoid infinite recursion
        if function.name in visited:
            return False

        visited.add(function.name)

        # Check if this function directly has external calls
        if function.has_external_calls:
            return True

        # Check functions called by this function
        called_functions = self._get_called_functions(function, all_functions)
        for called_func in called_functions:
            if self.analyze_call_tree_external_calls(called_func, all_functions, visited.copy()):
                return True

        return False

    def analyze_call_tree_asset_transfers(self, function: FunctionDeclaration,
                                        all_functions: List[FunctionDeclaration],
                                        visited: Optional[Set[str]] = None) -> bool:
        """
        Analyze if a function has asset transfers in its call tree (deep analysis).
        
        Args:
            function: The function to analyze
            all_functions: All functions in the codebase
            visited: Set of visited function names to avoid cycles
            
        Returns:
            True if the function or any function it calls has asset transfers
        """
        if visited is None:
            visited = set()

        # Avoid infinite recursion
        if function.name in visited:
            return False

        visited.add(function.name)

        # Check if this function directly has asset transfers
        if function.has_asset_transfers:
            return True

        # Check functions called by this function
        called_functions = self._get_called_functions(function, all_functions)
        for called_func in called_functions:
            if self.analyze_call_tree_asset_transfers(called_func, all_functions, visited.copy()):
                return True

        return False

    def _get_called_functions(self, function: FunctionDeclaration,
                            all_functions: List[FunctionDeclaration]) -> List[FunctionDeclaration]:
        """
        Get functions called by the given function.
        
        Args:
            function: The function to analyze
            all_functions: All functions in the codebase
            
        Returns:
            List of functions called by the given function
        """
        if not function.body:
            return []

        called_functions = []
        expressions = self._extract_all_expressions(function)

        # Extract function names from call expressions
        called_names = set()
        for expr in expressions:
            if isinstance(expr, CallExpression) and expr.function:
                if isinstance(expr.function, Identifier):
                    called_names.add(expr.function.name)
                elif hasattr(expr.function, 'name'):
                    called_names.add(expr.function.name)

        # Find matching functions
        for func in all_functions:
            if func.name in called_names and func != function:
                called_functions.append(func)

        return called_functions
