# Sol-Query API Reference

Complete reference for the Sol-Query Solidity code analysis engine.

## Core Classes

### SolidityQueryEngine

Main query engine providing comprehensive Solidity code analysis capabilities.

#### Constructor

```python
SolidityQueryEngine(source_paths: Optional[Union[str, Path, List[Union[str, Path]]]] = None)
```

**Parameters:**
- `source_paths`: Optional path(s) to load initially. Can be:
  - String or Path to a file or directory
  - List of strings/Paths for multiple sources

## Source Management

### `load_sources(source_paths: Union[str, Path, List[Union[str, Path]]]) -> None`
Load source files or directories.

**Parameters:**
- `source_paths`: Path(s) to load (files, directories, or lists thereof)

## Traditional Finder Methods

### Contract Discovery

#### `find_contracts(name_patterns=None, inheritance=None, kind=None, **filters) -> List[ContractDeclaration]`
Find contracts matching specified criteria.

**Parameters:**
- `name_patterns`: Name patterns to match (string, regex, or list)
- `inheritance`: Base contracts/interfaces this contract inherits from (string or list)
- `kind`: Contract kind - one of: `"contract"`, `"interface"`, `"library"`, `"abstract"`
- `**filters`: Additional filter conditions

#### `find_modifiers(name_patterns=None, contract_name=None, **filters) -> List[ModifierDeclaration]`
Find modifier declarations.

**Parameters:**
- `name_patterns`: Modifier name patterns to match (string, regex, or list)
- `contract_name`: Name of contract containing the modifier
- `**filters`: Additional filter conditions

#### `find_events(name_patterns=None, contract_name=None, **filters) -> List[EventDeclaration]`
Find event declarations.

**Parameters:**
- `name_patterns`: Event name patterns to match (string, regex, or list)
- `contract_name`: Name of contract containing the event
- `**filters`: Additional filter conditions

#### `find_structs(name_patterns=None, contract_name=None, **filters) -> List[StructDeclaration]`
Find struct declarations.

**Parameters:**
- `name_patterns`: Struct name patterns to match (string, regex, or list)
- `contract_name`: Name of contract containing the struct
- `**filters`: Additional filter conditions

#### `find_enums(name_patterns=None, contract_name=None, **filters) -> List[EnumDeclaration]`
Find enum declarations.

**Parameters:**
- `name_patterns`: Enum name patterns to match (string, regex, or list)
- `contract_name`: Name of contract containing the enum
- `**filters`: Additional filter conditions

#### `find_errors(name_patterns=None, contract_name=None, **filters) -> List[ErrorDeclaration]`
Find custom error declarations.

**Parameters:**
- `name_patterns`: Error name patterns to match (string, regex, or list)
- `contract_name`: Name of contract containing the error
- `**filters`: Additional filter conditions

### Function Discovery

#### `find_functions(name_patterns=None, visibility=None, modifiers=None, state_mutability=None, contract_name=None, with_external_calls=None, with_asset_transfers=None, with_external_calls_deep=None, with_asset_transfers_deep=None, **filters) -> List[FunctionDeclaration]`
Find functions matching specified criteria.

**Parameters:**
- `name_patterns`: Function name patterns to match (string, regex, or list)
- `visibility`: Function visibility - one or list of:
  - `Visibility.PUBLIC` (`"public"`)
  - `Visibility.PRIVATE` (`"private"`)
  - `Visibility.INTERNAL` (`"internal"`)
  - `Visibility.EXTERNAL` (`"external"`)
- `modifiers`: Modifier names that must be present (string or list)
- `state_mutability`: State mutability - one or list of:
  - `StateMutability.PURE` (`"pure"`)
  - `StateMutability.VIEW` (`"view"`)
  - `StateMutability.NONPAYABLE` (`"nonpayable"`)
  - `StateMutability.PAYABLE` (`"payable"`)
