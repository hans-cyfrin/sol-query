# Detailed Execution Checklist

This document provides granular, actionable tasks for each phase of the improvement plan.

---

## PHASE 1: TEST VALIDATION (Days 1-5)

### Day 1: Basic Tests Part 1-3

#### Task 1.1: `test_v2_basic_part1.py` - SimpleContract Tests

- [ ] **test_01_query_contracts_in_simplecontract**
  - [ ] Open `tests/fixtures/composition_and_imports/SimpleContract.sol`
  - [ ] Verify contract declaration is at line 7, column 1
  - [ ] Verify contract name is exactly "SimpleContract"
  - [ ] Verify no inheritance (empty list)
  - [ ] Update assertion if wrong

- [ ] **test_02_query_functions_in_simplecontract**
  - [ ] For each function, note actual line number in source:
    - [ ] `pureFunction` - verify line 22, signature `pureFunction(uint256,uint256)`, visibility public, mutability pure
    - [ ] `viewFunction` - verify line 27, signature `viewFunction()`, visibility public, mutability view
    - [ ] `setValue` - verify line 32, signature `setValue(uint256)`, visibility public, mutability nonpayable, modifier onlyOwner
    - [ ] `deposit` - verify line 37, signature `deposit()`, visibility public, mutability payable
    - [ ] `internalHelper` - verify line 42, visibility internal, mutability pure
    - [ ] `privateHelper` - verify line 47, visibility private, mutability pure
  - [ ] Verify constructor at line 16 if queried
  - [ ] Update all assertions with actual values

- [ ] **test_03_query_variables_in_simplecontract**
  - [ ] `value` - verify line 8, type uint256, visibility public
  - [ ] `owner` - verify line 9, type address, visibility public
  - [ ] Update assertions

- [ ] **test_04_query_events_in_erc721imports**
  - [ ] Open `tests/fixtures/composition_and_imports/ERC721WithImports.sol`
  - [ ] Find TokenMinted event - note exact line, parameters
  - [ ] Find PriceUpdated event - note exact line, parameters
  - [ ] Update assertions

- [ ] **test_05_query_modifiers_in_simplecontract**
  - [ ] Verify `onlyOwner` modifier at line 11
  - [ ] Check if other modifiers exist
  - [ ] Update assertions

#### Task 1.2: `test_v2_basic_part2.py` - Filter Tests

- [ ] **For each test function**:
  - [ ] Read test code
  - [ ] Identify target Solidity file
  - [ ] Manually find expected results in Solidity
  - [ ] Verify filter logic is correct:
    - Visibility filters (external, public, internal, private)
    - State mutability filters (pure, view, payable, nonpayable)
    - Name pattern filters (exact, wildcard, regex)
  - [ ] Update assertions with actual expected results
  - [ ] Add assertions for specific values (not just counts)

#### Task 1.3: `test_v2_basic_part3.py` - Advanced Filters

- [ ] **For each test function**:
  - [ ] Same process as 1.2
  - [ ] Pay special attention to:
    - Modifier filters (functions WITH specific modifiers applied)
    - Combined filters (multiple criteria)
    - Edge cases (empty results, single result)
  - [ ] Verify test expectations match Solidity reality

### Day 2: Basic Tests Part 4-5

#### Task 2.1: `test_v2_basic_part4.py`

- [ ] **For each test**:
  - [ ] Validate against source
  - [ ] Check complex scenarios (inheritance, imports)
  - [ ] Update assertions

#### Task 2.2: `test_v2_basic_part5.py`

- [ ] **For each test**:
  - [ ] Validate against source
  - [ ] Verify edge cases
  - [ ] Update assertions

### Day 3: Plan Tests Part 1-5

#### Task 3.1: `test_plan_part1.py` through `test_plan_part5.py`

**For EACH test function in EACH file**:

