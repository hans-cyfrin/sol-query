"""JSON serialization utilities for LLM integration."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from sol_query.core.ast_nodes import ASTNode, ContractDeclaration, FunctionDeclaration
from sol_query.query.collections import BaseCollection


def serialize_enum_value(enum_obj):
    """
    Utility function to safely serialize enum values to strings.
    
    Args:
        enum_obj: The enum object to serialize
        
    Returns:
        str: The enum's string value if it's a proper enum, otherwise string representation or None
    """
    if enum_obj is None:
        return None
    if hasattr(enum_obj, 'value'):
        return enum_obj.value
    return str(enum_obj) if enum_obj else None


class SerializationLevel(str, Enum):
    """Levels of detail for serialization."""
    SUMMARY = "summary"      # Basic info only
    DETAILED = "detailed"    # More comprehensive info
    FULL = "full"           # Complete information including source code


class LLMSerializer:
    """Serializes query results for LLM consumption with configurable detail levels."""

    def __init__(self, level: SerializationLevel = SerializationLevel.DETAILED):
        """
        Initialize serializer.
        
        Args:
            level: Default serialization detail level
        """
        self.level = level

    def serialize_node(self, node: ASTNode,
                      level: Optional[SerializationLevel] = None) -> Dict[str, Any]:
        """
        Serialize a single AST node.
        
        Args:
            node: The AST node to serialize
            level: Serialization level (uses default if not specified)
            
        Returns:
            Dictionary representation suitable for JSON
        """
        level = level or self.level

        # Base information for all nodes
        result = {
            "node_type": node.node_type.value,
            "source_code_preview": self._create_source_preview(node.get_source_code()),
            "source_location": self._serialize_location(node.source_location, level)
        }

        # Add type-specific information
        if isinstance(node, ContractDeclaration):
            result.update(self._serialize_contract(node, level))
        elif isinstance(node, FunctionDeclaration):
            result.update(self._serialize_function(node, level))
        else:
            # Generic serialization for other node types
            result.update(self._serialize_generic_node(node, level))

        return result

    def serialize_collection(self, collection: BaseCollection,
                           level: Optional[SerializationLevel] = None,
                           limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Serialize a collection of nodes.
        
        Args:
            collection: The collection to serialize
            level: Serialization level
            limit: Maximum number of items to include
            
        Returns:
            Dictionary with collection metadata and items
        """
        level = level or self.level
        items = list(collection)

        if limit:
            items = items[:limit]

        return {
            "collection_type": type(collection).__name__,
            "total_count": len(collection),
            "returned_count": len(items),
            "items": [self.serialize_node(item, level) for item in items]
        }

    def serialize_query_result(self, result: Union[ASTNode, BaseCollection, List[ASTNode]],
                              level: Optional[SerializationLevel] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Serialize any query result with metadata.
        
        Args:
            result: The query result to serialize
            level: Serialization level
            metadata: Additional metadata to include
            
        Returns:
            Complete serialized result with metadata
        """
        level = level or self.level

        # Build response
        response = {
            "query_timestamp": datetime.now().isoformat(),
            "serialization_level": level.value,
            "metadata": metadata or {}
        }

        # Serialize the result based on type
        if isinstance(result, BaseCollection):
            response["result"] = self.serialize_collection(result, level)
            response["result_type"] = "collection"
        elif isinstance(result, list):
            response["result"] = {
                "items": [self.serialize_node(item, level) for item in result],
                "count": len(result)
            }
            response["result_type"] = "list"
        elif isinstance(result, ASTNode):
            response["result"] = self.serialize_node(result, level)
            response["result_type"] = "single_node"
        else:
            response["result"] = str(result)
            response["result_type"] = "other"

        return response

    def to_json(self, data: Any, indent: Optional[int] = 2) -> str:
        """
        Convert data to JSON string.
        
        Args:
            data: Data to serialize
            indent: JSON indentation (None for compact)
            
        Returns:
            JSON string
        """
        return json.dumps(data, indent=indent, default=self._json_serializer)

    def _serialize_location(self, location, level: SerializationLevel) -> Dict[str, Any]:
        """Serialize source location information."""
        result = {
            "start_line": location.start_line,
            "start_column": location.start_column,
            "end_line": location.end_line,
            "end_column": location.end_column
        }

        if level in [SerializationLevel.DETAILED, SerializationLevel.FULL]:
            result.update({
                "start_byte": location.start_byte,
                "end_byte": location.end_byte,
                "file_path": str(location.file_path) if location.file_path else None
            })

        if level == SerializationLevel.FULL:
            result["source_text"] = location.source_text

        return result

    def _serialize_contract(self, contract: ContractDeclaration,
                           level: SerializationLevel) -> Dict[str, Any]:
        """Serialize contract-specific information."""
        result = {
            "name": contract.name,
            "kind": contract.kind,
            "inheritance": contract.inheritance
        }

        if level == SerializationLevel.SUMMARY:
            result.update({
                "function_count": len(contract.functions),
                "event_count": len(contract.events),
                "modifiers": [m.name for m in contract.modifiers],
                "variable_count": len(contract.variables)
            })
        elif level in [SerializationLevel.DETAILED, SerializationLevel.FULL]:
            result.update({
                "functions": [self._serialize_function_summary(f) for f in contract.functions],
                "events": [self._serialize_event_summary(e) for e in contract.events],
                "modifiers": [self._serialize_modifier_summary(m) for m in contract.modifiers],
                "variables": [self._serialize_variable_summary(v) for v in contract.variables]
            })

            if level == SerializationLevel.FULL:
                result.update({
                    "structs": [self._serialize_struct_summary(s) for s in contract.structs],
                    "enums": [self._serialize_enum_summary(e) for e in contract.enums],
                    "errors": [self._serialize_error_summary(e) for e in contract.errors]
                })

        return result

    def _serialize_function(self, function: FunctionDeclaration,
                           level: SerializationLevel) -> Dict[str, Any]:
        """Serialize function-specific information."""
        result = {
            "name": function.name,
            "visibility": function.visibility.value,
            "state_mutability": function.state_mutability.value,
            "signature": function.get_signature()
        }

        if level == SerializationLevel.SUMMARY:
            result.update({
                "parameter_count": len(function.parameters),
                "return_parameter_count": len(function.return_parameters),
                "modifiers": function.modifiers
            })
        elif level in [SerializationLevel.DETAILED, SerializationLevel.FULL]:
            result.update({
                "is_constructor": function.is_constructor,
                "is_receive": function.is_receive,
                "is_fallback": function.is_fallback,
                "is_virtual": function.is_virtual,
                "is_override": function.is_override,
                "modifiers": function.modifiers,
                "parameters": [self._serialize_parameter_summary(p) for p in function.parameters],
                "return_parameters": [self._serialize_parameter_summary(p) for p in function.return_parameters]
            })

            if level == SerializationLevel.FULL and function.body:
                result["has_body"] = True

        return result

    def _serialize_generic_node(self, node: ASTNode, level: SerializationLevel) -> Dict[str, Any]:
        """Serialize generic node information."""
        result = {}

        # Add common attributes
        if hasattr(node, 'name'):
            result["name"] = node.name

        if hasattr(node, 'type_name'):
            result["type"] = node.type_name

        if hasattr(node, 'visibility'):
            result["visibility"] = node.visibility.value if node.visibility else None

        return result

    def _serialize_function_summary(self, function: FunctionDeclaration) -> Dict[str, Any]:
        """Create a summary of a function for inclusion in contract serialization."""
        return {
            "name": function.name,
            "visibility": function.visibility.value,
            "state_mutability": function.state_mutability.value,
            "signature": function.get_signature(),
            "is_constructor": function.is_constructor,
            "modifiers": function.modifiers
        }

    def _serialize_variable_summary(self, variable) -> Dict[str, Any]:
        """Create a summary of a variable."""
        return {
            "name": variable.name,
            "type": variable.type_name,
            "visibility": variable.visibility.value if variable.visibility else None,
            "is_constant": variable.is_constant,
            "is_immutable": variable.is_immutable,
            "is_state_variable": variable.is_state_variable()
        }

    def _serialize_event_summary(self, event) -> Dict[str, Any]:
        """Create a summary of an event."""
        return {
            "name": event.name,
            "parameter_count": len(event.parameters)
        }

    def _serialize_modifier_summary(self, modifier) -> Dict[str, Any]:
        """Create a summary of a modifier."""
        return {
            "name": modifier.name,
            "parameter_count": len(modifier.parameters)
        }

    def _serialize_struct_summary(self, struct) -> Dict[str, Any]:
        """Create a summary of a struct."""
        return {
            "name": struct.name,
            "member_count": len(struct.members)
        }

    def _serialize_enum_summary(self, enum) -> Dict[str, Any]:
        """Create a summary of an enum."""
        return {
            "name": enum.name,
            "values": enum.values
        }

    def _serialize_error_summary(self, error) -> Dict[str, Any]:
        """Create a summary of an error."""
        return {
            "name": error.name,
            "parameter_count": len(error.parameters)
        }

    def _serialize_parameter_summary(self, parameter) -> Dict[str, Any]:
        """Create a summary of a parameter."""
        return {
            "name": parameter.name,
            "type": parameter.type_name,
            "storage_location": parameter.storage_location
        }

    def _create_source_preview(self, source_code: str) -> str:
        """Create a preview of source code, limiting to first 100 + last 100 chars if too long."""
        if len(source_code) <= 200:
            return source_code

        # Take first 100 characters and last 100 characters
        first_part = source_code[:100]
        last_part = source_code[-100:]
        return f"{first_part}...{last_part}"

    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for special types."""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, BaseModel):
            return obj.model_dump()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return str(obj)


