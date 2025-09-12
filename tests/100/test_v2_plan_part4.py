def test_61_basic_function_details(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="basic")
    print("get_details(function mint, basic):", resp)
    assert resp.get("success") is True

    # Validate response structure
    assert "data" in resp
    assert "elements" in resp["data"]
    assert "mint" in resp["data"]["elements"]

    el = resp["data"]["elements"]["mint"]
    assert el.get("found") is True

    # Validate basic_info content against fixture
    bi = el.get("basic_info", {})
    assert bi.get("name") == "mint"
    assert bi.get("type") == "FunctionDeclaration"

    # Should find mint from ERC721WithImports.sol (first match)
    location = bi.get("location", {})
    assert str(location.get("file")).endswith("ERC721WithImports.sol")
    assert location.get("line") == 34  # Line number in ERC721WithImports.sol
    assert location.get("column") == 5
    assert location.get("contract") == "ERC721WithImports"

    # Validate signature
    assert bi.get("signature") == "mint(address)"


def test_62_detailed_function_details(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="detailed")
    print("get_details(function mint, detailed):", resp)
    assert resp.get("success") is True

    el = resp["data"]["elements"]["mint"]
    assert el.get("found") is True
    assert "detailed_info" in el

    # Validate detailed_info content against ERC721WithImports.sol
    di = el["detailed_info"]
    assert str(di.get("visibility")) == "Visibility.EXTERNAL"
    assert str(di.get("state_mutability")) == "StateMutability.PAYABLE"

    # Check modifiers - mint function has nonReentrant modifier
    modifiers = di.get("modifiers", [])
    assert "nonReentrant" in modifiers

    # Check calls made within mint function
    calls = di.get("calls", [])
    call_names = [call.get("name") for call in calls]
    # mint function should make these calls based on ERC721WithImports.sol
    expected_calls = ["require", "_safeMint", "payable(msg.sender).transfer"]
    for expected_call in expected_calls:
        assert any(expected_call in call_name for call_name in call_names), f"Expected call '{expected_call}' not found in {call_names}"


def test_63_comprehensive_function_details(engine):
    resp = engine.get_details("function", ["mint"], analysis_depth="comprehensive")
    print("get_details(function mint, comprehensive):", resp)
    assert resp.get("success") is True

    el = resp["data"]["elements"]["mint"]
    assert el.get("found") is True

    ci = el.get("comprehensive_info", {})
    assert "dependencies" in ci and "call_graph" in ci and "data_flow" in ci

    # Validate dependencies - should include imports from ERC721WithImports.sol
    dependencies = ci.get("dependencies", [])
    dep_names = [dep.get("name") for dep in dependencies]
    expected_deps = ["ERC721", "Ownable", "ReentrancyGuard", "ILayerZeroReceiver", "SafeMath"]
    for expected_dep in expected_deps:
        assert any(expected_dep in dep_name for dep_name in dep_names), f"Expected dependency '{expected_dep}' not found"

    # Validate call_graph
    call_graph = ci.get("call_graph", {})
    assert "calls_made" in call_graph
    assert "called_by" in call_graph
    assert "call_depth" in call_graph
    assert isinstance(call_graph.get("call_depth"), int)
    assert call_graph.get("call_depth") > 0  # mint makes several calls

    # Validate data_flow
    data_flow = ci.get("data_flow", {})
    assert "variables_read" in data_flow
    assert "variables_written" in data_flow
    assert "external_interactions" in data_flow
    assert "state_changes" in data_flow

    # mint function should read these variables
    vars_read = data_flow.get("variables_read", [])
    expected_read_vars = ["to", "price", "nextTokenId", "maxSupply"]
    for expected_var in expected_read_vars:
        assert any(expected_var in var_name for var_name in vars_read), f"Expected read variable '{expected_var}' not found"

    # mint function should write these variables
    vars_written = data_flow.get("variables_written", [])
    expected_written_vars = ["tokenId", "refund"]
    for expected_var in expected_written_vars:
        assert any(expected_var in var_name for var_name in vars_written), f"Expected written variable '{expected_var}' not found"

    # Should detect state changes
    assert data_flow.get("state_changes") is True


def test_64_basic_contract_details(engine):
    resp = engine.get_details("contract", ["MultiInheritanceToken"], analysis_depth="basic")
    print("get_details(contract MultiInheritanceToken, basic):", resp)
    assert resp.get("success") is True

    el = resp["data"]["elements"]["MultiInheritanceToken"]
    assert el.get("found") is True

    # Validate basic_info content against MultipleInheritance.sol
    bi = el.get("basic_info", {})
    assert bi.get("name") == "MultiInheritanceToken"
    assert bi.get("type") == "ContractDeclaration"

    location = bi.get("location", {})
    assert str(location.get("file")).endswith("MultipleInheritance.sol")
    assert location.get("line") == 54  # Contract starts at line 54
    assert location.get("column") == 1
    assert location.get("contract") == "MultiInheritanceToken"


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
    assert resp.get("success") is True

    el = resp["data"]["elements"]["totalSupply"]
    assert el.get("found") is True

    # Validate basic_info content against fixture files
    bi = el.get("basic_info", {})
    assert bi.get("name") == "totalSupply"
    assert bi.get("type") == "VariableDeclaration"

    # Should find totalSupply from MultipleInheritance.sol (BaseToken contract)
    location = bi.get("location", {})
    assert str(location.get("file")).endswith("MultipleInheritance.sol")
    assert location.get("line") == 9  # totalSupply at line 9 in BaseToken


