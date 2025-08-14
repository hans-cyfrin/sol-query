# Sol-Query: Powerful Solidity Code Analysis Engine

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Coverage](https://img.shields.io/badge/coverage-44%25-yellow.svg)

A comprehensive Python-based query engine for Solidity smart contracts that provides both traditional and fluent query interfaces. Designed specifically for LLM integration with full JSON serialization support.

## Documentation

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api-reference.md)
- [Query Examples](docs/query-examples.md)
- [Architecture Overview](docs/architecture.md)
- [Development Guide](docs/development.md)

## Features

### Unified Query Interface
- **Traditional Style**: `engine.find_functions(visibility="public")`
- **Fluent Style**: `engine.functions.public().view()`
- **Seamless Integration**: Mix and match both styles in the same query

### Comprehensive Analysis
- **Contract Discovery**: Find contracts by name, inheritance, type (interface/library)
- **Function Analysis**: Query by visibility, modifiers, state mutability, parameters
- **Variable Inspection**: Search state variables, locals, constants, and immutables
- **Event & Error Tracking**: Locate events and custom errors with parameter analysis
- **Modifier Detection**: Find and analyze function modifiers
- **External Call Detection**: Identify functions making external contract calls
- **Asset Transfer Analysis**: Find ETH sends, token transfers, and asset movements
- **Deep Call Tree Analysis**: Trace external calls and transfers through function chains

### Advanced Pattern Matching
- **Wildcard Support**: `"transfer*"` matches `transfer`, `transferFrom`, `transferOwnership`
- **Regex Patterns**: Full regular expression support for complex searches
- **Type Matching**: Smart Solidity type matching including arrays and mappings
- **Multiple Patterns**: OR/AND logic for complex filtering conditions

### LLM-Ready JSON Serialization
- **Configurable Detail Levels**: Summary, Detailed, Full
- **Pagination Support**: Handle large result sets efficiently
- **Complete Metadata**: Source locations, signatures, relationships
- **Tool-Call Compatible**: Perfect for LLM framework integration

### Robust Parsing
- **Tree-sitter Based**: Handles malformed/incomplete code gracefully
- **Source Management**: Multi-file projects with dependency tracking
- **Incremental Parsing**: Efficient updates for large codebases
- **Error Recovery**: Continues analysis despite parse errors

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd sol-query

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Quick Start

```python
from sol_query import SolidityQueryEngine

# Initialize engine
engine = SolidityQueryEngine()

# Load Solidity files
engine.load_sources("path/to/contracts")  # Directory
engine.load_sources("contract.sol")       # Single file
engine.load_sources(["file1.sol", "file2.sol"])  # Multiple files

# Traditional queries
contracts = engine.find_contracts(name_patterns="Token*")
public_functions = engine.find_functions(visibility="public")
events = engine.find_events(name_patterns="Transfer")

# Fluent queries
external_functions = engine.functions.external()
token_contract = engine.contracts.with_name("Token").first()
view_functions = engine.functions.view().public()

# Chain multiple filters
payable_external = engine.functions.external().payable()
owner_functions = engine.functions.with_modifiers("onlyOwner")

# External call and asset transfer analysis
functions_with_external_calls = engine.functions.with_external_calls()
functions_with_asset_transfers = engine.functions.with_asset_transfers()
deep_external_calls = engine.functions.with_external_calls_deep()

# Navigation
token_functions = engine.contracts.with_name("Token").get_functions()
mapping_vars = engine.variables.with_type("mapping*")
```

## Example Usage

Run the example script to see the engine in action:

```bash
uv run python example.py
```

This demonstrates:
- Loading and analyzing Solidity contracts
- Both traditional and fluent query styles
- Pattern matching capabilities
- JSON serialization for LLM integration
- Navigation between code elements

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_basic_functionality.py

# Run with coverage
uv run pytest --cov=sol_query --cov-report=html
```

## Why Sol-Query Instead of Tree-Sitter?

While [tree-sitter-solidity](https://github.com/JoranHonig/tree-sitter-solidity) provides excellent parsing, it delivers raw syntax trees that require significant processing for meaningful analysis. Sol-Query bridges this gap:

**Tree-sitter gives you:**
- Raw syntax nodes requiring manual traversal
- Generic parsing without Solidity semantics
- Complex recursive tree walking for simple queries

**Sol-Query provides:**
- High-level query abstractions: `engine.functions.external().payable()`
- Solidity-specific intelligence: contract inheritance, modifier patterns, type systems
- LLM-ready JSON serialization with configurable detail levels
- Error-resilient parsing that handles malformed/incomplete code gracefully

## Core Architecture

### Components
- **Parser**: Tree-sitter based Solidity parsing with robust error handling
- **AST Builder**: Converts tree-sitter nodes to typed Python objects
- **Source Manager**: Multi-file handling with dependency tracking
- **Query Engine**: Unified interface supporting both query styles
- **Collections**: Fluent query collections with method chaining
- **Pattern Matcher**: Advanced pattern matching with regex and wildcards
- **Serializer**: LLM-ready JSON output with configurable detail levels

### Design Principles
- **Robustness**: Handles incomplete/malformed code gracefully
- **Performance**: Lazy evaluation, caching, efficient indexing
- **Extensibility**: Plugin architecture for custom analyzers
- **LLM Integration**: Full JSON serialization, tool-call compatible

## Usage Examples

### Traditional Query Style
```python
# Find all public functions with modifiers
public_modified = engine.find_functions(
    visibility="public",
    modifiers=["onlyOwner"]
)

# Find contracts inheriting from specific interfaces
erc20_contracts = engine.find_contracts(
    inheritance="IERC20",
    kind="contract"
)
```

### Fluent Query Style
```python
# Chain multiple filters
complex_functions = (engine.functions
                          .external()
                          .payable()
                          .with_modifiers("onlyOwner"))

# Navigate from contracts to elements
token_events = (engine.contracts
                     .with_name("Token")
                     .get_events())
```

### JSON Serialization
```python
from sol_query.utils.serialization import LLMSerializer, SerializationLevel

serializer = LLMSerializer(SerializationLevel.DETAILED)
result = serializer.serialize_query_result(contracts)
json_output = serializer.to_json(result)
```

## License

MIT License - Built for the Solidity development community.