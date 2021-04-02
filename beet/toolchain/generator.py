__all__ = [
    "Generator",
]


from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, DefaultDict, Optional, Tuple, overload

from beet.library.base import NamespaceFile

from .utils import LazyFormat, StableHashable, stable_hash

if TYPE_CHECKING:
    from .context import Context


@dataclass
class Generator:
    """Helper for generating assets and data pack resources."""

    ctx: "Context"
    scope: Tuple[Any, ...] = ()
    registry: DefaultDict[Tuple[Any, ...], int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def __getitem__(self, key: Any) -> "Generator":
        return Generator(
            ctx=self.ctx,
            scope=self.scope + (key,),
            registry=self.registry,
        )

    def get_prefix(self, separator: str = ".") -> str:
        """Join the serializable parts of the scope into a key prefix."""
        prefix = ()
        if prefix_value := self.ctx.meta.get("generate_prefix"):
            prefix = (prefix_value,)

        return "".join(
            part + separator
            for part in prefix + self.scope
            if part and isinstance(part, str)
        )

    def format(self, fmt: str, hash: Optional[StableHashable] = None) -> str:
        """Generate a unique key depending on the given template."""
        key = (self.ctx.project_name, *self.scope, fmt)

        count = self.registry[key]
        self.registry[key] += 1

        env = {
            "namespace": self.ctx.meta.get("generate_namespace", self.ctx.project_name),
            "path": LazyFormat(lambda: self.get_prefix("/")),
            "scope": LazyFormat(lambda: self.get_prefix()),
            "incr": count,
        }

        if hash is not None:
            value = hash
            env["hash"] = LazyFormat(lambda: stable_hash(value))
            env["short_hash"] = LazyFormat(lambda: stable_hash(value, short=True))

        return fmt.format_map(env)

    @overload
    def __call__(
        self,
        template: str,
        file_instance: NamespaceFile,
        *,
        hash: Optional[StableHashable] = None,
    ) -> str:
        ...

    @overload
    def __call__(
        self,
        file_instance: NamespaceFile,
        *,
        hash: Optional[StableHashable] = None,
    ) -> str:
        ...

    def __call__(self, *args: Any, hash: Optional[StableHashable] = None) -> Any:
        if len(args) == 2:
            template, file_instance = args
        else:
            file_instance = args[0]
            template = self.ctx.meta.get(
                "generate_format", "{namespace}:{path}generated_{incr}"
            )

        if hash is None:
            hash = lambda: file_instance.ensure_serialized()

        file_type = type(file_instance)
        key = self[file_type].format(template, hash)

        if file_type in self.ctx.data.namespace_type.field_map:
            self.ctx.data[key] = file_instance
        else:
            self.ctx.assets[key] = file_instance

        return key