- [ ] Read test code carefully
- [ ] Identify all Solidity files involved
- [ ] Open each Solidity file
- [ ] Manually count/find expected results:
  - [ ] If testing contracts: count actual contracts, note names, types
  - [ ] If testing functions: count actual functions, note names, signatures, line numbers
  - [ ] If testing variables: count actual variables, note names, types, line numbers
  - [ ] If testing modifiers/events/errors: same process
- [ ] Verify filter combinations work correctly in expectation
- [ ] Update assertions to match reality
- [ ] Add missing assertions (e.g., specific function names, not just count)

**Special attention**:
- [ ] Inheritance tests - verify inherited members are counted correctly
- [ ] Import tests - verify imported symbols are tracked
- [ ] Scope tests - verify scoping to contracts/files works

### Day 4: Plan Tests Part 6-10

#### Task 4.1: `test_plan_part6.py` through `test_plan_part10.py`

- [ ] Same process as Day 3
- [ ] Focus on advanced features:
  - [ ] `get_details()` tests - verify ALL returned fields are accurate
  - [ ] `find_references()` tests - manually trace references in code
  - [ ] Complex filter combinations
  - [ ] Edge cases

### Day 5: Other Test Suites

#### Task 5.1: Validate All Remaining Tests

Files to check:
- [ ] `tests/test_comprehensive_queries.py`
- [ ] `tests/test_contextual_analysis.py`
- [ ] `tests/test_contract_qualified_functions.py`
- [ ] `tests/test_data_flow_analysis.py`
- [ ] `tests/test_engine_v2_api.py`
- [ ] `tests/test_engine_v2_comprehensive.py`
- [ ] `tests/test_external_call_filters.py`
- [ ] `tests/test_filters_implementation.py`
- [ ] `tests/test_get_details_groupstaking.py`
- [ ] `tests/test_get_details_tokenstreamer.py`
- [ ] `tests/test_import_analyzer.py`
- [ ] `tests/test_line_content_enhancement.py`
- [ ] `tests/test_llm_serialization.py`
- [ ] `tests/test_modifier_serialization.py`
- [ ] `tests/test_negation_filters.py`
- [ ] `tests/test_new_api_features.py`
- [ ] `tests/test_query_composition.py`

**For each**:
- [ ] Read test
- [ ] Validate against fixtures
- [ ] Update assertions

#### Task 5.2: Compound Tests (MOST CRITICAL)

- [ ] **test_compound_comprehensive.py**:
  - [ ] Open `tests/fixtures/compound-protocol/contracts/CErc20.sol`
  - [ ] Find `mint` function - note EXACT line number, signature, visibility
  - [ ] Open `tests/fixtures/compound-protocol/contracts/Comptroller.sol`
  - [ ] Verify ALL expected contracts are listed
  - [ ] For each assertion in test:
    - [ ] Find corresponding code in Compound contracts
    - [ ] Verify assertion matches reality
    - [ ] Update if wrong

- [ ] **test_next_batch_issues.py**:
  - [ ] Same validation process
  - [ ] These are edge cases - verify they test real edge cases

---

## PHASE 2: CORE ARCHITECTURE (Days 6-10)

### Day 6: Parser Fixes

#### Task 6.1: Fix tree-sitter API Deprecation

- [ ] Open `sol_query/core/parser.py`
- [ ] Find line 31: `self._language = tree_sitter.Language(tree_sitter_solidity.language())`
- [ ] Check tree-sitter documentation for correct API
- [ ] Update to: `self._language = tree_sitter.Language(tree_sitter_solidity.language())`
  - Or whatever the non-deprecated API is
- [ ] Run test to verify warning disappears: `pytest tests/100/basic/test_v2_basic_part1.py::test_01 -v`
- [ ] Verify tests still pass

#### Task 6.2: Fix Position Calculation

- [ ] Open `sol_query/core/parser.py`
- [ ] Find `_get_node_position()` method (line 214)
- [ ] Current implementation:
  ```python
  lines = source_code[:node.start_byte].split('\n')
  line = len(lines)
  column = len(lines[-1]) + 1
  ```
