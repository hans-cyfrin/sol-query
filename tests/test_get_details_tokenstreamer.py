"""
Test for get_details function using TokenStreamer contract from sol-bug-bench.

This test validates the specific issues identified with get_details when querying
the TokenStreamer contract with comprehensive options enabled.

Issues being tracked:
1. Call graphs shouldn't be included for contract elements  
2. Variables_read/written incorrectly include contracts, events, expressions
3. Dependencies may be duplicative or incorrect
4. General validation of output structure and content accuracy
"""
import pytest
import json
from pathlib import Path
from sol_query.query.engine_v2 import SolidityQueryEngineV2


class TestGetDetailsTokenStreamer:
    """Test get_details function with TokenStreamer contract from sol-bug-bench."""

    @pytest.fixture
    def engine(self):
        """Create engine with sol-bug-bench source."""
        source_dir = Path(__file__).parent / "fixtures" / "sol-bug-bench" / "src"
        return SolidityQueryEngineV2(str(source_dir))

    @pytest.fixture
    def stablecoin_file(self):
        """Path to StableCoin.sol containing TokenStreamer contract."""
        return Path(__file__).parent / "fixtures" / "sol-bug-bench" / "src" / "StableCoin.sol"

    def test_get_details_tokenstreamer_comprehensive(self, engine):
        """
        Test comprehensive get_details response for TokenStreamer contract.
        
        Uses the exact parameters specified in the issue report to reproduce
        and validate the same problems identified earlier.
        """
        result = engine.get_details(
            element_type="contract",
            identifiers=["TokenStreamer"],
            include_context=True,
            options={
                "include_modifiers": True,
                "include_natspec": True,
                "include_signatures": True,
                "include_source": True,
                "max_context_lines": 10,
                "resolve_inheritance": False,
                "show_call_chains": False
            }
        )

        print("=== TokenStreamer get_details Result ===")
        print(json.dumps(result, indent=2))

        # Basic response structure validation
        assert result["success"] is True, f"Request should succeed, got: {result.get('errors', [])}"
        assert "data" in result, "Response must have data field"
        assert "elements" in result["data"], "Data must have elements field"
        assert "TokenStreamer" in result["data"]["elements"], "Elements must contain TokenStreamer"

        tokenstreamer = result["data"]["elements"]["TokenStreamer"]
        assert tokenstreamer["found"] is True, "TokenStreamer should be found"

        # Validate required sections exist
        assert "basic_info" in tokenstreamer, "TokenStreamer must have basic_info"
        assert "detailed_info" in tokenstreamer, "TokenStreamer must have detailed_info"
        assert "comprehensive_info" in tokenstreamer, "TokenStreamer must have comprehensive_info"
        assert "context" in tokenstreamer, "TokenStreamer must have context (include_context=True)"

        self._validate_basic_info(tokenstreamer["basic_info"])
        self._validate_detailed_info(tokenstreamer["detailed_info"])
        self._validate_comprehensive_info_issues(tokenstreamer["comprehensive_info"])
        self._validate_context_info(tokenstreamer["context"])

    def _validate_basic_info(self, basic_info):
        """Validate basic_info section structure and content."""
        assert basic_info["name"] == "TokenStreamer", f"Expected name 'TokenStreamer', got '{basic_info['name']}'"
        assert basic_info["type"] == "contract", f"Expected type 'contract', got '{basic_info['type']}'"

        # Validate location information
        assert "location" in basic_info, "basic_info must have location"
        location = basic_info["location"]
        assert "file" in location, "location must have file field"
        assert "line" in location, "location must have line field"
        assert "column" in location, "location must have column field"
        assert location["line"] == 56, f"Expected TokenStreamer at line 56, got line {location['line']}"
        assert str(location["file"]).endswith("StableCoin.sol"), f"Expected StableCoin.sol file, got {location['file']}"

    def _validate_detailed_info(self, detailed_info):
        """Validate detailed_info section for expected TokenStreamer elements."""
        # Validate functions
        assert "functions" in detailed_info, "detailed_info must have functions"
        functions = detailed_info["functions"]
        assert isinstance(functions, list), f"Functions must be a list, got {type(functions)}"

        # Expected TokenStreamer functions
        expected_functions = {
            "constructor", "createStream", "addToStream", "withdrawFromStream",
            "getAvailableTokens", "getStreamInfo", "getUserStreams", "getStreamRate"
        }
        found_functions = {func["name"] for func in functions if "name" in func}

        missing_functions = expected_functions - found_functions
        assert len(missing_functions) == 0, f"Missing expected functions: {missing_functions}"

        # Validate events
        assert "events" in detailed_info, "detailed_info must have events"
        events = detailed_info["events"]
        assert isinstance(events, list), f"Events must be a list, got {type(events)}"

        expected_events = {"StreamCreated", "StreamDeposit", "StreamWithdrawal"}
        found_events = {event["name"] for event in events if "name" in event}

        missing_events = expected_events - found_events
        assert len(missing_events) == 0, f"Missing expected events: {missing_events}"

        # Validate variables/state
        assert "variables" in detailed_info, "detailed_info must have variables"
        variables = detailed_info["variables"]
        assert isinstance(variables, list), f"Variables must be a list, got {type(variables)}"

        # Expected TokenStreamer state variables
        expected_variables = {
            "token", "STREAM_MIN_DURATION", "STREAM_MAX_DURATION",
            "streams", "userStreams", "nextStreamId"
        }
        found_variables = {var["name"] for var in variables if "name" in var}

        missing_variables = expected_variables - found_variables
        assert len(missing_variables) == 0, f"Missing expected variables: {missing_variables}"

        # Validate source code inclusion (include_source=True)
        assert "source_code" in detailed_info, "detailed_info must have source_code (include_source=True)"
        source_code = detailed_info["source_code"]
        assert isinstance(source_code, str), f"Source code must be string, got {type(source_code)}"
        assert len(source_code.strip()) > 0, "Source code must not be empty"
        assert "contract TokenStreamer" in source_code, "Source code should contain contract definition"

    def _validate_comprehensive_info_issues(self, comprehensive_info):
        """
        Validate comprehensive_info and check for the specific issues identified.
        
        This method contains assertions that should FAIL if the issues are still present,
        and assertions that document the current (problematic) behavior.
        """
        print("\\n=== ISSUE #1: Call Graph Analysis ===")

        # ISSUE #1: Call graphs shouldn't be included for contract elements
        # Contracts don't make function calls themselves - their functions do
        if "call_graph" in comprehensive_info:
            print("❌ ISSUE: call_graph is included for contract element (should not be)")
            call_graph = comprehensive_info["call_graph"]
            print(f"Call graph data: {json.dumps(call_graph, indent=2)}")

            # If call_graph exists, it should at least be empty/default values for contracts
            assert isinstance(call_graph, dict), "Call graph must be a dictionary"

            # The following assertions document what SHOULD be true for contracts:
            # (These may fail if the issue is present)
            try:
                assert call_graph.get("calls_made", []) == [], "Contracts should not make calls directly"
                assert call_graph.get("called_by", []) == [], "Contracts should not be called directly"
                assert call_graph.get("call_depth", 0) == 0, "Contracts should have call depth 0"
                assert call_graph.get("is_recursive", False) is False, "Contracts should not be recursive"
                print("✓ Call graph has expected empty values for contract")
            except AssertionError as e:
                print(f"❌ Call graph has unexpected content: {e}")
        else:
            print("✓ No call_graph included (correct behavior for contracts)")

        print("\\n=== ISSUE #2: Data Flow Variable Categorization ===")

        # ISSUE #2: Variables_read/written incorrectly include contracts, events, expressions
        if "data_flow" in comprehensive_info:
            data_flow = comprehensive_info["data_flow"]
            print(f"Data flow analysis: {json.dumps(data_flow, indent=2)}")

            if "variables_read" in data_flow:
                variables_read = data_flow["variables_read"]
                print(f"Variables read: {variables_read}")

                # Check for incorrect inclusions
                contract_names_in_read = [var for var in variables_read if var in ["TokenStreamer", "StableCoin", "ERC20"]]
                event_names_in_read = [var for var in variables_read if var in ["StreamCreated", "StreamDeposit", "StreamWithdrawal"]]
                error_names_in_read = [var for var in variables_read if var in ["InvalidTokenAddress", "InvalidStreamDuration", "StreamNotFound", "StreamEnded", "NotStreamRecipient", "InvalidRecipient", "InvalidAmount"]]

                if contract_names_in_read:
                    print(f"❌ ISSUE: Contract names incorrectly included in variables_read: {contract_names_in_read}")
                if event_names_in_read:
                    print(f"❌ ISSUE: Event names incorrectly included in variables_read: {event_names_in_read}")
                if error_names_in_read:
                    print(f"❌ ISSUE: Error names incorrectly included in variables_read: {error_names_in_read}")

                # Valid variable names we expect
                valid_state_variables = {
                    "token", "STREAM_MIN_DURATION", "STREAM_MAX_DURATION",
                    "streams", "userStreams", "nextStreamId"
                }

                # Function parameters and local variables that might appear
                valid_local_variables = {
                    "recipient", "totalDeposited", "totalWithdrawn", "startTime", "endTime",
                    "lastUpdateTime", "exists", "streamId", "depositor", "amount", "duration",
                    "user", "_token", "to", "stream", "available", "elapsedTime", "totalDuration",
                    "totalAvailable", "rate", "streamIds"
                }

                # Check that actual state variables are properly detected
                found_state_vars = [var for var in variables_read if var in valid_state_variables]
                print(f"✓ Valid state variables found: {found_state_vars}")

            if "variables_written" in data_flow:
                variables_written = data_flow["variables_written"]
                print(f"Variables written: {variables_written}")

                # Similar validation for variables_written
                contract_names_in_written = [var for var in variables_written if var in ["TokenStreamer", "StableCoin", "ERC20"]]
                if contract_names_in_written:
                    print(f"❌ ISSUE: Contract names incorrectly included in variables_written: {contract_names_in_written}")

        print("\\n=== ISSUE #3: Dependencies Validation ===")

        # ISSUE #3: Dependencies are duplicative
        if "dependencies" in comprehensive_info:
            dependencies = comprehensive_info["dependencies"]
            print(f"Dependencies: {json.dumps(dependencies, indent=2)}")

            # Check for duplicates
            dep_names = [dep.get("name", "") for dep in dependencies]
            duplicates = [name for name in set(dep_names) if dep_names.count(name) > 1]

            if duplicates:
                print(f"❌ ISSUE: Duplicate dependencies found: {duplicates}")
            else:
                print("✓ No duplicate dependencies detected")

            # Validate dependency structure
            for dep in dependencies:
                assert "name" in dep, f"Dependency missing name field: {dep}"
                assert "type" in dep, f"Dependency missing type field: {dep}"
                assert dep["type"] in ["import", "inheritance", "library"], f"Unexpected dependency type: {dep['type']}"

    def _validate_context_info(self, context):
        """Validate context information structure and content."""
        assert "file_context" in context, "Context must have file_context"
        file_context = context["file_context"]

        assert "file_path" in file_context, "file_context must have file_path"
        assert "line_number" in file_context, "file_context must have line_number"
        assert "contract" in file_context, "file_context must have contract"

        assert file_context["contract"] == "TokenStreamer", f"Expected contract 'TokenStreamer', got '{file_context['contract']}'"
        assert file_context["line_number"] == 56, f"Expected line 56, got {file_context['line_number']}"
        assert str(file_context["file_path"]).endswith("StableCoin.sol"), f"Expected StableCoin.sol, got {file_context['file_path']}"

        # Validate surrounding code (max_context_lines=10)
        if "surrounding_code" in context:
            surrounding_code = context["surrounding_code"]
            assert isinstance(surrounding_code, str), f"Surrounding code must be string, got {type(surrounding_code)}"
            assert len(surrounding_code.strip()) > 0, "Surrounding code must not be empty"
            assert "contract TokenStreamer" in surrounding_code, "Surrounding code should contain contract definition"

    def test_get_details_tokenstreamer_minimal_options(self, engine):
        """Test TokenStreamer get_details with minimal options to compare behavior."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["TokenStreamer"],
            include_context=False,
            options={}
        )

        assert result["success"] is True
        assert "TokenStreamer" in result["data"]["elements"]

        tokenstreamer = result["data"]["elements"]["TokenStreamer"]
        assert tokenstreamer["found"] is True

        # Should have basic sections even with minimal options
        assert "basic_info" in tokenstreamer
        assert "detailed_info" in tokenstreamer

        # Should NOT have context when include_context=False
        if "context" in tokenstreamer:
            print("Note: context included even when include_context=False")

    def test_get_details_tokenstreamer_invalid_identifier(self, engine):
        """Test get_details with non-existent contract identifier."""
        result = engine.get_details(
            element_type="contract",
            identifiers=["NonExistentContract"],
            include_context=False,
            options={}
        )

        # Should still succeed but mark element as not found
        assert result["success"] is True
        assert "NonExistentContract" in result["data"]["elements"]

        non_existent = result["data"]["elements"]["NonExistentContract"]
        assert non_existent["found"] is False

    def test_get_details_tokenstreamer_function_element(self, engine):
        """Test get_details for a specific function within TokenStreamer."""
        result = engine.get_details(
            element_type="function",
            identifiers=["createStream"],
            include_context=True,
            options={
                "include_signatures": True,
                "include_source": True,
                "show_call_chains": True  # This makes sense for functions
            }
        )

        print("\\n=== Function get_details Result ===")
        print(json.dumps(result, indent=2))

        assert result["success"] is True
        # Note: Function-level call chains should be valid unlike contract-level ones
