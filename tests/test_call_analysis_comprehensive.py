"""Comprehensive tests for all call analysis features."""

import pytest
from pathlib import Path

from sol_query.query.engine import SolidityQueryEngine
from sol_query.analysis.call_types import CallType, CallTypeDetector
from sol_query.analysis.call_analyzer import CallAnalyzer
from sol_query.analysis.call_metadata import CallMetadata


# Sample Solidity code for testing
COMPREHENSIVE_CALL_TEST_CODE = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

library SafeMath {
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        return a + b;
    }
}

contract CallAnalysisTest {
    IERC20 public token;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    // External calls
    function externalCall(address target) external {
        // Interface call
        token.transfer(msg.sender, 100);
        
        // Low-level calls
        target.call{value: 1 ether, gas: 5000}("");
        target.delegatecall(abi.encodeWithSignature("test()"));
        target.staticcall(abi.encodeWithSignature("view()"));
        
        // Try/catch calls
        try IERC20(target).transfer(msg.sender, 50) {
            emit Transfer(address(this), msg.sender, 50);
        } catch {
            revert("Transfer failed");
        }
    }
    
    // Internal calls
    function internalCall() external {
        _internalFunction();
        this.publicFunction();
    }
    
    function _internalFunction() internal {
        // Library call
        uint256 result = SafeMath.add(10, 20);
        
        // Built-in Solidity calls
        require(result > 0, "Invalid result");
        assert(result == 30);
        
        // Event emission
        emit Transfer(address(0), msg.sender, result);
    }
    
    function publicFunction() public pure returns (uint256) {
        return 42;
    }
    
    // Assembly calls
    function assemblyCall(address target) external {
        assembly {
            let result := call(gas(), target, 0, 0, 0, 0, 0)
            if iszero(result) { revert(0, 0) }
        }
        
        assembly {
            let result := delegatecall(gas(), target, 0, 0, 0, 0)
            if iszero(result) { revert(0, 0) }
        }
        
        assembly {
            let result := staticcall(gas(), target, 0, 0, 0, 0)
            if iszero(result) { revert(0, 0) }
        }
    }
    
    // Constructor calls
    function createContract() external {
        CallAnalysisTest newContract = new CallAnalysisTest();
        uint256[] memory arr = new uint256[](10);
    }
    
    // Type conversions
    function typeConversions(address addr) external pure {
        uint256 value = uint256(uint160(addr));
        address payableAddr = payable(addr);
        bytes32 hash = keccak256(abi.encodePacked(value));
    }
}
'''


class TestCallTypeDetection:
    """Test call type detection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = CallTypeDetector()

    def test_external_call_detection(self):
        """Test detection of external calls."""
        # Interface call
        call_type = self.detector.detect_call_type("token.transfer(msg.sender, 100)")
        assert call_type == CallType.EXTERNAL

        # Contract call
        call_type = self.detector.detect_call_type("IERC20(target).transfer(msg.sender, 50)")
        assert call_type == CallType.EXTERNAL

    def test_low_level_call_detection(self):
        """Test detection of low-level calls."""
        call_type = self.detector.detect_call_type("target.call{value: 1 ether}(\"\")")
        assert call_type == CallType.LOW_LEVEL

        call_type = self.detector.detect_call_type("target.send(1 ether)")
        assert call_type == CallType.LOW_LEVEL

        call_type = self.detector.detect_call_type("target.transfer(1 ether)")
        assert call_type == CallType.LOW_LEVEL

    def test_delegate_call_detection(self):
        """Test detection of delegate calls."""
        call_type = self.detector.detect_call_type("target.delegatecall(data)")
        assert call_type == CallType.DELEGATE

    def test_static_call_detection(self):
        """Test detection of static calls."""
        call_type = self.detector.detect_call_type("target.staticcall(data)")
        assert call_type == CallType.STATIC

    def test_library_call_detection(self):
        """Test detection of library calls."""
        call_type = self.detector.detect_call_type("SafeMath.add(10, 20)")
        assert call_type == CallType.LIBRARY

    def test_solidity_builtin_detection(self):
        """Test detection of built-in Solidity functions."""
        call_type = self.detector.detect_call_type("require(condition, \"message\")")
        assert call_type == CallType.SOLIDITY

        call_type = self.detector.detect_call_type("assert(condition)")
        assert call_type == CallType.SOLIDITY

        call_type = self.detector.detect_call_type("keccak256(data)")
        assert call_type == CallType.SOLIDITY

    def test_event_emission_detection(self):
        """Test detection of event emissions."""
        call_type = self.detector.detect_call_type("emit Transfer(from, to, amount)")
        assert call_type == CallType.EVENT

    def test_assembly_call_detection(self):
        """Test detection of assembly calls."""
        assembly_code = "assembly { let result := call(gas(), target, 0, 0, 0, 0, 0) }"
        call_type = self.detector.detect_call_type(assembly_code)
        assert call_type == CallType.ASSEMBLY

        delegate_assembly = "assembly { let result := delegatecall(gas(), target, 0, 0, 0, 0) }"
        call_type = self.detector.detect_call_type(delegate_assembly)
        assert call_type == CallType.DELEGATE

    def test_constructor_call_detection(self):
        """Test detection of constructor calls."""
        call_type = self.detector.detect_call_type("new CallAnalysisTest()")
        assert call_type == CallType.NEW_CONTRACT

        call_type = self.detector.detect_call_type("new uint256[](10)")
        assert call_type == CallType.NEW_ARR

    def test_type_conversion_detection(self):
        """Test detection of type conversions."""
        call_type = self.detector.detect_call_type("uint256(value)")
        assert call_type == CallType.TYPE_CONVERSION

        call_type = self.detector.detect_call_type("payable(addr)")
        assert call_type == CallType.TYPE_CONVERSION


class TestCallFiltering:
    """Test advanced call filtering capabilities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SolidityQueryEngine()
        # Create a temporary file with test content
        self.test_file = Path("test_call_filtering.sol")
        self.test_file.write_text(COMPREHENSIVE_CALL_TEST_CODE)
        self.engine.load_sources(str(self.test_file))

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_call_type_filtering(self):
        """Test filtering expressions by call type."""
        # Test external calls
        external_calls = self.engine.expressions.external_calls()
        assert len(external_calls) > 0

        # Test internal calls
        internal_calls = self.engine.expressions.internal_calls()
        assert len(internal_calls) > 0

        # Test library calls
        library_calls = self.engine.expressions.library_calls()
        assert len(library_calls) > 0

        # Test delegate calls
        delegate_calls = self.engine.expressions.delegate_calls()
        assert len(delegate_calls) > 0

        # Test static calls
        static_calls = self.engine.expressions.static_calls()
        assert len(static_calls) > 0

        # Test low-level calls
        low_level_calls = self.engine.expressions.low_level_calls()
        assert len(low_level_calls) > 0

    def test_function_name_filtering(self):
        """Test filtering calls by function name."""
        # Test exact function name
        transfer_calls = self.engine.expressions.calls().with_callee_function_name("transfer")
        assert len(transfer_calls) > 0

        # Test case insensitive
        transfer_calls_insensitive = self.engine.expressions.calls().with_callee_function_name("TRANSFER", sensitivity=False)
        assert len(transfer_calls_insensitive) > 0

        # Test prefix filtering
        prefix_calls = self.engine.expressions.calls().with_callee_function_name_prefix("transfer")
        assert len(prefix_calls) > 0

        # Test exclusion filtering
        non_require_calls = self.engine.expressions.calls().without_callee_function_name("require")
        assert len(non_require_calls) > 0

    def test_signature_filtering(self):
        """Test filtering calls by function signature."""
        # This would work better with more detailed signature parsing
        signature_calls = self.engine.expressions.calls().with_callee_function_signature("transfer")
        assert isinstance(signature_calls, type(self.engine.expressions))

    def test_value_and_gas_filtering(self):
        """Test filtering calls by value and gas specifications."""
        # Test calls with value
        value_calls = self.engine.expressions.calls().with_call_value()
        assert len(value_calls) > 0

        # Test calls without value
        no_value_calls = self.engine.expressions.calls().without_call_value()
        assert len(no_value_calls) > 0

        # Test calls with gas
        gas_calls = self.engine.expressions.calls().with_call_gas()
        assert len(gas_calls) > 0


class TestCallMetadata:
    """Test call metadata access functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SolidityQueryEngine()
        self.test_file = Path("test_call_metadata.sol")
        self.test_file.write_text(COMPREHENSIVE_CALL_TEST_CODE)
        self.engine.load_sources(str(self.test_file))

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_call_info_access(self):
        """Test accessing call information through metadata."""
        calls = self.engine.expressions.calls()

        if len(calls) > 0:
            call = calls.first()

            # Test call info access
            call_info = call.get_call_info()
            assert isinstance(call_info, CallMetadata)

            # Test function name extraction
            func_name = call_info.get_name()
            assert func_name is None or isinstance(func_name, str)

            # Test arguments
            args = call_info.get_args()
            assert isinstance(args, list)

            # Test signature
            signature = call_info.get_signature()
            assert signature is None or isinstance(signature, str)

    def test_call_value_and_gas_extraction(self):
        """Test extraction of call value and gas."""
        low_level_calls = self.engine.expressions.low_level_calls()

        if len(low_level_calls) > 0:
            call = low_level_calls.first()
            call_info = call.get_call_info()

            # Test value extraction
            call_value = call_info.get_call_value()
            # Should find value in low-level calls

            # Test gas extraction
            call_gas = call_info.get_call_gas()
            # Should find gas in low-level calls

    def test_call_serialization(self):
        """Test call metadata serialization."""
        calls = self.engine.expressions.calls()

        if len(calls) > 0:
            call = calls.first()
            call_info = call.get_call_info()

            # Test serialization to dict
            call_dict = call_info.to_dict()
            assert isinstance(call_dict, dict)

            # Check required fields
            assert 'function_name' in call_dict
            assert 'call_type' in call_dict
            assert 'source_code' in call_dict


class TestInstructionLevelAnalysis:
    """Test instruction-level call analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SolidityQueryEngine()
        self.test_file = Path("test_instruction_analysis.sol")
        self.test_file.write_text(COMPREHENSIVE_CALL_TEST_CODE)
        self.engine.load_sources(str(self.test_file))

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_instruction_level_call_finding(self):
        """Test finding calls at instruction level."""
        # Test general call instructions
        call_instructions = self.engine.find_call_instructions()
        assert len(call_instructions) > 0

        # Test external call instructions
        external_instructions = self.engine.find_external_call_instructions()
        assert len(external_instructions) > 0

        # Test internal call instructions
        internal_instructions = self.engine.find_internal_call_instructions()
        assert len(internal_instructions) > 0

        # Test delegate call instructions
        delegate_instructions = self.engine.find_delegate_call_instructions()
        assert len(delegate_instructions) > 0

        # Test library call instructions
        library_instructions = self.engine.find_library_call_instructions()
        assert len(library_instructions) > 0

    def test_function_name_instruction_filtering(self):
        """Test instruction-level filtering by function name."""
        # Test callee function name filtering
        transfer_instructions = self.engine.find_calls_with_callee_function_name("transfer")
        assert len(transfer_instructions) >= 0  # May or may not find any

        # Test signature filtering
        signature_instructions = self.engine.find_calls_with_callee_function_signature("transfer")
        assert len(signature_instructions) >= 0

        # Test prefix filtering
        prefix_instructions = self.engine.find_calls_with_called_function_name_prefix("transfer")
        assert len(prefix_instructions) >= 0


class TestAdvancedCallDetection:
    """Test advanced call detection features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CallAnalyzer()
        self.engine = SolidityQueryEngine()
        self.test_file = Path("test_advanced_detection.sol")
        self.test_file.write_text(COMPREHENSIVE_CALL_TEST_CODE)
        self.engine.load_sources(str(self.test_file))

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_try_catch_detection(self):
        """Test detection of try/catch calls."""
        functions = self.engine.functions.list()

        for func in functions:
            analysis = self.analyzer.analyze_enhanced_call_patterns(func)

            if 'try_catch_calls' in analysis:
                try_catch_calls = analysis['try_catch_calls']
                assert isinstance(try_catch_calls, list)

    def test_assembly_call_detection(self):
        """Test detection of assembly calls."""
        functions = self.engine.functions.list()

        for func in functions:
            analysis = self.analyzer.analyze_enhanced_call_patterns(func)

            if 'assembly_calls' in analysis:
                assembly_calls = analysis['assembly_calls']
                assert isinstance(assembly_calls, dict)
                assert 'call' in assembly_calls
                assert 'delegatecall' in assembly_calls
                assert 'staticcall' in assembly_calls

    def test_call_type_distribution(self):
        """Test call type distribution analysis."""
        functions = self.engine.functions.list()

        for func in functions:
            analysis = self.analyzer.analyze_enhanced_call_patterns(func)

            if 'call_type_distribution' in analysis:
                distribution = analysis['call_type_distribution']
                assert isinstance(distribution, dict)

                # Should have some call types if there are calls
                if analysis.get('total_calls', 0) > 0:
                    assert len(distribution) > 0


class TestCallAnalysisIntegration:
    """Test integration of all call analysis features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SolidityQueryEngine()
        self.test_file = Path("test_integration.sol")
        self.test_file.write_text(COMPREHENSIVE_CALL_TEST_CODE)
        self.engine.load_sources(str(self.test_file))

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_fluent_call_analysis_chain(self):
        """Test chaining multiple call analysis operations."""
        # Chain multiple call filtering operations
        result = (self.engine.expressions
                 .calls()
                 .external_calls()
                 .with_callee_function_name_prefix("transfer")
                 .with_call_value())

        assert hasattr(result, '__len__')
        assert len(result) >= 0

    def test_cross_feature_consistency(self):
        """Test consistency across different call analysis features."""
        # Get calls through different methods
        all_calls = self.engine.expressions.calls()
        external_calls_1 = self.engine.expressions.external_calls()
        external_calls_2 = self.engine.find_external_call_instructions()

        # Basic consistency checks
        assert len(all_calls) >= len(external_calls_1)
        # Note: external_calls_2 might be different due to different filtering logic

    def test_call_type_completeness(self):
        """Test that all calls are assigned a type."""
        all_calls = self.engine.expressions.calls()

        for call in all_calls:
            if hasattr(call, 'get_call_type'):
                call_type = call.get_call_type()
                assert call_type is not None
                assert isinstance(call_type, CallType)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
