"""Call type classification system for Solidity code analysis."""

from enum import Enum
from typing import Set, Dict, List, Optional, Pattern
import re


class CallType(str, Enum):
    """Types of calls in Solidity code, based on Glider's classification."""

    # Function call types
    EXTERNAL = "external"           # External contract calls
    INTERNAL = "internal"           # Internal function calls
    LIBRARY = "library"             # Library function calls
    LOW_LEVEL = "low_level"         # Low-level calls (.call, .delegatecall, etc.)

    # Visibility-based types
    PUBLIC = "public"               # Public function calls
    PRIVATE = "private"             # Private function calls

    # Special call types
    EVENT = "event"                 # Event emissions (emit)
    SOLIDITY = "solidity"           # Built-in Solidity functions

    # Constructor and creation calls
    NEW_ARR = "new_arr"             # Array creation (new uint256[](size))
    NEW_ELEMENTARY_TYPE = "new_elementary_type"  # Elementary type creation
    NEW_STRUCT = "new_struct"       # Struct creation
    NEW_CONTRACT = "new_contract"   # Contract creation (new Contract())

    # Conversion and casting
    TYPE_CONVERSION = "type_conversion"  # Type conversions

    # Assembly and special
    ASSEMBLY = "assembly"           # Assembly block calls
    DELEGATE = "delegate"           # Delegate calls specifically
    STATIC = "static"               # Static calls specifically

    # Unknown/unclassified
    UNKNOWN = "unknown"


