# Sol-Query Documentation

Complete documentation for the Sol-Query Solidity code analysis engine.

## Documentation Structure

### 📚 [API Reference](api-reference.md)
**COMPREHENSIVE** reference for all classes, methods, and enums.

**What's Included:**
- Complete method signatures with all parameters
- All enum values and their meanings
- Code examples for every major feature
- Pattern matching syntax and options
- Data flow analysis methods
- Import analysis capabilities
- Serialization options

**Quick Navigation:**
- [SolidityQueryEngine](api-reference.md#solidityqueryengine) - Main entry point
- [Collection Classes](api-reference.md#collection-classes) - Fluent API
- [AST Node Classes](api-reference.md#ast-node-classes) - Core data structures
- [Enums and Constants](api-reference.md#enums-and-constants) - All possible values
- [Advanced Features](api-reference.md#advanced-features) - Data flow, imports, composition

### 🏗️ [Architecture Overview](architecture.md)
Deep dive into the system design and component architecture.

**Key Topics:**
- System overview and component interaction
- AST node hierarchy and relationships
- Analysis modules (call, data flow, import)
- Query processing pipeline
- Design principles and patterns
- Performance characteristics
- Extensibility points

## Quick Start Guide

### Installation
```bash
pip install sol-query
```

### Basic Usage
```python
from sol_query import SolidityQueryEngine

# Load and analyze contracts
engine = SolidityQueryEngine("path/to/contracts")

# Traditional API
contracts = engine.find_contracts(name_patterns="*Token*")
external_funcs = engine.find_functions(visibility="external")

# Fluent API
dangerous_funcs = (engine.contracts
                   .with_name("*")
                   .functions
                   .external()
                   .with_external_calls()
                   .payable())

# Analysis
call_graph = engine.analyze_call_graph()
flow_paths = engine.trace_variable_flow("balance", "transfer")
```

## Key Features

### 🔍 **Comprehensive Querying**
- Traditional functional API for straightforward queries
- Fluent object-oriented API for complex compositions
- Pattern matching with wildcards and regex
- Set operations (union, intersection, difference)

### 🌊 **Advanced Analysis**
- **Call Graph Analysis**: External calls, asset transfers, call chains
- **Data Flow Analysis**: Variable tracking, influence analysis, flow paths
- **Import Analysis**: Dependency graphs, symbol usage, library detection
- **Pattern Matching**: Flexible search with multiple pattern types

### 🎯 **Precise Filtering**
- Function visibility (public, private, internal, external)
- State mutability (pure, view, payable, nonpayable)
- Contract types (interface, library, abstract)
- Call types (external, internal, low-level, library)
- Statement types (loops, conditionals, assignments)

### 📊 **Rich Metadata**
- Complete source location tracking
- Type-safe AST representation
- Contextual analysis for accuracy
- JSON serialization support

## Use Cases

### 🔒 **Security Analysis**
```python
# Find functions with external calls and asset transfers
risky_functions = (engine.functions
                   .with_external_calls()
                   .with_asset_transfers()
                   .payable())

# Analyze call patterns
external_calls = engine.find_external_calls()
low_level_calls = engine.find_calls(call_types=["low_level"])
```

### 🔄 **Code Migration**
```python
# Find usage of deprecated patterns
old_patterns = engine.expressions.with_source_pattern("*.transfer(*)")
library_usage = engine.find_import_usage("*SafeMath*")

# Analyze inheritance structures
token_contracts = engine.contracts.inheriting_from(["ERC20", "ERC721"])
```

### 📈 **Code Quality**
```python
# Find complex functions
complex_functions = engine.functions.where(
    lambda f: len(f.parameters) > 5 and not f.is_view()
)

# Analyze variable usage
unused_vars = engine.variables.where(
    lambda v: len(v.get_all_references()) == 0
)
```

### 🔬 **Research and Analysis**
```python
# Statistical analysis
stats = engine.get_statistics()
patterns = engine.analyze_patterns()

# Custom analysis with data flow
for func in engine.functions.external():
    flow = engine.trace_variable_flow("msg.value", func.name)
    # Analyze flow patterns...
```

## Advanced Usage

### Query Composition
```python
# Complex filtering with boolean logic
target_functions = (engine.contracts
                    .interfaces()
                    .union(engine.contracts.with_name("*Proxy*"))
                    .functions
                    .external()
                    .and_not(lambda f: f.is_view()))

# Set operations
safe_contracts = all_contracts.subtract(risky_contracts)
```

### Custom Analysis
```python
# Custom predicates
def has_complex_logic(function):
    statements = engine.find_statements(function_name=function.name)
    return len(statements.loops()) > 2 or len(statements.conditionals()) > 5

complex_functions = engine.functions.where(has_complex_logic)
```

### Data Export
```python
from sol_query.utils.serialization import LLMSerializer, SerializationLevel

# Export for further analysis
serializer = LLMSerializer(SerializationLevel.DETAILED)
data = serializer.serialize_collection(engine.contracts)

# Save to file
import json
with open("analysis.json", "w") as f:
    json.dump(data, f, indent=2)
```

## Performance Tips

1. **Use Specific Patterns**: `"MyContract"` is faster than `"*Contract*"`
2. **Filter Early**: Apply restrictive filters first in chains
3. **Cache Results**: Store engine instances for repeated queries
4. **Shallow Analysis**: Use `deep=False` when possible
5. **Monitor Memory**: Use `get_statistics()` to track usage

## Getting Help

### Documentation
- [API Reference](api-reference.md) - Complete method reference
- [Architecture](architecture.md) - System design details

### Examples
All major features include working code examples in the API reference.

### Common Patterns
The API reference includes sections on:
- Query composition techniques
- Pattern matching strategies  
- Data flow analysis workflows
- Import dependency analysis
- Performance optimization

### Error Handling
Sol-Query provides comprehensive error handling:
- Parse errors with location information
- Graceful handling of malformed code
- Type validation and helpful error messages
- Timeout protection for complex queries

---

For the most up-to-date API reference and examples, see [api-reference.md](api-reference.md).