- [ ] Replace with tree-sitter native positions:
  ```python
  # Tree-sitter provides row/column directly (0-indexed)
  return node.start_point.row + 1, node.start_point.column + 1
  ```
- [ ] Do same for `_get_node_end_position()` (line 221)
- [ ] Run ALL tests to verify line number assertions still pass
- [ ] If tests fail, check if it's position calculation or test assertion issue

#### Task 6.3: Create Position Test

- [ ] Create `tests/test_position_accuracy.py`
- [ ] Write test with known positions:
  ```python
  def test_position_accuracy():
      code = '''// Line 1
  pragma solidity ^0.8.0;  // Line 2

  contract Test {  // Line 4, column 1
      uint256 public value;  // Line 5, column 5
  }
  '''
      parser = SolidityParser()
      tree = parser.parse_text(code)
      # Find contract node, verify position is (4, 1)
      # Find variable node, verify position is (5, 5)
  ```
- [ ] Run test, verify accuracy

### Day 7: AST Builder Part 1

#### Task 7.1: Remove Inline Imports

- [ ] Open `sol_query/core/ast_builder.py`
- [ ] Find all `from ... import ...` statements inside functions/methods
- [ ] Move to top of file
- [ ] Check for circular imports:
  - If circular import, refactor to break cycle
  - Consider using TYPE_CHECKING guard
- [ ] Run tests to verify no breakage

#### Task 7.2: Fix Visibility Defaults

- [ ] Find `_build_function()` method
- [ ] Current logic for default visibility:
  ```python
  visibility = self._extract_visibility(node) or Visibility.PUBLIC
  ```
- [ ] Make context-aware:
  ```python
  def _get_default_function_visibility(self, node: tree_sitter.Node, parent_contract_type: str) -> Visibility:
      if parent_contract_type == "interface":
          return Visibility.EXTERNAL
      else:
          return Visibility.PUBLIC
  ```
- [ ] Update `_build_function()` to use context-aware default
- [ ] Find `_build_variable()` method
- [ ] State variable visibility defaults to `internal` if not specified
- [ ] Update accordingly
- [ ] Write test:
  ```python
  def test_interface_function_default_visibility():
      code = '''
      interface ITest {
          function foo();  // Should default to external
      }
      contract Test {
          function bar();  // Should default to public
      }
      '''
      # Parse and verify defaults
  ```

### Day 8: AST Builder Part 2

#### Task 8.1: Fix Parameter Extraction

- [ ] Find `_build_parameter()` method
- [ ] Verify parameter name is extracted correctly
- [ ] Verify parameter type is extracted correctly
- [ ] For event parameters, check for `indexed` keyword:
  ```python
  is_indexed = False
  for child in node.children:
      if child.type == 'indexed':
          is_indexed = True
  ```
- [ ] Test with event parameters

#### Task 8.2: Fix Inheritance Parsing

- [ ] Find `_build_contract()` method
- [ ] Find where inheritance is parsed
- [ ] Verify inheritance order is preserved (order matters in Solidity)
- [ ] Capture constructor arguments in inheritance:
  ```solidity
  contract Child is Parent(arg1, arg2) { }
  ```
- [ ] Test with multiple inheritance and arguments

### Day 9: AST Builder Part 3

#### Task 9.1: Verify Statement/Expression Building

- [ ] Review all `_build_*_statement()` methods
- [ ] Ensure each statement type is correctly categorized
- [ ] Test with complex nested statements:
  ```solidity
  function test() {
      if (condition) {
          for (uint i = 0; i < 10; i++) {
              if (nested) {
                  doSomething();
              }
          }
      }
  }
  ```

#### Task 9.2: Verify Call Expression Building

- [ ] Find `_build_call()` method
- [ ] Ensure nested member access is preserved:
  ```solidity
  contract.method().anotherMethod()
  ```
