# Sol-Query V2 API Reference

**SolidityQueryEngineV2** - Next-generation optimized interface with three powerful core methods.

## Overview

The V2 engine provides a streamlined, super-powerful interface with just three core methods that handle all query types:

1. **`query_code()`** - Universal query function for any Solidity construct
2. **`get_details()`** - Detailed element analysis with multiple depth levels
3. **`find_references()`** - Reference and relationship analysis with call graphs

This optimized design supports all security analysis patterns from advanced security frameworks while maintaining simplicity and high performance.

---

## Core Class

### SolidityQueryEngineV2

Main V2 query engine with optimized three-method interface.

#### Constructor

```python
SolidityQueryEngineV2(source_paths: Optional[Union[str, Path, List[Union[str, Path]]]] = None)
```

**Parameters:**
- `source_paths`: Optional path(s) to load initially
  - Single file: `"/path/to/contract.sol"`
  - Directory: `"/path/to/contracts"`
  - Multiple paths: `["/path/to/contract1.sol", "/path/to/contracts_dir"]`

**Example:**
```python
from sol_query.query.engine_v2 import SolidityQueryEngineV2

# Initialize with sources
engine = SolidityQueryEngineV2("/path/to/contracts")

# Initialize empty, load sources later
engine = SolidityQueryEngineV2()
engine.load_sources(["/path/to/contract1.sol", "/path/to/contract2.sol"])
```

#### Load Sources

```python
load_sources(source_paths: Union[str, Path, List[Union[str, Path]]]) -> None
```

Load additional source files or directories.

**Parameters:**
- `source_paths`: Path(s) to load (files, directories, or lists)

**Example:**
```python
# Load single file
engine.load_sources("MyToken.sol")

# Load directory recursively
engine.load_sources("/path/to/contracts")

# Load multiple sources
engine.load_sources([
    "contracts/Token.sol",
    "contracts/interfaces/",
    "/path/to/external/libs"
])
```

---

## Core Methods

### 1. query_code()

**Universal query function** - handles any Solidity construct with advanced filtering.

```python
query_code(
    query_type: str,
    filters: Dict[str, Any] = {},
    scope: Dict[str, Any] = {},
    include: List[str] = [],
    options: Dict[str, Any] = {}
) -> Dict[str, Any]
```

#### Parameters

**`query_type`** *(string, required)*
The type of Solidity construct to query:

| Query Type | Description | Example Use Case |
|------------|-------------|------------------|
| `"functions"` | Function declarations | Find external functions |
| `"contracts"` | Contract declarations | Find token contracts |
| `"variables"` | Variable declarations | Find state variables |
| `"calls"` | Function calls | Find external calls |
| `"statements"` | Statement nodes | Find require statements |
| `"expressions"` | Expression nodes | Find arithmetic operations |
| `"events"` | Event declarations | Find Transfer events |
| `"modifiers"` | Modifier declarations | Find access control modifiers |
| `"errors"` | Error declarations | Find custom errors |
| `"structs"` | Struct declarations | Find data structures |
| `"enums"` | Enum declarations | Find enumeration types |

**`filters`** *(dict, optional)*
Advanced filtering criteria:

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `names` | `str\|List[str]` | Name patterns (wildcards/regex) | `["transfer*", "approve"]` |
| `visibility` | `str\|List[str]` | Function/variable visibility | `["public", "external"]` |
| `state_mutability` | `str\|List[str]` | Function state mutability | `["view", "pure"]` |
| `modifiers` | `str\|List[str]` | Applied modifiers | `["onlyOwner", "validAddress"]` |
| `contracts` | `str\|List[str]` | Contract name patterns | `["*Token*", "MyContract"]` |
| `types` | `str\|List[str]` | Variable type patterns | `["uint256", "mapping*"]` |
| `has_external_calls` | `bool` | Functions with external calls | `True` |
| `has_asset_transfers` | `bool` | Functions with asset transfers | `True` |
| `changes_state` | `bool` | Functions that modify state | `True` |
| `is_payable` | `bool` | Payable functions | `True` |
| `is_state_variable` | `bool` | State vs local variables | `True` |
| `statement_types` | `List[str]` | Types of statements | `["if", "for", "require"]` |
| `operators` | `List[str]` | Expression operators | `["+", "*", "=="]` |
| `call_types` | `List[str]` | Types of calls | `["external", "low_level"]` |
| `low_level` | `bool` | Low-level calls (call/delegatecall) | `True` |
| `access_patterns` | `List[str]` | Variable access patterns | `["read", "write"]` |
| `field_patterns` | `List[str]` | Field pattern matching | `["msg.sender", "balance"]` |

