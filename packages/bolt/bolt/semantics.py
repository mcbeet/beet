__all__ = [
    "LexicalScope",
    "GlobalScope",
    "FunctionScope",
    "MacroScope",
    "ProcMacroScope",
    "ClassScope",
    "Variable",
    "Binding",
    "UndefinedIdentifier",
    "UnboundLocalIdentifier",
    "InconsistentIdentifierStorage",
]


from dataclasses import dataclass, field, replace
from typing import Dict, List, Literal, Optional, Set, Tuple, Type, TypeVar

from beet.core.utils import extra_field
from mecha import AstNode
from tokenstream import InvalidSyntax, set_location

from .utils import suggest_typo

LexicalScopeType = TypeVar("LexicalScopeType", bound="LexicalScope")


class UndefinedIdentifier(InvalidSyntax):
    """Raised when an identifier is not defined.

    Attributes
    ----------
    identifier
        The identifier that couldn't be found.
    lexical_scope
        The current scope.
    """

    identifier: str
    lexical_scope: "LexicalScope"

    def __init__(self, identifier: str, lexical_scope: "LexicalScope"):
        super().__init__(identifier, lexical_scope)
        self.identifier = identifier
        self.lexical_scope = lexical_scope

    def __str__(self) -> str:
        msg = f'Identifier "{self.identifier}" is not defined.'

        variable_names = self.lexical_scope.list_variables() - {self.identifier}
        if suggestion := suggest_typo(self.identifier, variable_names):
            msg += f" Did you mean {suggestion}?"

        return msg


class UnboundLocalIdentifier(UndefinedIdentifier):
    """Raised when mutating a variable before assignment.

    This is a specialized error for code that tries to access and mutate a variable
    with no local binding in the current scope.
    """

    def __init__(self, identifier: str, lexical_scope: "LexicalScope"):
        super().__init__(identifier, lexical_scope)
        if lexical_scope.parent and lexical_scope.parent.has_variable(identifier):
            self.notes.append(
                f'Use "global {identifier}" or "nonlocal {identifier}" to mutate the variable defined in outer scope.'
            )


class InconsistentIdentifierStorage(InvalidSyntax):
    """Raised when trying to change the storage of an already existing variable.

    Attributes
    ----------
    identifier
        The identifier with a prior conflicting definition in the current scope.
    storage
        The target storage of the inconsistent binding.
    lexical_scope
        The current scope.
    """

    identifier: str
    storage: Literal["local", "nonlocal", "global"]
    lexical_scope: "LexicalScope"

    def __init__(
        self,
        identifier: str,
        storage: Literal["local", "nonlocal", "global"],
        lexical_scope: "LexicalScope",
    ):
        super().__init__(identifier, storage, lexical_scope)
        self.identifier = identifier
        self.storage = storage
        self.lexical_scope = lexical_scope

    def __str__(self) -> str:
        return f'Can\'t make {self.lexical_scope.variables[self.identifier].storage} identifier "{self.identifier}" {self.storage}.'


@dataclass
class Binding:
    """Variable binding.

    Attributes
    ----------
    origin
        The code fragment performing the variable binding.
    references
        Other parts of the code that use the value set by the binding.
    cutoff
        The number of references in common after forking.
    """

    origin: AstNode
    references: List[AstNode] = field(default_factory=list)

    cutoff: int = extra_field(default=0)

    def fork(self) -> "Binding":
        return replace(
            self,
            references=self.references.copy(),
            cutoff=len(self.references),
        )

    def reconcile(self, binding: "Binding"):
        self.references += binding.references[binding.cutoff :]


@dataclass
class Variable:
    """Variable definition.

    Attributes
    ----------
    storage
        The type of storage for the variable.
    bindings
        Associated bindings updating the value or the storage of the variable.
    cutoff
        The number of bindings in common after forking.
    """

    storage: Literal["local", "nonlocal", "global", "deleted"] = "local"
    bindings: List[Binding] = field(default_factory=list)

    cutoff: int = extra_field(default=0)

    def fork(self):
        return replace(
            self,
            bindings=[binding.fork() for binding in self.bindings],
            cutoff=len(self.bindings),
        )

    def reconcile(self, variable: "Variable"):
        for i, binding in enumerate(variable.bindings[: variable.cutoff]):
            self.bindings[i].reconcile(binding)

        for new_binding in variable.bindings[variable.cutoff :]:
            self.bindings.append(new_binding)