- `contract_name`: Name of contract containing the function
- `with_external_calls`: Filter by functions with direct external calls (boolean)
- `with_asset_transfers`: Filter by functions with direct asset transfers (boolean)
- `with_external_calls_deep`: Filter by functions with external calls in call tree (boolean)
- `with_asset_transfers_deep`: Filter by functions with asset transfers in call tree (boolean)
- `**filters`: Additional filter conditions

### Variable Discovery

#### `find_variables(name_patterns=None, type_patterns=None, visibility=None, is_state_variable=None, contract_name=None, **filters) -> List[VariableDeclaration]`
Find variables matching specified criteria.

**Parameters:**
- `name_patterns`: Variable name patterns to match (string, regex, or list)
- `type_patterns`: Variable type patterns to match (string, regex, or list)
- `visibility`: Variable visibility - same values as function visibility
- `is_state_variable`: Whether to find only state variables (boolean)
- `contract_name`: Name of contract containing the variable
- `**filters`: Additional filter conditions

### Statement Discovery

#### `find_statements(statement_types=None, contract_name=None, function_name=None, **filters) -> List[Statement]`
Find statements matching specified criteria.

**Parameters:**
- `statement_types`: Types of statements to find (string or list)
- `contract_name`: Name of contract to search in
- `function_name`: Name of function to search in
- `**filters`: Additional filter conditions

#### `find_loops(loop_types=None, contract_name=None, function_name=None, **filters) -> List[Statement]`
Find loop statements.

**Parameters:**
- `loop_types`: Types of loops to find - one or list of: `"for"`, `"while"`, `"do-while"`
- `contract_name`: Name of contract to search in
- `function_name`: Name of function to search in
- `**filters`: Additional filter conditions

#### `find_conditionals(contract_name=None, function_name=None, **filters) -> List[Statement]`
Find conditional statements (if/else).

#### `find_assignments(contract_name=None, function_name=None, **filters) -> List[Statement]`
Find assignment statements.

#### `find_returns(contract_name=None, function_name=None, **filters) -> List[Statement]`
Find return statements.

#### `find_requires(contract_name=None, function_name=None, **filters) -> List[Statement]`
Find require statements.

#### `find_emits(contract_name=None, function_name=None, **filters) -> List[Statement]`
Find emit statements.

### Expression Discovery

#### `find_expressions(expression_types=None, contract_name=None, function_name=None, **filters) -> List[Expression]`
Find expressions matching specified criteria.

**Parameters:**
- `expression_types`: Types of expressions to find (string or list)
- `contract_name`: Name of contract to search in
- `function_name`: Name of function to search in
- `**filters`: Additional filter conditions

#### `find_calls(target_patterns=None, contract_name=None, function_name=None, **filters) -> List[Expression]`
Find function calls.

**Parameters:**
- `target_patterns`: Patterns for called function names (string, regex, or list)
- `contract_name`: Name of contract to search in
- `function_name`: Name of function to search in
- `**filters`: Additional filter conditions

#### `find_literals(literal_types=None, contract_name=None, function_name=None, **filters) -> List[Expression]`
Find literals.

**Parameters:**
- `literal_types`: Types of literals to find - `"string"`, `"number"`, `"bool"` (string or list)
- `contract_name`: Name of contract to search in
- `function_name`: Name of function to search in
- `**filters`: Additional filter conditions

#### `find_identifiers(name_patterns=None, contract_name=None, function_name=None, **filters) -> List[Expression]`
Find identifiers.

**Parameters:**
- `name_patterns`: Identifier name patterns to match (string, regex, or list)
- `contract_name`: Name of contract to search in
- `function_name`: Name of function to search in
- `**filters`: Additional filter conditions

#### `find_binary_operations(operators=None, contract_name=None, function_name=None, **filters) -> List[Expression]`
Find binary operations.

