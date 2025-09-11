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
| `"flow"` | Control flow elements | Find loops and branches |

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
    "errors": [],                       # Any errors
    "suggestions": [],                  # Query optimization suggestions
    "related_queries": []               # Related query suggestions
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
    analysis_depth: str = "basic",
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

**`analysis_depth`** *(string, optional, default: "basic")*
Level of analysis to perform:

| Depth | Description | Includes |
|-------|-------------|----------|
| `"basic"` | Essential information | Name, type, location, signature |
| `"detailed"` | Comprehensive details | + source code, visibility, modifiers, types |
| `"comprehensive"` | Full analysis | + dependencies, call graphs, data flow, security analysis |

**`include_context`** *(boolean, optional, default: True)*
Whether to include surrounding context and relationships.

**`options`** *(dict, optional)*
Analysis options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `include_source` | `bool` | Include source code | `True` |
| `show_call_chains` | `bool` | Show call relationship chains | `False` |
| `max_context_lines` | `int` | Lines of context to include | `5` |
| `include_signatures` | `bool` | Include function signatures | `True` |

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
                "basic_info": {...},         # Always included
                "detailed_info": {...},     # If depth >= "detailed"  
                "comprehensive_info": {...}, # If depth == "comprehensive"
                "context": {...}            # If include_context=True
            },
            "identifier2": {...}
        },
        "analysis_summary": {
            "elements_found": int,
            "analysis_depth": str,
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
# Analyze transfer functions at basic level
result = engine.get_details("function", ["transfer", "transferFrom"], 
                           analysis_depth="basic")

for name, analysis in result['data']['elements'].items():
    if analysis['found']:
        info = analysis['basic_info']
        print(f"{name}: {info['signature']} at {info['location']['file']}:{info['location']['line']}")
```

**Detailed Contract Analysis:**
```python
# Deep analysis of a token contract
result = engine.get_details("contract", ["MyToken"], 
                           analysis_depth="detailed",
                           include_context=True)

contract_info = result['data']['elements']['MyToken']
if contract_info['found']:
    basic = contract_info['basic_info']
    detailed = contract_info['detailed_info']
    
    print(f"Contract: {basic['name']}")
    print(f"Type: {basic['type']}")
    print(f"Functions: {len(detailed.get('functions', []))}")
    print(f"State Variables: {len(detailed.get('variables', []))}")
```

**Comprehensive Security Analysis:**
```python
# Full security analysis of critical functions
result = engine.get_details("function", 
    ["withdraw", "emergencyWithdraw", "claim"],
    analysis_depth="comprehensive",
    options={"show_call_chains": True})

for name, analysis in result['data']['elements'].items():
    if analysis['found']:
        security = analysis['comprehensive_info']['security_analysis']
        print(f"{name} security risks:")
        print(f"  Risk level: {security['risk_level']}")
        print(f"  Issues found: {len(security['issues'])}")
        for issue in security['issues']:
            print(f"    - {issue['type']}: {issue['severity']}")
```

**Variable State Analysis:**
```python
# Analyze state variables and their usage
result = engine.get_details("variable", 
    ["_balances", "totalSupply", "owner"],
    analysis_depth="comprehensive")

for name, analysis in result['data']['elements'].items():
    if analysis['found']:
        data_flow = analysis['comprehensive_info']['data_flow']
        print(f"{name}:")
        print(f"  Read by: {data_flow['variables_read']}")
        print(f"  Written by: {data_flow['variables_written']}")
        print(f"  State changes: {data_flow['state_changes']}")
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
    max_depth: int = -1,
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

**`max_depth`** *(integer, optional, default: -1)*
Maximum search depth:
- `-1`: Unlimited depth (follows all chains)
- `1`: Direct references only
- `2+`: Multi-level reference chains

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
    "errors": [...],                  # Error messages
    "suggestions": [...]              # Fix suggestions
}
```

### Example Error Handling

```python
result = engine.query_code("invalid_type", {})

if not result['success']:
    print("Query failed:")
    for error in result['errors']:
        print(f"- {error}")
    
    print("Suggestions:")
    for suggestion in result['suggestions']:
        print(f"- {suggestion}")
```

---

## Performance Optimization

### Best Practices

1. **Use Specific Filters Early:**
   ```python
   # Good: Specific contract filter first
   engine.query_code("functions", {"contracts": ["MyToken"]})
   
   # Less efficient: Broad search then filter
   engine.query_code("functions", {})  # Then manually filter results
   ```

2. **Limit Results:**
   ```python
   # For exploration, limit results
   result = engine.query_code("functions", {}, 
                             options={"max_results": 50})
   ```

3. **Choose Appropriate Analysis Depth:**
   ```python
   # Use "basic" when you only need names and locations
   engine.get_details("function", ["transfer"], analysis_depth="basic")
   
   # Use "comprehensive" only when you need full analysis
   engine.get_details("function", ["withdraw"], analysis_depth="comprehensive")
   ```

4. **Scope Queries Effectively:**
   ```python
   # Limit scope to relevant contracts
   engine.query_code("functions", 
                     {"has_external_calls": True},
                     scope={"contracts": ["*Token*", "*Vault*"]})
   ```

### Performance Monitoring

Monitor query performance using the returned metadata:

```python
result = engine.query_code("functions", {"visibility": "external"})

