# Sol-Query API Reference

Complete reference for the Sol-Query Solidity code analysis engine.

## Quick Start

```python
from sol_query import SolidityQueryEngine

# Initialize and load sources
engine = SolidityQueryEngine("path/to/contracts")
# or
engine = SolidityQueryEngine()
engine.load_sources(["contract1.sol", "directory/"])

# Traditional API
contracts = engine.find_contracts(name_patterns="*Token*")
functions = engine.find_functions(visibility="external", with_external_calls=True)

# Fluent API
external_funcs = engine.contracts.with_name("MyContract").functions.external()
```

## Core Classes

### SolidityQueryEngine

Main query engine providing both traditional and fluent interfaces.

#### Constructor
```python
SolidityQueryEngine(source_paths: Optional[Union[str, Path, List[Union[str, Path]]]] = None)
```

#### Source Management
- `load_sources(source_paths)` - Load Solidity files/directories
- `get_statistics()` - Get parsing and analysis statistics

#### Traditional API Methods

**Contract Queries:**
- `find_contracts(name_patterns=None, inheritance=None, kind=None, **filters)`
  - `name_patterns`: str/List[str]/Pattern - Name patterns to match
  - `inheritance`: str/List[str] - Base contracts/interfaces
  - `kind`: str - "contract", "interface", "library", "abstract"

- `find_structs(name_patterns=None, contract_name=None, **filters)`
- `find_enums(name_patterns=None, contract_name=None, **filters)`
- `find_errors(name_patterns=None, contract_name=None, **filters)`

**Function Queries:**
- `find_functions(name_patterns=None, visibility=None, modifiers=None, state_mutability=None, contract_name=None, with_external_calls=None, with_asset_transfers=None, with_external_calls_deep=None, with_asset_transfers_deep=None, **filters)`
  - `visibility`: Visibility enum or list - Function visibility
  - `state_mutability`: StateMutability enum or list - State mutability
  - `modifiers`: str/List[str] - Required modifiers
  - `with_external_calls`: bool - Has direct external calls
  - `with_external_calls_deep`: bool - Has external calls (including transitively)
  - `with_asset_transfers`: bool - Has direct asset transfers
  - `with_asset_transfers_deep`: bool - Has asset transfers (including transitively)

- `find_modifiers(name_patterns=None, contract_name=None, **filters)`

**Variable Queries:**
- `find_variables(name_patterns=None, type_patterns=None, visibility=None, is_state_variable=None, contract_name=None, **filters)`
  - `type_patterns`: str/List[str] - Type name patterns
  - `is_state_variable`: bool - Filter for state variables only

**Event Queries:**
- `find_events(name_patterns=None, contract_name=None, **filters)`

**Statement Queries:**
- `find_statements(statement_types=None, contract_name=None, function_name=None, **filters)`
- `find_loops(loop_types=None, **filters)`
- `find_conditionals(**filters)`
- `find_assignments(**filters)`
- `find_returns(**filters)`
- `find_requires(**filters)`
- `find_emits(**filters)`

**Expression Queries:**
- `find_expressions(expression_types=None, **filters)`
- `find_calls(call_types=None, function_names=None, **filters)`
  - `call_types`: CallType enum or list - Type of calls to find
  - `function_names`: str/List[str] - Function names being called
- `find_literals(literal_types=None, values=None, **filters)`
- `find_identifiers(names=None, **filters)`

**Call Analysis:**
- `find_external_calls(**filters)` - Find all external calls
- `find_asset_transfers(**filters)` - Find asset transfer operations
- `analyze_call_graph(contract_name=None)` - Build call graph analysis

**Data Flow Analysis:**
- `trace_variable_flow(variable_name, function_name, contract_name=None)`
- `find_variable_influences(variable_name, function_name, contract_name=None)`
- `find_variable_effects(variable_name, function_name, contract_name=None)`
- `trace_flow_between_statements(source_stmt, target_stmt)`

**Import Analysis:**
- `analyze_imports(pattern="*")` - Analyze import dependencies
- `find_import_usage(import_pattern)` - Find usage of imported symbols

#### Fluent API Properties

