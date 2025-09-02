"""Test LLMSerializer functionality including the new source_code field."""

import pytest
import tempfile
import os
from pathlib import Path

from sol_query import SolidityQueryEngine
from sol_query.utils.serialization import LLMSerializer, SerializationLevel


class TestLLMSerializerSourceCode:
    """Test the source_code field in node serialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SolidityQueryEngine()

        # Create a test contract with various node types
        self.test_code = """
        pragma solidity ^0.8.0;
        
        contract TestContract {
            uint256 public balance;
            
            event Transfer(address indexed from, address indexed to, uint256 value);
            
            modifier onlyOwner() {
                require(msg.sender == owner);
                _;
            }
            
            function transfer(address to, uint256 amount) public onlyOwner returns (bool) {
                balance -= amount;
                emit Transfer(msg.sender, to, amount);
                return true;
            }
            
            function getBalance() public view returns (uint256) {
                return balance;
            }
        }
        """

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(self.test_code)
            self.temp_file = f.name

        self.engine.load_sources(self.temp_file)

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)

    def test_contract_serialization_includes_source_code(self):
        """Test that contract serialization includes source_code field."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        contracts = self.engine.contracts.with_name("TestContract")
        assert len(contracts) > 0, "Should find TestContract"

        contract = contracts.first()
        serialized = serializer.serialize_node(contract)

        # Check that source_code_preview field exists
        assert "source_code_preview" in serialized, "Serialized contract should include source_code_preview field"
        assert isinstance(serialized["source_code_preview"], str), "source_code_preview should be a string"
        assert len(serialized["source_code_preview"]) > 0, "source_code_preview should not be empty"

        # Check that the source code contains expected contract content
        source_code = serialized["source_code_preview"]
        assert "contract TestContract" in source_code
        assert "uint256 public balance" in source_code

    def test_function_serialization_includes_source_code(self):
        """Test that function serialization includes source_code_preview field."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        functions = self.engine.functions.with_name("transfer")
        assert len(functions) > 0, "Should find transfer function"

        function = functions.first()
        serialized = serializer.serialize_node(function)

        # Check that source_code_preview field exists
        assert "source_code_preview" in serialized, "Serialized function should include source_code_preview field"
        assert isinstance(serialized["source_code_preview"], str), "source_code_preview should be a string"
        assert len(serialized["source_code_preview"]) > 0, "source_code_preview should not be empty"

        # Check that the source code contains expected function content
        source_code = serialized["source_code_preview"]
        assert "function transfer" in source_code
        assert "onlyOwner" in source_code
        assert "returns (bool)" in source_code

    def test_variable_serialization_includes_source_code(self):
        """Test that variable serialization includes source_code_preview field."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        variables = self.engine.variables.with_name("balance")
        assert len(variables) > 0, "Should find balance variable"

        variable = variables.first()
        serialized = serializer.serialize_node(variable)

        # Check that source_code_preview field exists
        assert "source_code_preview" in serialized, "Serialized variable should include source_code_preview field"
        assert isinstance(serialized["source_code_preview"], str), "source_code_preview should be a string"
        assert len(serialized["source_code_preview"]) > 0, "source_code_preview should not be empty"

        # Check that the source code contains expected variable content
        source_code = serialized["source_code_preview"]
        assert "uint256" in source_code
        assert "balance" in source_code

    def test_source_code_in_different_serialization_levels(self):
        """Test that source_code_preview field is included in all serialization levels."""
        contract = self.engine.contracts.with_name("TestContract").first()

        # Test SUMMARY level
        serializer_summary = LLMSerializer(SerializationLevel.SUMMARY)
        serialized_summary = serializer_summary.serialize_node(contract)
        assert "source_code_preview" in serialized_summary, "SUMMARY level should include source_code_preview"

        # Test DETAILED level
        serializer_detailed = LLMSerializer(SerializationLevel.DETAILED)
        serialized_detailed = serializer_detailed.serialize_node(contract)
        assert "source_code_preview" in serialized_detailed, "DETAILED level should include source_code_preview"

        # Test FULL level
        serializer_full = LLMSerializer(SerializationLevel.FULL)
        serialized_full = serializer_full.serialize_node(contract)
        assert "source_code_preview" in serialized_full, "FULL level should include source_code_preview"

        # All should have the same source_code_preview content
        assert serialized_summary["source_code_preview"] == serialized_detailed["source_code_preview"]
        assert serialized_detailed["source_code_preview"] == serialized_full["source_code_preview"]

    def test_collection_serialization_includes_source_code(self):
        """Test that collection serialization includes source_code_preview for all items."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        functions = self.engine.functions
        serialized_collection = serializer.serialize_collection(functions, limit=3)

        assert "items" in serialized_collection, "Collection should have items"
        assert len(serialized_collection["items"]) > 0, "Should have serialized items"

        # Check that each item has source_code_preview
        for item in serialized_collection["items"]:
            assert "source_code_preview" in item, f"Each serialized item should include source_code_preview field"
            assert isinstance(item["source_code_preview"], str), "source_code_preview should be a string"
            assert len(item["source_code_preview"]) > 0, "source_code_preview should not be empty"

    def test_query_result_serialization_includes_source_code(self):
        """Test that query result serialization includes source_code_preview."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        # Test single node result
        contract = self.engine.contracts.with_name("TestContract").first()
        result = serializer.serialize_query_result(contract)

        assert "result" in result, "Query result should have result field"
        assert "source_code_preview" in result["result"], "Single node result should include source_code_preview"

        # Test collection result
        functions = self.engine.functions
        collection_result = serializer.serialize_query_result(functions)

        assert "result" in collection_result, "Collection result should have result field"
        assert "items" in collection_result["result"], "Collection result should have items"

        for item in collection_result["result"]["items"]:
            assert "source_code_preview" in item, "Each item in collection result should include source_code_preview"

    def test_source_code_consistency_with_get_source_code(self):
        """Test that serialized source_code_preview is based on node.get_source_code()."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        function = self.engine.functions.with_name("transfer").first()
        serialized = serializer.serialize_node(function)

        # Direct call to get_source_code should be used to create preview
        direct_source = function.get_source_code()
        serialized_preview = serialized["source_code_preview"]

        # The preview should be derived from the original source
        if len(direct_source) <= 200:
            assert direct_source == serialized_preview, "For short source, preview should match original"
        else:
            # For long source, should be first 100 + ... + last 100
            assert serialized_preview.startswith(direct_source[:100]), "Preview should start with first 100 chars"
            assert serialized_preview.endswith(direct_source[-100:]), "Preview should end with last 100 chars"
            assert "..." in serialized_preview, "Preview should contain ellipsis for truncated content"

    def test_empty_or_missing_source_code_handling(self):
        """Test handling of nodes with potentially empty source code."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        # Get any node and serialize it
        contracts = self.engine.contracts
        if len(contracts) > 0:
            contract = contracts.first()
            serialized = serializer.serialize_node(contract)

            # Even if source code is minimal, the field should exist
            assert "source_code_preview" in serialized, "source_code_preview field should always exist"
            assert isinstance(serialized["source_code_preview"], str), "source_code_preview should always be a string"


