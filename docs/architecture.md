# Sol-Query Architecture

Comprehensive Solidity code analysis engine built on tree-sitter with modular, extensible architecture.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Sol-Query Engine                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────┐ │
│  │ Traditional API│  │   Fluent API   │  │   Analysis Suite    │ │
│  │                │  │                │  │                     │ │
│  │ find_contracts │  │ .contracts     │  │ • Call Graph        │ │
│  │ find_functions │  │ .functions     │  │ • Data Flow         │ │
│  │ find_variables │  │ .variables     │  │ • Import Analysis   │ │
│  │ find_calls     │  │ .expressions   │  │ • Pattern Matching  │ │
│  │      ...       │  │      ...       │  │ • Serialization     │ │
│  └────────────────┘  └────────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Collection Framework                         │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────┐ │
│  │ ContractColln  │  │ FunctionColln  │  │   StatementColln    │ │
│  │                │  │                │  │                     │ │
│  │ • with_name()  │  │ • external()   │  │ • loops()           │ │
│  │ • interfaces() │  │ • view()       │  │ • conditionals()    │ │
│  │ • inheriting() │  │ • payable()    │  │ • assignments()     │ │
│  │ • get_funcs()  │  │ • with_calls() │  │ • data_flow()       │ │
│  └────────────────┘  └────────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                     Analysis Engine                             │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────┐ │
│  │ Call Analyzer  │  │  Data Flow     │  │  Import Analyzer    │ │
│  │                │  │                │  │                     │ │
│  │ • External     │  │ • Variable     │  │ • Dependencies      │ │
│  │ • Internal     │  │   Tracking     │  │ • Usage Analysis    │ │
│  │ • Low-level    │  │ • Flow Paths   │  │ • Symbol Resolution │ │
│  │ • Asset Xfers  │  │ • Influences   │  │ • Graph Building    │ │
│  └────────────────┘  └────────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      Core Engine                               │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────┐ │
│  │  AST Builder   │  │ Pattern Match  │  │   Query Engine      │ │
│  │                │  │                │  │                     │ │
│  │ • Tree-sitter  │  │ • Wildcards    │  │ • Traditional API   │ │
│  │ • Node Creation│  │ • Regex        │  │ • Fluent API        │ │
│  │ • Type Safety  │  │ • Exact Match  │  │ • Collection Ops    │ │
│  │ • Validation   │  │ • Composition  │  │ • Set Operations    │ │
│  └────────────────┘  └────────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Foundation Layer                            │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────┐ │
│  │ Source Manager │  │   AST Nodes    │  │   Serialization     │ │
│  │                │  │                │  │                     │ │
│  │ • File Loading │  │ • Contract     │  │ • JSON Export       │ │
│  │ • Parsing      │  │ • Function     │  │ • LLM Ready         │ │
│  │ • Caching      │  │ • Variable     │  │ • Configurable      │ │
│  │ • Dependencies │  │ • Expression   │  │ • Type Safe         │ │
│  └────────────────┘  └────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
              │                    │                    │
         ┌──────────────┐    ┌─────────────┐    ┌─────────────────┐
         │ tree-sitter  │    │   Pydantic  │    │     Python      │
         │   Solidity   │    │   Models    │    │    Standard     │
         └──────────────┘    └─────────────┘    └─────────────────┘
