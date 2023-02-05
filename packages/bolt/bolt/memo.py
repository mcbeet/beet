__all__ = [
    "MemoHandler",
    "MemoRegistry",
    "MemoFileIndex",
    "MemoStorage",
    "MemoInvocation",
    "MemoState",
]


import logging
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from uuid import UUID

from beet import (
    Cache,
    CachePin,
    Container,
    Context,
    DataPack,
    Generator,
    MultiCache,
    ResourcePack,
)
from beet.core.utils import log_time, remove_path
from mecha import AstChildren, AstRoot, DiagnosticCollection, Mecha, rule
from mecha.contrib.nesting import InplaceNestingPredicate

from .ast import AstMemo, AstMemoResult
from .emit import CommandEmitter
from .utils import dump_pickle, load_pickle

logger = logging.getLogger("memo")


T = TypeVar("T")


@dataclass
class MemoState(Generic[T]):
    load: Callable[[Path], T]
    dump: Callable[[Path, T], Any]
    default: Callable[[], T]

    cached_field_name: str = "cached_{}"

    def __set_name__(self, owner: Type["MemoInvocation"], name: str):
        self.cached_field_name = self.cached_field_name.format(name)

    def __get__(self, obj: "MemoInvocation", objtype: Type["MemoInvocation"]) -> T:
        value = getattr(obj, self.cached_field_name, None)
        if value is None:
            if (
                obj.cached
                and (directory := obj.locate_directory())
                and (path := directory / self.cached_field_name).exists()
            ):
                logger.debug(
                    'Load "%s" for invocation "%s/%s".',
                    self.cached_field_name,
                    obj.parent.memo_id.hex,
                    hex(obj.state_id),
                )
                value = self.load(path)
            else:
                value = self.default()
            setattr(obj, self.cached_field_name, value)
        return value

    def __set__(self, obj: "MemoInvocation", value: T):
        if obj.cached and (directory := obj.locate_directory()):
            logger.debug(
                'Persist "%s" for invocation "%s/%s".',
                self.cached_field_name,
                obj.parent.memo_id.hex,
                hex(obj.state_id),
            )
            directory.mkdir(parents=True, exist_ok=True)
            self.dump(directory / self.cached_field_name, value)
        setattr(obj, self.cached_field_name, value)


class MemoInvocation:
    parent: "MemoStorage"
    state_id: int
    cached: bool
    epoch: int

    def __init__(self, parent: "MemoStorage", state_id: int):
        self.parent = parent
        self.state_id = state_id
        self.cached = False
        self.epoch = 0

    output: ClassVar[MemoState[str]] = MemoState(
        load=Path.read_text,
        dump=Path.write_text,
        default=str,
    )

    resource_pack: ClassVar[MemoState[ResourcePack]] = MemoState(
        load=lambda p: ResourcePack(path=p),
        dump=lambda p, pack: pack.save(path=p),
        default=ResourcePack,
    )

    data_pack: ClassVar[MemoState[DataPack]] = MemoState(
        load=lambda p: DataPack(path=p),
        dump=lambda p, pack: pack.save(path=p),
        default=DataPack,
    )

    bindings: ClassVar[MemoState[Tuple[Any, ...]]] = MemoState(
        load=load_pickle,
        dump=dump_pickle,
        default=tuple,
    )

    def __getstate__(self) -> Tuple["MemoStorage", int, bool, int]:
        return self.parent, self.state_id, self.cached, self.epoch

    def __setstate__(self, state: Tuple["MemoStorage", int, bool, int]):
        self.parent, self.state_id, self.cached, self.epoch = state

    def locate_directory(self) -> Optional[Path]:
        if path := self.parent.locate_directory():
            return path / hex(self.state_id)
        return None


