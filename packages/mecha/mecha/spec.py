__all__ = [
    "Parser",
    "CommandSpec",
]


from dataclasses import dataclass
from typing import Any, Dict, Protocol, Set, Tuple, Union

from beet import LATEST_MINECRAFT_VERSION
from beet.core.utils import JsonDict, extra_field
from tokenstream import TokenStream

from .config import CommandTree
from .prototype import CommandArgument, CommandPrototype, CommandSignature


class Parser(Protocol):
    """Protocol describing parser signature."""

    def __call__(self, stream: TokenStream) -> Any:
        ...


@dataclass
class CommandSpec:
    """Class responsible for managing the command specification."""

    multiline: bool = False

    tree: CommandTree = extra_field(
        default_factory=lambda: CommandTree.load_from(version=LATEST_MINECRAFT_VERSION)
    )
    prototypes: Dict[str, CommandPrototype] = extra_field(default_factory=dict)

    parsers: Dict[str, Parser] = extra_field(default_factory=dict)

    def __post_init__(self):
        self.update()

    def add_commands(self, tree: Union[CommandTree, JsonDict]):
        """Extend the command tree and regenerate prototypes."""
        if not isinstance(tree, CommandTree):
            tree = CommandTree(**tree)
        self.tree.extend(tree)
        self.update()

    def update(self):
        """Recalculate command prototypes."""
        self.tree.resolve()

        self.prototypes.clear()
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

        recursive = False
        hoisted: Set[str] = set()

        if target := self.tree.get(tree.redirect):
            recursive = target.subcommand
            if recursive and target.children:
                hoisted.update(target.children)

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

        if tree.children:
            for name, child in tree.children.items():
                if name in hoisted:
                    continue
                elif child.type == "literal":
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