**`scope`** *(dict, optional)*
Limit search scope:

| Scope | Type | Description | Example |
|-------|------|-------------|---------|
| `contracts` | `List[str]` | Specific contracts only | `["Token", "Vault"]` |
| `functions` | `List[str]` | Specific functions only | `["transfer", "withdraw"]` |
| `files` | `List[str]` | File path patterns | `["*.sol", "/contracts/*"]` |
| `directories` | `List[str]` | Directory patterns | `["/contracts", "/libs"]` |
| `inheritance_tree` | `str` | Contracts inheriting from base | `"ERC20"` |

**`include`** *(list, optional)*
Additional data to include in results:

| Include Option | Description |
|----------------|-------------|
| `"source"` | Source code text |
| `"ast"` | AST information |
| `"calls"` | Function calls made |
| `"callers"` | Functions that call this |
| `"variables"` | Variables accessed |
| `"events"` | Events emitted |
| `"modifiers"` | Applied modifiers |
| `"natspec"` | Documentation |
| `"dependencies"` | Code dependencies |
| `"inheritance"` | Inheritance details |

**`options`** *(dict, optional)*
Query processing options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `max_results` | `int` | Maximum results to return | `None` (unlimited) |
| `case_sensitive` | `bool` | Case-sensitive pattern matching | `True` |
| `regex_enabled` | `bool` | Enable regex in patterns | `True` |

#### Return Value

Returns a standardized response dictionary:

```python
{
    "success": bool,                    # Query success status
    "query_info": {
        "function": "query_code",       # Called function name
        "parameters": {...},            # Parameters used
        "execution_time": float,        # Execution time in seconds
        "result_count": int,            # Number of results
        "cache_hit": bool               # Whether cache was used
    },
    "data": {
        "results": [...],               # Array of matching elements
        "summary": {                    # Result summary statistics
            "total_count": int,
            "by_type": {...},           # Results by type
            "by_contract": {...},       # Results by contract
            "by_visibility": {...}      # Results by visibility
        }
    },
    "metadata": {
        "analysis_scope": {...},        # Scope applied
        "filters_applied": {...},       # Filters used
        "performance": {...}            # Performance metrics
    },
    "warnings": [],                     # Any warnings
    "errors": []                        # Any errors
}
```

#### Examples

**Basic Function Query:**
```python
# Find all external functions
result = engine.query_code("functions", {
    "visibility": "external"
})

print(f"Found {result['data']['summary']['total_count']} external functions")
for func in result['data']['results']:
    print(f"- {func['name']} in {func['location']['contract']}")
```

**Security Analysis - Reentrancy Detection:**
```python
# Find functions with external calls that change state
result = engine.query_code("functions", {
    "has_external_calls": True,
    "changes_state": True
}, include=["source", "calls"])

print("Potential reentrancy vulnerabilities:")
for func in result['data']['results']:
    print(f"- {func['location']['contract']}.{func['name']}")
    print(f"  External calls: {len(func['calls'])}")
```

**Complex Token Analysis:**
```python
# Find token transfer functions with comprehensive analysis
result = engine.query_code("functions", {
    "names": ["transfer*", "send*", "*Transfer*"],
    "visibility": ["public", "external"],
    "has_asset_transfers": True
}, scope={
    "contracts": ["*Token*", "*ERC*"]
}, include=["source", "calls", "variables", "modifiers"])

for func in result['data']['results']:
    print(f"Transfer function: {func['name']}")
    print(f"  Modifiers: {func.get('modifiers', [])}")
    print(f"  Variables accessed: {len(func.get('variables', []))}")
```