class MemoStorage(Container[Tuple[Any, ...], MemoInvocation]):
    parent: "MemoFileIndex"
    memo_id: UUID
    memo_lineno: int
    invocation_counter: int

    def __init__(self, parent: "MemoFileIndex", memo_id: UUID, lineno: int = -1):
        super().__init__()
        self.parent = parent
        self.memo_id = memo_id
        self.memo_lineno = lineno
        self.invocation_counter = 0

    def __delitem__(self, key: Tuple[Any, ...]):
        if directory := self[key].locate_directory():
            remove_path(directory)
        super().__delitem__(key)

    def missing(self, key: Tuple[Any, ...]) -> MemoInvocation:
        self.invocation_counter += 1
        return MemoInvocation(parent=self, state_id=self.invocation_counter)

    def locate_directory(self) -> Optional[Path]:
        if path := self.parent.path:
            return path.with_name(self.memo_id.hex)
        return None


class MemoFileIndex(Container[Union[Tuple[AstMemo, int], UUID], MemoStorage]):
    filename: str
    path: Optional[Path]

    def __init__(self, filename: str, path: Optional[Path] = None):
        super().__init__()
        self.filename = filename
        self.path = path

    def __getitem__(self, key: Union[Tuple[AstMemo, int], UUID]) -> MemoStorage:
        if isinstance(key, UUID):
            return super().__getitem__(key)

        memo = key[0]

        storage = self.get(memo.persistent_id)
        if storage is None:
            storage = super().__getitem__(key)
            storage.memo_lineno = memo.location.lineno
            self[memo.persistent_id] = storage

        return storage

    def __delitem__(self, key: Union[Tuple[AstMemo, int], UUID]):
        if isinstance(key, UUID):
            super().__delitem__(key)
            return
        if directory := self[key].locate_directory():
            remove_path(directory)
        del self[key[0].persistent_id]
        super().__delitem__(key)

    def missing(self, key: Union[Tuple[AstMemo, int], UUID]) -> MemoStorage:
        if isinstance(key, UUID):
            return super().missing(key)
        return MemoStorage(self, key[0].persistent_id)

    def clear(self):
        super().clear()
        if self.path:
            remove_path(self.path)

    def garbage_collect(self, gc_cutoff: int) -> Iterator[Tuple[UUID, int]]:
        keep_alive: Set[UUID] = set()

        for storage_key, storage in self.items():
            if isinstance(storage_key, UUID):
                for variables, invocation in list(storage.items()):
                    if not invocation.cached or invocation.epoch < gc_cutoff:
                        yield storage.memo_id, invocation.state_id
                        del storage[variables]
                if storage:
                    keep_alive.add(storage_key)

        for storage_key in list(self):
            if (
                isinstance(storage_key, tuple)
                and storage_key[0].persistent_id not in keep_alive
            ):
                del self[storage_key]

        for storage_key in list(self):
            if isinstance(storage_key, UUID) and storage_key not in keep_alive:
                del self[storage_key]


class MemoRegistry(Container[str, MemoFileIndex]):
    cache: Optional[Cache]

    epoch_counter: ClassVar[CachePin[int]] = CachePin("epoch_counter", 0)
    gc_epoch: ClassVar[CachePin[int]] = CachePin("gc_epoch", 0)
    gc_interval: ClassVar[CachePin[int]] = CachePin("gc_interval", 50)
    gc_max_age: ClassVar[CachePin[int]] = CachePin("gc_max_age", 30)

    def __init__(self, arg: Union[Context, MultiCache[Any], Optional[Cache]] = None):
        super().__init__()
        arg = arg.cache if isinstance(arg, Context) else arg
        self.cache = arg["memo"] if isinstance(arg, MultiCache) else arg

    def __setitem__(self, key: str, value: MemoFileIndex):
        super().__setitem__(key, value)
        if self.cache:
            self.cache.json.setdefault("files", {})[key] = str(value.path)

    def __delitem__(self, key: str):
        self[key].clear()
        if self.cache:
            del self.cache.json.setdefault("files", {})[key]
        super().__delitem__(key)

    def __iter__(self) -> Iterator[str]:
        if self.cache:
            for key in self.cache.json.setdefault("files", {}):
                yield key

    def missing(self, key: str) -> MemoFileIndex:
        if not self.cache:
            return MemoFileIndex(key)

        index_path = self.cache.get_path(f"{key}-memo")
        if index_path.is_file():
            if isinstance(memo_file_index := load_pickle(index_path), MemoFileIndex):
                memo_file_index.path = index_path
                return memo_file_index

        return MemoFileIndex(key, index_path)

    def flush(self):
        for memo_file_index in self.values():
            if memo_file_index.path:
                dump_pickle(memo_file_index.path, memo_file_index)

    @property
    def gc_cutoff(self) -> int:
        return self.epoch_counter - self.gc_max_age

    def garbage_collect(self, *keys: str) -> Iterator[Tuple[UUID, int]]:
        for key in keys:
            file_index = self[key]
            yield from file_index.garbage_collect(self.gc_cutoff)
            if not file_index:
                del self[key]
        self.gc_epoch = self.epoch_counter


