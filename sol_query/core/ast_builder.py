"""AST builder that converts tree-sitter nodes to our AST representation."""

import logging
from typing import Dict, List, Optional, Union, Any

import tree_sitter

from sol_query.core.ast_nodes import (
    ASTNode, ContractDeclaration, FunctionDeclaration, VariableDeclaration,
    ModifierDeclaration, EventDeclaration, ErrorDeclaration, StructDeclaration,
    EnumDeclaration, Parameter, Block, Statement, Expression, Identifier,
    Literal, CallExpression, BinaryExpression, ArrayAccess, SliceAccess,
    ParenthesizedExpression, InlineArrayExpression, NewExpression, StructExpression,
    ReturnStatement, ExpressionStatement, GenericStatement,
    Visibility, StateMutability, NodeType
)
from sol_query.core.parser import SolidityParser
from sol_query.models.source_location import SourceLocation
from sol_query.analysis.call_analyzer import CallAnalyzer

logger = logging.getLogger(__name__)


class ASTBuilder:
    """Builds our AST representation from tree-sitter nodes."""

    def __init__(self, parser: SolidityParser, source_code: str, file_path: Optional[Any] = None):
        """
        Initialize the AST builder.
        
        Args:
            parser: The SolidityParser instance
            source_code: Original source code
            file_path: Optional path to the source file
        """
        self.parser = parser
        self.source_code = source_code
        self.file_path = file_path
        self.call_analyzer = CallAnalyzer()

        # Mapping of tree-sitter node types to our AST node types
        self.node_type_mapping = {
            "contract_declaration": self._build_contract,
            "interface_declaration": self._build_contract,
            "library_declaration": self._build_contract,
            "function_definition": self._build_function,
            "constructor_definition": self._build_function,
            "modifier_definition": self._build_modifier,
            "variable_declaration": self._build_variable,
            "state_variable_declaration": self._build_variable,
            "event_definition": self._build_event,
            "error_definition": self._build_error,
            "error_declaration": self._build_error,  # Added this mapping
            "struct_definition": self._build_struct,
            "enum_definition": self._build_enum,
            "parameter": self._build_parameter,
            "error_parameter": self._build_parameter,  # Added this mapping
            "event_parameter": self._build_parameter,  # Added this mapping
            "block": self._build_block,
            "function_body": self._build_function_body,
            "statement": self._build_statement,
            "return_statement": self._build_return,
            "expression_statement": self._build_expression_statement,
            "variable_declaration_statement": self._build_variable_declaration_statement,
            "if_statement": self._build_if_statement,
            "for_statement": self._build_for_statement,
            "while_statement": self._build_while_statement,
            "identifier": self._build_identifier,
            "number_literal": self._build_literal,
            "string_literal": self._build_literal,
            "boolean_literal": self._build_literal,
            "call_expression": self._build_call,
            "binary_expression": self._build_binary,
            "unary_expression": self._build_unary,
            "assignment_expression": self._build_assignment,
            "augmented_assignment_expression": self._build_augmented_assignment,
            "member_expression": self._build_member_expression,
            "member_access_expression": self._build_member_access,
            "ternary_expression": self._build_ternary,
            "tuple_expression": self._build_tuple,
            "type_cast_expression": self._build_type_cast,
            "update_expression": self._build_update,
            "meta_type_expression": self._build_meta_type,
            "payable_conversion_expression": self._build_payable_conversion,
            "struct_expression": self._build_struct_expression,
            "parenthesized_expression": self._build_parenthesized,
            "parenthesized": self._build_parenthesized,
            "array_access": self._build_array_access,
            "slice_access": self._build_slice_access,
            "inline_array_expression": self._build_inline_array,
            "new_expression": self._build_new_expression,
            "user_defined_type": self._build_user_defined_type_expr,
            "primitive_type": self._build_primitive_type_expr,
            "expression": self._build_expression,  # Handle generic expression nodes
        }

    def build_ast(self, tree: tree_sitter.Tree) -> List[ASTNode]:
        """
        Build AST from a tree-sitter tree.
        
        Args:
            tree: The parsed tree-sitter tree
            
        Returns:
            List of top-level AST nodes
        """
        root_node = tree.root_node
        return self._build_children(root_node)

    def build_node(self, node: tree_sitter.Node) -> Optional[ASTNode]:
        """
        Build a single AST node from a tree-sitter node.
        
        Args:
            node: The tree-sitter node to convert
            
        Returns:
            The corresponding AST node, or None if not supported
        """
        node_type = node.type

        if node_type in self.node_type_mapping:
            try:
                return self.node_type_mapping[node_type](node)
            except Exception as e:
                logger.warning(f"Failed to build node of type {node_type}: {e}")
                return None

        # For unsupported node types, try to find supported children
        logger.debug(f"Unsupported node type: {node_type}")
        return None

    def _get_source_location(self, node: tree_sitter.Node) -> SourceLocation:
        """Get source location for a tree-sitter node."""
        return self.parser.get_source_location(node, self.source_code, self.file_path)

    def _build_children(self, node: tree_sitter.Node) -> List[ASTNode]:
        """Build AST nodes for all supported children of a tree-sitter node."""
        children = []
        for child in node.children:
            ast_node = self.build_node(child)
            if ast_node:
                children.append(ast_node)
            else:
                # Recursively check grandchildren
                children.extend(self._build_children(child))
        return children

    def _get_node_text(self, node: tree_sitter.Node) -> str:
        """Get the text content of a tree-sitter node."""
        return self.source_code[node.start_byte:node.end_byte]

    def _find_child_by_type(self, node: tree_sitter.Node, node_type: str) -> Optional[tree_sitter.Node]:
        """Find the first child node of a specific type."""
        for child in node.children:
            if child.type == node_type:
                return child
        return None

    def _find_children_by_type(self, node: tree_sitter.Node, node_type: str) -> List[tree_sitter.Node]:
        """Find all child nodes of a specific type."""
        return [child for child in node.children if child.type == node_type]

    def _build_contract(self, node: tree_sitter.Node) -> ContractDeclaration:
        """Build a contract declaration."""
        # Determine contract kind
        kind_map = {
            "contract_declaration": "contract",
            "interface_declaration": "interface",
            "library_declaration": "library"
        }
        kind = kind_map.get(node.type, "contract")

        # Get contract name
        name_node = self._find_child_by_type(node, "identifier")
        name = self._get_node_text(name_node) if name_node else "Unknown"

        # Get inheritance
        inheritance = []
        inheritance_node = self._find_child_by_type(node, "inheritance_specifier")
        if inheritance_node:
            # Look for user_defined_type nodes which contain the inheritance identifiers
            for type_node in self._find_children_by_type(inheritance_node, "user_defined_type"):
                identifier = self._find_child_by_type(type_node, "identifier")
                if identifier:
                    inheritance.append(self._get_node_text(identifier))
            # Also check for direct identifiers (fallback)
            for identifier in self._find_children_by_type(inheritance_node, "identifier"):
                inheritance.append(self._get_node_text(identifier))

        # Create contract
        contract = ContractDeclaration(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            kind=kind,
            inheritance=inheritance
        )

        # Build child elements
        body_node = self._find_child_by_type(node, "contract_body")
        if body_node:
            children = self._build_children(body_node)
            for child in children:
                if isinstance(child, FunctionDeclaration):
                    child.parent_contract = contract  # Set parent reference
                    contract.functions.append(child)
                elif isinstance(child, ModifierDeclaration):
                    contract.modifiers.append(child)
                elif isinstance(child, VariableDeclaration):
                    child.parent_contract = contract  # Set parent reference
                    contract.variables.append(child)
                elif isinstance(child, EventDeclaration):
                    contract.events.append(child)
                elif isinstance(child, ErrorDeclaration):
                    contract.errors.append(child)
                elif isinstance(child, StructDeclaration):
                    contract.structs.append(child)
                elif isinstance(child, EnumDeclaration):
                    contract.enums.append(child)

        return contract

    def _build_function(self, node: tree_sitter.Node) -> FunctionDeclaration:
        """Build a function declaration."""
        # Get function name
        if node.type == "constructor_definition":
            name = "constructor"
        else:
            name_node = self._find_child_by_type(node, "identifier")
            name = self._get_node_text(name_node) if name_node else "unknown"

        # Check for special function types
        is_constructor = (node.type == "constructor_definition" or name == "constructor")
        is_receive = name == "receive"
        is_fallback = name == "fallback"

        # Parse modifiers
        visibility = Visibility.INTERNAL  # Default
        state_mutability = StateMutability.NONPAYABLE  # Default
        is_virtual = False
        is_override = False
        modifiers = []

        # Parse visibility
        visibility_node = self._find_child_by_type(node, "visibility")
        if visibility_node:
            visibility_text = self._get_node_text(visibility_node)
            try:
                visibility = Visibility(visibility_text)
            except ValueError:
                pass

        # Parse state mutability
        state_mutability_node = self._find_child_by_type(node, "state_mutability")
        if state_mutability_node:
            mutability_text = self._get_node_text(state_mutability_node)
            try:
                state_mutability = StateMutability(mutability_text)
            except ValueError:
                pass

        # Parse override specifier
        override_node = self._find_child_by_type(node, "override_specifier")
        if override_node:
            is_override = True

        # Parse modifier invocations
        for modifier_node in self._find_children_by_type(node, "modifier_invocation"):
            modifier_text = self._get_node_text(modifier_node)
            # Extract just the modifier name (before any parentheses)
            modifier_name = modifier_text.split('(')[0].strip()
            if modifier_name:
                modifiers.append(modifier_name)

        # Get parameters
        parameters = []
        param_list_node = self._find_child_by_type(node, "parameter_list")
        if param_list_node:
            for param_node in self._find_children_by_type(param_list_node, "parameter"):
                param = self.build_node(param_node)
                if param and isinstance(param, Parameter):
                    parameters.append(param)

        # Get return parameters
        return_parameters = []
        returns_node = self._find_child_by_type(node, "return_type_definition")
        if returns_node:
            return_param_list = self._find_child_by_type(returns_node, "parameter_list")
            if return_param_list:
                for param_node in self._find_children_by_type(return_param_list, "parameter"):
                    param = self.build_node(param_node)
                    if param and isinstance(param, Parameter):
                        return_parameters.append(param)

        # Get function body
        body = None
        # Try both "block" and "function_body" node types
        body_node = self._find_child_by_type(node, "block") or self._find_child_by_type(node, "function_body")
        if body_node:
            body_ast = self.build_node(body_node)
            if isinstance(body_ast, Block):
                body = body_ast

        function = FunctionDeclaration(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            visibility=visibility,
            state_mutability=state_mutability,
            is_constructor=is_constructor,
            is_receive=is_receive,
            is_fallback=is_fallback,
            is_virtual=is_virtual,
            is_override=is_override,
            parameters=parameters,
            return_parameters=return_parameters,
            modifiers=modifiers,
            body=body
        )

        # Analyze function for external calls and asset transfers
        self.call_analyzer.analyze_function(function)

        return function

    def _build_variable(self, node: tree_sitter.Node) -> VariableDeclaration:
        """Build a variable declaration."""
        # Get variable name
        name_node = self._find_child_by_type(node, "identifier")
        name = self._get_node_text(name_node) if name_node else "unknown"

        # Get type
        type_node = self._find_child_by_type(node, "type_name")
        type_name = self._get_node_text(type_node) if type_node else "unknown"

        # Check for state variable modifiers
        visibility = None
        is_constant = False
        is_immutable = False

        for modifier_node in self._find_children_by_type(node, "visibility"):
            modifier_text = self._get_node_text(modifier_node)
            try:
                visibility = Visibility(modifier_text)
            except ValueError:
                pass

        # Check for constant/immutable keywords
        for child in node.children:
            if child.type in ["constant", "immutable"]:
                if child.type == "constant":
                    is_constant = True
                elif child.type == "immutable":
                    is_immutable = True

        # Get initial value
        initial_value = None
        # Look for assignment expression
        for child in node.children:
            if child.type == "=":
                # Next sibling should be the value
                value_node = child.next_sibling
                if value_node:
                    initial_value_ast = self.build_node(value_node)
                    if isinstance(initial_value_ast, Expression):
                        initial_value = initial_value_ast
                break

        return VariableDeclaration(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            type_name=type_name,
            visibility=visibility,
            is_constant=is_constant,
            is_immutable=is_immutable,
            initial_value=initial_value
        )

    def _build_modifier(self, node: tree_sitter.Node) -> ModifierDeclaration:
        """Build a modifier declaration."""
        # Get modifier name
        name_node = self._find_child_by_type(node, "identifier")
        name = self._get_node_text(name_node) if name_node else "unknown"

        # Get parameters
        parameters = []
        param_list_node = self._find_child_by_type(node, "parameter_list")
        if param_list_node:
            for param_node in self._find_children_by_type(param_list_node, "parameter"):
                param = self.build_node(param_node)
                if param and isinstance(param, Parameter):
                    parameters.append(param)

        # Get body
        body = None
        body_node = self._find_child_by_type(node, "block")
        if body_node:
            body_ast = self.build_node(body_node)
            if isinstance(body_ast, Block):
                body = body_ast

        return ModifierDeclaration(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            parameters=parameters,
            body=body
        )

    def _build_event(self, node: tree_sitter.Node) -> EventDeclaration:
        """Build an event declaration."""
        # Get event name
        name_node = self._find_child_by_type(node, "identifier")
        name = self._get_node_text(name_node) if name_node else "unknown"

        # Get parameters
        parameters = []
        param_list_node = self._find_child_by_type(node, "parameter_list")
        if param_list_node:
            for param_node in self._find_children_by_type(param_list_node, "parameter"):
                param = self.build_node(param_node)
                if param and isinstance(param, Parameter):
                    parameters.append(param)

        return EventDeclaration(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            parameters=parameters
        )

    def _build_error(self, node: tree_sitter.Node) -> ErrorDeclaration:
        """Build an error declaration."""
        # Get error name
        name_node = self._find_child_by_type(node, "identifier")
        name = self._get_node_text(name_node) if name_node else "unknown"

        # Get parameters - error parameters are direct children of error_declaration
        parameters = []

        # First try to find parameters in a parameter_list (standard structure)
        param_list_node = self._find_child_by_type(node, "parameter_list")
        if param_list_node:
            for param_node in self._find_children_by_type(param_list_node, "parameter"):
                param = self.build_node(param_node)
                if param and isinstance(param, Parameter):
                    parameters.append(param)
        else:
            # For error declarations, parameters might be direct children
            for param_node in self._find_children_by_type(node, "error_parameter"):
                param = self.build_node(param_node)
                if param and isinstance(param, Parameter):
                    parameters.append(param)

        return ErrorDeclaration(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            parameters=parameters
        )

    def _build_struct(self, node: tree_sitter.Node) -> StructDeclaration:
        """Build a struct declaration."""
        # Get struct name
        name_node = self._find_child_by_type(node, "identifier")
        name = self._get_node_text(name_node) if name_node else "unknown"

        # Get members
        members = []
        body_node = self._find_child_by_type(node, "struct_body")
        if body_node:
            for member_node in self._find_children_by_type(body_node, "struct_member"):
                member = self.build_node(member_node)
                if member and isinstance(member, VariableDeclaration):
                    members.append(member)

        return StructDeclaration(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            members=members
        )

    def _build_enum(self, node: tree_sitter.Node) -> EnumDeclaration:
        """Build an enum declaration."""
        # Get enum name
        name_node = self._find_child_by_type(node, "identifier")
        name = self._get_node_text(name_node) if name_node else "unknown"

        # Get enum values
        values = []
        body_node = self._find_child_by_type(node, "enum_body")
        if body_node:
            for value_node in self._find_children_by_type(body_node, "identifier"):
                values.append(self._get_node_text(value_node))

        return EnumDeclaration(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            values=values
        )

    def _build_parameter(self, node: tree_sitter.Node) -> Parameter:
        """Build a parameter."""
        # Get parameter name
        name_node = self._find_child_by_type(node, "identifier")
        name = self._get_node_text(name_node) if name_node else ""

        # Get type
        type_node = self._find_child_by_type(node, "type_name")
        type_name = self._get_node_text(type_node) if type_node else "unknown"

        # Get storage location
        storage_location = None
        for child in node.children:
            if child.type in ["memory", "storage", "calldata"]:
                storage_location = child.type
                break

        return Parameter(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name,
            type_name=type_name,
            storage_location=storage_location
        )

    def _build_block(self, node: tree_sitter.Node) -> Block:
        """Build a block statement."""
        statements = []
        for child in node.children:
            if child.type != "{" and child.type != "}":
                stmt = self.build_node(child)
                if stmt and isinstance(stmt, Statement):
                    statements.append(stmt)

        return Block(
            source_location=self._get_source_location(node),
            raw_node=node,
            statements=statements
        )

    def _build_return(self, node: tree_sitter.Node) -> ReturnStatement:
        """Build a return statement."""
        expression = None
        for child in node.children:
            if child.type != "return" and child.type != ";":
                expr = self.build_node(child)
                if expr and isinstance(expr, Expression):
                    expression = expr
                    break

        return ReturnStatement(
            source_location=self._get_source_location(node),
            raw_node=node,
            expression=expression
        )

    def _build_identifier(self, node: tree_sitter.Node) -> Identifier:
        """Build an identifier expression."""
        name = self._get_node_text(node)

        return Identifier(
            source_location=self._get_source_location(node),
            raw_node=node,
            name=name
        )

    def _build_literal(self, node: tree_sitter.Node) -> Literal:
        """Build a literal expression."""
        value = self._get_node_text(node)
        literal_type = node.type.replace("_literal", "")

        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            value=value,
            literal_type=literal_type
        )

    def _build_call(self, node: tree_sitter.Node) -> CallExpression:
        """Build a call expression."""
        # Get function being called
        function_node = node.children[0] if node.children else None
        function = None
        if function_node:
            func_ast = self.build_node(function_node)
            if isinstance(func_ast, Expression):
                function = func_ast

        if function is None:
            # Fallback to identifier
            function = Identifier(
                source_location=self._get_source_location(node),
                name="unknown"
            )

        # Get arguments
        arguments = []
        arg_list_node = self._find_child_by_type(node, "call_arguments")
        if arg_list_node:
            for arg_node in arg_list_node.children:
                if arg_node.type != "(" and arg_node.type != ")" and arg_node.type != ",":
                    arg = self.build_node(arg_node)
                    if arg and isinstance(arg, Expression):
                        arguments.append(arg)

        return CallExpression(
            source_location=self._get_source_location(node),
            raw_node=node,
            function=function,
            arguments=arguments
        )

    def _build_binary(self, node: tree_sitter.Node) -> BinaryExpression:
        """Build a binary expression."""
        # Find operator and operands
        operator = ""
        left = None
        right = None

        for i, child in enumerate(node.children):
            if child.type in ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
                operator = child.type
                # Left operand is before operator
                if i > 0:
                    left_ast = self.build_node(node.children[i-1])
                    if isinstance(left_ast, Expression):
                        left = left_ast
                # Right operand is after operator
                if i < len(node.children) - 1:
                    right_ast = self.build_node(node.children[i+1])
                    if isinstance(right_ast, Expression):
                        right = right_ast
                break

        # Fallback to first and last child if pattern matching fails
        if left is None and node.children:
            left_ast = self.build_node(node.children[0])
            if isinstance(left_ast, Expression):
                left = left_ast

        if right is None and len(node.children) >= 2:
            right_ast = self.build_node(node.children[-1])
            if isinstance(right_ast, Expression):
                right = right_ast

        # Create fallback expressions if needed
        if left is None:
            left = Identifier(source_location=self._get_source_location(node), name="unknown")
        if right is None:
            right = Identifier(source_location=self._get_source_location(node), name="unknown")

        return BinaryExpression(
            source_location=self._get_source_location(node),
            raw_node=node,
            operator=operator or "unknown",
            left=left,
            right=right
        )

    def _build_function_body(self, node: tree_sitter.Node) -> Block:
        """Build a function body (same as block but handles function_body node type)."""
        statements = []
        for child in node.children:
            if child.type not in ["{", "}", "comment"]:  # Skip braces and comments
                stmt = self.build_node(child)
                if stmt and isinstance(stmt, Statement):
                    statements.append(stmt)

        return Block(
            source_location=self._get_source_location(node),
            raw_node=node,
            statements=statements
        )

    def _build_statement(self, node: tree_sitter.Node) -> Optional[Statement]:
        """Build a generic statement node and extract ALL expressions recursively."""
        # For generic 'statement' nodes, try to build the first meaningful child
        for child in node.children:
            if child.type not in [";", "comment"]:
                stmt = self.build_node(child)
                if stmt and isinstance(stmt, Statement):
                    return stmt

        # Use recursive extraction to get ALL expressions
        expressions = self._extract_all_expressions_recursively(node)

        # Create a generic statement with nested expressions
        stmt = GenericStatement(
            source_location=self._get_source_location(node),
            raw_node=node
        )

        # Store expressions for traversal
        stmt._nested_expressions = expressions
        return stmt

    def _extract_all_expressions_recursively(self, node: tree_sitter.Node) -> List[Expression]:
        """Recursively extract ALL expressions from a tree-sitter node."""
        expressions = []

        # Build this node if it's an expression
        if (node.type in self.node_type_mapping and
            ('expression' in node.type or
             node.type in ['identifier', 'number_literal', 'string_literal', 'boolean_literal'])):
            expr = self.build_node(node)
            if expr and isinstance(expr, Expression):
                expressions.append(expr)

        # Recursively extract from all children
        for child in node.children:
            child_expressions = self._extract_all_expressions_recursively(child)
            expressions.extend(child_expressions)

        return expressions

    def _build_expression_statement(self, node: tree_sitter.Node) -> Statement:
        """Build an expression statement."""
        expression = None
        for child in node.children:
            if child.type != ";":
                expr = self.build_node(child)
                if expr and isinstance(expr, Expression):
                    expression = expr
                    break

        return ExpressionStatement(
            source_location=self._get_source_location(node),
            raw_node=node,
            expression=expression
        )

    def _build_variable_declaration_statement(self, node: tree_sitter.Node) -> Statement:
        """Build a variable declaration statement."""
        # For now, create a generic statement
        # This would need more sophisticated parsing for full variable declarations
        return GenericStatement(
            source_location=self._get_source_location(node),
            raw_node=node
        )

    def _build_if_statement(self, node: tree_sitter.Node) -> Statement:
        """Build an if statement and extract ALL its expressions recursively."""
        # Use recursive extraction to get ALL expressions
        expressions = self._extract_all_expressions_recursively(node)

        # Create a generic statement but store expressions for traversal
        stmt = GenericStatement(
            node_type=NodeType.IF_STATEMENT,
            source_location=self._get_source_location(node),
            raw_node=node
        )

        # Store expressions as a custom attribute for traversal
        stmt._nested_expressions = expressions
        return stmt

    def _build_for_statement(self, node: tree_sitter.Node) -> Statement:
        """Build a for statement and extract ALL its expressions recursively."""
        # Use recursive extraction to get ALL expressions
        expressions = self._extract_all_expressions_recursively(node)

        # Create a generic statement but store expressions for traversal
        stmt = GenericStatement(
            node_type=NodeType.FOR_STATEMENT,
            source_location=self._get_source_location(node),
            raw_node=node
        )

        # Store expressions as a custom attribute for traversal
        stmt._nested_expressions = expressions
        return stmt

    def _build_while_statement(self, node: tree_sitter.Node) -> Statement:
        """Build a while statement."""
        return GenericStatement(
            node_type=NodeType.WHILE_STATEMENT,
            source_location=self._get_source_location(node),
            raw_node=node
        )

    def _build_expression(self, node: tree_sitter.Node) -> Optional[Expression]:
        """Build a generic expression by examining its children more thoroughly."""
        # First, try to build meaningful children
        built_expressions = []
        for child in node.children:
            if child.type not in [";", "(", ")", "{", "}", "[", "]", ",", "comment", "."]:
                expr = self.build_node(child)
                if expr and isinstance(expr, Expression):
                    built_expressions.append(expr)

        # If we found exactly one expression, return it
        if len(built_expressions) == 1:
            return built_expressions[0]

        # If we found multiple expressions, return the most complex one
        if len(built_expressions) > 1:
            # Prefer non-identifier expressions
            non_identifiers = [e for e in built_expressions if not isinstance(e, Identifier)]
            if non_identifiers:
                return non_identifiers[0]
            return built_expressions[0]

        # If no children built successfully, try to create from text
        text = self._get_node_text(node)
        if text and text.strip():
            # Try to determine if it looks like a specific expression type
            text_clean = text.strip()
            if '(' in text_clean and ')' in text_clean and not text_clean.startswith('('):
                # Looks like a function call
                return CallExpression(
                    source_location=self._get_source_location(node),
                    raw_node=node,
                    function_name=text_clean,
                    arguments=[]
                )
            else:
                # Default to identifier
                return Identifier(
                    source_location=self._get_source_location(node),
                    raw_node=node,
                    name=text_clean
                )

        return None

    def _build_assignment(self, node: tree_sitter.Node) -> Expression:
        """Build an assignment expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.ASSIGNMENT_EXPRESSION,
            value=text if text else "assignment",
            literal_type="assignment"
        )

    def _build_augmented_assignment(self, node: tree_sitter.Node) -> Expression:
        """Build an augmented assignment expression (+=, -=, etc.)."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.ASSIGNMENT_EXPRESSION,  # Same type as regular assignment
            value=text if text else "augmented_assignment",
            literal_type="augmented_assignment"
        )

    def _build_member_access(self, node: tree_sitter.Node) -> Expression:
        """Build a member access expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.MEMBER_ACCESS,
            value=text if text else "member_access",
            literal_type="member_access"
        )

    def _build_member_expression(self, node: tree_sitter.Node) -> Expression:
        """Build a member expression (tree-sitter's member_expression type)."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.MEMBER_ACCESS,  # Map to same type as member_access
            value=text if text else "member_expression",
            literal_type="member_expression"
        )

    def _build_unary(self, node: tree_sitter.Node) -> Expression:
        """Build a unary expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.UNARY_EXPRESSION,
            value=text if text else "unary_expr",
            literal_type="unary"
        )

    def _build_ternary(self, node: tree_sitter.Node) -> Expression:
        """Build a ternary expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.TERNARY_EXPRESSION,
            value=text if text else "ternary_expr",
            literal_type="ternary"
        )

    def _build_tuple(self, node: tree_sitter.Node) -> Expression:
        """Build a tuple expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.TUPLE_EXPRESSION,
            value=text if text else "tuple_expr",
            literal_type="tuple"
        )

    def _build_type_cast(self, node: tree_sitter.Node) -> Expression:
        """Build a type cast expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.TYPE_CAST_EXPRESSION,
            value=text if text else "type_cast",
            literal_type="type_cast"
        )

    def _build_update(self, node: tree_sitter.Node) -> Expression:
        """Build an update expression (++, --)."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.UPDATE_EXPRESSION,
            value=text if text else "update_expr",
            literal_type="update"
        )

    def _build_meta_type(self, node: tree_sitter.Node) -> Expression:
        """Build a meta type expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.META_TYPE_EXPRESSION,
            value=text if text else "meta_type",
            literal_type="meta_type"
        )

    def _build_payable_conversion(self, node: tree_sitter.Node) -> Expression:
        """Build a payable conversion expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.PAYABLE_CONVERSION,
            value=text if text else "payable",
            literal_type="payable_conversion"
        )

    def _build_struct_expression(self, node: tree_sitter.Node) -> Expression:
        """Build a struct expression."""
        # Find type expression and field assignments
        type_expr = None
        fields = []

        for child in node.children:
            if child.type not in ["{", "}", ",", ":", "comment"]:
                expr = self.build_node(child)
                if expr and isinstance(expr, Expression):
                    if type_expr is None:
                        type_expr = expr
                    else:
                        fields.append(expr)

        if type_expr is None:
            type_expr = Identifier(source_location=self._get_source_location(node), name="unknown_type")

        return StructExpression(
            source_location=self._get_source_location(node),
            raw_node=node,
            type_expr=type_expr,
            fields=fields
        )

    def _build_parenthesized(self, node: tree_sitter.Node) -> Expression:
        """Build a parenthesized expression."""
        # Find the inner expression
        for child in node.children:
            if child.type not in ["(", ")", "comment"]:
                expr = self.build_node(child)
                if expr and isinstance(expr, Expression):
                    return ParenthesizedExpression(
                        source_location=self._get_source_location(node),
                        raw_node=node,
                        expression=expr
                    )

        # Fallback
        return ParenthesizedExpression(
            source_location=self._get_source_location(node),
            raw_node=node,
            expression=Identifier(source_location=self._get_source_location(node), name="unknown")
        )

    def _build_array_access(self, node: tree_sitter.Node) -> Expression:
        """Build an array access expression."""
        base = None
        index = None

        for child in node.children:
            if child.type not in ["[", "]", "comment"]:
                expr = self.build_node(child)
                if expr and isinstance(expr, Expression):
                    if base is None:
                        base = expr
                    else:
                        index = expr

        if base is None:
            base = Identifier(source_location=self._get_source_location(node), name="unknown_base")

        return ArrayAccess(
            source_location=self._get_source_location(node),
            raw_node=node,
            base=base,
            index=index
        )

    def _build_slice_access(self, node: tree_sitter.Node) -> Expression:
        """Build a slice access expression."""
        base = None
        start = None
        end = None
        expressions = []

        for child in node.children:
            if child.type not in ["[", "]", ":", "comment"]:
                expr = self.build_node(child)
                if expr and isinstance(expr, Expression):
                    expressions.append(expr)

        if expressions:
            base = expressions[0]
            if len(expressions) > 1:
                start = expressions[1]
            if len(expressions) > 2:
                end = expressions[2]

        if base is None:
            base = Identifier(source_location=self._get_source_location(node), name="unknown_base")

        return SliceAccess(
            source_location=self._get_source_location(node),
            raw_node=node,
            base=base,
            start=start,
            end=end
        )

    def _build_inline_array(self, node: tree_sitter.Node) -> Expression:
        """Build an inline array expression."""
        elements = []

        for child in node.children:
            if child.type not in ["[", "]", ",", "comment"]:
                expr = self.build_node(child)
                if expr and isinstance(expr, Expression):
                    elements.append(expr)

        return InlineArrayExpression(
            source_location=self._get_source_location(node),
            raw_node=node,
            elements=elements
        )

    def _build_new_expression(self, node: tree_sitter.Node) -> Expression:
        """Build a new expression."""
        type_name = "unknown_type"
        arguments = []

        for child in node.children:
            if child.type not in ["new", "(", ")", ",", "comment"]:
                if child.type == "identifier":
                    type_name = self._get_node_text(child)
                else:
                    expr = self.build_node(child)
                    if expr and isinstance(expr, Expression):
                        arguments.append(expr)

        return NewExpression(
            source_location=self._get_source_location(node),
            raw_node=node,
            type_name=type_name,
            arguments=arguments
        )

    def _build_user_defined_type_expr(self, node: tree_sitter.Node) -> Expression:
        """Build a user defined type as expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.USER_DEFINED_TYPE_EXPR,
            value=text if text else "user_type",
            literal_type="user_defined_type"
        )

    def _build_primitive_type_expr(self, node: tree_sitter.Node) -> Expression:
        """Build a primitive type as expression."""
        text = self._get_node_text(node)
        return Literal(
            source_location=self._get_source_location(node),
            raw_node=node,
            node_type=NodeType.PRIMITIVE_TYPE_EXPR,
            value=text if text else "primitive_type",
            literal_type="primitive_type"
        )