class CallTypeDetector:
    """Detects and classifies different types of calls in Solidity code."""

    def __init__(self):
        """Initialize the call type detector with patterns and rules."""

        # Low-level call patterns (more specific)
        self.low_level_patterns = {
            r'\.call\s*\{',           # .call{...}
            r'\.call\s*\(\s*["\']',   # .call("data") or .call('')
            r'\.call\s*\(\s*\)',      # .call()
            r'\.send\s*\(',           # .send()
            r'payable\s*\([^)]+\)\.transfer\s*\(',  # payable(addr).transfer() - this is low level
            r'\w+\.transfer\s*\(\s*\d+\s*(ether|wei|gwei)', # target.transfer(1 ether) - low level
        }

        # Delegate call specific patterns
        self.delegate_patterns = {
            r'\.delegatecall\s*\(',
            r'assembly\s*\{[^}]*delegatecall\s*\(',
        }

        # Static call patterns
        self.static_patterns = {
            r'\.staticcall\s*\(',
            r'assembly\s*\{[^}]*staticcall\s*\(',
        }

        # Event emission patterns
        self.event_patterns = {
            r'\bemit\s+\w+\s*\(',
        }

        # Built-in Solidity function patterns
        self.solidity_builtin_patterns = {
            r'\brequire\s*\(',
            r'\bassert\s*\(',
            r'\brevert\s*\(',
            r'\bkeccak256\s*\(',
            r'\bsha256\s*\(',
            r'\bsha3\s*\(',
            r'\bripemd160\s*\(',
            r'\becrecover\s*\(',
            r'\baddmod\s*\(',
            r'\bmulmod\s*\(',
            r'\babi\.encode\s*\(',
            r'\babi\.encodePacked\s*\(',
            r'\babi\.encodeWithSelector\s*\(',
            r'\babi\.encodeWithSignature\s*\(',
            r'\babi\.decode\s*\(',
            r'\bblock\.\w+',
            r'\bmsg\.\w+',
            r'\btx\.\w+',
            r'\bgasleft\s*\(',
        }

        # Library call patterns (using for directive context)
        self.library_patterns = {
            r'\busing\s+\w+\s+for\s+',  # using Library for Type
            r'\w+\.\w+\s*\(',  # LibraryName.functionName()
        }

        # Constructor/creation patterns
        self.creation_patterns = {
            'new_array': r'\bnew\s+\w+\[\]',
            'new_array_sized': r'\bnew\s+\w+\[\d+\]',
            'new_contract': r'\bnew\s+[A-Z]\w*\s*\(',
            'new_struct': r'\bnew\s+[A-Z]\w*\s*\{',
        }

        # Type conversion patterns
        self.type_conversion_patterns = {
            r'\b(address|uint\d*|int\d*|bytes\d*|bool|string)\s*\(',
            r'\bpayable\s*\(',
        }

        # Assembly patterns
        self.assembly_patterns = {
            r'\bassembly\s*\{[^}]*\bcall\s*\(',
            r'\bassembly\s*\{[^}]*\bdelegatecall\s*\(',
            r'\bassembly\s*\{[^}]*\bstaticcall\s*\(',
        }

        # Try/catch patterns
        self.try_catch_patterns = {
            r'\btry\s+\w+\.[a-zA-Z_]\w*\s*\(',
            r'\btry\s+[A-Z]\w*\s*\([^)]*\)\s*\.\w+\s*\(',
            r'\btry\s+new\s+\w+\s*\(',
        }

        # Enhanced assembly patterns for specific calls
        self.assembly_delegate_patterns = {
            r'\bassembly\s*\{[^}]*\bdelegatecall\s*\(',
            r'\bassembly\s*\{[^}]*let\s+result\s*:=\s*delegatecall\s*\(',
        }

        self.assembly_static_patterns = {
            r'\bassembly\s*\{[^}]*\bstaticcall\s*\(',
            r'\bassembly\s*\{[^}]*let\s+result\s*:=\s*staticcall\s*\(',
        }

        # Interface call patterns (be more specific to avoid false positives)
        self.interface_patterns = {
            r'I[A-Z]\w*\s*\([^)]*\)\s*\.\w+\s*\(',  # IInterface(address).method()
            r'[A-Z]\w*\s*\([^)]*\)\s*\.\w+\s*\(',   # Contract(address).method()
            r'\w+\.(transfer|balanceOf|approve|allowance)\s*\(',  # Common ERC20 methods
        }

        # Compile all patterns for performance
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        self.compiled_low_level = [re.compile(p, re.IGNORECASE) for p in self.low_level_patterns]
        self.compiled_delegate = [re.compile(p, re.IGNORECASE) for p in self.delegate_patterns]
        self.compiled_static = [re.compile(p, re.IGNORECASE) for p in self.static_patterns]
        self.compiled_event = [re.compile(p, re.IGNORECASE) for p in self.event_patterns]
        self.compiled_solidity = [re.compile(p, re.IGNORECASE) for p in self.solidity_builtin_patterns]
        self.compiled_library = [re.compile(p, re.IGNORECASE) for p in self.library_patterns]
        self.compiled_type_conversion = [re.compile(p, re.IGNORECASE) for p in self.type_conversion_patterns]
        self.compiled_assembly = [re.compile(p, re.IGNORECASE) for p in self.assembly_patterns]
        self.compiled_interface = [re.compile(p, re.IGNORECASE) for p in self.interface_patterns]
        self.compiled_try_catch = [re.compile(p, re.IGNORECASE) for p in self.try_catch_patterns]
        self.compiled_assembly_delegate = [re.compile(p, re.IGNORECASE) for p in self.assembly_delegate_patterns]
        self.compiled_assembly_static = [re.compile(p, re.IGNORECASE) for p in self.assembly_static_patterns]

        self.compiled_creation = {}
        for key, pattern in self.creation_patterns.items():
            self.compiled_creation[key] = re.compile(pattern, re.IGNORECASE)

    def detect_call_type(self, source_code: str, context: Optional[Dict] = None) -> CallType:
        """
        Detect the type of call from source code.
        
        Args:
            source_code: The source code of the call expression
            context: Optional context information (function visibility, etc.)
            
        Returns:
            The detected CallType
        """
        source_code = source_code.strip()

        # Priority order matters - check most specific patterns first

        # 1. Event emissions
        if self._matches_any(source_code, self.compiled_event):
            return CallType.EVENT

        # 2. Assembly delegate calls (most specific)
        if self._matches_any(source_code, self.compiled_assembly_delegate):
            return CallType.DELEGATE

        # 3. Assembly static calls (most specific)
        if self._matches_any(source_code, self.compiled_assembly_static):
            return CallType.STATIC

        # 4. Assembly calls (general)
        if self._matches_any(source_code, self.compiled_assembly):
            return CallType.ASSEMBLY

        # 5. Delegate calls (specific)
        if self._matches_any(source_code, self.compiled_delegate):
            return CallType.DELEGATE

        # 4. Static calls (specific)
        if self._matches_any(source_code, self.compiled_static):
            return CallType.STATIC

        # 5. Low-level calls (general)
        if self._matches_any(source_code, self.compiled_low_level):
            return CallType.LOW_LEVEL

        # 6. Interface/external calls (before built-in functions)
        if self._matches_any(source_code, self.compiled_interface):
            return CallType.EXTERNAL

        # 7. Built-in Solidity functions
        if self._matches_any(source_code, self.compiled_solidity):
            return CallType.SOLIDITY

        # 8. Constructor/creation calls
        creation_type = self._detect_creation_type(source_code)
        if creation_type:
            return creation_type

        # 9. Type conversions
        if self._matches_any(source_code, self.compiled_type_conversion):
            return CallType.TYPE_CONVERSION

        # 10. Internal calls via this
        if source_code.strip().startswith('this.'):
            return CallType.INTERNAL

        # 11. Library calls
        if self._is_library_call(source_code, context):
            return CallType.LIBRARY

        # 12. Internal vs external based on context
        if context:
            return self._classify_by_context(source_code, context)

        # 13. Default classification based on patterns
        return self._classify_default(source_code)

    def _matches_any(self, source_code: str, compiled_patterns: List[Pattern]) -> bool:
        """Check if source code matches any of the compiled patterns."""
        return any(pattern.search(source_code) for pattern in compiled_patterns)

    def _detect_creation_type(self, source_code: str) -> Optional[CallType]:
        """Detect constructor/creation call types."""
        if self.compiled_creation['new_array'].search(source_code) or \
           self.compiled_creation['new_array_sized'].search(source_code):
            return CallType.NEW_ARR

        if self.compiled_creation['new_contract'].search(source_code):
            return CallType.NEW_CONTRACT

        if self.compiled_creation['new_struct'].search(source_code):
            return CallType.NEW_STRUCT

        return None

    def _is_library_call(self, source_code: str, context: Optional[Dict]) -> bool:
        """Determine if this is a library call."""
        # Check for library usage patterns
        if self._matches_any(source_code, self.compiled_library):
            return True

        # Check context for library information
        if context and context.get('is_library_call'):
            return True

        # Pattern: LibraryName.function() where LibraryName is CamelCase and not interface patterns
        library_call_pattern = re.compile(r'^[A-Z]\w*\.\w+\s*\(', re.IGNORECASE)
        if library_call_pattern.match(source_code):
            # Exclude known interface patterns
            if not re.search(r'I[A-Z]\w*\s*\([^)]*\)', source_code):
                # Common library names
                if re.match(r'^(SafeMath|Math|Strings|Address|Arrays|LibraryName)\.\w+', source_code):
                    return True

        return False

    def _classify_by_context(self, source_code: str, context: Dict) -> CallType:
        """Classify call type based on context information."""
        # Use function visibility if available
        if 'function_visibility' in context:
            visibility = context['function_visibility']
            if visibility == 'private':
                return CallType.PRIVATE
            elif visibility == 'public':
                return CallType.PUBLIC
            elif visibility == 'internal':
                return CallType.INTERNAL
            elif visibility == 'external':
                return CallType.EXTERNAL

        # Use contract context
        if context.get('is_external_contract'):
            return CallType.EXTERNAL

        if context.get('is_same_contract'):
            return CallType.INTERNAL

        return CallType.UNKNOWN

    def _classify_default(self, source_code: str) -> CallType:
        """Default classification based on common patterns."""
        # Simple function call pattern: functionName(args)
        simple_call_pattern = re.compile(r'^[a-z_]\w*\s*\(', re.IGNORECASE)
        if simple_call_pattern.match(source_code):
            return CallType.INTERNAL

        # this.method() calls are internal
        if source_code.startswith('this.'):
            return CallType.INTERNAL

        # Member access pattern: object.method(args)
        member_call_pattern = re.compile(r'^\w+\.\w+\s*\(', re.IGNORECASE)
        if member_call_pattern.match(source_code):
            # Could be external or library, default to external
            return CallType.EXTERNAL

        return CallType.UNKNOWN

    def get_call_characteristics(self, call_type: CallType) -> Dict[str, any]:
        """Get characteristics and metadata for a call type."""
        characteristics = {
            CallType.EXTERNAL: {
                'is_external': True,
                'gas_cost': 'high',
                'trust_level': 'untrusted',
                'reentrancy_risk': True,
                'description': 'External contract call'
            },
            CallType.INTERNAL: {
                'is_external': False,
                'gas_cost': 'low',
                'trust_level': 'trusted',
                'reentrancy_risk': False,
                'description': 'Internal function call'
            },
            CallType.LIBRARY: {
                'is_external': False,
                'gas_cost': 'low',
                'trust_level': 'trusted',
                'reentrancy_risk': False,
                'description': 'Library function call'
            },
            CallType.LOW_LEVEL: {
                'is_external': True,
                'gas_cost': 'variable',
                'trust_level': 'untrusted',
                'reentrancy_risk': True,
                'description': 'Low-level call (.call, .send, .transfer)'
            },
            CallType.DELEGATE: {
                'is_external': True,
                'gas_cost': 'high',
                'trust_level': 'dangerous',
                'reentrancy_risk': True,
                'description': 'Delegate call (executes in current context)'
            },
            CallType.STATIC: {
                'is_external': True,
                'gas_cost': 'medium',
                'trust_level': 'safe',
                'reentrancy_risk': False,
                'description': 'Static call (read-only)'
            },
            CallType.EVENT: {
                'is_external': False,
                'gas_cost': 'medium',
                'trust_level': 'safe',
                'reentrancy_risk': False,
                'description': 'Event emission'
            },
            CallType.SOLIDITY: {
                'is_external': False,
                'gas_cost': 'low',
                'trust_level': 'trusted',
                'reentrancy_risk': False,
                'description': 'Built-in Solidity function'
            },
        }

        return characteristics.get(call_type, {
            'is_external': None,
            'gas_cost': 'unknown',
            'trust_level': 'unknown',
            'reentrancy_risk': None,
            'description': f'Unknown call type: {call_type}'
        })


# Convenience function for quick call type detection
def detect_call_type(source_code: str, context: Optional[Dict] = None) -> CallType:
    """Convenience function to detect call type from source code."""
    detector = CallTypeDetector()
    return detector.detect_call_type(source_code, context)
