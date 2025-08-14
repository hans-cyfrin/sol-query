# Sol-Query: Powerful Solidity Code Analysis Engine

![Python](https://img.shields.io/badge/python-3.11+-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Coverage](https://img.shields.io/badge/coverage-68%25-green.svg) ![Tests](https://img.shields.io/badge/tests-191%20passed-brightgreen.svg)

A comprehensive Python-based query engine for Solidity smart contracts that provides both traditional and fluent query interfaces. Designed for security analysis, code migration, and research with advanced call graph and data flow analysis.

## 🚀 Quick Start

### Installation

```bash
# Install from GitHub
pip install git+https://github.com/hans-cyfrin/sol-query.git

# For development
git clone https://github.com/hans-cyfrin/sol-query.git && cd sol-query && pip install -e .

# Add to your project dependencies:
# pyproject.toml: "sol-query @ git+https://github.com/hans-cyfrin/sol-query.git"
# requirements.txt: git+https://github.com/hans-cyfrin/sol-query.git
```

### Usage

```python
from sol_query import SolidityQueryEngine

# Load and analyze contracts
engine = SolidityQueryEngine("path/to/contracts")

# Traditional API - simple and direct
external_functions = engine.find_functions(visibility="external")
token_contracts = engine.find_contracts(name_patterns="*Token*")

# Fluent API - chainable and expressive
risky_functions = (engine.contracts
                   .with_name("*")
                   .functions
                   .external()
                   .with_external_calls()
                   .payable())

# Advanced analysis
call_graph = engine.analyze_call_graph()
flow_paths = engine.trace_variable_flow("balance", "transfer", "MyToken")
import_deps = engine.analyze_imports("*OpenZeppelin*")
```

## 📚 Documentation

- **[📖 Complete API Reference](docs/api-reference.md)** - Comprehensive method documentation with all parameters and examples
- **[🏗️ Architecture Overview](docs/architecture.md)** - System design and component details
- **[📋 Documentation Hub](docs/README.md)** - Quick navigation and use cases

## ✨ Key Features

### 🔍 **Dual Query Interface**
- **Traditional Style**: `engine.find_functions(visibility="public", state_mutability="view")`
- **Fluent Style**: `engine.functions.public().view().with_name("get*")`
- **Method Chaining**: `contracts.interfaces().functions.external().payable()`
- **Set Operations**: `union()`, `intersect()`, `subtract()` for complex compositions

### 🛡️ **Advanced Security Analysis**
- **External Call Detection**: Identify functions making cross-contract calls
- **Asset Transfer Analysis**: Find ETH sends, token transfers, NFT operations
- **Call Graph Analysis**: Trace call chains and dependency relationships
- **Deep Analysis**: Transitive analysis through function call chains
- **Low-level Call Detection**: Identify `.call()`, `.delegatecall()`, `.staticcall()`

### 🌊 **Comprehensive Data Flow Analysis**
- **Variable Tracking**: Trace variable reads, writes, and modifications
- **Influence Analysis**: Find what affects a variable's value
- **Effect Analysis**: Find what a variable influences
- **Flow Path Discovery**: Trace data flow between statements
- **Cross-function Analysis**: Follow data flow across function boundaries

### 📦 **Import & Dependency Analysis**
- **Import Pattern Matching**: Find usage of specific libraries or interfaces
- **Dependency Graphs**: Visualize contract dependencies
- **Symbol Usage**: Track where imported symbols are used
- **External Library Detection**: Identify usage of common libraries (OpenZeppelin, etc.)

### 🎯 **Precise Filtering & Pattern Matching**
- **Contract Types**: Filter by interfaces, libraries, abstract contracts
- **Function Properties**: Visibility, state mutability, modifiers, special functions
- **Variable Types**: State variables, constants, immutables with type matching
- **Statement Types**: Loops, conditionals, assignments, returns, requires
- **Expression Types**: Calls, literals, identifiers with detailed categorization
- **Wildcard Patterns**: `*Token*`, `get*`, `*[sS]afe*` with full regex support

### 📊 **Rich Metadata & Analysis**
- **Source Location Tracking**: Precise file, line, column information
- **Type-safe AST**: Pydantic-based models with validation
- **Call Classification**: External, internal, library, low-level call types
- **Contextual Analysis**: Smart detection based on contract context
- **JSON Serialization**: LLM-ready export with configurable detail levels

## 🎯 Advanced Examples

### Complex Query Composition
```python
# Find interface functions that are implemented across multiple contracts
interface_funcs = (engine.contracts
                   .interfaces()
                   .functions
                   .external()
                   .get_signatures())

implementations = []
for sig in interface_funcs:
    impls = (engine.contracts
             .not_interfaces()
             .functions
             .with_signature(sig))
    if len(impls) > 1:
        implementations.append((sig, impls))
```

### Data Flow Analysis
```python
# Trace how user funds flow through a contract
user_deposits = engine.functions.with_name("deposit*").payable()

for deposit_func in user_deposits:
    # Find where msg.value goes
    value_flow = engine.trace_variable_flow("msg.value", deposit_func.name)

    # Find what affects user balances
    balance_effects = engine.find_variable_effects("balances", deposit_func.name)

    print(f"Deposit function: {deposit_func.name}")
    print(f"Value flow: {len(value_flow)} paths")
    print(f"Balance effects: {len(balance_effects)} statements")
```

### Custom Analysis with Set Operations
```python
# Find functions that have external calls but no access control
external_call_funcs = engine.functions.with_external_calls()
protected_funcs = engine.functions.modifiers_applied(["onlyOwner", "onlyAdmin"])

unprotected_external = external_call_funcs.subtract(protected_funcs)

print(f"Found {len(unprotected_external)} potentially unsafe functions:")
for func in unprotected_external:
    print(f"  {func.parent_contract.name}.{func.name}")
```

## 🔬 Technical Architecture

Sol-Query is built on a robust, extensible architecture:

- **Tree-sitter Parser**: Robust parsing that handles incomplete/malformed code
- **Type-safe AST**: Pydantic models ensure data integrity and validation
- **Analysis Pipeline**: Modular analyzers for calls, data flow, and imports
- **Collection Framework**: Chainable, type-safe collections with set operations
- **Pattern Engine**: Flexible matching with wildcards, regex, and exact patterns
- **Memory Efficient**: Lazy evaluation and caching for large codebases

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- **[Complete API Documentation](docs/api-reference.md)**
- **[Architecture Guide](docs/architecture.md)**
- **[Documentation Hub](docs/README.md)**
