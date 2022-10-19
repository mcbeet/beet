"""Plugin for handling nested yaml."""


__all__ = [
    "BaseYamlObjectCollector",
    "BaseYamlArrayCollector",
    "JsonObjectCollector",
    "JsonArrayCollector",
    "NbtCompoundCollector",
    "NbtListCollector",
    "NestedYamlParser",
    "NestedYamlContextProvider",
    "collect_json_string",
    "collect_nbt_string",
]


from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterator, List, TypeVar

from beet import Context
from nbtlib import String
from tokenstream import SourceLocation, TokenStream, set_location

from mecha import (
    AstChildren,
    AstJson,
    AstJsonArray,
    AstJsonObject,
    AstJsonObjectEntry,
    AstJsonObjectKey,
    AstJsonValue,
    AstNbt,
    AstNbtCompound,
    AstNbtCompoundEntry,
    AstNbtCompoundKey,
    AstNbtList,
    AstNbtValue,
    Mecha,
    Parser,
    consume_line_continuation,
    delegate,
)
from mecha.utils import JsonQuoteHelper, QuoteHelper

EntryType = TypeVar("EntryType")
ValueType = TypeVar("ValueType")


def beet_default(ctx: Context):
    ctx.require("mecha.contrib.nesting")

    mc = ctx.inject(Mecha)

    mc.spec.parsers["json"] = NestedYamlParser(
        parser=delegate("json"),
        original_parser=mc.spec.parsers["json"],
        object_collector=JsonObjectCollector(),
        array_collector=JsonArrayCollector(),
        string_collector=collect_json_string,
    )

    mc.spec.parsers["nbt"] = NestedYamlParser(
        parser=delegate("nbt"),
        original_parser=mc.spec.parsers["nbt"],
        object_collector=NbtCompoundCollector(),
        array_collector=NbtListCollector(),
        string_collector=collect_nbt_string,
    )

    for argument_name in [
        "command:argument:minecraft:component",
        "command:argument:minecraft:nbt_compound_tag",
        "command:argument:minecraft:nbt_tag",
        "command:argument:mecha:nested_json",
    ]:
        if parser := mc.spec.parsers.get(argument_name):
            mc.spec.parsers[argument_name] = NestedYamlContextProvider(parser)


@dataclass
class BaseYamlObjectCollector(Generic[EntryType, ValueType]):
    """Base class for yaml object collectors."""

    entries: List[EntryType] = field(default_factory=list)

    @contextmanager
    def start(self) -> Iterator[None]:
        """Start a new object."""
        previous_entries = self.entries
        self.entries = []
        try:
            yield
        finally:
            self.entries = previous_entries

    def emit(
        self,
        key: str,
        value: ValueType,
        location: SourceLocation,
        end_location: SourceLocation,
    ) -> None:
        """Emit an object entry."""
        raise NotImplementedError()

    def result(self) -> ValueType:
        """Output the final ast node."""
        raise NotImplementedError()


@dataclass
class BaseYamlArrayCollector(Generic[ValueType]):
    """Base class for yaml array collectors."""

    elements: List[ValueType] = field(default_factory=list)

    @contextmanager
    def start(self) -> Iterator[None]:
        """Start a new array."""
        previous_elements = self.elements
        self.elements = []
        try:
            yield
        finally:
            self.elements = previous_elements

    def emit(self, value: ValueType) -> None:
        """Emit an array element."""
        raise NotImplementedError()

    def result(self) -> ValueType:
        """Output the final ast node."""
        raise NotImplementedError()


class JsonObjectCollector(BaseYamlObjectCollector[AstJsonObjectEntry, AstJson]):
    """Collect yaml as json objects."""

    def emit(
        self,
        key: str,
        value: AstJson,
        location: SourceLocation,
        end_location: SourceLocation,
    ) -> None:
        key_node = AstJsonObjectKey(value=key)
        key_node = set_location(key_node, location, end_location)
        entry_node = AstJsonObjectEntry(key=key_node, value=value)
        self.entries.append(set_location(entry_node, key_node, value))

    def result(self) -> AstJson:
        node = AstJsonObject(entries=AstChildren(self.entries))
        return set_location(node, node.entries[0], node.entries[-1])


