## Sol-Query V2 Demo Plan (100 Use Cases)

### Purpose
Design a comprehensive, generic demo plan to exercise the V2 API surface of `SolidityQueryEngineV2` via its three methods: `query_code`, `get_details`, and `find_references`. This plan specifies the codebase to load, conventions, and 100 concise use cases. Each use case lists inputs and expected outputs in terms of shape, fields, and qualitative constraints, avoiding environment- or dataset-dependent numeric assertions.

### Codebase Under Test
- Primary sources (existing):
  - `tests/fixtures/composition_and_imports/` (contracts with inheritance, imports, interfaces, libraries)
  - `tests/fixtures/detailed_scenarios/` (multi-file composition, token/NFT mechanics, external calls)
  - `tests/fixtures/sample_contract.sol`
  - Optionally: `tests/fixtures/sol-bug-bench/src/` for broader surface (tokens, pools, governance)

- Loading approach:
  - Initialize engine with no sources, then load directories for discoverability.
  - Prefer directory-level loads to ensure multi-file patterns are covered.

Example setup (Python):
```python
from sol_query.query.engine_v2 import SolidityQueryEngineV2

engine = SolidityQueryEngineV2()
engine.load_sources([
    "tests/fixtures/composition_and_imports/",
    "tests/fixtures/detailed_scenarios/",
    "tests/fixtures/sample_contract.sol",
])
```

### Conventions for This Plan
- Patterns are regex evaluated via Python re.search (e.g., ".*Token.*", "transfer.*", "composition_and_imports/.*").
- Case sensitivity follows implementation defaults (case-sensitive). Do not rely on disabling case sensitivity.
- Expected outputs focus on structure, presence of keys, non-emptiness where appropriate, and element types; avoid hardcoded counts.
- When a directory or file pattern is referenced, assume it exists in the listed fixtures. If not, adapt the pattern to a nearby equivalent.
- For identifier-based tests, use names that commonly exist in provided fixtures. Adapt as needed to actual files if names differ.

---

### Use Cases 1–60: query_code

1) Query all contracts
- Method: query_code
- Params: { query_type: "contracts", filters: {}, scope: {}, include: [], options: {} }
- Expected: success=True; data.results[] elements with type="ContractDeclaration"; each has location.file and location.contract.

2) Query all functions
- Method: query_code
- Params: { query_type: "functions" }
- Expected: results contain type="FunctionDeclaration", each with name and visibility fields present.

3) Query all variables
- Method: query_code
- Params: { query_type: "variables" }
- Expected: results contain type="VariableDeclaration", include visibility and is_state_variable when available.

4) Query all events
- Method: query_code
- Params: { query_type: "events" }
- Expected: elements of type="EventDeclaration" with location details.

5) Query all modifiers
- Method: query_code
- Params: { query_type: "modifiers" }
- Expected: elements of type="ModifierDeclaration" with names.

6) Query all errors
- Method: query_code
- Params: { query_type: "errors" }
- Expected: elements of type="ErrorDeclaration" (if present); empty list allowed.

7) Query all structs
- Method: query_code
- Params: { query_type: "structs" }
- Expected: elements of type="StructDeclaration"; empty list allowed.

8) Query all enums
- Method: query_code
- Params: { query_type: "enums" }
- Expected: elements of type="EnumDeclaration"; empty list allowed.

9) Query statements
- Method: query_code
- Params: { query_type: "statements" }
- Expected: elements of type="Statement"; empty list allowed.

10) Query expressions
- Method: query_code
- Params: { query_type: "expressions" }
- Expected: elements of type="Expression"; empty list allowed.

11) Query calls
- Method: query_code
- Params: { query_type: "calls" }
- Expected: results are call-like mock nodes with name/call_type when available; empty list allowed.

12) Query flow (placeholder)
- Method: query_code
- Params: { query_type: "flow" }
- Expected: success=True, may return empty results (supported as a valid type).

13) Functions by name pattern (single)
- Method: query_code
- Params: { query_type: "functions", filters: { names: "transfer.*" } }
- Expected: results where name matches the regex; zero or more matches.

14) Functions by name patterns (multiple)
- Method: query_code
- Params: { query_type: "functions", filters: { names: ["approve", ".*mint.*"] } }
- Expected: names in set; verify matching on both exact and regex.

