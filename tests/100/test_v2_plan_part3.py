def test_41_include_events(engine):
    resp = engine.query_code("functions", {}, {"files": [".*ERC721WithImports.sol"]}, ["events"])
    print("Functions(include=events, ERC721WithImports):", resp)
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "mint"), None)
    # Expect TokenMinted emission
    assert item and any(e.get("name") == "TokenMinted" for e in item.get("events", []))


def test_42_include_modifiers(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]}, ["modifiers"])
    print("Functions(include=modifiers, SimpleContract):", resp)
    assert resp.get("success") is True
    items = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}
    assert "onlyOwner" in [str(m) for m in items.get("setValue", {}).get("modifiers", [])]


def test_43_include_natspec(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]}, ["natspec"])
    print("Functions(include=natspec, SimpleContract):", resp)
    assert resp.get("success") is True
    # No NatSpec in fixture; expect empty/None fields
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "setValue"), None)
    assert item and isinstance(item.get("natspec"), dict)


def test_44_contracts_include_dependencies(engine):
    resp = engine.query_code("contracts", {}, {"files": [".*ERC721WithImports.sol"]}, ["dependencies"])
    print("Contracts(include=dependencies, ERC721WithImports):", resp)
    assert resp.get("success") is True
    item = next(iter(resp.get("data", {}).get("results", [])), {})
    deps = set(item.get("dependencies", []))
    assert any("openzeppelin" in d for d in deps) or any("SafeMath" in d for d in deps)


def test_45_contracts_include_inheritance(engine):
    resp = engine.query_code("contracts", {}, {"files": [".*ERC721WithImports.sol"]}, ["inheritance"])
    print("Contracts(include=inheritance, ERC721WithImports):", resp)
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "ERC721WithImports"), None)
    assert item and isinstance(item.get("inheritance_details"), dict)


def test_46_options_max_results(engine):
    resp = engine.query_code("functions", options={"max_results": 5})
    assert resp.get("success") is True
    assert len(resp.get("data", {}).get("results", [])) <= 5
    assert resp.get("query_info", {}).get("result_count") <= 5


def test_47_combined_filters_names_visibility_mutability(engine):
    resp = engine.query_code("functions", {
        "names": ".*balance.*",
        "visibility": ["public", "external"],
        "state_mutability": ["view", "pure"],
    })
    print("Functions(names=balance, vis=pub/ext, mut=view/pure):", resp)
    assert resp.get("success") is True


def test_48_combined_filters_modifiers_changes_state(engine):
    resp = engine.query_code("functions", {
        "modifiers": [".*Owner.*", ".*Admin.*"],
        "changes_state": True,
    })
    print("Functions(modifiers=Owner/Admin, changes_state):", resp)
    assert resp.get("success") is True


def test_49_combined_filters_external_calls_and_call_types(engine):
    resp = engine.query_code("functions", {
        "has_external_calls": True,
        "call_types": ["external"],
    })
    print("Functions(has_external_calls, call_types=external):", resp)
    assert resp.get("success") is True


def test_50_combined_filters_asset_transfers_low_level(engine):
    resp = engine.query_code("functions", {
        "has_asset_transfers": True,
        "low_level": True,
    })
    print("Functions(has_asset_transfers & low_level):", resp)
    assert resp.get("success") is True


def test_51_variables_types_and_scope(engine):
    resp = engine.query_code("variables", {
        "types": ["mapping*", "address"]
    }, {
        "contracts": [".*Pool.*", ".*Token.*"]
    })
    print("Variables(types & scope contracts=Pool/Token):", resp)
    assert resp.get("success") is True


def test_52_events_with_source_and_ast(engine):
    resp = engine.query_code("events", {}, {"files": [".*ERC721WithImports.sol"]}, ["source", "ast"])
    print("Events(include=source,ast in ERC721WithImports):", resp)
    assert resp.get("success") is True
    items = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}
    assert "TokenMinted" in items and "ast_info" in items["TokenMinted"] and "source_code" in items["TokenMinted"]


def test_53_modifiers_in_specific_files(engine):
    resp = engine.query_code("modifiers", {}, {"files": ["composition_and_imports/.*"]})
    print("Modifiers(files=composition_and_imports):", resp)
    assert resp.get("success") is True


def test_54_errors_in_directory(engine):
    resp = engine.query_code("errors", {}, {"directories": ["tests/fixtures/detailed_scenarios"]})
    print("Errors(dir=detailed_scenarios):", resp)
    assert resp.get("success") is True


def test_55_statements_loops(engine):
    resp = engine.query_code("statements", {"statement_types": ["for", "while", "do"]}, {"files": [".*ERC721WithImports.sol"]})
    print("Statements(loops in ERC721WithImports):", resp)
    assert resp.get("success") is True


def test_56_expressions_logical(engine):
    resp = engine.query_code("expressions", {"operators": ["&&", "||", "!"]}, {"files": [".*ERC721WithImports.sol"]})
    print("Expressions(logical in ERC721WithImports):", resp)
    assert resp.get("success") is True


def test_57_variables_name_patterns(engine):
    resp = engine.query_code("variables", {"names": [".*supply.*", ".*owner.*"]})
    print("Variables(names like supply/owner):", resp)
    assert resp.get("success") is True


def test_58_calls_filtered_by_names(engine):
    resp = engine.query_code("calls", {"names": ["transfer", "withdraw"]})
    print("Calls(names include transfer/withdraw):", resp)
    assert resp.get("success") is True


def test_59_contracts_deps_and_inheritance(engine):
    resp = engine.query_code("contracts", {}, {}, ["dependencies", "inheritance"])
    print("Contracts(include deps & inheritance):", resp)
    assert resp.get("success") is True


def test_60_functions_include_all(engine):
    resp = engine.query_code("functions", {}, {}, ["source", "ast", "calls", "variables", "events", "modifiers"])
    print("Functions(include all):", resp)
    assert resp.get("success") is True