class JsonArrayCollector(BaseYamlArrayCollector[AstJson]):
    """Collect yaml as json arrays."""

    def emit(self, value: AstJson) -> None:
        self.elements.append(value)

    def result(self) -> AstJson:
        node = AstJsonArray(elements=AstChildren(self.elements))
        return set_location(node, node.elements[0], node.elements[-1])


def collect_json_string(
    value: str,
    location: SourceLocation,
    end_location: SourceLocation,
) -> AstJson:
    """Collect yaml string as json node."""
    return set_location(AstJsonValue(value=value), location, end_location)


class NbtCompoundCollector(BaseYamlObjectCollector[AstNbtCompoundEntry, AstNbt]):
    """Collect yaml as nbt compounds."""

    def emit(
        self,
        key: str,
        value: AstNbt,
        location: SourceLocation,
        end_location: SourceLocation,
    ) -> None:
        key_node = AstNbtCompoundKey(value=key)
        key_node = set_location(key_node, location, end_location)
        entry_node = AstNbtCompoundEntry(key=key_node, value=value)
        self.entries.append(set_location(entry_node, key_node, value))

    def result(self) -> AstNbt:
        node = AstNbtCompound(entries=AstChildren(self.entries))
        return set_location(node, node.entries[0], node.entries[-1])


class NbtListCollector(BaseYamlArrayCollector[AstNbt]):
    """Collect yaml as nbt lists."""

    def emit(self, value: AstNbt) -> None:
        self.elements.append(value)

    def result(self) -> AstNbt:
        node = AstNbtList(elements=AstChildren(self.elements))
        return set_location(node, node.elements[0], node.elements[-1])


def collect_nbt_string(
    value: str,
    location: SourceLocation,
    end_location: SourceLocation,
) -> AstNbt:
    """Collect yaml string as nbt node."""
    return set_location(AstNbtValue(value=String(value)), location, end_location)


@dataclass
class NestedYamlParser:
    """Parser for nested yaml."""

    parser: Parser
    original_parser: Parser

    object_collector: BaseYamlObjectCollector[Any, Any]
    array_collector: BaseYamlArrayCollector[Any]
    string_collector: Callable[[str, SourceLocation, SourceLocation], Any]

    quote_helper: QuoteHelper = field(default_factory=JsonQuoteHelper)

    def __call__(self, stream: TokenStream) -> Any:
        nested_yaml = stream.data.get("nested_yaml")

        if not nested_yaml:
            return self.original_parser(stream)

        elif nested_yaml == "init":
            with stream.syntax(colon=r":"):
                if stream.get("colon"):
                    with stream.provide(nested_yaml="active"):
                        return self.parser(stream)
                else:
                    with stream.reset("nested_yaml"):
                        return self.original_parser(stream)

        with stream.intercept("newline"), stream.syntax(
            colon=r":",
            dash=r"\-",
            key=r"[a-zA-Z0-9._+-]+",
        ):
            if consume_line_continuation(stream):
                return self.parse_yaml(stream)

        with stream.ignore("newline"), stream.syntax(
            string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
        ):
            if token := stream.get("string"):
                return self.string_collector(
                    self.quote_helper.unquote_string(token),
                    token.location,
                    token.end_location,
                )
            else:
                return self.original_parser(stream)

    def parse_yaml(self, stream: TokenStream) -> Any:
        if dash := stream.get("dash"):
            with self.array_collector.start():
                while True:
                    with stream.provide(line_indentation=dash.location.colno - 1):
                        with stream.checkpoint() as commit:
                            self.array_collector.emit(self.parse_yaml(stream))
                            commit()
                        if commit.rollback:
                            self.array_collector.emit(self.parser(stream))

                    if consume_line_continuation(stream):
                        dash = stream.expect("dash")
                    else:
                        return self.array_collector.result()

        key = stream.expect("key")
        stream.expect("colon")

        with self.object_collector.start():
            while True:
                with stream.provide(line_indentation=key.location.colno - 1):
                    self.object_collector.emit(
                        key=key.value,
                        value=self.parser(stream),
                        location=key.location,
                        end_location=key.end_location,
                    )

                if consume_line_continuation(stream):
                    key = stream.expect("key")
                    stream.expect("colon")
                else:
                    return self.object_collector.result()


@dataclass
class NestedYamlContextProvider:
    """Parser that enables nested yaml."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.provide(nested_yaml="init"):
            return self.parser(stream)
