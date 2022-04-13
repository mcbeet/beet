"""Plugin that inserts comments containing mecha diagnostics."""


__all__ = [
    "annotate_diagnostics",
]


from heapq import heappop, heappush
from typing import Any, Dict, List, Tuple

from beet import Context, TextFileBase

from mecha import CompilationDatabase, DiagnosticCollection, Mecha


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    annotate_diagnostics(mc.database, mc.diagnostics)


def annotate_diagnostics(
    database: CompilationDatabase,
    diagnostics: DiagnosticCollection,
):
    """Insert formatted error messages in the original source as comments."""
    annotations: Dict[TextFileBase[Any], List[Tuple[int, int, List[str]]]] = {}

    for diagnostic in diagnostics.exceptions:
        message = f"{diagnostic.level.upper():<7}{diagnostic.format_message()}\n{diagnostic.format_location()}"

        if diagnostic.file and not diagnostic.location.unknown:
            if source := database[diagnostic.file].source:
                if code := diagnostic.format_code(source):
                    message += f"\n{code}"

            if diagnostic.notes:
                message += f"\n{diagnostic.format_notes()}"

            comments = [f"# {line}" for line in message.splitlines()]
            comments[0] = "#>" + comments[0][2:]
            rendered = annotations.setdefault(diagnostic.file, [])
            line_index = diagnostic.location.lineno - 1

            heappush(rendered, (line_index, len(rendered), comments))

    for function, rendered in annotations.items():
        lines = function.text.splitlines()
        result: List[str] = []

        i = 0
        while rendered:
            j, _, comments = heappop(rendered)
            result += lines[i:j]
            i = j
            result += comments

        result += lines[i:]

        function.text = "\n".join(result) + "\n"
