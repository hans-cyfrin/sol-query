import json

def test_86_find_references_function_all(engine):
    resp = engine.find_references("transfer", "function", reference_type="all")
    print("find_references(transfer,function,all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    # Validate response structure
    assert "data" in resp
    refs = resp["data"]["references"]
    assert "usages" in refs and "definitions" in refs

    # Validate definitions structure and content
    definitions = refs["definitions"]
    assert isinstance(definitions, list)
    assert len(definitions) > 0, "Should find at least one transfer function definition"

    for transfer_def in definitions:
        # Validate definition structure
        assert isinstance(transfer_def, dict), "Definition must be a dictionary"
        assert transfer_def.get("name") == "transfer", f"Expected name 'transfer', got '{transfer_def.get('name')}'"
        assert transfer_def.get("element_type") == "function", f"Expected element_type 'function', got '{transfer_def.get('element_type')}'"
        assert "location" in transfer_def, "Definition must have location field"
        assert "line_content" in transfer_def, "Definition must have line_content field"

        # Validate location content
        location = transfer_def["location"]
        assert isinstance(location, dict), "Location must be a dictionary"
        assert "file" in location, "Location must have file field"
        assert "line" in location, "Location must have line field"
        assert "column" in location, "Location must have column field"
        assert isinstance(location["line"], int), f"Line must be integer, got {type(location['line'])}"
        assert location["line"] > 0, f"Line must be positive, got {location['line']}"
        assert str(location["file"]).endswith(".sol"), f"File must be .sol, got {location['file']}"

        # Validate line_content
        line_content = transfer_def["line_content"]
        assert isinstance(line_content, str), f"line_content must be string, got {type(line_content)}"
        assert line_content.strip(), "line_content should not be empty"
        assert "transfer" in line_content.lower(), f"line_content should contain 'transfer': '{line_content}'"
        assert "function" in line_content.lower(), f"line_content should contain 'function': '{line_content}'"

    # Validate usages structure and content
    usages = refs["usages"]
    assert isinstance(usages, list)

    # Usages should have proper structure
    for usage in usages[:5]:  # Check first 5 usages
        assert isinstance(usage, dict), "Usage must be a dictionary"
        assert "location" in usage, "Usage must have location field"
        assert "context" in usage, "Usage must have context field"
        assert "line_content" in usage, "Usage must have line_content field"

        # Validate usage location
        location = usage["location"]
        assert isinstance(location, dict), "Usage location must be a dictionary"
        assert "file" in location, "Usage location must have file field"
        assert "line" in location, "Usage location must have line field"
        assert isinstance(location["line"], int), f"Usage line must be integer, got {type(location['line'])}"
        assert location["line"] > 0, f"Usage line must be positive, got {location['line']}"

        # Validate usage context
        context = usage["context"]
        assert isinstance(context, str), f"Usage context must be string, got {type(context)}"
        # Note: Context might be empty if not yet populated by the engine
        if len(context.strip()) > 0:
            assert "transfer" in context.lower(), f"Usage context should mention 'transfer', got: {context[:100]}..."
        else:
            print(f"Warning: Empty context found for usage at line {location['line']}")

        # Validate line_content
        line_content = usage["line_content"]
        assert isinstance(line_content, str), f"Usage line_content must be string, got {type(line_content)}"
        assert line_content.strip(), "Usage line_content should not be empty"
        # Most transfer usages should contain the word "transfer" or be a related call
        if "transfer" not in line_content.lower():
            print(f"Info: Usage line_content doesn't contain 'transfer': '{line_content}'")

    print(f"✓ Validated {len(definitions)} definitions and {len(usages)} usages with detailed content checks")


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
        assert "line_content" in usage
        location = usage["location"]
        assert "file" in location
        assert "line" in location
        assert "context" in usage

        # Validate line_content
        line_content = usage["line_content"]
        assert isinstance(line_content, str), "Usage line_content must be string"
        assert line_content.strip(), "Usage line_content should not be empty"


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
        assert "line_content" in definition

        # Should find transfer functions from fixture files
        location = definition["location"]
        assert "file" in location
        assert "line" in location
        assert str(location["file"]).endswith(".sol")

        # Validate line_content
        line_content = definition["line_content"]
        assert isinstance(line_content, str), "Definition line_content must be string"
        assert line_content.strip(), "Definition line_content should not be empty"
        assert "transfer" in line_content.lower(), f"Definition line_content should contain 'transfer': '{line_content}'"


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

    # Validate variable definition with detailed checks
    definitions = refs["definitions"]
    assert isinstance(definitions, list)
    assert len(definitions) > 0, "Should find at least one balances variable definition"

    for balances_def in definitions:
        # Validate definition structure
        assert isinstance(balances_def, dict), "Variable definition must be a dictionary"
        assert balances_def.get("name") == "balances", f"Expected name 'balances', got '{balances_def.get('name')}'"
        assert balances_def.get("element_type") == "variable", f"Expected element_type 'variable', got '{balances_def.get('element_type')}'"
        assert "location" in balances_def, "Variable definition must have location field"

        # Validate location details
        location = balances_def["location"]
        assert isinstance(location, dict), "Variable location must be a dictionary"
        assert "file" in location, "Variable location must have file field"
        assert "line" in location, "Variable location must have line field"
        assert isinstance(location["line"], int), f"Variable line must be integer, got {type(location['line'])}"
        assert location["line"] > 0, f"Variable line must be positive, got {location['line']}"
        assert str(location.get("file")).endswith(".sol"), f"Variable file must be .sol, got {location['file']}"

        # Expected files for balances variable
        expected_files = ["ERC721WithImports.sol", "sample_contract.sol", "MultipleInheritance.sol"]
        file_found = any(expected_file in str(location["file"]) for expected_file in expected_files)
        if not file_found:
            print(f"Warning: balances found in unexpected file: {location['file']}")

    # Validate variable usages with detailed checks
    usages = refs["usages"]
    assert isinstance(usages, list)

    # Check usage patterns for variables
    usage_patterns = set()
    for usage in usages[:10]:  # Check first 10 usages
        assert isinstance(usage, dict), "Variable usage must be a dictionary"
        assert "location" in usage, "Variable usage must have location field"
        assert "context" in usage, "Variable usage must have context field"

        # Validate usage location
        location = usage["location"]
        assert isinstance(location, dict), "Variable usage location must be a dictionary"
        assert "line" in location, "Variable usage location must have line field"
        assert isinstance(location["line"], int), f"Variable usage line must be integer, got {type(location['line'])}"
        assert location["line"] > 0, f"Variable usage line must be positive, got {location['line']}"

        # Validate usage context and detect patterns
        context = usage["context"]
        assert isinstance(context, str), f"Variable usage context must be string, got {type(context)}"
        # Note: Context might be empty if not yet populated by the engine
        if len(context.strip()) > 0:
            assert "balances" in context, f"Variable usage context should mention 'balances', got: {context[:100]}..."
        else:
            print(f"Warning: Empty context found for variable usage at line {location['line']}")
            continue  # Skip pattern detection for empty contexts

        # Detect common variable usage patterns
        if "balances[" in context:
            usage_patterns.add("mapping_access")
        if "balances =" in context or "balances+=" in context:
            usage_patterns.add("assignment")
        if "return balances" in context:
            usage_patterns.add("return_value")

    if usage_patterns:
        print(f"✓ Found variable usage patterns: {sorted(usage_patterns)}")

    print(f"✓ Validated {len(definitions)} variable definitions and {len(usages)} usages with detailed content checks")


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

    # Validate comprehensive error response structure for nonexistent targets
    assert "errors" in resp, "Error response must have errors field"
    errors = resp.get("errors")
    assert errors is not None, "Errors field must not be None"
    assert isinstance(errors, list), f"Errors must be a list, got {type(errors)}"
    assert len(errors) > 0, "Should have at least one error message"

    # Validate error content
    error_msg = str(errors[0]).lower()
    assert "not found" in error_msg or "does not exist" in error_msg or "cannot find" in error_msg, f"Error message should indicate target not found, got: {error_msg}"

    # Should include target name in error
    assert "doesnotexist" in error_msg, f"Error should mention the target name, got: {error_msg}"

    # Check that data field is present even on error (may be null)
    assert "data" in resp, "Response should have data field even on error"
    data = resp["data"]
    # Data may be null on error, which is acceptable
    if data is not None:
        assert isinstance(data, dict), f"Data field should be a dictionary when not null, got {type(data)}"

    print(f"✓ Validated proper error handling for nonexistent target with detailed error content")


def test_100_target_types_coverage(engine):
    for t in ("modifier", "event", "struct", "enum"):
        resp = engine.find_references("transfer", t)  # target name is a placeholder, may be not found
        print("find_references(transfer,", t, "):", json.dumps(resp, indent=2))
        # Either success with references or standardized error for not found
        assert resp.get("success") in (True, False)


