def test_41_include_events(engine):
    resp = engine.query_code("functions", {}, {"files": [".*ERC721WithImports.sol"]}, ["events"])
    print("Functions(include=events, ERC721WithImports):", resp)
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "mint"), None)
    assert item is not None
    
    # Validate that events are included and TokenMinted is present
    events = item.get("events", [])
    assert isinstance(events, list)
    token_minted_event = next((e for e in events if e.get("name") == "TokenMinted"), None)
    assert token_minted_event is not None
    
    # Validate TokenMinted event details (events in functions are simpler objects)
    assert token_minted_event.get("name") == "TokenMinted"
    assert "position" in token_minted_event  # Position where event is emitted
    assert isinstance(token_minted_event.get("position"), int)


def test_42_include_modifiers(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]}, ["modifiers"])
    print("Functions(include=modifiers, SimpleContract):", resp)
    assert resp.get("success") is True
    items = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}
    
    # Validate setValue function has onlyOwner modifier
    set_value_func = items.get("setValue")
    assert set_value_func is not None
    modifiers = set_value_func.get("modifiers", [])
    assert isinstance(modifiers, list)
    
    # Check if onlyOwner modifier is present (as string or object)
    modifier_names = [str(m) if isinstance(m, str) else m.get("name", str(m)) for m in modifiers]
    assert "onlyOwner" in modifier_names
    
    # Validate modifier details if available as objects
    only_owner_mod = next((m for m in modifiers if (isinstance(m, dict) and m.get("name") == "onlyOwner") or str(m) == "onlyOwner"), None)
    assert only_owner_mod is not None


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
    results = resp.get("data", {}).get("results", [])
    assert len(results) > 0
    
    # Find ERC721WithImports contract
    erc721_contract = next((r for r in results if r.get("name") == "ERC721WithImports"), None)
    assert erc721_contract is not None
    
    # Validate dependencies are included
    deps = erc721_contract.get("dependencies", [])
    assert isinstance(deps, list)
    
    # ERC721WithImports.sol imports OpenZeppelin contracts and SafeMath
    dep_strings = [str(d) for d in deps]
    expected_deps = {"openzeppelin", "safemath", "ierc721", "reentrancyguard"}
    found_deps = {d.lower() for d in dep_strings}
    
    # At least one of these dependencies should be found
    assert any(exp_dep in "".join(found_deps).lower() for exp_dep in expected_deps)


def test_45_contracts_include_inheritance(engine):
    resp = engine.query_code("contracts", {}, {"files": [".*ERC721WithImports.sol"]}, ["inheritance"])
    print("Contracts(include=inheritance, ERC721WithImports):", resp)
    assert resp.get("success") is True
    item = next((r for r in resp.get("data", {}).get("results", []) if r.get("name") == "ERC721WithImports"), None)
    assert item is not None
    
    # Validate inheritance details are included
    inheritance_details = item.get("inheritance_details")
    assert isinstance(inheritance_details, dict)
    
    # ERC721WithImports should inherit from ERC721, ReentrancyGuard
    base_contracts = inheritance_details.get("base_contracts", [])
    if base_contracts:
        assert isinstance(base_contracts, list)
        base_names = [str(bc.get("name") if isinstance(bc, dict) else bc) for bc in base_contracts]
        expected_bases = {"ERC721", "ReentrancyGuard"}
        found_bases = set(base_names)
        # At least one expected base should be found
        assert any(base in found_bases for base in expected_bases)


def test_46_options_max_results(engine):
    resp = engine.query_code("functions", options={"max_results": 5})
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert len(results) <= 5
    
    # Validate query_info contains result_count
    query_info = resp.get("query_info", {})
    assert isinstance(query_info, dict)
    result_count = query_info.get("result_count")
    if result_count is not None:
        assert result_count <= 5
        assert result_count == len(results)


def test_47_combined_filters_names_visibility_mutability(engine):
    resp = engine.query_code("functions", {
        "names": ".*balance.*",
        "visibility": ["public", "external"],
        "state_mutability": ["view", "pure"],
    })
    print("Functions(names=balance, vis=pub/ext, mut=view/pure):", resp)
    assert resp.get("success") is True
    
    # Validate that all returned functions match the combined filters
    results = resp.get("data", {}).get("results", [])
    for func in results:
        # Function name should contain "balance"
        assert "balance" in func.get("name", "").lower()
        
        # Visibility should be public or external
        visibility = str(func.get("visibility", "")).lower()
        assert visibility in {"public", "external"}
        
        # State mutability should be view or pure
        state_mutability = str(func.get("state_mutability", "")).lower()
        assert state_mutability in {"view", "pure"}


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
    results = resp.get("data", {}).get("results", [])
    items = {r.get("name"): r for r in results}
    
    # Validate TokenMinted event is present with source and ast info
    assert "TokenMinted" in items
    token_minted = items["TokenMinted"]
    
    # Validate ast_info is included
    assert "ast_info" in token_minted
    ast_info = token_minted["ast_info"]
    assert isinstance(ast_info, dict)
    
    # Validate source_code is included
    assert "source_code" in token_minted
    source_code = token_minted["source_code"]
    assert isinstance(source_code, str)
    assert len(source_code) > 0
    
    # Validate PriceUpdated event is also present
    assert "PriceUpdated" in items
    price_updated = items["PriceUpdated"]
    assert "ast_info" in price_updated
    assert "source_code" in price_updated


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


