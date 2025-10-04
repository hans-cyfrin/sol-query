# 🎯 Sol-Query Improvement Initiative

## 📋 Plan Documents

Three comprehensive documents guide this improvement initiative:

1. **PLAN_SUMMARY.md** - Quick reference and overview (START HERE)
2. **IMPROVEMENT_PLAN.md** - Detailed strategy and phases
3. **DETAILED_EXECUTION_CHECKLIST.md** - Granular daily tasks

## 🎯 Mission

Transform sol-query from "works for simple queries" to "production-ready, accurate Solidity analysis engine."

## 📊 Current State

```
Test Coverage:      27% overall (target: >80%)
Engine V2 Coverage: 14% (target: >70%)
Test Assertions:    Unvalidated (target: 100% validated)
Detection Method:   Regex patterns (target: Tree-sitter AST)
Code Organization:  Inline imports (target: Clean top-level imports)
```

## 🚀 The Plan - 5 Phases in 25 Days

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: TEST VALIDATION (Days 1-5)                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✓ Validate EVERY test assertion against Solidity  │    │
│  │ ✓ Fix inaccurate expectations                     │    │
│  │ ✓ Add deep assertions (values, not just types)    │    │
│  │ ✓ Focus on Compound tests (real-world validation) │    │
│  └────────────────────────────────────────────────────┘    │
│  Output: Accurate test suite (source of truth)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: CORE ARCHITECTURE (Days 6-10)                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✓ Fix Parser: Native tree-sitter positions        │    │
│  │ ✓ Fix AST Builder: Context-aware defaults         │    │
│  │ ✓ Remove inline imports                           │    │
│  │ ✓ Add parent tracking                             │    │
│  └────────────────────────────────────────────────────┘    │
│  Output: Solid foundation for accurate analysis            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: ANALYSIS LAYER (Days 11-15)                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✓ Rewrite Call Analyzer: Tree-sitter, not regex   │    │
│  │ ✓ Context-aware call classification               │    │
│  │ ✓ Fix Variable Tracker                            │    │
│  │ ✓ Review all analyzers                            │    │
│  └────────────────────────────────────────────────────┘    │
│  Output: Accurate AST-based analysis, no text patterns     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: ENGINE VERIFICATION (Days 16-20)                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✓ Fix query_code() filters                        │    │
│  │ ✓ Fix get_details() completeness                  │    │
│  │ ✓ Fix find_references() accuracy                  │    │
│  │ ✓ Fix scope filtering                             │    │
│  └────────────────────────────────────────────────────┘    │
│  Output: Reliable V2 API with accurate results             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: INTEGRATION & POLISH (Days 21-25)                │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✓ Run full test suite                             │    │
│  │ ✓ Fix all failures                                │    │
│  │ ✓ Add missing test coverage                       │    │
│  │ ✓ Performance optimization                        │    │
│  │ ✓ Final verification                              │    │
│  └────────────────────────────────────────────────────┘    │
│  Output: Production-ready engine, >80% coverage            │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Key Technical Changes

### 1. Parser Position Calculation

**BEFORE**:
```python
# Manual string splitting (error-prone)
lines = source_code[:node.start_byte].split('\n')
line = len(lines)
column = len(lines[-1]) + 1
```

**AFTER**:
```python
# Native tree-sitter positions (accurate)
return node.start_point.row + 1, node.start_point.column + 1
```

### 2. Visibility Defaults

**BEFORE**:
```python
# Always defaults to public
visibility = extract_visibility(node) or Visibility.PUBLIC
```

**AFTER**:
```python
# Context-aware defaults
def get_default_visibility(node, parent_contract_type):
    if parent_contract_type == "interface":
        return Visibility.EXTERNAL  # Interface functions default to external
    else:
        return Visibility.PUBLIC    # Contract functions default to public
```

### 3. Call Detection

**BEFORE**:
```python
# Regex-based (unreliable)
if re.search(r'\.call\(', source_text):
    return CallType.LOW_LEVEL
```

**AFTER**:
```python
# AST-based (accurate)
if isinstance(callee, MemberAccess) and callee.property.name == 'call':
    return CallType.LOW_LEVEL
```

### 4. Test Assertions

**BEFORE**:
```python
# Superficial - just checks type
assert len(results) > 0
assert results[0]['type'] == 'function'
```

**AFTER**:
```python
# Deep - checks actual values verified against source
assert len(results) == 6  # Verified by counting in Solidity file
assert results[0]['name'] == 'pureFunction'  # Verified at line 22
assert results[0]['signature'] == 'pureFunction(uint256,uint256)'
assert results[0]['visibility'] == 'public'
assert results[0]['state_mutability'] == 'pure'
assert results[0]['location']['line'] == 22  # Verified in source
```

## 📏 Critical Rules

| # | Rule | Why |
|---|------|-----|
| 1 | **Test assertions verified against Solidity source** | Tests are source of truth - must be accurate |
| 2 | **Tree-sitter only, no regex** | AST analysis is reliable, text patterns are not |
| 3 | **No backward compatibility concerns** | Correctness > compatibility |
| 4 | **No inline imports** | Clean code organization |
| 5 | **Context-aware defaults** | Solidity semantics vary by context |
| 6 | **Deep assertions** | Test actual values, not just presence |
| 7 | **Complete information** | API should return everything relevant |
| 8 | **Accuracy over features** | Correct results more important than advanced features |

