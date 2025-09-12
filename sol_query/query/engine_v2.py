"""
SolidityQueryEngineV2: LLM-friendly code query API with 3 core functions.

Implements the exact API specification from new-code-query-api-requirements.md
"""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sol_query.core.source_manager import SourceManager
from sol_query.core.ast_nodes import (
    ASTNode, ContractDeclaration, FunctionDeclaration, VariableDeclaration,
    ModifierDeclaration, EventDeclaration, ErrorDeclaration, StructDeclaration,
    EnumDeclaration, Statement, Expression, ExtractedStatement, ExtractedExpression,
    NodeType
)
from sol_query.models.source_location import SourceLocation
from sol_query.utils.pattern_matching import PatternMatcher
from sol_query.analysis.call_analyzer import CallAnalyzer
from sol_query.analysis.variable_tracker import VariableTracker


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

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize existing sophisticated analyzers
        self.call_analyzer = CallAnalyzer()
        self.variable_tracker = VariableTracker()

        # Performance optimization: cache frequently accessed data
        self._all_nodes_cache = None
        self._nodes_by_type_cache = {}

        if source_paths:
            self.load_sources(source_paths)

    def _get_all_nodes(self) -> List[ASTNode]:
        """Get all AST nodes from all source files with caching."""
        if self._all_nodes_cache is not None:
            return self._all_nodes_cache

        all_nodes = []

        # Get contracts (these are available directly)
        contracts = self.source_manager.get_contracts()
        all_nodes.extend(contracts)

        # Extract nested elements from contracts using attribute mapping for performance
        nested_attributes = ['functions', 'variables', 'events', 'modifiers', 'errors', 'structs', 'enums']

        for contract in contracts:
            for attr in nested_attributes:
                if hasattr(contract, attr):
                    all_nodes.extend(getattr(contract, attr))

        # Get all other nodes from each source file's AST
        for source_file in self.source_manager.get_all_files():
            if source_file.ast:
                all_nodes.extend(source_file.ast)

        # Cache the result
        self._all_nodes_cache = all_nodes
        return all_nodes

    def load_sources(self, source_paths: Union[str, Path, List[Union[str, Path]]]) -> None:
        """Load source files or directories and invalidate caches."""
        if isinstance(source_paths, (str, Path)):
            source_paths = [source_paths]

        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                self.source_manager.add_file(path)
            elif path.is_dir():
                self.source_manager.add_directory(path, recursive=True)

        # Invalidate caches after loading new sources
        self._invalidate_caches()

    def _invalidate_caches(self) -> None:
        """Invalidate all internal caches."""
        self._all_nodes_cache = None
        self._nodes_by_type_cache.clear()

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
            result_data = self._build_query_result_data(nodes, include)

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
            return self._handle_exception("query_code", {
                "query_type": query_type,
                "filters": filters,
                "scope": scope,
                "include": include,
                "options": options
            }, e, "during code query execution")

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
            return self._handle_exception("get_details", {
                "element_type": element_type,
                "identifiers": identifiers,
                "analysis_depth": analysis_depth,
                "include_context": include_context,
                "options": options
            }, e, "during element detail analysis")

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
            references = self._find_element_references(target_element, reference_type, direction, max_depth, filters, options)

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
            return self._handle_exception("find_references", {
                "target": target,
                "target_type": target_type,
                "reference_type": reference_type,
                "direction": direction,
                "max_depth": max_depth,
                "filters": filters,
                "options": options
            }, e, "during reference analysis")

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
            # Extract statements from function and modifier bodies using AST traversal
            statements = []
            functions_and_modifiers = [node for node in all_nodes if isinstance(node, (FunctionDeclaration, ModifierDeclaration))]
            for func in functions_and_modifiers:
                if hasattr(func, 'raw_node') and func.raw_node:
                    func_statements = self._get_node_statements(func)
                    # Convert dictionary statements to proper AST nodes
                    for stmt_data in func_statements:
                        source_loc = SourceLocation(
                            file_path=func.source_location.file_path,
                            start_line=stmt_data['source_location']['line'],
                            start_column=stmt_data['source_location']['column'],
                            end_line=stmt_data['source_location']['line'],
                            end_column=stmt_data['source_location']['column'] + 10,
                            start_byte=stmt_data['source_location']['start_byte'],
                            end_byte=stmt_data['source_location']['end_byte'],
                            source_text=stmt_data.get('source_text', '')
                        )

                        # Map statement types to NodeType enums
                        stmt_type_map = {
                            "return_statement": NodeType.RETURN_STATEMENT,
                            "emit_statement": NodeType.EMIT_STATEMENT,
                            "expression_statement": NodeType.EXPRESSION_STATEMENT,
                            "if_statement": NodeType.IF_STATEMENT,
                            "for_statement": NodeType.FOR_STATEMENT,
                            "while_statement": NodeType.WHILE_STATEMENT,
                        }

                        node_type = stmt_type_map.get(stmt_data.get('type', ''), NodeType.STATEMENT)

                        stmt_node = ExtractedStatement(
                            node_type=node_type,
                            source_location=source_loc
                        )
                        stmt_node.parent_function = func
                        statements.append(stmt_node)
            return statements
        elif query_type == "expressions":
            # Extract expressions from function bodies using AST traversal
            expressions = []
            functions = [node for node in all_nodes if isinstance(node, FunctionDeclaration)]
            for func in functions:
                if hasattr(func, 'raw_node') and func.raw_node:
                    func_expressions = self._get_node_expressions(func)
                    # Convert dictionary expressions to proper AST nodes
                    for expr_data in func_expressions:
                        source_loc = SourceLocation(
                            file_path=func.source_location.file_path,
                            start_line=expr_data['source_location']['line'],
                            start_column=expr_data['source_location']['column'],
                            end_line=expr_data['source_location']['line'],
                            end_column=expr_data['source_location']['column'] + 10,
                            start_byte=expr_data['source_location']['start_byte'],
                            end_byte=expr_data['source_location']['end_byte'],
                            source_text=expr_data.get('source_text', '')
                        )

                        # Map expression types to NodeType enums
                        expr_type_map = {
                            "binary_expression": NodeType.BINARY_EXPRESSION,
                            "call_expression": NodeType.CALL_EXPRESSION,
                            "member_access_expression": NodeType.MEMBER_ACCESS,
                            "identifier": NodeType.IDENTIFIER,
                            "literal": NodeType.LITERAL,
                            "assignment_expression": NodeType.ASSIGNMENT_EXPRESSION,
                            "array_access": NodeType.ARRAY_ACCESS,
                            "unary_expression": NodeType.UNARY_EXPRESSION,
                        }

                        node_type = expr_type_map.get(expr_data.get('type', ''), NodeType.IDENTIFIER)

                        expr_node = ExtractedExpression(
                            node_type=node_type,
                            source_location=source_loc
                        )
                        expr_node.parent_function = func
                        expressions.append(expr_node)
            return expressions
        elif query_type == "calls":
            # Extract calls from function bodies using AST analysis
            calls = []
            functions = [node for node in all_nodes if isinstance(node, FunctionDeclaration)]
            for func in functions:
                if hasattr(func, 'raw_node') and func.raw_node:
                    # Get all calls from this function using AST traversal
                    func_calls = self._get_node_calls(func)
                    for call in func_calls:
                        # Create a simple call representation that behaves like an AST node
                        class CallNode:
                            def __init__(self, call_data, func):
                                self.name = call_data.get('name', '')
                                self.source_code = call_data.get('name', '')
                                self.call_type = call_data.get('type', 'unknown')
                                self.position = call_data.get('position', 0)
                                self.line_number = call_data.get('line', 0)
                                self.column = call_data.get('column', 0)
                                self.parent_function = getattr(func, 'name', None)
                                self.parent_contract = getattr(func, 'parent_contract', None)
                                self.contract = getattr(self.parent_contract, 'name', None) if self.parent_contract else None
                                self.source_location = getattr(func, 'source_location', None)

                            def __str__(self):
                                return self.name

                        call_node = CallNode(call, func)
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

        normalized_values = [v.lower() for v in visibility_values]
        return [n for n in nodes if hasattr(n, 'visibility') and
                (n.visibility.value.lower() if hasattr(n.visibility, 'value') else str(n.visibility).lower()) in normalized_values]

    def _filter_by_state_mutability(self, nodes: List[ASTNode], mutability_values: Union[str, List[str]]) -> List[ASTNode]:
        """Filter nodes by state mutability."""
        if isinstance(mutability_values, str):
            mutability_values = [mutability_values]

        normalized_values = [m.lower() for m in mutability_values]
        return [n for n in nodes if hasattr(n, 'state_mutability') and
                (n.state_mutability.value.lower() if hasattr(n.state_mutability, 'value') else str(n.state_mutability).lower()) in normalized_values]

    def _filter_by_modifiers(self, nodes: List[ASTNode], modifier_patterns: Union[str, List[str]]) -> List[ASTNode]:
        """Filter nodes by modifier patterns."""
        if isinstance(modifier_patterns, str):
            modifier_patterns = [modifier_patterns]

        # Empty list means no modifiers
        if not modifier_patterns:
            filtered: List[ASTNode] = []
            for n in nodes:
                # Only functions can have modifiers here
                if isinstance(n, FunctionDeclaration):
                    if not getattr(n, 'modifiers', []):
                        filtered.append(n)
            return filtered

        filtered = []
        for node in nodes:
            if isinstance(node, FunctionDeclaration) and getattr(node, 'modifiers', []):
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
        """Check if a node contains external calls using AST analysis."""
        if not hasattr(node, 'raw_node') or not node.raw_node:
            return False

        def check_for_external_calls(ts_node) -> bool:
            """Recursively traverse tree-sitter nodes to find external calls."""
            if not ts_node:
                return False

            node_type = ts_node.type

            # Check for call expressions
            if node_type == "call_expression":
                call_info = self._analyze_call_expression(ts_node)
                if call_info and call_info.get('type') in ['external', 'low_level']:
                    return True

            # Check for member access that might be external calls
            elif node_type == "member_access":
                member_text = ts_node.text.decode('utf-8') if ts_node.text else ''
                if member_text:
                    # Check for low-level calls first
                    if any(method in member_text for method in ['call', 'delegatecall', 'staticcall', 'send', 'transfer']):
                        return True
                    # Check for external contract calls (exclude builtins)
                    builtin_members = {
                        'msg.sender', 'msg.value', 'msg.data', 'msg.sig',
                        'block.timestamp', 'block.number', 'block.coinbase',
                        'tx.origin', 'tx.gasprice'
                    }
                    if '.' in member_text and member_text not in builtin_members:
                        # This could be an external contract call
                        return True

            # Recursively check children
            for child in ts_node.children:
                if check_for_external_calls(child):
                    return True

            return False

        return check_for_external_calls(node.raw_node)

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
        """Check if a node modifies state variables using AST analysis."""
        if not hasattr(node, 'raw_node') or not node.raw_node:
            return False

        def check_for_state_changes(ts_node) -> bool:
            """Recursively traverse tree-sitter nodes to find state changes."""
            if not ts_node:
                return False

            node_type = ts_node.type

            # Check for assignment operations
            if node_type in ["assignment_operator", "assignment_expression"]:
                return True

            # Check for compound assignments (+=, -=, *=, /=)
            elif node_type in ["augmented_assignment_operator", "compound_assignment"]:
                return True

            # Check for update expressions (++, --)
            elif node_type in ["update_expression", "unary_expression"]:
                return self._is_update_expression(ts_node)

            # Check for function calls that modify state
            elif node_type == "call_expression":
                call_info = self._analyze_call_expression(ts_node)
                if call_info:
                    call_name = call_info.get('name', '').lower()
                    # State-modifying function patterns
                    state_modifying_calls = {'push', 'pop', 'delete', 'transfer', 'send'}
                    if any(method in call_name for method in state_modifying_calls):
                        return True

            # Check for member access assignments (e.g., balances[user] = amount)
            elif node_type == "index_access":
                # Check if this index access is on the left side of an assignment
                parent = ts_node.parent
                if parent and parent.type == "assignment_operator":
                    # Check if this is the left operand
                    if parent.children and parent.children[0] == ts_node:
                        return True

            # Check for delete statements
            elif node_type == "delete_statement":
                return True

            # Check for storage variable declarations with assignments
            elif node_type == "variable_declaration":
                var_text = ts_node.text.decode('utf-8') if ts_node.text else ''
                if 'storage' in var_text and '=' in var_text:
                    return True

            # Recursively check children
            for child in ts_node.children:
                if check_for_state_changes(child):
                    return True

            return False

        return check_for_state_changes(node.raw_node)

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches pattern (exact or regex)."""
        try:
            return bool(re.search(pattern, text))
        except re.error:
            # If regex is invalid, try exact match
            return text == pattern

    def _build_query_result_data(self, nodes: List[ASTNode], include: List[str]) -> Dict[str, Any]:
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
                    "visibility": getattr(node, 'visibility', None).value if hasattr(getattr(node, 'visibility', None), 'value') else (str(getattr(node, 'visibility', '')) or None),
                    "state_mutability": getattr(node, 'state_mutability', None).value if hasattr(getattr(node, 'state_mutability', None), 'value') else (str(getattr(node, 'state_mutability', '')) or None),
                    "signature": node.get_signature() if hasattr(node, 'get_signature') else None
                })
            elif isinstance(node, ContractDeclaration):
                result_item.update({
                    "kind": getattr(node, 'kind', None),
                    "inheritance": getattr(node, 'inheritance', [])
                })
            elif isinstance(node, VariableDeclaration):
                result_item.update({
                    "type_name": str(getattr(node, 'type_name', '')),
                    "visibility": getattr(node, 'visibility', None).value if hasattr(getattr(node, 'visibility', None), 'value') else (str(getattr(node, 'visibility', '')) or None),
                    "is_state_variable": (node.is_state_variable() if hasattr(node, 'is_state_variable') and callable(getattr(node, 'is_state_variable')) else (getattr(node, 'visibility', None) is not None))
                })

            # Add included data
            if "source" in include:
                result_item["source_code"] = node.get_source_code() if hasattr(node, 'get_source_code') else None

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
        """Get all nodes of specified element type with caching."""
        # Check cache first
        if element_type in self._nodes_by_type_cache:
            return self._nodes_by_type_cache[element_type]

        # Compute result
        if element_type == "function":
            all_nodes = self._get_all_nodes()
            result = [node for node in all_nodes if isinstance(node, FunctionDeclaration)]
        elif element_type == "contract":
            result = self.source_manager.get_contracts()
        elif element_type == "variable":
            all_nodes = self._get_all_nodes()
            result = [node for node in all_nodes if isinstance(node, VariableDeclaration)]
        elif element_type == "modifier":
            all_nodes = self._get_all_nodes()
            result = [node for node in all_nodes if isinstance(node, ModifierDeclaration)]
        elif element_type == "event":
            all_nodes = self._get_all_nodes()
            result = [node for node in all_nodes if isinstance(node, EventDeclaration)]
        elif element_type == "error":
            all_nodes = self._get_all_nodes()
            result = [node for node in all_nodes if isinstance(node, ErrorDeclaration)]
        elif element_type == "struct":
            all_nodes = self._get_all_nodes()
            result = [node for node in all_nodes if isinstance(node, StructDeclaration)]
        elif element_type == "enum":
            all_nodes = self._get_all_nodes()
            result = [node for node in all_nodes if isinstance(node, EnumDeclaration)]
        else:
            result = []

        # Cache and return
        self._nodes_by_type_cache[element_type] = result
        return result

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
            result["comprehensive_info"] = self._get_comprehensive_element_info(element)

        if include_context:
            result["context"] = self._get_element_context(element)

        return result

    def _get_basic_element_info(self, element: ASTNode) -> Dict[str, Any]:
        """Get basic information about an element."""
        return {
            "name": getattr(element, 'name', None),
            "type": type(element).__name__,
            "location": self._get_node_location(element),
            "signature": element.get_signature() if isinstance(element, FunctionDeclaration) and hasattr(element, 'get_signature') else None
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
            # Include calls in detailed analysis
            info["calls"] = self._get_node_calls(element)

        return info

    def _get_comprehensive_element_info(self, element: ASTNode) -> Dict[str, Any]:
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

    def _find_element_references(self, target_element: ASTNode,
                               reference_type: str, direction: str,
                               max_depth: int, filters: Dict[str, Any],
                               options: Dict[str, Any]) -> Dict[str, Any]:
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

    def _find_element_usages(self, element: ASTNode, _direction: str, _max_depth: int, _filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find where an element is used."""
        usages = []
        element_name = getattr(element, 'name', '')

        if not element_name:
            return usages

        # Search in all relevant nodes (simplified for now)
        search_nodes = self._get_all_nodes()

        for node in search_nodes:
            usage_info = self._analyze_element_usage_in_node(element, node)
            if usage_info:
                # Apply filters if provided (simplified for now)
                if True:  # TODO: implement filtering with _filters
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

    def _find_element_definitions(self, element: ASTNode, _direction: str, _max_depth: int, _filters: Dict[str, Any]) -> List[Dict[str, Any]]:
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

        # Apply filters (simplified for now)
        # TODO: implement filtering with _filters parameter

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
        # Derive contract name from parent_contract when available
        contract_name = None
        if isinstance(node, FunctionDeclaration) and getattr(node, 'parent_contract', None):
            contract_name = getattr(node.parent_contract, 'name', None)
        elif isinstance(node, ContractDeclaration):
            contract_name = getattr(node, 'name', None)

        # Use SourceLocation when available
        file_path = None
        line = None
        column = None
        if hasattr(node, 'source_location') and getattr(node, 'source_location') is not None:
            try:
                loc = node.source_location
                file_path = getattr(loc, 'file_path', None)
                line = getattr(loc, 'start_line', None)
                column = getattr(loc, 'start_column', None)
            except Exception:
                pass

        return {
            "file": file_path,
            "line": line,
            "column": column,
            "contract": contract_name
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

    def _get_related_queries(self, query_type: str, _filters: Dict[str, Any]) -> List[str]:
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

    def _handle_exception(self, function_name: str, parameters: Dict[str, Any],
                         exception: Exception, context: str = "") -> Dict[str, Any]:
        """Handle exceptions with consistent logging and error response."""
        error_msg = f"Error in {function_name}: {str(exception)}"
        if context:
            error_msg += f" (Context: {context})"

        self.logger.error(error_msg, exc_info=True)

        return self._create_error_response(
            function_name,
            parameters,
            [f"Internal error: {str(exception)}"]
        )

    # Scope filtering implementations
    def _node_in_contracts(self, node: ASTNode, contract_names: List[str]) -> bool:
        """Check if node is in specified contracts."""
        if not contract_names:
            return True

        # Determine contract name
        node_contract = None
        if isinstance(node, ContractDeclaration):
            node_contract = getattr(node, 'name', None)
        elif isinstance(node, FunctionDeclaration) and getattr(node, 'parent_contract', None):
            node_contract = getattr(node.parent_contract, 'name', None)
        elif hasattr(node, 'parent_contract') and getattr(node, 'parent_contract', None):
            node_contract = getattr(node.parent_contract, 'name', None)
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

        # If the node itself is a function
        if isinstance(node, FunctionDeclaration):
            node_name = getattr(node, 'name', None)
            if node_name:
                # For function scope filtering, use exact matches
                return node_name in function_names

        # Special handling: for variable declarations, allow filtering by usage in matching functions
        if isinstance(node, VariableDeclaration):
            var_name = getattr(node, 'name', None)
            parent_contract = getattr(node, 'parent_contract', None)
            if var_name and parent_contract:
                # Find functions in the same contract matching the patterns and check if they reference the variable name
                for func in getattr(parent_contract, 'functions', []) or []:
                    for func_name in function_names:
                        if self._matches_pattern(getattr(func, 'name', '') or '', func_name):
                            try:
                                src = func.get_source_code() if hasattr(func, 'get_source_code') else ''
                            except Exception:
                                src = ''
                            if src and var_name in src:
                                return True

        return False

    def _node_in_files(self, node: ASTNode, file_patterns: List[str]) -> bool:
        """Check if node is in specified files."""
        if not file_patterns:
            return True

        node_file = None
        if hasattr(node, 'source_location') and getattr(node, 'source_location') is not None:
            node_file = getattr(node.source_location, 'file_path', None)
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

        node_file = None
        if hasattr(node, 'source_location') and getattr(node, 'source_location') is not None:
            node_file = getattr(node.source_location, 'file_path', None)
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
        # Check parent_contract attribute first (preferred approach)
        if hasattr(node, 'parent_contract') and node.parent_contract:
            inheritance = getattr(node.parent_contract, 'inheritance', [])
            return base_contract in inheritance

        # Fallback to contract attribute
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
            # Check both contract and parent_contract attributes
            node_contract = getattr(node, 'contract', None)
            if not node_contract:
                parent_contract = getattr(node, 'parent_contract', None)
                node_contract = getattr(parent_contract, 'name', None) if parent_contract else None

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
        """Check if node contains asset transfers using AST analysis."""
        if not hasattr(node, 'raw_node') or not node.raw_node:
            return False

        def check_for_asset_transfers(ts_node) -> bool:
            """Recursively traverse tree-sitter nodes to find asset transfers."""
            if not ts_node:
                return False

            node_type = ts_node.type

            # Check for function calls that might be asset transfers
            if node_type == "call_expression":
                call_info = self._analyze_call_expression(ts_node)
                if call_info:
                    call_name = call_info.get('name', '').lower()
                    # Asset transfer function patterns
                    transfer_functions = {
                        'transfer', 'send', 'safetransfer', 'transferfrom', '_transfer'
                    }
                    if any(func in call_name for func in transfer_functions):
                        return True

            # Check for member access that indicates asset transfers
            elif node_type == "member_access":
                member_text = ts_node.text.decode('utf-8') if ts_node.text else ''
                if member_text:
                    # Check for Ether transfer methods
                    ether_transfer_methods = {'transfer', 'send'}
                    if any(f'.{method}' in member_text for method in ether_transfer_methods):
                        return True

            # Check for call expressions with value field (e.g., call{value: amount})
            elif node_type == "call_options":
                # This indicates a call with options like {value: ...}
                options_text = ts_node.text.decode('utf-8') if ts_node.text else ''
                if 'value' in options_text.lower():
                    return True

            # Check for payable cast expressions
            elif node_type == "call_expression":
                # Look for payable(...) patterns
                for child in ts_node.children:
                    if child.type == "identifier":
                        func_name = child.text.decode('utf-8') if child.text else ''
                        if func_name == 'payable':
                            return True

            # Recursively check children
            for child in ts_node.children:
                if check_for_asset_transfers(child):
                    return True

            return False

        return check_for_asset_transfers(node.raw_node)

    def _filter_by_payable(self, nodes: List[ASTNode], is_payable: bool) -> List[ASTNode]:
        """Filter for payable functions."""
        filtered = []
        for node in nodes:
            # Extract the enum value properly
            if hasattr(node, 'state_mutability') and node.state_mutability:
                if hasattr(node.state_mutability, 'value'):
                    mutability_value = node.state_mutability.value.lower()
                else:
                    mutability_value = str(node.state_mutability).lower()
                node_payable = mutability_value == 'payable'
            else:
                node_payable = False

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
            # Call the is_state_variable method if it exists, otherwise check visibility
            if hasattr(node, 'is_state_variable') and callable(getattr(node, 'is_state_variable')):
                node_is_state = node.is_state_variable()
            else:
                # Fallback: state variables typically have visibility
                node_is_state = getattr(node, 'visibility', None) is not None

            if node_is_state == is_state:
                filtered.append(node)
        return filtered

    def _filter_by_statement_types(self, nodes: List[ASTNode], statement_types: List[str]) -> List[ASTNode]:
        """Filter by statement types."""
        if isinstance(statement_types, str):
            statement_types = [statement_types]

        filtered = []
        for node in nodes:
            # Get the node type from the node_type attribute (for ExtractedStatement) or class name
            if hasattr(node, 'node_type') and node.node_type:
                node_type = str(node.node_type).lower()
            else:
                node_type = type(node).__name__.lower()

            # Get source text to check for specific statement content (like require, assert, etc.)
            source_text = getattr(node, 'source_location', None)
            if source_text and hasattr(source_text, 'source_text'):
                source_text = source_text.source_text.lower()
            else:
                source_text = ""

            for stmt_type in statement_types:
                stmt_type_lower = stmt_type.lower()
                # Check both node type and source text content
                if (stmt_type_lower in node_type or
                    (stmt_type_lower in ["require", "assert", "revert"] and
                     stmt_type_lower in source_text and
                     source_text.strip().startswith(stmt_type_lower + "("))):
                    filtered.append(node)
                    break
        return filtered

    def _filter_by_operators(self, nodes: List[ASTNode], operators: List[str]) -> List[ASTNode]:
        """Filter by operators used."""
        filtered = []
        for node in nodes:
            if self._node_uses_operators(node, operators):
                filtered.append(node)
        return filtered

    def _filter_by_access_patterns(self, nodes: List[ASTNode], patterns: List[str]) -> List[ASTNode]:
        """Filter by access patterns."""
        filtered = []
        for node in nodes:
            source = node.get_source_code() if hasattr(node, 'get_source_code') else ''
            if source:
                for pattern in patterns:
                    if self._matches_pattern(source, pattern):
                        filtered.append(node)
                        break
        return filtered

    def _filter_by_call_types(self, nodes: List[ASTNode], call_types: List[str]) -> List[ASTNode]:
        """Filter by call types using AST analysis."""
        filtered = []
        lowered = [ct.lower() for ct in call_types]
        for node in nodes:
            # Get all calls made by this node
            calls = self._get_node_calls(node)
            for call in calls:
                call_name = call.get('name', '') or ''
                call_type_val = (call.get('type', '') or '').lower()
                # Match by explicit type (external, low_level, library) OR substring in name
                if any(ct in call_type_val for ct in lowered) or any(ct in call_name.lower() for ct in lowered):
                        filtered.append(node)
                        break
        return filtered

    def _filter_by_low_level_calls(self, nodes: List[ASTNode], is_low_level: bool) -> List[ASTNode]:
        """Filter for low-level calls using AST analysis."""
        if not is_low_level:
            return nodes

        filtered = []
        for node in nodes:
            # Get all calls made by this node
            calls = self._get_node_calls(node)
            for call in calls:
                call_type = call.get('type', '')
                if call_type == 'low_level':
                    filtered.append(node)
                    break
        return filtered

    def _get_ast_info(self, node: ASTNode) -> Dict[str, Any]:
        """Get AST information for a node."""
        start_line = None
        end_line = None
        column = None
        if hasattr(node, 'source_location') and getattr(node, 'source_location') is not None:
            try:
                start_line = getattr(node.source_location, 'start_line', None)
                end_line = getattr(node.source_location, 'end_line', None)
                column = getattr(node.source_location, 'start_column', None)
            except Exception:
                pass
        return {
            "node_type": type(node).__name__,
            "node_id": getattr(node, 'id', None),
            "start_line": start_line,
            "end_line": end_line,
            "column": column
        }

    def _get_node_calls(self, node: ASTNode) -> List[Dict[str, Any]]:
        """Get function calls made by a node using AST traversal."""
        calls = []

        if not hasattr(node, 'raw_node') or not node.raw_node:
            return calls

        # Track found calls to avoid duplicates
        found_calls = set()

        def traverse_node(ts_node):
            """Recursively traverse tree-sitter nodes to find function calls."""
            if not ts_node:
                return

            node_type = ts_node.type

            # Identify function call patterns
            if node_type == "call_expression":
                call_info = self._analyze_call_expression(ts_node)
                if call_info:
                    call_key = f"{call_info['name']}_{call_info['position']}"
                    if call_key not in found_calls:
                        calls.append(call_info)
                        found_calls.add(call_key)

            elif node_type in ["member_access", "member_expression", "member_access_expression"]:
                # Check if this member access is part of a low-level call
                member_call = self._analyze_member_call(ts_node)
                if member_call:
                    call_key = f"{member_call['name']}_{member_call['position']}"
                    if call_key not in found_calls:
                        calls.append(member_call)
                        found_calls.add(call_key)

            # Recursively traverse children
            for child in ts_node.children:
                traverse_node(child)

        traverse_node(node.raw_node)
        return calls

    def _get_node_statements(self, node: ASTNode) -> List[Dict[str, Any]]:
        """Get statements from a node using AST traversal."""
        statements = []

        if not hasattr(node, 'raw_node') or not node.raw_node:
            return statements

        # Track found statements to avoid duplicates
        found_statements = set()

        def traverse_node(ts_node):
            """Recursively traverse tree-sitter nodes to find statements."""
            if not ts_node:
                return

            node_type = ts_node.type

            # Identify statement patterns
            if node_type in [
                "expression_statement", "return_statement", "if_statement",
                "for_statement", "while_statement", "emit_statement",
                "assembly_statement", "variable_declaration_statement"
            ]:
                stmt_info = self._analyze_statement(ts_node, node)
                if stmt_info:
                    stmt_key = f"{stmt_info['type']}_{stmt_info['position']}"
                    if stmt_key not in found_statements:
                        statements.append(stmt_info)
                        found_statements.add(stmt_key)

            # Continue traversing child nodes
            for child in ts_node.children:
                traverse_node(child)

        traverse_node(node.raw_node)
        return statements

    def _analyze_statement(self, ts_node, parent_node: ASTNode) -> Optional[Dict[str, Any]]:
        """Analyze a statement node to extract statement information."""
        try:
            # Get position in source code
            start_byte = ts_node.start_byte
            end_byte = ts_node.end_byte
            start_point = ts_node.start_point

            # Get source text
            source_text = ""
            if hasattr(self, 'source_manager') and self.source_manager:
                source_text = ts_node.text.decode('utf-8') if ts_node.text else ""

            stmt_info = {
                "type": ts_node.type,
                "source_location": {
                    "start_byte": start_byte,
                    "end_byte": end_byte,
                    "line": start_point[0] + 1,
                    "column": start_point[1]
                },
                "position": f"{start_point[0]}:{start_point[1]}",
                "source_text": source_text[:100] + "..." if len(source_text) > 100 else source_text,
                "parent_contract": getattr(parent_node, 'parent_contract', None),
                "parent_function": getattr(parent_node, 'name', None)
            }

            return stmt_info

        except Exception:
            return None

    def _get_node_expressions(self, node: ASTNode) -> List[Dict[str, Any]]:
        """Get expressions from a node using AST traversal."""
        expressions = []

        if not hasattr(node, 'raw_node') or not node.raw_node:
            return expressions

        # Track found expressions to avoid duplicates
        found_expressions = set()


        self._traverse_node_for_expressions(node.raw_node, expressions, found_expressions, node)
        return expressions

    def _traverse_node_for_expressions(self, ts_node, expressions: List[Dict[str, Any]],
                                     found_expressions: set, parent_node: ASTNode):
        """Recursively traverse tree-sitter nodes to find expressions."""
        if not ts_node:
            return

        node_type = ts_node.type

        # Identify expression patterns
        if node_type in [
            "binary_expression", "unary_expression", "assignment_expression",
            "call_expression", "member_expression", "identifier",
            "literal", "array_expression", "conditional_expression",
            "update_expression", "postfix_expression", "parenthesized_expression"
        ]:
            expr_info = self._analyze_expression(ts_node, parent_node)
            if expr_info:
                expr_key = f"{expr_info['type']}_{expr_info['position']}"
                if expr_key not in found_expressions:
                    expressions.append(expr_info)
                    found_expressions.add(expr_key)

        # Continue traversing child nodes
        for child in ts_node.children:
            self._traverse_node_for_expressions(child, expressions, found_expressions, parent_node)

    def _analyze_expression(self, ts_node, parent_node: ASTNode) -> Optional[Dict[str, Any]]:
        """Analyze an expression node to extract expression information."""
        try:
            # Get position in source code
            start_byte = ts_node.start_byte
            end_byte = ts_node.end_byte
            start_point = ts_node.start_point

            # Get source text
            source_text = ""
            if hasattr(self, 'source_manager') and self.source_manager:
                source_text = ts_node.text.decode('utf-8') if ts_node.text else ""

            expr_info = {
                "type": ts_node.type,
                "source_location": {
                    "start_byte": start_byte,
                    "end_byte": end_byte,
                    "line": start_point[0] + 1,
                    "column": start_point[1]
                },
                "position": f"{start_point[0]}:{start_point[1]}",
                "source_text": source_text[:50] + "..." if len(source_text) > 50 else source_text,
                "parent_contract": getattr(parent_node, 'parent_contract', None),
                "parent_function": getattr(parent_node, 'name', None)
            }

            return expr_info

        except Exception:
            return None

    def _analyze_call_expression(self, ts_node) -> Optional[Dict[str, Any]]:
        """Analyze a call_expression node to extract call information."""
        try:
            # Find the function being called
            function_node = None

            # First check direct children for identifier/member_access/member_expression
            for child in ts_node.children:
                if child.type in ["identifier", "member_access", "member_expression"]:
                    function_node = child
                    break
                # Also check inside expression nodes
                elif child.type == "expression":
                    for expr_child in child.children:
                        if expr_child.type in ["identifier", "member_access", "member_expression"]:
                            function_node = expr_child
                            break
                    if function_node:
                        break

            if not function_node:
                return None

            call_name = function_node.text.decode('utf-8') if function_node.text else None
            if not call_name:
                return None

            # Determine call type based on the function name/structure
            call_type = self._classify_call_type(call_name, function_node)

            return {
                'name': call_name,
                'type': call_type,
                'position': function_node.start_byte,
                'arguments_count': self._count_call_arguments(ts_node)
            }

        except Exception as e:
            self.logger.warning(f"Failed to analyze function call: {str(e)}")
            return None

    def _analyze_member_call(self, ts_node) -> Optional[Dict[str, Any]]:
        """Analyze member access that might be a low-level call."""
        try:
            member_text = ts_node.text.decode('utf-8') if ts_node.text else None
            if not member_text:
                return None

            # Check for low-level call patterns
            low_level_calls = {
                'call', 'delegatecall', 'staticcall', 'send', 'transfer'
            }

            # Extract the method name from member access
            parts = member_text.split('.')
            if len(parts) >= 2:
                method_name = parts[-1]
                if method_name in low_level_calls:
                    return {
                        'name': member_text,
                        'type': 'low_level',
                        'position': ts_node.start_byte,
                        'call_method': method_name
                    }

        except Exception as e:
            self.logger.debug(f"Failed to analyze member call: {str(e)}")
            pass

        return None

    def _classify_call_type(self, call_name: str, _function_node) -> str:
        """Classify the type of function call."""
        # Built-in functions
        builtin_functions = {
            'require', 'assert', 'revert', 'keccak256', 'sha256', 'ripemd160',
            'ecrecover', 'addmod', 'mulmod', 'selfdestruct'
        }

        if call_name in builtin_functions:
            return 'builtin'

        # Member access calls (contract.method or address.method)
        if '.' in call_name:
            parts = call_name.split('.')
            method = parts[-1]

            # True low-level calls on addresses
            if method in {'call', 'delegatecall', 'staticcall', 'send'}:
                return 'low_level'
            else:
                # All other member access calls are considered external
                # This includes transfer(), approve(), balanceOf(), etc.
                return 'external'

        # Library calls (if the function name suggests it)
        if any(lib in call_name.lower() for lib in ['safemath', 'strings', 'address']):
            return 'library'

        # Default to internal for simple identifiers
        return 'internal'

    def _count_call_arguments(self, call_node) -> int:
        """Count the number of arguments in a function call."""
        try:
            # Tree-sitter uses call_argument nodes directly as children
            arg_count = 0
            for child in call_node.children:
                if child.type == "call_argument":
                    arg_count += 1
            return arg_count
        except Exception as e:
            self.logger.debug(f"Failed to count call arguments: {str(e)}")
            pass
        return 0

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
        """Get variables accessed by a node using AST traversal."""
        variables = []

        if not hasattr(node, 'raw_node') or not node.raw_node:
            return variables

        # Track found variables to avoid duplicates
        found_vars = set()

        def traverse_node(ts_node, parent_context=None):
            """Recursively traverse tree-sitter nodes to find variable access."""
            if not ts_node:
                return

            node_type = ts_node.type

            # Skip certain contexts where identifiers are not variables
            skip_contexts = {
                'function_definition', 'constructor_definition', 'modifier_definition',
                'function_call', 'modifier_invocation', 'parameter_list', 'type_name',
                'function_type', 'event_definition', 'struct_definition', 'enum_definition'
            }

            if parent_context in skip_contexts:
                # Still traverse children but don't capture variables in these contexts
                for child in ts_node.children:
                    traverse_node(child, node_type)
                return

            # Handle member access first (e.g., msg.sender, block.timestamp)
            if node_type in ["member_access", "member_expression"]:
                member_info = self._analyze_member_access(ts_node)
                if member_info and member_info['name'] not in found_vars:
                    variables.append(member_info)
                    found_vars.add(member_info['name'])
                # Don't traverse children of member_access to avoid processing individual parts
                return

            # Handle array/mapping access like balances[user]
            elif node_type == "index_access":
                index_info = self._analyze_index_access(ts_node, parent_context)
                if index_info and index_info['name'] not in found_vars:
                    variables.append(index_info)
                    found_vars.add(index_info['name'])
                # Still traverse children to find variables in the index expression

            # Handle standalone identifiers (but only in appropriate contexts)
            elif node_type == "identifier":
                # Skip if this identifier is part of a member access expression
                if parent_context in {'member_access', 'call_expression', 'emit_statement'}:
                    pass  # Skip identifiers in these contexts
                else:
                    var_name = ts_node.text.decode('utf-8') if ts_node.text else None
                    if var_name and var_name not in found_vars:
                        var_info = self._analyze_identifier_context(ts_node, var_name, parent_context)
                        if var_info:
                            variables.append(var_info)
                            found_vars.add(var_name)

            # Recursively traverse children
            for child in ts_node.children:
                traverse_node(child, node_type)

        traverse_node(node.raw_node)
        return variables

    def _analyze_identifier_context(self, ts_node, var_name: str, parent_context: Optional[str]) -> Optional[Dict[str, Any]]:
        """Analyze an identifier node to determine if it's a relevant variable."""
        # Skip common keywords, types, and built-in globals
        excluded_names = {
            # Keywords and control flow
            'require', 'revert', 'assert', 'return', 'if', 'for', 'while', 'do',
            'function', 'modifier', 'emit', 'event', 'struct', 'enum', 'new', 'delete',
            'contract', 'interface', 'library', 'using', 'pragma', 'import', 'is', 'override',

            # Types
            'uint256', 'uint128', 'uint64', 'uint32', 'uint16', 'uint8', 'uint',
            'int256', 'int128', 'int64', 'int32', 'int16', 'int8', 'int',
            'address', 'bool', 'string', 'bytes', 'bytes32', 'bytes4',
            'mapping', 'array',

            # Storage/memory modifiers
            'memory', 'storage', 'calldata',

            # Function modifiers
            'view', 'pure', 'payable', 'constant', 'immutable',
            'public', 'private', 'internal', 'external',

            # Literals and built-ins
            'true', 'false', 'null', 'this', 'super',

            # Built-in globals (individual parts)
            'msg', 'block', 'tx', 'gasleft', 'now',

            # Common identifiers that aren't variables
            'sender', 'value', 'data', 'sig', 'timestamp', 'number', 'coinbase', 'difficulty',
            'origin', 'gasprice',

            # Common function names that get misidentified
            'transfer', 'approve', 'mint', 'burn', 'add', 'sub', 'mul', 'div',
            'safeTransfer', 'safeTransferFrom', '_mint', '_burn', '_transfer', '_approve',
            '_safeMint', '_safeBurn', 'transferFrom', 'increaseAllowance', 'decreaseAllowance',

            # Common modifier names
            'onlyOwner', 'nonReentrant', 'whenNotPaused', 'validAddress',

            # Event names that might be captured
            'Transfer', 'Approval', 'Mint', 'Burn', 'TokenMinted', 'OwnershipTransferred'
        }

        if var_name.lower() in excluded_names:
            return None

        # Determine variable type and access pattern
        var_type = self._classify_variable_type(var_name, parent_context)
        if not var_type:
            return None

        access_type = self._determine_access_type(ts_node)

        return {
            'name': var_name,
            'access_type': access_type,
            'position': ts_node.start_byte,
            'variable_type': var_type
        }

    def _analyze_member_access(self, ts_node) -> Optional[Dict[str, Any]]:
        """Analyze member access expressions like contract.method or object.property."""
        try:
            # Get the full member access text
            member_text = ts_node.text.decode('utf-8') if ts_node.text else None
            if not member_text:
                return None

            # Skip built-in globals - these are NOT variables we want to track
            builtin_globals = {
                'msg.sender', 'msg.value', 'msg.data', 'msg.sig',
                'block.timestamp', 'block.number', 'block.coinbase', 'block.difficulty',
                'tx.origin', 'tx.gasprice', 'gasleft()', 'this.balance'
            }

            if member_text in builtin_globals:
                # These are built-in globals, not variables we want to track
                return None

            # For other member access (like state.property or contract.method),
            # we want to extract the base object as a variable
            parts = member_text.split('.', 1)
            if len(parts) >= 2:
                base_name = parts[0]

                # Skip common patterns that aren't variables
                if base_name in {'msg', 'block', 'tx', 'this', 'super'}:
                    return None

                # This could be a state variable or contract reference
                var_type = self._classify_variable_type(base_name, 'member_access')
                if var_type:
                    return {
                        'name': base_name,
                        'access_type': 'read',
                        'position': ts_node.start_byte,
                        'variable_type': var_type
                    }

        except Exception as e:
            self.logger.debug(f"Failed to analyze index access: {str(e)}")
            pass

        return None

    def _analyze_index_access(self, ts_node, _parent_context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Analyze index access expressions like balances[user]."""
        try:
            # Find the base identifier (what's being indexed)
            base_node = None
            for child in ts_node.children:
                if child.type == "identifier":
                    base_node = child
                    break

            if not base_node:
                return None

            var_name = base_node.text.decode('utf-8') if base_node.text else None
            if not var_name:
                return None

            # Classify the variable type
            var_type = self._classify_variable_type(var_name, 'index_access')
            if not var_type:
                return None

            access_type = self._determine_access_type(ts_node)

            return {
                'name': var_name,
                'access_type': access_type,
                'position': base_node.start_byte,
                'variable_type': var_type
            }

        except Exception as e:
            self.logger.debug(f"Failed to classify variable type: {str(e)}")
            pass

        return None

    def _classify_variable_type(self, _var_name: str, context: Optional[str]) -> Optional[str]:
        """Classify variable type based on context only, no patterns."""

        # Context-based classification only
        if context == 'index_access':
            return 'array_access'
        elif context == 'member_access':
            return 'member_reference'

        # Return generic type for all other variables
        return 'variable'

    def _find_variable_declaration(self, var_name: str) -> Optional[Dict[str, str]]:
        """Find variable declaration using AST traversal."""

        # Search through all loaded AST nodes for variable declarations
        for contract in self.parser.parsed_contracts:
            for node in contract.all_nodes:
                # Check state variable declarations
                if hasattr(node, 'node_type') and 'VariableDeclaration' in str(node.node_type):
                    if hasattr(node, 'name') and node.name == var_name:
                        # Check if it's a state variable (declared at contract level)
                        if hasattr(node, 'is_state_variable') and node.is_state_variable:
                            visibility = getattr(node, 'visibility', 'internal')
                            if visibility in ['public', 'external']:
                                return {'type': 'public_state_variable'}
                            else:
                                return {'type': 'state_variable'}
                        else:
                            return {'type': 'local_variable'}

                # Check function parameters
                elif hasattr(node, 'node_type') and 'FunctionDeclaration' in str(node.node_type):
                    if hasattr(node, 'parameters'):
                        for param in node.parameters:
                            if hasattr(param, 'name') and param.name == var_name:
                                return {'type': 'parameter'}

                # Check struct members, enum values, etc.
                elif hasattr(node, 'node_type') and 'StructDeclaration' in str(node.node_type):
                    if hasattr(node, 'members'):
                        for member in node.members:
                            if hasattr(member, 'name') and member.name == var_name:
                                return {'type': 'struct_member'}

        return None

    def _is_builtin_global_access(self, ts_node) -> bool:
        """Check if this is a built-in global access using AST structure."""
        if not ts_node or not ts_node.children:
            return False

        # Check if this is msg.*, block.*, tx.* access
        children = [child for child in ts_node.children if child.type == 'identifier']
        if len(children) >= 1:
            base_name = children[0].text.decode('utf-8') if children[0].text else ''
            return base_name in ['msg', 'block', 'tx', 'abi', 'address']
        return False

    def _is_low_level_call(self, ts_node) -> bool:
        """Check if this is a low-level call using AST structure."""
        member_text = ts_node.text.decode('utf-8') if ts_node.text else ''
        if not member_text or '.' not in member_text:
            return False

        # Extract method name from AST structure
        for child in ts_node.children:
            if child.type == 'identifier':
                method_name = child.text.decode('utf-8') if child.text else ''
                # Check the last identifier for low-level methods
                if method_name in ['call', 'delegatecall', 'staticcall', 'send']:
                    return True
        return False

    def _is_external_contract_call(self, ts_node) -> bool:
        """Check if this is an external contract call using AST structure."""
        # If it's not a built-in global and has a dot, likely external
        return not self._is_builtin_global_access(ts_node)

    def _is_update_expression(self, ts_node) -> bool:
        """Check if this is an update expression (++/--) using AST structure."""
        # Look for increment/decrement operators in the node's children
        for child in ts_node.children:
            if child.type in ["++", "--", "increment_expression", "decrement_expression"]:
                return True
        return False

    def _node_uses_operators(self, node: ASTNode, operators: List[str]) -> bool:
        """Check if node uses specific operators using AST analysis."""
        # Fallback to source code analysis if no raw_node available (for ExtractedExpression/ExtractedStatement)
        if not hasattr(node, 'raw_node') or not node.raw_node:
            source_code = node.get_source_code() if hasattr(node, 'get_source_code') else ''
            if source_code:
                return any(op in source_code for op in operators)
            return False

        def check_operators(ts_node) -> bool:
            if not ts_node:
                return False

            # Map operator strings to AST node types
            operator_node_types = {
                '+': ['binary_expression'],
                '-': ['binary_expression'],
                '*': ['binary_expression'],
                '/': ['binary_expression'],
                '%': ['binary_expression'],
                '++': ['update_expression', 'increment_expression'],
                '--': ['update_expression', 'decrement_expression'],
                '+=': ['augmented_assignment_operator'],
                '-=': ['augmented_assignment_operator'],
                '*=': ['augmented_assignment_operator'],
                '/=': ['augmented_assignment_operator'],
                '==': ['binary_expression'],
                '!=': ['binary_expression'],
                '<': ['binary_expression'],
                '>': ['binary_expression'],
                '<=': ['binary_expression'],
                '>=': ['binary_expression'],
                '&&': ['binary_expression'],
                '||': ['binary_expression'],
                '!': ['unary_expression']
            }

            # Check if this node type matches any requested operators
            for op in operators:
                if op in operator_node_types:
                    if ts_node.type in operator_node_types[op]:
                        return True

            # Recursively check children
            for child in ts_node.children:
                if check_operators(child):
                    return True

            return False

        return check_operators(node.raw_node)

    def _determine_access_type(self, ts_node) -> str:
        """Determine if this is a read or write access."""
        # Walk up the parent chain to see if this is part of an assignment
        parent = ts_node.parent
        while parent:
            if parent.type == "assignment_operator":
                # Check if our node is on the left side (write) or right side (read)
                for i, child in enumerate(parent.children):
                    if self._node_contains(child, ts_node):
                        return 'write' if i == 0 else 'read'
            elif parent.type in ["variable_declaration", "state_variable_declaration"]:
                return 'write'
            parent = parent.parent

        return 'read'

    def _node_contains(self, ancestor, descendant) -> bool:
        """Check if ancestor node contains descendant node."""
        return (ancestor.start_byte <= descendant.start_byte and
                ancestor.end_byte >= descendant.end_byte)

    def _get_node_events(self, node: ASTNode) -> List[Dict[str, Any]]:
        """Get events emitted by a node using AST analysis."""
        events = []

        if not hasattr(node, 'raw_node') or not node.raw_node:
            return events

        def find_emit_statements(ts_node):
            """Recursively find emit statements in the AST."""
            if not ts_node:
                return

            node_type = ts_node.type

            # Look for emit statements
            if node_type == "emit_statement":
                # Find the event name being emitted
                for child in ts_node.children:
                    if child.type == "expression":
                        # Find the event identifier within the expression
                        for expr_child in child.children:
                            if expr_child.type == "identifier":
                                event_name = expr_child.text.decode('utf-8') if expr_child.text else None
                                if event_name:
                                    events.append({
                                        'name': event_name,
                                        'position': expr_child.start_byte
                                    })
                                break
                        break

            # Also look for emit keyword followed by call expressions
            elif node_type == "identifier" and ts_node.text and ts_node.text.decode('utf-8') == "emit":
                # Check if the next sibling is a call expression
                parent = ts_node.parent
                if parent:
                    found_emit = False
                    for child in parent.children:
                        if child == ts_node:
                            found_emit = True
                        elif found_emit and child.type == "call_expression":
                            # Extract event name from the call
                            for call_child in child.children:
                                if call_child.type == "identifier":
                                    event_name = call_child.text.decode('utf-8') if call_child.text else None
                                    if event_name:
                                        events.append({
                                            'name': event_name,
                                            'position': call_child.start_byte
                                        })
                                    break
                            break

            # Recursively check children
            for child in ts_node.children:
                find_emit_statements(child)

        find_emit_statements(node.raw_node)
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
        """Get dependencies of a node using AST analysis."""
        dependencies = []

        if not hasattr(node, 'raw_node') or not node.raw_node:
            return dependencies

        def find_dependencies(ts_node):
            """Recursively find dependencies in the AST."""
            if not ts_node:
                return

            node_type = ts_node.type

            # Look for import statements
            if node_type == "import_directive":
                for child in ts_node.children:
                    if child.type == "string":
                        import_path = child.text.decode('utf-8').strip('"\'') if child.text else None
                        if import_path:
                            dependencies.append(import_path)

            # Look for using directives
            elif node_type == "using_for_directive":
                for child in ts_node.children:
                    if child.type == "identifier":
                        library_name = child.text.decode('utf-8') if child.text else None
                        if library_name:
                            dependencies.append(library_name)
                            break

            # Look for inheritance
            elif node_type == "inheritance_specifier":
                for child in ts_node.children:
                    if child.type == "user_defined_type":
                        # Get the inherited contract name
                        for type_child in child.children:
                            if type_child.type == "identifier":
                                base_contract = type_child.text.decode('utf-8') if type_child.text else None
                                if base_contract:
                                    dependencies.append(base_contract)
                                    break

            # Recursively check children
            for child in ts_node.children:
                find_dependencies(child)

        # For contracts, we need to look at the source unit (file level) to find imports
        source_node = node.raw_node

        # Navigate to the source unit (root of the file) to find imports
        while source_node.parent:
            source_node = source_node.parent

        # First, find imports at source level
        find_dependencies(source_node)

        # Then, find contract-specific dependencies (inheritance, using directives)
        find_dependencies(node.raw_node)

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