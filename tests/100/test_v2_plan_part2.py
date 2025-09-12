def test_21_state_variables_only(engine):
    resp = engine.query_code("variables", {"is_state_variable": True}, {"files": [".*SimpleContract.sol"]})
    print("Variables(state only, SimpleContract):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert names == {"value", "owner"}


def test_22_statements_by_type(engine):
    resp = engine.query_code("statements", {"statement_types": ["require"]}, {"files": [".*SimpleContract.sol"]})
    print("Statements(require, SimpleContract):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert len(results) > 0


def test_23_expressions_by_operators(engine):
    resp = engine.query_code("expressions", {"operators": ["+", "*", "=="]}, {"files": [".*ERC721WithImports.sol"]})
    print("Expressions(+,* ,== in ERC721WithImports):", resp)
    assert resp.get("success") is True
    assert len(resp.get("data", {}).get("results", [])) > 0


def test_24_functions_that_change_state(engine):
    resp = engine.query_code("functions", {"changes_state": True}, {"files": [".*SimpleContract.sol"]})
    print("Functions(change state, SimpleContract):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "setValue" in names


def test_25_functions_with_external_calls(engine):
    resp = engine.query_code("functions", {"has_external_calls": True})
    print("Functions(has external calls):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert {"transferWithCall", "vulnerableTransfer"}.intersection(names)


def test_26_functions_with_asset_transfers(engine):
    resp = engine.query_code("functions", {"has_asset_transfers": True})
    print("Functions(has asset transfers):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "mint" in names


def test_27_payable_functions(engine):
    resp = engine.query_code("functions", {"is_payable": True})
    print("Functions(payable):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert {"deposit", "mint"}.intersection(names)


def test_28_calls_filtered_by_call_types(engine):
    resp = engine.query_code("functions", {"call_types": ["transfer", "balanceOf"]})
    print("Functions(call_types contain transfer|balanceOf):", resp)
    assert resp.get("success") is True
    # Expect RETHVault.deposit (calls rethToken.transfer)
    names = {(r.get("location", {}) or {}).get("contract", "") + "." + r.get("name", "") for r in resp.get("data", {}).get("results", [])}
    assert any(n.endswith("RETHVault.deposit") for n in names)


def test_29_low_level_calls(engine):
    resp = engine.query_code("functions", {"low_level": True})
    print("Functions(low_level):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "transferWithCall" in names


def test_30_access_patterns(engine):
    resp = engine.query_code("functions", {"access_patterns": ["msg.sender", "balanceOf("]}, {"files": [".*ERC721WithImports.sol"]})
    print("Functions(access_patterns in ERC721WithImports):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "internalOnlyFunction" in names or "vulnerableTransfer" in names


def test_31_scope_contracts(engine):
    resp = engine.query_code("functions", {}, {"contracts": [".*MultiInheritanceToken"]})
    print("Functions(scope contracts=MultiInheritanceToken):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert {"mint", "transferWithCall"}.issubset(names)


def test_32_scope_functions(engine):
    resp = engine.query_code("variables", {}, {"functions": [".*mint.*"]})
    print("Variables(scope functions=.*mint.*):", resp)
    assert resp.get("success") is True
    # Variables used in mint functions include balances/price/nextTokenId
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert {"balances", "price", "nextTokenId"}.intersection(names)


def test_33_scope_files(engine):
    resp = engine.query_code("contracts", {}, {"files": ["composition_and_imports/.*"]})
    print("Contracts(files=composition_and_imports):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Subset check
    assert {"MultiInheritanceToken", "ERC721WithImports"}.issubset(names)


def test_34_scope_directories(engine):
    resp = engine.query_code("contracts", {}, {"directories": ["tests/fixtures/detailed_scenarios"]})
    print("Contracts(dir=detailed_scenarios):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert {"MathOperations", "LayerZeroApp", "MultiInheritChild", "RETHVault"}.issubset(names)


def test_35_scope_inheritance_tree(engine):
    resp = engine.query_code("functions", {}, {"inheritance_tree": "ERC721"})
    print("Functions(inheritance_tree=ERC721):", resp)
    assert resp.get("success") is True
    # Expect functions from ERC721WithImports
    assert any((r.get("location", {}) or {}).get("contract") == "ERC721WithImports" for r in resp.get("data", {}).get("results", []))


def test_36_include_source(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]}, ["source"])
    print("Functions(include=source, SimpleContract):", resp)
    assert resp.get("success") is True
    items = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}
    assert "value =" in (items.get("setValue", {}).get("source_code") or "")


def test_37_include_ast(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]}, ["ast"])
    print("Functions(include=ast, SimpleContract):", resp)
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "setValue"), None)
    assert item and "ast_info" in item


def test_38_include_calls(engine):
    resp = engine.query_code("functions", {}, {"files": [".*ERC721WithImports.sol"]}, ["calls"])
    print("Functions(include=calls, ERC721WithImports):", resp)
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "mint"), None)
    assert item and isinstance(item.get("calls"), list) and len(item.get("calls")) > 0


def test_39_include_callers(engine):
    resp = engine.query_code("functions", {}, {}, ["callers"])
    print("Functions(include=callers):", resp)
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
    print("Functions(include=variables, ERC721WithImports):", resp)
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "internalOnlyFunction"), None)
    assert item and any(v.get("name") == "balances" for v in item.get("variables", []))


