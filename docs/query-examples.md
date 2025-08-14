# Query Examples

Practical examples demonstrating Sol-Query's capabilities for various Solidity code analysis tasks.

## Basic Contract Analysis

### Finding All Contracts

```python
from sol_query import SolidityQueryEngine

engine = SolidityQueryEngine("path/to/contracts")

# Get all contracts
all_contracts = engine.find_contracts()
print(f"Found {len(all_contracts)} contracts")

# Separate by type
contracts = engine.contracts.main_contracts()
interfaces = engine.contracts.interfaces()
libraries = engine.contracts.libraries()

print(f"Contracts: {len(contracts)}, Interfaces: {len(interfaces)}, Libraries: {len(libraries)}")
```

### Contract Inheritance Analysis

```python
# Find contracts that inherit from specific interfaces
erc20_contracts = engine.find_contracts(inheritance="IERC20")
ownable_contracts = engine.find_contracts(inheritance="Ownable")

# Using fluent interface
erc20_tokens = engine.contracts.with_inheritance("IERC20").main_contracts()

# Find contracts with multiple inheritance
multi_inherited = []
for contract in engine.contracts:
    if len(contract.inheritance) > 1:
        multi_inherited.append(contract)
        print(f"{contract.name} inherits from: {', '.join(contract.inheritance)}")
```

## Function Analysis

### Finding Functions by Patterns

```python
# Find all transfer-related functions
transfer_functions = engine.functions.with_name("transfer*")

# Find getter functions
getters = engine.functions.with_name("get*").view()

# Find functions with specific modifiers
admin_functions = engine.functions.with_modifiers("onlyAdmin")
owner_functions = engine.functions.with_modifiers(["onlyOwner", "onlyAdmin"])

# Find external payable functions (potential entry points)
entry_points = engine.functions.external().payable()

# Find functions that are NOT external (internal implementation functions)
internal_functions = engine.functions.not_external()

# Find functions that are NOT constructors (regular functions only)
regular_functions = engine.functions.not_constructors()

# Find non-view functions (state-changing functions)
state_changing = engine.functions.not_view()

# Find functions without any modifiers (unprotected functions)
unprotected = engine.functions.without_modifiers()
```

## Advanced Negation Filter Examples

### Contract Analysis with Negation

```python
# Find contracts that are NOT interfaces (implementation contracts)
implementation_contracts = engine.contracts.not_interfaces()

# Find contracts that do NOT inherit from Ownable (unowned contracts)
unowned_contracts = engine.contracts.not_with_inheritance("Ownable")

# Find contracts without transfer functions (non-token contracts)
non_token_contracts = engine.contracts.without_function_name("transfer*")

# Find contracts without events (contracts that don't emit)
silent_contracts = engine.contracts.without_event_name("*")
```

### Variable Analysis with Negation

```python
# Find variables that are NOT constants (mutable state)
mutable_state = engine.variables.not_constants()

# Find variables that are NOT public (private/internal state)
private_state = engine.variables.not_public()

# Find variables that are NOT mappings (simple state variables)
simple_vars = engine.variables.not_with_type("mapping*")

# Find variables that are NOT uint256 (other numeric types)
non_uint256 = engine.variables.not_with_type("uint256")
```

### Security Analysis Examples

```python
# Find functions without access control modifiers (potential security risk)
unprotected_functions = engine.functions.without_any_modifiers_matching([
    "onlyOwner", "onlyAdmin", "onlyRole", "requiresAuth"
])

# Find state-changing functions that are external (external attack surface)
external_state_changing = engine.functions.external().not_view().not_pure()

# Find functions that are NOT view or pure (state-changing functions)
state_modifying = engine.functions.not_view().not_pure()

# Find contracts that do NOT have constructor (uninitialized contracts)
uninitialized_contracts = engine.contracts.without_function_name("constructor")
```

### Function Complexity Analysis

```python
# Find functions with many parameters (potential code smell)
complex_functions = []
for func in engine.functions:
    if len(func.parameters) > 5:
        complex_functions.append(func)
        print(f"{func.name} has {len(func.parameters)} parameters")

# Find functions without modifiers (potential security issue)
unprotected_functions = engine.functions.without_modifiers().external()
print(f"Found {len(unprotected_functions)} external functions without modifiers")
```

### Constructor Analysis

```python
# Find all constructors
constructors = engine.functions.constructors()

# Analyze constructor parameters
for constructor in constructors:
    contract_name = constructor.source_location.file_path.stem
    param_count = len(constructor.parameters)
    print(f"{contract_name} constructor has {param_count} parameters")

    for param in constructor.parameters:
        print(f"  - {param.name}: {param.type_name}")
```

## State Variable Analysis

### Variable Classification

