# API Reference

Complete reference for all Sol-Query classes and methods.

## Core Classes

### SolidityQueryEngine

The main query engine class providing both traditional and fluent query interfaces.

#### Constructor

```python
SolidityQueryEngine(source_paths: Optional[Union[str, Path, List[Union[str, Path]]]] = None)
```

Initialize the query engine, optionally loading source files.

#### Loading Methods

- `load_sources(source_paths)` - Load Solidity source files or directories

#### Traditional Finder Methods

**Contract Finders:**
- `find_contracts(name_patterns=None, inheritance=None, kind=None, **filters)` - Find contracts
- `find_structs(name_patterns=None, contract_name=None, **filters)` - Find struct declarations
- `find_enums(name_patterns=None, contract_name=None, **filters)` - Find enum declarations
- `find_errors(name_patterns=None, contract_name=None, **filters)` - Find error declarations

**Function Finders:**
- `find_functions(name_patterns=None, visibility=None, modifiers=None, state_mutability=None, contract_name=None, with_external_calls=None, with_asset_transfers=None, with_external_calls_deep=None, with_asset_transfers_deep=None, **filters)` - Find functions
- `find_modifiers(name_patterns=None, contract_name=None, **filters)` - Find modifiers

**Variable Finders:**
- `find_variables(name_patterns=None, type_patterns=None, visibility=None, is_state_variable=None, contract_name=None, **filters)` - Find variables

**Event Finders:**
- `find_events(name_patterns=None, contract_name=None, **filters)` - Find events

**Statement Finders:**
- `find_statements(statement_types=None, contract_name=None, function_name=None, **filters)` - Find statements
- `find_loops(loop_types=None, **filters)` - Find loop statements
- `find_conditionals(**filters)` - Find if/else statements
- `find_assignments(**filters)` - Find assignment statements
- `find_returns(**filters)` - Find return statements
- `find_requires(**filters)` - Find require statements
- `find_emits(**filters)` - Find emit statements

**Expression Finders:**
- `find_expressions(expression_types=None, contract_name=None, function_name=None, **filters)` - Find expressions
- `find_calls(target_patterns=None, contract_name=None, function_name=None, **filters)` - Find function calls
- `find_literals(literal_types=None, contract_name=None, function_name=None, **filters)` - Find literals
- `find_identifiers(name_patterns=None, contract_name=None, function_name=None, **filters)` - Find identifiers
- `find_binary_operations(**filters)` - Find binary operations
- `find_unary_operations(**filters)` - Find unary operations

#### Advanced Analysis Methods

**Call Graph Analysis:**
- `find_callers_of(target, depth=1, **filters)` - Find functions that call the target
- `find_callees_of(source, depth=1, **filters)` - Find functions called by the source
- `find_call_chains(from_element, to_element, max_depth=10)` - Find call chains between functions

**External Call and Asset Transfer Analysis:**
- Functions with external calls (shallow): Direct external contract calls
- Functions with external calls (deep): External calls anywhere in call tree
- Functions with asset transfers (shallow): Direct ETH sends or token transfers
- Functions with asset transfers (deep): Asset transfers anywhere in call tree

**Reference Tracking:**
- `find_references_to(target, **filters)` - Find all references to a symbol
- `find_definitions_of(name, scope=None, **filters)` - Find symbol definitions
- `find_usages_of(element, usage_types=None, **filters)` - Find usages of an element
- `find_assignments_to(target, **filters)` - Find assignments to a variable
- `find_reads_of(target, **filters)` - Find read operations of a variable
- `find_modifications_of(target, **filters)` - Find modifications of a variable

**Pattern Matching:**
- `find_by_pattern(pattern, **filters)` - Find nodes matching a regex pattern
- `find_by_ast_pattern(pattern, **filters)` - Find nodes matching an AST pattern
- `find_by_custom_predicate(predicate_func, element_types=None, **filters)` - Find nodes matching custom logic

**Composite Queries:**
- `find_elements_matching_all(conditions, **filters)` - Find elements matching ALL conditions
- `find_elements_matching_any(conditions, **filters)` - Find elements matching ANY condition

#### Utility Methods

**Set Operations:**
- `intersect(*element_sets)` - Find intersection of multiple element sets
- `union(*element_sets)` - Find union of multiple element sets
- `difference(base_set, subtract_set)` - Find difference between two sets

**Element Manipulation:**
- `filter_elements(elements, **filter_conditions)` - Filter elements by conditions
- `group_elements(elements, group_by_attribute)` - Group elements by attribute
- `sort_elements(elements, sort_by_attribute, reverse=False)` - Sort elements by attribute

#### Fluent Collection Properties