15) Functions by visibility (public/external)
- Method: query_code
- Params: { query_type: "functions", filters: { visibility: ["public", "external"] } }
- Expected: every result has visibility in provided list.

16) Functions by state mutability (view)
- Method: query_code
- Params: { query_type: "functions", filters: { state_mutability: "view" } }
- Expected: each result has state_mutability "view".

17) Functions with no modifiers
- Method: query_code
- Params: { query_type: "functions", filters: { modifiers: [] } }
- Expected: results whose modifier list is empty or absent.

18) Functions with specific modifiers
- Method: query_code
- Params: { query_type: "functions", filters: { modifiers: ["only.*"] } }
- Expected: functions that include any modifier matching the regex.

19) Functions filtered by contract names (filters)
- Method: query_code
- Params: { query_type: "functions", filters: { contracts: [".*Token.*", ".*NFT.*"] } }
- Expected: results belong to contracts whose names match these regexes.

20) Variables by type (uint patterns)
- Method: query_code
- Params: { query_type: "variables", filters: { types: ["uint.*", "mapping.*"] } }
- Expected: variables whose type_name/var_type matches patterns.

21) State variables only
- Method: query_code
- Params: { query_type: "variables", filters: { is_state_variable: True } }
- Expected: results with is_state_variable=True.

22) Statements by type (require/if/for)
- Method: query_code
- Params: { query_type: "statements", filters: { statement_types: ["if", "for", "require"] } }
- Expected: statement elements whose internal type matches any requested type.

23) Expressions by operators (arithmetic)
- Method: query_code
- Params: { query_type: "expressions", filters: { operators: ["+", "*", "=="] } }
- Expected: expression elements that use those operators.

24) Functions that change state
- Method: query_code
- Params: { query_type: "functions", filters: { changes_state: True } }
- Expected: results for which internal `_changes_state` returns True.

25) Functions with external calls
- Method: query_code
- Params: { query_type: "functions", filters: { has_external_calls: True } }
- Expected: results where `_has_external_calls` returns True.

26) Functions with asset transfer patterns
- Method: query_code
- Params: { query_type: "functions", filters: { has_asset_transfers: True } }
- Expected: results where `_has_asset_transfers` returns True.

27) Payable functions
- Method: query_code
- Params: { query_type: "functions", filters: { is_payable: True } }
- Expected: functions whose state_mutability is payable.

28) Calls filtered by call_types (name substrings)
- Method: query_code
- Params: { query_type: "functions", filters: { call_types: ["transfer", "balanceOf"] } }
- Expected: functions that make at least one call whose name contains any provided substring.

29) Calls filtered by low_level=True
- Method: query_code
- Params: { query_type: "functions", filters: { low_level: True } }
- Expected: functions that make at least one low-level call (e.g., .call, .delegatecall, .send, .staticcall).

30) Access patterns in source (pattern search)
- Method: query_code
- Params: { query_type: "functions", filters: { access_patterns: ["msg.sender", "balanceOf(\"] } }
- Expected: functions whose source contains any of the patterns.

31) Scope: restrict to specific contracts
- Method: query_code
- Params: { query_type: "functions", scope: { contracts: [".*Token.*"] } }
- Expected: results only from matching contracts.

32) Scope: restrict to specific functions
- Method: query_code
- Params: { query_type: "variables", scope: { functions: [".*mint.*", ".*burn.*"] } }
- Expected: variables appearing in the named function contexts.

33) Scope: restrict by file patterns
- Method: query_code
- Params: { query_type: "contracts", scope: { files: ["composition_and_imports/.*"] } }
- Expected: contracts defined in files matching pattern.

34) Scope: restrict by directory patterns
- Method: query_code
- Params: { query_type: "contracts", scope: { directories: ["tests/fixtures/detailed_scenarios"] } }
- Expected: contracts from the specified directory.

35) Scope: inheritance tree filter
- Method: query_code
- Params: { query_type: "functions", scope: { inheritance_tree: "ERC721" } }
- Expected: functions whose contract inherits from the base named "ERC721" (if present).

36) Include: source code
- Method: query_code
- Params: { query_type: "functions", include: ["source"] }
- Expected: each result has source_code string when available.

