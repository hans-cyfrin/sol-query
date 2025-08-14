# Getting Started with Sol-Query

This guide will help you get up and running with Sol-Query quickly.

## Installation

### Requirements

- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`

### Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd sol-query

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Basic Usage

### 1. Initialize the Query Engine

```python
from sol_query import SolidityQueryEngine
from pathlib import Path

# Create engine instance
engine = SolidityQueryEngine()

# Load Solidity files
engine.load_sources("path/to/contracts")

# Or load specific files
engine.load_sources(["contract1.sol", "contract2.sol"])

# Or load with Path objects
engine.load_sources(Path("src"))
```

### 2. Traditional Query Methods

Sol-Query provides traditional finder methods for direct querying:

```python
# Find contracts
all_contracts = engine.find_contracts()
token_contracts = engine.find_contracts(name_patterns="*Token*")
interfaces = engine.find_contracts(kind="interface")

# Find functions
external_functions = engine.find_functions(visibility="external")
mint_functions = engine.find_functions(name_patterns="mint*")
view_functions = engine.find_functions(state_mutability="view")

# Find variables
state_variables = engine.find_variables(is_state_variable=True)
uint256_vars = engine.find_variables(type_patterns="uint256")
public_vars = engine.find_variables(visibility="public")

# Find other elements
events = engine.find_events(name_patterns="Transfer*")
modifiers = engine.find_modifiers(name_patterns="only*")
errors = engine.find_errors()
```

### 3. Fluent Query Interface

Sol-Query also provides a fluent interface for chainable queries:

```python
# Contract queries
governance_contracts = (engine.contracts
                       .with_name("*Governance*")
                       .main_contracts())

# Function queries
external_view_functions = (engine.functions
                          .external()
                          .view()
                          .with_name("get*"))

# Variable queries
public_mappings = (engine.variables
                  .public()
                  .with_type("mapping*"))

# Navigate from contracts to their elements
token_functions = (engine.contracts
                  .with_name("Token")
                  .get_functions()
                  .external())
```

### 4. Pattern Matching

Sol-Query supports flexible pattern matching:

```python
# Wildcard patterns
transfer_funcs = engine.functions.with_name("transfer*")  # starts with
burn_funcs = engine.functions.with_name("*burn*")        # contains
getter_funcs = engine.functions.with_name("get*")        # starts with

# Exact matching
exact_func = engine.functions.with_name("transfer")

# Multiple patterns
multi_funcs = engine.functions.with_name(["mint", "burn", "transfer"])

# Type patterns
uint_vars = engine.variables.with_type("uint*")          # uint256, uint128, etc.
mapping_vars = engine.variables.with_type("mapping*")    # any mapping type
```

### 5. Query Results

All queries return collections that can be used in various ways:

```python
contracts = engine.contracts.with_name("*Token*")

# Get count
print(f"Found {len(contracts)} contracts")

# Iterate over results
for contract in contracts:
    print(f"Contract: {contract.name}")

# Get first result
first_contract = contracts.first()

# Convert to list
contract_list = contracts.list()

# JSON serialization
json_data = contracts.to_dict()
```

### 6. Advanced Queries

#### Call Graph Analysis

```python
# Find what calls a function
mint_function = engine.functions.with_name("mint").first()
callers = engine.find_callers_of(mint_function)

# Find what a function calls
callees = engine.find_callees_of(mint_function)

# Find call chains
chains = engine.find_call_chains("mint", "transfer", max_depth=5)
```

#### Reference Tracking

```python
# Find all references to a symbol
owner_refs = engine.find_references_to("owner")

# Find definitions
definitions = engine.find_definitions_of("totalSupply")

# Find usages
usages = engine.find_usages_of("mint")
```

### 7. Statistics and Metadata

```python
# Get comprehensive statistics
stats = engine.get_statistics()
print(f"Total contracts: {stats['total_contracts']}")
print(f"Total functions: {stats['total_functions']}")

# Get contract names
contract_names = engine.get_contract_names()
print("Contracts:", contract_names)
```

## Next Steps

- Explore the [API Reference](api-reference.md) for complete method documentation
- See [Query Examples](query-examples.md) for more advanced usage patterns
- Read the [Architecture Overview](architecture.md) to understand the internals
- Check out the [Development Guide](development.md) for contributing