```python
# Find all state variables
state_vars = engine.variables.state_variables()

# Classify by type
uint_vars = engine.variables.with_type("uint*")
mapping_vars = engine.variables.with_type("mapping*")
address_vars = engine.variables.with_type("address")
array_vars = engine.variables.with_type("*[]")

print(f"State variables by type:")
print(f"  uint*: {len(uint_vars)}")
print(f"  mapping*: {len(mapping_vars)}")
print(f"  address: {len(address_vars)}")
print(f"  arrays: {len(array_vars)}")
```

### Storage Analysis

```python
# Find expensive storage patterns
expensive_mappings = []
for var in engine.variables.with_type("mapping*"):
    if "mapping" in var.type_name and "=>" in var.type_name:
        # Nested mapping (expensive)
        if var.type_name.count("mapping") > 1:
            expensive_mappings.append(var)

# Find public state variables (automatic getters)
public_state = engine.variables.public().state_variables()
print(f"Found {len(public_state)} public state variables (automatic getters)")
```

## Event and Error Analysis

### Event Pattern Analysis

```python
# Find all events
all_events = engine.find_events()

# Find events by pattern
transfer_events = engine.events.with_name("Transfer*")
approval_events = engine.events.with_name("Approval*")
update_events = engine.events.with_name("*Update*")

# Analyze event parameters
for event in transfer_events:
    print(f"Event {event.name} has {len(event.parameters)} parameters")
```

### Error Handling Analysis

```python
# Find custom errors (Solidity 0.8.0+)
custom_errors = engine.find_errors()

# Group errors by contract
error_by_contract = engine.group_elements(custom_errors, "source_location.file_path")

for file_path, errors in error_by_contract.items():
    print(f"{file_path.name}: {len(errors)} custom errors")
    for error in errors:
        print(f"  - {error.name}")
```

## Advanced Call Graph Analysis

### Function Call Analysis

```python
# Find the most called functions
call_counts = {}
for func in engine.functions:
    callers = engine.find_callers_of(func)
    call_counts[func.name] = len(callers)

# Sort by call count
most_called = sorted(call_counts.items(), key=lambda x: x[1], reverse=True)
print("Most called functions:")
for func_name, count in most_called[:10]:
    print(f"  {func_name}: {count} callers")
```

### Finding Call Chains

```python
# Find paths from mint to transfer
mint_to_transfer_chains = engine.find_call_chains("mint", "transfer", max_depth=5)

print(f"Found {len(mint_to_transfer_chains)} call chains from mint to transfer:")
for i, chain in enumerate(mint_to_transfer_chains):
    chain_names = [func.name for func in chain]
    print(f"  Chain {i+1}: {' -> '.join(chain_names)}")
```

### Dependency Analysis

```python
# Find functions that don't call any other functions (leaf functions)
leaf_functions = []
for func in engine.functions:
    callees = engine.find_callees_of(func)
    if len(callees) == 0:
        leaf_functions.append(func)

print(f"Found {len(leaf_functions)} leaf functions")

# Find functions with deep call chains
deep_callers = []
for func in engine.functions:
    callees = engine.find_callees_of(func)
    if len(callees) > 5:
        deep_callers.append((func, len(callees)))

print("Functions with many callees:")
for func, count in sorted(deep_callers, key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {func.name}: calls {count} other functions")
```

## Security Analysis Patterns

### Access Control Analysis

```python
# Find functions that should have access control but don't
potential_security_issues = []

for func in engine.functions.external():
    # Check for state-changing external functions without modifiers
    if not func.is_view() and not func.is_pure() and len(func.modifiers) == 0:
        potential_security_issues.append(func)

print(f"Potential security issues - {len(potential_security_issues)} external state-changing functions without modifiers:")
for func in potential_security_issues:
    print(f"  {func.name} in {func.source_location.file_path.name}")
```

### Reentrancy Pattern Detection

```python
# Find external calls (potential reentrancy vectors)
external_calls = engine.find_calls(target_patterns="*call*")

# Find functions that make external calls
functions_with_external_calls = set()
for call in external_calls:
    # Find which function contains this call
    for func in engine.functions:
        if (func.source_location.file_path == call.source_location.file_path and
            func.source_location.start_line <= call.source_location.start_line <= func.source_location.end_line):
            functions_with_external_calls.add(func)

print(f"Functions making external calls: {len(functions_with_external_calls)}")
```

### Integer Overflow/Underflow Patterns

```python
# Find arithmetic operations (potential overflow/underflow)
binary_ops = engine.find_binary_operations()

# Find functions using arithmetic without SafeMath (pre-0.8.0)
arithmetic_functions = set()
for op in binary_ops:
    # Find containing function
    for func in engine.functions:
        if (func.source_location.file_path == op.source_location.file_path and
            func.source_location.start_line <= op.source_location.start_line <= func.source_location.end_line):
            arithmetic_functions.add(func)

print(f"Functions with arithmetic operations: {len(arithmetic_functions)}")
```

## Code Quality Analysis

### Naming Convention Analysis