Access collections for fluent querying:
- `contracts` → ContractCollection
- `functions` → FunctionCollection
- `variables` → VariableCollection
- `modifiers` → ModifierCollection
- `events` → EventCollection
- `statements` → StatementCollection
- `expressions` → ExpressionCollection

## Collection Classes

All collections support method chaining and set operations.

### ContractCollection

**Filtering:**
- `with_name(patterns)` - Filter by name patterns
- `interfaces()` - Interface contracts only
- `libraries()` - Library contracts only
- `abstract()` - Abstract contracts only
- `inheriting_from(base_names)` - Contracts inheriting from bases
- `using_imports(import_patterns)` - Contracts using specific imports

**Navigation:**
- `get_functions()` → FunctionCollection
- `get_variables()` → VariableCollection
- `get_events()` → EventCollection
- `get_modifiers()` → ModifierCollection

**Set Operations:**
- `intersect(other)` - Intersection with another collection
- `union(other)` - Union with another collection
- `subtract(other)` - Difference from another collection

### FunctionCollection

**Visibility Filters:**
- `external()` - External functions only
- `public()` - Public functions only
- `internal()` - Internal functions only
- `private()` - Private functions only

**State Mutability Filters:**
- `view()` - View functions only
- `pure()` - Pure functions only
- `payable()` - Payable functions only

**Special Function Types:**
- `constructors()` - Constructor functions
- `modifiers_applied(modifier_names)` - Functions with specific modifiers

**Call Analysis Filters:**
- `with_external_calls(deep=False)` - Functions with external calls
- `without_external_calls(deep=False)` - Functions without external calls
- `with_asset_transfers(deep=False)` - Functions with asset transfers
- `without_asset_transfers(deep=False)` - Functions without asset transfers

**Data Flow Methods:**
- `reading_variable(variable_name)` - Functions reading a variable
- `writing_variable(variable_name)` - Functions writing a variable
- `data_flow_between(source, target)` - Functions with data flow between statements

### VariableCollection

**Type Filters:**
- `with_type(type_patterns)` - Variables matching type patterns
- `state_variables()` - State variables only
- `local_variables()` - Local variables only

**Visibility Filters:**
- `public()` - Public state variables
- `private()` - Private state variables
- `internal()` - Internal state variables

### StatementCollection

**Type Filters:**
- `loops()` - Loop statements
- `conditionals()` - If/else statements
- `assignments()` - Assignment statements
- `returns()` - Return statements
- `requires()` - Require statements
- `emits()` - Emit statements

**Source Pattern Filters:**
- `with_source_pattern(pattern)` - Statements matching source code pattern

**Data Flow Methods:**
- `influenced_by_variable(variable_name)` - Statements influenced by variable
- `influencing_variable(variable_name)` - Statements influencing variable
- `expand_backward_flow(max_depth=5)` - Expand to influencing statements
- `expand_forward_flow(max_depth=5)` - Expand to influenced statements

### ExpressionCollection

**Type Filters:**
- `calls()` - Call expressions
- `literals()` - Literal expressions
- `identifiers()` - Identifier expressions
- `binary_ops()` - Binary expressions
- `member_access()` - Member access expressions

**Call-Specific Filters:**
- `external_calls()` - External call expressions
- `internal_calls()` - Internal call expressions
- `library_calls()` - Library call expressions
- `low_level_calls()` - Low-level call expressions

**Value Filters:**
- `with_literal_value(values)` - Literals with specific values
- `with_operator(operators)` - Binary expressions with specific operators

## AST Node Classes

### Core Node Properties
All AST nodes inherit these properties:
- `node_type`: NodeType enum
- `source_location`: SourceLocation with file, line, column info
- `get_source_code()` → str - Get the source code text
- `get_children()` → List[ASTNode] - Get child nodes
- `to_dict()` → Dict - Convert to JSON-serializable dict