**Advanced Pattern Matching:**
```python
# Find all require statements with specific patterns
result = engine.query_code("statements", {
    "statement_types": ["require"],
    "access_patterns": ["msg.sender", "owner"]
})

print("Access control patterns found:")
for stmt in result['data']['results']:
    print(f"- {stmt['location']['contract']}: Line {stmt['location']['line']}")
```

---

### 2. get_details()

**Detailed element analysis** - provides comprehensive information about specific elements.

```python
get_details(
    element_type: str,
    identifiers: List[str],
    include_context: bool = True,
    options: Dict[str, Any] = {}
) -> Dict[str, Any]
```

#### Parameters

**`element_type`** *(string, required)*
Type of element to analyze:

| Element Type | Description | Example |
|--------------|-------------|---------|
| `"function"` | Function declarations | Analyze `transfer` function |
| `"contract"` | Contract declarations | Analyze `MyToken` contract |
| `"variable"` | Variable declarations | Analyze `_balances` state variable |
| `"modifier"` | Modifier declarations | Analyze `onlyOwner` modifier |
| `"event"` | Event declarations | Analyze `Transfer` event |
| `"error"` | Error declarations | Analyze `InsufficientBalance` error |
| `"struct"` | Struct declarations | Analyze `UserData` struct |
| `"enum"` | Enum declarations | Analyze `TokenState` enum |

**`identifiers`** *(List[string], required)*
List of element identifiers to analyze. Supports multiple formats:
- Simple names: `["transfer", "balanceOf"]`
- Function signatures: `["transfer(address,uint256)", "approve(address,uint256)"]`
- Contract.element format: `["Token.transfer", "Vault.withdraw"]`
- File:contract format: `["contracts/Token.sol:MyToken"]`

**`include_context`** *(boolean, optional, default: True)*
Whether to include surrounding context and relationships.

**`options`** *(dict, optional)*
Analysis options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `include_source` | `bool` | Include source code | `True` |
| `show_call_chains` | `bool` | Show call relationship chains (expensive) | `False` |
| `max_context_lines` | `int` | Lines of context to include | `5` |
| `include_signatures` | `bool` | Include function signatures | `True` |
| `include_natspec` | `bool` | Include NatSpec documentation | `True` |
| `include_modifiers` | `bool` | Include modifier information | `True` |
| `resolve_inheritance` | `bool` | Resolve inherited elements | `False` |

#### Return Value

```python
{
    "success": bool,
    "query_info": {
        "function": "get_details",
        "parameters": {...},
        "execution_time": float,
        "result_count": int
    },
    "data": {
        "elements": {
            "identifier1": {
                "found": bool,
                "element_info": {...},       # Element details
                "context": {...}            # If include_context=True
            },
            "identifier2": {...}
        },
        "analysis_summary": {
            "elements_found": int,
            "features_analyzed": [...],
            "success_rate": float
        }
    },
    "metadata": {
        "analysis_scope": {...},
        "performance": {...}
    },
    "warnings": [],
    "errors": []
}
```

#### Examples

**Basic Function Analysis:**
```python
# Analyze transfer functions
result = engine.get_details("function", ["transfer", "transferFrom"])

for name, analysis in result['data']['elements'].items():
    if analysis['found']:
        info = analysis['element_info']
        print(f"{name}: {info['signature']} at {info['location']['file']}:{info['location']['line']}")
```

**Detailed Contract Analysis:**
```python
# Deep analysis of a token contract
result = engine.get_details("contract", ["MyToken"], include_context=True)

contract_info = result['data']['elements']['MyToken']
if contract_info['found']:
    element_info = contract_info['element_info']

    print(f"Contract: {element_info['name']}")
    print(f"Type: {element_info['type']}")
    print(f"Functions: {len(element_info.get('functions', []))}")
    print(f"State Variables: {len(element_info.get('variables', []))}")
```

