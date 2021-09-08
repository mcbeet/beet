"""Plugin that adds a directive for running plugin code in a document."""


__all__ = [
    "PluginDirective",
]


from dataclasses import dataclass
from textwrap import indent

from beet import Context, DataPack, ResourcePack, TextFile
from beet.core.utils import JsonDict

from lectern import Document, Fragment


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.directives["plugin"] = PluginDirective(ctx)


@dataclass
class PluginDirective:
    """Directive that evaluates the fragment as a beet plugin."""

    ctx: Context

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        file_instance = fragment.as_file(TextFile)
        body = indent(file_instance.text.strip() or "pass", "    ")
        globals_dict: JsonDict = {}
        exec("def beet_default(ctx):\n" + body, globals_dict)
        self.ctx.require(globals_dict["beet_default"])