```python
# Check function naming conventions
camelCase_functions = []
snake_case_functions = []
other_naming = []

for func in engine.functions:
    name = func.name
    if name.islower() and '_' in name:
        snake_case_functions.append(func)
    elif any(c.isupper() for c in name[1:]) and '_' not in name:
        camelCase_functions.append(func)
    else:
        other_naming.append(func)

print(f"Function naming:")
print(f"  camelCase: {len(camelCase_functions)}")
print(f"  snake_case: {len(snake_case_functions)}")
print(f"  other: {len(other_naming)}")
```

### Documentation Analysis

```python
# This would require source code analysis to check for NatSpec comments
# For now, we can check function complexity as a proxy for documentation needs

complex_functions = []
for func in engine.functions:
    complexity_score = 0

    # Add points for parameters
    complexity_score += len(func.parameters)

    # Add points for modifiers
    complexity_score += len(func.modifiers)

    # Add points for return parameters
    complexity_score += len(func.return_parameters)

    if complexity_score > 5:
        complex_functions.append((func, complexity_score))

print("Complex functions that may need documentation:")
for func, score in sorted(complex_functions, key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {func.name}: complexity score {score}")
```

## Cross-Contract Analysis

### Interface Implementation Analysis

```python
# Find interface functions and their implementations
interfaces = engine.contracts.interfaces()

for interface in interfaces:
    print(f"\nInterface {interface.name}:")

    # Find contracts that implement this interface
    implementers = engine.contracts.with_inheritance(interface.name)

    for implementer in implementers:
        print(f"  Implemented by: {implementer.name}")

        # Check which interface functions are implemented
        interface_functions = interface.functions
        implementer_functions = implementer.functions

        implemented = []
        missing = []

        for if_func in interface_functions:
            found = any(impl_func.name == if_func.name for impl_func in implementer_functions)
            if found:
                implemented.append(if_func.name)
            else:
                missing.append(if_func.name)

        if missing:
            print(f"    Missing implementations: {', '.join(missing)}")
```

### Library Usage Analysis

```python
# Find library usage patterns
libraries = engine.contracts.libraries()

for library in libraries:
    print(f"\nLibrary {library.name}:")

    # Find contracts that might use this library
    # (This is simplified - would need more sophisticated analysis)
    library_refs = engine.find_references_to(library.name)
    print(f"  Referenced {len(library_refs)} times")
```

## Performance and Gas Analysis

### Storage Optimization Analysis

```python
# Find potentially expensive storage patterns
storage_issues = []

# Find large structs (expensive to store)
structs = engine.find_structs()
for struct in structs:
    if len(struct.members) > 8:  # Arbitrary threshold
        storage_issues.append(f"Large struct {struct.name} with {len(struct.members)} members")

# Find public arrays (expensive getters)
public_arrays = engine.variables.public().with_type("*[]")
for array in public_arrays:
    storage_issues.append(f"Public array {array.name} creates expensive getter")

print("Potential storage optimization opportunities:")
for issue in storage_issues:
    print(f"  - {issue}")
```

### Function Visibility Optimization

```python
# Find public functions that could be external
public_functions = engine.functions.public()
potentially_external = []

for func in public_functions:
    # Simple heuristic: if not called internally, could be external
    internal_callers = [caller for caller in engine.find_callers_of(func)
                       if caller.visibility in ["internal", "private"]]

    if len(internal_callers) == 0:
        potentially_external.append(func)

print(f"Functions that could be external instead of public: {len(potentially_external)}")
for func in potentially_external:
    print(f"  {func.name}")
```

## Testing and Debugging Helpers

### Test Coverage Analysis

```python
# Find functions without corresponding test functions
function_names = [func.name for func in engine.functions if not func.is_constructor]
test_functions = engine.functions.with_name("test*")
test_targets = [func.name.replace("test", "").replace("Test", "") for func in test_functions]

untested_functions = []
for func_name in function_names:
    # Simple check if function name appears in test function names
    is_tested = any(func_name.lower() in target.lower() for target in test_targets)
    if not is_tested:
        untested_functions.append(func_name)

print(f"Potentially untested functions: {len(untested_functions)}")
for func_name in untested_functions[:10]:  # Show first 10
    print(f"  {func_name}")
```

### Error Prone Pattern Detection

```python
# Find patterns that are commonly error-prone
error_patterns = []

# Functions with similar names (typo potential)
func_names = [func.name for func in engine.functions]
similar_names = []
for i, name1 in enumerate(func_names):
    for name2 in func_names[i+1:]:
        # Simple similarity check
        if abs(len(name1) - len(name2)) <= 2 and name1 != name2:
            common = sum(1 for a, b in zip(name1, name2) if a == b)
            if common >= max(len(name1), len(name2)) - 2:
                similar_names.append((name1, name2))

if similar_names:
    print("Functions with similar names (potential typos):")
    for name1, name2 in similar_names[:5]:
        print(f"  {name1} vs {name2}")
```

These examples demonstrate Sol-Query's versatility for analyzing Solidity code across security, performance, quality, and maintainability dimensions.
