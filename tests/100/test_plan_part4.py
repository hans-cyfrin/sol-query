"""
Test Plan Part 4: Use Cases 31-40
Tests query_code functionality with scope and include parameters.
"""
import json
import pytest
import re


def test_31_scope_restrict_to_specific_contracts(engine):
    """
    Use Case 31: Scope: restrict to specific contracts
    - Method: query_code
    - Params: { query_type: "functions", scope: { contracts: [".*Token.*"] } }
    - Expected: results only from matching contracts.
    """
    resp = engine.query_code("functions", {}, {"contracts": [".*Token.*"]})
    print("Functions(scope=.*Token.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions from Token contracts
    if results:
        assert len(results) > 10  # Should find multiple functions from Token contracts

        for result in results:
            assert result.get("type") == "function"
            location = result.get("location", {})
            contract = location.get("contract", "")
            file_path = location.get("file", "")

            # Should match Token pattern in contract name or file
            matches_token = re.search(r".*Token.*", contract, re.IGNORECASE) if contract else False
            if not matches_token:
                matches_token = "Token" in file_path
            assert matches_token, f"Function {result.get('name')} from {contract} in {file_path} doesn't match Token pattern"

        # Should find specific Token functions
        found_names = {r.get("name") for r in results}
        expected_token_functions = {"transfer", "mint", "approve", "balanceOf", "getInfo"}
        assert expected_token_functions.intersection(found_names), f"Expected Token functions not found"


def test_32_scope_restrict_to_specific_functions(engine):
    """
    Use Case 32: Scope: restrict to specific functions
    - Method: query_code
    - Params: { query_type: "variables", scope: { functions: [".*mint.*", ".*burn.*"] } }
    - Expected: variables appearing in the named function contexts.
    """
    resp = engine.query_code("variables", {}, {"functions": [".*mint.*", ".*burn.*"]})
    print("Variables(scope=mint/burn functions):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find variables from mint/burn function contexts
    if results:
        for result in results:
            assert result.get("type") == "variable"

        # Variables should be from mint/burn related contexts
        variable_names = {r.get("name") for r in results}
        # Common variables in mint/burn functions
        expected_vars = {"to", "amount", "totalSupply", "balances"}
        if expected_vars.intersection(variable_names):
            print(f"Found mint/burn variables: {expected_vars.intersection(variable_names)}")


def test_33_scope_restrict_by_file_patterns(engine):
    """
    Use Case 33: Scope: restrict by file patterns
    - Method: query_code
    - Params: { query_type: "contracts", scope: { files: ["composition_and_imports/.*"] } }
    - Expected: contracts defined in files matching pattern.
    """
    resp = engine.query_code("contracts", {}, {"files": ["composition_and_imports/.*"]})
    print("Contracts(scope=composition_and_imports):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 5  # Should find several contracts from composition_and_imports

    for result in results:
        assert result.get("type") == "contract"
        location = result.get("location", {})
        file_path = location.get("file", "")
        assert "composition_and_imports" in file_path, f"Contract {result.get('name')} not from composition_and_imports: {file_path}"

    # Should find specific contracts from that directory
    found_names = {r.get("name") for r in results}
    expected_contracts = {"SimpleContract", "ERC721WithImports", "BaseToken", "Ownable", "MultiInheritanceToken"}
    assert expected_contracts.intersection(found_names), f"Expected composition contracts not found"


def test_34_scope_restrict_by_directory_patterns(engine):
    """
    Use Case 34: Scope: restrict by directory patterns
    - Method: query_code
    - Params: { query_type: "contracts", scope: { directories: ["tests/fixtures/detailed_scenarios"] } }
    - Expected: contracts from the specified directory.
    """
    resp = engine.query_code("contracts", {}, {"directories": ["tests/fixtures/detailed_scenarios"]})
    print("Contracts(scope=detailed_scenarios):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 8  # Should find multiple contracts from detailed_scenarios

    for result in results:
        assert result.get("type") == "contract"
        location = result.get("location", {})
        file_path = location.get("file", "")
        assert "detailed_scenarios" in file_path, f"Contract {result.get('name')} not from detailed_scenarios: {file_path}"

    # Should find specific contracts from that directory
    found_names = {r.get("name") for r in results}
    expected_contracts = {"MathOperations", "LayerZeroApp", "RETHVault", "VulnerableNFTAuction"}
    assert expected_contracts.intersection(found_names), f"Expected detailed scenario contracts not found"


def test_35_scope_inheritance_tree_filter(engine):
    """
    Use Case 35: Scope: inheritance tree filter
    - Method: query_code
    - Params: { query_type: "functions", scope: { inheritance_tree: "ERC721" } }
    - Expected: functions whose contract inherits from the base named "ERC721" (if present).
    """
    resp = engine.query_code("functions", {}, {"inheritance_tree": "ERC721"})
    print("Functions(scope=inherits_ERC721):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])

    # Should find functions from contracts that inherit from ERC721
    if results:
        for result in results:
            assert result.get("type") == "function"

        # Should find functions from ERC721-inheriting contracts
        found_names = {r.get("name") for r in results}
        expected_erc721_functions = {"mint", "supportsInterface", "complexCalculation"}
        if expected_erc721_functions.intersection(found_names):
            print(f"Found ERC721 inheritance functions: {expected_erc721_functions.intersection(found_names)}")


def test_36_include_source_code(engine):
    """
    Use Case 36: Include: source code
    - Method: query_code
    - Params: { query_type: "functions", include: ["source"] }
    - Expected: each result has source_code string when available.
    """
    resp = engine.query_code("functions", {}, {}, ["source"])
    print("Functions(include=source) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many functions

    source_code_present = 0
    for result in results:
        assert result.get("type") == "function"
        assert "source_code" in result
        source_code = result.get("source_code")
        if source_code:
            source_code_present += 1
            assert isinstance(source_code, str)
            assert len(source_code) > 0

    print(f"Functions with source code: {source_code_present}/{len(results)}")
    # At least some functions should have source code
    assert source_code_present > 0


def test_37_include_ast_info(engine):
    """
    Use Case 37: Include: AST info
    - Method: query_code
    - Params: { query_type: "functions", include: ["ast"] }
    - Expected: each result has ast_info with node_type/node_id/start_line.
    """
    resp = engine.query_code("functions", {}, {}, ["ast"])
    print("Functions(include=ast) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many functions

    ast_info_present = 0
    for result in results:
        assert result.get("type") == "function"
        assert "ast_info" in result
        ast_info = result.get("ast_info")
        if ast_info:
            ast_info_present += 1
            assert isinstance(ast_info, dict)
            # Common AST info fields
            if "node_type" in ast_info:
                assert isinstance(ast_info["node_type"], str)

    print(f"Functions with AST info: {ast_info_present}/{len(results)}")


def test_38_include_calls(engine):
    """
    Use Case 38: Include: calls
    - Method: query_code
    - Params: { query_type: "functions", include: ["calls"] }
    - Expected: each result has calls as a list of call descriptors (name/type/position/arguments_count when derivable).
    """
    resp = engine.query_code("functions", {}, {}, ["calls"])
    print("Functions(include=calls) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many functions

    functions_with_calls = 0
    total_calls = 0
    for result in results:
        assert result.get("type") == "function"
        assert "calls" in result
        calls = result.get("calls", [])
        assert isinstance(calls, list)

        if calls:
            functions_with_calls += 1
            total_calls += len(calls)

            # Validate call structure
            for call in calls:
                if call:
                    assert isinstance(call, dict)
                    # Should have name or other identifying info

    print(f"Functions with calls: {functions_with_calls}/{len(results)}, Total calls: {total_calls}")
    # Should find many calls across functions
    assert functions_with_calls > 10


def test_39_include_callers(engine):
    """
    Use Case 39: Include: callers
    - Method: query_code
    - Params: { query_type: "functions", include: ["callers"] }
    - Expected: each result has callers listing functions that reference it (best-effort/source-based).
    """
    resp = engine.query_code("functions", {}, {}, ["callers"])
    print("Functions(include=callers) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many functions

    functions_with_callers = 0
    for result in results:
        assert result.get("type") == "function"
        assert "callers" in result
        callers = result.get("callers", [])
        assert isinstance(callers, list)

        if callers:
            functions_with_callers += 1
            # Validate caller structure
            for caller in callers:
                if caller:
                    assert isinstance(caller, dict)

    print(f"Functions with callers: {functions_with_callers}/{len(results)}")


def test_40_include_variables(engine):
    """
    Use Case 40: Include: variables
    - Method: query_code
    - Params: { query_type: "functions", include: ["variables"] }
    - Expected: each result has variables[] with name/access_type/variable_type when derivable.
    """
    resp = engine.query_code("functions", {}, {}, ["variables"])
    print("Functions(include=variables) count:", resp.get("query_info", {}).get("result_count", 0))
    assert resp.get("success") is True

    data = resp.get("data", {})
    results = data.get("results", [])
    assert len(results) > 20  # Should find many functions

    functions_with_variables = 0
    total_variables = 0
    for result in results:
        assert result.get("type") == "function"
        assert "variables" in result
        variables = result.get("variables", [])
        assert isinstance(variables, list)

        if variables:
            functions_with_variables += 1
            total_variables += len(variables)

            # Validate variable structure
            for variable in variables:
                if variable:
                    assert isinstance(variable, dict)
                    # Should have name or other identifying info

    print(f"Functions with variables: {functions_with_variables}/{len(results)}, Total variables: {total_variables}")
    # Should find many variables across functions
    assert functions_with_variables > 15