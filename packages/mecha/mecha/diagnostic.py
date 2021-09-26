__all__ = [
    "Diagnostic",
    "DiagnosticCollection",
    "DiagnosticLabelContainer",
    "DiagnosticError",
]


from dataclasses import dataclass, field, replace
from types import TracebackType
from typing import Any, Iterator, List, Literal, Optional, Type

from beet import Container, FormattedPipelineException
from tokenstream import UNKNOWN_LOCATION, SourceLocation


class DiagnosticLabelContainer(Container[Any, str]):
    """Container for diagnostic labels."""

    def normalize_key(self, key: Any) -> Any:
        if isinstance(key, SourceLocation):
            return key, key

        location = getattr(key, "location", None)
        end_location = getattr(key, "end_location", None)

        if location and end_location:
            return location, end_location

        return key


@dataclass
class Diagnostic(Exception):
    """Exception that can be raised to report messages."""

    level: Literal["info", "warn", "error"]
    message: str

    rule: Optional[str] = None
    hint: Optional[str] = None
    filename: Optional[str] = None
    location: SourceLocation = UNKNOWN_LOCATION
    end_location: SourceLocation = UNKNOWN_LOCATION
    labels: DiagnosticLabelContainer = field(default_factory=DiagnosticLabelContainer)

    def __str__(self) -> str:
        return self.format_message()

    def format_message(self) -> str:
        """Return the formatted message."""
        message = self.message
        if self.rule:
            message += f" ({self.rule})"
        return message

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

    def with_defaults(
        self,
        rule: Optional[str] = None,
        hint: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> "Diagnostic":
        """Set default values for unspecified attributes."""
        return replace(
            self,
            rule=self.rule or rule,
            hint=self.hint or hint,
            filename=self.filename or filename,
        )


@dataclass
class DiagnosticCollection(Exception):
    """Exception that can be raised to group multiple diagnostics."""

    exceptions: List[Diagnostic] = field(default_factory=list)

    rule: Optional[str] = None
    hint: Optional[str] = None
    filename: Optional[str] = None

    def add(self, exc: Diagnostic) -> Diagnostic:
        """Add diagnostic."""
        exc = exc.with_defaults(rule=self.rule, hint=self.hint, filename=self.filename)
        self.exceptions.append(exc)
        return exc

    def extend(self, other: "DiagnosticCollection"):
        """Combine diagnostics from another collection."""
        self.exceptions.extend(other.exceptions)

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


class DiagnosticError(FormattedPipelineException):
    """Wrap a collection of error diagnostics to abort the build."""

    diagnostics: DiagnosticCollection

    def __init__(self, diagnostics: DiagnosticCollection, show_details: bool = True):
        super().__init__(diagnostics)
        self.diagnostics = diagnostics

        if show_details:
            details = "\n".join(
                f"{diagnostic.format_location()}: {diagnostic.format_message()}"
                for diagnostic in diagnostics.exceptions
            )
            self.message = f"{diagnostics}\n\n{details}"
        else:
            self.message = str(diagnostics)

        self.format_cause = True
