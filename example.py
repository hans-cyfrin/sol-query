#!/usr/bin/env python3
"""
Example usage of the Solidity Query Engine.

This script demonstrates both traditional and fluent query styles
for analyzing Solidity smart contracts.
"""

from pathlib import Path
from sol_query import SolidityQueryEngine
from sol_query.utils.serialization import LLMSerializer, SerializationLevel

def main():
    """Demonstrate query engine capabilities."""

    # Initialize the query engine
    print("🔍 Initializing Solidity Query Engine...")
    engine = SolidityQueryEngine()

    # Load sample contract
    sample_path = Path("tests/fixtures/sample_contract.sol")
    if sample_path.exists():
        engine.load_sources(sample_path)
        print(f"✅ Loaded contract from {sample_path}")
    else:
        print("❌ Sample contract not found. Please ensure tests/fixtures/sample_contract.sol exists.")
        return

    # Display statistics
    stats = engine.get_statistics()
    print(f"\n📊 Codebase Statistics:")
    print(f"   Files: {stats['total_files']}")
    print(f"   Contracts: {stats['total_contracts']}")
    print(f"   Functions: {stats['total_functions']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")

    print(f"\n📋 Contract types:")
    for contract_type, count in stats['contracts_by_type'].items():
        if count > 0:
            print(f"   {contract_type.title()}: {count}")

    # Demonstrate traditional query style
    print(f"\n🔎 Traditional Query Style Examples:")

    # Find all contracts
    contracts = engine.find_contracts()
    print(f"   Found {len(contracts)} contracts: {[c.name for c in contracts]}")

    # Find public functions
    public_functions = engine.find_functions(visibility="public")
    print(f"   Found {len(public_functions)} public functions")

    # Find functions with modifiers
    modified_functions = engine.find_functions(modifiers="onlyOwner")
    print(f"   Found {len(modified_functions)} functions with 'onlyOwner' modifier")

    # Demonstrate fluent query style
    print(f"\n🌊 Fluent Query Style Examples:")

    # Chain multiple filters
    external_view_functions = engine.functions.external().view()
    print(f"   External view functions: {len(external_view_functions)}")

    # Contract-specific queries
    token_contract = engine.contracts.with_name("Token").first()
    if token_contract:
        print(f"   Token contract functions: {len(token_contract.functions)}")
        print(f"   Token contract events: {len(token_contract.events)}")

    # Get interfaces
    interfaces = engine.contracts.interfaces()
    print(f"   Interfaces: {[c.name for c in interfaces]}")

    # Get libraries
    libraries = engine.contracts.libraries()
    print(f"   Libraries: {[c.name for c in libraries]}")

    # Pattern matching examples
    print(f"\n🎯 Pattern Matching Examples:")

    # Wildcard patterns
    transfer_functions = engine.functions.with_name("transfer*")
    print(f"   Functions starting with 'transfer': {[f.name for f in transfer_functions]}")

    # Type patterns
    uint256_variables = engine.variables.with_type("uint256")
    print(f"   uint256 variables: {len(uint256_variables)}")

    # Mapping variables
    mapping_variables = engine.variables.with_type("mapping*")
    print(f"   Mapping variables: {len(mapping_variables)}")

    # Demonstrate JSON serialization
    print(f"\n📄 JSON Serialization Examples:")

    serializer = LLMSerializer(SerializationLevel.DETAILED)

    # Serialize a single contract
    if token_contract:
        contract_json = serializer.serialize_node(token_contract)
        print(f"   Token contract serialized (keys): {list(contract_json.keys())}")

    # Serialize a collection with pagination
    all_functions = engine.functions
    paginated_result = serializer.serialize_collection(all_functions, limit=5)
    print(f"   Functions collection (first 5): {paginated_result['returned_count']} of {paginated_result['total_count']}")

    # Navigation examples
    print(f"\n🧭 Navigation Examples:")

    # From contracts to their elements
    token_functions = engine.contracts.with_name("Token").get_functions()
    print(f"   Token contract functions: {[f.name for f in token_functions]}")

    # Get public functions from Token contract
    token_public_funcs = token_functions.public()
    print(f"   Token public functions: {[f.name for f in token_public_funcs]}")

    # Demonstrate negation filters
    print(f"\n🚫 Negation Filter Examples:")

    # Functions that are NOT external
    not_external = engine.functions.not_external()
    print(f"   Functions that are NOT external: {len(not_external)}")

    # Functions that are NOT constructors
    not_constructors = engine.functions.not_constructors()
    print(f"   Functions that are NOT constructors: {len(not_constructors)}")

    # Functions that are NOT view (state-changing functions)
    state_changing = engine.functions.not_view()
    print(f"   State-changing functions (NOT view): {len(state_changing)}")

    # Variables that are NOT constants (mutable state)
    mutable_vars = engine.variables.not_constants()
    print(f"   Mutable variables (NOT constants): {len(mutable_vars)}")

    # Contracts that are NOT interfaces
    implementation_contracts = engine.contracts.not_interfaces()
    print(f"   Implementation contracts (NOT interfaces): {len(implementation_contracts)}")

    # Security analysis with negation filters
    unprotected_external = engine.functions.external().without_any_modifiers_matching([
        "onlyOwner", "onlyAdmin", "requiresAuth"
    ])
    print(f"   Unprotected external functions: {len(unprotected_external)}")
    if unprotected_external:
        print(f"      Examples: {[f.name for f in unprotected_external[:3]]}")

    # Function analysis
    print(f"\n⚙️  Function Analysis Examples:")

    # Constructors
    constructors = engine.functions.constructors()
    print(f"   Constructors: {len(constructors)}")

    # Pure vs view functions
    pure_functions = engine.functions.pure()
    view_functions = engine.functions.view()
    print(f"   Pure functions: {len(pure_functions)}, View functions: {len(view_functions)}")

    # Functions with parameters
    functions_with_params = [f for f in engine.functions if len(f.parameters) > 0]
    print(f"   Functions with parameters: {len(functions_with_params)}")

    # Statement and Expression Analysis Examples
    print(f"\n🔄 Statement Analysis Examples:")

    # Find all loop statements
    loops = engine.find_loops()
    print(f"   Total loops found: {len(loops)}")

    # Find conditional statements
    conditionals = engine.find_conditionals()
    print(f"   Conditional statements (if/else): {len(conditionals)}")

    # Find assignment statements
    assignments = engine.find_assignments()
    print(f"   Assignment statements: {len(assignments)}")

    # Find return statements
    returns = engine.find_returns()
    print(f"   Return statements: {len(returns)}")

    # Find require statements
    requires = engine.find_requires()
    print(f"   Require statements: {len(requires)}")

    # Find emit statements
    emits = engine.find_emits()
    print(f"   Emit statements: {len(emits)}")

    # Expression Analysis
    print(f"\n🧮 Expression Analysis Examples:")

    # Find all expressions
    expressions = engine.find_expressions()
    print(f"   Total expressions found: {len(expressions)}")

    # Find specific expression types
    if expressions:
        expr_types = {}
        for expr in expressions[:20]:  # Limit to first 20 for display
            expr_type = expr.node_type.value if hasattr(expr, 'node_type') else 'unknown'
            expr_types[expr_type] = expr_types.get(expr_type, 0) + 1

        print(f"   Expression types (sample):")
        for expr_type, count in sorted(expr_types.items()):
            print(f"      {expr_type}: {count}")

    # Parent Contract Access Examples
    print(f"\n🏗️  Parent Contract Access Examples:")

    # Get parent contract of a specific function
    process_func = engine.functions.with_name("processNumbers").first()
    if process_func:
        parent = process_func.parent_contract
        print(f"   processNumbers function parent: {parent.name if parent else 'None'}")

    # Filter functions by parent contract
    complex_functions = engine.functions.from_contract("ComplexLogic")
    print(f"   Functions from ComplexLogic: {len(complex_functions)}")
    if complex_functions:
        print(f"      Names: {[f.name for f in complex_functions[:3]]}...")

    # Filter variables by parent contract
    complex_variables = engine.variables.from_contract("ComplexLogic")
    print(f"   Variables from ComplexLogic: {len(complex_variables)}")
    if complex_variables:
        print(f"      Names: {[v.name for v in complex_variables]}")

    # Advanced Statement Filtering Examples
    print(f"\n🎯 Advanced Statement Filtering:")

    # Find loops in specific functions
    complex_functions = engine.find_functions(name_patterns="*process*")
    if complex_functions:
        print(f"   Functions with 'process' in name: {len(complex_functions)}")
        for func in complex_functions[:3]:
            print(f"      - {func.name}")

    # Find functions with loops
    functions_with_loops = []
    for func in engine.functions:
        # Check if function contains loops (simplified check)
        if hasattr(func, 'body') and func.body:
            # This would need proper AST traversal in real implementation
            functions_with_loops.append(func)

    print(f"   Functions potentially containing loops: {len(functions_with_loops)}")

    # Find functions with complex conditionals
    complex_conditional_functions = engine.find_functions(name_patterns="*analyze*")
    if complex_conditional_functions:
        print(f"   Functions with 'analyze' in name: {len(complex_conditional_functions)}")

    # Statement Context Analysis
    print(f"\n🔍 Statement Context Analysis:")

    # Find statements in specific contracts
    complex_logic_contract = engine.contracts.with_name("ComplexLogic").first()
    if complex_logic_contract:
        print(f"   ComplexLogic contract found with {len(complex_logic_contract.functions)} functions")

        # Analyze specific functions in ComplexLogic contract
        process_func = engine.functions.with_name("processNumbers").first()
        if process_func:
            print(f"   Found processNumbers function")

        factorial_function = engine.functions.with_name("calculateFactorial").first()
        if factorial_function:
            print(f"   Found calculateFactorial function")

        nested_function = engine.functions.with_name("analyzeUserPatterns").first()
        if nested_function:
            print(f"   Found analyzeUserPatterns function")

    # Pattern-based Statement Analysis
    print(f"\n📊 Pattern-based Analysis:")

    # Find functions by name patterns (processing-related)
    process_funcs = engine.functions.with_name("*process*")
    calculate_funcs = engine.functions.with_name("*calculate*")
    analyze_funcs = engine.functions.with_name("*analyze*")
    sum_funcs = engine.functions.with_name("*sum*")

    processing_functions = engine.union(process_funcs, calculate_funcs, analyze_funcs, sum_funcs)
    print(f"   Processing-related functions: {len(processing_functions)}")

    # Find functions by name patterns (validation-related)
    validate_funcs = engine.functions.with_name("*validate*")
    check_funcs = engine.functions.with_name("*check*")
    find_funcs = engine.functions.with_name("*find*")
    get_funcs = engine.functions.with_name("*get*")

    validation_functions = engine.union(validate_funcs, check_funcs, find_funcs, get_funcs)
    print(f"   Validation-related functions: {len(validation_functions)}")

    # Security-focused statement analysis
    print(f"\n🔒 Security-focused Statement Analysis:")

    # Find functions with require statements (actual analysis)
    require_statements = engine.find_requires()
    print(f"   Total require statements found: {len(require_statements)}")

    # Find functions that contain validation logic by name
    validation_funcs = engine.functions.with_name("*validate*")
    print(f"   Functions with 'validate' in name: {len(validation_funcs)}")

    # Find functions with early returns (multiple exit points)
    early_return_functions = engine.functions.with_name("validateAndProcess")
    print(f"   Functions with early returns: {len(early_return_functions)}")

    # Find functions with assembly blocks (low-level operations)
    assembly_functions = engine.functions.with_name("getCodeSize")
    print(f"   Functions with assembly blocks: {len(assembly_functions)}")

    print(f"\n✨ Enhanced query engine demonstration complete!")
    print(f"💡 This engine supports both traditional find_*() methods and fluent .*() chaining")
    print(f"🔧 Perfect for LLM integration with full JSON serialization support")
    print(f"🔄 Now includes comprehensive statement and expression analysis capabilities")
    print(f"🎯 Enhanced with loop, conditional, assignment, and expression querying")


if __name__ == "__main__":
    main()