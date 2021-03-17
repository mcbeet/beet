__all__ = [
    "Fragment",
    "InvalidFragment",
]


from base64 import b64decode
from dataclasses import dataclass
from typing import Any, Optional, Sequence, Type, TypeVar, overload
from urllib.request import urlopen

from beet import BinaryFile, BinaryFileBase, Cache, File, FormattedPipelineException
from beet.core.utils import FileSystemPath

FileType = TypeVar("FileType", bound=File[Any, Any])


class InvalidFragment(FormattedPipelineException):
    """Raised when a fragment can not be processed."""

    def __init__(self, message: str, line: int):
        super().__init__(message, line)
        self.message = message + f" (line {line + 1})"


@dataclass(frozen=True)
class Fragment:
    """Class representing a fragment annotated by a directive."""

    start_line: int
    end_line: int
    directive: str
    modifier: Optional[str] = None
    arguments: Sequence[str] = ()
    content: Optional[str] = None
    url: Optional[str] = None
    path: Optional[FileSystemPath] = None
    cache: Optional[Cache] = None

    @overload
    def expect(self):
        ...

    @overload
    def expect(self, name1: str) -> str:
        ...

    @overload
    def expect(self, name1: str, name2: str, *names: str) -> Sequence[str]:
        ...

    def expect(self, *names: str):
        """Check directive arguments."""
        if missing := names[len(self.arguments) :]:
            msg = f"Missing argument {', '.join(map(repr, missing))} for directive @{self.directive}."
            raise InvalidFragment(msg, self.start_line)
        if extra := self.arguments[len(names) :]:
            msg = f"Unexpected argument {', '.join(map(repr, extra))} for directive @{self.directive}."
            raise InvalidFragment(msg, self.start_line)
        if len(self.arguments) == 0:
            return
        if len(self.arguments) == 1:
            return self.arguments[0]
        return self.arguments

    def as_file(self, file_type: Type[FileType] = BinaryFile) -> FileType:
        """Retrieve the content of the fragment as a file."""
        is_binary = issubclass(file_type, BinaryFileBase)
        content = self.content

        if content is not None and self.modifier == "base64":
            content = b64decode(content.strip())

        elif content is not None:
            if self.modifier == "strip_final_newline" and content.endswith("\n"):
                content = content[:-1]

            return file_type(content.encode() if is_binary else content)

        elif self.path:
            return file_type(source_path=self.path)

        elif self.url:
            if self.cache and not self.url.startswith("data:"):
                return file_type(source_path=self.cache.download(self.url))

            with urlopen(self.url) as f:
                content = f.read()

        else:
            msg = f"Expected content, path or url for directive @{self.directive}."
            raise InvalidFragment(msg, self.start_line)

        return file_type(content if is_binary else content.decode(errors="replace"))
