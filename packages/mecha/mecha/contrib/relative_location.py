"""Plugin that resolves relative resource locations."""


__all__ = [
    "RelativeResourceLocationNormalizer",
]


from dataclasses import dataclass, replace
from pathlib import PurePosixPath

from beet import Context
from beet.core.utils import required_field

from mecha import (
    AstResourceLocation,
    CompilationDatabase,
    Diagnostic,
    Mecha,
    MutatingReducer,
    rule,
)


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.normalize.extend(RelativeResourceLocationNormalizer(database=mc.database))


@dataclass
class RelativeResourceLocationNormalizer(MutatingReducer):
    """Normalizer that resolves relative resource locations."""

    database: CompilationDatabase = required_field()

    @rule(AstResourceLocation)
    def relative_resource_location(self, node: AstResourceLocation):
        if node.namespace is None and node.path.startswith(("./", "../")):
            current_file = self.database.current
            path = self.database[current_file].resource_location

            if not path:
                raise Diagnostic("error", "Can't resolve relative resource location.")

            namespace, _, current_path = path.partition(":")

            resolved = PurePosixPath(current_path).parent
            for name in node.path.split("/"):
                if name == "..":
                    resolved = resolved.parent
                elif name and name != ".":
                    resolved = resolved / name

            return replace(node, namespace=namespace, path=str(resolved))

        return node
