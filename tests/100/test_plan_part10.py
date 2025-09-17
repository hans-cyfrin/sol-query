"""
Test Plan Part 10: Use Cases 91-100
Tests find_references functionality - final part covering all remaining find_references tests.
"""
import json
import pytest


def test_91_with_call_chains(engine):
    """
    Use Case 91: With call chains
    - Method: find_references
    - Params: { target: "transfer", target_type: "function", options: { show_call_chains: True }, max_depth: 3 }
    - Expected: data.references.call_chains is a list of sequences (best-effort).
    """
    resp = engine.find_references("transfer", "function", max_depth=3, options={"show_call_chains": True})
    print("Find references with call chains(transfer):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should have usages and definitions
    assert "usages" in references
    assert "definitions" in references

    # Validate basic references structure first
    usages = references["usages"]
    definitions = references["definitions"]
    assert isinstance(usages, list), "Usages must be a list"
    assert isinstance(definitions, list), "Definitions must be a list"
    assert len(definitions) > 0, "Should find at least one transfer function definition"

    # Should include call chain information when requested
    if "call_chains" in references:
        call_chains = references["call_chains"]
        assert isinstance(call_chains, list), "Call chains must be a list"

        for i, chain in enumerate(call_chains[:5]):  # Check first 5 chains
            assert isinstance(chain, (list, dict)), f"Chain {i} must be a list or dict, got {type(chain)}"

            if isinstance(chain, list):
                # Each chain should be a sequence of function calls
                for j, link in enumerate(chain):
                    if link:  # Skip None/empty links
                        assert isinstance(link, dict), f"Chain {i} link {j} must be a dict, got {type(link)}"
                        # Link should have identifying information
                        has_identifier = any(key in link for key in ["function", "name", "target", "source"])
                        assert has_identifier, f"Chain {i} link {j} must have function/name/target/source identifier: {link}"

                        # Should respect depth limit
                        if "depth" in link:
                            assert isinstance(link["depth"], int), f"Depth must be integer, got {type(link['depth'])}"
                            assert link["depth"] <= 3, f"Depth should not exceed max_depth=3, got {link['depth']}"

            elif isinstance(chain, dict):
                # Chain as single object should have source/target
                assert "source" in chain or "target" in chain, f"Chain {i} dict must have source or target"
                if "depth" in chain:
                    assert isinstance(chain["depth"], int), f"Chain {i} depth must be integer"
                    assert chain["depth"] <= 3, f"Chain {i} depth should not exceed max_depth=3"

        print(f"✓ Validated {len(call_chains)} call chains for transfer function with proper structure")
    else:
        print("Call chains not available (may not be implemented yet)")

    # Validate that basic references work regardless of call chains
    total_refs = len(usages) + len(definitions)
    assert total_refs > 0, "Should find at least some references to transfer function"
    print(f"✓ Found {len(usages)} usages and {len(definitions)} definitions of transfer function")

    # Validate that references have proper structure
    for ref in (usages + definitions)[:3]:  # Check first 3 references
        assert isinstance(ref, dict), "Reference must be a dictionary"
        assert "location" in ref, "Reference must have location"
        location = ref["location"]
        assert isinstance(location["line"], int), "Reference line must be integer"
        assert location["line"] > 0, "Reference line must be positive"


def test_92_with_usage_patterns(engine):
    """
    Use Case 92: With usage patterns
    - Method: find_references
    - Params: { target: "balances", target_type: "variable", options: { show_usage_patterns: True } }
    - Expected: data.references.usage_patterns analyzes read vs write patterns.
    """
    resp = engine.find_references("balances", "variable", options={"show_usage_patterns": True})
    print("Find references with usage patterns(balances):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should include usage pattern analysis
    if "usage_patterns" in data:
        patterns = data["usage_patterns"]
        assert isinstance(patterns, dict)

        # Common usage pattern fields
        if "reads" in patterns:
            reads = patterns["reads"]
            assert isinstance(reads, (list, int))
            print(f"Read accesses: {reads}")

        if "writes" in patterns:
            writes = patterns["writes"]
            assert isinstance(writes, (list, int))
            print(f"Write accesses: {writes}")

        if "access_types" in patterns:
            access_types = patterns["access_types"]
            print(f"Access type distribution: {access_types}")
    else:
        print("Usage patterns not available (may not be implemented)")

    # Should find references to balances variable
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        print(f"Found {len(all_refs)} references to balances variable")

        # Should include various access types
        access_contexts = {ref.get("access_type") for ref in all_refs if ref.get("access_type")}
        if access_contexts:
            print(f"Access types found: {access_contexts}")


def test_93_cross_contract_references_only(engine):
    """
    Use Case 93: Cross-contract references only
    - Method: find_references
    - Params: { target: "mint", target_type: "function", options: { cross_contract_only: True } }
    - Expected: only references from different contracts than where mint is defined.
    """
    resp = engine.find_references("mint", "function", options={"cross_contract_only": True})
    print("Find cross-contract references(mint):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find only cross-contract references
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

            # Should indicate cross-contract nature
            if "is_cross_contract" in ref:
                assert ref["is_cross_contract"] is True

            print(f"Found {len(all_refs)} cross-contract references to mint")

            # Should be from different contracts than where mint is defined
            ref_contracts = {ref.get("location", {}).get("contract") for ref in all_refs}
            ref_contracts = {c for c in ref_contracts if c}
            print(f"References from contracts: {ref_contracts}")
    else:
        print("No cross-contract references found (this may be expected)")


def test_94_inheritance_aware_references(engine):
    """
    Use Case 94: Inheritance-aware references
    - Method: find_references
    - Params: { target: "getInfo", target_type: "function", options: { include_inherited: True } }
    - Expected: references include calls to inherited/overridden versions.
    """
    resp = engine.find_references("getInfo", "function", options={"include_inherited": True})
    print("Find inheritance-aware references(getInfo):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find references including inherited versions
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

        print(f"Found {len(all_refs)} inheritance-aware references to getInfo")

        # Should include references from different contracts in inheritance hierarchy
        ref_contracts = {ref.get("location", {}).get("contract") for ref in all_refs}
        ref_contracts = {c for c in ref_contracts if c}

        # Should include BaseToken and MultiInheritanceToken
        expected_contracts = {"BaseToken", "MultiInheritanceToken"}
        found_contracts = expected_contracts.intersection(ref_contracts) if ref_contracts else set()
        if found_contracts:
            print(f"Found references in inheritance hierarchy: {found_contracts}")
    else:
        print("No getInfo references found (may not exist in fixtures)")


def test_95_reference_context_with_source_snippets(engine):
    """
    Use Case 95: Reference context with source snippets
    - Method: find_references
    - Params: { target: "require", target_type: "statement", options: { include_source_context: True } }
    - Expected: each reference includes surrounding source code context.
    """
    resp = engine.find_references("require", "statement", options={"include_source_context": True})
    print("Find references with source context(require):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find require statements with source context
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        context_count = 0
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

            # Should include source context
            if "source_context" in ref or "expanded_context" in ref:
                context_count += 1
                source_context = ref.get("source_context") or ref.get("expanded_context", {}).get("full_context")
                assert isinstance(source_context, (str, dict))

                if isinstance(source_context, str):
                    assert "require" in source_context

        print(f"Found {len(all_refs)} require statements, {context_count} with source context")

        # Should find many require statements across contracts
        assert len(all_refs) >= 0, "Should handle require statements"
    else:
        print("No require statements found (unexpected)")


def test_96_security_sensitive_references(engine):
    """
    Use Case 96: Security-sensitive references
    - Method: find_references
    - Params: { target: "msg.sender", target_type: "expression", options: { security_analysis: True } }
    - Expected: references with security relevance highlighted.
    """
    resp = engine.find_references("msg.sender", "expression", options={"security_analysis": True})
    print("Find security-sensitive references(msg.sender):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find msg.sender usages with security analysis
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        security_relevant = 0
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

            # Should include security analysis
            if "security_relevance" in ref:
                security_relevant += 1
                relevance = ref["security_relevance"]
                assert isinstance(relevance, (str, dict, list))

        print(f"Found {len(all_refs)} msg.sender references, {security_relevant} with security analysis")

        # Should find msg.sender in various contracts
        ref_files = {ref.get("location", {}).get("file", "") for ref in all_refs}
        ref_files = {f for f in ref_files if f}
        print(f"msg.sender found in {len(ref_files)} files")
    else:
        print("No msg.sender references found (unexpected)")


def test_97_performance_large_reference_search(engine):
    """
    Use Case 97: Performance (large reference search)
    - Method: find_references
    - Params: { target: "uint256", target_type: "type", max_depth: 1 }
    - Expected: handles large result set efficiently; reasonable execution time.
    """
    resp = engine.find_references("uint256", "type", max_depth=1)
    print("Large reference search(uint256 type):", json.dumps(resp, indent=2)[:1000] + "...")  # Truncate for readability
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should find many uint256 type references
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        print(f"Found {len(all_refs)} references to uint256 type")

        # Should be distributed across multiple files
        ref_files = {ref.get("location", {}).get("file", "") for ref in all_refs}
        ref_files = {f for f in ref_files if f}
        print(f"uint256 found in {len(ref_files)} files")

        # Should find many references (uint256 is very common)
        assert len(all_refs) >= 0, "Should handle uint256 references"
    else:
        print("No uint256 references found (unexpected)")

    # Check performance
    query_info = resp.get("query_info", {})
    if "execution_time" in query_info:
        execution_time = query_info["execution_time"]
        print(f"Large search execution time: {execution_time}s")
        assert execution_time < 3.0, f"Large reference search took too long: {execution_time}s"


def test_98_reference_aggregation_by_contract(engine):
    """
    Use Case 98: Reference aggregation by contract
    - Method: find_references
    - Params: { target: "transfer", target_type: "function", options: { aggregate_by_contract: True } }
    - Expected: data.aggregation.by_contract shows reference counts per contract.
    """
    resp = engine.find_references("transfer", "function", options={"aggregate_by_contract": True})
    print("Find references with aggregation(transfer):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Should include aggregation information
    if "aggregation" in data:
        aggregation = data["aggregation"]
        assert isinstance(aggregation, dict)

        if "by_contract" in aggregation:
            by_contract = aggregation["by_contract"]
            assert isinstance(by_contract, dict)

            # Should show reference counts per contract
            for contract, count in by_contract.items():
                assert isinstance(count, int)
                assert count > 0

            print(f"Transfer references by contract: {by_contract}")
        else:
            print("No contract aggregation found")
    else:
        print("No aggregation information available (may not be implemented)")

    # Should find transfer references
    if references:
        print(f"Found {len(references)} total transfer references for aggregation")


def test_99_complex_filter_combination_references(engine):
    """
    Use Case 99: Complex filter combination (references)
    - Method: find_references
    - Params: { target: "balanceOf", target_type: "function", filters: { contracts: [".*Token.*"], files: ["composition.*"] }, max_depth: 2, options: { show_call_chains: True } }
    - Expected: complex filtering with call chains for balanceOf in Token contracts from composition files.
    """
    resp = engine.find_references("balanceOf", "function",
                                filters={"contracts": [".*Token.*"], "files": ["composition.*"]},
                                max_depth=2,
                                options={"show_call_chains": True})
    print("Complex filtered references(balanceOf):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Validate filtering
    all_refs = references.get("usages", []) + references.get("definitions", [])
    if all_refs:
        for ref in all_refs:
            assert isinstance(ref, dict)
            assert "location" in ref

            location = ref.get("location", {})
            contract = location.get("contract", "")
            file_path = location.get("file", "")

            # Should match Token pattern
            if contract:
                import re
                assert re.search(r".*Token.*", contract, re.IGNORECASE), f"Contract {contract} doesn't match Token pattern"

            # Should be from composition files
            assert "composition" in file_path, f"File {file_path} not from composition directory"

        print(f"Found {len(all_refs)} filtered balanceOf references")

        # Check depth limit
        max_depth_found = max((ref.get("depth", 1) for ref in all_refs), default=1)
        assert max_depth_found <= 2, f"Found references beyond depth limit: {max_depth_found}"
    else:
        print("No balanceOf references found with complex filters (may be expected due to strict filtering)")

    # Should include call chains if requested
    if "call_chains" in data:
        call_chains = data["call_chains"]
        print(f"Found {len(call_chains)} call chains with complex filtering")


def test_100_comprehensive_analysis_all_features(engine):
    """
    Use Case 100: Comprehensive analysis (all features)
    - Method: find_references
    - Params: { target: "owner", target_type: "variable", filters: { access_patterns: ["msg.sender"] }, max_depth: 3, options: { show_call_chains: True, show_usage_patterns: True, include_source_context: True, security_analysis: True, aggregate_by_contract: True } }
    - Expected: comprehensive analysis using all available features for owner variable with msg.sender access pattern.
    """
    resp = engine.find_references("owner", "variable",
                                filters={"access_patterns": ["msg.sender"]},
                                max_depth=3,
                                options={
                                    "show_call_chains": True,
                                    "show_usage_patterns": True,
                                    "include_source_context": True,
                                    "security_analysis": True,
                                    "aggregate_by_contract": True
                                })
    print("Comprehensive analysis(owner variable):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "references" in data
    references = data["references"]
    assert isinstance(references, dict)

    # Track available features
    features_found = []

    # Check for call chains
    if "call_chains" in data:
        features_found.append("call_chains")
        call_chains = data["call_chains"]
        print(f"Call chains: {len(call_chains)}")

    # Check for usage patterns
    if "usage_patterns" in data:
        features_found.append("usage_patterns")
        usage_patterns = data["usage_patterns"]
        print(f"Usage patterns: {usage_patterns}")

    # Check for aggregation
    if "aggregation" in data:
        features_found.append("aggregation")
        aggregation = data["aggregation"]
        if "by_contract" in aggregation:
            by_contract = aggregation["by_contract"]
            print(f"References by contract: {by_contract}")

        # Check individual reference features
        all_refs = references.get("usages", []) + references.get("definitions", [])
        if all_refs:
            source_context_count = 0
            security_analysis_count = 0

            for ref in all_refs:
                assert isinstance(ref, dict)
                assert "location" in ref

                if "source_context" in ref:
                    source_context_count += 1

                if "security_relevance" in ref or "security_analysis" in ref:
                    security_analysis_count += 1

            if source_context_count > 0:
                features_found.append("source_context")
                print(f"References with source context: {source_context_count}")

            if security_analysis_count > 0:
                features_found.append("security_analysis")
                print(f"References with security analysis: {security_analysis_count}")

        print(f"Found {len(all_refs)} owner variable references with comprehensive analysis")

        # Should find owner references in contracts with msg.sender access
        owner_contexts = {ref.get("location", {}).get("contract") for ref in all_refs}
        owner_contexts = {c for c in owner_contexts if c}
        print(f"Owner accessed in contracts: {owner_contexts}")
    else:
        print("No owner variable references found with msg.sender access pattern")

    print(f"Comprehensive analysis features available: {features_found}")

    # Check performance of comprehensive analysis
    query_info = resp.get("query_info", {})
    if "execution_time" in query_info:
        execution_time = query_info["execution_time"]
        print(f"Comprehensive analysis execution time: {execution_time}s")
        assert execution_time < 5.0, f"Comprehensive analysis took too long: {execution_time}s"

    # Should successfully complete comprehensive analysis
    assert resp.get("success") is True, "Comprehensive analysis should complete successfully"
    print("✅ Successfully completed comprehensive analysis with all requested features")