- [ ] Ensure call arguments are captured
- [ ] Test with complex calls

### Day 10: AST Nodes & Source Manager

#### Task 10.1: Fix Parent Tracking

- [ ] Open `sol_query/core/ast_nodes.py`
- [ ] Add `parent` field to ASTNode:
  ```python
  parent: Optional['ASTNode'] = Field(default=None, exclude=True)
  ```
- [ ] In AST Builder, when creating child nodes, set parent reference
- [ ] Implement `_find_containing_function()`:
  ```python
  def _find_containing_function(self) -> Optional['FunctionDeclaration']:
      current = self.parent
      while current:
          if isinstance(current, FunctionDeclaration):
              return current
          current = current.parent
      return None
  ```

#### Task 10.2: Verify Source Manager Caching

- [ ] Open `sol_query/core/source_manager.py`
- [ ] Find cache invalidation methods
- [ ] Verify `clear_caches()` is called when files are reloaded
- [ ] Write test:
  ```python
  def test_cache_invalidation():
      # Load file
      # Query
      # Modify file
      # Reload
      # Query again - should get updated results
  ```

---

## PHASE 3: ANALYSIS LAYER (Days 11-15)

### Day 11-12: Call Analyzer Rewrite

#### Task 11.1: Analyze Current Implementation

- [ ] Open `sol_query/analysis/call_analyzer.py`
- [ ] Identify all regex patterns used
- [ ] For each pattern, determine tree-sitter equivalent:
  - `.call(` -> check if node.type == "call_expression" and function name is "call"
  - `.delegatecall(` -> similar
  - Contract calls -> check if callee is not in current contract context

#### Task 11.2: Implement Tree-Sitter Based Detection

- [ ] Create new method `_classify_call_from_ast(call_expr: CallExpression, context: Dict) -> CallType`
- [ ] Logic:
  ```python
  def _classify_call_from_ast(self, call_expr: CallExpression, context: Dict) -> CallType:
      # Get callee
      callee = call_expr.callee

      # Check if it's a member access (e.g., x.method())
      if isinstance(callee, MemberAccess):
          object_name = callee.object.name if isinstance(callee.object, Identifier) else None
          method_name = callee.property.name if isinstance(callee.property, Identifier) else None

          # Check if method is low-level call
          if method_name in ['call', 'delegatecall', 'staticcall', 'send', 'transfer']:
              return CallType.LOW_LEVEL

          # Check if object is external contract
          if object_name not in context.get('local_variables', []) and \
             object_name not in context.get('state_variables', []) and \
             object_name not in context.get('parameters', []):
              # Likely external contract
              return CallType.EXTERNAL

          # Check if method exists in current contract
          if method_name in context.get('contract_functions', []):
              return CallType.INTERNAL
          else:
              return CallType.EXTERNAL

      # Direct function call
      elif isinstance(callee, Identifier):
          if callee.name in context.get('contract_functions', []):
              return CallType.INTERNAL
          else:
              # Could be library or external
              return CallType.LIBRARY

      return CallType.UNKNOWN
  ```
- [ ] Remove all regex-based detection
- [ ] Remove pattern dictionaries

#### Task 11.3: Fix Context Building

- [ ] Find `_build_contract_context()` method
- [ ] Ensure it includes:
  - [ ] All functions from current contract
  - [ ] All modifiers from current contract
  - [ ] All state variables
  - [ ] All functions from inherited contracts (recursive)
  - [ ] All functions from implemented interfaces
- [ ] Test with inherited contract

#### Task 11.4: Test Call Classification

- [ ] Create comprehensive test:
  ```python
  def test_call_classification():
      code = '''
      contract Test {
          function internal() internal {}
          function external() external {}

          function caller() public {
              internal();  // INTERNAL
              this.external();  // EXTERNAL
              address(this).call("");  // LOW_LEVEL
              OtherContract(addr).method();  // EXTERNAL
          }
      }
      '''
      # Parse and verify each call type
  ```

