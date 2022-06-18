__all__ = [
    "CommandTree",
]


import json
from importlib.resources import read_text
from pathlib import Path
from typing import Dict, Iterator, List, Literal, Optional, Set, Tuple, Union

from beet import ErrorMessage
from beet.core.utils import FileSystemPath, JsonDict, VersionNumber, split_version
from pydantic import BaseModel


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
        *args: FileSystemPath,
        version: Optional[VersionNumber] = None,
        unpatched: bool = False,
    ) -> "CommandTree":
        """Load the command tree from a file."""
        sources: List[str] = []

        for filename in args:
            sources.append(Path(filename).read_text())

        version = split_version(version) if version is not None else None

        if version:
            version_name = "_".join(map(str, version))
            try:
                sources.append(read_text("mecha.resources", f"{version_name}.json"))
            except FileNotFoundError as exc:
                raise ErrorMessage(f"Invalid minecraft version {version!r}.") from exc

        tree = cls.parse_raw(sources[0])

        for source in sources[1:]:
            tree.extend(cls.parse_raw(source))

        if version and not unpatched:
            for patch in json.loads(read_text("mecha.resources", "patches.json")):
                if any(split_version(v) == version for v in patch["versions"]):
                    tree.extend(cls(**patch["config"]))

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

    def get_literal(self, name: str) -> Optional["CommandTree"]:
        """Retrieve a literal child by name."""
        if self.children:
            if child := self.children.get(name):
                if child.type == "literal":
                    return child
        return None

    def get_argument(self, name: str) -> Optional["CommandTree"]:
        """Retrieve an argument child by name."""
        if self.children:
            if child := self.children.get(name):
                if child.type == "argument":
                    return child
        return None

    def get_all_literals(self) -> Iterator[Tuple[str, "CommandTree"]]:
        """Retrieve all the literal children."""
        if self.children:
            for name, child in self.children.items():
                if child.type == "literal":
                    yield name, child

    def get_all_arguments(self) -> Iterator[Tuple[str, "CommandTree"]]:
        """Retrieve all the argument children."""
        if self.children:
            for name, child in self.children.items():
                if child.type == "argument":
                    yield name, child

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

        hoisted: Set[str] = set()

        if self.redirect is not None:
            if target := root.get(self.redirect):
                if scope[: len(self.redirect)] == self.redirect:
                    target.subcommand = True
                if target.children:
                    if not self.children:
                        self.children = {}
                    self.children.update(target.children)
                    hoisted.update(target.children)
            else:
                raise ValueError(f"Invalid redirect {self.redirect}.")

        if self.children:
            for name, child in self.children.items():
                if name not in hoisted:
                    child.resolve(root, scope + (name,))

        if self.redirect is None and not self.children and not self.executable:
            self.redirect = ()
            self.resolve(root, scope)

        return self


CommandTree.update_forward_refs()
