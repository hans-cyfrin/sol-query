"""AST node abstraction layer for Solidity code elements."""

from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

import tree_sitter
from pydantic import BaseModel, Field, ConfigDict

from sol_query.models.source_location import SourceLocation

if TYPE_CHECKING:
    from sol_query.core.parser import SolidityParser


class Visibility(str, Enum):
    """Solidity visibility modifiers."""
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"
    EXTERNAL = "external"


class StateMutability(str, Enum):
    """Solidity state mutability modifiers."""
    PURE = "pure"
    VIEW = "view"
    NONPAYABLE = "nonpayable"
    PAYABLE = "payable"


class NodeType(str, Enum):
    """Types of AST nodes."""
    # Declarations
    CONTRACT = "contract"
    FUNCTION = "function"
    MODIFIER = "modifier"
    VARIABLE = "variable"
    STRUCT = "struct"
    ENUM = "enum"
    EVENT = "event"
    ERROR = "error"

    # Statements
    IF_STATEMENT = "if_statement"
    FOR_STATEMENT = "for_statement"
    WHILE_STATEMENT = "while_statement"
    DO_WHILE_STATEMENT = "do_while_statement"
    RETURN_STATEMENT = "return_statement"
    EMIT_STATEMENT = "emit_statement"
    REQUIRE_STATEMENT = "require_statement"
    ASSERT_STATEMENT = "assert_statement"
    REVERT_STATEMENT = "revert_statement"
    EXPRESSION_STATEMENT = "expression_statement"
    BLOCK = "block"
    STATEMENT = "statement"

    # Expressions
    CALL_EXPRESSION = "call_expression"
    BINARY_EXPRESSION = "binary_expression"
    UNARY_EXPRESSION = "unary_expression"
    ASSIGNMENT_EXPRESSION = "assignment_expression"
    TERNARY_EXPRESSION = "ternary_expression"
    TUPLE_EXPRESSION = "tuple_expression"
    TYPE_CAST_EXPRESSION = "type_cast_expression"
    UPDATE_EXPRESSION = "update_expression"
    META_TYPE_EXPRESSION = "meta_type_expression"
    PAYABLE_CONVERSION = "payable_conversion_expression"
    STRUCT_EXPRESSION = "struct_expression"
    PARENTHESIZED_EXPRESSION = "parenthesized_expression"
    ARRAY_ACCESS = "array_access"
    SLICE_ACCESS = "slice_access"
    INLINE_ARRAY_EXPRESSION = "inline_array_expression"
    NEW_EXPRESSION = "new_expression"
    USER_DEFINED_TYPE_EXPR = "user_defined_type_expr"
    PRIMITIVE_TYPE_EXPR = "primitive_type_expr"
    IDENTIFIER = "identifier"
    LITERAL = "literal"
    MEMBER_ACCESS = "member_access"
    INDEX_ACCESS = "index_access"


