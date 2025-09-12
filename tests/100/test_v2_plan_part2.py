import json

def test_21_state_variables_only(engine):
    resp = engine.query_code("variables", {"is_state_variable": True}, {"files": [".*SimpleContract.sol"]})
    print("Variables(state only, SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name") for r in results}
    assert names == {"value", "owner"}

    # Validate detailed state variable properties
    value_var = next((r for r in results if r.get("name") == "value"), None)
    owner_var = next((r for r in results if r.get("name") == "owner"), None)

    assert value_var is not None
    assert value_var.get("is_state_variable") is True
    assert str(value_var.get("type_name")).lower() == "uint256"
    assert value_var.get("location", {}).get("line") == 8

    assert owner_var is not None
    assert owner_var.get("is_state_variable") is True
    assert str(owner_var.get("type_name")).lower() == "address"
    assert owner_var.get("location", {}).get("line") == 9


def test_22_statements_by_type(engine):
    resp = engine.query_code("statements", {"statement_types": ["require"]}, {"files": [".*SimpleContract.sol"]})
    print("Statements(require, SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert len(results) > 0

    # Validate the require statement found in SimpleContract.sol
    for stmt in results:
        assert stmt.get("type") == "statement"
        location = stmt.get("location", {})

        # Should be from SimpleContract.sol
        file_path = str(location.get("file", ""))
        assert file_path.endswith("SimpleContract.sol")

        # Should be the require statement at line 12 (in onlyOwner modifier)
        assert location.get("line") == 12
        assert location.get("column") == 8  # Column position of require

        # Note: For statements, name and contract may be None as they represent code fragments
        # But we can validate the location is correct


def test_23_expressions_by_operators(engine):
    resp = engine.query_code("expressions", {"operators": ["+", "*", "=="]}, {"files": [".*ERC721WithImports.sol"]})
    print("Expressions(+,* ,== in ERC721WithImports):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert len(results) > 0

    # Validate expressions found in ERC721WithImports.sol
    for expr in results:
        assert expr.get("type") == "expression"
        location = expr.get("location", {})

        # Should be from ERC721WithImports.sol
        file_path = str(location.get("file", ""))
        assert file_path.endswith("ERC721WithImports.sol")

        # Should have valid location information
        assert isinstance(location.get("line"), int)
        assert isinstance(location.get("column"), int)

        # Note: For expressions, name and contract may be None as they represent code fragments


def test_24_functions_that_change_state(engine):
    resp = engine.query_code("functions", {"changes_state": True}, {"files": [".*SimpleContract.sol"]})
    print("Functions(change state, SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name") for r in results}
    assert "setValue" in names

    # Validate setValue function as a state-changing function
    set_value_func = next((r for r in results if r.get("name") == "setValue"), None)
    assert set_value_func is not None
    assert set_value_func.get("type") == "function"
    assert str(set_value_func.get("visibility")).lower() == "public"
    assert str(set_value_func.get("state_mutability")).lower() == "nonpayable"
    assert set_value_func.get("location", {}).get("line") == 32
    assert str(set_value_func.get("location", {}).get("file")).endswith("SimpleContract.sol")


def test_25_functions_with_external_calls(engine):
    resp = engine.query_code("functions", {"has_external_calls": True})
    print("Functions(has external calls):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name") for r in results}
    assert {"transferWithCall", "vulnerableTransfer"}.intersection(names)

    # Validate transferWithCall function has external calls
    if any(r.get("name") == "transferWithCall" for r in results):
        transfer_func = next((r for r in results if r.get("name") == "transferWithCall"), None)
        assert transfer_func is not None
        assert transfer_func.get("type") == "function"
        assert str(transfer_func.get("visibility")).lower() in ["external", "public"]
        # Should be from MultipleInheritance.sol
        assert str(transfer_func.get("location", {}).get("file")).endswith("MultipleInheritance.sol")


def test_26_functions_with_asset_transfers(engine):
    resp = engine.query_code("functions", {"has_asset_transfers": True})
    print("Functions(has asset transfers):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "mint" in names


def test_27_payable_functions(engine):
    resp = engine.query_code("functions", {"is_payable": True})
    print("Functions(payable):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name") for r in results}
    assert {"deposit", "mint"}.intersection(names)

    # Validate payable functions
    payable_functions = {r.get("name"): r for r in results}

    if "deposit" in payable_functions:
        deposit_func = payable_functions["deposit"]
        assert str(deposit_func.get("state_mutability")).lower() == "payable"
        assert str(deposit_func.get("location", {}).get("file")).endswith("SimpleContract.sol")
        assert deposit_func.get("location", {}).get("line") == 37

    if "mint" in payable_functions:
        mint_func = payable_functions["mint"]
        assert str(mint_func.get("state_mutability")).lower() == "payable"
        # mint should be from ERC721WithImports.sol
        assert str(mint_func.get("location", {}).get("file")).endswith("ERC721WithImports.sol")