### ContractDeclaration
- `name`: str - Contract name
- `kind`: str - "contract", "interface", "library", "abstract"
- `inheritance`: List[str] - Inherited contract names
- `functions`: List[FunctionDeclaration]
- `variables`: List[VariableDeclaration]
- `events`: List[EventDeclaration]
- `modifiers`: List[ModifierDeclaration]
- `structs`: List[StructDeclaration]
- `enums`: List[EnumDeclaration]
- `errors`: List[ErrorDeclaration]

**Methods:**
- `is_interface()` → bool
- `is_library()` → bool
- `is_abstract()` → bool
- `get_function(name)` → Optional[FunctionDeclaration]

### FunctionDeclaration
- `name`: str - Function name
- `visibility`: Visibility enum
- `state_mutability`: StateMutability enum
- `is_constructor`: bool
- `is_receive`: bool
- `is_fallback`: bool
- `is_virtual`: bool
- `is_override`: bool
- `parameters`: List[Parameter]
- `return_parameters`: List[Parameter]
- `modifiers`: List[str] - Applied modifier names
- `body`: Optional[Block]

**Analysis Properties:**
- `has_external_calls`: bool
- `has_asset_transfers`: bool
- `external_call_targets`: List[str]
- `asset_transfer_types`: List[str]

**Methods:**
- `get_signature()` → str
- `is_external()` → bool
- `is_public()` → bool
- `is_internal()` → bool
- `is_private()` → bool
- `is_view()` → bool
- `is_pure()` → bool
- `is_payable()` → bool

### VariableDeclaration
- `name`: str - Variable name
- `type_name`: str - Variable type
- `visibility`: Optional[Visibility] - For state variables
- `is_constant`: bool
- `is_immutable`: bool
- `initial_value`: Optional[Expression]

**Methods:**
- `is_state_variable()` → bool
- `get_all_references()` → List[VariableReference]
- `get_reads()` → List[VariableReference]
- `get_writes()` → List[VariableReference]

### CallExpression
- `function`: Expression - Function being called
- `arguments`: List[Expression] - Call arguments
- `call_type`: Optional[str] - Type of call

**Methods:**
- `get_call_type()` → Optional[CallType]
- `is_external_call()` → bool
- `is_internal_call()` → bool
- `is_library_call()` → bool
- `is_low_level_call()` → bool
- `get_call_signature()` → Optional[str]
- `get_call_info()` → CallMetadata
- `get_call_args()` → List[Any]
- `get_call_value()` → Optional[str]
- `get_call_gas()` → Optional[str]

## Enums and Constants

### Visibility
```python
class Visibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"
    EXTERNAL = "external"
```

### StateMutability
```python
class StateMutability(str, Enum):
    PURE = "pure"
    VIEW = "view"
    NONPAYABLE = "nonpayable"
    PAYABLE = "payable"
```

### CallType
```python
class CallType(str, Enum):
    # Function call types
    EXTERNAL = "external"        # External contract calls
    INTERNAL = "internal"        # Internal function calls
    LIBRARY = "library"          # Library function calls
    LOW_LEVEL = "low_level"      # Low-level calls (.call, .delegatecall, etc.)

    # Visibility-based types
    PUBLIC = "public"            # Public function calls
    PRIVATE = "private"          # Private function calls

    # Special call types
    EVENT = "event"              # Event emissions (emit)
    SOLIDITY = "solidity"        # Built-in Solidity functions

    # Constructor and creation calls
    NEW_ARR = "new_arr"          # Array creation
    NEW_ELEMENTARY_TYPE = "new_elementary_type"
    NEW_STRUCT = "new_struct"    # Struct creation
    NEW_CONTRACT = "new_contract" # Contract creation

    # Conversion and casting
    TYPE_CONVERSION = "type_conversion"

    # Assembly and special
    ASSEMBLY = "assembly"        # Assembly block calls
    DELEGATE = "delegate"        # Delegate calls specifically
    STATIC = "static"           # Static calls specifically

    UNKNOWN = "unknown"
```

