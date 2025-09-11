"""
SolidityQueryEngineV2: LLM-friendly code query API with 3 core functions.

Implements the exact API specification from new-code-query-api-requirements.md
"""

import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sol_query.core.source_manager import SourceManager
from sol_query.core.ast_nodes import (
    ASTNode, ContractDeclaration, FunctionDeclaration, VariableDeclaration,
    ModifierDeclaration, EventDeclaration, ErrorDeclaration, StructDeclaration,
    EnumDeclaration, Statement, Expression, Visibility, StateMutability
)
from sol_query.utils.pattern_matching import PatternMatcher
from unittest.mock import Mock


class SolidityQueryEngineV2:
    """
    LLM-friendly Solidity query engine implementing 3 core functions:
    1. query_code() - Universal query function
    2. get_details() - Detailed element analysis  
    3. find_references() - Reference and relationship analysis
    """

    def __init__(self, source_paths: Optional[Union[str, Path, List[Union[str, Path]]]] = None):
        """Initialize the V2 query engine."""
        self.source_manager = SourceManager()
        self.pattern_matcher = PatternMatcher()

        if source_paths:
            self.load_sources(source_paths)

    def _get_all_nodes(self) -> List[ASTNode]:
        """Get all AST nodes from all source files."""
        all_nodes = []

        # Get contracts (these are available directly)
        contracts = self.source_manager.get_contracts()
        all_nodes.extend(contracts)

        # Extract nested elements from contracts
        for contract in contracts:
            # Add functions from contract
            if hasattr(contract, 'functions'):
                all_nodes.extend(contract.functions)

            # Add variables from contract
            if hasattr(contract, 'variables'):
                all_nodes.extend(contract.variables)

            # Add events from contract
            if hasattr(contract, 'events'):
                all_nodes.extend(contract.events)

            # Add modifiers from contract
            if hasattr(contract, 'modifiers'):
                all_nodes.extend(contract.modifiers)

            # Add errors from contract
            if hasattr(contract, 'errors'):
                all_nodes.extend(contract.errors)

            # Add structs from contract
            if hasattr(contract, 'structs'):
                all_nodes.extend(contract.structs)

            # Add enums from contract
            if hasattr(contract, 'enums'):
                all_nodes.extend(contract.enums)

        # Get all other nodes from each source file's AST
        for source_file in self.source_manager.get_all_files():
            if source_file.ast:
                all_nodes.extend(source_file.ast)

        return all_nodes

    def load_sources(self, source_paths: Union[str, Path, List[Union[str, Path]]]) -> None:
        """Load source files or directories."""
        if isinstance(source_paths, (str, Path)):
            source_paths = [source_paths]

        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                self.source_manager.add_file(path)
            elif path.is_dir():
                self.source_manager.add_directory(path, recursive=True)

    def query_code(self,
                   query_type: str,
                   filters: Dict[str, Any] = {},
                   scope: Dict[str, Any] = {},
                   include: List[str] = [],
                   options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Universal query function for searching and analyzing code elements.
        
        Args:
            query_type: Type of elements to query (functions, contracts, variables, etc.)
            filters: Flexible filter criteria organized by category
            scope: Scope constraints to limit search area  
            include: Additional data to include in results
            options: Analysis and output options
            
        Returns:
            Standardized response dictionary with query results
        """
        start_time = time.time()

        try:
            # Validate parameters
            validation_errors = self._validate_query_code_params(query_type, filters, scope, include, options)
            if validation_errors:
                return self._create_error_response("query_code", {
                    "query_type": query_type,
                    "filters": filters,
                    "scope": scope,
                    "include": include,
                    "options": options
                }, validation_errors)

            # Get base nodes
            nodes = self._get_nodes_by_query_type(query_type)

            # Apply scope constraints
            if scope:
                nodes = self._apply_scope_filters(nodes, scope)

            # Apply filters
            if filters:
                nodes = self._apply_query_filters(nodes, filters, query_type)

            # Apply options (max_results, etc.)
            max_results = options.get("max_results", None)
            if max_results and len(nodes) > max_results:
                nodes = nodes[:max_results]

            # Build result data
            result_data = self._build_query_result_data(nodes, include, options)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "query_info": {
                    "function": "query_code",
                    "parameters": {
                        "query_type": query_type,
                        "filters": filters,
                        "scope": scope,
                        "include": include,
                        "options": options
                    },
                    "execution_time": execution_time,
                    "result_count": len(nodes),
                    "cache_hit": False
                },
                "data": result_data,
                "metadata": {
                    "analysis_scope": self._get_analysis_scope(scope),
                    "filters_applied": filters,
                    "performance": {
                        "nodes_analyzed": len(self._get_all_nodes()),
                        "files_processed": len(self.source_manager.files),
                        "memory_usage": "N/A"
                    },
                    "suggestions": self._get_query_suggestions(query_type, filters),
                    "related_queries": self._get_related_queries(query_type, filters)
                },
                "warnings": [],
                "errors": []
            }

        except Exception as e:
            return self._create_error_response("query_code", {
                "query_type": query_type,
                "filters": filters,
                "scope": scope,
                "include": include,
                "options": options
            }, [f"Internal error: {str(e)}"])

    def get_details(self,
                    element_type: str,
                    identifiers: List[str],
                    analysis_depth: str = "basic",
                    include_context: bool = True,
                    options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Get comprehensive details about specific code elements.
        
        Args:
            element_type: Type of element (function, contract, variable, etc.)
            identifiers: Element identifiers to analyze
            analysis_depth: Analysis depth level (basic, detailed, comprehensive)
            include_context: Whether to include surrounding context
            options: Additional analysis options
            
        Returns:
            Detailed analysis results for specified elements
        """
        start_time = time.time()

        try:
            # Validate parameters
            validation_errors = self._validate_get_details_params(element_type, identifiers, analysis_depth, options)
            if validation_errors:
                return self._create_error_response("get_details", {
                    "element_type": element_type,
                    "identifiers": identifiers,
                    "analysis_depth": analysis_depth,
                    "include_context": include_context,
                    "options": options
                }, validation_errors)

            # Find elements by identifiers
            elements = self._find_elements_by_identifiers(element_type, identifiers)

            # Perform analysis based on depth
            analysis_results = {}
            for identifier in identifiers:
                element = elements.get(identifier)
                if element:
                    analysis_results[identifier] = self._analyze_element(
                        element, analysis_depth, include_context, options
                    )
                else:
                    analysis_results[identifier] = {
                        "found": False,
                        "error": f"Element '{identifier}' of type '{element_type}' not found"
                    }

            execution_time = time.time() - start_time

            return {
                "success": True,
                "query_info": {
                    "function": "get_details",
                    "parameters": {
                        "element_type": element_type,
                        "identifiers": identifiers,
                        "analysis_depth": analysis_depth,
                        "include_context": include_context,
                        "options": options
                    },
                    "execution_time": execution_time,
                    "result_count": len([r for r in analysis_results.values() if r.get("found", True)]),
                    "cache_hit": False
                },
                "data": {
                    "elements": analysis_results,
                    "analysis_summary": self._create_analysis_summary(analysis_results, analysis_depth)
                },
                "metadata": {
                    "analysis_scope": {"element_type": element_type, "identifiers": identifiers},
                    "analysis_depth": analysis_depth,
                    "performance": {
                        "elements_analyzed": len(identifiers),
                        "files_processed": len(self.source_manager.files),
                        "memory_usage": "N/A"
                    }
                },
                "warnings": [],
                "errors": []
            }

        except Exception as e:
            return self._create_error_response("get_details", {
                "element_type": element_type,
                "identifiers": identifiers,
                "analysis_depth": analysis_depth,
                "include_context": include_context,
                "options": options
            }, [f"Internal error: {str(e)}"])

    def find_references(self,
                       target: str,
                       target_type: str,
                       reference_type: str = "all",
                       direction: str = "both",
                       max_depth: int = 5,
                       filters: Dict[str, Any] = {},
                       options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Analyze relationships, references, and dependencies between code elements.
        
        Args:
            target: Target element to analyze
            target_type: Type of target element
            reference_type: Type of references to find (all, usages, definitions)
            direction: Analysis direction (forward, backward, both)
            max_depth: Maximum search depth
            filters: Additional filters for found references
            options: Analysis options
            
        Returns:
            Reference and relationship analysis results
        """
        start_time = time.time()

        try:
            # Validate parameters
            validation_errors = self._validate_find_references_params(
                target, target_type, reference_type, direction, max_depth, filters, options
            )
            if validation_errors:
                return self._create_error_response("find_references", {
                    "target": target,
                    "target_type": target_type,
                    "reference_type": reference_type,
                    "direction": direction,
                    "max_depth": max_depth,
                    "filters": filters,
                    "options": options
                }, validation_errors)

            # Find the target element
            target_element = self._find_target_element(target, target_type)
            if not target_element:
                return self._create_error_response("find_references", {
                    "target": target,
                    "target_type": target_type
                }, [f"Target element '{target}' of type '{target_type}' not found"])

            # Find references based on type and direction
            references = self._find_element_references(
                target_element, target_type, reference_type, direction, max_depth, filters, options
            )

            execution_time = time.time() - start_time

            return {
                "success": True,
                "query_info": {
                    "function": "find_references",
                    "parameters": {
                        "target": target,
                        "target_type": target_type,
                        "reference_type": reference_type,
                        "direction": direction,
                        "max_depth": max_depth,
                        "filters": filters,
                        "options": options
                    },
                    "execution_time": execution_time,
                    "result_count": len(references.get("references", [])),
                    "cache_hit": False
                },
                "data": {
                    "target_info": self._get_target_info(target_element, target_type),
                    "references": references
                },
                "metadata": {
                    "analysis_scope": {
                        "target": target,
                        "target_type": target_type,
                        "max_depth": max_depth,
                        "direction": direction
                    },
                    "filters_applied": filters,
                    "performance": {
                        "references_found": len(references.get("references", [])),
                        "depth_reached": references.get("max_depth_reached", 0),
                        "files_analyzed": len(self.source_manager.files)
                    }
                },
                "warnings": [],
                "errors": []
            }

        except Exception as e:
            return self._create_error_response("find_references", {
                "target": target,
                "target_type": target_type
            }, [f"Internal error: {str(e)}"])

    # Private helper methods

    def _validate_query_code_params(self, query_type: str, filters: Dict[str, Any],
                                   scope: Dict[str, Any], include: List[str],
                                   options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate query_code parameters."""
        errors = []

        # Validate query_type
        valid_query_types = [
            "functions", "contracts", "variables", "calls", "flow", "statements",
            "expressions", "events", "modifiers", "errors", "structs", "enums"
        ]
        if query_type not in valid_query_types:
            errors.append({
                "parameter": "query_type",
                "error": f"Invalid query_type '{query_type}'",
                "suggestion": "Use one of the supported query types",
                "valid_values": valid_query_types
            })

        # Validate filters based on query_type
        if filters:
            filter_errors = self._validate_filters(filters, query_type)
            errors.extend(filter_errors)

        return errors

    def _validate_get_details_params(self, element_type: str, identifiers: List[str],
                                   analysis_depth: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate get_details parameters."""
        errors = []

        # Validate element_type
        valid_element_types = ["function", "contract", "variable", "modifier", "event", "error", "struct", "enum"]
        if element_type not in valid_element_types:
            errors.append({
                "parameter": "element_type",
                "error": f"Invalid element_type '{element_type}'",
                "valid_values": valid_element_types
            })

        # Validate analysis_depth
        valid_depths = ["basic", "detailed", "comprehensive"]
        if analysis_depth not in valid_depths:
            errors.append({
                "parameter": "analysis_depth",
                "error": f"Invalid analysis_depth '{analysis_depth}'",
                "valid_values": valid_depths
            })

        # Validate identifiers
        if not identifiers:
            errors.append({
                "parameter": "identifiers",
                "error": "identifiers list cannot be empty"
            })

        return errors

    def _validate_find_references_params(self, target: str, target_type: str, reference_type: str,
                                       direction: str, max_depth: int, filters: Dict[str, Any],
                                       options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate find_references parameters."""
        errors = []

        # Validate target_type
        valid_target_types = ["function", "variable", "contract", "modifier", "event", "struct", "enum"]
        if target_type not in valid_target_types:
            errors.append({
                "parameter": "target_type",
                "error": f"Invalid target_type '{target_type}'",
                "valid_values": valid_target_types
            })

        # Validate reference_type
        valid_reference_types = ["all", "usages", "definitions"]
        if reference_type not in valid_reference_types:
            errors.append({
                "parameter": "reference_type",
                "error": f"Invalid reference_type '{reference_type}'",
                "valid_values": valid_reference_types
            })

        # Validate direction
        valid_directions = ["forward", "backward", "both"]
        if direction not in valid_directions:
            errors.append({
                "parameter": "direction",
                "error": f"Invalid direction '{direction}'",
                "valid_values": valid_directions
            })

        # Validate max_depth
        if max_depth < -1 or max_depth == 0:
            errors.append({
                "parameter": "max_depth",
                "error": "max_depth must be positive or -1 for unlimited"
            })

        return errors

    def _validate_filters(self, filters: Dict[str, Any], query_type: str) -> List[Dict[str, Any]]:
        """Validate filter parameters based on query type."""
        errors = []

        for filter_name, filter_value in filters.items():
            # Validate visibility filters
            if filter_name == "visibility":
                valid_visibility = ["public", "external", "internal", "private"]
                if isinstance(filter_value, list):
                    invalid_values = [v for v in filter_value if v not in valid_visibility]
                    if invalid_values:
                        errors.append({
                            "parameter": f"filters.{filter_name}",
                            "error": f"Invalid visibility values: {invalid_values}",
                            "valid_values": valid_visibility
                        })
                elif filter_value not in valid_visibility:
                    errors.append({
                        "parameter": f"filters.{filter_name}",
                        "error": f"Invalid visibility '{filter_value}'",
                        "valid_values": valid_visibility
                    })

            # Validate state_mutability filters
            elif filter_name == "state_mutability":
                valid_mutability = ["view", "pure", "payable", "nonpayable"]
                if isinstance(filter_value, list):
                    invalid_values = [v for v in filter_value if v not in valid_mutability]
                    if invalid_values:
                        errors.append({
                            "parameter": f"filters.{filter_name}",
                            "error": f"Invalid state_mutability values: {invalid_values}",
                            "valid_values": valid_mutability
                        })
                elif filter_value not in valid_mutability:
                    errors.append({
                        "parameter": f"filters.{filter_name}",
                        "error": f"Invalid state_mutability '{filter_value}'",
                        "valid_values": valid_mutability
                    })

        return errors

    def _get_nodes_by_query_type(self, query_type: str) -> List[ASTNode]:
        """Get nodes by query type."""
        all_nodes = self._get_all_nodes()

        if query_type == "contracts":
            return self.source_manager.get_contracts()
        elif query_type == "functions":
            return [node for node in all_nodes if isinstance(node, FunctionDeclaration)]
        elif query_type == "variables":
            return [node for node in all_nodes if isinstance(node, VariableDeclaration)]
        elif query_type == "modifiers":
            return [node for node in all_nodes if isinstance(node, ModifierDeclaration)]
        elif query_type == "events":
            return [node for node in all_nodes if isinstance(node, EventDeclaration)]
        elif query_type == "errors":
            return [node for node in all_nodes if isinstance(node, ErrorDeclaration)]
        elif query_type == "structs":
            return [node for node in all_nodes if isinstance(node, StructDeclaration)]
        elif query_type == "enums":
            return [node for node in all_nodes if isinstance(node, EnumDeclaration)]
        elif query_type == "statements":
            return [node for node in all_nodes if isinstance(node, Statement)]
        elif query_type == "expressions":
            return [node for node in all_nodes if isinstance(node, Expression)]
        elif query_type == "calls":
            # Extract calls from function bodies - simplified approach
            calls = []
            functions = [node for node in all_nodes if isinstance(node, FunctionDeclaration)]
            for func in functions:
                if hasattr(func, 'source_code') and func.source_code:
                    # Create mock call nodes for detected calls
                    call_patterns = [r'\w+\s*\(', r'\w+\.\w+\s*\(']
                    for pattern in call_patterns:
                        matches = re.finditer(pattern, func.source_code)
                        for match in matches:
                            # Create a mock call node
                            call_node = Mock()
                            call_node.source_code = match.group(0)
                            call_node.name = match.group(0).split('(')[0]
                            calls.append(call_node)
            return calls
        else:
            return []

    def _apply_scope_filters(self, nodes: List[ASTNode], scope: Dict[str, Any]) -> List[ASTNode]:
        """Apply scope constraints to filter nodes."""
        filtered = nodes

        # Filter by contracts
        if "contracts" in scope:
            contract_names = scope["contracts"]
            filtered = [n for n in filtered if self._node_in_contracts(n, contract_names)]

        # Filter by functions
        if "functions" in scope:
            function_names = scope["functions"]
            filtered = [n for n in filtered if self._node_in_functions(n, function_names)]

        # Filter by files
        if "files" in scope:
            file_patterns = scope["files"]
            filtered = [n for n in filtered if self._node_in_files(n, file_patterns)]

        # Filter by directories
        if "directories" in scope:
            dir_patterns = scope["directories"]
            filtered = [n for n in filtered if self._node_in_directories(n, dir_patterns)]

        # Filter by inheritance tree
        if "inheritance_tree" in scope:
            base_contract = scope["inheritance_tree"]
            filtered = [n for n in filtered if self._node_in_inheritance_tree(n, base_contract)]

        return filtered

    def _apply_query_filters(self, nodes: List[ASTNode], filters: Dict[str, Any], query_type: str) -> List[ASTNode]:
        """Apply all query filters to nodes."""
        filtered = nodes

        for filter_name, filter_value in filters.items():
            filtered = self._apply_single_query_filter(filtered, filter_name, filter_value, query_type)

        return filtered

    def _apply_single_query_filter(self, nodes: List[ASTNode], filter_name: str,
                                 filter_value: Any, query_type: str) -> List[ASTNode]:
        """Apply a single filter to nodes."""

        # Name filters
        if filter_name == "names":
            return self._filter_by_names(nodes, filter_value)

        # Visibility filters
        elif filter_name == "visibility":
            return self._filter_by_visibility(nodes, filter_value)

        # State mutability filters
        elif filter_name == "state_mutability":
            return self._filter_by_state_mutability(nodes, filter_value)

        # Modifier filters
        elif filter_name == "modifiers":
            return self._filter_by_modifiers(nodes, filter_value)

        # Contract filters
        elif filter_name == "contracts":
            return self._filter_by_contract_names(nodes, filter_value)

        # Boolean filters for functions
        elif filter_name == "has_external_calls":
            return self._filter_by_external_calls(nodes, filter_value)

        elif filter_name == "has_asset_transfers":
            return self._filter_by_asset_transfers(nodes, filter_value)

        elif filter_name == "changes_state":
            return self._filter_by_state_changes(nodes, filter_value)

        elif filter_name == "is_payable":
            return self._filter_by_payable(nodes, filter_value)

        # Variable type filters
        elif filter_name == "types":
            return self._filter_by_types(nodes, filter_value)

        elif filter_name == "is_state_variable":
            return self._filter_by_state_variable(nodes, filter_value)

        # Statement filters
        elif filter_name == "statement_types":
            return self._filter_by_statement_types(nodes, filter_value)

        # Expression filters
        elif filter_name == "operators":
            return self._filter_by_operators(nodes, filter_value)

        elif filter_name == "access_patterns":
            return self._filter_by_access_patterns(nodes, filter_value)

        # Call filters
        elif filter_name == "call_types":
            return self._filter_by_call_types(nodes, filter_value)

        elif filter_name == "low_level":
            return self._filter_by_low_level_calls(nodes, filter_value)

        return nodes

    def _filter_by_names(self, nodes: List[ASTNode], name_patterns: Union[str, List[str]]) -> List[ASTNode]:
        """Filter nodes by name patterns."""
        if isinstance(name_patterns, str):
            name_patterns = [name_patterns]

        filtered = []
        for node in nodes:
            if hasattr(node, 'name') and node.name:
                for pattern in name_patterns:
                    if self._matches_pattern(node.name, pattern):
                        filtered.append(node)
                        break
        return filtered

    def _filter_by_visibility(self, nodes: List[ASTNode], visibility_values: Union[str, List[str]]) -> List[ASTNode]:
        """Filter nodes by visibility."""
        if isinstance(visibility_values, str):
            visibility_values = [visibility_values]

        return [n for n in nodes if hasattr(n, 'visibility') and str(n.visibility).lower() in
                [v.lower() for v in visibility_values]]

    def _filter_by_state_mutability(self, nodes: List[ASTNode], mutability_values: Union[str, List[str]]) -> List[ASTNode]:
        """Filter nodes by state mutability."""
        if isinstance(mutability_values, str):
            mutability_values = [mutability_values]

        return [n for n in nodes if hasattr(n, 'state_mutability') and str(n.state_mutability).lower() in
                [m.lower() for m in mutability_values]]

    def _filter_by_modifiers(self, nodes: List[ASTNode], modifier_patterns: Union[str, List[str]]) -> List[ASTNode]:
        """Filter nodes by modifier patterns."""
        if isinstance(modifier_patterns, str):
            modifier_patterns = [modifier_patterns]

        # Empty list means no modifiers
        if not modifier_patterns:
            return [n for n in nodes if not hasattr(n, 'modifiers') or not n.modifiers]

        filtered = []
        for node in nodes:
            if hasattr(node, 'modifiers') and node.modifiers:
                for pattern in modifier_patterns:
                    if any(self._matches_pattern(str(mod), pattern) for mod in node.modifiers):
                        filtered.append(node)
                        break
        return filtered

    def _filter_by_external_calls(self, nodes: List[ASTNode], has_calls: bool) -> List[ASTNode]:
        """Filter functions that have external calls."""
        if not has_calls:
            return nodes

        filtered = []
        for node in nodes:
            if self._has_external_calls(node):
                filtered.append(node)
        return filtered

    def _has_external_calls(self, node: ASTNode) -> bool:
        """Check if a node contains external calls."""
        if not hasattr(node, 'source_code') or not node.source_code:
            return False

        source = node.source_code

        # Low-level calls
        low_level_patterns = [
            r'\.call\s*\(',
            r'\.delegatecall\s*\(',
            r'\.staticcall\s*\(',
            r'\.send\s*\(',
            r'\.transfer\s*\('
        ]

        for pattern in low_level_patterns:
            if re.search(pattern, source):
                return True

        # Interface calls (pattern: contract.method())
        interface_call_pattern = r'\w+\.\w+\s*\([^)]*\)'
        if re.search(interface_call_pattern, source):
            # Exclude common false positives
            false_positives = ['msg.sender', 'block.timestamp', 'msg.value', 'tx.origin']
            matches = re.findall(interface_call_pattern, source)
            for match in matches:
                if not any(fp in match for fp in false_positives):
                    return True

        return False

    def _filter_by_state_changes(self, nodes: List[ASTNode], changes_state: bool) -> List[ASTNode]:
        """Filter functions that change state."""
        if not changes_state:
            return nodes

        filtered = []
        for node in nodes:
            if self._changes_state(node):
                filtered.append(node)
        return filtered

    def _changes_state(self, node: ASTNode) -> bool:
        """Check if a node modifies state variables."""
        if not hasattr(node, 'source_code') or not node.source_code:
            return False

        source = node.source_code

        # State-changing patterns
        state_change_patterns = [
            r'\w+\s*=\s*[^=]',  # Assignment (not comparison)
            r'\w+\s*\+=',       # Addition assignment
            r'\w+\s*-=',        # Subtraction assignment
            r'\w+\s*\*=',       # Multiplication assignment
            r'\w+\s*/=',        # Division assignment
            r'\w+\+\+',         # Increment
            r'\+\+\w+',         # Pre-increment
            r'\w+--',           # Decrement
            r'--\w+',           # Pre-decrement
            r'\w+\[.+\]\s*=',   # Array/mapping assignment
            r'push\s*\(',       # Array push
            r'pop\s*\(',        # Array pop
            r'delete\s+\w+',    # Delete statement
        ]

        for pattern in state_change_patterns:
            if re.search(pattern, source):
                return True

        # Check for storage keywords
        if re.search(r'\bstorage\b', source) and '=' in source:
            return True

        return False

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches pattern (exact or regex)."""
        try:
            return bool(re.search(pattern, text))
        except re.error:
            # If regex is invalid, try exact match
            return text == pattern

    def _build_query_result_data(self, nodes: List[ASTNode], include: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """Build result data for query_code response."""
        results = []

        for node in nodes:
            result_item = {
                "id": getattr(node, 'id', None),
                "name": getattr(node, 'name', None),
                "type": type(node).__name__,
                "location": self._get_node_location(node)
            }

            # Add basic node-specific info
            if isinstance(node, FunctionDeclaration):
                result_item.update({
                    "visibility": str(getattr(node, 'visibility', '')),
                    "state_mutability": str(getattr(node, 'state_mutability', '')),
                    "signature": getattr(node, 'signature', None)
                })
            elif isinstance(node, ContractDeclaration):
                result_item.update({
                    "kind": getattr(node, 'kind', None),
                    "inheritance": getattr(node, 'inheritance', [])
                })
            elif isinstance(node, VariableDeclaration):
                result_item.update({
                    "type_name": str(getattr(node, 'type_name', '')),
                    "visibility": str(getattr(node, 'visibility', '')),
                    "is_state_variable": getattr(node, 'is_state_variable', False)
                })

            # Add included data
            if "source" in include:
                result_item["source_code"] = getattr(node, 'source_code', None)

            if "ast" in include:
                result_item["ast_info"] = self._get_ast_info(node)

            if "calls" in include:
                result_item["calls"] = self._get_node_calls(node)

            if "callers" in include:
                result_item["callers"] = self._get_node_callers(node)

            if "variables" in include:
                result_item["variables"] = self._get_node_variables(node)

            if "events" in include:
                result_item["events"] = self._get_node_events(node)

            if "modifiers" in include and hasattr(node, 'modifiers'):
                result_item["modifiers"] = getattr(node, 'modifiers', [])

            if "natspec" in include:
                result_item["natspec"] = self._get_node_natspec(node)

            if "dependencies" in include:
                result_item["dependencies"] = self._get_node_dependencies(node)

            if "inheritance" in include and isinstance(node, ContractDeclaration):
                result_item["inheritance_details"] = self._get_inheritance_details(node)

            results.append(result_item)

        return {
            "results": results,
            "summary": {
                "total_count": len(results),
                "by_type": self._get_results_by_type(results),
                "by_contract": self._get_results_by_contract(results),
                "by_visibility": self._get_results_by_visibility(results)
            }
        }

    def _find_elements_by_identifiers(self, element_type: str, identifiers: List[str]) -> Dict[str, ASTNode]:
        """Find elements by their identifiers."""
        elements = {}

        # Get all nodes of the specified type
        all_nodes = self._get_all_nodes_by_element_type(element_type)

        # Match identifiers
        for identifier in identifiers:
            matching_node = self._find_best_match(all_nodes, identifier, element_type)
            if matching_node:
                elements[identifier] = matching_node

        return elements

    def _get_all_nodes_by_element_type(self, element_type: str) -> List[ASTNode]:
        """Get all nodes of specified element type."""
        if element_type == "function":
            all_nodes = self._get_all_nodes()
            return [node for node in all_nodes if isinstance(node, FunctionDeclaration)]
        elif element_type == "contract":
            return self.source_manager.get_contracts()
        elif element_type == "variable":
            all_nodes = self._get_all_nodes()
            return [node for node in all_nodes if isinstance(node, VariableDeclaration)]
        elif element_type == "modifier":
            all_nodes = self._get_all_nodes()
            return [node for node in all_nodes if isinstance(node, ModifierDeclaration)]
        elif element_type == "event":
            all_nodes = self._get_all_nodes()
            return [node for node in all_nodes if isinstance(node, EventDeclaration)]
        elif element_type == "error":
            all_nodes = self._get_all_nodes()
            return [node for node in all_nodes if isinstance(node, ErrorDeclaration)]
        elif element_type == "struct":
            all_nodes = self._get_all_nodes()
            return [node for node in all_nodes if isinstance(node, StructDeclaration)]
        elif element_type == "enum":
            all_nodes = self._get_all_nodes()
            return [node for node in all_nodes if isinstance(node, EnumDeclaration)]
        else:
            return []

    def _find_best_match(self, nodes: List[ASTNode], identifier: str, element_type: str) -> Optional[ASTNode]:
        """Find the best matching node for an identifier."""
        # Try exact name match first
        for node in nodes:
            if hasattr(node, 'name') and node.name == identifier:
                return node

        # Try signature match for functions
        if element_type == "function":
            for node in nodes:
                if self._matches_function_signature(node, identifier):
                    return node

        # Try contract.element format
        if '.' in identifier:
            parts = identifier.split('.', 1)
            if len(parts) == 2:
                contract_name, element_name = parts
                for node in nodes:
                    if (hasattr(node, 'contract') and node.contract == contract_name and
                        hasattr(node, 'name') and node.name == element_name):
                        return node

        # Try file:contract format for contracts
        if element_type == "contract" and ':' in identifier:
            parts = identifier.split(':')
            if len(parts) == 2:
                file_path, contract_name = parts
                for node in nodes:
                    if (hasattr(node, 'name') and node.name == contract_name and
                        hasattr(node, 'file_path') and file_path in str(node.file_path)):
                        return node

        return None

    def _matches_function_signature(self, node: ASTNode, signature: str) -> bool:
        """Check if node matches function signature."""
        if not isinstance(node, FunctionDeclaration):
            return False

        # Check if node has signature attribute
        if hasattr(node, 'signature') and node.signature == signature:
            return True

        # Try to build signature from name and parameters
        if hasattr(node, 'name') and node.name:
            # Extract function name from signature
            sig_name = signature.split('(')[0] if '(' in signature else signature
            if node.name == sig_name:
                return True

        return False


    def _analyze_element(self, element: ASTNode, analysis_depth: str,
                        include_context: bool, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an element based on analysis depth."""
        result = {
            "found": True,
            "basic_info": self._get_basic_element_info(element)
        }

        if analysis_depth in ["detailed", "comprehensive"]:
            result["detailed_info"] = self._get_detailed_element_info(element, options)

        if analysis_depth == "comprehensive":
            result["comprehensive_info"] = self._get_comprehensive_element_info(element, options)

        if include_context:
            result["context"] = self._get_element_context(element)

        return result

    def _get_basic_element_info(self, element: ASTNode) -> Dict[str, Any]:
        """Get basic information about an element."""
        return {
            "name": getattr(element, 'name', None),
            "type": type(element).__name__,
            "location": self._get_node_location(element),
            "signature": getattr(element, 'signature', None) if isinstance(element, FunctionDeclaration) else None
        }

    def _get_detailed_element_info(self, element: ASTNode, options: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about an element."""
        info = {}

        if options.get("include_source", True):
            info["source_code"] = getattr(element, 'source_code', None)

        if isinstance(element, FunctionDeclaration):
            info["visibility"] = str(element.visibility) if hasattr(element, 'visibility') else None
            info["state_mutability"] = str(element.state_mutability) if hasattr(element, 'state_mutability') else None
            info["modifiers"] = element.modifiers if hasattr(element, 'modifiers') else []

        return info

    def _get_comprehensive_element_info(self, element: ASTNode, options: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive information about an element."""
        return {
            "dependencies": self._get_element_dependencies(element),
            "call_graph": self._get_element_call_graph(element),
            "data_flow": self._get_element_data_flow(element),
            "security_analysis": self._get_element_security_analysis(element)
        }

    def _find_target_element(self, target: str, target_type: str) -> Optional[ASTNode]:
        """Find the target element for reference analysis."""
        elements = self._find_elements_by_identifiers(target_type, [target])
        element = elements.get(target)

        # If not found, try related element types for common naming patterns
        if not element:
            if target_type == "variable":
                # Try as function (for getter functions like totalSupply)
                func_elements = self._find_elements_by_identifiers("function", [target])
                element = func_elements.get(target)

                # Try with underscore prefix (for private variables like _totalSupply)
                if not element:
                    private_name = f"_{target}"
                    var_elements = self._find_elements_by_identifiers("variable", [private_name])
                    element = var_elements.get(private_name)

            elif target_type == "function":
                # Try as variable (for state variables)
                var_elements = self._find_elements_by_identifiers("variable", [target])
                element = var_elements.get(target)

        return element

    def _find_element_references(self, target_element: ASTNode, target_type: str,
                               reference_type: str, direction: str, max_depth: int,
                               filters: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Find references to an element."""
        references = {
            "usages": [],
            "definitions": [],
            "call_chains": [],
            "max_depth_reached": 0
        }

        # Find usages
        if reference_type in ["all", "usages"]:
            usages = self._find_element_usages(target_element, direction, max_depth, filters)
            references["usages"] = usages

        # Find definitions
        if reference_type in ["all", "definitions"]:
            definitions = self._find_element_definitions(target_element, direction, max_depth, filters)
            references["definitions"] = definitions

        # Build call chains if requested
        if options.get("show_call_chains", False):
            references["call_chains"] = self._build_call_chains(target_element, max_depth)

        return references

    def _find_element_usages(self, element: ASTNode, direction: str, max_depth: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find where an element is used."""
        usages = []
        element_name = getattr(element, 'name', '')

        if not element_name:
            return usages

        # Search in all relevant nodes based on direction
        search_nodes = self._get_search_nodes_by_direction(element, direction)

        for node in search_nodes:
            usage_info = self._analyze_element_usage_in_node(element, node)
            if usage_info:
                # Apply filters if provided
                if self._usage_passes_filters(usage_info, filters):
                    usages.append(usage_info)

                    # Stop if we've reached max depth or max results
                    if len(usages) >= 100:  # Reasonable limit
                        break

        return usages

    def _get_search_nodes_by_direction(self, element: ASTNode, direction: str) -> List[ASTNode]:
        """Get nodes to search based on analysis direction."""
        all_nodes = self._get_all_nodes()

        if direction == "forward":
            # For forward analysis, look in nodes that come after this element
            return [n for n in all_nodes if self._node_comes_after(n, element)]
        elif direction == "backward":
            # For backward analysis, look in nodes that come before this element
            return [n for n in all_nodes if self._node_comes_before(n, element)]
        else:  # "both"
            return all_nodes

    def _node_comes_after(self, node: ASTNode, reference: ASTNode) -> bool:
        """Check if node comes after reference node."""
        # Simple heuristic based on line numbers
        node_line = getattr(node, 'line_number', 0)
        ref_line = getattr(reference, 'line_number', 0)
        return node_line > ref_line

    def _node_comes_before(self, node: ASTNode, reference: ASTNode) -> bool:
        """Check if node comes before reference node."""
        node_line = getattr(node, 'line_number', 0)
        ref_line = getattr(reference, 'line_number', 0)
        return node_line < ref_line

    def _analyze_element_usage_in_node(self, element: ASTNode, node: ASTNode) -> Optional[Dict[str, Any]]:
        """Analyze how an element is used in a specific node."""
        element_name = getattr(element, 'name', '')
        node_source = getattr(node, 'source_code', '')

        if not element_name or not node_source or element_name not in node_source:
            return None

        # Determine usage type
        usage_type = self._determine_usage_type(element, element_name, node_source)

        # Get context around the usage
        context = self._extract_usage_context(element_name, node_source)

        return {
            "location": self._get_node_location(node),
            "usage_type": usage_type,
            "context": context,
            "node_type": type(node).__name__,
            "element_name": element_name,
            "source_snippet": node_source[:200] + "..." if len(node_source) > 200 else node_source
        }

    def _determine_usage_type(self, element: ASTNode, element_name: str, source: str) -> str:
        """Determine how an element is being used."""
        if isinstance(element, FunctionDeclaration):
            if f"{element_name}(" in source:
                return "function_call"
        elif isinstance(element, VariableDeclaration):
            if f"{element_name} =" in source or f"{element_name}=" in source:
                return "assignment"
            elif f"{element_name}[" in source:
                return "array_access"
            elif f"{element_name}." in source:
                return "member_access"
            else:
                return "variable_read"

        return "reference"

    def _extract_usage_context(self, element_name: str, source: str) -> str:
        """Extract contextual code around element usage."""
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if element_name in line:
                # Return the line with some context
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context_lines = lines[start:end]
                return '\n'.join(context_lines).strip()

        return source[:100] + "..." if len(source) > 100 else source

    def _usage_passes_filters(self, usage_info: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if usage passes the provided filters."""
        if not filters:
            return True

        # Apply contract filter
        if "contracts" in filters:
            usage_contract = usage_info.get("location", {}).get("contract")
            if usage_contract not in filters["contracts"]:
                return False

        # Apply visibility filter
        if "visibility" in filters:
            # This would require more complex analysis
            pass

        # Apply file filter
        if "files" in filters:
            usage_file = usage_info.get("location", {}).get("file")
            if usage_file:
                file_matches = any(self._matches_pattern(str(usage_file), pattern)
                                 for pattern in filters["files"])
                if not file_matches:
                    return False

        return True

    def _find_element_definitions(self, element: ASTNode, direction: str, max_depth: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find where an element is defined."""
        definitions = []
        element_name = getattr(element, 'name', '')

        # Primary definition (the element itself)
        primary_def = {
            "location": self._get_node_location(element),
            "definition_type": "primary",
            "context": getattr(element, 'source_code', ''),
            "element_type": type(element).__name__,
            "name": element_name
        }
        definitions.append(primary_def)

        # Look for overrides and implementations
        if isinstance(element, FunctionDeclaration):
            overrides = self._find_function_overrides(element)
            for override in overrides:
                definitions.append({
                    "location": self._get_node_location(override),
                    "definition_type": "override",
                    "context": getattr(override, 'source_code', ''),
                    "element_type": type(override).__name__,
                    "name": getattr(override, 'name', '')
                })

        # Look for interface declarations
        if isinstance(element, (FunctionDeclaration, EventDeclaration)):
            interface_defs = self._find_interface_declarations(element)
            for interface_def in interface_defs:
                definitions.append({
                    "location": self._get_node_location(interface_def),
                    "definition_type": "interface",
                    "context": getattr(interface_def, 'source_code', ''),
                    "element_type": type(interface_def).__name__,
                    "name": getattr(interface_def, 'name', '')
                })

        # Apply filters
        if filters:
            definitions = [d for d in definitions if self._definition_passes_filters(d, filters)]

        return definitions

    def _find_function_overrides(self, function: FunctionDeclaration) -> List[FunctionDeclaration]:
        """Find functions that override the given function."""
        overrides = []
        function_name = getattr(function, 'name', '')

        if not function_name:
            return overrides

        all_nodes = self._get_all_nodes()
        all_functions = [node for node in all_nodes if isinstance(node, FunctionDeclaration)]

        for func in all_functions:
            if (func != function and
                getattr(func, 'name', '') == function_name and
                self._is_function_override(func, function)):
                overrides.append(func)

        return overrides

    def _is_function_override(self, candidate: FunctionDeclaration, original: FunctionDeclaration) -> bool:
        """Check if candidate function is an override of original."""
        # Check for explicit override keyword
        candidate_source = getattr(candidate, 'source_code', '')
        if 'override' in candidate_source:
            return True

        # Check if they're in inheritance hierarchy
        candidate_contract = getattr(candidate, 'contract', '')
        original_contract = getattr(original, 'contract', '')

        if candidate_contract != original_contract:
            # Check if candidate's contract inherits from original's contract
            return self._contracts_in_inheritance(candidate_contract, original_contract)

        return False

    def _contracts_in_inheritance(self, derived: str, base: str) -> bool:
        """Check if derived contract inherits from base contract."""
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if (getattr(contract, 'name', '') == derived and
                base in getattr(contract, 'inheritance', [])):
                return True

        return False

    def _find_interface_declarations(self, element: ASTNode) -> List[ASTNode]:
        """Find interface declarations for an element."""
        interface_defs = []
        element_name = getattr(element, 'name', '')

        if not element_name:
            return interface_defs

        # Look in interface contracts
        contracts = self.source_manager.get_contracts()

        for contract in contracts:
            if getattr(contract, 'kind', '') == 'interface':
                # Get all functions/events in this interface
                if isinstance(element, FunctionDeclaration):
                    interface_functions = self._get_contract_functions(contract)
                    for func in interface_functions:
                        if getattr(func, 'name', '') == element_name:
                            interface_defs.append(func)

        return interface_defs

    def _get_contract_functions(self, contract: ContractDeclaration) -> List[FunctionDeclaration]:
        """Get all functions in a contract."""
        contract_name = getattr(contract, 'name', '')
        all_nodes = self._get_all_nodes()
        all_functions = [node for node in all_nodes if isinstance(node, FunctionDeclaration)]

        return [f for f in all_functions if getattr(f, 'contract', '') == contract_name]

    def _definition_passes_filters(self, definition: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if definition passes the provided filters."""
        # Similar to usage filters but for definitions
        if "contracts" in filters:
            def_contract = definition.get("location", {}).get("contract")
            if def_contract and def_contract not in filters["contracts"]:
                return False

        return True

    # Utility methods

    def _get_node_location(self, node: ASTNode) -> Dict[str, Any]:
        """Get location information for a node."""
        return {
            "file": getattr(node, 'file_path', None),
            "line": getattr(node, 'line_number', None),
            "column": getattr(node, 'column', None),
            "contract": getattr(node, 'contract', None)
        }

    def _get_analysis_scope(self, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Get the actual analysis scope used."""
        return {
            "total_files": len(self.source_manager.files),
            "total_contracts": len(self.source_manager.get_contracts()),
            "scope_applied": scope
        }

    def _get_query_suggestions(self, query_type: str, filters: Dict[str, Any]) -> List[str]:
        """Get query optimization suggestions."""
        suggestions = []

        if not filters:
            suggestions.append(f"Consider adding filters to narrow down {query_type} results")

        if query_type == "functions" and "visibility" not in filters:
            suggestions.append("Add visibility filter to focus on public/external functions")

        return suggestions

    def _get_related_queries(self, query_type: str, filters: Dict[str, Any]) -> List[str]:
        """Get suggestions for related queries."""
        related = []

        if query_type == "functions":
            related.append("query_code('calls', filters={'in_functions': results})")
            related.append("query_code('variables', filters={'function_context': results})")

        elif query_type == "contracts":
            related.append("query_code('functions', filters={'contracts': results})")

        return related

    def _create_error_response(self, function_name: str, parameters: Dict[str, Any],
                             errors: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """Create a standardized error response."""
        # Convert string errors to dict format
        formatted_errors = []
        validation_errors = []

        for error in errors:
            if isinstance(error, str):
                formatted_errors.append(error)
            elif isinstance(error, dict):
                validation_errors.append(error)
                formatted_errors.append(error.get("error", "Validation error"))

        return {
            "success": False,
            "query_info": {
                "function": function_name,
                "parameters": parameters,
                "validation_errors": validation_errors,
                "execution_time": 0.0,
                "result_count": 0,
                "cache_hit": False
            },
            "data": None,
            "metadata": {
                "analysis_scope": {},
                "filters_applied": {},
                "performance": {
                    "references_found": 0,
                    "depth_reached": 0,
                    "files_analyzed": 0
                }
            },
            "warnings": [],
            "errors": formatted_errors,
            "suggestions": [
                "Check parameter documentation",
                f"Use {function_name}() with broader filters to understand project structure"
            ]
        }

    # Scope filtering implementations
    def _node_in_contracts(self, node: ASTNode, contract_names: List[str]) -> bool:
        """Check if node is in specified contracts."""
        if not contract_names:
            return True

        node_contract = getattr(node, 'contract', None)
        if not node_contract:
            return False

        for contract_name in contract_names:
            if self._matches_pattern(node_contract, contract_name):
                return True
        return False

    def _node_in_functions(self, node: ASTNode, function_names: List[str]) -> bool:
        """Check if node is in specified functions."""
        if not function_names:
            return True

        # Check if node is a function itself
        if isinstance(node, FunctionDeclaration):
            node_name = getattr(node, 'name', None)
            if node_name:
                for func_name in function_names:
                    if self._matches_pattern(node_name, func_name):
                        return True

        # Check if node is within a function
        node_function = getattr(node, 'function', None)
        if node_function:
            for func_name in function_names:
                if self._matches_pattern(node_function, func_name):
                    return True

        return False

    def _node_in_files(self, node: ASTNode, file_patterns: List[str]) -> bool:
        """Check if node is in specified files."""
        if not file_patterns:
            return True

        node_file = getattr(node, 'file_path', None)
        if not node_file:
            return False

        node_file_str = str(node_file)
        for file_pattern in file_patterns:
            if self._matches_pattern(node_file_str, file_pattern):
                return True
        return False

    def _node_in_directories(self, node: ASTNode, dir_patterns: List[str]) -> bool:
        """Check if node is in specified directories."""
        if not dir_patterns:
            return True

        node_file = getattr(node, 'file_path', None)
        if not node_file:
            return False

        node_dir = str(Path(node_file).parent)
        for dir_pattern in dir_patterns:
            if self._matches_pattern(node_dir, dir_pattern):
                return True
        return False

    def _node_in_inheritance_tree(self, node: ASTNode, base_contract: str) -> bool:
        """Check if node is in inheritance tree of base contract."""
        if isinstance(node, ContractDeclaration):
            inheritance = getattr(node, 'inheritance', [])
            return base_contract in inheritance

        # For other nodes, check their contract's inheritance
        node_contract = getattr(node, 'contract', None)
        if node_contract:
            # Find the contract and check its inheritance
            contracts = self.source_manager.get_contracts()
            for contract in contracts:
                if contract.name == node_contract:
                    inheritance = getattr(contract, 'inheritance', [])
                    return base_contract in inheritance

        return False

    def _filter_by_contract_names(self, nodes: List[ASTNode], contract_patterns: List[str]) -> List[ASTNode]:
        """Filter nodes by contract name patterns."""
        if isinstance(contract_patterns, str):
            contract_patterns = [contract_patterns]

        filtered = []
        for node in nodes:
            node_contract = getattr(node, 'contract', None)
            if node_contract:
                for pattern in contract_patterns:
                    if self._matches_pattern(node_contract, pattern):
                        filtered.append(node)
                        break
        return filtered

    def _filter_by_asset_transfers(self, nodes: List[ASTNode], has_transfers: bool) -> List[ASTNode]:
        """Filter for asset transfer functions."""
        if not has_transfers:
            return nodes

        filtered = []
        for node in nodes:
            if self._has_asset_transfers(node):
                filtered.append(node)
        return filtered

    def _has_asset_transfers(self, node: ASTNode) -> bool:
        """Check if node contains asset transfers."""
        if not hasattr(node, 'source_code') or not node.source_code:
            return False

        source = node.source_code

        # Asset transfer patterns
        transfer_patterns = [
            r'\.transfer\s*\(',
            r'\.send\s*\(',
            r'\.call\s*\{\s*value\s*:',
            r'payable\s*\(',
            r'_transfer\s*\(',
            r'safeTransfer\s*\(',
            r'transferFrom\s*\('
        ]

        for pattern in transfer_patterns:
            if re.search(pattern, source):
                return True

        return False

    def _filter_by_payable(self, nodes: List[ASTNode], is_payable: bool) -> List[ASTNode]:
        """Filter for payable functions."""
        filtered = []
        for node in nodes:
            node_payable = (hasattr(node, 'state_mutability') and
                          str(node.state_mutability).lower() == 'payable')
            if node_payable == is_payable:
                filtered.append(node)
        return filtered

    def _filter_by_types(self, nodes: List[ASTNode], type_patterns: List[str]) -> List[ASTNode]:
        """Filter variables by type patterns."""
        if isinstance(type_patterns, str):
            type_patterns = [type_patterns]

        filtered = []
        for node in nodes:
            node_type = str(getattr(node, 'type_name', '')) or str(getattr(node, 'var_type', ''))
            if node_type:
                for pattern in type_patterns:
                    if self._matches_pattern(node_type, pattern):
                        filtered.append(node)
                        break
        return filtered

    def _filter_by_state_variable(self, nodes: List[ASTNode], is_state: bool) -> List[ASTNode]:
        """Filter for state variables."""
        filtered = []
        for node in nodes:
            node_is_state = getattr(node, 'is_state_variable', False)
            if node_is_state == is_state:
                filtered.append(node)
        return filtered

    def _filter_by_statement_types(self, nodes: List[ASTNode], statement_types: List[str]) -> List[ASTNode]:
        """Filter by statement types."""
        if isinstance(statement_types, str):
            statement_types = [statement_types]

        filtered = []
        for node in nodes:
            node_type = getattr(node, 'statement_type', None) or type(node).__name__.lower()
            for stmt_type in statement_types:
                if stmt_type.lower() in node_type:
                    filtered.append(node)
                    break
        return filtered

    def _filter_by_operators(self, nodes: List[ASTNode], operators: List[str]) -> List[ASTNode]:
        """Filter by operators used."""
        filtered = []
        for node in nodes:
            source = getattr(node, 'source_code', '')
            if source and any(op in source for op in operators):
                filtered.append(node)
        return filtered

    def _filter_by_access_patterns(self, nodes: List[ASTNode], patterns: List[str]) -> List[ASTNode]:
        """Filter by access patterns."""
        filtered = []
        for node in nodes:
            source = getattr(node, 'source_code', '')
            if source:
                for pattern in patterns:
                    if self._matches_pattern(source, pattern):
                        filtered.append(node)
                        break
        return filtered

    def _filter_by_call_types(self, nodes: List[ASTNode], call_types: List[str]) -> List[ASTNode]:
        """Filter by call types."""
        filtered = []
        for node in nodes:
            source = getattr(node, 'source_code', '')
            if source:
                for call_type in call_types:
                    pattern = f'\\.{call_type}\\s*\\('
                    if re.search(pattern, source):
                        filtered.append(node)
                        break
        return filtered

    def _filter_by_low_level_calls(self, nodes: List[ASTNode], is_low_level: bool) -> List[ASTNode]:
        """Filter for low-level calls."""
        if not is_low_level:
            return nodes

        filtered = []
        for node in nodes:
            source = getattr(node, 'source_code', '')
            if source:
                low_level_patterns = [r'\.call\s*\(', r'\.delegatecall\s*\(', r'\.staticcall\s*\(', r'\.send\s*\(', r'\.transfer\s*\(']
                if any(re.search(pattern, source) for pattern in low_level_patterns):
                    filtered.append(node)
        return filtered

    def _get_ast_info(self, node: ASTNode) -> Dict[str, Any]:
        """Get AST information for a node."""
        return {
            "node_type": type(node).__name__,
            "node_id": getattr(node, 'id', None),
            "start_line": getattr(node, 'line_number', None),
            "end_line": getattr(node, 'end_line_number', None),
            "column": getattr(node, 'column', None)
        }

    def _get_node_calls(self, node: ASTNode) -> List[Dict[str, Any]]:
        """Get function calls made by a node."""
        calls = []
        source = getattr(node, 'source_code', '')

        if source:
            # Extract function calls using regex patterns
            call_patterns = [
                r'(\w+)\s*\(',  # Simple function calls
                r'(\w+\.\w+)\s*\(',  # Method calls
                r'\.call\s*\(',  # Low-level calls
                r'\.delegatecall\s*\(',
                r'\.staticcall\s*\('
            ]

            for pattern in call_patterns:
                matches = re.finditer(pattern, source)
                for match in matches:
                    call_name = match.group(1) if match.lastindex else 'call'
                    calls.append({
                        'name': call_name,
                        'type': 'external' if '.' in call_name else 'internal',
                        'position': match.start()
                    })

        return calls

    def _get_node_callers(self, node: ASTNode) -> List[Dict[str, Any]]:
        """Get functions that call this node."""
        callers = []

        if hasattr(node, 'name') and node.name:
            # Find all functions that reference this node
            all_nodes = self._get_all_nodes()
            all_functions = [node for node in all_nodes if isinstance(node, FunctionDeclaration)]

            for func in all_functions:
                func_source = getattr(func, 'source_code', '')
                if func_source and node.name in func_source:
                    callers.append({
                        'name': getattr(func, 'name', None),
                        'contract': getattr(func, 'contract', None),
                        'file': getattr(func, 'file_path', None)
                    })

        return callers

    def _get_node_variables(self, node: ASTNode) -> List[Dict[str, Any]]:
        """Get variables accessed by a node."""
        variables = []
        source = getattr(node, 'source_code', '')

        if source:
            # Extract variable access patterns
            var_patterns = [
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=',  # Assignment targets
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\[',  # Array access
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.',  # Member access
                r'\b(msg\.(sender|value|data))',     # Built-in variables
                r'\b(block\.(timestamp|number))',   # Block variables
                r'\b(tx\.origin)'                   # Transaction variables
            ]

            for pattern in var_patterns:
                matches = re.finditer(pattern, source)
                for match in matches:
                    var_name = match.group(1)
                    if var_name and not var_name.isdigit():  # Exclude numbers
                        variables.append({
                            'name': var_name,
                            'access_type': 'read' if '=' not in match.group(0) else 'write',
                            'position': match.start()
                        })

        return variables

    def _get_node_events(self, node: ASTNode) -> List[Dict[str, Any]]:
        """Get events emitted by a node."""
        events = []
        source = getattr(node, 'source_code', '')

        if source:
            # Extract emit statements
            emit_pattern = r'emit\s+(\w+)\s*\('
            matches = re.finditer(emit_pattern, source)

            for match in matches:
                event_name = match.group(1)
                events.append({
                    'name': event_name,
                    'position': match.start()
                })

        return events

    def _get_node_natspec(self, node: ASTNode) -> Dict[str, Any]:
        """Get NatSpec documentation for a node."""
        return {
            'title': getattr(node, 'natspec_title', None),
            'notice': getattr(node, 'natspec_notice', None),
            'dev': getattr(node, 'natspec_dev', None),
            'params': getattr(node, 'natspec_params', {}),
            'returns': getattr(node, 'natspec_returns', {})
        }

    def _get_node_dependencies(self, node: ASTNode) -> List[str]:
        """Get dependencies of a node."""
        dependencies = []
        source = getattr(node, 'source_code', '')

        if source:
            # Extract import-like dependencies
            import_patterns = [
                r'import\s+["\']([^"\']*)["\'\s;]',
                r'using\s+(\w+)\s+for',
                r'\binherits\s+(\w+)',
                r'\bimplements\s+(\w+)'
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, source)
                dependencies.extend(matches)

        return list(set(dependencies))  # Remove duplicates

    def _get_inheritance_details(self, node: ContractDeclaration) -> Dict[str, Any]:
        """Get inheritance details for a contract."""
        return {
            'base_contracts': getattr(node, 'inheritance', []),
            'is_abstract': getattr(node, 'is_abstract', False),
            'interfaces': getattr(node, 'interfaces', []),
            'override_functions': getattr(node, 'override_functions', [])
        }

    def _get_results_by_type(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get results distribution by type."""
        distribution = {}
        for result in results:
            result_type = result.get("type", "unknown")
            distribution[result_type] = distribution.get(result_type, 0) + 1
        return distribution

    def _get_results_by_contract(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get results distribution by contract."""
        distribution = {}
        for result in results:
            contract = result.get("location", {}).get("contract", "unknown")
            distribution[contract] = distribution.get(contract, 0) + 1
        return distribution

    def _get_results_by_visibility(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get results distribution by visibility."""
        distribution = {}
        for result in results:
            visibility = result.get("visibility", "unknown")
            if visibility and visibility != "unknown":
                distribution[visibility] = distribution.get(visibility, 0) + 1
        return distribution

    def _create_analysis_summary(self, analysis_results: Dict[str, Any], depth: str) -> Dict[str, Any]:
        """Create summary of analysis results."""
        found_count = len([r for r in analysis_results.values() if r.get("found", True)])

        # Count analysis features by depth
        features_analyzed = ["basic_info"]
        if depth in ["detailed", "comprehensive"]:
            features_analyzed.append("detailed_info")
        if depth == "comprehensive":
            features_analyzed.extend(["comprehensive_info", "dependencies", "call_graphs"])

        return {
            "elements_found": found_count,
            "elements_requested": len(analysis_results),
            "analysis_depth": depth,
            "success_rate": found_count / len(analysis_results) if analysis_results else 0,
            "features_analyzed": features_analyzed,
            "total_analysis_points": len(features_analyzed) * found_count
        }

    def _get_target_info(self, element: ASTNode, target_type: str) -> Dict[str, Any]:
        """Get information about the target element."""
        return {
            "name": getattr(element, 'name', None),
            "type": target_type,
            "location": self._get_node_location(element)
        }

    def _get_element_context(self, element: ASTNode) -> Dict[str, Any]:
        """Get context information for an element."""
        context = {
            "surrounding_code": getattr(element, 'source_code', ''),
            "file_context": {
                "file_path": getattr(element, 'file_path', None),
                "line_number": getattr(element, 'line_number', None),
                "contract": getattr(element, 'contract', None)
            }
        }

        # Add parent/child relationships
        if hasattr(element, 'parent'):
            context["parent"] = {
                "type": type(element.parent).__name__,
                "name": getattr(element.parent, 'name', None)
            }

        # Add sibling elements for context
        context["siblings"] = self._get_sibling_elements(element)

        return context

    def _get_sibling_elements(self, element: ASTNode) -> List[Dict[str, Any]]:
        """Get sibling elements for context."""
        siblings = []
        element_contract = getattr(element, 'contract', None)

        if element_contract:
            # Get other elements in the same contract
            same_type_nodes = self._get_all_nodes_by_element_type(
                type(element).__name__.replace('Declaration', '').lower()
            )

            for node in same_type_nodes[:5]:  # Limit to 5 siblings
                if (node != element and
                    getattr(node, 'contract', None) == element_contract):
                    siblings.append({
                        "name": getattr(node, 'name', None),
                        "type": type(node).__name__
                    })

        return siblings

    def _get_element_dependencies(self, element: ASTNode) -> List[Dict[str, Any]]:
        """Get dependencies of an element."""
        dependencies = []

        # Get direct dependencies from source code
        source_deps = self._get_node_dependencies(element)
        for dep in source_deps:
            dependencies.append({
                "name": dep,
                "type": "import",
                "source": "code_analysis"
            })

        # For functions, get called functions as dependencies
        if isinstance(element, FunctionDeclaration):
            calls = self._get_node_calls(element)
            for call in calls:
                dependencies.append({
                    "name": call.get("name", ""),
                    "type": "function_call",
                    "call_type": call.get("type", "unknown")
                })

        # For contracts, get inheritance dependencies
        if isinstance(element, ContractDeclaration):
            inheritance = getattr(element, 'inheritance', [])
            for base in inheritance:
                dependencies.append({
                    "name": base,
                    "type": "inheritance",
                    "source": "contract_hierarchy"
                })

        return dependencies

    def _get_element_call_graph(self, element: ASTNode) -> Dict[str, Any]:
        """Get call graph for an element."""
        call_graph = {
            "calls_made": [],
            "called_by": [],
            "call_depth": 0,
            "is_recursive": False
        }

        if isinstance(element, FunctionDeclaration):
            # Get functions this element calls
            calls = self._get_node_calls(element)
            call_graph["calls_made"] = [call.get("name", "") for call in calls]

            # Get functions that call this element
            callers = self._get_node_callers(element)
            call_graph["called_by"] = [caller.get("name", "") for caller in callers]

            # Check for recursion
            element_name = getattr(element, 'name', '')
            call_graph["is_recursive"] = element_name in call_graph["calls_made"]

            # Calculate approximate call depth
            call_graph["call_depth"] = len(call_graph["calls_made"])

        return call_graph

    def _get_element_data_flow(self, element: ASTNode) -> Dict[str, Any]:
        """Get data flow analysis for an element."""
        data_flow = {
            "variables_read": [],
            "variables_written": [],
            "external_interactions": [],
            "state_changes": False
        }

        # Get variable access patterns
        variables = self._get_node_variables(element)
        for var in variables:
            if var.get("access_type") == "read":
                data_flow["variables_read"].append(var.get("name", ""))
            elif var.get("access_type") == "write":
                data_flow["variables_written"].append(var.get("name", ""))

        # Check for external interactions
        if self._has_external_calls(element):
            calls = self._get_node_calls(element)
            external_calls = [call for call in calls if call.get("type") == "external"]
            data_flow["external_interactions"] = [call.get("name", "") for call in external_calls]

        # Check for state changes
        data_flow["state_changes"] = self._changes_state(element)

        return data_flow

    def _get_element_security_analysis(self, element: ASTNode) -> Dict[str, Any]:
        """Get security analysis for an element."""
        security_analysis = {
            "risk_level": "low",
            "issues": [],
            "recommendations": []
        }

        # Check for common security issues
        if isinstance(element, FunctionDeclaration):
            issues = []

            # Check for reentrancy risks
            if (self._has_external_calls(element) and
                self._changes_state(element)):
                issues.append({
                    "type": "reentrancy_risk",
                    "severity": "high",
                    "description": "Function makes external calls and modifies state"
                })
                security_analysis["recommendations"].append("Add reentrancy guard")

            # Check for missing access control
            visibility = getattr(element, 'visibility', None)
            modifiers = getattr(element, 'modifiers', [])
            if (str(visibility).lower() in ['external', 'public'] and
                not any('only' in str(mod).lower() for mod in modifiers)):
                issues.append({
                    "type": "missing_access_control",
                    "severity": "medium",
                    "description": "Public/external function without access control"
                })
                security_analysis["recommendations"].append("Add access control modifier")

            # Check for unchecked external calls
            source = getattr(element, 'source_code', '')
            if '.call(' in source and '(bool success,' not in source:
                issues.append({
                    "type": "unchecked_call",
                    "severity": "medium",
                    "description": "External call result not checked"
                })
                security_analysis["recommendations"].append("Check call return value")

            security_analysis["issues"] = issues

            # Determine overall risk level
            if any(issue["severity"] == "high" for issue in issues):
                security_analysis["risk_level"] = "high"
            elif any(issue["severity"] == "medium" for issue in issues):
                security_analysis["risk_level"] = "medium"

        return security_analysis

    def _build_call_chains(self, element: ASTNode, max_depth: int) -> List[List[str]]:
        """Build call chains for an element."""
        call_chains = []
        element_name = getattr(element, 'name', '')

        if not element_name or max_depth <= 0:
            return call_chains

        # Start building chains from this element
        visited = set()
        current_chain = [element_name]

        self._build_call_chain_recursive(element, current_chain, call_chains, visited, max_depth, 0)

        return call_chains

    def _build_call_chain_recursive(self, current_element: ASTNode, current_chain: List[str],
                                   all_chains: List[List[str]], visited: set, max_depth: int, depth: int):
        """Recursively build call chains."""
        if depth >= max_depth:
            if len(current_chain) > 1:
                all_chains.append(current_chain.copy())
            return

        element_name = getattr(current_element, 'name', '')
        if element_name in visited:
            return

        visited.add(element_name)

        # Find what this element calls
        calls = self._get_element_calls(current_element)

        if not calls:
            # End of chain
            if len(current_chain) > 1:
                all_chains.append(current_chain.copy())
        else:
            for call in calls:
                call_name = call.get('name', '')
                if call_name and call_name not in visited:
                    # Find the called element
                    called_element = self._find_element_by_name(call_name)
                    if called_element:
                        current_chain.append(call_name)
                        self._build_call_chain_recursive(called_element, current_chain, all_chains,
                                                        visited.copy(), max_depth, depth + 1)
                        current_chain.pop()

        visited.remove(element_name)

    def _get_element_calls(self, element: ASTNode) -> List[Dict[str, str]]:
        """Get calls made by an element."""
        return self._get_node_calls(element)

    def _find_element_by_name(self, name: str) -> Optional[ASTNode]:
        """Find an element by name across all node types."""
        # Search functions first
        all_nodes = self._get_all_nodes()
        functions = [node for node in all_nodes if isinstance(node, FunctionDeclaration)]
        for func in functions:
            if getattr(func, 'name', '') == name:
                return func

        # Search contracts
        contracts = self.source_manager.get_contracts()
        for contract in contracts:
            if getattr(contract, 'name', '') == name:
                return contract

        # Search other node types
        for node in all_nodes:
            if getattr(node, 'name', '') == name:
                return node

        return None