37) Include: AST info
- Method: query_code
- Params: { query_type: "functions", include: ["ast"] }
- Expected: each result has ast_info with node_type/node_id/start_line.

38) Include: calls
- Method: query_code
- Params: { query_type: "functions", include: ["calls"] }
- Expected: each result has calls as a list of call descriptors (name/type/position/arguments_count when derivable).

39) Include: callers
- Method: query_code
- Params: { query_type: "functions", include: ["callers"] }
- Expected: each result has callers listing functions that reference it (best-effort/source-based).

40) Include: variables
- Method: query_code
- Params: { query_type: "functions", include: ["variables"] }
- Expected: each result has variables[] with name/access_type/variable_type when derivable.

41) Include: events
- Method: query_code
- Params: { query_type: "functions", include: ["events"] }
- Expected: each result has events[] for emit statements found.

42) Include: modifiers
- Method: query_code
- Params: { query_type: "functions", include: ["modifiers"] }
- Expected: each result includes its modifiers array (may be empty).

43) Include: natspec
- Method: query_code
- Params: { query_type: "functions", include: ["natspec"] }
- Expected: each result has natspec object with title/notice/dev/params/returns when available.

44) Include: dependencies
- Method: query_code
- Params: { query_type: "contracts", include: ["dependencies"] }
- Expected: each result lists import/using/inheritance dependencies.

45) Include: inheritance
- Method: query_code
- Params: { query_type: "contracts", include: ["inheritance"] }
- Expected: each result includes inheritance_details with base_contracts/is_abstract/interfaces/override_functions as applicable.

46) Options: max_results
- Method: query_code
- Params: { query_type: "functions", options: { max_results: 5 } }
- Expected: at most 5 results; query_info.result_count reflects truncated length.

47) Combined filters: names + visibility + state mutability
- Method: query_code
- Params: { query_type: "functions", filters: { names: ".*balance.*", visibility: ["public", "external"], state_mutability: ["view", "pure"] } }
- Expected: all returned functions satisfy all requested filter constraints.

48) Combined filters: modifiers + changes_state
- Method: query_code
- Params: { query_type: "functions", filters: { modifiers: [".*Owner.*", ".*Admin.*"], changes_state: True } }
- Expected: only functions with matching modifiers and detected state changes.

49) Combined filters: has_external_calls + call_types
- Method: query_code
- Params: { query_type: "functions", filters: { has_external_calls: True, call_types: ["external"] } }
- Expected: functions with at least one external call.

50) Combined filters: has_asset_transfers + low_level
- Method: query_code
- Params: { query_type: "functions", filters: { has_asset_transfers: True, low_level: True } }
- Expected: functions that both appear to transfer assets and use low-level calls.

51) Variables by types and scope (contract patterns)
- Method: query_code
- Params: { query_type: "variables", filters: { types: ["mapping*", "address"] }, scope: { contracts: [".*Pool.*", ".*Token.*"] } }
- Expected: variable declarations that match type patterns within selected contracts.

52) Events with include source and ast
- Method: query_code
- Params: { query_type: "events", include: ["source", "ast"] }
- Expected: event nodes provide source code and ast_info fields.

53) Modifiers in specific files
- Method: query_code
- Params: { query_type: "modifiers", scope: { files: ["composition_and_imports/.*"] } }
- Expected: modifier declarations from matching files.

54) Errors in a directory
- Method: query_code
- Params: { query_type: "errors", scope: { directories: ["tests/fixtures/detailed_scenarios"] } }
- Expected: error declarations defined in that directory (empty allowed).

55) Statements by type (loops)
- Method: query_code
- Params: { query_type: "statements", filters: { statement_types: ["for", "while", "do"] } }
- Expected: loop-related statements if present; empty allowed.

56) Expressions by operators (logical)
- Method: query_code
- Params: { query_type: "expressions", filters: { operators: ["&&", "||", "!"] } }
- Expected: logical expressions matched.

57) Access patterns in variables (source scan)
- Method: query_code
- Params: { query_type: "variables", filters: { names: [".*supply.*", ".*owner.*"] } }
- Expected: variables whose names match patterns.

58) Calls query filtered by names
- Method: query_code
- Params: { query_type: "calls", filters: { names: ["transfer", "withdraw"] } }
- Expected: call nodes whose names match any of the provided regexes.