### NodeType
```python
class NodeType(str, Enum):
    # Declarations
    CONTRACT = "contract"
    FUNCTION = "function"
    MODIFIER = "modifier"
    VARIABLE = "variable"
    STRUCT = "struct"
    ENUM = "enum"
    EVENT = "event"
    ERROR = "error"
    IMPORT = "import"

    # Statements
    IF_STATEMENT = "if_statement"
    FOR_STATEMENT = "for_statement"
    WHILE_STATEMENT = "while_statement"
    DO_WHILE_STATEMENT = "do_while_statement"
    RETURN_STATEMENT = "return_statement"
    EMIT_STATEMENT = "emit_statement"
    REQUIRE_STATEMENT = "require_statement"
    ASSERT_STATEMENT = "assert_statement"
    REVERT_STATEMENT = "revert_statement"
    EXPRESSION_STATEMENT = "expression_statement"
    BLOCK = "block"
    STATEMENT = "statement"

    # Expressions
    CALL_EXPRESSION = "call_expression"
    BINARY_EXPRESSION = "binary_expression"
    UNARY_EXPRESSION = "unary_expression"
    ASSIGNMENT_EXPRESSION = "assignment_expression"
    TERNARY_EXPRESSION = "ternary_expression"
    TUPLE_EXPRESSION = "tuple_expression"
    TYPE_CAST_EXPRESSION = "type_cast_expression"
    UPDATE_EXPRESSION = "update_expression"
    META_TYPE_EXPRESSION = "meta_type_expression"
    PAYABLE_CONVERSION = "payable_conversion_expression"
    STRUCT_EXPRESSION = "struct_expression"
    PARENTHESIZED_EXPRESSION = "parenthesized_expression"
    ARRAY_ACCESS = "array_access"
    SLICE_ACCESS = "slice_access"
    INLINE_ARRAY_EXPRESSION = "inline_array_expression"
    NEW_EXPRESSION = "new_expression"
    USER_DEFINED_TYPE_EXPR = "user_defined_type_expr"
    PRIMITIVE_TYPE_EXPR = "primitive_type_expr"
    IDENTIFIER = "identifier"
    LITERAL = "literal"
    MEMBER_ACCESS = "member_access"
    INDEX_ACCESS = "index_access"
```

## Advanced Features

### Query Composition

Combine queries using boolean logic:

```python
# AND operation (method chaining)
results = engine.contracts.with_name("*Token*").functions.external().view()

# Set operations
external_funcs = engine.functions.external()
payable_funcs = engine.functions.payable()

# Union
all_funcs = external_funcs.union(payable_funcs)

# Intersection
external_payable = external_funcs.intersect(payable_funcs)

# Difference
non_payable_external = external_funcs.subtract(payable_funcs)
```

### Filtering with Custom Predicates

```python
# Filter with lambda functions
complex_functions = engine.functions.where(
    lambda f: len(f.parameters) > 3 and f.is_payable()
)

# Negation filters
non_view_functions = engine.functions.and_not(lambda f: f.is_view())
```

### Pattern Matching

Supports wildcards and regex:
- `*` - Match any characters
- `?` - Match single character
- `[abc]` - Match any of a, b, c
- Regex patterns for complex matching

### Data Flow Analysis

```python
# Trace variable data flow
flow_path = engine.trace_variable_flow("amount", "transfer", "MyToken")

# Find what influences a variable
influences = engine.find_variable_influences("balance", "withdraw")

# Find what a variable affects
effects = engine.find_variable_effects("owner", "changeOwner")
```

### Import Analysis

```python
# Analyze import dependencies
dependencies = engine.analyze_imports("*OpenZeppelin*")

# Find usage of imported symbols
usage = engine.find_import_usage("*SafeMath*")
```

### Serialization

```python
# Convert results to JSON
from sol_query.utils.serialization import LLMSerializer, SerializationLevel

serializer = LLMSerializer(SerializationLevel.DETAILED)
json_data = serializer.serialize_collection(engine.contracts)
```

## Error Handling

- `ParseError` - Raised for syntax/parsing errors
- `FileNotFoundError` - Missing source files
- Invalid patterns return empty collections
- Type mismatches are gracefully handled

## Performance Tips

- Use specific patterns instead of broad wildcards
- Filter early in query chains
- Use `deep=False` for shallow analysis when possible
- Cache engine instances for repeated queries
- Use `get_statistics()` to monitor parsing performance