# Sol-Query Improvement Plan - Executive Summary

## Overview

Comprehensive plan to improve sol-query engine correctness through systematic test validation, core architecture review, and engine verification.

## Three Key Documents

1. **IMPROVEMENT_PLAN.md** - High-level strategy and phases
2. **DETAILED_EXECUTION_CHECKLIST.md** - Granular daily tasks
3. **This summary** - Quick reference

## The Problem

- Engine works for simple queries but fails on advanced codebases (Compound Protocol)
- Test coverage: 27% overall, Engine V2: 14% (critical component)
- Many test assertions unvalidated against actual Solidity source
- Regex-based pattern matching instead of tree-sitter analysis
- Inline imports throughout codebase

## The Solution - Three Phases

### Phase 1: Test Validation (Days 1-5) - CRITICAL FOUNDATION

**Goal**: Ensure every test assertion is verified against actual Solidity source code.

**Process**:
1. Read test code
2. Open referenced Solidity file
3. **Manually verify** expected results match source
4. Update test assertions with accurate values
5. Focus on **deep assertions** (actual values, not just types)

**Files**: ~15 test files, ~200+ test functions

**Key Insight**: Tests are source of truth. If test expects something, Solidity code must match that expectation.

### Phase 2: Core Architecture (Days 6-10) - BUILD SOLID FOUNDATION

**Goal**: Fix fundamental building blocks to ensure accurate tree-sitter analysis.

**Key Fixes**:

1. **Parser** (`parser.py`):
   - Fix tree-sitter API deprecation warning
   - Use native tree-sitter positions instead of manual calculation
   - Accurate line/column numbers

2. **AST Builder** (`ast_builder.py`):
   - Remove ALL inline imports
   - Context-aware visibility defaults (interface functions default to `external`, not `public`)
   - Complete parameter extraction (names + types + `indexed` for events)
   - Accurate inheritance parsing (order + arguments)

3. **AST Nodes** (`ast_nodes.py`):
   - Add parent reference tracking
   - Fix `_find_containing_function()` implementation

### Phase 3: Analysis Layer (Days 11-15) - REPLACE REGEX WITH TREE-SITTER

**Goal**: Eliminate all regex-based Solidity code detection.

**Critical Change - Call Analyzer**:

**BEFORE** (wrong):
```python
# Uses regex patterns
if re.search(r'\.call\(', source_text):
    return CallType.LOW_LEVEL
```

**AFTER** (correct):
```python
# Uses tree-sitter AST analysis
if isinstance(callee, MemberAccess) and callee.property.name == 'call':
    return CallType.LOW_LEVEL
```

**Impact**: Accurate call classification (internal vs external vs low-level) based on actual code structure, not text patterns.

### Phase 4: Engine Verification (Days 16-20) - FIX THE HEART

**Goal**: Ensure Engine V2 query methods work correctly.

**Key Fixes**:

1. **`query_code()` filters**:
   - Each filter tested individually
   - Filter combinations tested
   - All filters use AST node properties, not text matching

2. **`get_details()` completeness**:
   - Return ALL relevant information
   - Function: params with names+types, return type, modifiers, body
   - Contract: complete inheritance chain, all members
   - Variable: full type info, visibility, flags

3. **`find_references()` accuracy**:
   - Find ALL references, no false positives
   - Direction filters work correctly
   - Reference types accurate

### Phase 5: Integration (Days 21-25) - VERIFY & POLISH

**Goal**: 100% test pass rate with >80% coverage.

**Process**:
1. Run full test suite
2. For EACH failure:
   - Verify test is correct (check Solidity source)
   - If test correct, debug engine
   - If test wrong, fix test
3. Add missing test coverage
4. Performance optimization
5. Final verification

## Critical Rules

1. ✅ **Test assertions are source of truth** - verify against Solidity first
2. ✅ **Tree-sitter only** - no regex for code analysis
3. ✅ **No backward compatibility** - break old code for correctness
4. ✅ **No inline imports** - all imports at top
5. ✅ **Meaningful assertions** - test actual values, not just types
6. ✅ **Context awareness** - defaults depend on context (interface vs contract)
7. ✅ **Complete information** - `get_details()` returns everything
8. ✅ **Accuracy over features** - correct results more important

## Success Metrics