class TestLLMSerializerIntegration:
    """Test LLMSerializer integration with existing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SolidityQueryEngine()

        # Use the existing sample contract for consistency with other tests
        sample_file = Path(__file__).parent / "fixtures" / "sample_contract.sol"
        if sample_file.exists():
            self.engine.load_sources(str(sample_file))

    def test_existing_serialization_compatibility(self):
        """Test that adding source_code doesn't break existing serialization."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        # Test with various node types
        contracts = self.engine.contracts
        if len(contracts) > 0:
            contract = contracts.first()
            serialized = serializer.serialize_node(contract)

            # Check that all expected fields are still present
            assert "node_type" in serialized, "node_type should be present"
            assert "source_location" in serialized, "source_location should be present"
            assert "source_code_preview" in serialized, "source_code_preview should be present"

            # Contract-specific fields should still be there
            if "name" in serialized:
                assert isinstance(serialized["name"], str), "name should be a string"

    def test_json_serialization_with_source_code(self):
        """Test that JSON serialization works correctly with source_code field."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        contracts = self.engine.contracts
        if len(contracts) > 0:
            contract = contracts.first()

            # Test dictionary serialization
            serialized_dict = serializer.serialize_node(contract)
            assert "source_code_preview" in serialized_dict

            # Test JSON string serialization
            json_string = serializer.to_json(serialized_dict)
            assert isinstance(json_string, str), "Should produce valid JSON string"
            assert "source_code_preview" in json_string, "JSON should contain source_code_preview"

            # JSON should be parseable
            import json
            parsed = json.loads(json_string)
            assert "source_code_preview" in parsed, "Parsed JSON should contain source_code_preview"

    def test_source_code_preview_truncation(self):
        """Test that long source code is properly truncated to preview format."""
        serializer = LLMSerializer(SerializationLevel.DETAILED)

        # Create a mock long source code
        long_source = "a" * 150 + "middle content here" + "z" * 150  # 318 characters total

        # Test the _create_source_preview method directly
        preview = serializer._create_source_preview(long_source)

        # Should be truncated to first 100 + ... + last 100
        expected_preview = long_source[:100] + "..." + long_source[-100:]
        assert preview == expected_preview, "Long source should be truncated properly"
        assert len(preview) == 203, "Preview should be 100 + 3 + 100 = 203 characters"

        # Test with short source code
        short_source = "short code"
        short_preview = serializer._create_source_preview(short_source)
        assert short_preview == short_source, "Short source should not be truncated"
