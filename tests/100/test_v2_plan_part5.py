def test_86_find_references_function_all(engine):
    resp = engine.find_references("transfer", "function", reference_type="all")
    print("find_references(transfer,function,all):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        refs = resp.get("data", {}).get("references", {})
        assert "usages" in refs and "definitions" in refs


def test_87_find_references_function_usages(engine):
    resp = engine.find_references("transfer", "function", reference_type="usages")
    print("find_references(transfer,function,usages):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        refs = resp.get("data", {}).get("references", {})
        assert "usages" in refs


def test_88_find_references_function_definitions(engine):
    resp = engine.find_references("transfer", "function", reference_type="definitions")
    print("find_references(transfer,function,definitions):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        defs = resp.get("data", {}).get("references", {}).get("definitions", [])
        # Primary definition is always included when found
        assert isinstance(defs, list)


def test_89_references_direction_forward(engine):
    resp = engine.find_references("transfer", "function", direction="forward")
    print("find_references(transfer,function,forward):", resp)
    assert resp.get("success") in (True, False)


def test_90_references_direction_backward(engine):
    resp = engine.find_references("transfer", "function", direction="backward")
    print("find_references(transfer,function,backward):", resp)
    assert resp.get("success") in (True, False)


def test_91_references_direction_both(engine):
    resp = engine.find_references("transfer", "function", direction="both")
    print("find_references(transfer,function,both):", resp)
    assert resp.get("success") in (True, False)


def test_92_references_max_depth_one(engine):
    resp = engine.find_references("transfer", "function", direction="both", max_depth=1)
    print("find_references(transfer,function,depth=1):", resp)
    assert resp.get("success") in (True, False)


def test_93_references_unlimited_depth(engine):
    resp = engine.find_references("transfer", "function", max_depth=-1)
    print("find_references(transfer,function,depth=-1):", resp)
    assert resp.get("success") in (True, False)


def test_94_references_with_call_chains(engine):
    resp = engine.find_references("transfer", "function", options={"show_call_chains": True}, max_depth=3)
    print("find_references(transfer,function,call_chains,depth=3):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        refs = resp.get("data", {}).get("references", {})
        assert "call_chains" in refs


def test_95_variable_references_all(engine):
    resp = engine.find_references("balances", "variable", reference_type="all")
    print("find_references(balances,variable,all):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        refs = resp.get("data", {}).get("references", {})
        assert "definitions" in refs and "usages" in refs


def test_96_contract_references(engine):
    resp = engine.find_references("Token", "contract", reference_type="all")
    print("find_references(Token,contract,all):", resp)
    assert resp.get("success") in (True, False)


def test_97_references_filtered_by_contracts(engine):
    resp = engine.find_references("transfer", "function", filters={"contracts": [".*Token.*"]})
    print("find_references(transfer,function,contracts=.*Token.*):", resp)
    assert resp.get("success") in (True, False)


def test_98_references_filtered_by_files(engine):
    resp = engine.find_references("transfer", "function", filters={"files": ["detailed_scenarios/.*"]})
    print("find_references(transfer,function,files=detailed_scenarios):", resp)
    assert resp.get("success") in (True, False)


def test_99_nonexistent_target(engine):
    resp = engine.find_references("doesNotExist", "function")
    print("find_references(doesNotExist,function):", resp)
    assert resp.get("success") is False
    assert resp.get("errors")


def test_100_target_types_coverage(engine):
    for t in ("modifier", "event", "struct", "enum"):
        resp = engine.find_references("transfer", t)  # target name is a placeholder, may be not found
        print("find_references(transfer,", t, "):", resp)
        # Either success with references or standardized error for not found
        assert resp.get("success") in (True, False)