59) Contracts include dependencies and inheritance
- Method: query_code
- Params: { query_type: "contracts", include: ["dependencies", "inheritance"] }
- Expected: each contract shows base contracts and imports/using declarations if present.

60) Functions include multiple: source, ast, calls, variables, events, modifiers
- Method: query_code
- Params: { query_type: "functions", include: ["source", "ast", "calls", "variables", "events", "modifiers"] }
- Expected: result items include all requested fields.

---

### Use Cases 61–82: get_details

61) Function details by name
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer"] }
- Expected: success=True; data.elements["transfer"] includes basic_info (name/type/location/signature), detailed_info (visibility/state_mutability/modifiers/calls), and comprehensive_info (dependencies/call_graph/data_flow).

62) Function details with options
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer"], options: { include_source: True } }
- Expected: detailed_info includes source_code along with visibility/state_mutability/modifiers and calls[] list.

63) Function details by signature
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer(address,uint256)"] }
- Expected: signature-based matching resolves the function and returns comprehensive information including dependencies, call_graph, and data_flow keys.

64) Contract details by name
- Method: get_details
- Params: { element_type: "contract", identifiers: ["Token"] }
- Expected: comprehensive information including basic_info (location), detailed_info, and comprehensive_info (dependencies/call_graph); may include siblings/context.

65) Contract details with context
- Method: get_details
- Params: { element_type: "contract", identifiers: ["Token"], include_context: True }
- Expected: context.file_context and siblings[] populated along with comprehensive analysis.

66) Contract details by file:contract pattern
- Method: get_details
- Params: { element_type: "contract", identifiers: ["tests/fixtures/composition_and_imports/MultipleInheritance.sol:MultipleInheritance"] }
- Expected: file path pattern + contract name resolves the element with comprehensive info.

67) Variable details by name
- Method: get_details
- Params: { element_type: "variable", identifiers: ["totalSupply"] }
- Expected: comprehensive information including basic_info (location), detailed_info, and comprehensive_info; signature may be None.

68) Modifier details by name
- Method: get_details
- Params: { element_type: "modifier", identifiers: ["onlyOwner"] }
- Expected: comprehensive analysis with detailed_info.source_code present when available; context shows parent/siblings if derivable.

69) Event details by name
- Method: get_details
- Params: { element_type: "event", identifiers: ["Transfer"] }
- Expected: comprehensive information including basic_info (location/type), detailed_info, and comprehensive_info.

70) Error details by name
- Method: get_details
- Params: { element_type: "error", identifiers: ["InsufficientBalance"] }
- Expected: comprehensive information when present; not-found allowed.

71) Struct details by name
- Method: get_details
- Params: { element_type: "struct", identifiers: ["UserData"] }
- Expected: comprehensive information for struct elements.

72) Enum details by name
- Method: get_details
- Params: { element_type: "enum", identifiers: ["TokenState"] }
- Expected: comprehensive information for enum elements.

73) Function details by contract.element
- Method: get_details
- Params: { element_type: "function", identifiers: ["Token.transfer"] }
- Expected: identifier resolved via contract+name format with comprehensive information.

74) Multiple function identifiers mixed
- Method: get_details
- Params: { element_type: "function", identifiers: ["approve", "balanceOf", "mint"] }
- Expected: per-identifier found/not-found entries with comprehensive information for found ones.

75) include_context=False
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer"], include_context: False }
- Expected: no context key for the element, only basic_info, detailed_info, and comprehensive_info.

76) Options: include_source=False
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer"], options: { include_source: False } }
- Expected: detailed_info.source_code omitted or None.

77) Options: include_signatures=True (default)
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer"], options: { include_signatures: True } }
- Expected: basic_info.signature present when derivable.

78) Options: show_call_chains
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer"], options: { show_call_chains: True } }
- Expected: comprehensive_info.call_graph present. (Options flag accepted; output structure is unchanged.)

79) Mixed element types batch (contracts and variables)
- Method: get_details
- Params: Multiple calls per type. For contracts: { element_type: "contract", identifiers: ["Token", "NFT"] }; For variables: { element_type: "variable", identifiers: ["owner", "balances"] }
- Expected: per-call results typed appropriately with comprehensive information.

