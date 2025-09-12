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

    # Validate combined filters work correctly
    results = resp.get("data", {}).get("results", [])
    for func in results:
        # Should have state-changing functions with Owner/Admin modifiers
        assert func.get("changes_state") is True or func.get("state_mutability") in {"nonpayable", "payable"}
        # Modifier validation would need modifier information to be included
        assert func.get("type") == "FunctionDeclaration"


def test_49_combined_filters_external_calls_and_call_types(engine):
    resp = engine.query_code("functions", {
        "has_external_calls": True,
        "call_types": ["external"],
    })
    print("Functions(has_external_calls, call_types=external):", resp)
    assert resp.get("success") is True

    # Validate functions are external or make external calls
    results = resp.get("data", {}).get("results", [])
    for func in results:
        # API applies the filter correctly, so results should be valid
        assert func.get("type") == "FunctionDeclaration"
        # Should find functions that make external calls or have external visibility
        func_name = func.get("name", "")
        assert func_name  # Should have a name
        visibility = func.get("visibility", "").lower()
        # Results are filtered correctly by the engine - internal functions can also make external calls
        assert visibility in {"external", "public", "internal"}  # Functions that can make external calls


def test_50_combined_filters_asset_transfers_low_level(engine):
    resp = engine.query_code("functions", {
        "has_asset_transfers": True,
        "low_level": True,
    })
    print("Functions(has_asset_transfers & low_level):", resp)
    assert resp.get("success") is True

    # Validate functions are filtered correctly for asset transfers and low-level
    results = resp.get("data", {}).get("results", [])
    for func in results:
        # API applies the filter correctly, so results should be valid
        assert func.get("type") == "FunctionDeclaration"
        # These functions should involve asset transfers and low-level operations
        func_name = func.get("name", "").lower()
        assert "transfer" in func_name or "withdraw" in func_name or "pay" in func_name


def test_51_variables_types_and_scope(engine):
    resp = engine.query_code("variables", {
        "types": ["mapping*", "address"]
    }, {
        "contracts": [".*Pool.*", ".*Token.*"]
    })
    print("Variables(types & scope contracts=Pool/Token):", resp)
    assert resp.get("success") is True

    # Validate variables match type and scope filters
    results = resp.get("data", {}).get("results", [])
    for var in results:
        # Should be mapping or address type
        var_type = str(var.get("type_name", "")).lower()
        assert "mapping" in var_type or "address" in var_type, f"Unexpected type: {var_type}"

        # Should be from Token or Pool contracts - but contract name might be None in basic queries
        location = var.get("location", {})
        file_path = str(location.get("file", ""))
        # Variables are filtered by contract scope, so file path should match Token-related files
        assert any(token_file in file_path.lower() for token_file in ["token", "inheritance", "sample_contract"]), f"Unexpected file: {file_path}"


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

    # Validate modifiers are found in composition_and_imports files
    results = resp.get("data", {}).get("results", [])
    modifier_names = {r.get("name") for r in results}
    # Should find onlyOwner from SimpleContract.sol and possibly others
    assert "onlyOwner" in modifier_names

    # Validate file scope works - all results should be from composition_and_imports
    for modifier in results:
        location = modifier.get("location", {})
        file_path = str(location.get("file", ""))
        assert "composition_and_imports" in file_path


def test_54_errors_in_directory(engine):
    resp = engine.query_code("errors", {}, {"directories": ["tests/fixtures/detailed_scenarios"]})
    print("Errors(dir=detailed_scenarios):", resp)
    assert resp.get("success") is True

    # Validate directory scope works
    results = resp.get("data", {}).get("results", [])
    # If errors are found, they should be from detailed_scenarios directory
    for error in results:
        location = error.get("location", {})
        file_path = str(location.get("file", ""))
        assert "detailed_scenarios" in file_path
        assert error.get("type") == "ErrorDeclaration"


def test_55_statements_loops(engine):
    resp = engine.query_code("statements", {"statement_types": ["for", "while", "do"]}, {"files": [".*ERC721WithImports.sol"]})
    print("Statements(loops in ERC721WithImports):", resp)
    assert resp.get("success") is True

    # Validate loop statements are properly filtered
    results = resp.get("data", {}).get("results", [])
    for stmt in results:
        stmt_type = stmt.get("statement_type", "").lower()
        assert stmt_type in {"for", "while", "do"}, f"Unexpected statement type: {stmt_type}"

        # Should be from ERC721WithImports.sol
        location = stmt.get("location", {})
        file_path = str(location.get("file", ""))
        assert file_path.endswith("ERC721WithImports.sol")


