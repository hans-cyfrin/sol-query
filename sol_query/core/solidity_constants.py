"""
Centralized Solidity language constants to avoid duplication across the codebase.

This module contains all Solidity keywords, types, modifiers, and built-in identifiers
that are used for filtering and analysis throughout the codebase.
"""

from typing import Set, FrozenSet

# Core Solidity keywords and control flow
SOLIDITY_KEYWORDS: FrozenSet[str] = frozenset({
    # Control flow
    'if', 'else', 'for', 'while', 'do', 'break', 'continue', 'return',

    # Declarations
    'function', 'modifier', 'event', 'struct', 'enum', 'contract', 'interface', 'library',
    'constructor', 'fallback', 'receive',

    # Special keywords
    'emit', 'new', 'delete', 'using', 'pragma', 'import', 'is', 'override',
    'virtual', 'abstract',
})

# Solidity primitive types
SOLIDITY_TYPES: FrozenSet[str] = frozenset({
    # Integer types
    'uint8', 'uint16', 'uint32', 'uint64', 'uint128', 'uint256', 'uint',
    'int8', 'int16', 'int32', 'int64', 'int128', 'int256', 'int',

    # Other primitives
    'address', 'bool', 'string', 'bytes',
    'bytes1', 'bytes2', 'bytes4', 'bytes8', 'bytes16', 'bytes32',

    # Complex types
    'mapping', 'array',
})

# Storage and memory modifiers
SOLIDITY_STORAGE_MODIFIERS: FrozenSet[str] = frozenset({
    'memory', 'storage', 'calldata',
})

# Function visibility modifiers
SOLIDITY_VISIBILITY_MODIFIERS: FrozenSet[str] = frozenset({
    'public', 'private', 'internal', 'external',
})

# Function state mutability modifiers
SOLIDITY_MUTABILITY_MODIFIERS: FrozenSet[str] = frozenset({
    'view', 'pure', 'payable', 'constant', 'immutable',
})

# Built-in literals
SOLIDITY_LITERALS: FrozenSet[str] = frozenset({
    'true', 'false', 'null',
})

# Built-in global objects and their properties
SOLIDITY_GLOBAL_OBJECTS: FrozenSet[str] = frozenset({
    'this', 'super', 'msg', 'block', 'tx', 'now',  # 'now' is deprecated but still used
})

SOLIDITY_GLOBAL_PROPERTIES: FrozenSet[str] = frozenset({
    # msg properties
    'sender', 'value', 'data', 'sig', 'origin', 'gasprice',

    # block properties
    'timestamp', 'number', 'coinbase', 'difficulty', 'gaslimit', 'chainid',
    'basefee', 'prevrandao',

    # tx properties
    'origin', 'gasprice',
})

# Built-in functions (language level)
SOLIDITY_BUILTIN_FUNCTIONS: FrozenSet[str] = frozenset({
    # Error handling
    'require', 'assert', 'revert',

    # Cryptographic functions
    'keccak256', 'sha256', 'sha3', 'ripemd160', 'ecrecover',

    # Mathematical functions
    'addmod', 'mulmod',

    # Other builtins
    'gasleft', 'selfdestruct', 'blockhash',

    # ABI functions (these are actually abi.* but often seen without prefix)
    'encode', 'encodePacked', 'encodeWithSelector', 'encodeWithSignature', 'decode',
})

# Low-level call functions
SOLIDITY_LOW_LEVEL_CALLS: FrozenSet[str] = frozenset({
    'call', 'delegatecall', 'staticcall', 'send', 'transfer',
})

# Common ERC standard function names (these are NOT Solidity keywords but commonly filtered)
ERC_STANDARD_FUNCTIONS: FrozenSet[str] = frozenset({
    # ERC20
    'transfer', 'transferFrom', 'approve', 'allowance', 'balanceOf', 'totalSupply',
    'mint', 'burn', 'increaseAllowance', 'decreaseAllowance',

    # Safe versions
    'safeTransfer', 'safeTransferFrom', 'safeMint', 'safeBurn',

    # ERC721
    'ownerOf', 'tokenURI', 'setApprovalForAll', 'getApproved', 'isApprovedForAll',

    # Common extensions
    'pause', 'unpause', 'paused',
})

# Common ERC standard event names
ERC_STANDARD_EVENTS: FrozenSet[str] = frozenset({
    'Transfer', 'Approval', 'OwnershipTransferred', 'Paused', 'Unpaused',
    'Mint', 'Burn', 'TokenMinted', 'TokenBurned',
})

# All Solidity language keywords combined (for easy access)
ALL_SOLIDITY_KEYWORDS: FrozenSet[str] = frozenset(
    SOLIDITY_KEYWORDS |
    SOLIDITY_TYPES |
    SOLIDITY_STORAGE_MODIFIERS |
    SOLIDITY_VISIBILITY_MODIFIERS |
    SOLIDITY_MUTABILITY_MODIFIERS |
    SOLIDITY_LITERALS |
    SOLIDITY_GLOBAL_OBJECTS |
    SOLIDITY_GLOBAL_PROPERTIES |
    SOLIDITY_BUILTIN_FUNCTIONS |
    SOLIDITY_LOW_LEVEL_CALLS
)

def is_solidity_keyword(identifier: str) -> bool:
    """
    Check if an identifier is a Solidity language keyword.
    
    Args:
        identifier: The identifier to check
        
    Returns:
        True if the identifier is a Solidity keyword, False otherwise
    """
    return identifier in ALL_SOLIDITY_KEYWORDS or identifier.lower() in ALL_SOLIDITY_KEYWORDS

def is_likely_builtin_function(identifier: str) -> bool:
    """
    Check if an identifier is likely a Solidity built-in function.
    
    Args:
        identifier: The identifier to check
        
    Returns:
        True if the identifier is a built-in function, False otherwise
    """
    return identifier in SOLIDITY_BUILTIN_FUNCTIONS

def is_low_level_call(identifier: str) -> bool:
    """
    Check if an identifier represents a low-level call function.
    
    Args:
        identifier: The identifier to check
        
    Returns:
        True if the identifier is a low-level call, False otherwise
    """
    return identifier in SOLIDITY_LOW_LEVEL_CALLS

def is_erc_standard_identifier(identifier: str) -> bool:
    """
    Check if an identifier is a standard ERC function or event name.
    
    Args:
        identifier: The identifier to check
        
    Returns:
        True if the identifier is a standard ERC name, False otherwise
    """
    return identifier in ERC_STANDARD_FUNCTIONS or identifier in ERC_STANDARD_EVENTS
