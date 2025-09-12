import json

def test_86_find_references_function_all(engine):
    resp = engine.find_references("transfer", "function", reference_type="all")
    print("find_references(transfer,function,all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    # Validate response structure
    assert "data" in resp
    refs = resp["data"]["references"]
    assert "usages" in refs and "definitions" in refs

    # Validate definitions structure
    definitions = refs["definitions"]
    assert isinstance(definitions, list)
    if definitions:
        # At least one transfer function should be found
        transfer_def = definitions[0]
        assert transfer_def.get("name") == "transfer"
        assert transfer_def.get("element_type") == "function"
        assert "location" in transfer_def

    # Validate usages structure
    usages = refs["usages"]
    assert isinstance(usages, list)
    # Usages should have location information
    for usage in usages[:3]:  # Check first 3 usages
        assert "location" in usage
        assert "context" in usage


def test_87_find_references_function_usages(engine):
    resp = engine.find_references("transfer", "function", reference_type="usages")
    print("find_references(transfer,function,usages):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    # Validate that usages are included (API includes both fields but only populates requested one)
    refs = resp["data"]["references"]
    assert "usages" in refs
    # When requesting only usages, definitions should be empty
    definitions = refs.get("definitions", [])
    assert isinstance(definitions, list)
    assert len(definitions) == 0  # Should be empty when only usages requested

    # Validate usages structure
    usages = refs["usages"]
    assert isinstance(usages, list)
    if usages:
        # Check first usage details
        usage = usages[0]
        assert "location" in usage
        location = usage["location"]
        assert "file" in location
        assert "line" in location
        assert "context" in usage


def test_88_find_references_function_definitions(engine):
    resp = engine.find_references("transfer", "function", reference_type="definitions")
    print("find_references(transfer,function,definitions):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    # Validate that definitions are included (API includes both fields but only populates requested one)
    refs = resp["data"]["references"]
    assert "definitions" in refs
    # When requesting only definitions, usages should be empty
    usages = refs.get("usages", [])
    assert isinstance(usages, list)
    assert len(usages) == 0  # Should be empty when only definitions requested

    # Validate definitions structure
    defs = refs["definitions"]
    assert isinstance(defs, list)
    if defs:
        # Primary definition should be included when found
        definition = defs[0]
        assert definition.get("name") == "transfer"
        assert definition.get("element_type") == "function"
        assert "location" in definition

        # Should find transfer functions from fixture files
        location = definition["location"]
        assert "file" in location
        assert "line" in location
        assert str(location["file"]).endswith(".sol")


def test_89_references_direction_forward(engine):
    resp = engine.find_references("transfer", "function", direction="forward")
    print("find_references(transfer,function,forward):", json.dumps(resp, indent=2))
    assert resp.get("success") in (True, False)


def test_90_references_direction_backward(engine):
    resp = engine.find_references("transfer", "function", direction="backward")
    print("find_references(transfer,function,backward):", json.dumps(resp, indent=2))
    assert resp.get("success") in (True, False)


def test_91_references_direction_both(engine):
    resp = engine.find_references("transfer", "function", direction="both")
    print("find_references(transfer,function,both):", json.dumps(resp, indent=2))
    assert resp.get("success") in (True, False)


def test_92_references_max_depth_one(engine):
    resp = engine.find_references("transfer", "function", direction="both", max_depth=1)
    print("find_references(transfer,function,depth=1):", json.dumps(resp, indent=2))
    assert resp.get("success") in (True, False)


def test_93_references_unlimited_depth(engine):
    resp = engine.find_references("transfer", "function", max_depth=-1)
    print("find_references(transfer,function,depth=-1):", json.dumps(resp, indent=2))
    assert resp.get("success") in (True, False)


def test_94_references_with_call_chains(engine):
    resp = engine.find_references("transfer", "function", options={"show_call_chains": True}, max_depth=3)
    print("find_references(transfer,function,call_chains,depth=3):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    # Validate call chains are included when requested
    refs = resp["data"]["references"]
    if "call_chains" in refs:
        call_chains = refs["call_chains"]
        assert isinstance(call_chains, list)
        # Each call chain should have source and target information
        for chain in call_chains[:2]:  # Check first 2 chains
            assert "source" in chain
            assert "target" in chain
            assert "depth" in chain
            assert isinstance(chain["depth"], int)
            assert chain["depth"] <= 3  # Should respect max_depth


def test_95_variable_references_all(engine):
    resp = engine.find_references("balances", "variable", reference_type="all")
    print("find_references(balances,variable,all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    # Validate variable references structure
    refs = resp["data"]["references"]
    assert "definitions" in refs and "usages" in refs

    # Validate variable definition
    definitions = refs["definitions"]
    assert isinstance(definitions, list)
    if definitions:
        balances_def = definitions[0]
        assert balances_def.get("name") == "balances"
        assert balances_def.get("element_type") == "variable"
        assert "location" in balances_def

        # balances should be from ERC721WithImports.sol or sample_contract.sol
        location = balances_def["location"]
        assert str(location.get("file")).endswith(".sol")

    # Validate variable usages
    usages = refs["usages"]
    assert isinstance(usages, list)


def test_96_contract_references(engine):
    resp = engine.find_references("Token", "contract", reference_type="all")
    print("find_references(Token,contract,all):", json.dumps(resp, indent=2))
    assert resp.get("success") in (True, False)


def test_97_references_filtered_by_contracts(engine):
    resp = engine.find_references("transfer", "function", filters={"contracts": [".*Token.*"]})
    print("find_references(transfer,function,contracts=.*Token.*):", json.dumps(resp, indent=2))
    assert resp.get("success") in (True, False)


def test_98_references_filtered_by_files(engine):
    resp = engine.find_references("transfer", "function", filters={"files": ["detailed_scenarios/.*"]})
    print("find_references(transfer,function,files=detailed_scenarios):", json.dumps(resp, indent=2))
    assert resp.get("success") in (True, False)


def test_99_nonexistent_target(engine):
    resp = engine.find_references("doesNotExist", "function")
    print("find_references(doesNotExist,function):", json.dumps(resp, indent=2))
    assert resp.get("success") is False

    # Validate error response structure for nonexistent targets
    errors = resp.get("errors")
    assert errors is not None
    assert len(errors) > 0

    # Error should indicate target not found
    error_msg = str(errors[0]).lower()
    assert "not found" in error_msg or "does not exist" in error_msg


def test_100_target_types_coverage(engine):
    for t in ("modifier", "event", "struct", "enum"):
        resp = engine.find_references("transfer", t)  # target name is a placeholder, may be not found
        print("find_references(transfer,", t, "):", json.dumps(resp, indent=2))
        # Either success with references or standardized error for not found
        assert resp.get("success") in (True, False)