perf = result['metadata']['performance']
print(f"Query took {result['query_info']['execution_time']:.3f}s")
print(f"Found {perf['total_results']} results")
print(f"Analyzed {perf['files_processed']} files")
```

---

## Security Analysis Patterns

The V2 API is optimized for security analysis workflows. Here are common patterns:

### Reentrancy Detection

```python
# Find functions vulnerable to reentrancy
result = engine.query_code("functions", {
    "has_external_calls": True,
    "changes_state": True,
    "visibility": ["public", "external"]
}, include=["source", "calls"])

for func in result['data']['results']:
    # Analyze each function for reentrancy patterns
    details = engine.get_details("function", [func['name']], 
                                analysis_depth="comprehensive")
    
    security = details['data']['elements'][func['name']]['comprehensive_info']['security_analysis']
    if security['risk_level'] == 'high':
        print(f"High risk: {func['location']['contract']}.{func['name']}")
```

### Access Control Analysis

```python
# Find public/external functions without access control
result = engine.query_code("functions", {
    "visibility": ["public", "external"],
    "modifiers": []  # No modifiers
})

unprotected = result['data']['results']
print(f"Found {len(unprotected)} unprotected functions")
```

### Asset Flow Analysis

```python
# Trace asset transfers through the system
transfer_funcs = engine.query_code("functions", {
    "has_asset_transfers": True
})['data']['results']

for func in transfer_funcs:
    # Find what calls this transfer function
    refs = engine.find_references(func['name'], "function", 
                                 reference_type="usages")
    
    print(f"{func['name']} called by {len(refs['data']['references']['usages'])} functions")
```

---

## Integration Examples

### Export for Analysis Tools

```python
# Export comprehensive analysis for external tools
functions = engine.query_code("functions", 
                              {"visibility": ["public", "external"]},
                              include=["source", "calls", "variables"])

# Format for security analysis tools
security_data = []
for func in functions['data']['results']:
    details = engine.get_details("function", [func['name']], 
                                analysis_depth="comprehensive")
    
    if details['success']:
        func_details = details['data']['elements'][func['name']]
        security_data.append({
            'name': func['name'],
            'contract': func['location']['contract'],
            'signature': func.get('signature', ''),
            'risks': func_details['comprehensive_info']['security_analysis']['issues'],
            'external_calls': len(func.get('calls', [])),
            'source': func.get('source_code', '')
        })

# Export to JSON
import json
with open('security_analysis.json', 'w') as f:
    json.dump(security_data, f, indent=2)
```

### Custom Analysis Pipeline

```python
def analyze_contract_security(engine, contract_name):
    """Complete security analysis pipeline for a contract."""
    
    # Step 1: Get all functions in the contract
    functions = engine.query_code("functions", {
        "contracts": [contract_name],
        "visibility": ["public", "external"]
    })
    
    # Step 2: Analyze each function in detail
    func_names = [f['name'] for f in functions['data']['results']]
    details = engine.get_details("function", func_names,
                                analysis_depth="comprehensive")
    
    # Step 3: Find cross-function references
    call_graph = {}
    for func_name in func_names:
        refs = engine.find_references(func_name, "function",
                                     direction="both",
                                     options={"show_call_chains": True})
        call_graph[func_name] = refs['data']['references']
    
    # Step 4: Compile security report
    security_report = {
        'contract': contract_name,
        'total_functions': len(func_names),
        'high_risk_functions': [],
        'call_graph': call_graph,
        'recommendations': []
    }
    
    for func_name, analysis in details['data']['elements'].items():
        if analysis['found']:
            security = analysis['comprehensive_info']['security_analysis']
            if security['risk_level'] == 'high':
                security_report['high_risk_functions'].append({
                    'name': func_name,
                    'issues': security['issues'],
                    'recommendations': security['recommendations']
                })
    
    return security_report

# Usage
report = analyze_contract_security(engine, "MyToken")
print(f"Security analysis for {report['contract']}:")
print(f"High risk functions: {len(report['high_risk_functions'])}")
```

---

## Version Compatibility

The V2 API is designed to coexist with the V1 traditional/fluent APIs:

```python
# V1 Traditional API
from sol_query import SolidityQueryEngine
v1_engine = SolidityQueryEngine("contracts/")
contracts = v1_engine.find_contracts(name_patterns="*Token*")

# V2 Optimized API  
from sol_query.query.engine_v2 import SolidityQueryEngineV2
v2_engine = SolidityQueryEngineV2("contracts/")
result = v2_engine.query_code("contracts", {"names": ["*Token*"]})

# Both can load the same sources and provide equivalent results
# Choose based on your use case:
# - V1 for traditional workflows and fluent chaining
# - V2 for performance, security analysis, and advanced filtering
```

The V2 API provides the same core functionality as V1 but with:
- **Better Performance**: Optimized three-method interface
- **Enhanced Security**: Built-in security analysis patterns  
- **Standardized Responses**: Consistent response format
- **Advanced Filtering**: More powerful filtering capabilities
- **Comprehensive Analysis**: Multi-level analysis depths

Choose V2 for new projects requiring advanced security analysis and high performance.