80) Not-found identifiers
- Method: get_details
- Params: { element_type: "function", identifiers: ["nonexistentFunction"] }
- Expected: elements.nonexistentFunction.found=False with error message.

81) Sibling context present
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer"], include_context: True }
- Expected: context.siblings exists and lists nearby elements (limited to 5).

82) Analysis summary fields
- Method: get_details
- Params: { element_type: "function", identifiers: ["transfer", "approve"] }
- Expected: data.analysis_summary includes elements_found, elements_requested, success_rate, features_analyzed.

---

### Use Cases 83–100: find_references

83) References for a function (all)
- Method: find_references
- Params: { target: "transfer", target_type: "function", reference_type: "all" }
- Expected: data.references.usages[], definitions[] present; metadata.performance available; success=True.

84) Function usages only
- Method: find_references
- Params: { target: "transfer", target_type: "function", reference_type: "usages" }
- Expected: references.usages populated where source references exist.

85) Function definitions only
- Method: find_references
- Params: { target: "transfer", target_type: "function", reference_type: "definitions" }
- Expected: primary definition plus overrides/interface definitions when present.

86) References direction forward
- Method: find_references
- Params: { target: "transfer", target_type: "function", direction: "forward" }
- Expected: usages discovered in nodes after the target element.

87) References direction backward
- Method: find_references
- Params: { target: "transfer", target_type: "function", direction: "backward" }
- Expected: usages discovered in nodes before the target element.

88) References both directions
- Method: find_references
- Params: { target: "transfer", target_type: "function", direction: "both" }
- Expected: union of forward/backward behaviors; may be superset of each.

89) Max depth limit (1)
- Method: find_references
- Params: { target: "transfer", target_type: "function", direction: "both", max_depth: 1 }
- Expected: traversal adheres to depth limit; metadata.performance.depth_reached reflects.

90) Unlimited depth (-1)
- Method: find_references
- Params: { target: "transfer", target_type: "function", max_depth: -1 }
- Expected: allowed by validation; depth may extend as far as relationships permit.

91) With call chains
- Method: find_references
- Params: { target: "transfer", target_type: "function", options: { show_call_chains: True }, max_depth: 3 }
- Expected: data.references.call_chains is a list of sequences (best-effort).

92) Variable references (all)
- Method: find_references
- Params: { target: "balances", target_type: "variable", reference_type: "all" }
- Expected: usages identified as assignment/array_access/member_access/variable_read; definitions include primary declaration.

93) Contract references
- Method: find_references
- Params: { target: "Token", target_type: "contract", reference_type: "all" }
- Expected: usages include instantiation or references in code; definitions show primary contract declaration.

94) References filtered by contracts
- Method: find_references
- Params: { target: "transfer", target_type: "function", filters: { contracts: [".*Token.*"] } }
- Expected: only usages/definitions whose location.contract matches patterns.

95) References filtered by files
- Method: find_references
- Params: { target: "transfer", target_type: "function", filters: { files: ["detailed_scenarios/.*"] } }
- Expected: only locations from matching files.

96) Non-existent target element
- Method: find_references
- Params: { target: "doesNotExist", target_type: "function" }
- Expected: success=False error response with errors[] indicating not found.

97) Target types coverage (modifier)
- Method: find_references
- Params: { target: "onlyOwner", target_type: "modifier", reference_type: "all" }
- Expected: structure of references object returned; empty lists allowed when not present.

98) Target types coverage (event)
- Method: find_references
- Params: { target: "Transfer", target_type: "event", reference_type: "all" }
- Expected: structure of references object returned; empty lists allowed when not present.

99) Target types coverage (struct)
- Method: find_references
- Params: { target: "UserData", target_type: "struct", reference_type: "all" }
- Expected: structure of references object returned; empty lists allowed when not present.

100) Target types coverage (enum)
- Method: find_references
- Params: { target: "TokenState", target_type: "enum", reference_type: "all" }
- Expected: structure of references object returned; empty lists allowed when not present.

---

### Execution Notes
- For name patterns and identifiers, align with actual names available in fixtures. When a specific identifier is unavailable, adapt the identifier to a similar one in the same directory set.
- Many result lists can be empty depending on code contents; empty is acceptable if structure is correct and no errors are returned.
- This plan intentionally emphasizes API coverage across combinations of filters, scope, include, and options, plus all element/target types.