**Comprehensive Security Analysis:**
```python
# Security analysis of critical functions
result = engine.get_details("function",
    ["withdraw", "emergencyWithdraw", "claim"],
    options={"show_call_chains": True})

for name, analysis in result['data']['elements'].items():
    if analysis['found']:
        element_info = analysis['element_info']
        print(f"{name} details:")
        print(f"  Location: {element_info['location']}")
        print(f"  Signature: {element_info.get('signature', 'N/A')}")
        print(f"  Visibility: {element_info.get('visibility', 'N/A')}")
```

**Variable State Analysis:**
```python
# Analyze state variables and their usage
result = engine.get_details("variable",
    ["_balances", "totalSupply", "owner"])

for name, analysis in result['data']['elements'].items():
    if analysis['found']:
        element_info = analysis['element_info']
        print(f"{name}:")
        print(f"  Type: {element_info.get('type', 'N/A')}")
        print(f"  Visibility: {element_info.get('visibility', 'N/A')}")
        print(f"  Location: {element_info['location']}")
```

---

### 3. find_references()

**Reference and relationship analysis** - traces references, usages, and call relationships.

```python
find_references(
    target: str,
    target_type: str,
    reference_type: str = "all",
    direction: str = "both",
    max_depth: int = 5,
    filters: Dict[str, Any] = {},
    options: Dict[str, Any] = {}
) -> Dict[str, Any]
```

#### Parameters

**`target`** *(string, required)*
The target element to analyze references for:
- Function names: `"transfer"`, `"withdraw"`
- Variable names: `"balances"`, `"totalSupply"`
- Contract names: `"MyToken"`, `"Vault"`
- Signatures: `"transfer(address,uint256)"`

**`target_type`** *(string, required)*
Type of the target element:

| Target Type | Description | Use Case |
|-------------|-------------|----------|
| `"function"` | Function declarations | Find function call sites |
| `"variable"` | Variable declarations | Find variable usage |
| `"contract"` | Contract declarations | Find contract instantiation |
| `"modifier"` | Modifier declarations | Find modifier applications |
| `"event"` | Event declarations | Find event emissions |
| `"struct"` | Struct declarations | Find struct usage |
| `"enum"` | Enum declarations | Find enum value usage |

**`reference_type`** *(string, optional, default: "all")*
Type of references to find:

| Reference Type | Description |
|----------------|-------------|
| `"all"` | All references (usages + definitions) |
| `"usages"` | Usage sites only |
| `"definitions"` | Definition sites only |

**`direction`** *(string, optional, default: "both")*
Analysis direction:

| Direction | Description |
|-----------|-------------|
| `"forward"` | Find what this element calls/uses |
| `"backward"` | Find what calls/uses this element |
| `"both"` | Bidirectional analysis |

**`max_depth`** *(integer, optional, default: 5)*
Maximum search depth:
- `1`: Direct references only
- `2+`: Multi-level reference chains
- Higher values: Deeper reference chains

**`filters`** *(dict, optional)*
Filter found references:

| Filter | Type | Description |
|--------|------|-------------|
| `contracts` | `List[str]` | Limit to specific contracts |
| `files` | `List[str]` | Limit to file patterns |
| `visibility` | `List[str]` | Function visibility filter |
| `exclude_self` | `bool` | Exclude self-references |

**`options`** *(dict, optional)*
Analysis options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `show_call_chains` | `bool` | Build complete call chains | `False` |
| `include_context` | `bool` | Include usage context | `True` |
| `max_results_per_type` | `int` | Limit results per reference type | `100` |

#### Return Value

