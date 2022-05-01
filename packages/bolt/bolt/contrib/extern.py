"""Plugin for handling bolt modules outside data packs."""


__all__ = [
    "ExternOptions",
    "extern",
]


from typing import Dict, Optional, Union

from beet import Context, ListOption, configurable
from pydantic import BaseModel


class ExternOptions(BaseModel):
    namespace: Optional[str] = None
    modules: Union[ListOption[str], Dict[str, ListOption[str]]] = {}


def beet_default(ctx: Context):
    ctx.require(extern)


@configurable(validator=ExternOptions)
def extern(ctx: Context, opts: ExternOptions):
    """Plugin for handling bolt modules outside data packs."""
