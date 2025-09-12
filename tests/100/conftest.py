"""
Shared test configuration for all 100-test files.
Provides common fixtures to avoid repetition across test files.

This conftest.py file implements DRY (Don't Repeat Yourself) principle by providing
shared fixtures that all test files can use instead of defining the same fixture
multiple times across different test files.
"""
import pytest
from sol_query.query.engine_v2 import SolidityQueryEngineV2


@pytest.fixture(scope="session")
def engine():
    """
    Session-scoped engine fixture shared across all test files.
    
    Initializes the SolidityQueryEngineV2 once per test session and loads
    all test fixtures. This is more efficient than creating a new engine
    for each test function since loading sources is expensive.
    
    The fixture loads:
    - tests/fixtures/composition_and_imports/ (contracts with imports/inheritance)
    - tests/fixtures/detailed_scenarios/ (complex real-world scenarios) 
    - tests/fixtures/sample_contract.sol (basic test contract)
    
    Returns:
        SolidityQueryEngineV2: Configured engine ready for testing
    """
    engine = SolidityQueryEngineV2()
    engine.load_sources([
        "tests/fixtures/composition_and_imports/",
        "tests/fixtures/detailed_scenarios/",
        "tests/fixtures/sample_contract.sol",
    ])
    return engine


@pytest.fixture(scope="function")
def fresh_engine():
    """
    Function-scoped engine fixture for tests that need a clean engine instance.
    Creates a new engine for each test function.
    """
    engine = SolidityQueryEngineV2()
    engine.load_sources([
        "tests/fixtures/composition_and_imports/",
        "tests/fixtures/detailed_scenarios/",
        "tests/fixtures/sample_contract.sol",
    ])
    return engine