**Parameters:**
- `operators`: Operators to match - `+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, etc. (string or list)
- `contract_name`: Name of contract to search in
- `function_name`: Name of function to search in
- `**filters`: Additional filter conditions

#### `find_unary_operations(operators=None, contract_name=None, function_name=None, **filters) -> List[Expression]`
Find unary operations.

**Parameters:**
- `operators`: Operators to match - `!`, `-`, `+`, `++`, `--`, etc. (string or list)
- `contract_name`: Name of contract to search in
- `function_name`: Name of function to search in
- `**filters`: Additional filter conditions

### Enhanced Expression Finders

#### `find_expressions_with_operator(operators: Union[str, List[str]], contract_name=None, function_name=None, **filters) -> List[Expression]`
Find expressions with specific operators.

#### `find_expressions_with_value(value: Union[str, int, float], contract_name=None, function_name=None, **filters) -> List[Expression]`
Find literal expressions with specific values.

#### `find_expressions_accessing_member(member_name: str, contract_name=None, function_name=None, **filters) -> List[Expression]`
Find expressions that access a specific member (e.g., 'balance', 'length').

### Pattern-Based Discovery

#### `find_by_pattern(pattern: Union[str, Pattern], **filters) -> List[ASTNode]`
Find nodes matching a regex pattern in their source code.

**Parameters:**
- `pattern`: Regular expression pattern to match (string or compiled Pattern)
- `**filters`: Additional filter conditions

#### `find_by_custom_predicate(predicate: Callable[[ASTNode], bool], element_types=None, **filters) -> List[ASTNode]`
Find nodes matching a custom predicate function.

**Parameters:**
- `predicate`: Function that takes an ASTNode and returns bool
- `element_types`: Optional list of AST node types to filter by
- `**filters`: Additional filter conditions

#### `find_functions_with_source_pattern(pattern: Union[str, Pattern], contract_name=None, **filters) -> List[FunctionDeclaration]`
Find functions containing specific patterns in their source code.

#### `find_functions_with_time_operations(contract_name=None, **filters) -> List[FunctionDeclaration]`
Find functions that contain time-related operations.

#### `find_variables_time_related(contract_name=None, **filters) -> List[VariableDeclaration]`
Find time-related variables.

#### `find_statements_with_source_pattern(pattern: Union[str, Pattern], contract_name=None, function_name=None, **filters) -> List[Statement]`
Find statements containing specific patterns in their source code.

## Fluent Collection Properties

### `contracts: ContractCollection`
Entry point for fluent contract queries.

### `functions: FunctionCollection`
Entry point for fluent function queries.

### `variables: VariableCollection`
Entry point for fluent variable queries.

### `modifiers: ModifierCollection`
Entry point for fluent modifier queries.

### `events: EventCollection`
Entry point for fluent event queries.

### `statements: StatementCollection`
Entry point for fluent statement queries.

### `expressions: ExpressionCollection`
Entry point for fluent expression queries.

## Reference Analysis

#### `find_references_to(target: Union[str, ASTNode], **filters) -> List[ASTNode]`
Find all references to a target symbol or node.

**Parameters:**
- `target`: Symbol name (string) or AST node to find references for
- `**filters`: Additional filter conditions

#### `find_callers_of(target: Union[str, FunctionDeclaration], depth=1, **filters) -> List[FunctionDeclaration]`
Find functions that call the target function.

**Parameters:**
- `target`: Function name (string) or FunctionDeclaration to find callers for
- `depth`: Search depth (currently only depth=1 is supported)
- `**filters`: Additional filter conditions

#### `find_callees_of(source: Union[str, FunctionDeclaration], depth=1, **filters) -> List[FunctionDeclaration]`
Find functions called by the source function.

**Parameters:**
- `source`: Function name (string) or FunctionDeclaration to analyze
- `depth`: Search depth (currently only depth=1 is supported)
- `**filters`: Additional filter conditions

#### `find_call_chains(from_element: Union[str, FunctionDeclaration], to_element: Union[str, FunctionDeclaration], max_depth=10) -> List[List[FunctionDeclaration]]`
Find call chains from one function to another.

**Parameters:**
- `from_element`: Starting function (name or declaration)
- `to_element`: Target function (name or declaration)
- `max_depth`: Maximum chain depth to search (default: 10)

#### `find_definitions_of(name: str, scope=None, **filters) -> List[ASTNode]`
Find definitions of a symbol by name.

#### `find_usages_of(element: Union[str, ASTNode], usage_types=None, **filters) -> List[ASTNode]`
Find all usages of an element.

#### `find_assignments_to(target: Union[str, ASTNode], **filters) -> List[ASTNode]`
Find assignments to a target variable.

#### `find_reads_of(target: Union[str, ASTNode], **filters) -> List[ASTNode]`
Find read operations of a target variable.

#### `find_modifications_of(target: Union[str, ASTNode], **filters) -> List[ASTNode]`
Find modifications of a target variable.

## Data Flow Analysis

#### `trace_variable_flow(variable_name: str, direction='forward', function_name=None, contract_name=None, max_depth=5) -> List[Statement]`
Trace how a variable flows through the code.

**Parameters:**
- `variable_name`: Name of the variable to trace
- `direction`: Flow direction - `'forward'`, `'backward'`, or `'both'`
- `function_name`: Optional function to limit analysis scope
- `contract_name`: Optional contract to limit analysis scope
- `max_depth`: Maximum analysis depth to prevent infinite loops (default: 5)

#### `find_variable_influences(variable_name: str, function_name=None, contract_name=None, **filters) -> List[Statement]`
Find all statements that influence a variable's value (backward flow).

#### `find_variable_effects(variable_name: str, function_name=None, contract_name=None, **filters) -> List[Statement]`
Find all statements affected by a variable's value (forward flow).

#### `trace_flow_between_statements(from_pattern: str, to_pattern: str, function_name=None, contract_name=None, **filters) -> List[List[Statement]]`
Find data flow paths between statement types.

**Parameters:**
- `from_pattern`: Pattern for source statements (e.g., `"require*"`, `"*.call(*)"`)
- `to_pattern`: Pattern for target statements
- `function_name`: Optional function to limit scope
- `contract_name`: Optional contract to limit scope
- `**filters`: Additional filter conditions

#### `find_data_flow_paths(from_point: ASTNode, to_point: ASTNode) -> List[List[Statement]]`
Find all data flow paths between two AST nodes.

#### `get_variable_references_by_function(function: FunctionDeclaration) -> Dict[str, List]`
Get all variable references within a function, organized by variable name.

#### `get_data_flow_statistics() -> Dict[str, Any]`
Get statistics about data flow analysis across the codebase.

## Call Instruction Analysis

#### `find_call_instructions(call_type=None, **filters) -> List[Expression]`
Find call instructions, optionally filtered by call type.

#### `find_external_call_instructions(**filters) -> List[Expression]`
Find only external call instructions.

#### `find_internal_call_instructions(visibility=None, **filters) -> List[Expression]`
Find internal call instructions.

**Parameters:**
- `visibility`: Optional visibility filter - `"private"`, `"public"`, `"internal"`

#### `find_delegate_call_instructions(**filters) -> List[Expression]`
Find delegate call instructions.

#### `find_library_call_instructions(**filters) -> List[Expression]`
Find library call instructions.

#### `find_low_level_call_instructions(**filters) -> List[Expression]`
Find low-level call instructions (.call, .send, .transfer).

#### `find_static_call_instructions(**filters) -> List[Expression]`
Find static call instructions.

#### `find_calls_with_callee_function_name(name: str, sensitivity=True, **filters) -> List[Expression]`
Find calls to functions with specific name.

**Parameters:**
- `name`: Function name to match
- `sensitivity`: Case-sensitive matching (default: True)

#### `find_calls_with_callee_function_signature(signature: str, **filters) -> List[Expression]`
Find calls with specific function signature.

#### `find_calls_with_called_function_name_prefix(prefix: str, **filters) -> List[Expression]`
Find calls to functions with names starting with prefix.

## Import Analysis

#### `import_analyzer()`
Get an import analyzer instance for dependency analysis.

#### `find_imports(pattern=None, **filters) -> List`
Find import statements matching a pattern.

**Parameters:**
- `pattern`: Pattern to match import paths/symbols (supports wildcards)

#### `find_contracts_using_imports(import_patterns: Union[str, List[str]], **filters)`
Find contracts that use specific imports.

#### `find_functions_calling_imported(import_patterns: Union[str, List[str]], **filters)`
Find functions that call symbols from specific imports.

## Set Operations

#### `intersect(*element_sets) -> List[ASTNode]`
Find intersection of multiple element sets.

#### `union(*element_sets) -> List[ASTNode]`
Find union of multiple element sets.

#### `difference(base_set, subtract_set) -> List[ASTNode]`
Find difference between two element sets.

## Element Manipulation

#### `filter_elements(elements, **filter_conditions) -> List[ASTNode]`
Filter elements based on arbitrary conditions.

#### `group_elements(elements, group_by_attribute: str) -> Dict[str, List[ASTNode]]`
Group elements by a specific attribute.

#### `sort_elements(elements, sort_by_attribute: str, reverse=False) -> List[ASTNode]`
Sort elements by a specific attribute.

## Context Analysis

#### `find_containing_elements(element: ASTNode, container_types=None, **filters) -> List[ASTNode]`
Find elements that contain the given element.

#### `find_contained_elements(container: ASTNode, element_types=None, **filters) -> List[ASTNode]`
Find elements contained within the given container.

#### `find_sibling_elements(element: ASTNode, sibling_types=None, **filters) -> List[ASTNode]`
Find sibling elements of the given element.

#### `get_surrounding_context(element: ASTNode, context_radius=1, **filters) -> Dict[str, Any]`
Get surrounding context for an element.

## Pattern Matching

#### `find_by_ast_pattern(pattern, **filters) -> List[ASTNode]`
Find nodes matching an AST pattern.

#### `find_elements_matching_all(conditions: List[Callable[[ASTNode], bool]], **filters) -> List[ASTNode]`
Find elements that match ALL provided conditions.

#### `find_elements_matching_any(conditions: List[Callable[[ASTNode], bool]], **filters) -> List[ASTNode]`
Find elements that match ANY provided conditions.

## Analysis and Metrics

#### `extract_properties(elements: List[ASTNode], property_names: List[str]) -> List[Dict]`
Extract specified properties from elements.

#### `extract_conditions(conditional_elements: List[ASTNode]) -> List[Dict]`
Extract conditions from conditional elements.

#### `get_metrics(elements: List[ASTNode], metric_types=None) -> Dict[str, Any]`
Get metrics for a collection of elements.

#### `analyze_complexity(elements: List[ASTNode], metrics=None) -> Dict[str, Any]`
Analyze complexity of elements.

#### `get_statistics() -> Dict[str, Any]`
Get comprehensive statistics about the loaded codebase.

#### `get_contract_names() -> List[str]`
Get names of all loaded contracts.

## Quick Usage Examples

```python
from sol_query import SolidityQueryEngine