## 🎯 Success Criteria

### Tests
- [x] Create comprehensive plan
- [ ] 100% of assertions validated against Solidity source
- [ ] 100% test pass rate
- [ ] >80% overall coverage
- [ ] Compound Protocol tests passing with accurate assertions

### Architecture
- [ ] No inline imports
- [ ] No regex-based Solidity code detection
- [ ] Tree-sitter positions used natively
- [ ] Context-aware visibility/mutability defaults
- [ ] Parent tracking implemented

### Engine
- [ ] All `query_code()` filters work correctly
- [ ] `get_details()` returns complete information
- [ ] `find_references()` finds all references accurately
- [ ] Scope filtering works
- [ ] Performance <5s for Compound Protocol

## 📊 Progress Tracking

Check DETAILED_EXECUTION_CHECKLIST.md for granular task tracking.

### Phase Completion
- [ ] Phase 1: Test Validation (Days 1-5)
- [ ] Phase 2: Core Architecture (Days 6-10)
- [ ] Phase 3: Analysis Layer (Days 11-15)
- [ ] Phase 4: Engine Verification (Days 16-20)
- [ ] Phase 5: Integration & Polish (Days 21-25)

## 🚦 Getting Started

### Day 1 Quick Start

1. **Read the plans**:
   ```bash
   cat PLAN_SUMMARY.md          # Overview
   cat IMPROVEMENT_PLAN.md      # Strategy
   cat DETAILED_EXECUTION_CHECKLIST.md  # Daily tasks
   ```

2. **Start validation**:
   ```bash
   # Open first test
   vim tests/100/basic/test_v2_basic_part1.py

   # Open corresponding Solidity fixture
   vim tests/fixtures/composition_and_imports/SimpleContract.sol

   # Verify test_01: contract at line 7? Yes ✓
   # Verify test_01: name "SimpleContract"? Yes ✓
   # Verify test_02: pureFunction at line 22? Yes ✓
   # ... continue for all assertions
   ```

3. **Run tests**:
   ```bash
   pytest tests/100/basic/test_v2_basic_part1.py -v
   ```

4. **Track progress**:
   - Check off tasks in DETAILED_EXECUTION_CHECKLIST.md
   - Document any issues found
   - Update assertions as needed

## 📂 Key Files to Work On

```
sol_query/
├── core/
│   ├── parser.py           ← Fix position calculation (Day 6)
│   ├── ast_builder.py      ← Fix defaults, remove inline imports (Days 7-9)
│   ├── ast_nodes.py        ← Add parent tracking (Day 10)
│   └── source_manager.py   ← Verify caching (Day 10)
├── analysis/
│   ├── call_analyzer.py    ← Rewrite with tree-sitter (Days 11-12) **CRITICAL**
│   ├── variable_tracker.py ← Complete implementation (Day 13)
│   └── call_types.py       ← Verify classification (Day 14)
└── query/
    ├── engine_v2.py        ← Fix filters, details, references (Days 16-19) **CRITICAL**
    └── pattern_matching.py ← Fix pattern matching (Day 20)

tests/
├── 100/                    ← Validate assertions (Days 1-4)
│   ├── basic/
│   └── test_plan_*.py
└── compound/               ← Validate Compound tests (Day 5) **MOST CRITICAL**
```

## 🔍 Daily Workflow

1. **Morning**: Review checklist, identify today's tasks
2. **Implementation**: Work through tasks methodically
3. **Testing**: Run tests after each change
4. **Documentation**: Document decisions
5. **Evening**: Update checklist, prepare for tomorrow

## ⚠️ Common Pitfalls to Avoid

1. ❌ Skipping test validation - "test passes, must be correct"
   - ✅ Always verify against Solidity source

2. ❌ Using regex for Solidity code detection
   - ✅ Use tree-sitter AST exclusively

3. ❌ Adding features before fixing correctness
   - ✅ Accuracy first, features later

4. ❌ Superficial test assertions
   - ✅ Test actual values, not just presence

5. ❌ Ignoring context in defaults
   - ✅ Interface vs contract matters for visibility

## 📈 Expected Progress

```
Week 1: Tests validated, confidence in expectations
Week 2: Core architecture solid, positions accurate
Week 3: Analysis layer using tree-sitter, no regex
Week 4: Engine filters working, details complete
Week 5: All tests passing, >80% coverage, production-ready
```

## 🎉 Definition of Done

When you can say:

- ✅ "Every test assertion has been verified against the actual Solidity source code"
- ✅ "The engine uses tree-sitter exclusively for code analysis, no text patterns"
- ✅ "All Compound Protocol tests pass with accurate expectations"
- ✅ "Call classification is context-aware and accurate"
- ✅ "Test coverage is >80% with meaningful tests"
- ✅ "Engine V2 returns complete, accurate information"
- ✅ "Performance is acceptable for large codebases"

## 📞 Questions?

Refer to:
- **PLAN_SUMMARY.md** - Quick overview
- **IMPROVEMENT_PLAN.md** - Detailed strategy
- **DETAILED_EXECUTION_CHECKLIST.md** - Daily tasks
- **CLAUDE.md** - Architecture guide

---

**Ready to build a production-grade Solidity analysis engine!** 🚀

Start with Day 1 in DETAILED_EXECUTION_CHECKLIST.md
