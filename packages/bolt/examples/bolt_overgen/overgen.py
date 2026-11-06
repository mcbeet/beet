from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, ClassVar

from beet import (
    Context,
    DataPack,
    NamespaceFileScope,
    ResourcePack,
    TextFile,
    TextFileBase,
)
from beet.core.utils import normalize_string

from mecha import CompilationDatabase, CompilationUnit, Mecha

from bolt import Runtime


class Overgen(TextFile):
    scope: ClassVar[NamespaceFileScope] = ("overgen",)
    extension: ClassVar[str] = ".bolt"


def define_custom_resources(ctx: Context):
    ctx.data.extend_namespace.append(Overgen)


def provide_compilation_units(
    pack: ResourcePack | DataPack,
    match: list[str] | None = None,
) -> Iterable[tuple[TextFileBase[Any], CompilationUnit]]:
    for resource_location in pack[Overgen].match(*match or ["*"]):
        file_instance = pack[Overgen][resource_location]

        yield (
            file_instance,
            CompilationUnit(
                resource_location=resource_location,
                pack=pack.overlays[normalize_string(resource_location)],
            ),
        )


def define_compilation_unit_providers(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.providers = [provide_compilation_units]


@dataclass
class DeclareOverlayFormats:
    database: CompilationDatabase

    def __call__(self, min_format: int, max_format: int):
        pack = self.database[self.database.current].pack
        if pack is not None:
            pack.min_format = min_format
            pack.max_format = max_format


def define_module_globals(ctx: Context):
    mc = ctx.inject(Mecha)
    declare_overlay_formats = DeclareOverlayFormats(mc.database)

    runtime = ctx.inject(Runtime)
    runtime.expose("declare_overlay_formats", declare_overlay_formats)


def remove_custom_resources(ctx: Context):
    ctx.data[Overgen].clear()
