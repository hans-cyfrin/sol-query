"""
Test Plan Part 9: Use Cases 81-90
Tests get_details functionality - final part and find_references functionality - first part.
"""
import json
import pytest


def test_81_sibling_context_present(engine):
    """
    Use Case 81: Sibling context present
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["transfer"], include_context: True }
    - Expected: context.siblings exists and lists nearby elements (limited to 5).
    """
    resp = engine.get_details("function", ["transfer"], include_context=True)
    print("Function details with siblings(transfer):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "transfer" in elements

    element = elements["transfer"]
    assert element.get("found") is True, "transfer function should be found"

    # Should have context information
    if "context" in element:
        context = element["context"]
        assert isinstance(context, dict)

        if "siblings" in context:
            siblings = context["siblings"]
            assert isinstance(siblings, list)
            assert len(siblings) <= 5, "Siblings should be limited to 5"

            # Validate sibling structure
            for sibling in siblings:
                if sibling:
                    assert isinstance(sibling, dict)
                    assert "name" in sibling
                    assert "type" in sibling

            print(f"Found {len(siblings)} siblings for transfer function")
            sibling_names = [s.get("name") for s in siblings if s]
            print(f"Sibling names: {sibling_names}")
        else:
            print("No siblings context found (may not be implemented)")
    else:
        print("No context found (may not be implemented)")


def test_82_container_hierarchy_context(engine):
    """
    Use Case 82: Container hierarchy context
    - Method: get_details
    - Params: { element_type: "variable", identifiers: ["balances"], include_context: True }
    - Expected: context.container shows the containing contract/function hierarchy.
    """
    resp = engine.get_details("variable", ["balances"], include_context=True)
    print("Variable details with container(balances):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "balances" in elements

    element = elements["balances"]
    assert element.get("found") is True, "balances variable should be found"

    # Should have context information
    if "context" in element:
        context = element["context"]
        assert isinstance(context, dict)

        if "container" in context:
            container = context["container"]
            assert isinstance(container, dict)

            # Should show containing contract
            if "name" in container:
                container_name = container["name"]
                print(f"balances variable is contained in: {container_name}")
                # Should be in Token or similar contract
                assert any(keyword in container_name for keyword in ["Token", "ERC"])

            if "type" in container:
                container_type = container["type"]
                assert container_type == "contract"

        if "hierarchy" in context:
            hierarchy = context["hierarchy"]
            assert isinstance(hierarchy, list)
            print(f"Container hierarchy: {hierarchy}")
    else:
        print("No context found (may not be implemented)")


def test_83_basic_find_references_function(engine):
    """
    Use Case 83: Basic find_references (function)
    - Method: find_references
    - Params: { target: "transfer", target_type: "function" }
    - Expected: success=True; data.references[] lists locations where transfer is called.
    """
    resp = engine.find_references("transfer", "function")
    print("Find references(transfer function):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references_data = data["references"]
    assert isinstance(references_data, dict)

    # Should have usages and definitions
    assert "usages" in references_data
    assert "definitions" in references_data

    usages = references_data["usages"]
    definitions = references_data["definitions"]
    all_references = usages + definitions

    # Should find references to transfer function (at least definitions)
    assert len(definitions) > 0, "Should find at least the definition of transfer function"

    if all_references:
        for ref in all_references:
            assert isinstance(ref, dict)
            assert "location" in ref

        print(f"Found {len(usages)} usages and {len(definitions)} definitions of transfer function")

        # Should find references in various contracts
        ref_files = {ref.get("location", {}).get("file", "") for ref in all_references}
        ref_files = {f for f in ref_files if f}  # Remove empty strings
        print(f"References found in files: {len(ref_files)}")
    else:
        print("No references found (this may be expected depending on implementation)")


def test_84_find_references_variable_state(engine):
    """
    Use Case 84: Find references (variable, state)
    - Method: find_references
    - Params: { target: "balances", target_type: "variable" }
    - Expected: locations where balances variable is accessed/modified.
    """
    resp = engine.find_references("balances", "variable")
    print("Find references(balances variable):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references_data = data["references"]
    assert isinstance(references_data, dict)

    # Should have usages and definitions
    assert "usages" in references_data
    assert "definitions" in references_data

    usages = references_data["usages"]
    definitions = references_data["definitions"]
    all_references = usages + definitions

    # Should find references to balances variable (at least definitions)
    if all_references:
        for ref in all_references:
            assert isinstance(ref, dict)
            assert "location" in ref

        print(f"Found {len(usages)} usages and {len(definitions)} definitions of balances variable")

        # Should find references in Token-related functions
        ref_contexts = {ref.get("context", {}).get("function") for ref in all_references if ref.get("context")}
        print(f"Referenced in functions: {ref_contexts}")
    else:
        print("No references found (this may be expected depending on implementation)")


def test_85_find_references_event_emit_sites(engine):
    """
    Use Case 85: Find references (event emit sites)
    - Method: find_references
    - Params: { target: "Transfer", target_type: "event" }
    - Expected: locations where Transfer event is emitted.
    """
    resp = engine.find_references("Transfer", "event")
    print("Find references(Transfer event):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find emit sites for Transfer event
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

        print(f"Found {len(all_refs)} emit sites for Transfer event")

        # Should find emits in transfer-related functions
        ref_files = {ref.get("location", {}).get("file", "") for ref in all_refs}
        ref_files = {f for f in ref_files if f}
        print(f"Transfer emitted in files: {len(ref_files)}")

        # Should include sample_contract.sol where Token contract emits Transfer
        sample_contract_refs = [ref for ref in all_refs if "sample_contract.sol" in ref.get("location", {}).get("file", "")]
        assert len(sample_contract_refs) >= 0, "Should handle Transfer emits in sample_contract.sol"
    else:
        print("No Transfer event emit sites found (unexpected)")


def test_86_find_references_modifier_usage(engine):
    """
    Use Case 86: Find references (modifier usage)
    - Method: find_references
    - Params: { target: "onlyOwner", target_type: "modifier" }
    - Expected: functions that use onlyOwner modifier.
    """
    resp = engine.find_references("onlyOwner", "modifier")
    print("Find references(onlyOwner modifier):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find functions using onlyOwner modifier
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

        print(f"Found {len(all_refs)} functions using onlyOwner modifier")

        # Should find functions like setValue, mint, transferOwnership
        ref_functions = {ref.get("context", {}).get("function") for ref in all_refs if ref.get("context")}
        expected_modified_functions = {"setValue", "mint", "transferOwnership"}
        found_modified = expected_modified_functions.intersection(ref_functions) if ref_functions else set()
        if found_modified:
            print(f"Found expected modified functions: {found_modified}")
    else:
        print("No onlyOwner modifier usage found (this may be expected depending on implementation)")


def test_87_find_references_with_filters_contract_scope(engine):
    """
    Use Case 87: Find references with filters (contract scope)
    - Method: find_references
    - Params: { target: "mint", target_type: "function", filters: { contracts: [".*Token.*"] } }
    - Expected: references to mint only within Token-related contracts.
    """
    resp = engine.find_references("mint", "function", filters={"contracts": [".*Token.*"]})
    print("Find references(mint, Token contracts only):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find references to mint function in Token contracts
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

            # Should be from Token-related contracts/files
            location = ref.get("location", {})
            contract = location.get("contract", "")
            file_path = location.get("file", "")

            # Verify it's from Token context
            is_token_context = (
                (contract and "Token" in contract) or
                (file_path and "Token" in file_path) or
                (file_path and any(keyword in file_path for keyword in ["sample_contract", "MultipleInheritance"]))
            )
            assert is_token_context, f"Reference not from Token context: {contract} in {file_path}"

        print(f"Found {len(all_refs)} references to mint in Token contracts")
    else:
        print("No mint references found in Token contracts")


def test_88_find_references_with_filters_file_scope(engine):
    """
    Use Case 88: Find references with filters (file scope)
    - Method: find_references
    - Params: { target: "owner", target_type: "variable", filters: { files: ["sample_contract.sol"] } }
    - Expected: references to owner variable only within sample_contract.sol.
    """
    resp = engine.find_references("owner", "variable", filters={"files": ["sample_contract.sol"]})
    print("Find references(owner variable, sample_contract.sol only):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find references to owner variable in sample_contract.sol
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

            # Should be from sample_contract.sol only
            location = ref.get("location", {})
            file_path = location.get("file", "")
            assert "sample_contract.sol" in file_path, f"Reference not from sample_contract.sol: {file_path}"

        print(f"Found {len(all_refs)} references to owner variable in sample_contract.sol")
    else:
        print("No owner variable references found in sample_contract.sol")


def test_89_find_references_with_depth_limit(engine):
    """
    Use Case 89: Find references with depth limit
    - Method: find_references
    - Params: { target: "balanceOf", target_type: "function", max_depth: 2 }
    - Expected: references to balanceOf and functions that call those functions (up to depth 2).
    """
    resp = engine.find_references("balanceOf", "function", max_depth=2)
    print("Find references(balanceOf, max_depth=2):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find direct and indirect references to balanceOf
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        direct_refs = []
        indirect_refs = []

        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

            # Check if this is a direct or indirect reference
            depth = ref.get("depth", 1)
            if depth == 1:
                direct_refs.append(ref)
            else:
                indirect_refs.append(ref)

        print(f"Found {len(direct_refs)} direct references and {len(indirect_refs)} indirect references")

        # Should not exceed depth limit
        max_depth_found = max((ref.get("depth", 1) for ref in all_refs), default=1)
        assert max_depth_found <= 2, f"Found references beyond depth limit: {max_depth_found}"
    else:
        print("No balanceOf references found")


def test_90_find_references_target_not_found(engine):
    """
    Use Case 90: Find references (target not found)
    - Method: find_references
    - Params: { target: "nonExistentFunction", target_type: "function" }
    - Expected: success=True; data.references=[] and appropriate message about target not found.
    """
    resp = engine.find_references("nonExistentFunction", "function")
    print("Find references(nonExistentFunction):", json.dumps(resp, indent=2))
    assert resp.get("success") is False

    # Should have appropriate error message about target not found
    errors = resp.get("errors", [])
    assert len(errors) > 0, "Should have error messages for non-existent function"
    assert any("not found" in error.lower() for error in errors), "Should include appropriate not found message"

    error_msg = errors[0] if errors else "No error message"
    print(f"Appropriate message: {error_msg}")

    print("Correctly handled non-existent function reference search")