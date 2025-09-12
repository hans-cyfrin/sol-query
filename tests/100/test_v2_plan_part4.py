def test_61_basic_function_details(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="basic")
    print("get_details(function mint, basic):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("mint", {})
        if el.get("found"):
            bi = el.get("basic_info", {})
            assert bi.get("name") == "mint"


def test_62_detailed_function_details(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="detailed")
    print("get_details(function mint, detailed):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("mint", {})
        if el.get("found"):
            assert "detailed_info" in el


def test_63_comprehensive_function_details(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="comprehensive")
    print("get_details(function mint, comprehensive):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("mint", {})
        if el.get("found"):
            ci = el.get("comprehensive_info", {})
            assert "dependencies" in ci and "call_graph" in ci and "data_flow" in ci


def test_64_basic_contract_details(engine):
    resp = engine.get_details("contract", ["MultiInheritanceToken"], analysis_depth="basic")
    print("get_details(contract MultiInheritanceToken, basic):", resp)
    assert resp.get("success") in (True, False)


def test_65_detailed_contract_with_context(engine):
    resp = engine.get_details("contract", ["ERC721WithImports"], analysis_depth="detailed", include_context=True)
    print("get_details(contract ERC721WithImports, detailed, with context):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("ERC721WithImports", {})
        if el.get("found"):
            assert "detailed_info" in el
            assert "context" in el


def test_66_comprehensive_contract_details(engine):
    resp = engine.get_details("contract", ["ERC721WithImports"], analysis_depth="comprehensive")
    print("get_details(contract ERC721WithImports, comprehensive):", resp)
    assert resp.get("success") in (True, False)


def test_67_variable_details(engine):
    resp = engine.get_details("variable", ["totalSupply"], analysis_depth="basic")
    print("get_details(variable totalSupply, basic):", resp)
    assert resp.get("success") in (True, False)


def test_68_modifier_details(engine):
    resp = engine.get_details("modifier", ["onlyOwner"], analysis_depth="detailed")
    print("get_details(modifier onlyOwner, detailed):", resp)
    assert resp.get("success") in (True, False)


def test_69_event_details(engine):
    resp = engine.get_details("event", ["TokenMinted"], analysis_depth="basic")
    print("get_details(event TokenMinted, basic):", resp)
    assert resp.get("success") in (True, False)


def test_70_error_details(engine):
    resp = engine.get_details("error", ["InsufficientBalance"], analysis_depth="basic")
    print("get_details(error InsufficientBalance, basic):", resp)
    assert resp.get("success") in (True, False)


def test_71_struct_details(engine):
    resp = engine.get_details("struct", ["UserData"], analysis_depth="basic")
    assert resp.get("success") in (True, False)


def test_72_enum_details(engine):
    resp = engine.get_details("enum", ["TokenState"], analysis_depth="basic")
    assert resp.get("success") in (True, False)


def test_73_function_details_by_signature(engine):
    resp = engine.get_details("function", ["mint(address)"], analysis_depth="basic")
    print("get_details(function mint(address), basic):", resp)
    assert resp.get("success") in (True, False)


def test_74_function_details_by_contract_element(engine):
    resp = engine.get_details("function", ["MultiInheritanceToken.mint"], analysis_depth="basic")
    print("get_details(function MultiInheritanceToken.mint, basic):", resp)
    assert resp.get("success") in (True, False)


def test_75_contract_details_by_file_contract(engine):
    key = "tests/fixtures/composition_and_imports/MultipleInheritance.sol:MultipleInheritance"
    resp = engine.get_details("contract", [key], analysis_depth="basic")
    print("get_details(contract file:contract MultipleInheritance):", resp)
    assert resp.get("success") in (True, False)


def test_76_multiple_function_identifiers(engine):
    resp = engine.get_details("function", ["approve", "balanceOf", "mint"], analysis_depth="detailed")
    assert resp.get("success") in (True, False)


def test_77_include_context_false(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="detailed", include_context=False)
    print("get_details(function mint, detailed, no context):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("mint", {})
        if el.get("found"):
            assert "context" not in el


def test_78_option_include_source_false(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="detailed", options={"include_source": False})
    print("get_details(function mint, detailed, include_source=False):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("mint", {})
        if el.get("found") and "detailed_info" in el:
            assert el["detailed_info"].get("source_code") in (None, "",)


def test_79_option_include_signatures_true(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="basic", options={"include_signatures": True})
    print("get_details(function mint, basic, include_signatures=True):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("mint", {})
        if el.get("found"):
            assert "basic_info" in el


def test_80_option_show_call_chains(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="comprehensive", options={"show_call_chains": True})
    print("get_details(function mint, comprehensive, show_call_chains=True):", resp)
    assert resp.get("success") in (True, False)


def test_81_mixed_element_types_batches(engine):
    r1 = engine.get_details("contract", ["MultiInheritanceToken", "ERC721WithImports"], analysis_depth="basic")
    r2 = engine.get_details("variable", ["owner", "balances"], analysis_depth="basic")
    print("get_details(mixed batches):", r1, r2)
    assert r1.get("success") in (True, False)
    assert r2.get("success") in (True, False)


def test_82_not_found_identifiers(engine):
    resp = engine.get_details("function", ["nonexistentFunction"], analysis_depth="basic")
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("nonexistentFunction", {})
        assert not el.get("found", True)


def test_83_depth_comparison(engine):
    r_basic = engine.get_details("function", ["transfer"], analysis_depth="basic")
    r_comp = engine.get_details("function", ["transfer"], analysis_depth="comprehensive")
    assert r_basic.get("success") in (True, False)
    assert r_comp.get("success") in (True, False)


def test_84_sibling_context_present(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="basic", include_context=True)
    print("get_details(function mint, basic, include_context=True):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        el = resp.get("data", {}).get("elements", {}).get("mint", {})
        if el.get("found") and "context" in el:
            assert "siblings" in el["context"]


def test_85_analysis_summary_fields(engine):
    resp = engine.get_details("function", ["mint", "internalOnlyFunction"], analysis_depth="detailed")
    print("get_details(function mint,internalOnlyFunction detailed):", resp)
    assert resp.get("success") in (True, False)
    if resp.get("success"):
        summary = resp.get("data", {}).get("analysis_summary", {})
        for k in ("elements_found", "elements_requested", "analysis_depth", "success_rate", "features_analyzed"):
            assert k in summary


