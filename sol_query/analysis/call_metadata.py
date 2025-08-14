"""Call metadata wrapper for structured access to call information."""

import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from sol_query.core.ast_nodes import CallExpression, Expression, ASTNode
from sol_query.analysis.call_types import CallType, CallTypeDetector


@dataclass
class CallArgument:
    """Represents a call argument with metadata."""
    index: int
    expression: Expression
    value: Optional[str] = None
    type_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'index': self.index,
            'value': self.value,
            'type_hint': self.type_hint,
            'source_code': self.expression.get_source_code() if self.expression else None
        }


class CallMetadata:
    """
    Wrapper class providing structured access to call information.
    Similar to Glider's Call class functionality.
    """

    def __init__(self, call_expression: CallExpression):
        """Initialize with a call expression."""
        self.call_expression = call_expression
        self._call_type: Optional[CallType] = None
        self._function_name: Optional[str] = None
        self._signature: Optional[str] = None
        self._arguments: Optional[List[CallArgument]] = None
        self._call_value: Optional[str] = None
        self._call_gas: Optional[str] = None
        self._contract_name: Optional[str] = None

        # Initialize detector
        self.detector = CallTypeDetector()

    def get_call_type(self) -> CallType:
        """Get the type of this call."""
        if self._call_type is None:
            source_code = self.call_expression.get_source_code()
            self._call_type = self.detector.detect_call_type(source_code)
        return self._call_type

    def get_name(self) -> Optional[str]:
        """Get the name of the function being called."""
        if self._function_name is None:
            self._function_name = self._extract_function_name()
        return self._function_name

    def get_signature(self) -> Optional[str]:
        """Get the signature of the function call."""
        if self._signature is None:
            self._signature = self._extract_signature()
        return self._signature

    def get_args(self) -> List[CallArgument]:
        """Get the arguments of the call."""
        if self._arguments is None:
            self._arguments = self._extract_arguments()
        return self._arguments

    def get_arg(self, index: int) -> Optional[CallArgument]:
        """Get a specific argument by index."""
        args = self.get_args()
        if 0 <= index < len(args):
            return args[index]
        return None

    def get_call_value(self) -> Optional[str]:
        """Get the ETH value being sent with the call."""
        if self._call_value is None:
            self._call_value = self._extract_call_value()
        return self._call_value

    def get_call_gas(self) -> Optional[str]:
        """Get the gas specification for the call."""
        if self._call_gas is None:
            self._call_gas = self._extract_call_gas()
        return self._call_gas

    def get_contract_name(self) -> Optional[str]:
        """Get the contract name if this is an external call."""
        if self._contract_name is None:
            self._contract_name = self._extract_contract_name()
        return self._contract_name

    def get_function(self) -> Optional[ASTNode]:
        """
        Get the function being called if it can be resolved.
        Returns None for external calls or unresolvable calls.
        """
        # This is a simplified implementation
        # In a full implementation, this would resolve to the actual function declaration
        return None

    def get_special_params(self) -> Dict[str, str]:
        """Get special parameters like gas, value, salt for low-level calls."""
        params = {}

        # Extract gas
        gas = self.get_call_gas()
        if gas:
            params['gas'] = gas

        # Extract value
        value = self.get_call_value()
        if value:
            params['value'] = value

        # Extract salt (for CREATE2)
        salt = self._extract_call_salt()
        if salt:
            params['salt'] = salt

        return params

    def get_call_qualifier(self) -> Optional[str]:
        """Get the call qualifier (.call, .delegatecall, .staticcall, etc.)."""
        source = self.call_expression.get_source_code()

        # Look for low-level call patterns
        patterns = [
            r'\.call\s*\(',
            r'\.delegatecall\s*\(',
            r'\.staticcall\s*\(',
            r'\.send\s*\(',
            r'\.transfer\s*\(',
        ]

        for pattern in patterns:
            match = re.search(pattern, source)
            if match:
                return match.group(0).strip('(').strip()

        return None

    def kv_parameters(self) -> Dict[str, Any]:
        """Get key-value parameters from the call."""
        params = {}

        # Add basic call information
        params['function_name'] = self.get_name()
        params['call_type'] = self.get_call_type().value if self.get_call_type() else 'unknown'
        params['signature'] = self.get_signature()
        params['argument_count'] = len(self.get_args())

        # Add special parameters
        special = self.get_special_params()
        params.update(special)

        return params

    @property
    def expression(self) -> str:
        """Get the source code expression."""
        return self.call_expression.get_source_code()

    def _extract_function_name(self) -> Optional[str]:
        """Extract function name from the call expression."""
        # Try to get from AST first
        if hasattr(self.call_expression, 'function'):
            if hasattr(self.call_expression.function, 'name'):
                return self.call_expression.function.name

        # Fall back to regex extraction from source code
        source = self.call_expression.get_source_code()

        # Pattern for simple function calls: functionName(...)
        simple_match = re.match(r'^(\w+)\s*\(', source)
        if simple_match:
            return simple_match.group(1)

        # Pattern for member calls: object.functionName(...)
        member_match = re.search(r'\.(\w+)\s*\(', source)
        if member_match:
            return member_match.group(1)

        # Pattern for interface calls: Interface(...).functionName(...)
        interface_match = re.search(r'\([^)]*\)\.(\w+)\s*\(', source)
        if interface_match:
            return interface_match.group(1)

        return None

    def _extract_signature(self) -> Optional[str]:
        """Extract function signature from the call."""
        function_name = self.get_name()
        if not function_name:
            return None

        args = self.get_args()
        arg_types = []

        for arg in args:
            # Try to infer argument types from source code
            arg_source = arg.expression.get_source_code()
            arg_type = self._infer_argument_type(arg_source)
            arg_types.append(arg_type)

        return f"{function_name}({','.join(arg_types)})"

    def _extract_arguments(self) -> List[CallArgument]:
        """Extract call arguments."""
        arguments = []

        if hasattr(self.call_expression, 'arguments'):
            for i, arg_expr in enumerate(self.call_expression.arguments):
                arg_value = arg_expr.get_source_code()
                arg_type = self._infer_argument_type(arg_value)

                call_arg = CallArgument(
                    index=i,
                    expression=arg_expr,
                    value=arg_value,
                    type_hint=arg_type
                )
                arguments.append(call_arg)

        return arguments

    def _extract_call_value(self) -> Optional[str]:
        """Extract ETH value from call if present."""
        source = self.call_expression.get_source_code()

        # Pattern: .call{value: amount}(...)
        value_match = re.search(r'\{[^}]*value\s*:\s*([^,}]+)', source)
        if value_match:
            return value_match.group(1).strip()

        # Pattern: .call{value: amount, gas: gasAmount}(...)
        complex_value_match = re.search(r'value\s*:\s*([^,}]+)', source)
        if complex_value_match:
            return complex_value_match.group(1).strip()

        return None

    def _extract_call_gas(self) -> Optional[str]:
        """Extract gas specification from call if present."""
        source = self.call_expression.get_source_code()

        # Pattern: .call{gas: amount}(...)
        gas_match = re.search(r'\{[^}]*gas\s*:\s*([^,}]+)', source)
        if gas_match:
            return gas_match.group(1).strip()

        # Pattern: .call{value: val, gas: gasAmount}(...)
        complex_gas_match = re.search(r'gas\s*:\s*([^,}]+)', source)
        if complex_gas_match:
            return complex_gas_match.group(1).strip()

        return None

    def _extract_call_salt(self) -> Optional[str]:
        """Extract salt parameter for CREATE2 calls."""
        source = self.call_expression.get_source_code()

        # Pattern: .call{salt: saltValue}(...)
        salt_match = re.search(r'salt\s*:\s*([^,}]+)', source)
        if salt_match:
            return salt_match.group(1).strip()

        return None

    def _extract_contract_name(self) -> Optional[str]:
        """Extract contract name for external calls."""
        source = self.call_expression.get_source_code()

        # Pattern: ContractName(address).method(...)
        contract_match = re.match(r'([A-Z]\w*)\s*\([^)]*\)\.', source)
        if contract_match:
            return contract_match.group(1)

        # Pattern: IContractName(address).method(...)
        interface_match = re.match(r'(I[A-Z]\w*)\s*\([^)]*\)\.', source)
        if interface_match:
            return interface_match.group(1)

        return None

    def _infer_argument_type(self, arg_source: str) -> str:
        """Infer argument type from source code."""
        arg_source = arg_source.strip()

        # Numeric literals
        if re.match(r'^\d+$', arg_source):
            return 'uint256'

        # Hex literals
        if re.match(r'^0x[0-9a-fA-F]+$', arg_source):
            if len(arg_source) == 42:  # 0x + 40 hex chars = address
                return 'address'
            else:
                return 'bytes'

        # String literals
        if arg_source.startswith('"') and arg_source.endswith('"'):
            return 'string'

        # Boolean literals
        if arg_source in ['true', 'false']:
            return 'bool'

        # Address-like patterns
        if re.match(r'.*\.sender|.*\.origin', arg_source):
            return 'address'

        # Default to unknown
        return 'unknown'

    def to_dict(self) -> Dict[str, Any]:
        """Convert call metadata to JSON-serializable dictionary."""
        return {
            'function_name': self.get_name(),
            'signature': self.get_signature(),
            'call_type': self.get_call_type().value if self.get_call_type() else 'unknown',
            'arguments': [arg.to_dict() for arg in self.get_args()],
            'call_value': self.get_call_value(),
            'call_gas': self.get_call_gas(),
            'contract_name': self.get_contract_name(),
            'call_qualifier': self.get_call_qualifier(),
            'special_params': self.get_special_params(),
            'source_code': self.expression
        }


# Convenience function to create call metadata
def analyze_call(call_expression: CallExpression) -> CallMetadata:
    """Create call metadata wrapper for a call expression."""
    return CallMetadata(call_expression)
