# Architecture Overview

Sol-Query is designed as a comprehensive Solidity code analysis engine built on tree-sitter with a clean, modular architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Sol-Query Engine                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │ Traditional API │  │   Fluent API    │  │   Statistics  │ │
│  │                 │  │                 │  │               │ │
│  │ find_contracts  │  │ .contracts      │  │ get_stats()   │ │
│  │ find_functions  │  │ .functions      │  │ get_names()   │ │
│  │ find_variables  │  │ .variables      │  │               │ │
│  │      ...        │  │      ...        │  │               │ │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
├─────────────────────────────────────────────────────────────┤
│                    Query Collections                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │ ContractColln   │  │ FunctionColln   │  │ VariableColln │ │
│  │                 │  │                 │  │               │ │
│  │ .with_name()    │  │ .external()     │  │ .public()     │ │
│  │ .interfaces()   │  │ .view()         │  │ .with_type()  │ │
│  │ .get_functions()│  │ .with_name()    │  │               │ │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
├─────────────────────────────────────────────────────────────┤
│                      Core Engine                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │   AST Builder   │  │  Pattern Match  │  │  Call Graph   │ │
│  │                 │  │                 │  │               │ │
│  │ Tree-sitter     │  │ Wildcards       │  │ find_callers  │ │
│  │ -> AST Nodes    │  │ Regex Support   │  │ find_callees  │ │
│  │                 │  │ Exact Match     │  │ call_chains   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
├─────────────────────────────────────────────────────────────┤
│                    Foundation Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │ Source Manager  │  │   AST Nodes     │  │ Serialization │ │
│  │                 │  │                 │  │               │ │
│  │ File Loading    │  │ ContractDecl    │  │ JSON Export   │ │
│  │ Path Resolution │  │ FunctionDecl    │  │ LLM Ready     │ │
│  │ Caching         │  │ VariableDecl    │  │               │ │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
└─────────────────────────────────────────────────────────────┘
              │                  │                  │
         ┌────────────┐    ┌─────────────┐    ┌─────────────┐
         │ tree-sitter│    │   Pydantic  │    │    Python   │
         │  Solidity  │    │   Models    │    │   Standard  │
         └────────────┘    └─────────────┘    └─────────────┘
