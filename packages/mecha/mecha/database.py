__all__ = [
    "CompilationDatabase",
    "CompilationUnit",
    "CompilationUnitProvider",
    "FileTypeCompilationUnitProvider",
]


from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from heapq import heappop, heappush
from typing import (
    Any,
    DefaultDict,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from beet import (
    Container,
    DataPack,
    Generator,
    NamespaceFile,
    ResourcePack,
    TextFile,
    TextFileBase,
)
from beet.core.utils import FileSystemPath, extra_field

from .ast import AstRoot
from .diagnostic import DiagnosticCollection
from .utils import resolve_source_filename


@dataclass
class CompilationUnit:
    """Information associated with the compilation of a specific function file."""

    ast: Optional[AstRoot] = None
    source: Optional[str] = None
    filename: Optional[str] = None
    resource_location: Optional[str] = None
    no_index: bool = False
    pack: Optional[Union[ResourcePack, DataPack]] = None
    priority: int = 0

    diagnostics: DiagnosticCollection = extra_field(init=False)
    perf: Dict[int, float] = extra_field(init=False)

    def __post_init__(self):
        self.diagnostics = DiagnosticCollection(
            filename=self.filename,
            hint=self.resource_location,
        )
        self.perf = {}


class CompilationDatabase(Container[TextFileBase[Any], CompilationUnit]):
    """Compilation database."""

    indices: DefaultDict[
        Optional[Union[ResourcePack, DataPack]], Dict[str, TextFileBase[Any]]
    ]
    session: Set[TextFileBase[Any]]
    queue: List[Tuple[int, int, str, int, TextFileBase[Any]]]
    step: int
    current: TextFileBase[Any]
    count: int

    generate: Optional[Generator]
    directory: Optional[FileSystemPath]

    def __init__(self):
        super().__init__()
        self.indices = defaultdict(dict)
        self.session = set()
        self.queue = []
        self.step = -1
        self.current = TextFile()
        self.count = 0

        self.generate = None
        self.directory = None

    def configure(
        self,
        generate: Optional[Generator] = None,
        directory: Optional[FileSystemPath] = None,
    ):
        self.generate = generate
        self.directory = directory
        self[self.current] = CompilationUnit()

    @property
    def index(self) -> Dict[str, TextFileBase[Any]]:
        return self.indices[self[self.current].pack]

    def process(
        self,
        key: TextFileBase[Any],
        value: CompilationUnit,
    ) -> CompilationUnit:
        if not value.filename:
            value.filename = resolve_source_filename(key, self.directory)
        if not value.diagnostics.filename and value.filename:
            value.diagnostics.filename = value.filename

        value.diagnostics.file = key

        if not value.no_index:
            pack_index = self.indices[value.pack]
            for index in [value.filename, value.resource_location]:
                if index:
                    pack_index[index] = key

        return value

    def __delitem__(self, key: TextFileBase[Any]):
        pack_index = self.indices[self[key].pack]
        for index in [self[key].filename, self[key].resource_location]:
            if index:
                del pack_index[index]
        super().__delitem__(key)

    def setup_compilation(self):
        """Setup database for compilation."""
        self.session.clear()
        self.queue.clear()

    def enqueue(self, key: TextFileBase[Any], step: int = -1, priority: int = 0):
        """Enqueue a file and schedule it to be processed with the given step."""
        self.session.add(key)
        self.count += 1
        heappush(
            self.queue,
            (
                step,
                priority,
                self[key].resource_location or "<unknown>",
                self.count,
                key,
            ),
        )

    def dequeue(self) -> Tuple[int, TextFileBase[Any]]:
        """Dequeue the next file that needs to be processed."""
        step, _, _, _, key = heappop(self.queue)
        return step, key

    def process_queue(self) -> Iterator[Tuple[int, TextFileBase[Any]]]:
        """Yield database entries from the queue."""
        while self.queue:
            self.step, self.current = self.dequeue()
            with self.process_context(self.current):
                yield self.step, self.current

    @contextmanager
    def process_context(self, file_instance: TextFileBase[Any]):
        if self.generate is not None:
            compilation_unit = self[file_instance]
            if compilation_unit.pack is not None:
                with self.generate.overlays[compilation_unit.pack.overlay_name].push():
                    yield
                    return
        yield


class CompilationUnitProvider(Protocol):
    """Provide source files for compilation."""

    def __call__(
        self,
        pack: Union[ResourcePack, DataPack],
        match: Optional[List[str]] = None,
    ) -> Iterable[Tuple[TextFileBase[Any], CompilationUnit]]:
        ...


@dataclass
class FileTypeCompilationUnitProvider:
    """Provide source files based on their type."""

    file_types: Sequence[Type[NamespaceFile]]
    no_index: bool = False

    def __call__(
        self,
        pack: Union[ResourcePack, DataPack],
        match: Optional[List[str]] = None,
    ) -> Iterable[Tuple[TextFileBase[Any], CompilationUnit]]:
        packs = [pack]
        if pack.overlay_parent is None:
            packs.extend(pack.overlays.values())

        for file_type in self.file_types:
            if not issubclass(file_type, TextFileBase):
                continue

            for pack in packs:
                for resource_location in pack[file_type].match(*match or ["*"]):
                    file_instance = pack[file_type][resource_location]

                    yield file_instance, CompilationUnit(
                        resource_location=resource_location,
                        no_index=self.no_index,
                        pack=pack,
                    )