```python
{
    "success": bool,
    "query_info": {
        "function": "find_references",
        "parameters": {...},
        "execution_time": float
    },
    "data": {
        "references": {
            "usages": [                  # Usage sites
                {
                    "location": {...},   # File, line, column
                    "usage_type": str,   # "function_call", "variable_read", etc.
                    "context": str,      # Source code context
                    "node_type": str,    # AST node type
                    "source_snippet": str
                }
            ],
            "definitions": [             # Definition sites
                {
                    "location": {...},
                    "definition_type": str, # "primary", "override", "interface"
                    "context": str,
                    "element_type": str
                }
            ],
            "call_chains": [             # If show_call_chains=True
                ["element1", "element2", "element3"]  # Call sequence
            ]
        },
        "summary": {
            "total_references": int,
            "usages_found": int,
            "definitions_found": int,
            "max_depth_reached": int
        }
    },
    "metadata": {
        "target_info": {
            "name": str,
            "type": str,
            "location": {...}
        },
        "analysis_scope": {...},
        "performance": {
            "references_found": int,
            "depth_reached": int,
            "files_analyzed": int
        }
    },
    "warnings": [],
    "errors": []
}
```

#### Examples

**Function Usage Analysis:**
```python
# Find all places where 'transfer' function is called
result = engine.find_references("transfer", "function",
                               reference_type="usages")

if result['success']:
    usages = result['data']['references']['usages']
    print(f"Found {len(usages)} usages of transfer function:")

    for usage in usages:
        loc = usage['location']
        print(f"- {loc['contract']}.{loc['function']} at line {loc['line']}")
        print(f"  Context: {usage['context'][:100]}...")
```

**Variable Reference Tracking:**
```python
# Track all references to 'totalSupply' variable
result = engine.find_references("totalSupply", "variable",
                               reference_type="all",
                               direction="both",
                               filters={"contracts": ["MyToken"]})

refs = result['data']['references']
print(f"Total references to totalSupply: {result['data']['summary']['total_references']}")
print(f"Usages: {len(refs['usages'])}")
print(f"Definitions: {len(refs['definitions'])}")

for usage in refs['usages']:
    print(f"Used in: {usage['location']['contract']} ({usage['usage_type']})")
```

**Call Chain Analysis:**
```python
# Analyze complete call chains from critical functions
result = engine.find_references("emergencyWithdraw", "function",
                               direction="both",
                               max_depth=3,
                               options={"show_call_chains": True})

if result['success']:
    chains = result['data']['references']['call_chains']
    print(f"Found {len(chains)} call chains:")

    for i, chain in enumerate(chains):
        print(f"Chain {i+1}: {' -> '.join(chain)}")
```

**Cross-Contract Reference Analysis:**
```python
# Find references across contract boundaries
result = engine.find_references("IERC20", "contract",
                               reference_type="usages",
                               direction="forward")

if result['success']:
    usages = result['data']['references']['usages']
    contracts_using = set()

    for usage in usages:
        contracts_using.add(usage['location']['contract'])

    print(f"IERC20 interface used by {len(contracts_using)} contracts:")
    for contract in contracts_using:
        print(f"- {contract}")
```

**Advanced Security Call Analysis:**
```python
# Find all external calls and their complete call chains
external_funcs = engine.query_code("functions", {
    "has_external_calls": True
})['data']['results']

for func in external_funcs[:5]:  # Analyze first 5 functions
    result = engine.find_references(func['name'], "function",
                                   direction="forward",
                                   max_depth=2,
                                   options={"show_call_chains": True})

    if result['success']:
        chains = result['data']['references']['call_chains']
        print(f"External call chains from {func['name']}:")
        for chain in chains:
            print(f"  {' -> '.join(chain)}")
```

---

## Error Handling

All methods return standardized error responses when issues occur:

### Common Error Types

| Error Type | Description | Solution |
|------------|-------------|----------|
| **Validation Error** | Invalid parameters | Check parameter values and types |
| **Parse Error** | Solidity syntax errors | Fix source code syntax |
| **Not Found Error** | Element not found | Verify element names and types |
| **Timeout Error** | Query too complex | Reduce scope or add filters |

### Error Response Format

```python
{
    "success": False,
    "query_info": {
        "function": str,              # Which method failed
        "parameters": {...},          # Parameters used
        "validation_errors": [...]    # Detailed validation errors
    },
    "data": None,
    "errors": [...]                   # Error messages
}
```

### Example Error Handling

```python
result = engine.query_code("invalid_type", {})

if not result['success']:
    print("Query failed:")
    for error in result['errors']:
        print(f"- {error}")
```
