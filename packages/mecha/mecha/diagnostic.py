__all__ = [
    "Diagnostic",
    "DiagnosticCollection",
    "DiagnosticError",
    "DiagnosticErrorSummary",
]


from dataclasses import dataclass, field, replace
from textwrap import indent
from types import TracebackType
from typing import Any, Iterator, List, Literal, Optional, Type

from beet import BubbleException, TextFileBase
from tokenstream import UNKNOWN_LOCATION, SourceLocation

from .error import MechaError
from .utils import underline_code


@dataclass
class Diagnostic(MechaError):
    """Exception that can be raised to report messages."""

    level: Literal["info", "warn", "error"]
    message: str
    notes: List[str] = field(default_factory=list)

    rule: Optional[str] = None
    hint: Optional[str] = None
    filename: Optional[str] = None
    file: Optional[TextFileBase[Any]] = None
    location: SourceLocation = UNKNOWN_LOCATION
    end_location: SourceLocation = UNKNOWN_LOCATION

    def __str__(self) -> str:
        return self.format_message()

    def format_message(self) -> str:
        """Return the formatted message."""
        message = self.message
        if self.rule:
            message += f" ({self.rule})"
        return message

    def format_notes(self) -> str:
        """Return the formatted notes."""
        return "Notes:\n" + "\n".join(
            "  - " + indent(note, "    ")[4:] for note in self.notes
        )

    def format_location(self) -> str:
        """Return the formatted location of the reported message."""
        if self.filename:
            location = self.filename
            if not self.location.unknown:
                location += f":{self.location.lineno}:{self.location.colno}"
        elif not self.location.unknown:
            location = f"line {self.location.lineno}, column {self.location.colno}"
            if self.hint:
                location = f'File "{self.hint}", {location}'
        elif self.hint:
            location = self.hint
        else:
            location = ""
        return location

    def format_code(self, code: str) -> Optional[str]:
        """Return the formatted code."""
        if self.location.unknown:
            return None
        return underline_code(
            code,
            self.location,
            self.location if self.end_location.unknown else self.end_location,
        )

    def with_defaults(
        self,
        rule: Optional[str] = None,
        hint: Optional[str] = None,
        filename: Optional[str] = None,
        file: Optional[TextFileBase[Any]] = None,
        location: SourceLocation = UNKNOWN_LOCATION,
        end_location: SourceLocation = UNKNOWN_LOCATION,
    ) -> "Diagnostic":
        """Set default values for unspecified attributes."""
        if not self.location.unknown:
            location = self.location
            end_location = self.end_location
        return replace(
            self,
            rule=self.rule or rule,
            hint=self.hint or hint,
            filename=self.filename or filename,
            file=self.file or file,
            location=location,
            end_location=end_location,
        )


@dataclass
class DiagnosticCollection(MechaError):
    """Exception that can be raised to group multiple diagnostics."""

    exceptions: List[Diagnostic] = field(default_factory=list)

    rule: Optional[str] = None
    hint: Optional[str] = None
    filename: Optional[str] = None
    file: Optional[TextFileBase[Any]] = None

    def add(self, exc: Diagnostic) -> Diagnostic:
        """Add diagnostic."""
        exc = exc.with_defaults(
            rule=self.rule,
            hint=self.hint,
            filename=self.filename,
            file=self.file,
        )
        self.exceptions.append(exc)
        return exc

    def extend(self, other: "DiagnosticCollection"):
        """Combine diagnostics from another collection."""
        self.exceptions.extend(other.exceptions)

    def clear(self):
        """Clear all the diagnostics."""
        self.exceptions.clear()

    @property
    def error(self) -> bool:
        """Return true if the diagnostics contain at least one error."""
        for exc in self.exceptions:
            if exc.level == "error":
                return True
        return False

    def get_all_errors(self) -> Iterator[Diagnostic]:
        """Yield all the diagnostics with a severity level of "error"."""
        for exc in self.exceptions:
            if exc.level == "error":
                yield exc

    def __enter__(self) -> "DiagnosticCollection":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        if not exc_type:
            if self.exceptions:
                raise self

    def __str__(self) -> str:
        term = (
            "error"
            if all(exc.level == "error" for exc in self.exceptions)
            else "diagnostic"
        )
        term += "s" * (len(self.exceptions) > 1)
        return f"Reported {len(self.exceptions)} {term}."


class DiagnosticError(MechaError):
    """Raised with a collection of error diagnostics."""

    diagnostics: DiagnosticCollection

    def __init__(self, diagnostics: DiagnosticCollection):
        super().__init__(diagnostics)
        self.diagnostics = diagnostics

    def __str__(self) -> str:
        details = "\n".join(
            f"{diagnostic.format_location()}: {diagnostic.format_message()}"
            for diagnostic in self.diagnostics.exceptions
        )
        return f"{self.diagnostics}\n\n{details}"


class DiagnosticErrorSummary(BubbleException):
    """Raised for showing a summary of how many errors occurred."""

    diagnostics: DiagnosticCollection

    def __init__(self, diagnostics: DiagnosticCollection):
        super().__init__(diagnostics)
        self.diagnostics = diagnostics

    def __str__(self) -> str:
        return str(self.diagnostics)