### Day 13: Variable Tracker

#### Task 13.1: Review Implementation

- [ ] Open `sol_query/analysis/variable_tracker.py`
- [ ] Find all methods
- [ ] For each method, verify it's implemented or remove if not needed

#### Task 13.2: Implement Scope Tracking

- [ ] Ensure variable tracker handles:
  - [ ] Function parameters
  - [ ] Local variables
  - [ ] State variables
  - [ ] Variable shadowing (local shadows state)
- [ ] Test with shadowed variables

### Day 14: Call Types & Data Flow

#### Task 14.1: Review Call Types

- [ ] Open `sol_query/analysis/call_types.py`
- [ ] Verify CallType enum has all necessary types
- [ ] Verify CallTypeDetector methods work correctly
- [ ] Add tests for edge cases

#### Task 14.2: Data Flow Decision

- [ ] Check if data flow is used by V2 API
- [ ] If not used, comment it out or remove (can add back later)
- [ ] If used, implement fully with tests

### Day 15: Import Analyzer

#### Task 15.1: Review Import Handling

- [ ] Open `sol_query/analysis/import_analyzer.py`
- [ ] Verify import path resolution works
- [ ] Test with:
  - [ ] Relative imports: `import "./Token.sol"`
  - [ ] Named imports: `import {Token} from "./Token.sol"`
  - [ ] Aliased imports: `import {Token as MyToken} from "./Token.sol"`
  - [ ] Node modules style: `import "@openzeppelin/contracts/token/ERC20/ERC20.sol"`

---

## PHASE 4: ENGINE VERIFICATION (Days 16-20)

### Day 16-17: Engine V2 `query_code()` Fixes

#### Task 16.1: Test Each Filter Individually

**Create test file**: `tests/test_engine_v2_filters_isolated.py`

- [ ] **Test `visibility` filter**:
  ```python
  def test_visibility_filter_public():
      result = engine.query_code("functions", {"visibility": "public"})
      # Verify ALL results have visibility == "public"
      for func in result['data']['results']:
          assert func['visibility'] == 'public'
  ```
  - [ ] Test: public, private, internal, external
  - [ ] Verify no false positives/negatives

- [ ] **Test `state_mutability` filter**:
  - [ ] Test: pure, view, payable, nonpayable
  - [ ] Verify accuracy

- [ ] **Test `names` filter**:
  - [ ] Test exact match: `{"names": ["transfer"]}`
  - [ ] Test wildcard: `{"names": ["*transfer*"]}`
  - [ ] Test multiple: `{"names": ["transfer", "approve"]}`
  - [ ] Test regex: `{"names": ["^get.*"]}`

- [ ] **Test `has_external_calls` filter**:
  - [ ] Create test contract with known external calls
  - [ ] Query with filter
  - [ ] Verify only functions with external calls are returned

- [ ] **Test `has_asset_transfers` filter**:
  - [ ] Similar to above

- [ ] **Test `modifiers` filter**:
  - [ ] Create test contract with functions having specific modifiers
  - [ ] Query with `{"modifiers": ["onlyOwner"]}`
  - [ ] Verify only functions WITH onlyOwner modifier are returned

#### Task 16.2: Test Filter Combinations

- [ ] Test: `{"visibility": "external", "state_mutability": "view"}`
- [ ] Test: `{"names": ["transfer*"], "visibility": "public"}`
- [ ] Test: `{"has_external_calls": true, "modifiers": ["onlyOwner"]}`
- [ ] Verify logical AND (all criteria must match)

#### Task 16.3: Fix Filter Implementation

- [ ] Open `sol_query/query/engine_v2.py`
- [ ] Find filter application logic in `query_code()`
- [ ] For each filter:
  - [ ] Verify it checks the AST node field correctly
  - [ ] Fix any bugs found during testing
  - [ ] Ensure filter logic is clear and correct

