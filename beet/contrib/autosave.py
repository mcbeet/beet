"""Service for saving the data pack and resource pack at the end of the build."""


__all__ = [
    "Autosave",
    "AutosaveOptions",
]


from dataclasses import dataclass, field

from beet import Context, PluginOptions, PluginSpec


class AutosaveOptions(PluginOptions):
    link: bool = False
    output_handlers: list[str] = []
    link_handlers: list[str] = []


@dataclass
class Autosave:
    """Service for saving the data pack and resource pack at the end of the build."""

    ctx: Context
    link: bool = False
    output_handlers: list[PluginSpec] = field(default_factory=list)
    link_handlers: list[PluginSpec] = field(default_factory=list)

    def __post_init__(self):
        opts = self.ctx.validate("autosave", AutosaveOptions)
        self.link = opts.link
        self.output_handlers = list(opts.output_handlers)
        self.link_handlers = list(opts.link_handlers)
        self.ctx.require(self.finalize)

    def add_output(self, *specs: PluginSpec):
        """Register output handler."""
        self.output_handlers.extend(specs)

    def add_link(self, *specs: PluginSpec):
        """Register link handler."""
        self.link_handlers.extend(specs)

    def finalize(self, ctx: Context):
        yield
        ctx.require(*self.output_handlers)
        if self.link:
            ctx.require(*self.link_handlers)