class ResultPaginator:
    """Handles pagination of large result sets."""

    def __init__(self, page_size: int = 50):
        """
        Initialize paginator.
        
        Args:
            page_size: Number of items per page
        """
        self.page_size = page_size

    def paginate(self, items: List[Any], page: int = 1) -> Dict[str, Any]:
        """
        Paginate a list of items.
        
        Args:
            items: List of items to paginate
            page: Page number (1-indexed)
            
        Returns:
            Paginated result with metadata
        """
        total_items = len(items)
        total_pages = (total_items + self.page_size - 1) // self.page_size

        start_idx = (page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_items)

        page_items = items[start_idx:end_idx]

        return {
            "items": page_items,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "page_size": self.page_size,
                "total_items": total_items,
                "start_index": start_idx,
                "end_index": end_idx - 1,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }


class LLMQueryResponse:
    """Structured response for LLM tool calls."""

    def __init__(self,
                 success: bool,
                 data: Optional[Any] = None,
                 error: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize response.
        
        Args:
            success: Whether the query was successful
            data: The query result data
            error: Error message if unsuccessful
            metadata: Additional metadata
        """
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

        if self.success:
            result["data"] = self.data
        else:
            result["error"] = self.error

        return result

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Convert response to JSON string."""
        serializer = LLMSerializer()
        return serializer.to_json(self.to_dict(), indent)