# Initialize
engine = SolidityQueryEngine("path/to/contracts")

# Find external functions
external_funcs = engine.find_functions(visibility="external")

# Security analysis
risky_functions = (engine.functions
                  .external()
                  .payable()
                  .with_external_calls())

# Find delegate calls
delegate_calls = engine.find_delegate_call_instructions()

# Data flow analysis
flow = engine.trace_variable_flow("balance", direction="both")

# Pattern matching
assembly = engine.find_by_pattern(r"assembly\s*\{")
```

## JSON Serialization

### LLMSerializer

The `LLMSerializer` class provides configurable JSON serialization for analysis results, particularly useful for LLM integration and data export.

#### Constructor

```python
from sol_query.utils.serialization import LLMSerializer, SerializationLevel

serializer = LLMSerializer(level: SerializationLevel = SerializationLevel.DETAILED)
```

**Parameters:**
- `level`: Default serialization detail level (`SUMMARY`, `DETAILED`, or `FULL`)

#### Serialization Levels

- **`SerializationLevel.SUMMARY`**: Basic information only
- **`SerializationLevel.DETAILED`**: Comprehensive information (default)
- **`SerializationLevel.FULL`**: Complete information including additional source details

#### Methods

##### `serialize_node(node: ASTNode, level: Optional[SerializationLevel] = None) -> Dict[str, Any]`

Serialize a single AST node to a dictionary.

**Returns a dictionary containing:**
- `node_type`: The type of AST node
- `source_code_preview`: A preview of the source code for this node (truncated for long code)
- `source_location`: Location information (line, column, byte positions)
- Additional type-specific fields based on the node type

**Example:**
```python
serializer = LLMSerializer(SerializationLevel.DETAILED)
contract = engine.contracts.with_name("Token").first()
serialized = serializer.serialize_node(contract)