```

## Core Components

### 1. Foundation Layer

#### Source Manager (`sol_query.core.source_manager`)
- **File Discovery**: Recursively finds Solidity files in directories
- **Path Resolution**: Handles relative and absolute paths
- **Caching**: Optimizes repeated access to source files
- **Error Handling**: Graceful handling of malformed files

#### AST Nodes (`sol_query.core.ast_nodes`)
- **Pydantic Models**: Type-safe AST node representations
- **Source Location**: Precise mapping to source code positions
- **Node Hierarchy**: Structured representation of Solidity constructs
- **Serialization**: JSON export for LLM integration

#### Parser (`sol_query.core.parser`)
- **Tree-sitter Integration**: Leverages tree-sitter-solidity for parsing
- **Error Recovery**: Handles partial/malformed Solidity code
- **Performance**: Efficient parsing of large codebases

### 2. Core Engine

#### AST Builder (`sol_query.core.ast_builder`)
- **Tree-sitter → AST**: Converts tree-sitter nodes to structured AST
- **Type Resolution**: Extracts type information from Solidity syntax
- **Modifier Processing**: Handles visibility, state mutability, custom modifiers
- **Parameter Extraction**: Parses function/event parameters with types

#### Pattern Matching (`sol_query.utils.pattern_matching`)
- **Wildcard Support**: `*` and `?` patterns for flexible matching
- **Regex Integration**: Full regex support for complex patterns
- **Exact Matching**: Optimized exact string matching
- **Multi-pattern**: Support for lists of patterns

#### Query Engine (`sol_query.query.engine`)
- **Unified Interface**: Single engine supporting multiple query paradigms
- **Traditional Finders**: Direct query methods for all AST elements
- **Advanced Analysis**: Call graph, reference tracking, pattern matching
- **Performance Optimization**: Efficient filtering and caching

### 3. Query Collections

#### Collection Architecture
All collections inherit from `BaseCollection` providing:
- **Lazy Evaluation**: Operations are chained, executed on demand
- **Immutable Operations**: Each operation returns a new collection
- **JSON Serialization**: Built-in support for LLM integration
- **Python Integration**: Standard Python container protocols

#### Specialized Collections
- **ContractCollection**: Contract-specific filters and navigation
- **FunctionCollection**: Function visibility, modifiers, signature matching
- **VariableCollection**: Type patterns, visibility, state variable filters
- **ModifierCollection**: Modifier-specific operations
- **EventCollection**: Event parameter and naming filters

### 4. API Layers

#### Traditional API
Direct method calls for immediate results:
```python
functions = engine.find_functions(visibility="external", modifiers="onlyOwner")
```

#### Fluent API
Chainable operations for complex queries:
```python
functions = engine.functions.external().with_modifiers("onlyOwner").view()
```

## Design Principles

### 1. **Separation of Concerns**
- **Parsing**: Isolated in core.parser with tree-sitter integration
- **AST Building**: Clean conversion from tree-sitter to structured nodes
- **Querying**: Separated traditional and fluent interfaces
- **Serialization**: Dedicated utilities for JSON export

### 2. **Performance**
- **Lazy Evaluation**: Collections don't execute until needed
- **Caching**: Parsed ASTs are cached to avoid re-parsing
- **Efficient Filtering**: O(1) lookups where possible
- **Memory Management**: Streaming processing for large codebases

### 3. **Extensibility**
- **Plugin Architecture**: Easy to add new query methods
- **Custom Predicates**: Support for arbitrary filtering logic
- **AST Node Extension**: New node types can be added
- **Collection Extension**: New collection types can be created

### 4. **Type Safety**
- **Pydantic Models**: Runtime type validation
- **TypeScript-style**: Optional static typing with mypy
- **Enum Safety**: Structured enums for visibility, mutability, etc.
- **Generic Collections**: Type-safe collection operations

### 5. **LLM Integration**
- **JSON Serialization**: Complete AST serialization
- **Structured Output**: Consistent, predictable format
- **Source Mapping**: Precise location information
- **Error Handling**: Graceful degradation for LLM contexts

## Data Flow

### 1. Loading Phase
```
Source Files → SourceManager → SolidityParser → Tree-sitter AST
```

### 2. Building Phase
```
Tree-sitter AST → ASTBuilder → Structured AST Nodes → QueryEngine
```

### 3. Query Phase
```
Query Request → Pattern Matching → AST Traversal → Collection → Results
```

### 4. Output Phase
```
Results → Serialization → JSON → LLM Integration
```

## Extension Points

### 1. **Custom AST Nodes**
Add new node types by:
- Extending `ASTNode` base class
- Adding to `ast_builder.py` parsing logic
- Updating serialization in `utils/serialization.py`

### 2. **Custom Query Methods**
Add new query capabilities by:
- Adding methods to `SolidityQueryEngine`
- Creating specialized collection filters
- Implementing custom predicates

### 3. **Custom Collections**
Create domain-specific collections by:
- Extending `BaseCollection`
- Implementing specialized filtering logic
- Adding navigation methods

### 4. **Analysis Modules**
Add advanced analysis by:
- Creating modules in `sol_query/analysis/`
- Integrating with query engine
- Providing domain-specific APIs

## Error Handling Strategy

### 1. **Graceful Degradation**
- Continue parsing when encountering malformed code
- Return partial results instead of failing completely
- Log warnings for issues that don't prevent analysis

### 2. **Structured Errors**
- Custom exception types for different error categories
- Detailed error messages with source locations
- Recovery suggestions where possible

### 3. **Validation**
- Pydantic model validation for type safety
- Pattern validation for query parameters
- File system validation for source paths

## Performance Characteristics

### 1. **Time Complexity**
- **Parsing**: O(n) where n is source code size
- **Query Execution**: O(m) where m is result set size
- **Pattern Matching**: O(1) for exact, O(n) for wildcards
- **Collection Operations**: O(k) where k is collection size

### 2. **Memory Usage**
- **AST Storage**: ~10-20MB per 1000 contracts
- **Query Results**: Minimal overhead due to lazy evaluation
- **Caching**: Configurable memory limits for large codebases

### 3. **Scalability**
- **Horizontal**: Can process multiple files in parallel
- **Vertical**: Handles codebases up to 10,000+ contracts
- **Streaming**: Supports processing larger-than-memory codebases

This architecture provides a solid foundation for comprehensive Solidity code analysis while maintaining performance, extensibility, and ease of use.
