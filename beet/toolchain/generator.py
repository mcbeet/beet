__all__ = [
    "Generator",
]


import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, DefaultDict, Optional, Tuple, TypeVar, overload

from beet.core.utils import TextComponent
from beet.library.base import NamespaceFile

from .utils import LazyFormat, StableHashable, stable_hash

if TYPE_CHECKING:
    from .context import Context


GeneratorType = TypeVar("GeneratorType", bound="Generator")


@dataclass
class Generator:
    """Helper for generating assets and data pack resources."""

    ctx: "Context"
    scope: Tuple[Any, ...] = ()
    registry: DefaultDict[Tuple[Any, ...], int] = field(
        default_factory=lambda: defaultdict(int)  # type: ignore
    )

    def __getitem__(self: GeneratorType, key: Any) -> GeneratorType:
        return self.__class__(
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

    def get_increment(self, *key: Any) -> int:
        """Return the current value for the given key and increment it."""
        key = (self.ctx.project_name, *self.scope, *key)
        count = self.registry[key]
        self.registry[key] += 1
        return count

    def format(self, fmt: str, hash: Optional[StableHashable] = None) -> str:
        """Generate a unique key depending on the given template."""
        env = {
            "namespace": self.ctx.meta.get("generate_namespace", self.ctx.project_name),
            "path": LazyFormat(lambda: self.get_prefix("/")),
            "scope": LazyFormat(lambda: self.get_prefix()),
            "incr": LazyFormat(lambda: self.get_increment(fmt)),
        }

        if hash is not None:
            value = hash
            env["hash"] = LazyFormat(lambda: stable_hash(value))
            env["short_hash"] = LazyFormat(lambda: stable_hash(value, short=True))

        return fmt.format_map(env)

    @overload
    def __call__(
        self,
        fmt: str,
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
            fmt, file_instance = args
        else:
            file_instance = args[0]
            fmt = "generated_{incr}"

        if hash is None:
            hash = lambda: file_instance.ensure_serialized()

        template = self.ctx.meta.get("generate_file", "{namespace}:{path}")
        file_type = type(file_instance)
        key = self[file_type].format(template + fmt, hash)

        if file_type in self.ctx.data.namespace_type.field_map:
            self.ctx.data[key] = file_instance
        else:
            self.ctx.assets[key] = file_instance

        return key

    def id(self, fmt: str = "{incr}", hash: Optional[StableHashable] = None) -> str:
        """Generate a scoped id."""
        template = self.ctx.meta.get("generate_id", "{namespace}.{scope}")
        return self.format(template + fmt, hash)

    def hash(
        self,
        fmt: str,
        hash: Optional[StableHashable] = None,
        short: bool = False,
    ) -> str:
        """Generate a scoped hash."""
        template = self.ctx.meta.get("generate_hash", "{namespace}.{scope}")
        return stable_hash(self.format(template + fmt, hash), short)

    def objective(
        self,
        fmt: str = "{incr}",
        hash: Optional[StableHashable] = None,
        criterion: str = "dummy",
        display: Optional[TextComponent] = None,
    ) -> str:
        """Generate a scoreboard objective."""
        template = self.ctx.meta.get("generate_objective", "{namespace}.{scope}")
        key = self.format(template + fmt, hash)
        objective = stable_hash(key)
        display = json.dumps(display or key)

        scoreboard = self.ctx.meta.setdefault("generate_scoreboard", {})
        scoreboard[objective] = f"{criterion} {display}"

        return objective