@dataclass
class LexicalScope:
    """Class for managing variable scopes during parsing.

    Attributes
    ----------
    parent
        Parent scope if the current scope has one.
    variables
        Dictionary holding variable definitions.
    dirty
        Flag to skip reconciliation after forking in case no additional
        variables or bindings were introduced.
    """

    variables: Dict[str, Variable] = field(default_factory=dict)

    anchor: Optional[AstNode] = extra_field(default=None)
    parent: Optional["LexicalScope"] = extra_field(default=None)
    children: List["LexicalScope"] = extra_field(default_factory=list)

    dirty: bool = extra_field(default=False)

    next_branch: Optional["LexicalScope"] = extra_field(default=None)
    next_deferred: Optional["LexicalScope"] = extra_field(default=None)
    pending_bindings: List[Tuple[str, AstNode]] = extra_field(default_factory=list)

    def has_binding(self, identifier: str, search_parents: bool = False) -> bool:
        variable = self.variables.get(identifier)
        return (variable and variable.storage != "deleted") or bool(
            search_parents
            and self.parent
            and self.parent.has_binding(identifier, search_parents=True)
        )

    def reference_binding(self, identifier: str, node: AstNode):
        if not self.has_binding(identifier):
            raise set_location(UnboundLocalIdentifier(identifier, self), node)
        self.reference_variable(identifier, node)

    def has_variable(self, identifier: str) -> bool:
        return identifier in self.variables or bool(
            self.parent and self.parent.has_variable(identifier)
        )

    def list_variables(self) -> Set[str]:
        all_variables = set(self.variables)
        if self.parent:
            all_variables |= self.parent.list_variables()
        return all_variables

    def reference_variable(
        self,
        identifier: str,
        node: AstNode,
        scope: Optional["LexicalScope"] = None,
    ):
        if not scope:
            scope = self

        if variable := self.variables.get(identifier):
            binding = variable.bindings[-1]

            if not binding.references or binding.references[-1] is not node:
                self.dirty = True
                binding.references.append(node)

                if variable.storage != "local" and self.parent:
                    self.parent.reference_variable(identifier, node, scope)

            return

        if not self.parent:
            raise set_location(UndefinedIdentifier(identifier, scope), node)

        self.parent.reference_variable(identifier, node, scope)

    def bind_variable(self, identifier: str, node: AstNode):
        self.dirty = True

        if self.has_binding(identifier):
            self.reference_variable(identifier, node)

        variable = self.variables.get(identifier)
        if not variable:
            variable = Variable()
            self.variables[identifier] = variable

        variable.bindings.append(Binding(origin=node))

        if variable.storage != "local" and self.parent:
            self.parent.bind_variable(identifier, node)

    def bind_storage(
        self,
        identifier: str,
        storage: Literal["nonlocal", "global", "deleted"],
        node: AstNode,
    ):
        self.dirty = True

        self.reference_variable(identifier, node)

        variable = self.variables.get(identifier)
        if not variable:
            variable = Variable(storage=storage)
            self.variables[identifier] = variable
        elif storage == "deleted":
            variable.storage = storage
        elif variable.storage != storage:
            exc = InconsistentIdentifierStorage(identifier, storage, self)
            raise set_location(exc, node)

        variable.bindings.append(Binding(origin=node))

    def push(self, scope_type: Type["LexicalScopeType"]) -> "LexicalScopeType":
        child = scope_type(parent=self)
        self.children.append(child)
        return child

    def deferred(self, scope_type: Type["LexicalScopeType"]) -> "LexicalScopeType":
        if not isinstance(self.next_deferred, scope_type):
            self.next_deferred = self.push(scope_type)
        return self.next_deferred  # type: ignore

    def deferred_complete(self):
        self.next_deferred = None

    def fork(self) -> "LexicalScope":
        return replace(
            self,
            parent=self.parent and self.parent.fork(),
            dirty=False,
            variables=self.fork_variables(),
        )

    def fork_variables(self) -> Dict[str, Variable]:
        return {
            identifier: variable.fork()
            for identifier, variable in self.variables.items()
        }

    def reconcile(self, lexical_scope: "LexicalScope"):
        if lexical_scope.dirty:
            self.dirty = True
            self.reconcile_variables(lexical_scope.variables)
            if self.parent and lexical_scope.parent:
                self.parent.reconcile(lexical_scope.parent)

    def reconcile_variables(self, variables: Dict[str, Variable]):
        for identifier, variable in variables.items():
            if current_variable := self.variables.get(identifier):
                current_variable.reconcile(variable)
            else:
                self.variables[identifier] = variable

    def create_pending_binding(self, identifier: str, node: AstNode):
        self.pending_bindings.append((identifier, node))

    def flush_pending_bindings(self):
        for identifier, node in self.pending_bindings:
            self.bind_variable(identifier, node)
        self.pending_bindings.clear()


@dataclass
class GlobalScope(LexicalScope):
    """Specialized global scope to fork more efficiently."""

    identifiers: Set[str] = field(default_factory=set)

    def has_variable(self, identifier: str) -> bool:
        return identifier in self.identifiers or super().has_variable(identifier)

    def list_variables(self) -> Set[str]:
        return self.identifiers | super().list_variables()

    def reference_variable(
        self,
        identifier: str,
        node: AstNode,
        scope: Optional["LexicalScope"] = None,
    ):
        if identifier not in self.identifiers or identifier in self.variables:
            super().reference_variable(identifier, node, scope)


class FunctionScope(LexicalScope):
    """Dedicated type for function scope."""


class MacroScope(FunctionScope):
    """Dedicated type for macro scope."""


class ProcMacroScope(FunctionScope):
    """Dedicated type for proc macro scope."""


class ClassScope(LexicalScope):
    """Dedicated type for class scope."""

    def push(self, scope_type: Type["LexicalScopeType"]) -> "LexicalScopeType":
        if issubclass(scope_type, FunctionScope):
            if not self.parent:
                raise ValueError("Class scope has no parent.")
            return self.parent.push(scope_type)
        return super().push(scope_type)
