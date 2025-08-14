"""Basic functionality tests for sol_query."""

import pytest
from pathlib import Path

from sol_query import SolidityQueryEngine
from sol_query.core.ast_nodes import ContractDeclaration, FunctionDeclaration


class TestBasicFunctionality:
    """Test basic query engine functionality."""
    
    @pytest.fixture
    def sample_contract_path(self):
        """Path to sample contract file."""
        return Path(__file__).parent / "fixtures" / "sample_contract.sol"
    
    @pytest.fixture
    def engine(self, sample_contract_path):
        """Query engine loaded with sample contract."""
        engine = SolidityQueryEngine()
        engine.load_sources(sample_contract_path)
        return engine
    
    def test_load_contract(self, engine):
        """Test loading a contract file."""
        stats = engine.get_statistics()
        assert stats["total_files"] > 0
        assert stats["total_contracts"] > 0
    
    def test_find_contracts_traditional(self, engine):
        """Test traditional contract finding."""
        # Find all contracts
        all_contracts = engine.find_contracts()
        assert len(all_contracts) >= 3  # Token, IERC20, SafeMath
        
        # Find specific contract
        token_contracts = engine.find_contracts(name_patterns="Token")
        assert len(token_contracts) == 1
        assert token_contracts[0].name == "Token"
        
        # Find by kind
        interfaces = engine.find_contracts(kind="interface")
        assert len(interfaces) >= 1
        
        libraries = engine.find_contracts(kind="library")
        assert len(libraries) >= 1
    
    def test_find_contracts_fluent(self, engine):
        """Test fluent contract finding."""
        # Get all contracts
        all_contracts = engine.contracts
        assert len(all_contracts) >= 3
        
        # Filter by name
        token_contracts = engine.contracts.with_name("Token")
        assert len(token_contracts) == 1
        
        # Get interfaces
        interfaces = engine.contracts.interfaces()
        assert len(interfaces) >= 1
        
        # Get libraries
        libraries = engine.contracts.libraries()
        assert len(libraries) >= 1
    
    def test_find_functions_traditional(self, engine):
        """Test traditional function finding."""
        # Find all functions
        all_functions = engine.find_functions()
        assert len(all_functions) > 0
        
        # Find public functions
        public_functions = engine.find_functions(visibility="public")
        assert len(public_functions) > 0
        
        # Find functions by name
        transfer_functions = engine.find_functions(name_patterns="transfer*")
        assert len(transfer_functions) >= 2  # transfer, transferFrom, transferOwnership
        
        # Find view functions
        view_functions = engine.find_functions(state_mutability="view")
        assert len(view_functions) > 0
    
    def test_find_functions_fluent(self, engine):
        """Test fluent function finding."""
        # Get all functions
        all_functions = engine.functions
        assert len(all_functions) > 0
        
        # Get public functions
        public_functions = engine.functions.public()
        assert len(public_functions) > 0
        
        # Get external functions
        external_functions = engine.functions.external()
        assert len(external_functions) > 0
        
        # Get view functions
        view_functions = engine.functions.view()
        assert len(view_functions) > 0
        
        # Get constructors
        constructors = engine.functions.constructors()
        assert len(constructors) >= 1
        
        # Chain filters
        public_view = engine.functions.public().view()
        assert len(public_view) > 0
    
    def test_find_variables(self, engine):
        """Test variable finding."""
        # Find all variables
        all_variables = engine.find_variables()
        assert len(all_variables) > 0
        
        # Find private variables
        private_vars = engine.find_variables(visibility="private")
        assert len(private_vars) > 0
        
        # Find by type
        uint256_vars = engine.find_variables(type_patterns="uint256")
        assert len(uint256_vars) > 0
        
        # Find mapping variables
        mapping_vars = engine.find_variables(type_patterns="mapping*")
        assert len(mapping_vars) >= 2
    
    def test_contract_navigation(self, engine):
        """Test navigation from contracts to their elements."""
        token_contract = engine.contracts.with_name("Token").first()
        assert isinstance(token_contract, ContractDeclaration)
        
        # Get functions from contract
        functions = engine.contracts.with_name("Token").get_functions()
        assert len(functions) > 0
        
        # Get variables from contract
        variables = engine.contracts.with_name("Token").get_variables()
        assert len(variables) > 0
        
        # Get events from contract
        events = engine.contracts.with_name("Token").get_events()
        assert len(events) >= 3  # Transfer, Approval, OwnershipTransferred
    
    def test_query_statistics(self, engine):
        """Test query statistics."""
        stats = engine.get_statistics()
        
        assert "total_files" in stats
        assert "total_contracts" in stats
        assert "total_functions" in stats
        assert "contracts_by_type" in stats
        
        assert stats["total_contracts"] >= 3
        assert stats["total_functions"] > 0
        
        # Check contract types
        contract_types = stats["contracts_by_type"]
        assert contract_types["contract"] >= 1
        assert contract_types["interface"] >= 1
        assert contract_types["library"] >= 1
    
    def test_serialization(self, engine):
        """Test JSON serialization."""
        # Get a contract and serialize it
        token_contract = engine.contracts.with_name("Token").first()
        serialized = token_contract.to_dict()
        
        assert isinstance(serialized, dict)
        assert "name" in serialized
        assert "kind" in serialized
        assert serialized["name"] == "Token"
        
        # Test collection serialization
        all_contracts = engine.contracts
        collection_dict = all_contracts.to_dict()
        
        assert isinstance(collection_dict, list)
        assert len(collection_dict) >= 3
    
    def test_pattern_matching(self, engine):
        """Test various pattern matching capabilities."""
        # Wildcard patterns
        transfer_funcs = engine.functions.with_name("transfer*")
        assert len(transfer_funcs) >= 2
        
        # Exact matching - should find both interface declaration and implementation
        exact_transfer = engine.functions.with_name("transfer")
        assert len(exact_transfer) == 2  # One in interface, one in contract
        assert all(f.name == "transfer" for f in exact_transfer)
        
        # Multiple patterns
        multiple_patterns = engine.functions.with_name(["transfer", "approve"])
        assert len(multiple_patterns) >= 2
    
    def test_modifiers_and_visibility(self, engine):
        """Test modifier and visibility filtering."""
        # Find functions with specific modifiers
        only_owner_funcs = engine.functions.with_modifiers("onlyOwner")
        assert len(only_owner_funcs) >= 2
        
        # Find functions with validAddress modifier
        valid_address_funcs = engine.functions.with_modifiers("validAddress")
        assert len(valid_address_funcs) >= 3
        
        # Test override keyword detection
        override_funcs = [f for f in engine.functions if f.is_override]
        assert len(override_funcs) >= 5  # ERC20 interface implementations


@pytest.mark.skip(reason="Advanced features not yet implemented")
class TestAdvancedFeatures:
    """Test advanced query features."""
    
    def test_call_graph_analysis(self, engine):
        """Test call graph analysis (placeholder)."""
        # This would test call relationship analysis
        pass
    
    def test_data_flow_analysis(self, engine):
        """Test data flow analysis (placeholder)."""
        # This would test data flow tracing
        pass
    
    def test_reference_tracking(self, engine):
        """Test reference tracking (placeholder)."""
        # This would test finding all references to symbols
        pass