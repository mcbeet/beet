"""Plugin for handling lexically nested resource locations."""

__all__ = [
    "AstNestedLocation",
    "UnresolvedNestedLocation",
    "nested_location",
    "parse_nested_location",
    "NestedLocationResolver",
    "NestedLocationTransformer",
]


from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Tuple, Union

from beet import Context, Generator
from beet.core.utils import required_field
from tokenstream import InvalidSyntax, TokenStream, set_location

from mecha import (
    AlternativeParser,
    AstCommand,
    AstNode,
    AstResourceLocation,
    AstRoot,
    CommandSpec,
    CommentDisambiguation,
    CompilationDatabase,
    Dispatcher,
    Mecha,
    MutatingReducer,
    delegate,
    rule,
)
from mecha.contrib.relative_location import resolve_relative_location


def beet_default(ctx: Context):
    ctx.require(nested_location)


def nested_location(ctx: Context):
    ctx.require("mecha.contrib.nesting")

    mc = ctx.inject(Mecha)

    mc.spec.parsers["nested_location"] = parse_nested_location
    mc.spec.parsers["resource_location_or_tag"] = CommentDisambiguation(
        AlternativeParser(
            [
                delegate("nested_location"),
                mc.spec.parsers["resource_location_or_tag"],
            ]
        )
    )

    mc.transform.extend(
        NestedLocationTransformer(
            nested_location_resolver=ctx.inject(NestedLocationResolver)
        )
    )


@dataclass(frozen=True, slots=True)
class AstNestedLocation(AstResourceLocation):
    """Ast nested location node."""

    def get_value(self) -> str:
        raise set_location(UnresolvedNestedLocation(self), self)

    def get_canonical_value(self) -> str:
        raise set_location(UnresolvedNestedLocation(self), self)


class UnresolvedNestedLocation(InvalidSyntax):
    node: AstNestedLocation

    def __init__(self, node: AstNestedLocation):
        super().__init__(node)
        self.node = node

    def __str__(self) -> str:
        tag = "#" * self.node.is_tag
        return f'Unresolved nested location "{tag}~/{self.node.path}".'


def parse_nested_location(stream: TokenStream) -> AstNestedLocation:
    with stream.syntax(nested_location=r"#?~/[0-9a-z_./-]*"):
        token = stream.expect("nested_location")
        value = token.value

        if is_tag := value.startswith("#"):
            value = value[1:]

        path = value[2:]

        node = AstNestedLocation(is_tag=is_tag, path=path)
        return set_location(node, token)


class NestedLocationResolver:
    spec: CommandSpec
    steps: List[Dispatcher[AstRoot]]
    database: CompilationDatabase
    generate: Generator

    def __init__(self, ctx: Context):
        mc = ctx.inject(Mecha)
        self.spec = mc.spec
        self.steps = mc.steps
        self.database = mc.database
        self.generate = ctx.generate

    def resolve(
        self,
        nested_location: AstNestedLocation = AstNestedLocation(path=""),
    ) -> Tuple[str, str]:
        root, relative_path = self.concat_nested_path(
            nested_location,
            self.walk_location_hierarchy(
                self.spec,
                (
                    (command.identifier, command.arguments)
                    for command in reversed(self.steps[self.database.step].stack)
                    if (
                        isinstance(command, AstCommand)
                        and command.arguments
                        and isinstance(command.arguments[-1], (AstCommand, AstRoot))
                        and all(nested_location is not arg for arg in command.arguments)
                    )
                ),
            ),
        )

        if not root:
            current_file = self.database.current
            root = self.database[current_file].resource_location

        if not root:
            return resolve_relative_location(relative_path, self.generate.path("dummy"))

        return resolve_relative_location(relative_path, root, include_root_file=True)

    @staticmethod
    def walk_location_hierarchy(
        spec: CommandSpec,
        stack: Iterable[Tuple[str, Tuple[AstNode, ...]]],
    ) -> Iterator[AstResourceLocation]:
        for identifier, arguments in stack:
            prototype = spec.prototypes[identifier]

            for i, argument_node in enumerate(arguments):
                node = spec.tree.get(prototype.get_argument(i).scope)
                if (
                    node
                    and node.parser == "minecraft:function"
                    and (tail := spec.tree.get(*identifier.split(":")))
                    and tail.redirect != ("execute",)
                    and isinstance(argument_node, AstResourceLocation)
                ):
                    yield argument_node
                    break

    @staticmethod
    def concat_nested_path(
        *args: Union[
            Iterable[Union[AstResourceLocation, str]], AstResourceLocation, str
        ],
    ) -> Tuple[Optional[str], str]:
        root = None
        fragments: List[str] = []

        for segments in args:
            if isinstance(segments, (AstResourceLocation, str)):
                segments = [segments]
            for segment in segments:
                if isinstance(segment, AstNestedLocation):
                    value = segment.path
                elif isinstance(segment, AstResourceLocation):
                    value = segment.get_canonical_value()
                else:
                    value = segment
                if ":" in value:
                    root = value
                    break
                fragments.append(value)

        return root, "/".join(reversed(fragments))


@dataclass
class NestedLocationTransformer(MutatingReducer):
    nested_location_resolver: NestedLocationResolver = required_field()

    @rule(AstNestedLocation)
    def nested_location(self, node: AstNestedLocation):
        namespace, resolved = self.nested_location_resolver.resolve(node)
        resource_location = AstResourceLocation(
            is_tag=node.is_tag,
            namespace=namespace,
            path=resolved,
        )
        return set_location(resource_location, node)