### Day 18: Engine V2 `get_details()` Fixes

#### Task 18.1: Test Detail Completeness

- [ ] **Test function details**:
  ```python
  def test_get_details_function_complete():
      result = engine.get_details("function", ["transfer"])
      func = result['data']['results'][0]

      # Verify ALL fields are present and accurate:
      assert func['name'] == 'transfer'
      assert func['signature'] == 'transfer(address,uint256)'
      assert func['visibility'] == 'public'
      assert func['state_mutability'] == 'nonpayable'
      assert 'parameters' in func
      assert len(func['parameters']) == 2
      assert func['parameters'][0]['name'] == 'to'  # Actual param name
      assert func['parameters'][0]['type'] == 'address'
      assert func['parameters'][1]['name'] == 'amount'
      assert func['parameters'][1]['type'] == 'uint256'
      assert 'return_parameters' in func
      assert 'modifiers' in func
      assert 'body' in func
  ```

- [ ] **Test contract details**:
  - [ ] Verify inheritance chain
  - [ ] Verify all members listed
  - [ ] Verify contract type (contract/interface/library)

- [ ] **Test variable details**:
  - [ ] Verify full type information
  - [ ] Verify visibility
  - [ ] Verify constant/immutable flags
  - [ ] Verify initialization value if present

#### Task 18.2: Fix Detail Generation

- [ ] Open `sol_query/query/engine_v2.py`
- [ ] Find `get_details()` method
- [ ] For each element type, ensure ALL relevant fields are included
- [ ] Fix any missing fields

### Day 19: Engine V2 `find_references()` Fixes

#### Task 19.1: Test Reference Finding

- [ ] **Create test with known references**:
  ```python
  def test_find_references_variable():
      # Fixture with known references:
      # - Variable 'balance' defined at line X
      # - Read at line Y in function A
      # - Written at line Z in function B
      # - Read at line W in function C

      result = engine.find_references("balance", "variable")
      refs = result['data']['results']

      # Verify ALL references found:
      assert len(refs) == 3  # Y, Z, W
      # Verify no false positives
  ```

- [ ] **Test direction filter**:
  - [ ] `direction: "both"` - all references
  - [ ] `direction: "upstream"` - references that affect this
  - [ ] `direction: "downstream"` - references affected by this

- [ ] **Test reference types**:
  - [ ] Function references (calls to function)
  - [ ] Variable references (reads/writes)
  - [ ] Contract references (usage of contract)

#### Task 19.2: Fix Reference Implementation

- [ ] Find `find_references()` method
- [ ] Verify it traverses AST correctly to find all references
- [ ] Fix any bugs

### Day 20: Scope Filtering & Pattern Matching

#### Task 20.1: Test Scope Filtering

- [ ] **Test file scope**:
  ```python
  result = engine.query_code("functions", {}, {"files": [".*Token.sol"]})
  # Verify only functions from Token.sol
  for func in result['data']['results']:
      assert 'Token.sol' in func['location']['file']
  ```

- [ ] **Test contract scope**:
  ```python
  result = engine.query_code("functions", {}, {"contracts": ["Token"]})
  # Verify only functions from Token contract
  for func in result['data']['results']:
      assert func['location']['contract'] == 'Token'
  ```

#### Task 20.2: Fix Pattern Matching

- [ ] Open `sol_query/utils/pattern_matching.py`
- [ ] Test wildcard matching:
  - `*Token` matches "ERC20Token", "Token", "MyToken"
  - `Token*` matches "Token", "TokenSale"
  - `*Token*` matches all
  - `?oken` matches "Token" (single char)
- [ ] Test regex matching
- [ ] Fix any bugs

---

## PHASE 5: INTEGRATION (Days 21-25)

### Day 21-22: Run Full Test Suite

#### Task 21.1: Run All Tests