- `contracts` - Entry point for contract queries (returns ContractCollection)
- `functions` - Entry point for function queries (returns FunctionCollection)
- `variables` - Entry point for variable queries (returns VariableCollection)
- `modifiers` - Entry point for modifier queries (returns ModifierCollection)
- `events` - Entry point for event queries (returns EventCollection)
- `statements` - Entry point for statement queries (returns StatementCollection)
- `expressions` - Entry point for expression queries (returns ExpressionCollection)

#### Statistics and Metadata

- `get_statistics()` - Get comprehensive codebase statistics
- `get_contract_names()` - Get names of all loaded contracts

## Collection Classes

### BaseCollection

Base class for all collections with common functionality.

**Common Methods:**
- `__len__()` - Get collection size
- `__iter__()` - Iterate over elements
- `__getitem__(index)` - Get element by index
- `list()` - Convert to Python list
- `first()` - Get first element or None
- `count()` - Get element count
- `is_empty()` - Check if collection is empty
- `to_dict()` - Convert to JSON-serializable dict

### ContractCollection

Collection of contract declarations with fluent query methods.

**Filtering Methods:**
- `with_name(pattern)` - Filter by name pattern
- `with_name_not(pattern)` - Exclude by name pattern
- `with_names(names)` - Filter by exact name list
- `with_inheritance(base_contract)` - Filter by inheritance
- `with_function_name(name)` - Filter contracts having function
- `with_event_name(name)` - Filter contracts having event
- `with_state_variable(name)` - Filter contracts having variable

**Type Filters:**
- `interfaces()` - Get only interface contracts
- `libraries()` - Get only library contracts
- `main_contracts()` - Get only regular contracts

**Type Negation Filters:**
- `not_interfaces()` - Get contracts that are NOT interfaces
- `not_libraries()` - Get contracts that are NOT libraries

**Inheritance and Feature Negation Filters:**
- `not_with_inheritance(base_contract)` - Contracts that do NOT inherit from specified contract
- `without_function_name(name)` - Contracts that do NOT have function with specified name
- `without_event_name(name)` - Contracts that do NOT have event with specified name
- `without_state_variable(name)` - Contracts that do NOT have state variable with specified name

**Navigation Methods:**
- `get_functions()` - Get all functions from contracts
- `get_variables()` - Get all variables from contracts
- `get_events()` - Get all events from contracts
- `get_modifiers()` - Get all modifiers from contracts

### FunctionCollection

Collection of function declarations with fluent query methods.

**Filtering Methods:**
- `with_name(pattern)` - Filter by name pattern
- `with_signature(signature)` - Filter by exact signature
- `with_visibility(visibility)` - Filter by visibility
- `with_modifiers(modifiers)` - Filter by modifier presence
- `with_modifier_regex(pattern)` - Filter by modifier regex
- `without_modifiers()` - Filter functions without modifiers
- `with_parameter_count(count)` - Filter by parameter count
- `with_parameter_type(type_pattern)` - Filter by parameter type

**Visibility Shortcuts:**
- `external()` - Get only external functions
- `public()` - Get only public functions
- `internal()` - Get only internal functions
- `private()` - Get only private functions

**Visibility Negation Filters:**
- `not_external()` - Get functions that are NOT external
- `not_public()` - Get functions that are NOT public
- `not_internal()` - Get functions that are NOT internal
- `not_private()` - Get functions that are NOT private
- `not_with_visibility(visibility)` - Generic negation for visibility

**State Mutability Shortcuts:**
- `view()` - Get only view functions
- `pure()` - Get only pure functions
- `payable()` - Get only payable functions

**State Mutability Negation Filters:**
- `not_view()` - Get functions that are NOT view
- `not_pure()` - Get functions that are NOT pure
- `not_payable()` - Get functions that are NOT payable

**Special Function Types:**
- `constructors()` - Get only constructor functions
- `not_constructors()` - Get functions that are NOT constructors

**Modifier Negation Filters:**
- `without_modifier(modifier)` - Functions without specific modifier
- `without_any_modifiers_matching(modifiers)` - Functions without any of the specified modifiers

**Parent Contract Access:**
- `get_parent_contract(function)` - Get the parent contract of a function
- `from_contract(contract_name)` - Filter functions from a specific contract

**External Call and Asset Transfer Filters:**
- `with_external_calls()` - Functions that directly contain external calls
- `without_external_calls()` - Functions that do NOT directly contain external calls
- `with_asset_transfers()` - Functions that directly contain asset transfers (ETH send, token transfers)
- `without_asset_transfers()` - Functions that do NOT directly contain asset transfers
- `with_external_calls_deep()` - Functions whose call tree includes external calls (deep analysis)
- `without_external_calls_deep()` - Functions whose call tree does NOT include external calls
- `with_asset_transfers_deep()` - Functions whose call tree includes asset transfers (deep analysis)
- `without_asset_transfers_deep()` - Functions whose call tree does NOT include asset transfers
- `with_external_call_targets(targets)` - Functions that call specific external targets
- `with_asset_transfer_types(types)` - Functions that perform specific types of asset transfers