- [ ] 100% of test assertions validated against Solidity source
- [ ] 100% test pass rate
- [ ] >80% test coverage overall
- [ ] No regex-based Solidity code detection
- [ ] No inline imports
- [ ] Tree-sitter positions used natively
- [ ] Context-aware visibility/mutability defaults
- [ ] Compound Protocol tests pass with accurate assertions
- [ ] Engine V2 coverage >70% (currently 14%)
- [ ] Query performance <5s for Compound Protocol

## Most Critical Tasks

### Top 3 Priorities

1. **Validate Compound tests** (`tests/compound/test_compound_comprehensive.py`)
   - These test real-world complex code
   - If these pass, engine is solid
   - Current assertions may be wrong - verify against source

2. **Fix Call Analyzer** (`sol_query/analysis/call_analyzer.py`)
   - Remove ALL regex patterns
   - Use tree-sitter AST exclusively
   - Context-aware classification

3. **Fix Parser positions** (`sol_query/core/parser.py`)
   - Many tests depend on accurate line numbers
   - Use native tree-sitter positions
   - Fix deprecation warning

## Quick Start

### Week 1: Validate Tests
```bash
# Start with basic tests
cd tests/100/basic/
# For each test file:
# 1. Read test
# 2. Open fixture Solidity file
# 3. Verify assertions match source
# 4. Update test

# Example:
# test_01_query_contracts_in_simplecontract expects:
# - Contract at line 7 ✓ (verify in SimpleContract.sol)
# - Name "SimpleContract" ✓
# - No inheritance ✓
```

### Week 2: Fix Core
```bash
# Fix parser positions
vim sol_query/core/parser.py
# Replace manual position calculation with:
# node.start_point.row + 1, node.start_point.column + 1

# Fix AST Builder defaults
vim sol_query/core/ast_builder.py
# Make visibility defaults context-aware
```

### Week 3: Rewrite Call Analyzer
```bash
# Remove regex, use tree-sitter
vim sol_query/analysis/call_analyzer.py
# Delete external_call_patterns, asset_transfer_patterns
# Implement _classify_call_from_ast() using AST structure
```

### Weeks 4-5: Verify & Polish
```bash
# Run full suite
pytest tests/ -v --cov=sol_query

# Fix failures one by one
# Add missing tests
# Optimize performance
```

## Expected Outcomes

### Before
- ❌ Tests pass but assertions may be inaccurate
- ❌ 27% overall coverage
- ❌ Engine V2: 14% coverage
- ❌ Regex-based detection
- ❌ Inline imports everywhere
- ❌ Compound tests may have wrong expectations
- ❌ Call classification unreliable

### After
- ✅ Tests pass with verified assertions
- ✅ >80% overall coverage
- ✅ Engine V2: >70% coverage
- ✅ Tree-sitter based detection exclusively
- ✅ Clean imports at top
- ✅ Compound tests accurate and passing
- ✅ Call classification accurate and context-aware
- ✅ Reliable engine for production use

## Time Estimate

- **Phase 1** (Test Validation): 5 days
- **Phase 2** (Core Architecture): 5 days
- **Phase 3** (Analysis Layer): 5 days
- **Phase 4** (Engine Verification): 5 days
- **Phase 5** (Integration): 5 days

**Total**: 25 days (~5 weeks)

## Next Steps

1. Read IMPROVEMENT_PLAN.md for detailed strategy
2. Read DETAILED_EXECUTION_CHECKLIST.md for daily tasks
3. Start with Day 1: Validate `tests/100/basic/test_v2_basic_part1.py`
4. Work systematically through checklist
5. Don't skip validation steps
6. Test frequently
7. Document decisions

## Questions to Ask During Implementation

1. **Test fails** - Is the test assertion correct? Check Solidity source first.
2. **Engine gives wrong result** - Is it using tree-sitter or regex? Should use tree-sitter.
3. **Visibility wrong** - Is default context-aware? Should be different for interface vs contract.
4. **Line number off** - Is parser using native positions? Should use `node.start_point`.
5. **Call misclassified** - Is CallAnalyzer using AST structure? Should not use regex.

## Files to Monitor

Most changes will be in:
- `sol_query/core/parser.py` - Position fixes
- `sol_query/core/ast_builder.py` - Context-aware building
- `sol_query/analysis/call_analyzer.py` - Tree-sitter based detection
- `sol_query/query/engine_v2.py` - Filter and detail fixes
- All test files - Assertion validation

## Final Note

**Accuracy is paramount**. This plan prioritizes correctness over speed. Each test assertion must be verified against actual Solidity source code. The engine must use tree-sitter analysis exclusively, no text patterns. The result will be a production-ready, reliable Solidity query engine.

Good luck! 🚀
