from typing import ClassVar

from beet import Context, TextFile
from mecha import Mecha

from bolt import Runtime


class Patcher(TextFile):
    scope: ClassVar[tuple[str, ...]] = ("patchers",)
    extension: ClassVar[str] = ".bolt"


def define_custom_resources(ctx: Context):
    ctx.data.extend_namespace.append(Patcher)


def process_files(ctx: Context):
    mc = ctx.inject(Mecha)
    for patcher_name, patcher in ctx[Patcher]:
        mc.compile(
            patcher,
            resource_location=patcher_name,
            report=mc.diagnostics,
        )

    if mc.diagnostics.error:
        return

    runtime = ctx.inject(Runtime)
    for patcher_name, patcher in ctx[Patcher]:
        with runtime.modules.error_handler(
            message="Patcher raised an exception.",
            resource_location=patcher_name,
        ):
            impl = runtime.modules[patcher].namespace
            for entries in ctx.query(match=impl["targets"]).values():
                for name, file_instance in entries:
                    result = impl["patch"](name, file_instance.ensure_deserialized())
                    if result is not None:
                        file_instance.set_content(result)

    for pack in [ctx.data, *ctx.data.overlays.values()]:
        pack[Patcher].clear()
