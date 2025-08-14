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

    def analyze_function(self, function: FunctionDeclaration, contract_context: Optional[Dict] = None) -> None:
        """
        Analyze a function for external calls and asset transfers.
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

        # Extract all expressions from the function
        expressions = self._extract_all_expressions(function)

        # Analyze for external calls with context
        external_calls = self._detect_external_calls_contextual(expressions, function, contract_context)
        function.has_external_calls = len(external_calls) > 0
        function.external_call_targets = list(external_calls)

        # Analyze for asset transfers with context
        asset_transfers = self._detect_asset_transfers_contextual(expressions, function, contract_context)
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

    # ===== CONTEXTUAL ANALYSIS METHODS =====

    def _build_basic_context(self, function: FunctionDeclaration) -> Dict:
        """
        Build a basic context for a function when full contract context is not available.
        
        Args:
            function: The function being analyzed
            
        Returns:
            Basic context dictionary
        """
        context = {
            'contract_functions': set(),
            'inherited_functions': set(),
            'contract_variables': set(),
            'is_interface_call': lambda target: self._looks_like_interface_call(target),
            'is_low_level_call': lambda target: target in ['call', 'delegatecall', 'staticcall']
        }

        # If we have parent contract info, use it
        if hasattr(function, 'parent_contract') and function.parent_contract:
            contract = function.parent_contract
            context['contract_functions'] = {f.name for f in contract.functions}
            context['contract_variables'] = {v.name for v in contract.variables}

        return context

    def build_contract_context(self, contract, all_contracts: List) -> Dict:
        """
        Build comprehensive contract context for accurate call analysis.
        
        Args:
            contract: The current contract being analyzed
            all_contracts: All contracts in the codebase
            
        Returns:
            Comprehensive context dictionary
        """
        context = {
            'contract_functions': set(),
            'inherited_functions': set(),
            'contract_variables': set(),
            'contract_name': contract.name,
            'is_interface_call': lambda target: self._looks_like_interface_call(target),
            'is_low_level_call': lambda target: target in ['call', 'delegatecall', 'staticcall']
        }

        # Add current contract functions and variables
        context['contract_functions'] = {f.name for f in contract.functions}
        context['contract_variables'] = {v.name for v in contract.variables}

        # Add inherited functions
        for base_name in contract.inheritance:
            base_contract = self._find_contract_by_name(base_name, all_contracts)
            if base_contract:
                context['inherited_functions'].update(f.name for f in base_contract.functions)
                # Recursively add inherited functions from base contracts
                base_context = self.build_contract_context(base_contract, all_contracts)
                context['inherited_functions'].update(base_context['inherited_functions'])

        return context

    def _find_contract_by_name(self, name: str, contracts: List) -> Optional[ASTNode]:
        """Find a contract by name in the list of contracts."""
        for contract in contracts:
            if hasattr(contract, 'name') and contract.name == name:
                return contract
        return None

    def _detect_external_calls_contextual(self, expressions: List[Expression],
                                        function: FunctionDeclaration,
                                        context: Dict) -> Set[str]:
        """
        Detect external calls using contextual analysis.
        
        Args:
            expressions: List of expressions to analyze
            function: The function being analyzed
            context: Contract context information
            
        Returns:
            Set of external call types detected
        """
        external_calls = set()

        for expr in expressions:
            if isinstance(expr, CallExpression):
                call_info = self._analyze_call_contextually(expr, context)
                if call_info:
                    external_calls.add(call_info)

        return external_calls

    def _detect_asset_transfers_contextual(self, expressions: List[Expression],
                                         function: FunctionDeclaration,
                                         context: Dict) -> Set[str]:
        """
        Detect asset transfers using contextual analysis.
        
        Args:
            expressions: List of expressions to analyze
            function: The function being analyzed
            context: Contract context information
            
        Returns:
            Set of asset transfer types detected
        """
        asset_transfers = set()

        for expr in expressions:
            if isinstance(expr, CallExpression):
                transfer_info = self._analyze_transfer_contextually(expr, context)
                if transfer_info:
                    asset_transfers.add(transfer_info)

            # Check for ETH value transfers
            if self._is_eth_value_transfer(expr):
                asset_transfers.add('eth_transfer')

        return asset_transfers

    def _analyze_call_contextually(self, call: CallExpression, context: Dict) -> Optional[str]:
        """
        Analyze a call expression contextually to determine if it's external.
        
        Args:
            call: The call expression to analyze
            context: Contract context information
            
        Returns:
            String describing the external call type, or None if internal
        """
        if not call.function:
            return None

        # Parse the call target and function name
        target, function_name = self._parse_call_target(call)

        # Low-level calls are always external
        if context['is_low_level_call'](function_name):
            return f'low_level_call_{function_name}'

        # Direct function calls (no target)
        if target is None:
            # Check if function exists in current contract context
            if (function_name in context['contract_functions'] or
                function_name in context['inherited_functions']):
                return None  # Internal call
            else:
                # Could be external, but be conservative
                if function_name in self.external_function_names:
                    return f'possible_external_call_{function_name}'
                return None

        # Calls with explicit targets
        if target == 'this':
            return None  # Internal call via this

        # Interface calls or contract variable calls
        if (context['is_interface_call'](target) or
            self._is_contract_variable_call(target, context)):
            return f'external_call_{function_name}'

        # Member access that looks external
        if '.' in str(target) or self._looks_like_external_target(target):
            return f'external_call_{function_name}'

        return None

    def _analyze_transfer_contextually(self, call: CallExpression, context: Dict) -> Optional[str]:
        """
        Analyze a call expression contextually to determine if it's an asset transfer.
        
        Args:
            call: The call expression to analyze
            context: Contract context information
            
        Returns:
            String describing the transfer type, or None if not a transfer
        """
        if not call.function:
            return None

        target, function_name = self._parse_call_target(call)

        # Check if this is a transfer function
        if function_name not in self.asset_transfer_function_names:
            return None

        # Low-level calls with value
        if function_name in ['call', 'send', 'transfer'] and self._has_value_parameter(call):
            return 'eth_transfer'

        # Direct function calls
        if target is None:
            # Check if it's an internal transfer function
            if function_name in context['contract_functions']:
                # Internal function, but might still transfer assets
                return f'internal_transfer_{function_name}'
            else:
                # Likely external transfer
                return self._classify_transfer_type(function_name)

        # External contract calls
        if target != 'this' and (context['is_interface_call'](target) or
                                self._is_contract_variable_call(target, context)):
            return self._classify_transfer_type(function_name)

        return None

    def _parse_call_target(self, call: CallExpression) -> Tuple[Optional[str], str]:
        """
        Parse a call expression to extract the target and function name.
        
        Args:
            call: The call expression to parse
            
        Returns:
            Tuple of (target, function_name)
        """
        if not call.function:
            return None, "unknown"

        # Simple identifier (direct function call)
        if isinstance(call.function, Identifier):
            return None, call.function.name

        # Try to get source code and parse it
        if hasattr(call.function, 'get_source_code'):
            source = call.function.get_source_code()
            if '.' in source:
                parts = source.split('.')
                if len(parts) >= 2:
                    target = '.'.join(parts[:-1])
                    function_name = parts[-1]
                    return target, function_name

        # Fallback
        if hasattr(call.function, 'name'):
            return None, call.function.name

        return None, "unknown"

    def _looks_like_interface_call(self, target: str) -> bool:
        """Check if a target looks like an interface call."""
        if not target:
            return False

        # Interface casting patterns
        interface_patterns = [
            r'I[A-Z][a-zA-Z0-9]*\(',  # IERC20(address)
            r'[A-Z][a-zA-Z0-9]*\(',   # Contract(address)
        ]

        for pattern in interface_patterns:
            if re.search(pattern, target):
                return True

        return False

    def _is_contract_variable_call(self, target: str, context: Dict) -> bool:
        """Check if target is a contract variable."""
        if not target:
            return False

        # Simple variable name
        if target in context['contract_variables']:
            return True

        # Could be a more complex expression, be conservative
        return False

    def _looks_like_external_target(self, target: str) -> bool:
        """Check if target looks like an external call target."""
        if not target:
            return False

        # Common external patterns
        external_patterns = [
            r'[a-zA-Z_][a-zA-Z0-9_]*\[',  # array access
            r'[a-zA-Z_][a-zA-Z0-9_]*\.',  # member access
            r'address\(',                  # address casting
            r'payable\(',                  # payable casting
        ]

        for pattern in external_patterns:
            if re.search(pattern, target):
                return True

        return False

    def _classify_transfer_type(self, function_name: str) -> str:
        """Classify the type of asset transfer based on function name."""
        if function_name in ['send', 'transfer'] and function_name != 'transfer':
            return 'eth_transfer'
        elif function_name in ['transfer', 'transferFrom', 'safeTransfer', 'safeTransferFrom']:
            return 'token_transfer'
        elif function_name in ['mint', 'burn']:
            return 'token_mint_burn'
        elif function_name in ['deposit', 'withdraw']:
            return 'asset_movement'
        else:
            return f'asset_transfer_{function_name}'
