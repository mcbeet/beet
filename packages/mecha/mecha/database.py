__all__ = [
    "CompilationDatabase",
    "CompilationUnit",
]


from dataclasses import dataclass
from typing import Any, Dict, Optional

from beet import Container, TextFileBase
from beet.core.utils import extra_field

from .ast import AstRoot
from .diagnostic import DiagnosticCollection


@dataclass
class CompilationUnit:
    """Information associated with the compilation of a specific function file."""

    ast: Optional[AstRoot] = None
    source: Optional[str] = None
    filename: Optional[str] = None
    resource_location: Optional[str] = None

    diagnostics: DiagnosticCollection = extra_field(init=False)

    def __post_init__(self):
        self.diagnostics = DiagnosticCollection(
            filename=self.filename,
            hint=self.resource_location,
        )


class CompilationDatabase(Container[TextFileBase[Any], CompilationUnit]):
    """Compilation database."""

    index: Dict[str, TextFileBase[Any]]

    def __init__(self):
        super().__init__()
        self.index = {}

    def process(
        self,
        key: TextFileBase[Any],
        value: CompilationUnit,
    ) -> CompilationUnit:
        for index in [value.filename, value.resource_location]:
            if index:
                self.index[index] = key
        return value

    def __delitem__(self, key: TextFileBase[Any]):
        for index in [self[key].filename, self[key].resource_location]:
            if index:
                del self.index[index]
        super().__delitem__(key)
