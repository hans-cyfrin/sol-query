"""
Comprehensive tests for get_details function using the GroupStaking contract.

This test file focuses on the specific issues identified with get_details:
1. Call graphs shouldn't be included for contract elements
2. Variables_read/written incorrectly include contracts, events, expressions  
3. Dependencies are duplicative
4. General validation of output structure and content accuracy
"""
import pytest
import json
from pathlib import Path
from sol_query.query.engine_v2 import SolidityQueryEngineV2

class TestGetDetailsGroupStaking:
    """Test get_details function with GroupStaking contract from sol-bug-bench."""

    @pytest.fixture
    def engine(self):
        """Create engine with sol-bug-bench source."""
        source_dir = Path(__file__).parent / "fixtures" / "sol-bug-bench" / "src"
        return SolidityQueryEngineV2(str(source_dir))

    @pytest.fixture
    def governance_token_file(self):
        """Path to GovernanceToken.sol containing GroupStaking contract."""
        return Path(__file__).parent / "fixtures" / "sol-bug-bench" / "src" / "GovernanceToken.sol"

    def test_get_details_groupstaking_basic_structure(self, engine):
        """Test basic structure of get_details response for GroupStaking contract."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=True,
            options={
                "include_signatures": True,
                "include_source": True,
                "max_context_lines": 400,
                "show_call_chains": True
            }
        )

        # Basic response structure validation
        assert result["success"] is True
        assert "data" in result
        assert "elements" in result["data"]
        assert "GroupStaking" in result["data"]["elements"]

        group_staking = result["data"]["elements"]["GroupStaking"]
        assert group_staking["found"] is True

        # Required top-level sections
        assert "basic_info" in group_staking
        assert "detailed_info" in group_staking
        assert "comprehensive_info" in group_staking
        assert "context" in group_staking

    def test_get_details_groupstaking_basic_info(self, engine):
        """Test basic_info section accuracy for GroupStaking contract."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=False,
            options={"include_source": False}
        )

        basic_info = result["data"]["elements"]["GroupStaking"]["basic_info"]

        # Validate basic information
        assert basic_info["name"] == "GroupStaking"
        assert basic_info["type"] == "contract"
        assert basic_info["signature"] is None  # Contracts don't have signatures

        # Location should be accurate
        location = basic_info["location"]
        assert location["line"] == 97  # Line where GroupStaking contract starts
        assert location["contract"] == "GroupStaking"
        assert "GovernanceToken.sol" in location["file"]

    def test_get_details_groupstaking_detailed_info(self, engine):
        """Test detailed_info section for GroupStaking contract."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=False,
            options={"include_source": True, "include_signatures": True}
        )

        detailed_info = result["data"]["elements"]["GroupStaking"]["detailed_info"]

        # Validate contract-specific detailed information
        assert "inheritance" in detailed_info
        assert "functions" in detailed_info
        assert "variables" in detailed_info
        assert "events" in detailed_info
        assert "modifiers" in detailed_info
        assert "source_code" in detailed_info

        # Check inheritance
        assert detailed_info["inheritance"] == ["Ownable"]

        # Check functions - should include all contract functions
        functions = detailed_info["functions"]
        function_names = [f["name"] for f in functions]
        expected_functions = [
            "constructor", "createStakingGroup", "stakeToGroup",
            "withdrawFromGroup", "getGroupInfo", "isMemberOfGroup"
        ]
        for expected_func in expected_functions:
            assert expected_func in function_names

        # Check variables - should include state variables
        variables = detailed_info["variables"]
        variable_names = [v["name"] for v in variables]
        expected_variables = ["token", "stakingGroups", "nextGroupId"]
        for expected_var in expected_variables:
            assert expected_var in variable_names

        # Check events
        events = detailed_info["events"]
        event_names = [e["name"] for e in events]
        expected_events = ["GroupCreated", "StakeAdded", "RewardsDistributed"]
        for expected_event in expected_events:
            assert expected_event in event_names

        # Check source code is included
        assert detailed_info["source_code"] is not None
        assert "contract GroupStaking is Ownable" in detailed_info["source_code"]

    def test_get_details_groupstaking_call_graph_issue(self, engine):
        """Test that call_graph is not included for contract elements (Issue #1)."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=False,
            options={}
        )

        comprehensive_info = result["data"]["elements"]["GroupStaking"]["comprehensive_info"]

        # ISSUE: Call graph should NOT be included for contracts
        # Contracts don't make function calls themselves - their functions do
        if "call_graph" in comprehensive_info:
            call_graph = comprehensive_info["call_graph"]
            # If call_graph exists, it should be empty/default values for contracts
            assert call_graph["calls_made"] == []
            assert call_graph["called_by"] == []
            assert call_graph["call_depth"] == 0
            assert call_graph["is_recursive"] is False

        assert "call_graph" not in comprehensive_info

    def test_get_details_groupstaking_data_flow_variable_categorization(self, engine):
        """Test data flow variable categorization issues (Issue #2)."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=False,
            options={}
        )

        data_flow = result["data"]["elements"]["GroupStaking"]["comprehensive_info"]["data_flow"]

        # Check variables_read and variables_written
        variables_read = data_flow["variables_read"]
        variables_written = data_flow["variables_written"]

        # ISSUE: These should not include contracts, events, or expressions
        # Contract names that shouldn't be in variables
        invalid_contract_names = ["GroupStaking", "GovernanceToken", "StakingGroup", "Ownable"]
        for invalid_name in invalid_contract_names:
            if invalid_name in variables_read:
                print(f"ERROR: Contract name '{invalid_name}' found in variables_read")
            if invalid_name in variables_written:
                print(f"ERROR: Contract name '{invalid_name}' found in variables_written")

        # Event names that shouldn't be in variables
        invalid_event_names = ["GroupCreated", "StakeAdded", "RewardsDistributed"]
        for invalid_name in invalid_event_names:
            if invalid_name in variables_read:
                print(f"ERROR: Event name '{invalid_name}' found in variables_read")
            if invalid_name in variables_written:
                print(f"ERROR: Event name '{invalid_name}' found in variables_written")

        # Error names that shouldn't be in variables
        invalid_error_names = ["InvalidTokenAddress", "InvalidWeight", "InvalidMember",
                              "BlacklistedMember", "DuplicateMember"]
        for invalid_name in invalid_error_names:
            if invalid_name in variables_read:
                print(f"ERROR: Error name '{invalid_name}' found in variables_read")
            if invalid_name in variables_written:
                print(f"ERROR: Error name '{invalid_name}' found in variables_written")

        # Expression fragments that shouldn't be variables
        invalid_expressions = ["!token", "i < group", "!token.blacklisted"]
        for invalid_expr in invalid_expressions:
            if invalid_expr in variables_read:
                print(f"ERROR: Expression '{invalid_expr}' found in variables_read")
            if invalid_expr in variables_written:
                print(f"ERROR: Expression '{invalid_expr}' found in variables_written")

        # Valid variables that should be present
        expected_read_variables = ["token", "stakingGroups", "nextGroupId", "_token",
                                  "_members", "_weights", "_groupId", "_amount", "_member"]
        expected_write_variables = ["token", "stakingGroups", "nextGroupId"]

        # Check some expected variables are present
        for expected_var in expected_write_variables:
            assert expected_var in variables_written, f"Expected variable '{expected_var}' missing from variables_written"

    def test_get_details_groupstaking_dependencies_duplication(self, engine):
        """Test dependencies duplication issue (Issue #3)."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=False,
            options={}
        )

        dependencies = result["data"]["elements"]["GroupStaking"]["comprehensive_info"]["dependencies"]

        # Count occurrences of each dependency
        dependency_counts = {}
        for dep in dependencies:
            key = (dep["name"], dep["type"])
            dependency_counts[key] = dependency_counts.get(key, 0) + 1

        # ISSUE: Check for duplicates
        duplicates = [(name_type, count) for name_type, count in dependency_counts.items() if count > 1]
        if duplicates:
            print("DUPLICATED DEPENDENCIES:")
            for (name, dep_type), count in duplicates:
                print(f"  {name} ({dep_type}): {count} times")

        # Validate expected dependencies exist
        dependency_names = [dep["name"] for dep in dependencies]
        expected_dependencies = [
            "@openzeppelin/contracts/access/Ownable.sol",
            "@openzeppelin/contracts/token/ERC20/ERC20.sol",
            "Ownable"  # Should appear once as import, once as inheritance
        ]

        for expected_dep in expected_dependencies:
            assert expected_dep in dependency_names, f"Expected dependency '{expected_dep}' not found"

        # Check inheritance specifically
        inheritance_deps = [dep for dep in dependencies if dep["type"] == "inheritance"]
        inheritance_names = [dep["name"] for dep in inheritance_deps]
        assert "Ownable" in inheritance_names

    def test_get_details_groupstaking_external_interactions(self, engine):
        """Test external interactions detection."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=False,
            options={}
        )

        data_flow = result["data"]["elements"]["GroupStaking"]["comprehensive_info"]["data_flow"]
        external_interactions = data_flow["external_interactions"]

        # GroupStaking should have external interactions with GovernanceToken
        expected_interactions = ["token.blacklisted", "token.transferFrom", "token.transfer"]

        # Check that legitimate external interactions are captured
        assert len(external_interactions) > 0

        # Validate some expected interactions
        for interaction in expected_interactions:
            # The interaction might be captured in different forms
            found = any(interaction in ext_int for ext_int in external_interactions)
            if not found:
                print(f"Expected external interaction '{interaction}' not found in: {external_interactions}")

    def test_get_details_groupstaking_state_changes(self, engine):
        """Test state changes detection."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=False,
            options={}
        )

        data_flow = result["data"]["elements"]["GroupStaking"]["comprehensive_info"]["data_flow"]

        # GroupStaking contract should have state changes (writes to stakingGroups, nextGroupId)
        assert data_flow["state_changes"] is True

    def test_get_details_groupstaking_context_information(self, engine):
        """Test context information accuracy."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=True,
            options={"max_context_lines": 100}
        )

        context = result["data"]["elements"]["GroupStaking"]["context"]

        # Validate context structure
        assert "file_context" in context
        assert "surrounding_code" in context
        assert "siblings" in context

        file_context = context["file_context"]
        assert file_context["contract"] == "GroupStaking"
        assert file_context["line_number"] == 97
        assert "GovernanceToken.sol" in file_context["file_path"]

        # Surrounding code should contain contract definition
        surrounding_code = context["surrounding_code"]
        assert "contract GroupStaking is Ownable" in surrounding_code

    def test_get_details_multiple_contracts(self, engine):
        """Test get_details with multiple contract identifiers."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking", "GovernanceToken"],
            include_context=False,
            options={"include_source": False}
        )

        assert result["success"] is True
        elements = result["data"]["elements"]

        # Both contracts should be found
        assert "GroupStaking" in elements
        assert "GovernanceToken" in elements
        assert elements["GroupStaking"]["found"] is True
        assert elements["GovernanceToken"]["found"] is True

        # Validate basic info for both
        assert elements["GroupStaking"]["basic_info"]["name"] == "GroupStaking"
        assert elements["GovernanceToken"]["basic_info"]["name"] == "GovernanceToken"

    def test_get_details_nonexistent_contract(self, engine):
        """Test get_details with non-existent contract."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["NonExistentContract"],
            include_context=False,
            options={}
        )

        assert result["success"] is True  # Overall operation succeeds
        elements = result["data"]["elements"]

        # Contract should not be found
        assert "NonExistentContract" in elements
        assert elements["NonExistentContract"]["found"] is False
        assert "error" in elements["NonExistentContract"]

    def test_get_details_options_validation(self, engine):
        """Test different option combinations."""
        # Test with minimal options
        result1 = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=False,
            options={}
        )
        assert result1["success"] is True

        # Test with all options enabled
        result2 = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=True,
            options={
                "include_signatures": True,
                "include_source": True,
                "max_context_lines": 200,
                "show_call_chains": True
            }
        )
        assert result2["success"] is True

        # Source should be included when requested
        assert "source_code" in result2["data"]["elements"]["GroupStaking"]["detailed_info"]

        # Context should be included when requested
        assert "context" in result2["data"]["elements"]["GroupStaking"]

    def print_current_issues(self, engine):
        """Helper method to print current issues for manual inspection."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["GroupStaking"],
            include_context=True,
            options={
                "include_signatures": True,
                "include_source": True,
                "max_context_lines": 400,
                "show_call_chains": True
            }
        )

        print("=== CURRENT ISSUES WITH GET_DETAILS ===")
        comprehensive_info = result["data"]["elements"]["GroupStaking"]["comprehensive_info"]

        print("\n1. CALL GRAPH (should not exist for contracts):")
        if "call_graph" in comprehensive_info:
            print("  ❌ call_graph exists in comprehensive_info")
            print(f"  Content: {comprehensive_info['call_graph']}")
        else:
            print("  ✅ call_graph correctly absent")

        print("\n2. VARIABLES CATEGORIZATION:")
        data_flow = comprehensive_info["data_flow"]
        print(f"  variables_read: {data_flow['variables_read']}")
        print(f"  variables_written: {data_flow['variables_written']}")

        print("\n3. DEPENDENCIES DUPLICATION:")
        dependencies = comprehensive_info["dependencies"]
        print(f"  Total dependencies: {len(dependencies)}")
        for dep in dependencies:
            print(f"    {dep['name']} ({dep['type']})")

        # Save full output for analysis
        with open("/tmp/groupstaking_get_details_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n  Full output saved to /tmp/groupstaking_get_details_output.json")

if __name__ == "__main__":
    # Allow running this test file directly for debugging
    test_instance = TestGetDetailsGroupStaking()
    from sol_query.query.engine_v2 import SolidityQueryEngineV2
    from pathlib import Path

    source_dir = Path(__file__).parent / "fixtures" / "sol-bug-bench" / "src"
    engine = SolidityQueryEngineV2(str(source_dir))

    print("Running manual inspection of current issues...")
    test_instance.print_current_issues(engine)
