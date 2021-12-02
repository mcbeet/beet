"""Plugin that resolves relative resource locations."""


__all__ = [
    "RelativeResourceLocationParser",
]


from dataclasses import dataclass, replace
from pathlib import PurePosixPath

from beet import Context
from tokenstream import InvalidSyntax, TokenStream, set_location

from mecha import AstResourceLocation, CompilationDatabase, Mecha, Parser


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.spec.parsers["resource_location_or_tag"] = RelativeResourceLocationParser(
        database=mc.database,
        parser=mc.spec.parsers["resource_location_or_tag"],
    )


@dataclass
class RelativeResourceLocationParser:
    """Parser that resolves relative resource locations."""

    database: CompilationDatabase
    parser: Parser

    def __call__(self, stream: TokenStream) -> AstResourceLocation:
        node: AstResourceLocation = self.parser(stream)

        if node.namespace is None and node.path.startswith(("./", "../")):
            current_file = self.database.current
            path = self.database[current_file].resource_location

            if not path:
                exc = InvalidSyntax(
                    f"Can't resolve relative resource location {node.path!r}."
                )
                raise set_location(exc, node)

            namespace, _, current_path = path.partition(":")

            resolved = PurePosixPath(current_path).parent
            for name in node.path.split("/"):
                if name == "..":
                    resolved = resolved.parent
                elif name and name != ".":
                    resolved = resolved / name

            return replace(node, namespace=namespace, path=str(resolved))

        return node
