"""Fluent collection classes for chainable queries."""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Pattern, Callable, TYPE_CHECKING

from sol_query.core.ast_nodes import (
    ASTNode, ContractDeclaration, FunctionDeclaration, VariableDeclaration,
    ModifierDeclaration, EventDeclaration, Statement, Expression,
    Visibility, StateMutability
)

if TYPE_CHECKING:
    from sol_query.query.engine import SolidityQueryEngine


class BaseCollection(ABC):
    """Base class for all collections supporting fluent queries."""

    def __init__(self, elements: List[ASTNode], engine: "SolidityQueryEngine"):
        """
        Initialize collection.
        
        Args:
            elements: List of AST elements
            engine: Reference to the query engine
        """
        self._elements = elements
        self._engine = engine

    def __len__(self) -> int:
        """Get number of elements in collection."""
        return len(self._elements)

    def __iter__(self):
        """Iterate over elements in collection."""
        return iter(self._elements)

    def __getitem__(self, index: Union[int, slice]):
        """Get element(s) by index."""
        return self._elements[index]

    def list(self) -> List[ASTNode]:
        """Get the underlying list of elements."""
        return list(self._elements)

    def first(self) -> Optional[ASTNode]:
        """Get the first element, or None if empty."""
        return self._elements[0] if self._elements else None

    def count(self) -> int:
        """Get count of elements."""
        return len(self._elements)

    def is_empty(self) -> bool:
        """Check if collection is empty."""
        return len(self._elements) == 0

    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert all elements to dictionaries for JSON serialization."""
        return [element.to_dict() for element in self._elements]

    @abstractmethod
    def _create_new_collection(self, elements: List[ASTNode]) -> "BaseCollection":
        """Create a new collection of the same type with filtered elements."""
        pass


class ContractCollection(BaseCollection):
    """Collection of contract declarations with fluent query methods."""

    def _create_new_collection(self, elements: List[ASTNode]) -> "ContractCollection":
        contracts = [e for e in elements if isinstance(e, ContractDeclaration)]
        return ContractCollection(contracts, self._engine)

    def with_name(self, pattern: Union[str, Pattern]) -> "ContractCollection":
        """Filter contracts by name pattern."""
        filtered = [c for c in self._elements
                   if self._engine.pattern_matcher.matches_name_pattern(c.name, pattern)]
        return self._create_new_collection(filtered)

    def with_name_not(self, pattern: Union[str, Pattern]) -> "ContractCollection":
        """Filter contracts excluding name pattern."""
        filtered = [c for c in self._elements
                   if not self._engine.pattern_matcher.matches_name_pattern(c.name, pattern)]
        return self._create_new_collection(filtered)

    def with_names(self, names: List[str]) -> "ContractCollection":
        """Filter contracts by exact name matches."""
        filtered = [c for c in self._elements if c.name in names]
        return self._create_new_collection(filtered)

    def with_inheritance(self, base_contract: str) -> "ContractCollection":
        """Filter contracts that inherit from the specified contract."""
        filtered = [c for c in self._elements if base_contract in c.inheritance]
        return self._create_new_collection(filtered)

    def interfaces(self) -> "ContractCollection":
        """Get only interface contracts."""
        filtered = [c for c in self._elements if c.is_interface()]
        return self._create_new_collection(filtered)

    def libraries(self) -> "ContractCollection":
        """Get only library contracts."""
        filtered = [c for c in self._elements if c.is_library()]
        return self._create_new_collection(filtered)

    def main_contracts(self) -> "ContractCollection":
        """Get only regular contracts (not interfaces or libraries)."""
        filtered = [c for c in self._elements
                   if not c.is_interface() and not c.is_library()]
        return self._create_new_collection(filtered)

    def with_function_name(self, name: Union[str, Pattern]) -> "ContractCollection":
        """Filter contracts that have a function with the specified name."""
        filtered = []
        for contract in self._elements:
            if any(self._engine.pattern_matcher.matches_name_pattern(f.name, name)
                   for f in contract.functions):
                filtered.append(contract)
        return self._create_new_collection(filtered)

    def with_event_name(self, name: Union[str, Pattern]) -> "ContractCollection":
        """Filter contracts that have an event with the specified name."""
        filtered = []
        for contract in self._elements:
            if any(self._engine.pattern_matcher.matches_name_pattern(e.name, name)
                   for e in contract.events):
                filtered.append(contract)
        return self._create_new_collection(filtered)

    def with_state_variable(self, name: Union[str, Pattern]) -> "ContractCollection":
        """Filter contracts that have a state variable with the specified name."""
        filtered = []
        for contract in self._elements:
            if any(self._engine.pattern_matcher.matches_name_pattern(v.name, name)
                   for v in contract.variables):
                filtered.append(contract)
        return self._create_new_collection(filtered)

    # Additional negation filters for contracts
    def not_interfaces(self) -> "ContractCollection":
        """Get contracts that are NOT interfaces."""
        filtered = [c for c in self._elements if not c.is_interface()]
        return self._create_new_collection(filtered)

    def not_libraries(self) -> "ContractCollection":
        """Get contracts that are NOT libraries."""
        filtered = [c for c in self._elements if not c.is_library()]
        return self._create_new_collection(filtered)

    def not_with_inheritance(self, base_contract: str) -> "ContractCollection":
        """Filter contracts that do NOT inherit from the specified contract."""
        filtered = [c for c in self._elements if base_contract not in c.inheritance]
        return self._create_new_collection(filtered)

    def without_function_name(self, name: Union[str, Pattern]) -> "ContractCollection":
        """Filter contracts that do NOT have a function with the specified name."""
        filtered = []
        for contract in self._elements:
            if not any(self._engine.pattern_matcher.matches_name_pattern(f.name, name)
                      for f in contract.functions):
                filtered.append(contract)
        return self._create_new_collection(filtered)

    def without_event_name(self, name: Union[str, Pattern]) -> "ContractCollection":
        """Filter contracts that do NOT have an event with the specified name."""
        filtered = []
        for contract in self._elements:
            if not any(self._engine.pattern_matcher.matches_name_pattern(e.name, name)
                      for e in contract.events):
                filtered.append(contract)
        return self._create_new_collection(filtered)

    def without_state_variable(self, name: Union[str, Pattern]) -> "ContractCollection":
        """Filter contracts that do NOT have a state variable with the specified name."""
        filtered = []
        for contract in self._elements:
            if not any(self._engine.pattern_matcher.matches_name_pattern(v.name, name)
                      for v in contract.variables):
                filtered.append(contract)
        return self._create_new_collection(filtered)

    # Navigation methods
    def get_functions(self) -> "FunctionCollection":
        """Get all functions from all contracts in this collection."""
        functions = []
        for contract in self._elements:
            functions.extend(contract.functions)
        return FunctionCollection(functions, self._engine)

    def get_variables(self) -> "VariableCollection":
        """Get all state variables from all contracts in this collection."""
        variables = []
        for contract in self._elements:
            variables.extend(contract.variables)
        return VariableCollection(variables, self._engine)

    def get_events(self) -> "EventCollection":
        """Get all events from all contracts in this collection."""
        events = []
        for contract in self._elements:
            events.extend(contract.events)
        return EventCollection(events, self._engine)

    def get_modifiers(self) -> "ModifierCollection":
        """Get all modifiers from all contracts in this collection."""
        modifiers = []
        for contract in self._elements:
            modifiers.extend(contract.modifiers)
        return ModifierCollection(modifiers, self._engine)


class FunctionCollection(BaseCollection):
    """Collection of function declarations with fluent query methods."""

    def _create_new_collection(self, elements: List[ASTNode]) -> "FunctionCollection":
        functions = [e for e in elements if isinstance(e, FunctionDeclaration)]
        return FunctionCollection(functions, self._engine)

    def with_name(self, pattern: Union[str, Pattern]) -> "FunctionCollection":
        """Filter functions by name pattern."""
        filtered = [f for f in self._elements
                   if self._engine.pattern_matcher.matches_name_pattern(f.name, pattern)]
        return self._create_new_collection(filtered)

    def with_signature(self, signature: str) -> "FunctionCollection":
        """Filter functions by exact signature."""
        filtered = [f for f in self._elements if f.get_signature() == signature]
        return self._create_new_collection(filtered)

    def with_visibility(self, visibility: Visibility) -> "FunctionCollection":
        """Filter functions by visibility."""
        filtered = [f for f in self._elements if f.visibility == visibility]
        return self._create_new_collection(filtered)

    def external(self) -> "FunctionCollection":
        """Get only external functions."""
        return self.with_visibility(Visibility.EXTERNAL)

    def public(self) -> "FunctionCollection":
        """Get only public functions."""
        return self.with_visibility(Visibility.PUBLIC)

    def internal(self) -> "FunctionCollection":
        """Get only internal functions."""
        return self.with_visibility(Visibility.INTERNAL)

    def private(self) -> "FunctionCollection":
        """Get only private functions."""
        return self.with_visibility(Visibility.PRIVATE)

    def view(self) -> "FunctionCollection":
        """Get only view functions."""
        filtered = [f for f in self._elements if f.is_view()]
        return self._create_new_collection(filtered)

    def pure(self) -> "FunctionCollection":
        """Get only pure functions."""
        filtered = [f for f in self._elements if f.is_pure()]
        return self._create_new_collection(filtered)

    def payable(self) -> "FunctionCollection":
        """Get only payable functions."""
        filtered = [f for f in self._elements if f.is_payable()]
        return self._create_new_collection(filtered)

    def constructors(self) -> "FunctionCollection":
        """Get only constructor functions."""
        filtered = [f for f in self._elements if f.is_constructor]
        return self._create_new_collection(filtered)

    def with_modifiers(self, modifiers: Union[str, List[str]]) -> "FunctionCollection":
        """Filter functions that have the specified modifiers."""
        modifier_list = [modifiers] if isinstance(modifiers, str) else modifiers
        filtered = [f for f in self._elements
                   if any(mod in f.modifiers for mod in modifier_list)]
        return self._create_new_collection(filtered)

    def with_modifier_regex(self, pattern: Union[str, Pattern]) -> "FunctionCollection":
        """Filter functions that have modifiers matching the regex pattern."""
        pattern_obj = re.compile(pattern) if isinstance(pattern, str) else pattern
        filtered = []
        for func in self._elements:
            if any(pattern_obj.search(mod) for mod in func.modifiers):
                filtered.append(func)
        return self._create_new_collection(filtered)

    def without_modifiers(self) -> "FunctionCollection":
        """Get functions without any modifiers."""
        filtered = [f for f in self._elements if not f.has_modifiers()]
        return self._create_new_collection(filtered)

    def with_parameter_count(self, count: int) -> "FunctionCollection":
        """Filter functions by parameter count."""
        filtered = [f for f in self._elements if len(f.parameters) == count]
        return self._create_new_collection(filtered)

    def with_parameter_type(self, type_pattern: Union[str, Pattern]) -> "FunctionCollection":
        """Filter functions that have parameters of the specified type."""
        filtered = []
        for func in self._elements:
            if any(self._engine.pattern_matcher.matches_name_pattern(p.type_name, type_pattern)
                   for p in func.parameters):
                filtered.append(func)
        return self._create_new_collection(filtered)

    # Negation filters for visibility
    def not_external(self) -> "FunctionCollection":
        """Get functions that are NOT external."""
        filtered = [f for f in self._elements if f.visibility != Visibility.EXTERNAL]
        return self._create_new_collection(filtered)

    def not_public(self) -> "FunctionCollection":
        """Get functions that are NOT public."""
        filtered = [f for f in self._elements if f.visibility != Visibility.PUBLIC]
        return self._create_new_collection(filtered)

    def not_internal(self) -> "FunctionCollection":
        """Get functions that are NOT internal."""
        filtered = [f for f in self._elements if f.visibility != Visibility.INTERNAL]
        return self._create_new_collection(filtered)

    def not_private(self) -> "FunctionCollection":
        """Get functions that are NOT private."""
        filtered = [f for f in self._elements if f.visibility != Visibility.PRIVATE]
        return self._create_new_collection(filtered)

    # Negation filters for state mutability
    def not_view(self) -> "FunctionCollection":
        """Get functions that are NOT view."""
        filtered = [f for f in self._elements if not f.is_view()]
        return self._create_new_collection(filtered)

    def not_pure(self) -> "FunctionCollection":
        """Get functions that are NOT pure."""
        filtered = [f for f in self._elements if not f.is_pure()]
        return self._create_new_collection(filtered)

    def not_payable(self) -> "FunctionCollection":
        """Get functions that are NOT payable."""
        filtered = [f for f in self._elements if not f.is_payable()]
        return self._create_new_collection(filtered)

    # Negation filters for special function types
    def not_constructors(self) -> "FunctionCollection":
        """Get functions that are NOT constructors."""
        filtered = [f for f in self._elements if not f.is_constructor]
        return self._create_new_collection(filtered)

    # Negation filters for modifiers
    def without_modifier(self, modifier: str) -> "FunctionCollection":
        """Filter functions that do NOT have the specified modifier."""
        filtered = [f for f in self._elements if modifier not in f.modifiers]
        return self._create_new_collection(filtered)

    def without_any_modifiers_matching(self, modifiers: Union[str, List[str]]) -> "FunctionCollection":
        """Filter functions that do NOT have any of the specified modifiers."""
        modifier_list = [modifiers] if isinstance(modifiers, str) else modifiers
        filtered = [f for f in self._elements
                   if not any(mod in f.modifiers for mod in modifier_list)]
        return self._create_new_collection(filtered)

    # Generic negation filter
    def not_with_visibility(self, visibility: Visibility) -> "FunctionCollection":
        """Filter functions that do NOT have the specified visibility."""
        filtered = [f for f in self._elements if f.visibility != visibility]
        return self._create_new_collection(filtered)

    def get_parent_contract(self, function: FunctionDeclaration) -> Optional[ContractDeclaration]:
        """Get the parent contract of a function."""
        return getattr(function, 'parent_contract', None)

    def from_contract(self, contract_name: str) -> "FunctionCollection":
        """Filter functions from a specific contract."""
        filtered = [f for f in self._elements
                   if f.parent_contract and f.parent_contract.name == contract_name]
        return self._create_new_collection(filtered)

    # External call and asset transfer filters
    def with_external_calls(self) -> "FunctionCollection":
        """Filter functions that directly contain external calls."""
        filtered = [f for f in self._elements if f.has_external_calls]
        return self._create_new_collection(filtered)

    def without_external_calls(self) -> "FunctionCollection":
        """Filter functions that do NOT directly contain external calls."""
        filtered = [f for f in self._elements if not f.has_external_calls]
        return self._create_new_collection(filtered)

    def with_asset_transfers(self) -> "FunctionCollection":
        """Filter functions that directly contain asset transfers (ETH send, token transfers)."""
        filtered = [f for f in self._elements if f.has_asset_transfers]
        return self._create_new_collection(filtered)

    def without_asset_transfers(self) -> "FunctionCollection":
        """Filter functions that do NOT directly contain asset transfers."""
        filtered = [f for f in self._elements if not f.has_asset_transfers]
        return self._create_new_collection(filtered)

    def with_external_calls_deep(self) -> "FunctionCollection":
        """
        Filter functions whose call tree includes any external calls (deep analysis).
        This analyzes the entire call chain to find functions that may indirectly make external calls.
        """
        from sol_query.analysis.call_analyzer import CallAnalyzer
        analyzer = CallAnalyzer()
        all_functions = self._engine._get_all_functions()

        filtered = []
        for func in self._elements:
            if analyzer.analyze_call_tree_external_calls(func, all_functions):
                filtered.append(func)

        return self._create_new_collection(filtered)

    def without_external_calls_deep(self) -> "FunctionCollection":
        """
        Filter functions whose call tree does NOT include any external calls (deep analysis).
        """
        from sol_query.analysis.call_analyzer import CallAnalyzer
        analyzer = CallAnalyzer()
        all_functions = self._engine._get_all_functions()

        filtered = []
        for func in self._elements:
            if not analyzer.analyze_call_tree_external_calls(func, all_functions):
                filtered.append(func)

        return self._create_new_collection(filtered)

    def with_asset_transfers_deep(self) -> "FunctionCollection":
        """
        Filter functions whose call tree includes any asset transfers (deep analysis).
        This analyzes the entire call chain to find functions that may indirectly transfer assets.
        """
        from sol_query.analysis.call_analyzer import CallAnalyzer
        analyzer = CallAnalyzer()
        all_functions = self._engine._get_all_functions()

        filtered = []
        for func in self._elements:
            if analyzer.analyze_call_tree_asset_transfers(func, all_functions):
                filtered.append(func)

        return self._create_new_collection(filtered)

    def without_asset_transfers_deep(self) -> "FunctionCollection":
        """
        Filter functions whose call tree does NOT include any asset transfers (deep analysis).
        """
        from sol_query.analysis.call_analyzer import CallAnalyzer
        analyzer = CallAnalyzer()
        all_functions = self._engine._get_all_functions()

        filtered = []
        for func in self._elements:
            if not analyzer.analyze_call_tree_asset_transfers(func, all_functions):
                filtered.append(func)

        return self._create_new_collection(filtered)

    def with_external_call_targets(self, targets: Union[str, List[str]]) -> "FunctionCollection":
        """Filter functions that call specific external targets."""
        target_list = [targets] if isinstance(targets, str) else targets
        filtered = []
        for func in self._elements:
            if any(target in func.external_call_targets for target in target_list):
                filtered.append(func)
        return self._create_new_collection(filtered)

    def with_asset_transfer_types(self, transfer_types: Union[str, List[str]]) -> "FunctionCollection":
        """Filter functions that perform specific types of asset transfers."""
        type_list = [transfer_types] if isinstance(transfer_types, str) else transfer_types
        filtered = []
        for func in self._elements:
            if any(transfer_type in func.asset_transfer_types for transfer_type in type_list):
                filtered.append(func)
        return self._create_new_collection(filtered)


class VariableCollection(BaseCollection):
    """Collection of variable declarations with fluent query methods."""

    def _create_new_collection(self, elements: List[ASTNode]) -> "VariableCollection":
        variables = [e for e in elements if isinstance(e, VariableDeclaration)]
        return VariableCollection(variables, self._engine)

    def with_name(self, pattern: Union[str, Pattern]) -> "VariableCollection":
        """Filter variables by name pattern."""
        filtered = [v for v in self._elements
                   if self._engine.pattern_matcher.matches_name_pattern(v.name, pattern)]
        return self._create_new_collection(filtered)

    def with_type(self, type_pattern: Union[str, Pattern]) -> "VariableCollection":
        """Filter variables by type pattern."""
        filtered = [v for v in self._elements
                   if self._engine.pattern_matcher.matches_name_pattern(v.type_name, type_pattern)]
        return self._create_new_collection(filtered)

    def with_visibility(self, visibility: Visibility) -> "VariableCollection":
        """Filter variables by visibility."""
        filtered = [v for v in self._elements
                   if v.visibility == visibility]
        return self._create_new_collection(filtered)

    def public(self) -> "VariableCollection":
        """Get only public variables."""
        return self.with_visibility(Visibility.PUBLIC)

    def private(self) -> "VariableCollection":
        """Get only private variables."""
        return self.with_visibility(Visibility.PRIVATE)

    def internal(self) -> "VariableCollection":
        """Get only internal variables."""
        return self.with_visibility(Visibility.INTERNAL)

    def constants(self) -> "VariableCollection":
        """Get only constant variables."""
        filtered = [v for v in self._elements if v.is_constant]
        return self._create_new_collection(filtered)

    def immutable(self) -> "VariableCollection":
        """Get only immutable variables."""
        filtered = [v for v in self._elements if v.is_immutable]
        return self._create_new_collection(filtered)

    def state_variables(self) -> "VariableCollection":
        """Get only state variables."""
        filtered = [v for v in self._elements if v.is_state_variable()]
        return self._create_new_collection(filtered)

    # Negation filters for visibility
    def not_public(self) -> "VariableCollection":
        """Get variables that are NOT public."""
        filtered = [v for v in self._elements if v.visibility != Visibility.PUBLIC]
        return self._create_new_collection(filtered)

    def not_private(self) -> "VariableCollection":
        """Get variables that are NOT private."""
        filtered = [v for v in self._elements if v.visibility != Visibility.PRIVATE]
        return self._create_new_collection(filtered)

    def not_internal(self) -> "VariableCollection":
        """Get variables that are NOT internal."""
        filtered = [v for v in self._elements if v.visibility != Visibility.INTERNAL]
        return self._create_new_collection(filtered)

    # Negation filters for special variable types
    def not_constants(self) -> "VariableCollection":
        """Get variables that are NOT constants."""
        filtered = [v for v in self._elements if not v.is_constant]
        return self._create_new_collection(filtered)

    def not_immutable(self) -> "VariableCollection":
        """Get variables that are NOT immutable."""
        filtered = [v for v in self._elements if not v.is_immutable]
        return self._create_new_collection(filtered)

    def not_state_variables(self) -> "VariableCollection":
        """Get variables that are NOT state variables."""
        filtered = [v for v in self._elements if not v.is_state_variable()]
        return self._create_new_collection(filtered)

    # Generic negation filters
    def not_with_visibility(self, visibility: Visibility) -> "VariableCollection":
        """Filter variables that do NOT have the specified visibility."""
        filtered = [v for v in self._elements if v.visibility != visibility]
        return self._create_new_collection(filtered)

    def not_with_type(self, type_pattern: Union[str, Pattern]) -> "VariableCollection":
        """Filter variables that do NOT match the type pattern."""
        filtered = [v for v in self._elements
                   if not self._engine.pattern_matcher.matches_name_pattern(v.type_name, type_pattern)]
        return self._create_new_collection(filtered)

    def get_parent_contract(self, variable: VariableDeclaration) -> Optional[ContractDeclaration]:
        """Get the parent contract of a variable."""
        return getattr(variable, 'parent_contract', None)

    def from_contract(self, contract_name: str) -> "VariableCollection":
        """Filter variables from a specific contract."""
        filtered = [v for v in self._elements
                   if v.parent_contract and v.parent_contract.name == contract_name]
        return self._create_new_collection(filtered)


class ModifierCollection(BaseCollection):
    """Collection of modifier declarations with fluent query methods."""

    def _create_new_collection(self, elements: List[ASTNode]) -> "ModifierCollection":
        modifiers = [e for e in elements if isinstance(e, ModifierDeclaration)]
        return ModifierCollection(modifiers, self._engine)

    def with_name(self, pattern: Union[str, Pattern]) -> "ModifierCollection":
        """Filter modifiers by name pattern."""
        filtered = [m for m in self._elements
                   if self._engine.pattern_matcher.matches_name_pattern(m.name, pattern)]
        return self._create_new_collection(filtered)

    def with_parameter_count(self, count: int) -> "ModifierCollection":
        """Filter modifiers by parameter count."""
        filtered = [m for m in self._elements if len(m.parameters) == count]
        return self._create_new_collection(filtered)


class EventCollection(BaseCollection):
    """Collection of event declarations with fluent query methods."""

    def _create_new_collection(self, elements: List[ASTNode]) -> "EventCollection":
        events = [e for e in elements if isinstance(e, EventDeclaration)]
        return EventCollection(events, self._engine)

    def with_name(self, pattern: Union[str, Pattern]) -> "EventCollection":
        """Filter events by name pattern."""
        filtered = [e for e in self._elements
                   if self._engine.pattern_matcher.matches_name_pattern(e.name, pattern)]
        return self._create_new_collection(filtered)

    def with_parameter_count(self, count: int) -> "EventCollection":
        """Filter events by parameter count."""
        filtered = [e for e in self._elements if len(e.parameters) == count]
        return self._create_new_collection(filtered)


class StatementCollection(BaseCollection):
    """Collection of statements with fluent query methods."""

    def _create_new_collection(self, elements: List[ASTNode]) -> "StatementCollection":
        statements = [e for e in elements if isinstance(e, Statement)]
        return StatementCollection(statements, self._engine)

    def with_type(self, statement_type: str) -> "StatementCollection":
        """Filter statements by type."""
        filtered = [s for s in self._elements if s.node_type.value == statement_type]
        return self._create_new_collection(filtered)

    def returns(self) -> "StatementCollection":
        """Get only return statements."""
        return self.with_type("return_statement")

    def blocks(self) -> "StatementCollection":
        """Get only block statements."""
        return self.with_type("block")


class ExpressionCollection(BaseCollection):
    """Collection of expressions with fluent query methods."""

    def _create_new_collection(self, elements: List[ASTNode]) -> "ExpressionCollection":
        expressions = [e for e in elements if isinstance(e, Expression)]
        return ExpressionCollection(expressions, self._engine)

    def with_type(self, expression_type: str) -> "ExpressionCollection":
        """Filter expressions by type."""
        filtered = [e for e in self._elements if e.node_type.value == expression_type]
        return self._create_new_collection(filtered)

    def calls(self) -> "ExpressionCollection":
        """Get only call expressions."""
        return self.with_type("call_expression")

    def identifiers(self) -> "ExpressionCollection":
        """Get only identifier expressions."""
        return self.with_type("identifier")

    def literals(self) -> "ExpressionCollection":
        """Get only literal expressions."""
        return self.with_type("literal")