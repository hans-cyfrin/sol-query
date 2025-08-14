"""Import dependency analysis for Solidity contracts."""

import re
from typing import List, Dict, Set, Optional, Any
from pathlib import Path

from sol_query.core.ast_nodes import ImportStatement, ContractDeclaration, FunctionDeclaration, ASTNode
from sol_query.core.source_manager import SourceManager


class ImportAnalyzer:
    """Analyzer for import dependencies and usage patterns."""

    def __init__(self, source_manager: SourceManager):
        """
        Initialize the import analyzer.
        
        Args:
            source_manager: Source manager containing parsed files
        """
        self.source_manager = source_manager

    def find_imports_matching(self, pattern: str) -> List[ImportStatement]:
        """
        Find import statements matching a pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards like *LayerZero*)
            
        Returns:
            List of matching import statements
        """
        matching_imports = []

        for source_file in self.source_manager.get_all_files():
            for import_stmt in source_file.imports:
                if import_stmt.matches_pattern(pattern):
                    matching_imports.append(import_stmt)

        return matching_imports

    def get_dependencies(self, contract_name: str) -> Dict[str, List[str]]:
        """
        Get all import dependencies for a specific contract.
        
        Args:
            contract_name: Name of the contract to analyze
            
        Returns:
            Dictionary mapping dependency types to lists of dependencies
        """
        dependencies = {
            "direct_imports": [],
            "imported_symbols": [],
            "external_libraries": [],
            "interfaces": []
        }

        # Find the contract
        contract = self._find_contract(contract_name)
        if not contract:
            return dependencies

        # Get imports from the same source file
        source_file = self._find_source_file_for_contract(contract)
        if not source_file:
            return dependencies

        for import_stmt in source_file.imports:
            dependencies["direct_imports"].append(import_stmt.import_path)
            dependencies["imported_symbols"].extend(import_stmt.get_imported_names())

            # Categorize imports
            if self._is_library_import(import_stmt):
                dependencies["external_libraries"].append(import_stmt.import_path)
            elif self._is_interface_import(import_stmt):
                dependencies["interfaces"].append(import_stmt.import_path)

        return dependencies

    def find_usage_of_import(self, import_pattern: str) -> List[Dict[str, Any]]:
        """
        Find where imported symbols are used in the codebase.
        
        Args:
            import_pattern: Pattern to match import names
            
        Returns:
            List of usage locations with context
        """
        usage_locations = []

        # Find matching imports first
        matching_imports = self.find_imports_matching(import_pattern)

        # Extract all symbol names from matching imports
        imported_symbols = set()
        for import_stmt in matching_imports:
            imported_symbols.update(import_stmt.get_imported_names())

        # Search for usage of these symbols in contracts and functions
        for contract in self.source_manager.get_contracts():
            # Check contract inheritance
            for inherited in contract.inheritance:
                if inherited in imported_symbols:
                    usage_locations.append({
                        "type": "inheritance",
                        "contract": contract.name,
                        "symbol": inherited,
                        "location": contract.source_location
                    })

            # Check function bodies for symbol usage
            for function in contract.functions:
                if function.body:
                    source_code = function.get_source_code()
                    for symbol in imported_symbols:
                        if self._symbol_used_in_code(symbol, source_code):
                            usage_locations.append({
                                "type": "function_usage",
                                "contract": contract.name,
                                "function": function.name,
                                "symbol": symbol,
                                "location": function.source_location
                            })

        return usage_locations

    def analyze_external_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze all external dependencies across the codebase.
        
        Returns:
            Dictionary mapping dependency names to analysis results
        """
        dependencies = {}

        for source_file in self.source_manager.get_all_files():
            for import_stmt in source_file.imports:
                dep_name = import_stmt.import_path

                if dep_name not in dependencies:
                    dependencies[dep_name] = {
                        "import_count": 0,
                        "importing_files": [],
                        "symbols": set(),
                        "is_external": self._is_external_dependency(import_stmt),
                        "is_library": self._is_library_import(import_stmt),
                        "is_interface": self._is_interface_import(import_stmt)
                    }

                dependencies[dep_name]["import_count"] += 1
                dependencies[dep_name]["importing_files"].append(source_file.path)
                dependencies[dep_name]["symbols"].update(import_stmt.get_imported_names())

        # Convert sets to lists for JSON serialization
        for dep_info in dependencies.values():
            dep_info["symbols"] = list(dep_info["symbols"])

        return dependencies

    def get_import_graph(self) -> Dict[str, List[str]]:
        """
        Build a dependency graph of imports.
        
        Returns:
            Dictionary mapping files to their direct dependencies
        """
        graph = {}

        for source_file in self.source_manager.get_all_files():
            file_path = str(source_file.path)
            graph[file_path] = []

            for import_stmt in source_file.imports:
                graph[file_path].append(import_stmt.import_path)

        return graph

    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies in the import graph.
        
        Returns:
            List of circular dependency chains
        """
        graph = self.get_import_graph()
        cycles = []

        def dfs(node: str, path: List[str], visited: Set[str]) -> None:
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, path.copy(), visited)

        for start_node in graph:
            dfs(start_node, [], set())

        return cycles

    def get_contracts_using_imports(self, import_patterns: List[str]) -> List[ContractDeclaration]:
        """
        Find contracts that use specific imports.
        
        Args:
            import_patterns: List of import patterns to match
            
        Returns:
            List of contracts using any of the specified imports
        """
        matching_contracts = []

        for contract in self.source_manager.get_contracts():
            source_file = self._find_source_file_for_contract(contract)
            if not source_file:
                continue

            # Check if this contract's file has matching imports
            for import_stmt in source_file.imports:
                for pattern in import_patterns:
                    if import_stmt.matches_pattern(pattern):
                        matching_contracts.append(contract)
                        break
                else:
                    continue
                break

        return matching_contracts

    def get_functions_calling_imported_symbols(self, import_patterns: List[str]) -> List[FunctionDeclaration]:
        """
        Find functions that call symbols from specific imports.
        
        Args:
            import_patterns: List of import patterns to match
            
        Returns:
            List of functions calling imported symbols
        """
        # Find all symbols from matching imports
        imported_symbols = set()
        for pattern in import_patterns:
            matching_imports = self.find_imports_matching(pattern)
            for import_stmt in matching_imports:
                imported_symbols.update(import_stmt.get_imported_names())

        matching_functions = []

        for contract in self.source_manager.get_contracts():
            for function in contract.functions:
                if function.body:
                    source_code = function.get_source_code()
                    # Check if function uses any imported symbols
                    for symbol in imported_symbols:
                        if self._symbol_used_in_code(symbol, source_code):
                            matching_functions.append(function)
                            break

        return matching_functions

    # Private helper methods

    def _find_contract(self, contract_name: str) -> Optional[ContractDeclaration]:
        """Find a contract by name."""
        for contract in self.source_manager.get_contracts():
            if contract.name == contract_name:
                return contract
        return None

    def _find_source_file_for_contract(self, contract: ContractDeclaration):
        """Find the source file containing a contract."""
        for source_file in self.source_manager.get_all_files():
            for file_contract in source_file.contracts:
                if file_contract.name == contract.name:
                    return source_file
        return None

    def _is_library_import(self, import_stmt: ImportStatement) -> bool:
        """Check if import is likely a library."""
        # Heuristics for library detection
        library_patterns = [
            "SafeMath", "OpenZeppelin", "solmate", "forge-std",
            "lib/", "@openzeppelin", "@chainlink"
        ]

        for pattern in library_patterns:
            if pattern.lower() in import_stmt.import_path.lower():
                return True

        return False

    def _is_interface_import(self, import_stmt: ImportStatement) -> bool:
        """Check if import is likely an interface."""
        # Check for interface naming patterns
        interface_patterns = ["interface", "Interface", "IERC", "I[A-Z]"]

        for pattern in interface_patterns:
            if re.search(pattern, import_stmt.import_path):
                return True

            for symbol in import_stmt.imported_symbols:
                if re.search(pattern, symbol):
                    return True

        return False

    def _is_external_dependency(self, import_stmt: ImportStatement) -> bool:
        """Check if import is an external dependency (not local file)."""
        # External dependencies typically don't start with './' or '../'
        return not (import_stmt.import_path.startswith('./') or
                   import_stmt.import_path.startswith('../'))

    def _symbol_used_in_code(self, symbol: str, code: str) -> bool:
        """Check if a symbol is used in code."""
        # Simple pattern matching for symbol usage
        # This could be enhanced with proper AST analysis
        pattern = rf'\b{re.escape(symbol)}\b'
        return bool(re.search(pattern, code))
