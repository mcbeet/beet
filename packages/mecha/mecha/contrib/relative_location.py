"""Plugin that resolves relative resource locations."""


__all__ = [
    "RelativeResourceLocationParser",
    "resolve_using_database",
]


from dataclasses import dataclass, replace
from pathlib import PurePosixPath
from typing import Tuple

from beet import Context
from tokenstream import InvalidSyntax, SourceLocation, TokenStream, set_location

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
            namespace, resolved = resolve_using_database(
                relative_path=node.path,
                database=self.database,
                location=node.location,
                end_location=node.end_location,
            )

            return replace(node, namespace=namespace, path=resolved)

        return node


def resolve_using_database(
    relative_path: str,
    database: CompilationDatabase,
    location: SourceLocation,
    end_location: SourceLocation,
) -> Tuple[str, str]:
    """Resolve relative resource location."""
    current_file = database.current
    path = database[current_file].resource_location

    if not path:
        exc = InvalidSyntax(
            f"Can't resolve relative resource location {relative_path!r}."
        )
        raise set_location(exc, location, end_location)

    namespace, _, current_path = path.partition(":")

    resolved = PurePosixPath(current_path).parent
    for name in relative_path.split("/"):
        if name == "..":
            resolved = resolved.parent
        elif name and name != ".":
            resolved = resolved / name

    return namespace, str(resolved)
