__all__ = [
    "beet_default",
]


import logging

from beet import Context

from .api import Mecha
from .diagnostic import DiagnosticCollection, DiagnosticError

logger = logging.getLogger("mecha")


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)

    mc.compile(ctx.data, report=mc.diagnostics)

    yield

    for diagnostic in mc.diagnostics.exceptions:
        message = diagnostic.format_message()
        args = {"annotate": diagnostic.format_location()}

        if diagnostic.level == "error":
            logger.error(message, args)
        elif diagnostic.level == "warn":
            logger.warn(message, args)
        elif diagnostic.level == "info":
            logger.info(message, args)

    if errors := list(mc.diagnostics.get_all_errors()):
        raise DiagnosticError(DiagnosticCollection(errors), show_details=False)
