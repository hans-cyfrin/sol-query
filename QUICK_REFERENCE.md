# Quick Reference Card

## 🎯 The Mission
Transform sol-query into a production-ready, accurate Solidity analysis engine using tree-sitter exclusively.

## 📚 Documentation Hierarchy

1. **START HERE**: `README_IMPROVEMENT.md` - Visual overview
2. **STRATEGY**: `PLAN_SUMMARY.md` - Executive summary
3. **TACTICS**: `IMPROVEMENT_PLAN.md` - Detailed phases
4. **EXECUTION**: `DETAILED_EXECUTION_CHECKLIST.md` - Daily tasks
5. **ARCHITECTURE**: `CLAUDE.md` - Technical guide

## 🔑 Core Principles

| Principle | Action |
|-----------|--------|
| **Tests are truth** | Verify every assertion against Solidity source |
| **AST not text** | Use tree-sitter, never regex for code analysis |
| **Context matters** | Defaults vary (interface vs contract) |
| **Deep not shallow** | Assert actual values, not just types |
| **Complete not partial** | Return all relevant information |
| **Accurate not fast** | Correctness over performance |

## 📅 5-Week Timeline

| Week | Phase | Focus | Key Deliverable |
|------|-------|-------|-----------------|
| 1 | Test Validation | Verify assertions vs Solidity | Accurate test suite |
| 2 | Core Architecture | Parser, AST Builder fixes | Solid foundation |
| 3 | Analysis Layer | Tree-sitter based analyzers | No regex detection |
| 4 | Engine Verification | V2 API correctness | Working filters/details |
| 5 | Integration | Testing & polish | Production ready |

## 🔧 Critical Technical Fixes

### Parser Position (Day 6)
```python
# OLD: Manual (wrong)
lines = source_code[:node.start_byte].split('\n')
line = len(lines)

# NEW: Native (correct)
return node.start_point.row + 1, node.start_point.column + 1
```

### Visibility Defaults (Day 7)
```python
# OLD: Always public (wrong)
visibility = extract_visibility(node) or Visibility.PUBLIC

# NEW: Context-aware (correct)
if parent_contract_type == "interface":
    return Visibility.EXTERNAL
else:
    return Visibility.PUBLIC
```

### Call Detection (Days 11-12)
```python
# OLD: Regex (wrong)
if re.search(r'\.call\(', source_text):
    return CallType.LOW_LEVEL

# NEW: AST (correct)
if isinstance(callee, MemberAccess) and callee.property.name == 'call':
    return CallType.LOW_LEVEL
```

### Test Assertions (Days 1-5)
```python
# OLD: Superficial (useless)
assert len(results) > 0

# NEW: Deep (valuable)
assert len(results) == 6  # Counted in Solidity file
assert results[0]['name'] == 'pureFunction'
assert results[0]['location']['line'] == 22  # Verified in source
```

## 📊 Success Metrics

```
Before  →  After
27%     →  >80%    Overall coverage
14%     →  >70%    Engine V2 coverage
❌      →  ✅      Regex detection
❌      →  ✅      Inline imports
❌      →  ✅      Compound tests passing
❌      →  ✅      Context-aware defaults
```

## 🎯 Top 3 Priorities

1. **Validate Compound tests** - Real-world validation
2. **Fix Call Analyzer** - Remove regex, use AST
3. **Fix Parser positions** - Foundation for accurate results

## 📂 Key Files (Most Changes)

```
sol_query/core/parser.py           ← Position calculation
sol_query/core/ast_builder.py      ← Context-aware building
sol_query/analysis/call_analyzer.py ← Tree-sitter detection
sol_query/query/engine_v2.py       ← Filter/detail fixes
tests/compound/*.py                ← Critical validation
tests/100/**/*.py                  ← Assertion validation
```

## ⚡ Quick Commands

```bash
# Run specific test
pytest tests/100/basic/test_v2_basic_part1.py::test_01 -v

# Run all tests with coverage
pytest tests/ -v --cov=sol_query --cov-report=term-missing

# Run Compound tests (critical)
pytest tests/compound/ -v

# Check coverage report
pytest tests/ --cov=sol_query --cov-report=html
open htmlcov/index.html

# Run single test file
pytest tests/100/basic/test_v2_basic_part1.py -v

# Run with output
pytest tests/100/basic/test_v2_basic_part1.py -v -s
```

## 🔍 Daily Checklist

