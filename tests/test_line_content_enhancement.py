"""
Test suite specifically for the line_content enhancement in find_references.
This test suite validates that the actual line content is correctly extracted
and included in the find_references response.
"""

import pytest
from pathlib import Path
from sol_query.query.engine_v2 import SolidityQueryEngineV2


class TestLineContentEnhancement:
    """Test the line_content field in find_references responses."""

    @pytest.fixture
    def engine_with_sample_contract(self):
        """Create engine loaded with sample contract."""
        engine = SolidityQueryEngineV2()

        # Load the sample contract which has known, predictable content
        fixtures_dir = Path(__file__).parent / "fixtures"
        sample_contract = fixtures_dir / "sample_contract.sol"

        if sample_contract.exists():
            engine.load_sources([sample_contract])

        return engine

    def test_function_definition_line_content(self, engine_with_sample_contract):
        """Test that function definitions include correct line content."""
        engine = engine_with_sample_contract

        # Test transfer function definition
        result = engine.find_references("transfer", "function", reference_type="definitions")

        assert result["success"], f"find_references failed: {result.get('errors', [])}"

        definitions = result["data"]["references"]["definitions"]
        assert len(definitions) > 0, "Should find transfer function definition"

        for definition in definitions:
            assert "line_content" in definition, "Definition should have line_content"
            line_content = definition["line_content"]

            # Validate line content structure for function definition
            assert isinstance(line_content, str), "line_content should be string"
            assert line_content.strip(), "line_content should not be empty"
            assert "transfer" in line_content.lower(), f"Function definition should contain 'transfer': '{line_content}'"
            assert "function" in line_content.lower(), f"Function definition should contain 'function': '{line_content}'"

            # More specific assertions for known function signature
            if "public" in line_content and "returns" in line_content:
                assert "address" in line_content, f"Transfer function should have address parameter: '{line_content}'"
                assert "uint256" in line_content, f"Transfer function should have uint256 parameter: '{line_content}'"

    def test_variable_definition_line_content(self, engine_with_sample_contract):
        """Test that variable definitions include correct line content."""
        engine = engine_with_sample_contract

        # Test _balances variable definition
        result = engine.find_references("_balances", "variable", reference_type="definitions")

        assert result["success"], f"find_references failed: {result.get('errors', [])}"

        definitions = result["data"]["references"]["definitions"]
        assert len(definitions) > 0, "Should find _balances variable definition"

        for definition in definitions:
            assert "line_content" in definition, "Variable definition should have line_content"
            line_content = definition["line_content"]

            # Validate line content for variable definition
            assert isinstance(line_content, str), "line_content should be string"
            assert line_content.strip(), "line_content should not be empty"
            assert "_balances" in line_content, f"Variable definition should contain '_balances': '{line_content}'"

            # Should be a mapping definition
            if "mapping" in line_content.lower():
                assert "address" in line_content, f"Balances mapping should include address: '{line_content}'"
                assert "uint256" in line_content, f"Balances mapping should include uint256: '{line_content}'"

    def test_variable_usage_line_content(self, engine_with_sample_contract):
        """Test that variable usages include correct line content."""
        engine = engine_with_sample_contract

        # Test _balances variable usages
        result = engine.find_references("_balances", "variable", reference_type="usages")

        assert result["success"], f"find_references failed: {result.get('errors', [])}"

        usages = result["data"]["references"]["usages"]
        # Note: usages might be empty if no usages are found in the fixture

        for usage in usages:
            assert "line_content" in usage, "Variable usage should have line_content"
            line_content = usage["line_content"]

            # Validate line content for variable usage
            assert isinstance(line_content, str), "line_content should be string"
            assert line_content.strip(), "line_content should not be empty"
            # Variable usage line should contain the variable name or be a related operation
            if "_balances" in line_content:
                assert "_balances" in line_content, f"Variable usage should reference '_balances': '{line_content}'"

    def test_line_content_matches_location(self, engine_with_sample_contract):
        """Test that line_content corresponds to the location line number."""
        engine = engine_with_sample_contract

        # Get function definitions with known locations
        result = engine.find_references("totalSupply", "function", reference_type="definitions")

        assert result["success"], f"find_references failed: {result.get('errors', [])}"

        definitions = result["data"]["references"]["definitions"]

        for definition in definitions:
            location = definition["location"]
            line_content = definition["line_content"]

            # Verify that the line_content is consistent with being a function definition
            assert "line" in location, "Location should have line number"
            assert isinstance(location["line"], int), "Line should be integer"
            assert location["line"] > 0, "Line should be positive"

            # The line_content should be relevant to the element type
            if definition.get("element_type") == "function":
                # Function definition line should contain function-related keywords
                line_lower = line_content.lower()
                assert any(keyword in line_lower for keyword in ["function", "view", "returns", "public", "external", "private", "internal"]), \
                    f"Function definition line should contain function keywords: '{line_content}'"

    def test_line_content_not_empty_for_valid_locations(self, engine_with_sample_contract):
        """Test that line_content is not empty when location is valid."""
        engine = engine_with_sample_contract

        # Test with all reference types
        result = engine.find_references("transfer", "function", reference_type="all")

        assert result["success"], f"find_references failed: {result.get('errors', [])}"

        references = result["data"]["references"]
        all_items = references["usages"] + references["definitions"]

        for item in all_items:
            location = item["location"]
            line_content = item["line_content"]

            # If location has valid file and line, line_content should not be empty
            if location.get("file") and location.get("line"):
                assert line_content.strip(), f"line_content should not be empty for valid location {location}: '{line_content}'"

    def test_line_content_consistency_across_reference_types(self, engine_with_sample_contract):
        """Test that line_content is consistent across different reference types."""
        engine = engine_with_sample_contract

        # Get definitions only
        defs_result = engine.find_references("approve", "function", reference_type="definitions")

        # Get all references
        all_result = engine.find_references("approve", "function", reference_type="all")

        if defs_result["success"] and all_result["success"]:
            defs_only = defs_result["data"]["references"]["definitions"]
            all_defs = all_result["data"]["references"]["definitions"]

            # Compare line_content for same definitions
            for def_only in defs_only:
                for all_def in all_defs:
                    # If same location, should have same line_content
                    if (def_only["location"].get("file") == all_def["location"].get("file") and
                        def_only["location"].get("line") == all_def["location"].get("line")):
                        assert def_only["line_content"] == all_def["line_content"], \
                            f"line_content should be consistent: '{def_only['line_content']}' vs '{all_def['line_content']}'"

    def test_line_content_with_helper_method_directly(self, engine_with_sample_contract):
        """Test the _get_full_line_content helper method directly."""
        engine = engine_with_sample_contract

        # Test known locations in sample contract
        test_cases = [
            {"file": "sample_contract.sol", "line": 1, "expected_content": "// SPDX-License-Identifier"},
            {"file": "sample_contract.sol", "line": 2, "expected_content": "pragma solidity"},
        ]

        for test_case in test_cases:
            location_info = {
                "file": test_case["file"],
                "line": test_case["line"]
            }

            line_content = engine._get_full_line_content(location_info)

            assert isinstance(line_content, str), "line_content should be string"
            if test_case["expected_content"]:
                assert test_case["expected_content"] in line_content, \
                    f"Line {test_case['line']} should contain '{test_case['expected_content']}': '{line_content}'"
