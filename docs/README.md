# Sol-Query Documentation

A comprehensive Python-based code query engine for Solidity using tree-sitter-solidity that provides both traditional and fluent query interfaces, designed to serve as tools for LLM-based code search.

## Table of Contents

- [Getting Started](getting-started.md)
- [API Reference](api-reference.md)
- [Query Examples](query-examples.md)
- [Architecture Overview](architecture.md)
- [Development Guide](development.md)

## Quick Start

```python
from sol_query import SolidityQueryEngine

# Initialize the engine
engine = SolidityQueryEngine()

# Load Solidity source files
engine.load_sources("path/to/solidity/files")

# Traditional query approach
contracts = engine.find_contracts(name_patterns="Token*")
functions = engine.find_functions(visibility="external", contract_name="MyContract")

# Fluent query approach
external_funcs = engine.contracts.with_name("MyContract").get_functions().external()
public_vars = engine.variables.public().with_type("uint256")
```

## Key Features

- **Unified Interface**: Supports both traditional finder methods and fluent collection-based queries
- **Comprehensive Coverage**: Query contracts, functions, variables, events, errors, modifiers, and more
- **Pattern Matching**: Flexible name and type pattern matching with wildcards and regex
- **Call Graph Analysis**: Find callers, callees, and call chains between functions
- **JSON Serialization**: Full JSON serialization support for LLM integration
- **Performance Optimized**: Efficient parsing and querying for large codebases
- **Robust Error Handling**: Graceful handling of malformed or incomplete Solidity code

## Architecture

Sol-Query is built with a modular architecture:

- **Core**: Tree-sitter integration, AST building, and source management
- **Query**: Unified query engine with traditional and fluent interfaces
- **Collections**: Chainable collection classes for fluent queries
- **Utils**: Pattern matching, serialization, and utility functions
- **Models**: Data models and AST node representations

## Support

- [Report Issues](https://github.com/your-repo/sol-query/issues)
- [Contributing Guidelines](contributing.md)
- [API Documentation](api-reference.md)
