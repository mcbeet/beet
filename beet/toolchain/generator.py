__all__ = [
    "Generator",
    "Draft",
    "DraftCacheSignal",
]


import json
from collections import defaultdict
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field, replace
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    DefaultDict,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from beet.core.file import TextFileBase
from beet.core.utils import TextComponent, log_time, required_field
from beet.library.base import NamespaceFile
from beet.library.data_pack import DataPack, Function
from beet.library.resource_pack import ResourcePack

from .tree import TreeNode, generate_tree
from .utils import LazyFormat, stable_hash

if TYPE_CHECKING:
    from .context import Context


T = TypeVar("T", contravariant=True)
GeneratorType = TypeVar("GeneratorType", bound="Generator")
NamespaceFileType = TypeVar("NamespaceFileType", bound="NamespaceFile")


@dataclass
class Generator:
    """Helper for generating assets and data pack resources."""

    ctx: "Context"
    scope: Tuple[Any, ...] = ()
    registry: DefaultDict[Tuple[Any, ...], int] = field(
        default_factory=lambda: defaultdict(int)  # type: ignore
    )

    assets: ResourcePack = field(default_factory=ResourcePack)
    data: DataPack = field(default_factory=DataPack)

    def __getitem__(self: GeneratorType, key: Any) -> GeneratorType:
        return replace(self, scope=self.scope + (key,))

    @contextmanager
    def push(self) -> Iterator[None]:
        """Temporarily push the current state into the root context generator."""
        root = self.ctx.generate

        previous_scope = root.scope
        previous_assets = root.assets
        previous_data = root.data

        root.scope = self.scope
        root.assets = self.assets
        root.data = self.data

        try:
            yield
        finally:
            root.scope = previous_scope
            root.assets = previous_assets
            root.data = previous_data

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
        key = (self.ctx.project_id, *self.scope, *key)
        count = self.registry[key]
        self.registry[key] += 1
        return count

    def format(self, fmt: str, hash: Any = None) -> str:
        """Generate a unique key depending on the given template."""
        env = {
            "namespace": self.ctx.meta.get("generate_namespace", self.ctx.project_id),
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
        hash: Any = None,
    ) -> str:
        ...

    @overload
    def __call__(
        self,
        fmt: str,
        *,
        render: TextFileBase[Any],
        hash: Any = None,
        **kwargs: Any,
    ) -> str:
        ...

    @overload
    def __call__(
        self,
        fmt: str,
        *,
        merge: NamespaceFile,
        hash: Any = None,
    ) -> str:
        ...

    @overload
    def __call__(
        self,
        fmt: str,
        *,
        default: Union[Type[NamespaceFileType], NamespaceFileType],
        hash: Any = None,
    ) -> NamespaceFileType:
        ...

    @overload
    def __call__(
        self,
        file_instance: NamespaceFile,
        *,
        hash: Any = None,
    ) -> str:
        ...

    @overload
    def __call__(
        self,
        *,
        render: TextFileBase[Any],
        hash: Any = None,
        **kwargs: Any,
    ) -> str:
        ...

    def __call__(
        self,
        *args: Any,
        render: Optional[TextFileBase[Any]] = None,
        merge: Optional[NamespaceFile] = None,
        default: Optional[Union[Type[NamespaceFile], NamespaceFile]] = None,
        hash: Any = None,
        **kwargs: Any,
    ) -> Any:
        default_file = None

        if default:
            if isinstance(default, type):
                file_type = default
            else:
                file_type = type(default)
                default_file = default

            file_instance = None
            fmt = args[0]

        else:
            if render:
                file_instance = cast(NamespaceFile, render)
                fmt = args[0] if args else None
            elif merge:
                file_instance = merge
                fmt = args[0]
            elif len(args) == 2:
                fmt, file_instance = args
            else:
                file_instance = args[0]
                fmt = None

            if hash is None and not render:
                hash = lambda: file_instance.ensure_serialized()

            file_type = type(file_instance)

        pack = (
            self.data
            if file_type in self.data.namespace_type.field_map
            else self.assets
        )

        if not fmt:
            key = self[file_type].path(hash=hash)
        elif ":" in fmt:
            key = self[file_type].format(fmt, hash)
        else:
            key = self[file_type].path(fmt, hash)

        if file_instance:
            if merge:
                pack[file_type].merge({key: file_instance})
            else:
                pack[key] = file_instance
        elif default:
            return pack[file_type].setdefault(key, default_file)

        if render:
            with self.ctx.override(
                render_path=key,
                render_group=pack.namespace_type.field_map[file_type],
            ):
                self.ctx.template.render_file(render, **kwargs)

        return key

    def path(self, fmt: str = "generated_{incr}", hash: Any = None) -> str:
        """Generate a scoped resource path."""
        template = self.ctx.meta.get("generate_path", "{namespace}:{path}")
        return self.format(template + fmt, hash)

    def id(self, fmt: str = "{incr}", hash: Any = None) -> str:
        """Generate a scoped id."""
        template = self.ctx.meta.get("generate_id", "{namespace}.{scope}")
        return self.format(template + fmt, hash)

    def hash(
        self,
        fmt: str,
        hash: Any = None,
        short: bool = False,
    ) -> str:
        """Generate a scoped hash."""
        template = self.ctx.meta.get("generate_hash", "{namespace}.{scope}")
        return stable_hash(self.format(template + fmt, hash), short)

    def objective(
        self,
        fmt: str = "{incr}",
        hash: Any = None,
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

    @overload
    def function_tree(
        self,
        fmt: str,
        items: Iterable[T],
        /,
        *,
        key: Optional[Callable[[T], int]] = None,
        hash: Any = None,
        name: Optional[str] = None,
    ) -> Iterator[Tuple[TreeNode[T], Function]]:
        ...

    @overload
    def function_tree(
        self,
        items: Iterable[T],
        /,
        *,
        key: Optional[Callable[[T], int]] = None,
        hash: Any = None,
        name: Optional[str] = None,
    ) -> Iterator[Tuple[TreeNode[T], Function]]:
        ...

    def function_tree(
        self,
        *args: Any,
        key: Optional[Callable[[Any], int]] = None,
        hash: Any = None,
        name: Optional[str] = None,
    ) -> Iterator[Tuple[TreeNode[Any], Function]]:
        """Generate a function tree."""
        if len(args) == 2:
            fmt, items = args
        else:
            items = args[0]
            fmt = None

        if hash is None:
            hash = lambda: str(items)

        root = self[Function].path(fmt, hash) if fmt else self[Function].path(hash=hash)

        for node in generate_tree(root, items, key, name):
            yield node, self.data.functions.setdefault(node.parent, Function())

    @contextmanager
    def draft(self) -> Iterator["Draft"]:
        """Work on an intermediate draft."""
        assets = ResourcePack().configure(self.assets)
        data = DataPack().configure(self.data)

        with ExitStack() as exit_stack:
            draft = Draft(
                ctx=self.ctx,
                scope=self.scope,
                registry=self.registry,
                assets=assets,
                data=data,
                exit_stack=exit_stack,
            )

            try:
                yield draft
            except DraftCacheSignal:
                pass

        self.assets.merge(assets)
        self.data.merge(data)


class DraftCacheSignal(Exception):
    """Raised when the draft is cached."""


@dataclass
class Draft(Generator):
    """Generator that works on an intermediate resource pack and data pack."""

    exit_stack: ExitStack = required_field()

    def cache(
        self,
        name: str,
        key: str,
        zipped: bool = False,
    ):
        """Skip the rest of the code if the draft is cached."""
        cache = self.ctx.cache[f"draft_{name}"]

        suffix = ".zip" if zipped else ""
        cached_resource_pack = cache.directory / f"draft_resource_pack{suffix}"
        cached_data_pack = cache.directory / f"draft_data_pack{suffix}"

        key = f"{key} {zipped=}"

        if cache.json.get("draft_key") == key:
            with log_time('Load draft "%s" from cache.', name):
                self.assets.load(cached_resource_pack)
                self.data.load(cached_data_pack)
            raise DraftCacheSignal()

        @self.exit_stack.callback
        @log_time('Update cache for draft "%s".', name)
        def _():
            if self.assets:
                self.assets.save(path=cached_resource_pack, overwrite=True)
            if self.data:
                self.data.save(path=cached_data_pack, overwrite=True)
            cache.json["draft_key"] = key

        self.exit_stack.enter_context(log_time('Generate draft "%s".', name))