- [ ] Run: `pytest tests/ -v --tb=short > test_results.txt 2>&1`
- [ ] Review ALL failures
- [ ] For each failure:
  1. [ ] Read test code
  2. [ ] Check if test assertion is correct (verify against Solidity)
  3. [ ] If test is correct, debug engine
  4. [ ] If test is wrong, fix test
  5. [ ] Document decision

#### Task 21.2: Fix Engine Issues

- [ ] For each engine bug found:
  - [ ] Identify root cause
  - [ ] Fix bug
  - [ ] Verify fix doesn't break other tests
  - [ ] Add regression test if needed

### Day 23: Add Missing Coverage

#### Task 23.1: Identify Uncovered Code

- [ ] Run: `pytest tests/ --cov=sol_query --cov-report=html`
- [ ] Open `htmlcov/index.html`
- [ ] Find files with <50% coverage
- [ ] For each:
  - [ ] Check if code is actually used
  - [ ] If used, write tests
  - [ ] If unused, mark for potential removal

#### Task 23.2: Write New Tests

- [ ] Target: >80% coverage overall
- [ ] Focus on critical paths:
  - [ ] Parser edge cases
  - [ ] AST builder for all Solidity constructs
  - [ ] Engine filters and combinations
  - [ ] Error handling

### Day 24: Performance Testing

#### Task 24.1: Benchmark Performance

- [ ] Create benchmark script:
  ```python
  import time

  def benchmark_query():
      start = time.time()
      engine = SolidityQueryEngineV2()
      engine.load_sources("tests/fixtures/compound-protocol/contracts/")
      load_time = time.time() - start

      start = time.time()
      result = engine.query_code("functions")
      query_time = time.time() - start

      print(f"Load time: {load_time:.2f}s")
      print(f"Query time: {query_time:.2f}s")
  ```
- [ ] Run benchmark
- [ ] Identify bottlenecks with profiler:
  ```bash
  python -m cProfile -o profile.stats benchmark.py
  python -m pstats profile.stats
  ```

#### Task 24.2: Optimize

- [ ] If AST building is slow:
  - [ ] Check for redundant operations
  - [ ] Ensure caching works
- [ ] If queries are slow:
  - [ ] Check filter implementation efficiency
  - [ ] Consider indexing for common queries
- [ ] Goal: Compound contracts load + query <5 seconds

### Day 25: Final Verification

#### Task 25.1: Final Test Run

- [ ] Run: `pytest tests/ -v --cov=sol_query`
- [ ] Verify: 100% pass rate
- [ ] Verify: >80% coverage
- [ ] Verify: No warnings (except deprecation warnings from dependencies)

#### Task 25.2: Documentation Update

- [ ] Update README.md with any API changes
- [ ] Update CLAUDE.md with new architectural insights
- [ ] Update docs/api-reference-v2.md if needed
- [ ] Add migration guide if breaking changes

#### Task 25.3: Final Checklist

- [ ] All Phase 1 success criteria met
- [ ] All Phase 2 success criteria met
- [ ] All Phase 3 success criteria met
- [ ] All Phase 4 success criteria met
- [ ] All Phase 5 success criteria met
- [ ] No inline imports
- [ ] No regex-based Solidity detection
- [ ] Tree-sitter exclusively used
- [ ] Context-aware defaults
- [ ] Compound tests pass
- [ ] Performance acceptable

---

## Daily Workflow

Each day:

1. **Morning**: Review checklist, identify today's tasks
2. **Implementation**: Work through tasks methodically
3. **Testing**: After each change, run relevant tests
4. **Documentation**: Document decisions and changes
5. **Evening**: Update checklist, prepare for next day

## Notes

- **Don't skip validation steps** - test assertions must be verified against source
- **Don't rush** - accuracy is more important than speed
- **Write tests first** when fixing bugs - ensure bug is captured
- **Run tests frequently** - catch regressions early
- **Document decisions** - when fixing a test, note why assertion was wrong

