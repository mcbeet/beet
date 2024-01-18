"""Plugin for parsing and resolving embeds in json and nbt strings."""


__all__ = [
    "AstJsonValueEmbed",
    "AstNbtValueEmbed",
    "EmbedHandler",
    "EmbedResolver",
    "EmbedParseCallback",
    "EmbedSerializeCallback",
]


from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, List, Optional, Protocol, TypeVar, Union

from beet import Context, TextFileBase
from beet.core.utils import required_field
from tokenstream import INITIAL_LOCATION, Preprocessor, SourceLocation, set_location

from mecha import (
    AstJsonValue,
    AstNbtValue,
    AstNode,
    CompilationDatabase,
    Diagnostic,
    DiagnosticError,
    Mecha,
    MutatingReducer,
    rule,
)

AstNodeType = TypeVar("AstNodeType", bound=AstNode)


@dataclass(frozen=True, slots=True)
class AstJsonValueEmbed(AstJsonValue):
    """Ast json value embed node."""

    embed: AstNode = required_field()


@dataclass(frozen=True, slots=True)
class AstNbtValueEmbed(AstNbtValue):
    """Ast nbt value embed node."""

    embed: AstNode = required_field()


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    embed_handler = ctx.inject(EmbedHandler)

    mc.steps.append(embed_handler.resolver)


class EmbedParseCallback(Protocol):
    """Callback required for parsing embed."""

    def __call__(
        self,
        source: TextFileBase[Any],
        *,
        using: str,
        preprocessor: Preprocessor,
    ) -> AstNode:
        ...


class EmbedSerializeCallback(Protocol):
    """Callback required for serializing embed."""

    def __call__(self, node: AstNode) -> str:
        ...


class EmbedHandler:
    """Service for handling embeds within json and nbt strings."""

    database: CompilationDatabase
    parse_callback: EmbedParseCallback
    serialize_callback: EmbedSerializeCallback
    resolver: "EmbedResolver"

    def __init__(self, arg: Union[Context, Mecha]):
        if isinstance(arg, Context):
            arg = arg.inject(Mecha)

        self.database = arg.database
        self.parse_callback = arg.parse
        self.serialize_callback = arg.serialize
        self.resolver = EmbedResolver(embed_handler=self)

    def parse(
        self,
        node: AstNodeType,
        source: Optional[TextFileBase[Any]] = None,
        *,
        using: str,
    ) -> AstNodeType:
        """Parse a string embed originating from the given source file.

        Defaults to the current source file.
        """
        if isinstance(node, (AstJsonValueEmbed, AstNbtValueEmbed)):
            return node
        if not isinstance(node, (AstJsonValue, AstNbtValue)):
            return node

        if source is None:
            source = self.database.current
        compilation_unit = self.database[source]

        if not isinstance(node.value, str):
            d = Diagnostic(
                "error",
                f'Couldn\'t parse value of type "{type(node.value).__name__}" as "{using}" embed.',
            )
            raise set_location(d, node)

        value = str(node.value)
        source_mappings: List[SourceLocation] = []
        preprocessed_mappings: List[SourceLocation] = []

        if (
            compilation_unit.source
            and not node.location.unknown
            and not node.end_location.unknown
        ):
            source_location = node.location
            preprocessed_location = INITIAL_LOCATION

            raw_value = compilation_unit.source[
                node.location.pos : node.end_location.pos
            ]

            index = 0
            raw_index = 0

            sequence_matcher = SequenceMatcher(None, value, raw_value)
            for i, j, size in sequence_matcher.get_matching_blocks():
                if size == 0:
                    continue

                source_mappings.append(source_location)
                preprocessed_mappings.append(preprocessed_location)

                extra = raw_value[raw_index:j]
                missing = value[index:i]

                if extra or missing:
                    source_location = source_location.skip_over(extra)
                    preprocessed_location = preprocessed_location.skip_over(missing)
                    source_mappings.append(source_location)
                    preprocessed_mappings.append(preprocessed_location)

                index = i + size
                raw_index = j + size

                source_location = source_location.skip_over(raw_value[j:raw_index])
                preprocessed_location = preprocessed_location.skip_over(value[i:index])

            source_mappings.append(source_location)
            preprocessed_mappings.append(preprocessed_location)

        try:
            embed = self.parse_callback(
                source,
                using=using,
                preprocessor=lambda _: (value, source_mappings, preprocessed_mappings),
            )
        except DiagnosticError as exc:
            raise exc.diagnostics.exceptions[0] from None

        if isinstance(node, AstJsonValue):
            embed_type = AstJsonValueEmbed
        else:
            embed_type = AstNbtValueEmbed

        return set_location(embed_type(value=node.value, embed=embed), node)  # type: ignore


@dataclass
class EmbedResolver(MutatingReducer):
    """Mutating reducer that serializes embeds back to regular json and nbt strings."""

    embed_handler: EmbedHandler = required_field()

    @rule(AstJsonValueEmbed)
    def json_embed(self, node: AstJsonValueEmbed):
        return set_location(
            AstJsonValue.from_value(self.embed_handler.serialize_callback(node.embed)),
            node,
        )

    @rule(AstNbtValueEmbed)
    def nbt_embed(self, node: AstNbtValueEmbed):
        return set_location(
            AstNbtValue.from_value(self.embed_handler.serialize_callback(node.embed)),
            node,
        )