```

## Core Components

### 1. Query Engine (SolidityQueryEngine)

The main interface providing both traditional functional and fluent object-oriented APIs.

**Key Features:**
- Dual API design (traditional + fluent)
- Source file management and parsing
- Comprehensive filtering and pattern matching
- Built-in analysis capabilities

**Design Patterns:**
- Factory pattern for collection creation
- Strategy pattern for different query styles
- Observer pattern for parse event handling

### 2. Collection Framework

Type-safe, chainable collections for different AST element types.

**Collection Types:**
- `ContractCollection` - Contract declarations
- `FunctionCollection` - Function declarations  
- `VariableCollection` - Variable declarations
- `ModifierCollection` - Modifier declarations
- `EventCollection` - Event declarations
- `StatementCollection` - Statement nodes
- `ExpressionCollection` - Expression nodes

**Collection Operations:**
- **Filtering**: `with_name()`, `external()`, `view()`, etc.
- **Set Operations**: `union()`, `intersect()`, `subtract()`
- **Navigation**: `get_functions()`, `get_variables()`, etc.
- **Composition**: Method chaining and boolean logic

### 3. AST Node Hierarchy

Pydantic-based type-safe AST representation with rich metadata.

```
ASTNode (BaseModel, ABC)
├── ContractDeclaration
├── FunctionDeclaration
├── VariableDeclaration
├── ModifierDeclaration
├── EventDeclaration
├── ErrorDeclaration
├── StructDeclaration
├── EnumDeclaration
├── Statement (ABC)
│   ├── Block
│   ├── ReturnStatement
│   ├── ExpressionStatement
│   └── GenericStatement
├── Expression (ABC)
│   ├── Identifier
│   ├── Literal
│   ├── CallExpression
│   ├── BinaryExpression
│   ├── ArrayAccess
│   └── ...
└── ImportStatement
```

**Key Properties:**
- `node_type`: NodeType enum for type identification
- `source_location`: Precise source position tracking
- `get_source_code()`: Access to original source text
- `get_children()`: AST traversal support

### 4. Analysis Modules

#### Call Analyzer
Sophisticated call detection and classification system.

**Capabilities:**
- External vs internal call detection
- Low-level call identification (`.call`, `.delegatecall`)
- Asset transfer detection (ETH, tokens, NFTs)
- Library and interface call recognition
- Contextual analysis for accuracy

**Call Types:**
- `EXTERNAL` - Cross-contract calls
- `INTERNAL` - Same-contract calls
- `LIBRARY` - Library function calls
- `LOW_LEVEL` - Raw `.call()` operations
- `DELEGATE` - Delegate calls
- `STATIC` - Static calls
- `SOLIDITY` - Built-in functions

#### Data Flow Analyzer
Variable dependency and flow tracking.

**Features:**
- Variable reference tracking (reads/writes)
- Data flow path discovery
- Influence analysis (what affects what)
- Cross-function flow analysis
- Flow graph construction

**API:**
- `trace_variable_flow()` - Find flow paths
- `find_variable_influences()` - What influences a variable  
- `find_variable_effects()` - What a variable affects
- `get_data_flow_backward/forward()` - Directional analysis

#### Import Analyzer
Import dependency analysis and symbol tracking.

**Capabilities:**
- Import pattern matching
- Dependency graph construction
- Symbol usage tracking
- External library detection
- Import statistics

### 5. Source Management

Robust file handling with caching and incremental parsing.

**Features:**
- Multiple source format support (files, directories, patterns)
- Intelligent caching with modification time checking
- Dependency resolution for imports
- Error handling and recovery
- Statistics and metadata tracking

**Components:**
- `SourceManager` - Main file management
- `SourceFile` - Individual file representation
- `SolidityParser` - Tree-sitter integration
- Dependency graph tracking

### 6. Pattern Matching

Flexible pattern matching with multiple strategies.

**Supported Patterns:**
- **Wildcards**: `*` (any chars), `?` (single char), `[abc]` (character sets)
- **Regex**: Full regular expression support
- **Exact**: String equality matching
- **List**: Multiple pattern combinations

**Use Cases:**
- Name filtering (`*Token*`, `get*`)
- Type matching (`uint*`, `mapping*`)
- Source code pattern matching
- Import path filtering

## Data Flow

### 1. Source Loading
```
Files → SourceManager → SolidityParser → tree-sitter → Parse Tree
```

### 2. AST Construction
```
Parse Tree → ASTBuilder → AST Nodes → Validation → Metadata Enrichment
```

### 3. Analysis Pipeline
```
AST Nodes → CallAnalyzer → DataFlowAnalyzer → ImportAnalyzer → Enhanced AST
```

### 4. Query Processing
```
Query → PatternMatcher → Collection Filter → Result Set → Serialization
```

## Design Principles

### 1. Type Safety
- Pydantic models for all data structures
- Enum-based type constants
- Generic type annotations throughout
- Runtime type validation

### 2. Performance
- Lazy evaluation for expensive operations
- Efficient caching strategies
- Incremental parsing support
- Optimized collection operations

### 3. Extensibility
- Plugin architecture for analyzers
- Abstract base classes for extensibility
- Configuration-driven behavior
- Modular component design

### 4. Usability
- Dual API design (functional + fluent)
- Comprehensive documentation
- Rich error messages
- Interactive development support

## Error Handling

### Parse Errors
- Graceful handling of syntax errors
- Partial parsing recovery
- Detailed error reporting with location info
- Batch processing error accumulation

### Query Errors
- Invalid pattern detection
- Type mismatch handling
- Empty result set management
- Timeout protection for complex queries

### File System Errors
- Missing file recovery
- Permission error handling
- Path resolution failures
- Encoding issue management

## Memory Management

### Caching Strategy
- LRU cache for parsed files
- Configurable cache size limits
- Memory pressure detection
- Explicit cache clearing APIs

### Resource Cleanup
- Automatic resource disposal
- Context manager support
- Lazy loading of heavy objects
- Efficient collection iterations

## Threading and Concurrency

### Thread Safety
- Immutable AST node design
- Thread-safe collection operations
- Concurrent parsing support
- Lock-free read operations

### Performance Optimization
- Parallel file parsing
- Concurrent analysis pipeline
- Asynchronous I/O support
- Background cache warming

## Future Extensibility

### Plugin Architecture
- Custom analyzer registration
- Extended node type support
- Additional language support
- Custom serialization formats

### Analysis Extensions
- Control flow analysis
- Security vulnerability detection
- Gas optimization analysis
- Code quality metrics

### Integration Points
- IDE plugin support
- CI/CD pipeline integration
- Custom tool development
- Research platform support

## Dependencies

### Core Dependencies
- `tree-sitter` - Parsing engine
- `tree-sitter-solidity` - Solidity grammar
- `pydantic` - Data validation and serialization
- `pathlib` - Path handling

### Optional Dependencies
- Analysis libraries for extended features
- Visualization tools for graph rendering
- Export formats for different integrations

This architecture provides a solid foundation for comprehensive Solidity code analysis while maintaining flexibility for future enhancements and integrations.