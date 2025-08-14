# External Call and Asset Transfer Analysis

This guide demonstrates how to use Sol-Query's new external call and asset transfer analysis features.

## Overview

Sol-Query now provides powerful filters to identify functions that:
- Make external contract calls
- Transfer assets (ETH, tokens, NFTs)
- Have external calls or asset transfers anywhere in their call tree (deep analysis)

## Basic Usage

### Finding Functions with External Calls

```python
from sol_query.query.engine import SolidityQueryEngine

# Load your contracts
engine = SolidityQueryEngine()
engine.load_sources("path/to/contracts")

# Find functions that directly make external calls
functions_with_external_calls = engine.functions.with_external_calls()

for func in functions_with_external_calls:
    print(f"Function {func.name} makes external calls: {func.external_call_targets}")
```

### Finding Functions with Asset Transfers

```python
# Find functions that directly transfer assets
functions_with_transfers = engine.functions.with_asset_transfers()

for func in functions_with_transfers:
    print(f"Function {func.name} transfers assets: {func.asset_transfer_types}")
```

## Deep Analysis (Call Tree)

### External Calls in Call Tree

```python
# Find functions that may indirectly make external calls
# This analyzes the entire call chain
functions_with_deep_external_calls = engine.functions.with_external_calls_deep()

print(f"Found {len(functions_with_deep_external_calls)} functions with external calls in their call tree")
```

### Asset Transfers in Call Tree

```python
# Find functions that may indirectly transfer assets
functions_with_deep_transfers = engine.functions.with_asset_transfers_deep()

print(f"Found {len(functions_with_deep_transfers)} functions with asset transfers in their call tree")
```

## Traditional Finder Methods

You can also use the traditional finder methods with the new parameters:

```python
# Find external functions that make external calls
external_functions_with_calls = engine.find_functions(
    visibility=Visibility.EXTERNAL,
    with_external_calls=True
)

# Find payable functions with asset transfers
payable_functions_with_transfers = engine.find_functions(
    state_mutability=StateMutability.PAYABLE,
    with_asset_transfers=True
)

# Find functions with deep external calls
deep_external_functions = engine.find_functions(
    with_external_calls_deep=True
)
```

## Combining Filters

The new filters work seamlessly with existing filters:

```python
# Find external functions that make external calls but don't transfer assets
risky_functions = (engine.functions
                  .external()
                  .with_external_calls()
                  .without_asset_transfers())

# Find public functions with deep asset transfers
public_transfer_functions = (engine.functions
                           .public()
                           .with_asset_transfers_deep())

# Find functions with specific call targets
functions_calling_transfer = engine.functions.with_external_call_targets(['transfer', 'call'])

# Find functions with specific transfer types
eth_transfer_functions = engine.functions.with_asset_transfer_types(['eth_transfer'])
```

## Negation Filters

Use negation filters to find functions that DON'T have certain characteristics:

```python
# Find functions without any external calls
safe_functions = engine.functions.without_external_calls()

# Find functions without asset transfers (even in call tree)
non_transfer_functions = engine.functions.without_asset_transfers_deep()
```

## Security Analysis Examples

### Finding Potential Reentrancy Vectors

```python
# Find external functions that make external calls (potential reentrancy)
reentrancy_vectors = (engine.functions
                     .external()
                     .with_external_calls()
                     .not_view()
                     .not_pure())

print("Potential reentrancy vectors:")
for func in reentrancy_vectors:
    print(f"  - {func.name} in {func.parent_contract.name}")
    print(f"    External calls: {func.external_call_targets}")
```

### Finding Asset Transfer Functions

```python
# Find all functions that can transfer assets
asset_transfer_functions = engine.functions.with_asset_transfers_deep()

# Group by transfer type
eth_transfers = engine.functions.with_asset_transfer_types(['eth_transfer'])
token_transfers = engine.functions.with_asset_transfer_types(['token_transfer'])

print(f"ETH transfer functions: {len(eth_transfers)}")
print(f"Token transfer functions: {len(token_transfers)}")
```

### Access Control Analysis

```python
# Find external asset transfer functions without access control modifiers
unprotected_transfers = (engine.functions
                        .external()
                        .with_asset_transfers()
                        .without_modifiers())

print("Unprotected asset transfer functions:")
for func in unprotected_transfers:
    print(f"  - {func.name} in {func.parent_contract.name}")
```

## Detected Call Types

### External Call Types
- `external_call_*`: Direct external function calls
- `contract_call`: Low-level contract calls (.call, .delegatecall, .staticcall)
- `interface_call_*`: Interface-based contract calls

### Asset Transfer Types
- `eth_transfer`: ETH transfers (.send, .transfer, {value: ...})
- `token_transfer`: Token transfers (.transfer, .transferFrom, .safeTransfer)
- `nft_transfer`: NFT transfers
- `token_mint_burn`: Token minting/burning operations
- `asset_movement`: General asset deposits/withdrawals

## Performance Considerations

- **Shallow analysis** (`with_external_calls`, `with_asset_transfers`) is fast as it uses pre-computed metadata
- **Deep analysis** (`with_external_calls_deep`, `with_asset_transfers_deep`) analyzes call trees and may be slower for large codebases
- Deep analysis results are not cached, so consider storing results if you need to reuse them

## Limitations

- External call detection is based on pattern matching and may not catch all edge cases
- Cross-contract calls through complex proxy patterns may not be detected
- Dynamic calls using assembly or complex call patterns may be missed
- The analysis is performed during AST building, so it reflects the static code structure

## Best Practices

1. **Start with shallow analysis** to get quick results
2. **Use deep analysis** for comprehensive security audits
3. **Combine with other filters** to narrow down results
4. **Verify results manually** for critical security analysis
5. **Use specific target/type filters** to focus on particular patterns

## Example: Complete Security Analysis

```python
def analyze_contract_security(engine, contract_name):
    """Perform a comprehensive security analysis of a contract."""
    
    contract_functions = engine.functions.from_contract(contract_name)
    
    print(f"=== Security Analysis for {contract_name} ===")
    
    # External functions with external calls (reentrancy risk)
    reentrancy_risk = contract_functions.external().with_external_calls().not_view()
    print(f"Potential reentrancy vectors: {len(reentrancy_risk)}")
    
    # Asset transfer functions without access control
    unprotected_transfers = contract_functions.with_asset_transfers().without_modifiers()
    print(f"Unprotected asset transfers: {len(unprotected_transfers)}")
    
    # Functions with deep external calls
    deep_external = contract_functions.with_external_calls_deep()
    print(f"Functions with external calls (deep): {len(deep_external)}")
    
    # Functions with deep asset transfers
    deep_transfers = contract_functions.with_asset_transfers_deep()
    print(f"Functions with asset transfers (deep): {len(deep_transfers)}")
    
    return {
        'reentrancy_risk': reentrancy_risk.list(),
        'unprotected_transfers': unprotected_transfers.list(),
        'deep_external': deep_external.list(),
        'deep_transfers': deep_transfers.list()
    }

# Usage
results = analyze_contract_security(engine, "LiquidityPool")
```