@dataclass
class MemoHandler:
    mc: Mecha
    registry: MemoRegistry
    generate: Optional[Generator] = None
    inplace_nesting_predicate: Optional[InplaceNestingPredicate] = None

    def __post_init__(self):
        self.mc.serialize.extend(serialize_memo_result)

    def restore(self, emit: CommandEmitter, invocation: MemoInvocation):
        if not self.generate or not self.inplace_nesting_predicate:
            return

        invocation.epoch = self.registry.epoch_counter

        if output := invocation.output:
            emit.commands.append(AstMemoResult(serialized=output))

        self.generate.assets.merge(invocation.resource_pack)
        self.generate.data.merge(invocation.data_pack)

    @contextmanager
    def record(
        self,
        emit: CommandEmitter,
        invocation: MemoInvocation,
        name: Optional[str] = None,
    ):
        if not self.generate or not self.inplace_nesting_predicate or not name:
            yield
            return

        database = self.mc.database
        source = database.index[name]
        compilation_unit = database[source]

        with self.generate.draft() as draft, draft.push():
            with emit.scope() as commands:
                yield

            root = AstRoot(commands=AstChildren(commands))

            diagnostics = DiagnosticCollection()

            previous_session = database.session
            previous_queue = database.queue
            previous_step = database.step
            previous_current = database.current
            previous_callback = self.inplace_nesting_predicate.callback
            try:
                database.session = set()
                database.queue = []
                self.inplace_nesting_predicate.callback = (
                    lambda target: previous_callback(target)
                    or target is previous_current
                )
                function = self.mc.compile(
                    root,
                    report=diagnostics,
                    initial_step=database.step + 1,
                )
            finally:
                previous_session.update(database.session)
                database.session = previous_session
                database.queue = previous_queue
                database.step = previous_step
                database.current = previous_current
                self.inplace_nesting_predicate.callback = previous_callback

            if output := function.text.rstrip():
                emit.commands.append(AstMemoResult(serialized=output))

            database[function].source = compilation_unit.source

            if not diagnostics.exceptions:
                invocation.epoch = self.registry.epoch_counter
                invocation.cached = True

                if output:
                    invocation.output = output
                if draft.assets:
                    invocation.resource_pack = draft.assets
                if draft.data:
                    invocation.data_pack = draft.data

    def finalize(self):
        self.registry.epoch_counter += 1
        next_gc = self.registry.gc_epoch + self.registry.gc_interval
        if self.registry.epoch_counter >= next_gc:
            with log_time("GC bolt memo."):
                for memo_id, state_id in self.registry.garbage_collect(*self.registry):
                    logger.debug('GC "%s/%s".', memo_id.hex, hex(state_id))
        self.registry.flush()


@rule(AstMemoResult)
def serialize_memo_result(node: AstMemoResult, result: List[str]):
    result.append(node.serialized)
