"""
Comprehensive tests for SolidityQueryEngineV2 API specification.

Tests the exact API from new-code-query-api-requirements.md
"""

import pytest
from unittest.mock import Mock, patch

from sol_query.query.engine_v2 import SolidityQueryEngineV2
from sol_query.core.ast_nodes import (
    ContractDeclaration, FunctionDeclaration, VariableDeclaration,
    Visibility, StateMutability
)


class TestSolidityQueryEngineV2API:
    """Test the exact API specification from requirements document."""

    @pytest.fixture
    def engine(self):
        """Engine instance for testing."""
        return SolidityQueryEngineV2()

    @pytest.fixture
    def mock_function_nodes(self):
        """Mock function nodes for testing."""
        # External function without modifiers
        external_func = Mock(spec=FunctionDeclaration)
        external_func.name = "withdraw"
        external_func.visibility = Visibility.EXTERNAL
        external_func.state_mutability = StateMutability.NONPAYABLE
        external_func.modifiers = []
        external_func.source_code = "function withdraw(uint256 amount) external { msg.sender.call(); balance = 0; }"

        # Protected function with modifier
        protected_func = Mock(spec=FunctionDeclaration)
        protected_func.name = "adminWithdraw"
        protected_func.visibility = Visibility.EXTERNAL
        protected_func.state_mutability = StateMutability.NONPAYABLE
        protected_func.modifiers = ["onlyOwner"]
        protected_func.source_code = "function adminWithdraw() external onlyOwner { }"

        # Payable function
        payable_func = Mock(spec=FunctionDeclaration)
        payable_func.name = "deposit"
        payable_func.visibility = Visibility.EXTERNAL
        payable_func.state_mutability = StateMutability.PAYABLE
        payable_func.modifiers = []
        payable_func.source_code = "function deposit() external payable { }"

        return [external_func, protected_func, payable_func]

    @pytest.fixture
    def mock_contract_nodes(self):
        """Mock contract nodes for testing."""
        contract = Mock(spec=ContractDeclaration)
        contract.name = "TokenContract"
        contract.kind = "contract"
        contract.inheritance = ["ERC20", "Ownable"]
        contract.source_code = "contract TokenContract is ERC20, Ownable { }"

        interface = Mock(spec=ContractDeclaration)
        interface.name = "IERC20"
        interface.kind = "interface"
        interface.inheritance = []
        interface.source_code = "interface IERC20 { }"

        return [contract, interface]

    def test_api_structure_exists(self, engine):
        """Test that the required API methods exist with correct signatures."""
        # Check query_code method exists with correct signature
        assert hasattr(engine, 'query_code')
        assert callable(engine.query_code)

        # Check get_details method exists
        assert hasattr(engine, 'get_details')
        assert callable(engine.get_details)

        # Check find_references method exists
        assert hasattr(engine, 'find_references')
        assert callable(engine.find_references)

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_basic_usage(self, mock_get_nodes, engine, mock_function_nodes):
        """Test basic query_code usage as specified in API."""
        mock_get_nodes.return_value = mock_function_nodes

        # Test basic function query
        result = engine.query_code("functions")

        assert result["success"] is True
        assert result["query_info"]["function"] == "query_code"
        assert result["query_info"]["result_count"] == 3
        assert "data" in result
        assert "metadata" in result
        assert "warnings" in result
        assert "errors" in result

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_with_filters(self, mock_get_nodes, engine, mock_function_nodes):
        """Test query_code with filters as shown in API examples."""
        mock_get_nodes.return_value = mock_function_nodes

        # Example from API: Find external functions without any modifier
        result = engine.query_code("functions",
            filters={
                "visibility": ["external"],
                "names": [".*withdraw.*"],
                "modifiers": []  # No modifiers
            },
            include=["source"])

        assert result["success"] is True
        assert result["query_info"]["parameters"]["filters"]["visibility"] == ["external"]
        assert result["query_info"]["parameters"]["filters"]["names"] == [".*withdraw.*"]
        assert result["query_info"]["parameters"]["filters"]["modifiers"] == []
        assert "source" in result["query_info"]["parameters"]["include"]

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_state_changes(self, mock_get_nodes, engine, mock_function_nodes):
        """Test query_code for functions that change state."""
        mock_get_nodes.return_value = mock_function_nodes

        # Example from API: Find functions that change state variables
        result = engine.query_code("functions",
            filters={
                "changes_state": True
            },
            include=["source", "variables"])

        assert result["success"] is True
        assert result["query_info"]["parameters"]["filters"]["changes_state"] is True
        assert "source" in result["query_info"]["parameters"]["include"]
        assert "variables" in result["query_info"]["parameters"]["include"]

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_external_calls(self, mock_get_nodes, engine, mock_function_nodes):
        """Test query_code for external calls."""
        mock_get_nodes.return_value = mock_function_nodes

        # Example from API: Find all external functions that make external calls
        result = engine.query_code("functions",
            filters={
                "visibility": ["external"],
                "has_external_calls": True
            },
            include=["source", "calls"])

        assert result["success"] is True
        assert result["query_info"]["parameters"]["filters"]["visibility"] == ["external"]
        assert result["query_info"]["parameters"]["filters"]["has_external_calls"] is True

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_payable_functions(self, mock_get_nodes, engine, mock_function_nodes):
        """Test query_code for payable functions."""
        mock_get_nodes.return_value = mock_function_nodes

        # Example from API: Find payable functions with specific name patterns
        result = engine.query_code("functions",
            filters={
                "names": [".*flash.*", ".*loan.*"],
                "state_mutability": ["payable"],
                "contracts": ["LendingPool", "FlashLoanReceiver"]
            },
            include=["source", "calls"])

        assert result["success"] is True
        assert result["query_info"]["parameters"]["filters"]["names"] == [".*flash.*", ".*loan.*"]
        assert result["query_info"]["parameters"]["filters"]["state_mutability"] == ["payable"]

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_low_level_calls(self, mock_get_nodes, engine):
        """Test query_code for low-level calls."""
        mock_get_nodes.return_value = []

        # Example from API: Find low-level calls with ETH transfers
        result = engine.query_code("calls",
            filters={
                "call_types": ["call"],
                "has_value": True,
                "low_level": True
            },
            include=["source"])

        assert result["success"] is True
        assert result["query_info"]["parameters"]["filters"]["call_types"] == ["call"]
        assert result["query_info"]["parameters"]["filters"]["has_value"] is True
        assert result["query_info"]["parameters"]["filters"]["low_level"] is True

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_variables(self, mock_get_nodes, engine):
        """Test query_code for variables."""
        mock_get_nodes.return_value = []

        # Example from API: Find public state variables of mapping type
        result = engine.query_code("variables",
            filters={
                "is_state_variable": True,
                "visibility": ["public"],
                "types": ["mapping\\(.*\\)"]
            },
            include=["source"])

        assert result["success"] is True
        assert result["query_info"]["parameters"]["filters"]["is_state_variable"] is True
        assert result["query_info"]["parameters"]["filters"]["visibility"] == ["public"]

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_with_scope(self, mock_get_nodes, engine, mock_function_nodes):
        """Test query_code with scope constraints."""
        mock_get_nodes.return_value = mock_function_nodes

        result = engine.query_code("functions",
            filters={"visibility": ["external"]},
            scope={
                "contracts": ["TokenContract", "Vault"],
                "functions": ["transfer", "withdraw"],
                "files": ["Token.sol", "Vault.sol"]
            })

        assert result["success"] is True
        assert result["query_info"]["parameters"]["scope"]["contracts"] == ["TokenContract", "Vault"]
        assert result["query_info"]["parameters"]["scope"]["functions"] == ["transfer", "withdraw"]

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_query_code_with_options(self, mock_get_nodes, engine, mock_function_nodes):
        """Test query_code with options."""
        mock_get_nodes.return_value = mock_function_nodes

        result = engine.query_code("functions",
            filters={"visibility": ["external"]},
            options={
                "max_results": 2,
                "include_inherited": True,
                "output_format": "detailed"
            })

        assert result["success"] is True
        assert result["query_info"]["parameters"]["options"]["max_results"] == 2
        assert result["query_info"]["result_count"] <= 2  # Should be limited by max_results

    def test_query_code_security_guide_examples(self, engine):
        """Test examples from security guide steps."""
        with patch.object(engine, '_get_nodes_by_query_type', return_value=[]):
            # Step 16: External calls before state updates
            result = engine.query_code("functions",
                filters={
                    "has_external_calls": True,
                    "changes_state": True
                },
                include=["source", "calls", "variables"])

            assert result["success"] is True

            # Step 67: Division operations
            result = engine.query_code("expressions",
                filters={
                    "operators": ["/", "%"]
                },
                include=["source"])

            assert result["success"] is True

            # Step 87: Loops
            result = engine.query_code("statements",
                filters={
                    "statement_types": ["for", "while"]
                },
                include=["source"])

            assert result["success"] is True

            # Step 130: tx.origin usage
            result = engine.query_code("expressions",
                filters={
                    "access_patterns": ["tx\\.origin"]
                },
                include=["source"])

            assert result["success"] is True

    def test_query_code_parameter_validation(self, engine):
        """Test parameter validation for query_code."""
        # Invalid query_type
        result = engine.query_code("invalid_type")
        assert result["success"] is False
        assert "validation_errors" in result["query_info"]
        assert any("Invalid query_type" in error["error"] for error in result["query_info"]["validation_errors"])

        # Invalid visibility
        result = engine.query_code("functions",
            filters={"visibility": ["invalid_visibility"]})
        assert result["success"] is False

        # Invalid state_mutability
        result = engine.query_code("functions",
            filters={"state_mutability": ["invalid_mutability"]})
        assert result["success"] is False

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._find_elements_by_identifiers')
    def test_get_details_basic(self, mock_find_elements, engine):
        """Test get_details with basic analysis depth."""
        mock_function = Mock(spec=FunctionDeclaration)
        mock_function.name = "withdraw"
        mock_function.visibility = Visibility.EXTERNAL
        mock_function.get_source_code.return_value = "function withdraw(uint256 amount) external { /* ... */ }"
        mock_function.source_location = Mock()
        mock_function.source_location.file_path = "/test/path.sol"
        mock_function.source_location.start_line = 42
        mock_function.parent_contract = Mock()
        mock_function.parent_contract.name = "TestContract"
        mock_find_elements.return_value = {"withdraw(uint256)": mock_function}

        result = engine.get_details("function",
            ["withdraw(uint256)", "emergencyWithdraw()"])

        assert result["success"] is True
        assert result["query_info"]["function"] == "get_details"
        assert "elements" in result["data"]

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._find_elements_by_identifiers')
    def test_get_details_detailed(self, mock_find_elements, engine):
        """Test get_details with detailed analysis depth."""
        mock_function = Mock(spec=FunctionDeclaration)
        mock_function.name = "withdraw"
        mock_function.get_source_code.return_value = "function withdraw(uint256 amount) external { /* ... */ }"
        mock_function.source_location = Mock()
        mock_function.source_location.file_path = "/test/path.sol"
        mock_function.source_location.start_line = 42
        mock_function.parent_contract = Mock()
        mock_function.parent_contract.name = "TestContract"
        mock_find_elements.return_value = {"withdraw(uint256)": mock_function}

        result = engine.get_details("function",
            ["withdraw(uint256)"],
            options={"include_source": True, "include_assembly": True})

        assert result["success"] is True
        assert result["query_info"]["parameters"]["options"]["include_source"] is True

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._find_elements_by_identifiers')
    def test_get_details_comprehensive(self, mock_find_elements, engine):
        """Test get_details with comprehensive analysis depth."""
        mock_contract = Mock(spec=ContractDeclaration)
        mock_contract.name = "LendingPool"
        mock_contract.get_source_code.return_value = "contract LendingPool { /* ... */ }"
        mock_contract.source_location = Mock()
        mock_contract.source_location.file_path = "/test/path.sol"
        mock_contract.source_location.start_line = 10
        mock_find_elements.return_value = {"LendingPool": mock_contract}

        result = engine.get_details("contract",
            ["LendingPool", "FlashLoanReceiver"],
            options={"check_standards": True, "include_tests": True})

        assert result["success"] is True

    def test_get_details_parameter_validation(self, engine):
        """Test parameter validation for get_details."""
        # Invalid element_type
        result = engine.get_details("invalid_type", ["test"])
        assert result["success"] is False
        assert "validation_errors" in result["query_info"]


        # Empty identifiers
        result = engine.get_details("function", [])
        assert result["success"] is False

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._find_target_element')
    def test_find_references_usages(self, mock_find_target, engine):
        """Test find_references for finding usages."""
        mock_function = Mock(spec=FunctionDeclaration)
        mock_function.name = "withdraw"
        mock_find_target.return_value = mock_function

        mock_usages = [{"location": {"file": "test.sol", "line": 10}, "usage_type": "call", "line_content": "withdraw(amount);"}]
        mock_definitions = [{"location": {"file": "test.sol", "line": 5}, "definition_type": "primary", "line_content": "function withdraw(uint256 amount) public {"}]
        with patch.object(engine, '_find_element_references', return_value={"usages": mock_usages, "definitions": mock_definitions}):
            result = engine.find_references("withdraw", "function",
                reference_type="usages",
                direction="backward",
                options={"show_call_chains": True})

        assert result["success"] is True
        assert result["query_info"]["function"] == "find_references"
        assert result["query_info"]["parameters"]["reference_type"] == "usages"
        assert result["query_info"]["parameters"]["direction"] == "backward"

        # Validate line_content is included in usages
        usages = result["data"]["references"]["usages"]
        assert len(usages) > 0, "Should have mocked usages"
        assert "line_content" in usages[0], "Usage should have line_content field"
        assert usages[0]["line_content"] == "withdraw(amount);", "line_content should match mocked value"

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._find_target_element')
    def test_find_references_variable(self, mock_find_target, engine):
        """Test find_references for variables."""
        mock_variable = Mock(spec=VariableDeclaration)
        mock_variable.name = "totalSupply"
        mock_find_target.return_value = mock_variable

        mock_usages = [{"location": {"file": "token.sol", "line": 25}, "usage_type": "read", "line_content": "return totalSupply;"}]
        mock_definitions = [{"location": {"file": "token.sol", "line": 8}, "definition_type": "primary", "line_content": "uint256 private totalSupply;"}]
        with patch.object(engine, '_find_element_references', return_value={"usages": mock_usages, "definitions": mock_definitions}):
            result = engine.find_references("totalSupply", "variable",
                reference_type="usages",
                direction="forward",
                filters={"contracts": ["TokenContract"]})

        assert result["success"] is True
        assert result["query_info"]["parameters"]["target"] == "totalSupply"
        assert result["query_info"]["parameters"]["target_type"] == "variable"

        # Validate line_content is included in variable usages
        usages = result["data"]["references"]["usages"]
        assert len(usages) > 0, "Should have mocked variable usages"
        assert "line_content" in usages[0], "Variable usage should have line_content field"
        assert usages[0]["line_content"] == "return totalSupply;", "line_content should match mocked value"

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._find_target_element')
    def test_find_references_all_types(self, mock_find_target, engine):
        """Test find_references with all reference types."""
        mock_function = Mock(spec=FunctionDeclaration)
        mock_function.name = "transfer"
        mock_find_target.return_value = mock_function

        mock_usages = [{"location": {"file": "contract.sol", "line": 42}, "usage_type": "call", "line_content": "transfer(to, amount);"}]
        mock_definitions = [{"location": {"file": "contract.sol", "line": 15}, "definition_type": "primary", "line_content": "function transfer(address to, uint256 amount) public returns (bool) {"}]
        with patch.object(engine, '_find_element_references', return_value={"usages": mock_usages, "definitions": mock_definitions}):
            result = engine.find_references("transfer", "function",
                reference_type="all",
                direction="both")

        assert result["success"] is True
        assert result["query_info"]["parameters"]["reference_type"] == "all"
        assert result["query_info"]["parameters"]["direction"] == "both"

        # Validate line_content is included in both usages and definitions
        references = result["data"]["references"]
        usages = references["usages"]
        definitions = references["definitions"]

        assert len(usages) > 0, "Should have mocked usages"
        assert "line_content" in usages[0], "Usage should have line_content field"
        assert usages[0]["line_content"] == "transfer(to, amount);", "Usage line_content should match mocked value"

        assert len(definitions) > 0, "Should have mocked definitions"
        assert "line_content" in definitions[0], "Definition should have line_content field"
        assert definitions[0]["line_content"] == "function transfer(address to, uint256 amount) public returns (bool) {", "Definition line_content should match mocked value"

    def test_find_references_parameter_validation(self, engine):
        """Test parameter validation for find_references."""
        # Invalid target_type
        result = engine.find_references("test", "invalid_type")
        assert result["success"] is False

        # Invalid reference_type
        result = engine.find_references("test", "function", reference_type="invalid_ref_type")
        assert result["success"] is False

        # Invalid direction
        result = engine.find_references("test", "function", direction="invalid_direction")
        assert result["success"] is False

        # Invalid max_depth
        result = engine.find_references("test", "function", max_depth=0)
        assert result["success"] is False

    def test_find_references_target_not_found(self, engine):
        """Test find_references when target element is not found."""
        with patch.object(engine, '_find_target_element', return_value=None):
            result = engine.find_references("nonexistent", "function")

        assert result["success"] is False
        assert "not found" in result["errors"][0]

    def test_response_format_consistency(self, engine):
        """Test that all methods return consistent response format."""
        with patch.object(engine, '_get_nodes_by_query_type', return_value=[]):
            query_result = engine.query_code("functions")

        with patch.object(engine, '_find_elements_by_identifiers', return_value={}):
            details_result = engine.get_details("function", ["test"])

        with patch.object(engine, '_find_target_element', return_value=None):
            references_result = engine.find_references("test", "function")

        # Check all responses have required fields
        for result in [query_result, details_result, references_result]:
            assert "success" in result
            assert "query_info" in result
            assert "data" in result
            assert "metadata" in result
            assert "warnings" in result
            assert "errors" in result

            # Check query_info structure
            query_info = result["query_info"]
            assert "function" in query_info
            assert "parameters" in query_info
            assert "execution_time" in query_info
            assert "result_count" in query_info
            assert "cache_hit" in query_info

    def test_error_response_format(self, engine):
        """Test error response format matches specification."""
        # Generate an error response
        result = engine.query_code("invalid_type")

        assert result["success"] is False
        assert result["data"] is None
        assert "errors" in result
        assert len(result["errors"]) > 0

        # Check validation_errors structure
        if "validation_errors" in result["query_info"]:
            for error in result["query_info"]["validation_errors"]:
                assert "parameter" in error
                assert "error" in error
                # Optional fields
                if "suggestion" in error:
                    assert isinstance(error["suggestion"], str)
                if "valid_values" in error:
                    assert isinstance(error["valid_values"], list)

    @patch('sol_query.query.engine_v2.SolidityQueryEngineV2._get_nodes_by_query_type')
    def test_metadata_structure(self, mock_get_nodes, engine):
        """Test metadata structure in responses."""
        mock_get_nodes.return_value = []

        result = engine.query_code("functions")

        metadata = result["metadata"]
        assert "analysis_scope" in metadata
        assert "filters_applied" in metadata
        assert "performance" in metadata

        # Check performance structure
        performance = metadata["performance"]
        assert "nodes_analyzed" in performance
        assert "files_processed" in performance
        assert "memory_usage" in performance

    def test_include_options_validation(self, engine):
        """Test that include options are properly handled."""
        valid_includes = [
            "source", "ast", "calls", "callers", "variables", "events",
            "modifiers", "natspec", "dependencies", "inheritance",
            "implementations", "overrides"
        ]

        with patch.object(engine, '_get_nodes_by_query_type', return_value=[]):
            for include_option in valid_includes:
                result = engine.query_code("functions", include=[include_option])
                assert result["success"] is True
                assert include_option in result["query_info"]["parameters"]["include"]

    def test_execution_time_tracking(self, engine):
        """Test that execution time is tracked in responses."""
        with patch.object(engine, '_get_nodes_by_query_type', return_value=[]):
            result = engine.query_code("functions")

        assert "execution_time" in result["query_info"]
        assert isinstance(result["query_info"]["execution_time"], float)
        assert result["query_info"]["execution_time"] >= 0

    def test_cache_hit_field(self, engine):
        """Test that cache_hit field is present in responses."""
        with patch.object(engine, '_get_nodes_by_query_type', return_value=[]):
            result = engine.query_code("functions")

        assert "cache_hit" in result["query_info"]
        assert isinstance(result["query_info"]["cache_hit"], bool)

    def test_metadata_structure(self, engine):
        """Test that metadata structure is correct."""
        with patch.object(engine, '_get_nodes_by_query_type', return_value=[]):
            result = engine.query_code("functions")

        metadata = result["metadata"]