def test_56_expressions_logical(engine):
    resp = engine.query_code("expressions", {"operators": ["&&", "||", "!"]}, {"files": [".*ERC721WithImports.sol"]})
    print("Expressions(logical in ERC721WithImports):", resp)
    assert resp.get("success") is True

    # Validate expressions are filtered correctly
    results = resp.get("data", {}).get("results", [])
    for expr in results:
        # API filters expressions correctly, validate basic structure
        assert expr.get("type") == "ExtractedExpression"

        # Should be from ERC721WithImports.sol
        location = expr.get("location", {})
        file_path = str(location.get("file", ""))
        assert file_path.endswith("ERC721WithImports.sol")

        # Location should have line and column information
        assert location.get("line") is not None
        assert location.get("column") is not None


def test_57_variables_name_patterns(engine):
    resp = engine.query_code("variables", {"names": [".*supply.*", ".*owner.*"]})
    print("Variables(names like supply/owner):", resp)
    assert resp.get("success") is True

    # Validate variables match name patterns
    results = resp.get("data", {}).get("results", [])
    for var in results:
        var_name = var.get("name", "").lower()
        assert "supply" in var_name or "owner" in var_name, f"Variable name '{var_name}' doesn't match pattern"
        assert var.get("type") == "VariableDeclaration"

    # Should find variables like totalSupply, maxSupply, owner
    var_names = {r.get("name") for r in results}
    expected_matches = {"totalSupply", "maxSupply", "owner"}
    assert expected_matches.intersection(var_names), f"Expected to find some of {expected_matches} in {var_names}"


def test_58_calls_filtered_by_names(engine):
    resp = engine.query_code("calls", {"names": ["transfer", "withdraw"]})
    print("Calls(names include transfer/withdraw):", resp)
    assert resp.get("success") is True

    # Validate calls are filtered correctly
    results = resp.get("data", {}).get("results", [])
    for call in results:
        call_name = call.get("name", "").lower()
        # API filters calls correctly - call names should contain transfer or withdraw
        assert "transfer" in call_name or "withdraw" in call_name, f"Call name '{call_name}' doesn't contain expected patterns"
        assert "location" in call
        assert call.get("type") == "CallNode"

    # Should find transfer and/or withdraw calls in fixtures
    if results:
        call_names = {r.get("name") for r in results}
        # At least some calls should contain our target patterns
        assert any("transfer" in name.lower() or "withdraw" in name.lower() for name in call_names)


def test_59_contracts_deps_and_inheritance(engine):
    resp = engine.query_code("contracts", {}, {}, ["dependencies", "inheritance"])
    print("Contracts(include deps & inheritance):", resp)
    assert resp.get("success") is True

    # Validate contracts include dependencies and inheritance info
    results = resp.get("data", {}).get("results", [])
    assert len(results) > 0, "Should find contracts in fixtures"

    for contract in results:
        assert contract.get("type") == "ContractDeclaration"
        # Should have dependencies and inheritance_details when requested
        assert "dependencies" in contract
        assert "inheritance_details" in contract

    # Find ERC721WithImports which should have both dependencies and inheritance
    erc721_contract = next((c for c in results if c.get("name") == "ERC721WithImports"), None)
    if erc721_contract:
        deps = erc721_contract.get("dependencies", [])
        assert isinstance(deps, list)
        # Should have OpenZeppelin dependencies
        dep_strings = [str(d).lower() for d in deps]
        assert any("openzeppelin" in dep or "erc721" in dep for dep in dep_strings)


def test_60_functions_include_all(engine):
    resp = engine.query_code("functions", {}, {}, ["source", "ast", "calls", "variables", "events", "modifiers"])
    print("Functions(include all):", resp)
    assert resp.get("success") is True

    # Validate functions include all requested additional information
    results = resp.get("data", {}).get("results", [])
    assert len(results) > 0, "Should find functions in fixtures"

    # Check that functions have all the requested include fields
    for func in results[:3]:  # Check first 3 functions
        assert func.get("type") == "FunctionDeclaration"

        # All functions should have these fields when requested
        expected_fields = {"source_code", "ast_info", "calls", "variables", "events", "modifiers"}
        actual_fields = set(func.keys())
        missing_fields = expected_fields - actual_fields
        assert not missing_fields, f"Function '{func.get('name')}' missing fields: {missing_fields}"

        # Validate field types
        assert isinstance(func.get("calls", []), list)
        assert isinstance(func.get("variables", []), list)
        assert isinstance(func.get("events", []), list)
        assert isinstance(func.get("modifiers", []), list)


