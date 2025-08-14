"""Tests for import analyzer and import-based filtering."""

import pytest
from pathlib import Path

from sol_query.query.engine import SolidityQueryEngine


class TestImportAnalyzer:
    """Test import analysis functionality."""

    @pytest.fixture
    def engine(self):
        """Set up engine with test fixtures."""
        engine = SolidityQueryEngine()
        fixtures_path = Path(__file__).parent / "fixtures" / "composition_and_imports"
        engine.load_sources(fixtures_path)
        return engine

    def test_find_imports_matching(self, engine):
        """Test finding imports by pattern matching."""
        analyzer = engine.import_analyzer()

        # Find OpenZeppelin imports
        oz_imports = analyzer.find_imports_matching("*openzeppelin*")
        assert len(oz_imports) > 0

        for import_stmt in oz_imports:
            assert "openzeppelin" in import_stmt.import_path.lower()

        # Find SafeMath imports
        safemath_imports = analyzer.find_imports_matching("*SafeMath*")
        assert len(safemath_imports) > 0

        for import_stmt in safemath_imports:
            assert "SafeMath" in import_stmt.import_path or "SafeMath" in import_stmt.imported_symbols

    def test_get_dependencies(self, engine):
        """Test getting dependencies for a specific contract."""
        analyzer = engine.import_analyzer()

        # Get dependencies for ERC721WithImports contract
        deps = analyzer.get_dependencies("ERC721WithImports")

        assert "direct_imports" in deps
        assert "imported_symbols" in deps
        assert "external_libraries" in deps
        assert "interfaces" in deps

        # Should have multiple imports
        assert len(deps["direct_imports"]) > 0
        assert len(deps["imported_symbols"]) > 0

    def test_find_usage_of_import(self, engine):
        """Test finding where imported symbols are used."""
        analyzer = engine.import_analyzer()

        # Find usage of SafeMath
        safemath_usage = analyzer.find_usage_of_import("*SafeMath*")

        assert len(safemath_usage) > 0

        # Verify usage locations contain expected information
        for usage in safemath_usage:
            assert "type" in usage
            assert usage["type"] in ["inheritance", "function_usage"]
            assert "symbol" in usage
            assert "location" in usage

    def test_analyze_external_dependencies(self, engine):
        """Test analyzing all external dependencies."""
        analyzer = engine.import_analyzer()

        deps = analyzer.analyze_external_dependencies()

        assert len(deps) > 0

        for dep_name, dep_info in deps.items():
            assert "import_count" in dep_info
            assert "importing_files" in dep_info
            assert "symbols" in dep_info
            assert "is_external" in dep_info
            assert "is_library" in dep_info
            assert "is_interface" in dep_info

    def test_get_import_graph(self, engine):
        """Test building import dependency graph."""
        analyzer = engine.import_analyzer()

        graph = analyzer.get_import_graph()

        assert len(graph) > 0

        # Each file should map to a list of its imports
        for file_path, imports in graph.items():
            assert isinstance(imports, list)

    def test_find_contracts_using_imports(self, engine):
        """Test finding contracts that use specific imports."""
        # Find contracts using OpenZeppelin imports
        oz_contracts = engine.find_contracts_using_imports(["*openzeppelin*"])
        assert len(oz_contracts) > 0

        # Find contracts using SafeMath
        safemath_contracts = engine.find_contracts_using_imports("*SafeMath*")
        assert len(safemath_contracts) > 0

    def test_find_functions_calling_imported(self, engine):
        """Test finding functions that call imported symbols."""
        # Find functions calling SafeMath functions
        safemath_funcs = engine.find_functions_calling_imported("*SafeMath*")

        # Should find functions that use .add, .sub, .mul, .div
        assert len(safemath_funcs) > 0

    def test_contract_collection_import_filters(self, engine):
        """Test import-based filtering on contract collections."""
        # Test using_imports filter
        oz_contracts = engine.contracts.using_imports(["*openzeppelin*"])
        assert len(oz_contracts) > 0

        # Test not_using_imports filter
        non_oz_contracts = engine.contracts.not_using_imports(["*openzeppelin*"])

        # Should be mutually exclusive
        oz_contract_names = {c.name for c in oz_contracts.list()}
        non_oz_contract_names = {c.name for c in non_oz_contracts.list()}

        assert len(oz_contract_names.intersection(non_oz_contract_names)) == 0

    def test_function_collection_import_filters(self, engine):
        """Test import-based filtering on function collections."""
        # Test calling_imported_symbols filter
        safemath_funcs = engine.functions.calling_imported_symbols(["*SafeMath*"])

        # Test not_calling_imported_symbols filter
        non_safemath_funcs = engine.functions.not_calling_imported_symbols(["*SafeMath*"])

        # Verify they're mutually exclusive
        safemath_func_names = {f.name for f in safemath_funcs.list()}
        non_safemath_func_names = {f.name for f in non_safemath_funcs.list()}

        # No overlap expected
        overlap = safemath_func_names.intersection(non_safemath_func_names)
        assert len(overlap) == 0

    def test_import_pattern_matching(self, engine):
        """Test various import pattern matching scenarios."""
        analyzer = engine.import_analyzer()

        # Test wildcard patterns
        wildcard_imports = analyzer.find_imports_matching("*contracts*")
        assert len(wildcard_imports) > 0

        # Test case insensitive matching
        case_imports = analyzer.find_imports_matching("*OPENZEPPELIN*")
        assert len(case_imports) > 0

        # Test specific file matching
        interface_imports = analyzer.find_imports_matching("*ILayerZeroReceiver*")
        assert len(interface_imports) > 0

    def test_import_analyzer_with_no_imports(self, engine):
        """Test import analyzer behavior with contracts that have no imports."""
        # SimpleContract should have no imports
        deps = engine.import_analyzer().get_dependencies("SimpleContract")

        assert deps["direct_imports"] == []
        assert deps["imported_symbols"] == []

    def test_library_and_interface_detection(self, engine):
        """Test detection of library vs interface imports."""
        analyzer = engine.import_analyzer()

        deps = analyzer.analyze_external_dependencies()

        # Should detect some libraries and interfaces
        libraries = [name for name, info in deps.items() if info["is_library"]]
        interfaces = [name for name, info in deps.items() if info["is_interface"]]

        assert len(libraries) > 0 or len(interfaces) > 0

    def test_composition_with_import_filters(self, engine):
        """Test combining import filters with other composition operators."""
        # Complex query: Find external functions in contracts using OpenZeppelin
        # that also have external calls but no reentrancy guards

        oz_contracts = engine.contracts.using_imports(["*openzeppelin*"])
        oz_functions = oz_contracts.get_functions()

        risky_functions = (oz_functions
                          .external()
                          .with_external_calls()
                          .and_not(lambda f: "nonReentrant" in f.modifiers))

        # Verify results
        for func in risky_functions.list():
            assert func.is_external()
            assert func.has_external_calls
            assert "nonReentrant" not in func.modifiers

            # Function's contract should use OpenZeppelin imports
            assert func.parent_contract in oz_contracts.list()

    def test_multiple_import_patterns(self, engine):
        """Test filtering with multiple import patterns."""
        # Find contracts using either OpenZeppelin OR SafeMath
        multi_pattern_contracts = engine.contracts.using_imports([
            "*openzeppelin*",
            "*SafeMath*"
        ])

        assert len(multi_pattern_contracts) > 0

        # Each contract should use at least one of the specified patterns
        analyzer = engine.import_analyzer()
        for contract in multi_pattern_contracts.list():
            deps = analyzer.get_dependencies(contract.name)
            import_paths = " ".join(deps["direct_imports"]).lower()
            symbols = " ".join(deps["imported_symbols"]).lower()

            has_oz = "openzeppelin" in import_paths
            has_safemath = "safemath" in (import_paths + symbols).lower()

            assert has_oz or has_safemath

    def test_import_statistics(self, engine):
        """Test getting import statistics and metadata."""
        analyzer = engine.import_analyzer()

        # Get all imports
        all_imports = engine.find_imports()
        assert len(all_imports) > 0

        # Get external dependencies analysis
        deps = analyzer.analyze_external_dependencies()

        # Count total external vs local imports
        external_count = sum(1 for info in deps.values() if info["is_external"])
        local_count = sum(1 for info in deps.values() if not info["is_external"])

        assert external_count + local_count == len(deps)

    def test_edge_cases_and_error_handling(self, engine):
        """Test edge cases and error handling."""
        analyzer = engine.import_analyzer()

        # Test with non-existent contract
        empty_deps = analyzer.get_dependencies("NonExistentContract")
        assert empty_deps["direct_imports"] == []

        # Test with pattern that should match nothing
        no_imports = analyzer.find_imports_matching("NonExistentLibrary123")
        assert len(no_imports) == 0

        # Test with pattern that matches nothing
        no_matches = analyzer.find_imports_matching("ThisShouldNotMatchAnything")
        assert len(no_matches) == 0
