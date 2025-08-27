"""Test that previously missing node types are now properly handled."""

import pytest
from sol_query import SolidityQueryEngine
from sol_query.core.ast_nodes import NodeType


class TestMissingNodeTypes:
    """Test that previously unsupported node types are now handled."""

    def test_pragma_directive_parsing(self):
        """Test that pragma directives are properly parsed."""
        source_code = """
        pragma solidity ^0.8.0;
        
        contract TestContract {
            function test() public {}
        }
        """

        # Create a temporary file with the source code
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(source_code)
            temp_file = f.name

        try:
            engine = SolidityQueryEngine()
            engine.load_sources(temp_file)

            # Should find pragma directive
            pragma_nodes = engine.find_pragmas()
            assert len(pragma_nodes) > 0, "Should find pragma directive"

            pragma = pragma_nodes[0]
            assert pragma.pragma_type == "solidity"
            assert pragma.pragma_value == "^0.8.0"

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_emit_statement_parsing(self):
        """Test that emit statements are properly parsed."""
        source_code = """
        pragma solidity ^0.8.0;
        
        contract TestContract {
            event TestEvent(uint256 value);
            
            function test() public {
                emit TestEvent(42);
            }
        }
        """

        # Create a temporary file with the source code
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(source_code)
            temp_file = f.name

        try:
            engine = SolidityQueryEngine()
            engine.load_sources(temp_file)

            # Should find emit statement
            emit_nodes = engine.find_statements(statement_types=["emit_statement"])
            assert len(emit_nodes) > 0, "Should find emit statements"

            # Check that emit statement is parsed
            contract = engine.find_contracts(name_patterns="TestContract")[0]
            functions = contract.functions
            assert len(functions) > 0, "Should find functions"

            function = functions[0]
            assert function.name == "test"

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_struct_parsing(self):
        """Test that struct declarations and members are properly parsed."""
        source_code = """
        pragma solidity ^0.8.0;
        
        contract TestContract {
            struct TestStruct {
                uint256 value;
                string name;
                bool active;
            }
            
            TestStruct public testStruct;
        }
        """

        # Create a temporary file with the source code
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(source_code)
            temp_file = f.name

        try:
            engine = SolidityQueryEngine()
            engine.load_sources(temp_file)

            # Should find struct declaration
            contract = engine.find_contracts(name_patterns="TestContract")[0]
            structs = contract.structs
            assert len(structs) > 0, "Should find structs"

            struct = structs[0]
            assert struct.name == "TestStruct"
            assert len(struct.fields) > 0, "Should find struct fields"

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_comment_handling(self):
        """Test that comments are handled gracefully."""
        source_code = """
        // This is a comment
        pragma solidity ^0.8.0;
        
        contract TestContract {
            // Another comment
            function test() public {
                // Function comment
                uint256 value = 42; // Inline comment
            }
        }
        """

        # Create a temporary file with the source code
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(source_code)
            temp_file = f.name

        try:
            engine = SolidityQueryEngine()
            engine.load_sources(temp_file)

            # Should parse without errors
            contracts = engine.find_contracts()
            assert len(contracts) > 0, "Should parse contract with comments"

            contract = contracts[0]
            assert contract.name == "TestContract"

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_punctuation_handling(self):
        """Test that punctuation and syntax elements are handled gracefully."""
        source_code = """
        pragma solidity ^0.8.0;
        
        contract TestContract {
            uint256[10] public array;
            mapping(address => uint256) public balances;
            
            function test() public {
                if (true) {
                    // Do something
                }
            }
        }
        """

        # Create a temporary file with the source code
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(source_code)
            temp_file = f.name

        try:
            engine = SolidityQueryEngine()
            engine.load_sources(temp_file)

            # Should parse without errors
            contracts = engine.find_contracts()
            assert len(contracts) > 0, "Should parse contract with various syntax elements"

            contract = contracts[0]
            assert contract.name == "TestContract"

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_comprehensive_parsing(self):
        """Test comprehensive parsing with all previously missing node types."""
        source_code = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;
        
        import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
        
        contract TestContract is ERC20 {
            // Struct definition
            struct UserInfo {
                uint256 balance;
                uint256 lastUpdate;
                bool isActive;
            }
            
            // Events
            event UserRegistered(address indexed user, uint256 timestamp);
            event BalanceUpdated(address indexed user, uint256 oldBalance, uint256 newBalance);
            
            // State variables
            mapping(address => UserInfo) public userInfo;
            uint256 public totalUsers;
            
            constructor() ERC20("Test", "TST") {}
            
            function registerUser() public {
                require(!userInfo[msg.sender].isActive, "User already registered");
                
                userInfo[msg.sender] = UserInfo({
                    balance: 0,
                    lastUpdate: block.timestamp,
                    isActive: true
                });
                
                totalUsers++;
                emit UserRegistered(msg.sender, block.timestamp);
            }
            
            function updateBalance(address user, uint256 newBalance) public {
                require(userInfo[user].isActive, "User not registered");
                
                uint256 oldBalance = userInfo[user].balance;
                userInfo[user].balance = newBalance;
                userInfo[user].lastUpdate = block.timestamp;
                
                emit BalanceUpdated(user, oldBalance, newBalance);
            }
        }
        """

        # Create a temporary file with the source code
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(source_code)
            temp_file = f.name

        try:
            engine = SolidityQueryEngine()
            engine.load_sources(temp_file)

            # Should parse without errors
            contracts = engine.find_contracts()
            assert len(contracts) > 0, "Should parse comprehensive contract"

            # Check for pragma directive
            pragma_nodes = engine.find_pragmas()
            assert len(pragma_nodes) > 0, "Should find pragma directive"

            # Check for import
            import_nodes = engine.find_imports()
            assert len(import_nodes) > 0, "Should find import statement"

            # Check for contract
            contract_nodes = engine.find_contracts()
            assert len(contract_nodes) > 0, "Should find contract"

            contract = contract_nodes[0]
            assert contract.name == "TestContract"
            assert len(contract.functions) > 0, "Should find functions"
            assert len(contract.structs) > 0, "Should find structs"
            assert len(contract.events) > 0, "Should find events"

        finally:
            # Clean up temporary file
            os.unlink(temp_file)