print(serialized["source_code_preview"])  # Shows contract source code preview
```

##### `serialize_collection(collection: BaseCollection, level: Optional[SerializationLevel] = None, limit: Optional[int] = None) -> Dict[str, Any]`

Serialize a collection of nodes.

**Parameters:**
- `collection`: The collection to serialize
- `level`: Serialization level override
- `limit`: Maximum number of items to include

**Returns:**
```python
{
    "collection_type": "ContractsCollection",
    "total_count": 10,
    "returned_count": 5,
    "items": [
        {"node_type": "contract_declaration", "source_code_preview": "contract Token...", ...},
        ...
    ]
}
```

##### `serialize_query_result(result: Union[ASTNode, BaseCollection, List[ASTNode]], level: Optional[SerializationLevel] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

Serialize any query result with metadata.

**Returns:**
```python
{
    "query_timestamp": "2024-01-15T10:30:00.000Z",
    "serialization_level": "detailed",
    "result_type": "collection",
    "metadata": {},
    "result": {...}
}
```

##### `to_json(data: Any, indent: Optional[int] = 2) -> str`

Convert serialized data to JSON string.

#### Complete Example

```python
from sol_query import SolidityQueryEngine
from sol_query.utils.serialization import LLMSerializer, SerializationLevel

# Load contracts
engine = SolidityQueryEngine("contracts/")

# Create serializer
serializer = LLMSerializer(SerializationLevel.DETAILED)

# Serialize individual nodes
contract = engine.contracts.with_name("Token").first()
contract_data = serializer.serialize_node(contract)
print(f"Contract source: {contract_data['source_code_preview']}")

# Serialize collections
functions = engine.functions.external()
functions_data = serializer.serialize_collection(functions, limit=10)

# Export to JSON file
import json
with open("analysis.json", "w") as f:
    json.dump(functions_data, f, indent=2)

# Full query result serialization
result = serializer.serialize_query_result(
    engine.functions.payable().with_external_calls(),
    metadata={"analysis_type": "security_review"}
)
```

#### Source Code Preview Field

All serialized nodes include a `source_code_preview` field containing a preview of the source code for that AST element:

- **Contracts**: Contract definition (truncated for long contracts)
- **Functions**: Function implementation (truncated for long functions)
- **Variables**: Variable declaration
- **Statements**: Individual statement source
- **Expressions**: Expression source code

**Preview Format:**
- **Short code (≤200 chars)**: Complete source code
- **Long code (>200 chars)**: First 100 characters + "..." + last 100 characters

This provides manageable source code previews for LLM processing while maintaining readability and keeping payload sizes reasonable.