def test_28_calls_filtered_by_call_types(engine):
    resp = engine.query_code("functions", {"call_types": ["transfer", "balanceOf"]})
    print("Functions(call_types contain transfer|balanceOf):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    # Expect RETHVault.deposit (calls rethToken.transfer)
    names = {(r.get("location", {}) or {}).get("contract", "") + "." + r.get("name", "") for r in resp.get("data", {}).get("results", [])}
    assert any(n.endswith("RETHVault.deposit") for n in names)


def test_29_low_level_calls(engine):
    resp = engine.query_code("functions", {"low_level": True})
    print("Functions(low_level):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "transferWithCall" in names


def test_30_access_patterns(engine):
    resp = engine.query_code("functions", {"access_patterns": ["msg.sender", "balanceOf("]}, {"files": [".*ERC721WithImports.sol"]})
    print("Functions(access_patterns in ERC721WithImports):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "internalOnlyFunction" in names or "vulnerableTransfer" in names


def test_31_scope_contracts(engine):
    resp = engine.query_code("functions", {}, {"contracts": [".*MultiInheritanceToken"]})
    print("Functions(scope contracts=MultiInheritanceToken):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name") for r in results}
    assert {"mint", "transferWithCall"}.issubset(names)

    # Validate functions are specifically from MultiInheritanceToken contract
    for result in results:
        # All results should be from MultipleInheritance.sol file
        assert str(result.get("location", {}).get("file")).endswith("MultipleInheritance.sol")
        # Contract context should be MultiInheritanceToken (where available)
        location_contract = result.get("location", {}).get("contract")
        if location_contract:  # Some elements might not have contract populated
            assert location_contract == "MultiInheritanceToken"


def test_32_scope_functions(engine):
    resp = engine.query_code("variables", {}, {"functions": [".*mint.*"]})
    print("Variables(scope functions=.*mint.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    # Variables used in mint functions include balances/price/nextTokenId
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name") for r in results}
    assert {"balances", "price", "nextTokenId"}.intersection(names)

    # Validate specific variables used in mint functions
    var_dict = {r.get("name"): r for r in results}

    if "price" in var_dict:
        price_var = var_dict["price"]
        assert str(price_var.get("type_name")).lower() == "uint256"
        assert str(price_var.get("location", {}).get("file")).endswith("ERC721WithImports.sol")

    if "nextTokenId" in var_dict:
        next_token_var = var_dict["nextTokenId"]
        assert str(next_token_var.get("type_name")).lower() == "uint256"
        assert str(next_token_var.get("location", {}).get("file")).endswith("ERC721WithImports.sol")


def test_33_scope_files(engine):
    resp = engine.query_code("contracts", {}, {"files": ["composition_and_imports/.*"]})
    print("Contracts(files=composition_and_imports):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Subset check
    assert {"MultiInheritanceToken", "ERC721WithImports"}.issubset(names)


def test_34_scope_directories(engine):
    resp = engine.query_code("contracts", {}, {"directories": ["tests/fixtures/detailed_scenarios"]})
    print("Contracts(dir=detailed_scenarios):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert {"MathOperations", "LayerZeroApp", "MultiInheritChild", "RETHVault"}.issubset(names)


def test_35_scope_inheritance_tree(engine):
    resp = engine.query_code("functions", {}, {"inheritance_tree": "ERC721"})
    print("Functions(inheritance_tree=ERC721):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    # Expect functions from ERC721WithImports
    assert any((r.get("location", {}) or {}).get("contract") == "ERC721WithImports" for r in resp.get("data", {}).get("results", []))


def test_36_include_source(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]}, ["source"])
    print("Functions(include=source, SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    items = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}
    assert "value =" in (items.get("setValue", {}).get("source_code") or "")


def test_37_include_ast(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]}, ["ast"])
    print("Functions(include=ast, SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "setValue"), None)
    assert item and "ast_info" in item


def test_38_include_calls(engine):
    resp = engine.query_code("functions", {}, {"files": [".*ERC721WithImports.sol"]}, ["calls"])
    print("Functions(include=calls, ERC721WithImports):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "mint"), None)
    assert item and isinstance(item.get("calls"), list) and len(item.get("calls")) > 0


def test_39_include_callers(engine):
    resp = engine.query_code("functions", {}, {}, ["callers"])
    print("Functions(include=callers):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    # At least one mint is called by lzReceive (in MultiInheritanceToken)
    for r in resp.get("data", {}).get("results", []):
        if r.get("name") == "mint":
            callers = [c.get("name") for c in r.get("callers", [])]
            if callers:
                assert "lzReceive" in callers
                break


def test_40_include_variables(engine):
    resp = engine.query_code("functions", {}, {"files": [".*ERC721WithImports.sol"]}, ["variables"])
    print("Functions(include=variables, ERC721WithImports):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "internalOnlyFunction"), None)
    assert item and any(v.get("name") == "balances" for v in item.get("variables", []))


