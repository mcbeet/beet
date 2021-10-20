__all__ = [
    "beet_default",
]


import logging

from beet import Context

from .api import Mecha
from .diagnostic import DiagnosticCollection, DiagnosticErrorSummary

logger = logging.getLogger("mecha")


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)

    mc.compile(ctx.data, report=mc.diagnostics)

    yield

    for diagnostic in mc.diagnostics.exceptions:
        message = diagnostic.format_message()

        if diagnostic.file:
            if source := mc.database[diagnostic.file].source:
                if code := diagnostic.format_code(source):
                    message += f"\n{code}"

        extra = {"annotate": diagnostic.format_location()}

        if diagnostic.level == "error":
            logger.error("%s", message, extra=extra)
        elif diagnostic.level == "warn":
            logger.warn("%s", message, extra=extra)
        elif diagnostic.level == "info":
            logger.info("%s", message, extra=extra)

    if errors := list(mc.diagnostics.get_all_errors()):
        raise DiagnosticErrorSummary(DiagnosticCollection(errors))
