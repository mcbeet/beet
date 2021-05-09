"""Plugin that adds a directive for interpreting lectern text templates."""


__all__ = [
    "ScriptDirective",
]


from dataclasses import dataclass

from beet import Context, DataPack, ResourcePack, TextFile

from lectern import Document, Fragment


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.directives["script"] = ScriptDirective(ctx)


@dataclass
class ScriptDirective:
    """Directive that renders the fragment and interprets the result as lectern text."""

    ctx: Context

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        fragment.expect()
        file_instance = fragment.as_file(TextFile)

        source = self.ctx.template.render_file(file_instance)

        document = self.ctx.inject(Document)
        document.add_text(source.text)