- [ ] Read today's tasks in DETAILED_EXECUTION_CHECKLIST.md
- [ ] For test validation: Open Solidity file, verify assertions
- [ ] For code changes: Make change, run tests
- [ ] Document decisions
- [ ] Update checklist
- [ ] Commit working changes

## ⚠️ Red Flags

| Red Flag | What to Do |
|----------|------------|
| Test expects line 50, Solidity shows line 52 | Update test assertion |
| Using `re.search()` for Solidity code | Replace with tree-sitter AST traversal |
| Import inside function | Move to top of file |
| Interface function defaults to `public` | Fix to `external` (context-aware) |
| `get_details()` missing parameter names | Add complete parameter info |
| Assertion: `assert len(x) > 0` | Change to exact count verified in source |

## 🎯 When Stuck

1. **Test fails**: Is test assertion correct? Check Solidity source.
2. **Don't know expected value**: Open Solidity file, count manually.
3. **Engine wrong result**: Is it using tree-sitter or regex? Should use tree-sitter.
4. **Visibility wrong**: Is default context-aware? Check parent contract type.
5. **Position wrong**: Is parser using native positions? Should use `start_point`.

## 📈 Progress Indicators

### Week 1 (Test Validation)
✅ All test assertions verified against Solidity
✅ No superficial assertions
✅ Compound test expectations documented

### Week 2 (Core Architecture)
✅ Parser uses native positions
✅ No inline imports
✅ Context-aware defaults
✅ Parent tracking works

### Week 3 (Analysis Layer)
✅ No regex in Call Analyzer
✅ AST-based call classification
✅ Context-aware analysis

### Week 4 (Engine)
✅ All filters work individually
✅ Filter combinations work
✅ `get_details()` complete
✅ `find_references()` accurate

### Week 5 (Integration)
✅ 100% test pass rate
✅ >80% coverage
✅ Performance acceptable
✅ Production ready

## 🚀 Day 1 Kickstart

```bash
# 1. Read the overview
cat README_IMPROVEMENT.md

# 2. Read the summary
cat PLAN_SUMMARY.md

# 3. Open first test
vim tests/100/basic/test_v2_basic_part1.py

# 4. Open Solidity fixture
vim tests/fixtures/composition_and_imports/SimpleContract.sol

# 5. Verify line 7 has "contract SimpleContract" - YES ✓
# 6. Verify line 22 has "function pureFunction" - YES ✓
# 7. Continue for all assertions...

# 8. Run test
pytest tests/100/basic/test_v2_basic_part1.py -v

# 9. Mark tasks complete in checklist
vim DETAILED_EXECUTION_CHECKLIST.md
```

## 💡 Key Insights

1. **Tests lie sometimes** - They may pass but assert wrong things
2. **Context is king** - Same code, different meaning in different contexts
3. **Tree-sitter knows best** - Trust the AST, not text patterns
4. **Solidity is complex** - Many edge cases, defaults vary by context
5. **Coverage ≠ Quality** - Need meaningful assertions, not just execution

## ✅ Definition of Done

You're done when:

1. ✅ Every test assertion verified against Solidity source
2. ✅ Zero regex-based Solidity code detection
3. ✅ Zero inline imports
4. ✅ Compound tests pass with accurate assertions
5. ✅ Test coverage >80%
6. ✅ Engine V2 coverage >70%
7. ✅ All tests pass (100%)
8. ✅ Performance <5s for Compound
9. ✅ Context-aware defaults everywhere
10. ✅ Complete information from `get_details()`

## 🎓 Learning Resources

- **Solidity Docs**: https://docs.soliditylang.org/
- **Tree-sitter Docs**: https://tree-sitter.github.io/tree-sitter/
- **Tree-sitter Solidity**: https://github.com/JoranHonig/tree-sitter-solidity
- **Compound Protocol**: https://github.com/compound-finance/compound-protocol

## 📞 Document Quick Access

| Need | Document |
|------|----------|
| Overview | README_IMPROVEMENT.md |
| Summary | PLAN_SUMMARY.md |
| Strategy | IMPROVEMENT_PLAN.md |
| Daily Tasks | DETAILED_EXECUTION_CHECKLIST.md |
| Architecture | CLAUDE.md |
| This | QUICK_REFERENCE.md |

---

**Remember**: Accuracy over speed. Verify over assume. Tree-sitter over regex. 🎯

**Start**: DETAILED_EXECUTION_CHECKLIST.md → Day 1 → Task 1.1