### VariableCollection

Collection of variable declarations with fluent query methods.

**Filtering Methods:**
- `with_name(pattern)` - Filter by name pattern
- `with_type(type_pattern)` - Filter by type pattern
- `with_visibility(visibility)` - Filter by visibility

**Visibility Shortcuts:**
- `public()` - Get only public variables
- `private()` - Get only private variables
- `internal()` - Get only internal variables

**Visibility Negation Filters:**
- `not_public()` - Get variables that are NOT public
- `not_private()` - Get variables that are NOT private
- `not_internal()` - Get variables that are NOT internal
- `not_with_visibility(visibility)` - Generic negation for visibility

**Special Variable Types:**
- `constants()` - Get only constant variables
- `immutable()` - Get only immutable variables
- `state_variables()` - Get only state variables

**Special Variable Type Negation Filters:**
- `not_constants()` - Get variables that are NOT constants
- `not_immutable()` - Get variables that are NOT immutable
- `not_state_variables()` - Get variables that are NOT state variables
- `not_with_type(type_pattern)` - Variables that do NOT match type pattern

**Parent Contract Access:**
- `get_parent_contract(variable)` - Get the parent contract of a variable
- `from_contract(contract_name)` - Filter variables from a specific contract

### ModifierCollection

Collection of modifier declarations with fluent query methods.

**Filtering Methods:**
- `with_name(pattern)` - Filter by name pattern
- `with_parameter_count(count)` - Filter by parameter count

### EventCollection

Collection of event declarations with fluent query methods.

**Filtering Methods:**
- `with_name(pattern)` - Filter by name pattern
- `with_parameter_count(count)` - Filter by parameter count

### StatementCollection

Collection of statements with fluent query methods.

**Filtering Methods:**
- `with_type(statement_type)` - Filter by statement type

**Statement Type Shortcuts:**
- `returns()` - Get only return statements
- `blocks()` - Get only block statements

### ExpressionCollection

Collection of expressions with fluent query methods.

**Filtering Methods:**
- `with_type(expression_type)` - Filter by expression type

**Expression Type Shortcuts:**
- `calls()` - Get only call expressions
- `identifiers()` - Get only identifier expressions
- `literals()` - Get only literal expressions

## AST Node Classes

### Core Node Classes

**ASTNode** - Base class for all AST nodes
- `source_location` - Location in source code
- `raw_node` - Original tree-sitter node
- `node_type` - Type of AST node
- `get_source_code()` - Extract source code text

**ContractDeclaration** - Represents a contract, interface, or library
- `name` - Contract name
- `kind` - Contract type ("contract", "interface", "library")
- `inheritance` - List of inherited contracts
- `functions` - List of function declarations
- `variables` - List of state variables
- `events` - List of event declarations
- `modifiers` - List of modifier declarations
- `structs` - List of struct declarations
- `enums` - List of enum declarations
- `errors` - List of error declarations

**FunctionDeclaration** - Represents a function
- `name` - Function name
- `visibility` - Function visibility
- `state_mutability` - State mutability
- `is_constructor` - Whether this is a constructor
- `is_receive` - Whether this is a receive function
- `is_fallback` - Whether this is a fallback function
- `is_virtual` - Whether function is virtual
- `is_override` - Whether function overrides
- `parameters` - Function parameters
- `return_parameters` - Return parameters
- `modifiers` - Applied modifiers
- `body` - Function body

**VariableDeclaration** - Represents a variable
- `name` - Variable name
- `type_name` - Variable type
- `visibility` - Variable visibility
- `is_constant` - Whether variable is constant
- `is_immutable` - Whether variable is immutable
- `initial_value` - Initial value expression

### Enums and Constants

**Visibility** - Enum for visibility levels
- `PUBLIC` - "public"
- `PRIVATE` - "private"
- `INTERNAL` - "internal"
- `EXTERNAL` - "external"

**StateMutability** - Enum for state mutability
- `PURE` - "pure"
- `VIEW` - "view"
- `NONPAYABLE` - "nonpayable"
- `PAYABLE` - "payable"

**NodeType** - Enum for AST node types
- Various node type constants

## Error Handling

**ParseError** - Raised when parsing fails
- `source_file` - Source file path
- `line` - Error line number
- `column` - Error column number

## Pattern Matching

Sol-Query supports flexible pattern matching:

- **Exact matching**: `"transfer"` matches only "transfer"
- **Wildcard patterns**: `"transfer*"` matches "transfer", "transferFrom", etc.
- **Contains patterns**: `"*burn*"` matches "burnTokens", "preBurn", etc.
- **Regex patterns**: Full regex support for complex patterns
- **Multiple patterns**: `["mint", "burn"]` matches either "mint" or "burn"

## JSON Serialization

All AST nodes and collections support JSON serialization via the `to_dict()` method for LLM integration.