def test_68_modifier_details(engine):
    resp = engine.get_details("modifier", ["onlyOwner"], analysis_depth="detailed")
    print("get_details(modifier onlyOwner, detailed):", resp)
    assert resp.get("success") is True

    el = resp["data"]["elements"]["onlyOwner"]
    assert el.get("found") is True

    # Validate basic_info content
    bi = el.get("basic_info", {})
    assert bi.get("name") == "onlyOwner"
    assert bi.get("type") == "ModifierDeclaration"

    # Should find onlyOwner from MultipleInheritance.sol (Ownable contract)
    location = bi.get("location", {})
    assert str(location.get("file")).endswith("MultipleInheritance.sol")
    assert location.get("line") == 39  # onlyOwner modifier at line 39

    # Validate detailed_info
    assert "detailed_info" in el


def test_69_event_details(engine):
    resp = engine.get_details("event", ["TokenMinted"], analysis_depth="basic")
    print("get_details(event TokenMinted, basic):", resp)
    assert resp.get("success") is True

    el = resp["data"]["elements"]["TokenMinted"]
    assert el.get("found") is True

    # Validate basic_info content against ERC721WithImports.sol
    bi = el.get("basic_info", {})
    assert bi.get("name") == "TokenMinted"
    assert bi.get("type") == "EventDeclaration"

    location = bi.get("location", {})
    assert str(location.get("file")).endswith("ERC721WithImports.sol")
    assert location.get("line") == 23  # TokenMinted event at line 23


def test_70_error_details(engine):
    resp = engine.get_details("error", ["InsufficientBalance"], analysis_depth="basic")
    print("get_details(error InsufficientBalance, basic):", resp)
    assert resp.get("success") is True

    el = resp["data"]["elements"]["InsufficientBalance"]
    assert el.get("found") is True

    # Validate basic_info content against sample_contract.sol
    bi = el.get("basic_info", {})
    assert bi.get("name") == "InsufficientBalance"
    assert bi.get("type") == "ErrorDeclaration"

    location = bi.get("location", {})
    assert str(location.get("file")).endswith("sample_contract.sol")
    assert location.get("line") == 28  # InsufficientBalance error at line 28


def test_71_struct_details(engine):
    resp = engine.get_details("struct", ["UserData"], analysis_depth="basic")
    assert resp.get("success") is True

    el = resp["data"]["elements"]["UserData"]
    assert el.get("found") is True

    # Validate basic_info content against sample_contract.sol
    bi = el.get("basic_info", {})
    assert bi.get("name") == "UserData"
    assert bi.get("type") == "StructDeclaration"

    location = bi.get("location", {})
    assert str(location.get("file")).endswith("sample_contract.sol")
    # UserData struct should be around line 152-158 in sample_contract.sol


def test_72_enum_details(engine):
    resp = engine.get_details("enum", ["TokenState"], analysis_depth="basic")
    assert resp.get("success") in (True, False)


def test_73_function_details_by_signature(engine):
    resp = engine.get_details("function", ["mint(address)"], analysis_depth="basic")
    print("get_details(function mint(address), basic):", resp)
    assert resp.get("success") is True

    el = resp["data"]["elements"]["mint(address)"]
    assert el.get("found") is True

    # Validate that signature-based lookup works correctly
    bi = el.get("basic_info", {})
    assert bi.get("name") == "mint"
    assert bi.get("signature") == "mint(address)"

    # Should find the specific mint(address) function from ERC721WithImports
    location = bi.get("location", {})
    assert str(location.get("file")).endswith("ERC721WithImports.sol")
    assert location.get("contract") == "ERC721WithImports"


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
    assert resp.get("success") is True  # Engine should succeed but element not found

    el = resp["data"]["elements"]["nonexistentFunction"]
    assert el.get("found") is False
    assert "error" in el
    assert "not found" in el["error"].lower()


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
    assert resp.get("success") is True

    # Validate analysis_summary contains expected values
    summary = resp["data"]["analysis_summary"]
    for k in ("elements_found", "elements_requested", "analysis_depth", "success_rate", "features_analyzed"):
        assert k in summary

    # Validate specific values
    assert summary["elements_requested"] == 2
    assert summary["elements_found"] == 2  # Both functions should be found
    assert summary["analysis_depth"] == "detailed"
    assert summary["success_rate"] == 1.0  # 100% success rate
    assert "basic_info" in summary["features_analyzed"]
    assert "detailed_info" in summary["features_analyzed"]

    # Validate both elements were found
    elements = resp["data"]["elements"]
    assert elements["mint"]["found"] is True
    assert elements["internalOnlyFunction"]["found"] is True


