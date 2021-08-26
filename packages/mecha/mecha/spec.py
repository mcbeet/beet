__all__ = [
    "Parser",
    "CommandSpecification",
    "CommandTree",
    "CommandPrototype",
    "CommandSignature",
    "CommandArgument",
]


from dataclasses import dataclass
from importlib.resources import read_text
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    NamedTuple,
    Optional,
    Protocol,
    Tuple,
    Union,
)

from beet.core.utils import FileSystemPath, JsonDict, extra_field
from pydantic import BaseModel
from tokenstream import TokenStream


class Parser(Protocol):
    """Protocol describing parser signature."""

    def __call__(self, stream: TokenStream) -> Any:
        ...


CommandSignature = Tuple[Union[str, "CommandArgument"], ...]


class CommandArgument(NamedTuple):
    """Class representing an argument in a command prototype."""

    name: str
    scope: Tuple[str, ...]


class CommandPrototype(NamedTuple):
    """Class representing a command prototype."""

    identifier: str
    signature: CommandSignature
    arguments: Tuple[int, ...]

    def get_argument(self, arg: Union[str, int]) -> CommandArgument:
        """Return the argument corresponding to the given name or index."""
        if isinstance(arg, str):
            for i in self.arguments:
                if self.get_argument(i).name == arg:
                    arg = i
                    break
            else:
                arg = len(self.signature)

        return self.signature[self.arguments[arg]]  # type: ignore


class CommandTree(BaseModel):
    """Deserialized representation of the command tree."""

    type: Literal["root", "literal", "argument"]
    parser: Optional[str] = None
    properties: Optional[JsonDict] = None
    executable: Optional[bool] = None
    redirect: Optional[Tuple[str, ...]] = None
    children: Optional[Dict[str, "CommandTree"]] = None

    @classmethod
    def load_from(
        cls,
        filename: Optional[FileSystemPath] = None,
        version: Optional[str] = None,
        patch: bool = True,
    ) -> "CommandTree":
        """Load the command tree from a file."""
        sources: List[str] = []

        if filename:
            sources.append(Path(filename).read_text())
        if version:
            sources.append(read_text("mecha.resources", f"{version}.json"))
        if patch:
            sources.append(read_text("mecha.resources", "patch.json"))

        tree = cls.parse_raw(sources[0])

        for source in sources[1:]:
            tree = tree.extend(cls.parse_raw(source))

        return tree

    def extend(self, other: "CommandTree") -> "CommandTree":
        """Merge nodes from another command tree."""
        self.type = other.type

        if other.parser is not None:
            self.parser = other.parser

        if other.properties is not None:
            self.properties = other.properties

        if other.executable is not None:
            self.executable = other.executable

        if other.redirect is not None:
            self.redirect = other.redirect

        if other.children:
            if self.children is None:
                self.children = {}
            for name, child in other.children.items():
                if name in self.children:
                    self.children[name].extend(child)
                else:
                    self.children[name] = child

        return self

    def get(self, *scope: str) -> Optional["CommandTree"]:
        """Retrieve a nested node."""
        if not scope:
            return self
        if not self.children:
            return None
        child = self.children.get(scope[0])
        return child and child.get(*scope[1:])

    def get_literal_children(self) -> Iterable[str]:
        """Yield the name of all the literal children."""
        if self.children:
            for name, child in self.children.items():
                if child.type == "literal":
                    yield name

    def get_argument_children(self) -> Iterable[str]:
        """Yield the name of all the argument children."""
        if self.children:
            for name, child in self.children.items():
                if child.type == "argument":
                    yield name


CommandTree.update_forward_refs()


@dataclass
class CommandSpecification:
    """Class responsible for managing the command specification."""

    tree: CommandTree = extra_field(
        default_factory=lambda: CommandTree.load_from(version="1_17")
    )
    flattened_tree: Dict[Tuple[str, ...], CommandTree] = extra_field(
        default_factory=dict
    )
    prototypes: Dict[str, CommandPrototype] = extra_field(default_factory=dict)
    parsers: Dict[str, Parser] = extra_field(default_factory=dict)

    def __post_init__(self):
        self.update()

    def add_commands(self, tree: CommandTree):
        """Extend the command tree and regenerate prototypes."""
        self.tree.extend(tree)
        self.update()

    def update(self):
        """Recalculate flattened tree and command prototypes."""
        self.flattened_tree = {}
        self.prototypes = {}

        self.generate_flattened_tree(self.tree)
        self.generate_prototypes(self.tree)

        subcommands = {
            last_arg.scope: ":".join(last_arg.scope) + ":"
            for prototype in self.prototypes.values()
            if prototype.signature
            and isinstance(last_arg := prototype.signature[-1], CommandArgument)
            and last_arg.name == "subcommand"
            and last_arg.scope
        }

        truncated: Dict[Tuple[str, ...], CommandPrototype] = {}

        for identifier, prototype in self.prototypes.items():
            for scope, prefix in subcommands.items():
                pivot = len(scope)
                if identifier.startswith(prefix):
                    truncated[scope] = prototype
                    self.prototypes[identifier] = CommandPrototype(
                        prototype.identifier,
                        prototype.signature[pivot:],
                        tuple(
                            offset
                            for arg in prototype.arguments
                            if (offset := arg - pivot) >= 0
                        ),
                    )

        for scope, prototype in truncated.items():
            pivot = len(scope)
            identifier = ":".join(scope + ("subcommand",))
            self.prototypes[identifier] = CommandPrototype(
                identifier,
                prototype.signature[:pivot] + (CommandArgument("subcommand", scope),),
                tuple(arg for arg in prototype.arguments if arg < pivot) + (pivot,),
            )

    def generate_flattened_tree(
        self,
        tree: CommandTree,
        scope: Tuple[str, ...] = (),
    ):
        """Traverse command tree and generate flattened lookup table."""
        self.flattened_tree[scope] = tree

        if tree.children:
            for name, child in tree.children.items():
                self.generate_flattened_tree(child, scope + (name,))

    def generate_prototypes(
        self,
        tree: CommandTree,
        scope: Tuple[str, ...] = (),
        signature: CommandSignature = (),
        arguments: Tuple[int, ...] = (),
    ):
        """Traverse command tree and generate prototypes."""
        subcommand = (
            tree.redirect is not None and scope[: len(tree.redirect)] == tree.redirect
        )

        if tree.redirect is not None and subcommand:
            identifier = ":".join(scope + ("subcommand",))
            self.prototypes[identifier] = CommandPrototype(
                identifier,
                signature + (CommandArgument("subcommand", tree.redirect),),
                arguments + (len(signature),),
            )

        if tree.executable:
            identifier = ":".join(scope)
            self.prototypes[identifier] = CommandPrototype(
                identifier, signature, arguments
            )

        children: Dict[str, CommandTree] = {}

        if tree.children:
            children.update(tree.children)
        if tree.redirect is not None and not subcommand:
            if redirect := self.flattened_tree[tree.redirect]:
                children.update(redirect.children or {})

        for name, child in children.items():
            self.generate_prototypes(
                child,
                scope + (name,),
                signature
                + (
                    CommandArgument(name, scope + (name,))
                    if child.type == "argument"
                    else name,
                ),
                arguments + ((len(signature),) if child.type == "argument" else ()),
            )
