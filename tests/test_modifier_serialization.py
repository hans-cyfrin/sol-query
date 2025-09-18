"""
Tests for modifier JSON serialization fix.

This test file specifically verifies that ModifierDeclaration objects
are properly serialized to JSON when using the 'modifiers' include option.
"""

import json
import pytest
from typing import Any, Dict, List
from sol_query.query.engine_v2 import SolidityQueryEngineV2


class TestModifierSerialization:
    """Test modifier serialization in query_code with include option."""

    @pytest.fixture
    def engine(self):
        """Engine instance for testing with loaded test sources."""
        engine = SolidityQueryEngineV2()
        engine.load_sources([
            "tests/fixtures/composition_and_imports/",
            "tests/fixtures/detailed_scenarios/",
            "tests/fixtures/sample_contract.sol",
        ])
        return engine

    def test_modifiers_include_json_serializable(self, engine):
        """Test that query_code with modifiers include returns JSON-serializable results."""
        resp = engine.query_code(
            "functions",
            {},
            {"files": [".*SimpleContract.sol"]},
            ["modifiers"]
        )

        # Verify the result is JSON serializable
        json_str = json.dumps(resp, indent=2)
        assert json_str is not None
        assert len(json_str) > 0

        # Verify response structure
        assert resp.get("success") is True
        assert "data" in resp
        assert "results" in resp["data"]

        results = resp["data"]["results"]
        assert isinstance(results, list)
        assert len(results) > 0

    def test_setValue_function_has_onlyOwner_modifier(self, engine):
        """Test that setValue function has properly serialized onlyOwner modifier."""
        resp = engine.query_code(
            "functions",
            {},
            {"files": [".*SimpleContract.sol"]},
            ["modifiers"]
        )

        assert resp.get("success") is True
        results = resp.get("data", {}).get("results", [])
        assert len(results) > 0

        # Find the setValue function in the results
        set_value_func = next((f for f in results if f.get("name") == "setValue"), None)
        assert set_value_func is not None, "setValue function not found in results"
        assert set_value_func.get("type") == "function"

        # Verify modifiers field exists and is properly structured
        modifiers = set_value_func.get("modifiers", [])
        assert isinstance(modifiers, list)
        assert len(modifiers) == 1

        # Verify modifier is a dictionary with proper structure
        only_owner_modifier = modifiers[0]
        assert isinstance(only_owner_modifier, dict)
        assert "name" in only_owner_modifier
        assert "parameter_count" in only_owner_modifier
        assert only_owner_modifier["name"] == "onlyOwner"
        assert only_owner_modifier["parameter_count"] == 0

    def test_functions_without_modifiers_have_empty_list(self, engine):
        """Test that functions without modifiers have empty modifiers list."""
        resp = engine.query_code(
            "functions",
            {},
            {"files": [".*SimpleContract.sol"]},
            ["modifiers"]
        )

        assert resp.get("success") is True
        results = resp.get("data", {}).get("results", [])
        assert len(results) > 0

        # Find the pureFunction in the results
        pure_func = next((f for f in results if f.get("name") == "pureFunction"), None)
        assert pure_func is not None, "pureFunction not found in results"

        # Verify modifiers field exists but is empty
        modifiers = pure_func.get("modifiers", [])
        assert isinstance(modifiers, list)
        assert len(modifiers) == 0

    def test_multiple_functions_with_mixed_modifiers(self, engine):
        """Test multiple functions with mixed modifier scenarios."""
        resp = engine.query_code(
            "functions",
            {},
            {"files": [".*SimpleContract.sol"]},
            ["modifiers"]
        )

        assert resp.get("success") is True
        results = resp.get("data", {}).get("results", [])

        # Create a mapping of function name to function data
        functions = {func.get("name"): func for func in results}

        # Test setValue function has modifiers
        set_value = functions.get("setValue")
        assert set_value is not None
        modifiers = set_value.get("modifiers", [])
        assert len(modifiers) == 1
        assert modifiers[0]["name"] == "onlyOwner"
        assert modifiers[0]["parameter_count"] == 0

        # Test pureFunction has no modifiers
        pure_func = functions.get("pureFunction")
        assert pure_func is not None
        modifiers = pure_func.get("modifiers", [])
        assert len(modifiers) == 0

        # Test viewFunction has no modifiers
        view_func = functions.get("viewFunction")
        assert view_func is not None
        modifiers = view_func.get("modifiers", [])
        assert len(modifiers) == 0

        # Test deposit function has no modifiers
        deposit_func = functions.get("deposit")
        assert deposit_func is not None
        modifiers = deposit_func.get("modifiers", [])
        assert len(modifiers) == 0

    def test_modifiers_include_with_other_include_options(self, engine):
        """Test that modifiers work correctly when combined with other include options."""
        resp = engine.query_code(
            "functions",
            {},
            {"files": [".*SimpleContract.sol"]},
            ["modifiers", "parameters", "signature", "source"]
        )

        assert resp.get("success") is True
        results = resp.get("data", {}).get("results", [])
        assert len(results) > 0

        # Find the setValue function in the results
        func = next((f for f in results if f.get("name") == "setValue"), None)
        assert func is not None, "setValue function not found in results"

        # Verify modifiers and available include options are present and properly structured
        assert "modifiers" in func
        assert "signature" in func
        assert "source_code" in func

        # Verify modifiers is properly serialized
        modifiers = func["modifiers"]
        assert isinstance(modifiers, list)
        assert len(modifiers) == 1
        assert isinstance(modifiers[0], dict)
        assert modifiers[0]["name"] == "onlyOwner"

        # Verify other fields are also properly structured
        assert isinstance(func.get("signature", ""), str)
        assert isinstance(func.get("source_code", ""), str)

        # Note: "parameters" include option may not be implemented yet,
        # but modifiers serialization is the main focus of this test

    def test_query_modifiers_directly(self, engine):
        """Test querying modifiers directly as a query type."""
        resp = engine.query_code(
            "modifiers",
            {},
            {"files": [".*SimpleContract.sol"]}
        )

        assert resp.get("success") is True
        results = resp.get("data", {}).get("results", [])
        assert len(results) == 1

        modifier = results[0]
        assert modifier.get("name") == "onlyOwner"
        assert modifier.get("type") == "modifier"

        # Verify the modifier result is JSON serializable
        json_str = json.dumps(modifier, indent=2)
        assert json_str is not None

    def test_comprehensive_json_serialization(self, engine):
        """Comprehensive test to ensure entire response is JSON serializable."""
        resp = engine.query_code(
            "functions",
            {},
            {"files": [".*SimpleContract.sol"]},
            ["modifiers", "parameters", "variables", "events", "source", "ast"]
        )

        # This should not raise any JSON serialization exceptions
        json_str = json.dumps(resp, indent=2)
        assert json_str is not None

        # Parse it back to ensure it's valid JSON
        parsed = json.loads(json_str)
        assert parsed == resp

        # Verify structure
        assert parsed.get("success") is True
        results = parsed.get("data", {}).get("results", [])

        # Find the setValue function and verify its modifier structure
        set_value = next((f for f in results if f.get("name") == "setValue"), None)
        assert set_value is not None

        modifiers = set_value.get("modifiers", [])
        assert len(modifiers) == 1
        assert isinstance(modifiers[0], dict)
        assert modifiers[0]["name"] == "onlyOwner"
        assert modifiers[0]["parameter_count"] == 0

    def test_modifier_serialization_structure_validation(self, engine):
        """Test that modifier serialization follows expected structure."""
        resp = engine.query_code(
            "functions",
            {"name": "setValue"},
            {"files": [".*SimpleContract.sol"]},
            ["modifiers"]
        )

        assert resp.get("success") is True
        results = resp.get("data", {}).get("results", [])
        func = results[0]
        modifiers = func.get("modifiers", [])

        # Each modifier should be a dictionary with specific fields
        for modifier in modifiers:
            assert isinstance(modifier, dict)

            # Required fields
            assert "name" in modifier
            assert "parameter_count" in modifier

            # Field types
            assert isinstance(modifier["name"], str)
            assert isinstance(modifier["parameter_count"], int)

            # Field values for onlyOwner modifier
            if modifier["name"] == "onlyOwner":
                assert modifier["parameter_count"] == 0
                assert len(modifier["name"]) > 0

    def test_no_raw_modifier_objects_in_response(self, engine):
        """Test that no raw ModifierDeclaration objects exist in the response."""
        resp = engine.query_code(
            "functions",
            {},
            {"files": [".*SimpleContract.sol"]},
            ["modifiers"]
        )

        assert resp.get("success") is True
        results = resp.get("data", {}).get("results", [])

        def check_for_raw_objects(obj, path=""):
            """Recursively check for non-serializable objects."""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Check if this looks like a raw ModifierDeclaration object
                    if hasattr(value, '__class__') and 'ModifierDeclaration' in str(type(value)):
                        pytest.fail(f"Found raw ModifierDeclaration object at {path}.{key}: {type(value)}")
                    check_for_raw_objects(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if hasattr(item, '__class__') and 'ModifierDeclaration' in str(type(item)):
                        pytest.fail(f"Found raw ModifierDeclaration object at {path}[{i}]: {type(item)}")
                    check_for_raw_objects(item, f"{path}[{i}]")

        # This will fail if any raw ModifierDeclaration objects are found
        check_for_raw_objects(resp, "response")
