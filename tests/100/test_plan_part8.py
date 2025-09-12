"""
Test Plan Part 8: Use Cases 71-80
Tests get_details functionality - second part of get_details tests.
"""
import json
import pytest


def test_71_struct_details_by_name(engine):
    """
    Use Case 71: Struct details by name
    - Method: get_details
    - Params: { element_type: "struct", identifiers: ["UserData"] }
    - Expected: comprehensive information for struct elements.
    """
    resp = engine.get_details("struct", ["UserData"])
    print("Struct details(UserData):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "UserData" in elements

    element = elements["UserData"]
    assert element.get("found") is True, "UserData struct should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "UserData"
    assert basic_info.get("type") == "struct"
    assert "location" in basic_info

    # Should be in sample_contract.sol
    location = basic_info.get("location", {})
    file_path = location.get("file", "")
    assert "sample_contract.sol" in file_path

    print(f"Found UserData struct at line {location.get('line')}")


def test_72_enum_details_handling(engine):
    """
    Use Case 72: Enum details handling
    - Method: get_details
    - Params: { element_type: "enum", identifiers: ["Status"] }
    - Expected: enum details or appropriate not-found handling.
    """
    resp = engine.get_details("enum", ["Status"])
    print("Enum details(Status):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "Status" in elements

    element = elements["Status"]
    # Enum might not exist in our fixtures, so either found=True or found=False is acceptable
    if element.get("found"):
        basic_info = element["basic_info"]
        assert basic_info.get("name") == "Status"
        assert basic_info.get("type") == "enum"
        print("Found Status enum")
    else:
        print("Status enum not found (expected if not in fixtures)")


def test_73_error_details_by_name(engine):
    """
    Use Case 73: Error details by name
    - Method: get_details
    - Params: { element_type: "error", identifiers: ["InsufficientBalance"] }
    - Expected: error definition details including parameters.
    """
    resp = engine.get_details("error", ["InsufficientBalance"])
    print("Error details(InsufficientBalance):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "InsufficientBalance" in elements

    element = elements["InsufficientBalance"]
    assert element.get("found") is True, "InsufficientBalance error should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "InsufficientBalance"
    assert basic_info.get("type") == "error"
    assert "location" in basic_info

    # Should be in sample_contract.sol around line 28
    location = basic_info.get("location", {})
    file_path = location.get("file", "")
    assert "sample_contract.sol" in file_path
    assert location.get("line") == 28

    print(f"Found InsufficientBalance error at line {location.get('line')}")


def test_74_library_details_comprehensive(engine):
    """
    Use Case 74: Library details comprehensive
    - Method: get_details
    - Params: { element_type: "contract", identifiers: ["SafeMath"] }
    - Expected: library information treated as contract with appropriate details.
    """
    resp = engine.get_details("contract", ["SafeMath"])
    print("Library details(SafeMath):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "SafeMath" in elements

    element = elements["SafeMath"]
    assert element.get("found") is True, "SafeMath library should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "SafeMath"
    assert basic_info.get("type") == "contract"  # Libraries are treated as contracts
    assert "location" in basic_info

    # Should have kind = library if available
    if "kind" in basic_info:
        assert basic_info.get("kind") == "library"

    print(f"Found SafeMath library at: {basic_info.get('location')}")


def test_75_interface_details_with_functions(engine):
    """
    Use Case 75: Interface details with functions
    - Method: get_details
    - Params: { element_type: "contract", identifiers: ["IERC20"] }
    - Expected: interface details showing function signatures without implementations.
    """
    resp = engine.get_details("contract", ["IERC20"])
    print("Interface details(IERC20):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "IERC20" in elements

    element = elements["IERC20"]
    assert element.get("found") is True, "IERC20 interface should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "IERC20"
    assert basic_info.get("type") == "contract"  # Interfaces are treated as contracts
    assert "location" in basic_info

    # Should have kind = interface if available
    if "kind" in basic_info:
        assert basic_info.get("kind") == "interface"

    # Should have detailed_info with functions
    if "detailed_info" in element:
        detailed_info = element["detailed_info"]
        if "functions" in detailed_info:
            functions = detailed_info["functions"]
            assert isinstance(functions, list)
            # Should find IERC20 functions
            function_names = {f.get("name") for f in functions if isinstance(f, dict)}
            expected_ierc20_functions = {"transfer", "approve", "balanceOf", "totalSupply"}
            if expected_ierc20_functions.intersection(function_names):
                print(f"Found IERC20 functions: {expected_ierc20_functions.intersection(function_names)}")

    print(f"Found IERC20 interface at: {basic_info.get('location')}")


def test_76_inheritance_chain_analysis(engine):
    """
    Use Case 76: Inheritance chain analysis
    - Method: get_details
    - Params: { element_type: "contract", identifiers: ["MultiInheritanceToken"], include_inheritance_chain: True }
    - Expected: detailed inheritance chain information.
    """
    resp = engine.get_details("contract", ["MultiInheritanceToken"], include_inheritance_chain=True)
    print("Inheritance chain(MultiInheritanceToken):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "MultiInheritanceToken" in elements

    element = elements["MultiInheritanceToken"]
    assert element.get("found") is True, "MultiInheritanceToken should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "MultiInheritanceToken"
    assert basic_info.get("type") == "contract"

    # Should have inheritance information
    if "inheritance" in basic_info:
        inheritance = basic_info["inheritance"]
        assert isinstance(inheritance, list)
        # Should inherit from BaseToken
        assert "BaseToken" in inheritance
        print(f"MultiInheritanceToken inherits from: {inheritance}")

    # Should have detailed inheritance chain if requested
    if "inheritance_chain" in element:
        chain = element["inheritance_chain"]
        assert isinstance(chain, (list, dict))
        print(f"Inheritance chain: {chain}")

    print("Found MultiInheritanceToken with inheritance details")


def test_77_cross_contract_references(engine):
    """
    Use Case 77: Cross-contract references
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["lzReceive"], include_cross_references: True }
    - Expected: information about cross-contract usage and interface implementations.
    """
    resp = engine.get_details("function", ["lzReceive"], include_cross_references=True)
    print("Cross-contract references(lzReceive):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "lzReceive" in elements

    element = elements["lzReceive"]
    assert element.get("found") is True, "lzReceive function should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "lzReceive"
    assert basic_info.get("type") == "function"

    # Should be from LayerZero-related contracts
    location = basic_info.get("location", {})
    file_path = location.get("file", "")
    assert any(pattern in file_path for pattern in ["LayerZero", "ERC721WithImports", "MultipleInheritance"])

    # Should have cross-reference information if requested
    if "cross_references" in element:
        cross_refs = element["cross_references"]
        assert isinstance(cross_refs, (list, dict))
        print(f"Cross references: {cross_refs}")

    print("Found lzReceive with cross-reference analysis")


def test_78_data_flow_analysis_details(engine):
    """
    Use Case 78: Data flow analysis details
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["transfer"], include_data_flow: True }
    - Expected: detailed data flow analysis showing variable dependencies and modifications.
    """
    resp = engine.get_details("function", ["transfer"], include_data_flow=True)
    print("Data flow analysis(transfer):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "transfer" in elements

    element = elements["transfer"]
    assert element.get("found") is True, "transfer function should be found"

    # Validate comprehensive_info for data flow
    if "comprehensive_info" in element:
        comprehensive_info = element["comprehensive_info"]

        if "data_flow" in comprehensive_info:
            data_flow = comprehensive_info["data_flow"]
            assert isinstance(data_flow, dict)

            # Common data flow analysis fields
            if "reads" in data_flow:
                reads = data_flow["reads"]
                assert isinstance(reads, list)
                print(f"Variables read: {len(reads)}")

            if "writes" in data_flow:
                writes = data_flow["writes"]
                assert isinstance(writes, list)
                print(f"Variables written: {len(writes)}")

            if "dependencies" in data_flow:
                dependencies = data_flow["dependencies"]
                print(f"Dependencies: {dependencies}")

    print("Data flow analysis completed for transfer function")


def test_79_security_analysis_patterns(engine):
    """
    Use Case 79: Security analysis patterns
    - Method: get_details
    - Params: { element_type: "function", identifiers: ["vulnerableWithdraw"], include_security_analysis: True }
    - Expected: security pattern analysis highlighting potential vulnerabilities.
    """
    resp = engine.get_details("function", ["vulnerableWithdraw"], include_security_analysis=True)
    print("Security analysis(vulnerableWithdraw):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "vulnerableWithdraw" in elements

    element = elements["vulnerableWithdraw"]
    assert element.get("found") is True, "vulnerableWithdraw function should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "vulnerableWithdraw"
    assert basic_info.get("type") == "function"

    # Should be from ERC721Reentrancy.sol
    location = basic_info.get("location", {})
    file_path = location.get("file", "")
    assert "ERC721Reentrancy.sol" in file_path

    # Should have security analysis if requested
    if "security_analysis" in element:
        security = element["security_analysis"]
        assert isinstance(security, dict)

        # Common security analysis fields
        if "vulnerabilities" in security:
            vulnerabilities = security["vulnerabilities"]
            assert isinstance(vulnerabilities, list)
            print(f"Potential vulnerabilities: {len(vulnerabilities)}")

        if "patterns" in security:
            patterns = security["patterns"]
            print(f"Security patterns: {patterns}")

    print("Security analysis completed for vulnerableWithdraw function")


def test_80_performance_metrics_collection(engine):
    """
    Use Case 80: Performance metrics collection
    - Method: get_details
    - Params: { element_type: "contract", identifiers: ["ComplexLogic"], include_performance_metrics: True }
    - Expected: performance-related metrics and analysis for complex contract.
    """
    resp = engine.get_details("contract", ["ComplexLogic"], include_performance_metrics=True)
    print("Performance metrics(ComplexLogic):", json.dumps(resp, indent=2))
    assert resp.get("success") is True

    data = resp.get("data", {})
    assert "elements" in data
    elements = data["elements"]
    assert "ComplexLogic" in elements

    element = elements["ComplexLogic"]
    assert element.get("found") is True, "ComplexLogic contract should be found"

    # Validate structure
    assert "basic_info" in element

    # Validate basic_info
    basic_info = element["basic_info"]
    assert basic_info.get("name") == "ComplexLogic"
    assert basic_info.get("type") == "contract"

    # Should be from sample_contract.sol
    location = basic_info.get("location", {})
    file_path = location.get("file", "")
    assert "sample_contract.sol" in file_path
    assert location.get("line") == 148

    # Should have performance metrics if requested
    if "performance_metrics" in element:
        metrics = element["performance_metrics"]
        assert isinstance(metrics, dict)

        # Common performance metrics
        if "complexity" in metrics:
            complexity = metrics["complexity"]
            print(f"Complexity metrics: {complexity}")

        if "gas_estimates" in metrics:
            gas_estimates = metrics["gas_estimates"]
            print(f"Gas estimates: {gas_estimates}")

        if "function_count" in metrics:
            function_count = metrics["function_count"]
            assert function_count > 5, "ComplexLogic should have many functions"
            print(f"Function count: {function_count}")

    # Check execution time for performance
    query_info = resp.get("query_info", {})
    if "execution_time" in query_info:
        execution_time = query_info["execution_time"]
        print(f"Execution time: {execution_time}s")
        assert execution_time < 2.0, f"Details query took too long: {execution_time}s"

    print("Performance metrics analysis completed for ComplexLogic contract")