class ASTNode(BaseModel, ABC):
    """Base class for all AST nodes."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    node_type: NodeType = Field(description="Type of this AST node")
    source_location: SourceLocation = Field(description="Location in source code")
    raw_node: Optional[tree_sitter.Node] = Field(
        default=None,
        exclude=True,
        description="Original tree-sitter node (excluded from serialization)"
    )

    def get_source_code(self) -> str:
        """Get the source code for this node."""
        return self.source_location.source_text

    def get_children(self) -> List["ASTNode"]:
        """Get child nodes. Override in subclasses."""
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(exclude={"raw_node"})


class ContractDeclaration(ASTNode):
    """Represents a contract declaration."""

    node_type: NodeType = Field(default=NodeType.CONTRACT, frozen=True)
    name: str = Field(description="Contract name")
    kind: str = Field(description="Contract kind (contract, interface, library)")
    inheritance: List[str] = Field(
        default_factory=list,
        description="Names of inherited contracts/interfaces"
    )

    # Child elements (populated during analysis)
    functions: List["FunctionDeclaration"] = Field(
        default_factory=list,
        description="Functions defined in this contract"
    )
    modifiers: List["ModifierDeclaration"] = Field(
        default_factory=list,
        description="Modifiers defined in this contract"
    )
    variables: List["VariableDeclaration"] = Field(
        default_factory=list,
        description="State variables defined in this contract"
    )
    events: List["EventDeclaration"] = Field(
        default_factory=list,
        description="Events defined in this contract"
    )
    errors: List["ErrorDeclaration"] = Field(
        default_factory=list,
        description="Custom errors defined in this contract"
    )
    structs: List["StructDeclaration"] = Field(
        default_factory=list,
        description="Structs defined in this contract"
    )
    enums: List["EnumDeclaration"] = Field(
        default_factory=list,
        description="Enums defined in this contract"
    )

    def is_interface(self) -> bool:
        """Check if this is an interface."""
        return self.kind == "interface"

    def is_library(self) -> bool:
        """Check if this is a library."""
        return self.kind == "library"

    def is_abstract(self) -> bool:
        """Check if this is an abstract contract."""
        return self.kind == "abstract"

    def get_function(self, name: str) -> Optional["FunctionDeclaration"]:
        """Get a function by name."""
        for func in self.functions:
            if func.name == name:
                return func
        return None

    def get_children(self) -> List[ASTNode]:
        """Get all child nodes."""
        children: List[ASTNode] = []
        children.extend(self.functions)
        children.extend(self.modifiers)
        children.extend(self.variables)
        children.extend(self.events)
        children.extend(self.errors)
        children.extend(self.structs)
        children.extend(self.enums)
        return children


class FunctionDeclaration(ASTNode):
    """Represents a function declaration."""

    node_type: NodeType = Field(default=NodeType.FUNCTION, frozen=True)
    name: str = Field(description="Function name")
    visibility: Visibility = Field(description="Function visibility")
    state_mutability: StateMutability = Field(description="State mutability")
    is_constructor: bool = Field(default=False, description="Whether this is a constructor")
    is_receive: bool = Field(default=False, description="Whether this is a receive function")
    is_fallback: bool = Field(default=False, description="Whether this is a fallback function")
    is_virtual: bool = Field(default=False, description="Whether function is virtual")
    is_override: bool = Field(default=False, description="Whether function is override")
    parent_contract: Optional["ContractDeclaration"] = Field(
        default=None,
        description="Reference to the parent contract",
        exclude=True  # Exclude from serialization to avoid circular references
    )

    parameters: List["Parameter"] = Field(
        default_factory=list,
        description="Function parameters"
    )
    return_parameters: List["Parameter"] = Field(
        default_factory=list,
        description="Return parameters"
    )
    modifiers: List[str] = Field(
        default_factory=list,
        description="Applied modifier names"
    )
    body: Optional["Block"] = Field(
        default=None,
        description="Function body (None for interface functions)"
    )

    def get_signature(self) -> str:
        """Get function signature."""
        param_types = [p.type_name for p in self.parameters]
        return f"{self.name}({','.join(param_types)})"

    def is_external(self) -> bool:
        """Check if function is external."""
        return self.visibility == Visibility.EXTERNAL

    def is_public(self) -> bool:
        """Check if function is public."""
        return self.visibility == Visibility.PUBLIC

    def is_internal(self) -> bool:
        """Check if function is internal."""
        return self.visibility == Visibility.INTERNAL

    def is_private(self) -> bool:
        """Check if function is private."""
        return self.visibility == Visibility.PRIVATE

    def is_view(self) -> bool:
        """Check if function is view."""
        return self.state_mutability == StateMutability.VIEW

    def is_pure(self) -> bool:
        """Check if function is pure."""
        return self.state_mutability == StateMutability.PURE

    def is_payable(self) -> bool:
        """Check if function is payable."""
        return self.state_mutability == StateMutability.PAYABLE

    def has_modifiers(self) -> bool:
        """Check if function has any modifiers."""
        return len(self.modifiers) > 0

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        children: List[ASTNode] = []
        children.extend(self.parameters)
        children.extend(self.return_parameters)
        if self.body:
            children.append(self.body)
        return children


class Parameter(ASTNode):
    """Represents a function parameter."""

    node_type: NodeType = Field(default=NodeType.VARIABLE, frozen=True)
    name: str = Field(description="Parameter name")
    type_name: str = Field(description="Parameter type")


class VariableDeclaration(ASTNode):
    """Represents a variable declaration."""

    node_type: NodeType = Field(default=NodeType.VARIABLE, frozen=True)
    name: str = Field(description="Variable name")
    type_name: str = Field(description="Variable type")
    visibility: Optional[Visibility] = Field(
        default=None,
        description="Variable visibility (for state variables)"
    )
    is_constant: bool = Field(default=False, description="Whether variable is constant")
    is_immutable: bool = Field(default=False, description="Whether variable is immutable")
    initial_value: Optional["Expression"] = Field(
        default=None,
        description="Initial value expression"
    )
    parent_contract: Optional["ContractDeclaration"] = Field(
        default=None,
        description="Reference to the parent contract",
        exclude=True  # Exclude from serialization to avoid circular references
    )

    def is_state_variable(self) -> bool:
        """Check if this is a state variable."""
        return self.visibility is not None

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        if self.initial_value:
            return [self.initial_value]
        return []


class ModifierDeclaration(ASTNode):
    """Represents a modifier declaration."""

    node_type: NodeType = Field(default=NodeType.MODIFIER, frozen=True)
    name: str = Field(description="Modifier name")
    parameters: List[Parameter] = Field(
        default_factory=list,
        description="Modifier parameters"
    )
    body: Optional["Block"] = Field(
        default=None,
        description="Modifier body"
    )

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        children: List[ASTNode] = []
        children.extend(self.parameters)
        if self.body:
            children.append(self.body)
        return children


class EventDeclaration(ASTNode):
    """Represents an event declaration."""

    node_type: NodeType = Field(default=NodeType.EVENT, frozen=True)
    name: str = Field(description="Event name")
    parameters: List[Parameter] = Field(
        default_factory=list,
        description="Event parameters"
    )

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        return list(self.parameters)


class ErrorDeclaration(ASTNode):
    """Represents an error declaration."""

    node_type: NodeType = Field(default=NodeType.ERROR, frozen=True)
    name: str = Field(description="Error name")
    parameters: List[Parameter] = Field(
        default_factory=list,
        description="Error parameters"
    )

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        return list(self.parameters)


class StructDeclaration(ASTNode):
    """Represents a struct declaration."""

    node_type: NodeType = Field(default=NodeType.STRUCT, frozen=True)
    name: str = Field(description="Struct name")
    fields: List[VariableDeclaration] = Field(
        default_factory=list,
        description="Struct fields"
    )

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        return list(self.fields)


class EnumDeclaration(ASTNode):
    """Represents an enum declaration."""

    node_type: NodeType = Field(default=NodeType.ENUM, frozen=True)
    name: str = Field(description="Enum name")
    values: List[str] = Field(
        default_factory=list,
        description="Enum values"
    )


# Statement classes
class Statement(ASTNode):
    """Base class for all statements."""
    pass


class Block(Statement):
    """Represents a block statement."""

    node_type: NodeType = Field(default=NodeType.BLOCK, frozen=True)
    statements: List[Statement] = Field(
        default_factory=list,
        description="Statements in the block"
    )

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        return list(self.statements)


class ReturnStatement(Statement):
    """Represents a return statement."""

    node_type: NodeType = Field(default=NodeType.RETURN_STATEMENT, frozen=True)
    expression: Optional["Expression"] = Field(
        default=None,
        description="Return expression"
    )

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        if self.expression:
            return [self.expression]
        return []


class ExpressionStatement(Statement):
    """Represents an expression statement."""

    node_type: NodeType = Field(default=NodeType.EXPRESSION_STATEMENT, frozen=True)
    expression: Optional["Expression"] = Field(
        default=None,
        description="The expression in this statement"
    )

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        if self.expression:
            return [self.expression]
        return []


class GenericStatement(Statement):
    """Represents a generic statement with configurable node type."""

    node_type: NodeType = Field(description="Type of this statement")

    def __init__(self, node_type: NodeType = NodeType.STATEMENT, **kwargs):
        super().__init__(node_type=node_type, **kwargs)

    def get_children(self) -> List[ASTNode]:
        """Get child nodes including nested expressions."""
        children = []

        # Include any nested expressions stored during building
        if hasattr(self, '_nested_expressions'):
            children.extend(self._nested_expressions)

        return children


# Expression classes
class Expression(ASTNode):
    """Base class for all expressions."""
    pass


class Identifier(Expression):
    """Represents an identifier expression."""

    node_type: NodeType = Field(default=NodeType.IDENTIFIER, frozen=True)
    name: str = Field(description="Identifier name")


class Literal(Expression):
    """Represents a literal expression."""

    node_type: NodeType = Field(default=NodeType.LITERAL, frozen=True)
    value: str = Field(description="Literal value")
    literal_type: str = Field(description="Type of literal (number, string, boolean)")


class CallExpression(Expression):
    """Represents a function call expression."""

    node_type: NodeType = Field(default=NodeType.CALL_EXPRESSION, frozen=True)
    function: Expression = Field(description="Function being called")
    arguments: List[Expression] = Field(
        default_factory=list,
        description="Call arguments"
    )

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        children: List[ASTNode] = [self.function]
        children.extend(self.arguments)
        return children


class BinaryExpression(Expression):
    """Represents a binary expression."""

    node_type: NodeType = Field(default=NodeType.BINARY_EXPRESSION, frozen=True)
    operator: str = Field(description="Binary operator")
    left: Expression = Field(description="Left operand")
    right: Expression = Field(description="Right operand")

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        return [self.left, self.right]


class ArrayAccess(Expression):
    """Represents array access expression."""

    node_type: NodeType = Field(default=NodeType.ARRAY_ACCESS, frozen=True)
    base: Expression = Field(description="Base expression")
    index: Optional[Expression] = Field(default=None, description="Index expression")

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        children = [self.base]
        if self.index:
            children.append(self.index)
        return children


class SliceAccess(Expression):
    """Represents slice access expression."""

    node_type: NodeType = Field(default=NodeType.SLICE_ACCESS, frozen=True)
    base: Expression = Field(description="Base expression")
    start: Optional[Expression] = Field(default=None, description="Start expression")
    end: Optional[Expression] = Field(default=None, description="End expression")

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        children = [self.base]
        if self.start:
            children.append(self.start)
        if self.end:
            children.append(self.end)
        return children


class ParenthesizedExpression(Expression):
    """Represents a parenthesized expression."""

    node_type: NodeType = Field(default=NodeType.PARENTHESIZED_EXPRESSION, frozen=True)
    expression: Expression = Field(description="Inner expression")

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        return [self.expression]


class InlineArrayExpression(Expression):
    """Represents an inline array expression."""

    node_type: NodeType = Field(default=NodeType.INLINE_ARRAY_EXPRESSION, frozen=True)
    elements: List[Expression] = Field(default_factory=list, description="Array elements")

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        return list(self.elements)


class NewExpression(Expression):
    """Represents a new expression."""

    node_type: NodeType = Field(default=NodeType.NEW_EXPRESSION, frozen=True)
    type_name: str = Field(description="Type being instantiated")
    arguments: List[Expression] = Field(default_factory=list, description="Constructor arguments")

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        return list(self.arguments)


class StructExpression(Expression):
    """Represents a struct expression."""

    node_type: NodeType = Field(default=NodeType.STRUCT_EXPRESSION, frozen=True)
    type_expr: Expression = Field(description="Struct type expression")
    fields: List[Expression] = Field(default_factory=list, description="Field assignments")

    def get_children(self) -> List[ASTNode]:
        """Get child nodes."""
        children = [self.type_expr]
        children.extend(self.fields)
        return children