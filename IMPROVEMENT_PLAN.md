# Sol-Query Comprehensive Improvement Plan

**Goal**: Ensure sol-query engine correctness through systematic test validation, core architecture review, and engine verification.

**Approach**: Test-driven improvements with focus on tree-sitter analysis over text patterns, no backward compatibility concerns.

---

## Phase 1: Test Suite Validation & Correction (Priority: CRITICAL)

### Objective
Validate ALL test assertions against actual Solidity source code. Tests are the source of truth - they must be 100% accurate.

### 1.1 Basic V2 Tests (`tests/100/basic/`)

**Files**: `test_v2_basic_part1.py` through `test_v2_basic_part5.py`

**Process**:
1. Read each test case function
2. Identify the target Solidity file(s) referenced
3. **Manually analyze the Solidity source** to determine expected results
4. Verify assertion accuracy:
   - Line numbers (critical - must match exactly)
   - Column numbers (if asserted)
   - Names, signatures, types
   - Visibility, state mutability
   - Return types, parameters
   - Inheritance relationships
5. Correct any inaccurate assertions
6. Add missing assertions for completeness (e.g., actual parameter names, not just counts)

**Key Files to Validate**:
- `tests/fixtures/composition_and_imports/SimpleContract.sol`
- `tests/fixtures/composition_and_imports/ERC721WithImports.sol`
- `tests/fixtures/composition_and_imports/MultipleInheritance.sol`
- `tests/fixtures/detailed_scenarios/*.sol`
- `tests/fixtures/sample_contract.sol`

**Critical Checks**:
- Constructor declarations (line numbers, parameters)
- Function visibility defaults (external vs public in interfaces)
- Modifier applications
- Event parameters with `indexed` keyword
- Error declarations with parameters
- Struct member ordering
- Inheritance chain accuracy

### 1.2 Advanced Test Plans (`tests/100/test_plan_part*.py`)

**Files**: `test_plan_part1.py` through `test_plan_part10.py`

**Process**:
1. Same validation process as 1.1
2. Focus on complex scenarios:
   - Filter combinations
   - Scope restrictions
   - Reference tracking
   - Cross-contract analysis
3. Verify `get_details()` returns complete, accurate information
4. Verify `find_references()` captures all actual references

**Special Attention**:
- Wildcard pattern matching expectations
- Regular expression filter results
- Modifier filter accuracy (functions with specific modifiers)
- Call detection (external vs internal - context-dependent)

### 1.3 Compound Protocol Tests (`tests/compound/`)

**Files**: `test_compound_comprehensive.py`, `test_next_batch_issues.py`

**Process**:
1. Read actual Compound contracts from `tests/fixtures/compound-protocol/contracts/`
2. Validate ALL hardcoded expectations:
   - Contract names list (complete and accurate)
   - Function line numbers (verify against actual source)
   - Variable locations
   - Inheritance relationships
3. **THIS IS THE MOST IMPORTANT VALIDATION** - Real-world complex codebase
4. Document any Compound-specific patterns that break the engine

**Critical Files**:
- `Comptroller.sol` - Complex state machine
- `CToken.sol` - Abstract base with inheritance
- `CErc20.sol` - Concrete implementation
- `CTokenInterfaces.sol` - Interface definitions

### 1.4 Other Test Suites

**Files**: All other `test_*.py` in `tests/`

**Process**:
1. Review each test file
2. Validate assertions against fixtures
3. Ensure tests actually test what they claim to test
4. Remove superficial assertions (e.g., `assert type == "function"` without verifying which function)
5. Add deep assertions (actual values, not just presence)

---

## Phase 2: Core Architecture Review & Optimization

### Objective
Fix fundamental building blocks to ensure accurate tree-sitter analysis.

### 2.1 Parser Layer (`sol_query/core/parser.py`)

**Current Issues**:
- Line/column calculation in `_get_node_position()` uses manual string splitting
- May have off-by-one errors
- Deprecation warning with tree-sitter API

**Improvements**:
1. **Fix tree-sitter API deprecation**
   - Update to modern tree-sitter Language initialization
   - Test: Ensure warning disappears

