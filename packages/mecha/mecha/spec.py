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
    subcommand: bool = False

    @classmethod
    def load_from(
        cls,
        filename: Optional[FileSystemPath] = None,
        version: Optional[str] = None,
    ) -> "CommandTree":
        """Load the command tree from a file."""
        sources: List[str] = []

        if filename:
            sources.append(Path(filename).read_text())
        if version:
            sources.append(read_text("mecha.resources", f"{version}.json"))

        tree = cls.parse_raw(sources[0])

        for source in sources[1:]:
            tree = tree.extend(cls.parse_raw(source))

        return tree

    def get(self, *scope: Union[str, Tuple[str, ...], None]) -> Optional["CommandTree"]:
        """Retrieve a nested node."""
        node = self
        for arg in scope:
            if arg is None:
                return None
            for name in [arg] if isinstance(arg, str) else arg:
                if node.children:
                    node = node.children.get(name)
                    if not node:
                        return None
        return node

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

    def resolve(
        self,
        root: Optional["CommandTree"] = None,
        scope: Tuple[str, ...] = (),
    ) -> "CommandTree":
        """Resolve redirections and subcommands."""
        if not root:
            root = self

        if self.redirect is not None:
            if target := root.get(self.redirect):
                if scope[: len(self.redirect)] == self.redirect:
                    target.subcommand = True
                self.children = target.children
            else:
                raise ValueError(f"Invalid redirect {self.redirect}.")

        elif self.children:
            for name, child in self.children.items():
                child.resolve(root, scope + (name,))

        elif not self.executable:
            self.redirect = ()
            self.resolve(root, scope)

        return self


CommandTree.update_forward_refs()


@dataclass
class CommandSpecification:
    """Class responsible for managing the command specification."""

    tree: CommandTree = extra_field(
        default_factory=lambda: CommandTree.load_from(version="1_17")
    )
    parsers: Dict[str, Parser] = extra_field(default_factory=dict)

    prototypes: Dict[str, CommandPrototype] = extra_field(init=False)

    def __post_init__(self):
        self.update()

    def add_commands(self, tree: CommandTree):
        """Extend the command tree and regenerate prototypes."""
        self.tree.extend(tree)
        self.update()

    def update(self):
        """Recalculate command prototypes."""
        self.tree.resolve()

        self.prototypes = {}
        self.generate_prototypes(self.tree)

    def generate_prototypes(
        self,
        tree: CommandTree,
        scope: Tuple[str, ...] = (),
        signature: CommandSignature = (),
        arguments: Tuple[int, ...] = (),
    ):
        """Traverse command tree and generate prototypes."""
        if tree.executable:
            identifier = ":".join(scope)
            self.prototypes[identifier] = CommandPrototype(
                identifier, signature, arguments
            )

        target = self.tree.get(tree.redirect)
        recursive = target and target.subcommand

        if scope and tree.subcommand or recursive:
            identifier = ":".join(scope + ("subcommand",))
            argument_scope = tree.redirect if tree.redirect is not None else scope
            self.prototypes[identifier] = CommandPrototype(
                identifier,
                signature + (CommandArgument("subcommand", argument_scope),),
                arguments + (len(signature),),
            )
            signature = signature[len(scope) :]
            arguments = tuple(
                offset for arg in arguments if (offset := arg - len(scope)) >= 0
            )

        if tree.children and not recursive:
            for name, child in tree.children.items():
                if child.type == "literal":
                    self.generate_prototypes(
                        child,
                        scope + (name,),
                        signature + (name,),
                        arguments,
                    )
                elif child.type == "argument":
                    self.generate_prototypes(
                        child,
                        scope + (name,),
                        signature + (CommandArgument(name, scope + (name,)),),
                        arguments + (len(signature),),
                    )
