"""Plugin for handling message references in commands."""


__all__ = [
    "AstMessageReference",
    "MessageReferenceParser",
    "MessageReferenceTransformer",
    "MessageReferenceSerializer",
]


from dataclasses import dataclass
from typing import Any, List, Optional

from beet import Context
from beet.contrib.messages import MessageManager
from beet.core.utils import required_field
from tokenstream import TokenStream, set_location

from mecha import (
    AstJson,
    AstLiteral,
    AstNode,
    AstResourceLocation,
    Diagnostic,
    Mecha,
    MutatingReducer,
    Parser,
    Visitor,
    delegate,
    rule,
)


@dataclass(frozen=True)
class AstMessageReference(AstNode):
    """Ast message reference node."""

    name: AstResourceLocation = required_field()
    path: Optional[AstLiteral] = None


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    messages = ctx.inject(MessageManager)

    component = "command:argument:minecraft:component"
    mc.spec.parsers[component] = MessageReferenceParser(mc.spec.parsers[component])

    mc.transform.extend(MessageReferenceTransformer(messages=messages))
    mc.serialize.extend(MessageReferenceSerializer())


@dataclass
class MessageReferenceParser:
    """Parser for message references."""

    component_parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        token = stream.get(("literal", "from"))
        if not token:
            return self.component_parser(stream)

        with stream.syntax(path=r"\w+(?:\[\d+\]|\.\w+)*"):
            name = delegate("resource_location", stream)
            path = stream.get("path")

        if path is not None:
            path = set_location(AstLiteral(value=path.value), path)

        node = AstMessageReference(name=name, path=path)
        return set_location(node, token, path or name)


@dataclass
class MessageReferenceTransformer(MutatingReducer):
    """Transformer that turns message references into inline text components."""

    messages: MessageManager = required_field()

    @rule(AstMessageReference)
    def message_reference(self, node: AstMessageReference):
        name = node.name.get_canonical_value()
        path = node.path and node.path.value

        try:
            message = self.messages.get(name, path)
        except (KeyError, IndexError):
            path = f"{path!r} in " if path else ""
            raise Diagnostic("error", f"Message not found {path}{name!r}.") from None

        return set_location(AstJson.from_value(message), node)


class MessageReferenceSerializer(Visitor):
    """Serializer for message references."""

    @rule(AstMessageReference)
    def message_reference(self, node: AstMessageReference, result: List[str]):
        result.append("from ")
        yield node.name
        if node.path:
            result.append(" ")
            yield node.path
