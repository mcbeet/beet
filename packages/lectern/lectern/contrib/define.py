"""Plugin that adds a directive for rendering a fragment and storing the output."""


__all__ = [
    "DefineDirective",
]


from dataclasses import dataclass

from beet import Context, DataPack, ResourcePack, TextFile

from lectern import Document, Fragment


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.directives["define"] = DefineDirective(ctx)


@dataclass
class DefineDirective:
    """Directive that renders the fragment and stores the resulting string as a template global."""

    ctx: Context

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        variable = fragment.expect("variable")
        file_instance = fragment.as_file(TextFile)

        result = self.ctx.template.render_file(file_instance)
        self.ctx.template.globals[variable] = result.text