2. **Verify position calculation accuracy**
   - Tree-sitter provides `start_point` and `end_point` attributes directly
   - Use `node.start_point.row` and `node.start_point.column` instead of manual calculation
   - Verify 0-based vs 1-based indexing consistency
   - Test: Create fixture with known line/column positions, verify accuracy

3. **Improve error handling**
   - Better error messages for malformed Solidity
   - Partial parsing support (don't fail entire file for one error)

**Implementation**:
```python
def _get_node_position(self, node: tree_sitter.Node, source_code: str) -> Tuple[int, int]:
    """Get line and column position of node start (1-indexed)."""
    # Use tree-sitter's built-in position tracking
    return node.start_point.row + 1, node.start_point.column + 1
```

### 2.2 AST Builder (`sol_query/core/ast_builder.py`)

**Current Issues**:
- 66KB file, very complex
- Many inline imports (violates requirements)
- Potential inaccuracies in node type detection
- May miss edge cases in Solidity grammar

**Improvements**:

1. **Remove inline imports**
   - Move all imports to top of file
   - Check for circular dependency issues and resolve architecturally

2. **Verify node type mapping completeness**
   - Review tree-sitter-solidity grammar
   - Ensure all node types are mapped
   - Test: Parse diverse Solidity files, check for unmapped nodes

3. **Fix visibility/mutability defaults**
   - Functions default to `public` in contracts, not interfaces
   - Functions in interfaces default to `external`
   - State variables default to `internal`
   - Verify defaults are context-aware
   - Test: Parse interface vs contract, verify defaults

4. **Improve parameter extraction**
   - Ensure parameter names are captured, not just types
   - Handle complex parameter types (nested structs, arrays)
   - Test: Functions with complex parameters

5. **Fix inheritance parsing**
   - Capture inheritance arguments (constructor parameters)
   - Maintain order of inheritance
   - Test: Multiple inheritance with constructor args

6. **Validate statement/expression building**
   - Ensure all statement types are properly categorized
   - Nested expressions must preserve structure
   - Test: Complex expressions with nested calls

**Specific Fixes**:
- `_build_contract()`: Verify interface detection logic uses tree-sitter node type, not name pattern
- `_build_function()`: Context-aware visibility defaults
- `_build_variable()`: Accurate state variable detection
- `_build_parameter()`: Capture full parameter information including `indexed` for events

### 2.3 AST Nodes (`sol_query/core/ast_nodes.py`)

**Current Issues**:
- Many data flow methods that import analyzers (circular dependency risk)
- Some fields may not match actual Solidity semantics

**Improvements**:

1. **Review all Pydantic models**
   - Ensure fields match Solidity specification
   - Add validation where appropriate
   - Test: Create nodes with invalid data, ensure validation catches it

2. **Fix parent relationship tracking**
   - `_find_containing_function()` returns None (incomplete implementation)
   - Need proper parent references for context-aware analysis
   - Implementation: Add `parent` field to ASTNode, populate during building

3. **Optimize data flow methods**
   - Lazy loading of analyzers
   - Cache results
   - Test: Performance on large contracts

### 2.4 Source Manager (`sol_query/core/source_manager.py`)

**Current Issues**:
- Cache invalidation may be incomplete
- File dependency tracking might miss imports

**Improvements**:

1. **Verify cache invalidation**
   - When reloading files, ensure all caches are cleared
   - Test: Load file, query, reload file, query again - results should update

2. **Improve import resolution**
   - Handle relative imports correctly
   - Handle node_modules style imports
   - Test: Files with complex import paths

---

## Phase 3: Analysis Layer Improvements

### 3.1 Call Analyzer (`sol_query/analysis/call_analyzer.py`)

**Current Issues**:
- Uses regex patterns for call detection (violates requirement)
- May miss calls or misclassify them
- Context awareness incomplete

**Improvements**:

1. **Replace regex-based detection with tree-sitter analysis**
   - Traverse call expressions in AST
   - Classify calls based on tree structure, not text patterns
   - Implementation:
     ```python
     def _is_external_call(self, call_expr: CallExpression, context: Dict) -> bool:
         # Check if callee is member access (e.g., contract.function())
         # Check if contract is in context or external
         # Use tree-sitter node types, not regex
     ```

2. **Improve context building**
   - `_build_contract_context()` must include all functions/modifiers from inheritance chain
   - Handle interface implementations
   - Test: Call in inherited function should know about base contract

3. **Fix call type classification**
   - Use tree-sitter node structure to identify:
     - `.call()`, `.delegatecall()`, `.staticcall()` - check node.children for these identifiers
     - External contract calls - check if callee is not in current contract
     - Internal calls - check if callee is in current contract context
   - Test: Various call types in same function

4. **Remove pattern matching fallbacks**
   - All detection should be AST-based
   - Remove `external_call_patterns`, `asset_transfer_patterns` dictionaries
   - Rely on actual tree structure

### 3.2 Variable Tracker (`sol_query/analysis/variable_tracker.py`)

**Current Coverage**: Only 16%

**Improvements**:

1. **Complete implementation**
   - Review all TODO/FIXME comments
   - Implement missing methods
   - Test: Variable tracking in complex functions

2. **Improve scope tracking**
   - Handle function parameters vs local variables vs state variables
   - Track variable shadowing correctly
   - Test: Same variable name in different scopes

### 3.3 Data Flow Analyzer (`sol_query/analysis/data_flow.py`)

**Current Coverage**: 0%

**Improvements**:

1. **Complete implementation or remove**
   - If not critical for V2 API, consider removing
   - If critical, implement fully with tests
   - Test: Data flow through complex logic

### 3.4 Call Types (`sol_query/analysis/call_types.py`)

**Current Coverage**: 44%

**Improvements**:

1. **Review detection logic**
   - Ensure all call types properly detected from tree structure
   - Test: Each call type with examples

---

## Phase 4: Query Engine Verification

### 4.1 Engine V2 (`sol_query/query/engine_v2.py`)

**Current Coverage**: 14% (4692 lines, only 2481 covered)

**This is the main engine - needs major attention**

**Improvements**:

1. **Fix `query_code()` filter application**
   - Verify each filter type works correctly:
     - `visibility` - check against AST node visibility
     - `state_mutability` - check against AST node state_mutability
     - `names` - pattern matching must be accurate
     - `has_external_calls` - must use CallAnalyzer correctly
     - `has_asset_transfers` - must use CallAnalyzer correctly
     - `modifiers` - check applied modifiers, not modifier definitions
   - Test: Each filter individually and in combination

2. **Fix `get_details()` completeness**
   - Return ALL relevant information for element type
   - Functions: params with names+types, return type, modifiers, body location
   - Variables: full type info, initialization value
   - Contracts: complete inheritance chain, all members
   - Test: Compare output to manual code analysis

3. **Fix `find_references()` accuracy**
   - Must find ALL references, not miss any
   - Must not return false positives
   - Direction filter (`both`, `upstream`, `downstream`) must work correctly
   - Test: Known reference patterns in fixtures

4. **Improve scope filtering**
   - `files` scope - regex patterns must work
   - `contracts` scope - must find in specified contracts only
   - `functions` scope - must find in specified functions only
   - Test: Scoped queries return correct subset

5. **Fix caching issues**
   - `_invalidate_caches()` must be called appropriately
   - Cache hits must return correct data
   - Test: Query, modify, query - results should update

### 4.2 Pattern Matching (`sol_query/utils/pattern_matching.py`)

**Current Coverage**: 17%

**Improvements**:

1. **Test all pattern types**
   - Exact match
   - Wildcard (`*`, `?`)
   - Regex
   - Case sensitivity
   - Test: Each pattern type with edge cases

2. **Fix match accuracy**
   - Ensure wildcards work like standard glob patterns
   - Regex should support full Python regex syntax
   - Test: Complex patterns from real queries

---

## Phase 5: Integration & Verification

### 5.1 Run Full Test Suite

**Process**:
1. Run: `pytest tests/ -v --tb=short`
2. For each failure:
   - Read the test
   - **First**, verify the test assertion is correct by reading Solidity source
   - **Second**, if test is correct, debug why engine gives wrong result
   - Fix engine, not test (unless test is genuinely wrong)
3. Goal: 100% test pass rate with meaningful assertions

### 5.2 Add Missing Test Coverage

**Areas with low coverage need tests**:
- Data flow analysis (0%)
- Import analysis (0%)
- Collection framework (23%)
- V1 Engine (14%)
- Variable tracker (16%)
- Pattern matching (17%)

**Process**:
1. Write tests for uncovered code paths
2. Ensure tests are meaningful (test behavior, not implementation)
3. Fix bugs discovered by new tests

### 5.3 Performance Testing

**Process**:
1. Profile engine on large codebases (Compound)
2. Identify bottlenecks
3. Optimize without sacrificing correctness
4. Test: Query performance benchmarks

---

## Implementation Order

### Week 1: Test Validation Foundation
1. **Day 1-2**: Validate `tests/100/basic/` tests against Solidity fixtures
2. **Day 3-4**: Validate `tests/100/test_plan_*` tests against Solidity fixtures
3. **Day 5**: Validate other test suites

### Week 2: Core Architecture Fixes
1. **Day 1**: Fix Parser (position calculation, API deprecation)
2. **Day 2-3**: Fix AST Builder (visibility defaults, node mapping)
3. **Day 4**: Fix AST Nodes (parent tracking, validation)
4. **Day 5**: Fix Source Manager (caching, imports)

### Week 3: Analysis Layer Overhaul
1. **Day 1-2**: Rewrite Call Analyzer (tree-sitter based, remove regex)
2. **Day 3**: Fix Variable Tracker
3. **Day 4**: Fix Call Types
4. **Day 5**: Review Data Flow (implement or remove)

### Week 4: Engine Verification
1. **Day 1-2**: Fix Engine V2 `query_code()` filters
2. **Day 3**: Fix Engine V2 `get_details()`
3. **Day 4**: Fix Engine V2 `find_references()`
4. **Day 5**: Fix Pattern Matching

### Week 5: Integration & Polish
1. **Day 1-2**: Run full test suite, fix failures
2. **Day 3**: Add missing test coverage
3. **Day 4**: Performance optimization
4. **Day 5**: Final verification, documentation updates

---

## Success Criteria

### Test Suite
- [ ] 100% of test assertions verified against Solidity source
- [ ] 100% test pass rate
- [ ] No superficial assertions (all assertions meaningful)
- [ ] Test coverage >80% overall
- [ ] Compound tests pass with accurate assertions

### Architecture
- [ ] No inline imports
- [ ] No regex-based Solidity code detection
- [ ] Tree-sitter used exclusively for parsing/analysis
- [ ] Parser uses native tree-sitter positions
- [ ] AST Builder handles all Solidity constructs
- [ ] Context-aware visibility/mutability defaults

### Engine Accuracy
- [ ] `query_code()` filters work individually and combined
- [ ] `get_details()` returns complete, accurate information
- [ ] `find_references()` finds all references, no false positives
- [ ] Scope filtering works correctly
- [ ] Line/column numbers accurate to source
- [ ] Call classification accurate (internal vs external)

### Code Quality
- [ ] No over-engineering
- [ ] Concise, readable code
- [ ] Proper error handling
- [ ] Comprehensive logging
- [ ] Performance acceptable on large codebases

---

## Critical Rules

1. **Test assertions are source of truth** - if test expects something, verify it's correct by reading Solidity first
2. **Tree-sitter only** - no regex for Solidity code analysis
3. **No backward compatibility** - break old code if needed for correctness
4. **No inline imports** - all imports at top
5. **Meaningful assertions** - test actual values, not just types
6. **Context awareness** - visibility/mutability defaults depend on context
7. **Complete information** - `get_details()` should return everything relevant
8. **Accuracy over features** - correct results more important than advanced features

---

## Notes

- The 27% overall coverage suggests large portions of code are untested or dead code
- Engine V2 (14% coverage, 4692 lines) is the highest priority for improvement
- Compound tests are most important - real-world validation
- Parser position calculation is critical - many tests depend on accurate line numbers
- Call Analyzer regex patterns must be replaced with tree-sitter traversal
- Many analysis modules have 0% coverage - either implement fully or remove

