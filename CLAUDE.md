# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sol-Query is a comprehensive Python-based query engine for Solidity smart contracts. It provides both traditional and fluent query interfaces for security analysis, code migration, and research with advanced call graph and data flow analysis.

**Key Technologies:**
- Tree-sitter for robust Solidity parsing
- Pydantic for type-safe AST models
- Python 3.10+

## Development Commands

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_engine_v2_api.py

# Run tests with verbose output
pytest -v

# Run specific test by name
pytest tests/test_engine_v2_api.py::test_specific_function -v
```

### Code Quality
```bash
# Format code with Black
black sol_query/ tests/

# Type checking with mypy
mypy sol_query/

# Lint with ruff
ruff check sol_query/ tests/
```

### Installation
```bash
# Development installation (editable mode)
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

## Architecture

### Dual Engine Design

The codebase implements **two distinct query engines**:

1. **V1 Engine** (`sol_query/query/engine.py` - `SolidityQueryEngine`)
   - Traditional API: `engine.find_functions(visibility="external")`
   - Fluent API: `engine.functions.external().with_name("transfer*")`
   - Collection framework with chainable operations

2. **V2 Engine** (`sol_query/query/engine_v2.py` - `SolidityQueryEngineV2`)
   - Optimized 3-method interface: `query_code()`, `get_details()`, `find_references()`
   - LLM-friendly with standardized JSON responses
   - Performance-optimized with caching

**Important:** These are independent implementations, not versions of the same engine. Changes to V1 do not affect V2 and vice versa.

### Core Components

**Parsing & AST Building:**
- `sol_query/core/parser.py` - Tree-sitter wrapper for Solidity parsing
- `sol_query/core/ast_builder.py` - Converts tree-sitter nodes to Pydantic AST models (66KB file, most complex)
- `sol_query/core/ast_nodes.py` - Type-safe AST node definitions with Pydantic validation
- `sol_query/core/source_manager.py` - File loading, parsing coordination, caching

**Analysis Suite:**
- `sol_query/analysis/call_analyzer.py` - Detects external calls, asset transfers, call types (33KB file)
- `sol_query/analysis/variable_tracker.py` - Variable read/write tracking across scopes
- `sol_query/analysis/data_flow.py` - Data flow and variable influence analysis
- `sol_query/analysis/import_analyzer.py` - Import dependency tracking and symbol resolution
- `sol_query/analysis/call_types.py` - Call type classification (external, internal, library, low-level)

**Query Infrastructure:**
- `sol_query/query/collections.py` - Chainable type-safe collections for fluent API (V1 only)
- `sol_query/utils/pattern_matching.py` - Wildcard, regex, and exact pattern matching
- `sol_query/utils/serialization.py` - JSON serialization for LLM consumption

### Important Design Patterns

**AST Builder Node Mapping:**
The `ASTBuilder` class uses a dictionary-based dispatch pattern (`node_type_mapping`) to map tree-sitter node types to builder methods. When adding support for new Solidity constructs, add entries to this mapping in `ast_builder.py`.

**Context-Aware Analysis:**
`CallAnalyzer.analyze_function()` requires contract context to distinguish internal vs external calls. The analyzer builds this context from the parent contract's function and modifier declarations.

**Collection Framework (V1 only):**
Collections provide chainable filtering with set operations (union, intersect, subtract). Each filter returns a new collection, enabling method chaining.

**Caching Strategy:**
Both engines cache parsed AST nodes. V2 additionally caches `_all_nodes_cache` and `_nodes_by_type_cache`. Invalidate caches when loading new sources.

## Test Organization

```
tests/
├── test_*.py              # V1 API tests (traditional/fluent)
├── test_engine_v2_*.py    # V2 API tests
├── 100/                   # Comprehensive V2 test suite split into parts
│   ├── basic/             # Basic V2 functionality tests
│   └── test_plan_part*.py # Systematic V2 feature tests
├── compound/              # Real-world Compound Protocol tests
└── fixtures/              # Test fixtures including sol-bug-bench
```

**Test Fixtures:**
- `tests/fixtures/` contains real Solidity code for testing
- Compound Protocol is included as a Git submodule for comprehensive testing
- Sol-bug-bench provides vulnerable contract examples

## Key Implementation Notes

### Adding New AST Node Support

1. Define node model in `core/ast_nodes.py` with Pydantic validation
2. Add tree-sitter node type mapping in `ast_builder.py` `node_type_mapping` dictionary
3. Implement builder method in `ASTBuilder` class (e.g., `_build_new_node_type`)
4. Update `NodeType` enum if introducing new node category
5. Add tests in appropriate test file

### Extending Analysis Capabilities

**For Call Analysis:**
- Add patterns to `CallAnalyzer.external_call_patterns` or `asset_transfer_patterns`
- Update `CallTypeDetector` in `analysis/call_types.py` for new call classifications

**For Data Flow:**
- Extend `VariableTracker` for new tracking requirements
- Modify `DataFlowAnalyzer` for new flow analysis patterns

### V2 Engine Filters

V2's `query_code()` supports 13+ filter types including:
- `visibility`, `state_mutability`, `modifiers`
- `has_external_calls`, `has_asset_transfers`
- `names` (with wildcard/regex support)
- `types`, `is_constant`, `is_immutable`
- `reference_type`, `direction` (for `find_references`)

See `docs/api-reference-v2.md` for complete filter documentation.

## Common Gotchas

- **Import both engines explicitly:** V1 is in `__init__.py`, V2 must be imported directly from `query.engine_v2`
- **Tree-sitter node types vary:** Some constructs have multiple tree-sitter names (e.g., `struct_definition` vs `struct_declaration`)
- **Context matters for call analysis:** Always provide contract context to `CallAnalyzer` for accurate internal/external call distinction
- **Line numbers in source locations:** Source locations use 0-based indexing internally but may be presented as 1-based in output
- **Pattern matching is case-sensitive:** Use `-i` regex flag or lowercase comparisons for case-insensitive matching

After finishing, run: afplay /System/Library/Sounds/Funk.aiff