"""Plugin for performing basic substitutions."""


__all__ = [
    "find_replace",
    "FindReplaceHandler",
    "FindReplaceOptions",
    "SubstitutionOption",
    "TextSubstitutionOption",
    "RenderSubstitutionOption",
]


from dataclasses import dataclass
from typing import Any, Callable, Generic, Sequence, Tuple, TypeVar, Union

from pydantic import BaseModel

from beet import (
    Context,
    DataPack,
    ListOption,
    Pack,
    PackSelectOption,
    PackSelector,
    PluginOptions,
    PreparedPackSelector,
    RegexOption,
    ResourcePack,
    TemplateManager,
    TextFileBase,
    configurable,
)

PackType = TypeVar("PackType", bound=Pack[Any])


class TextSubstitutionOption(BaseModel):
    find: RegexOption
    replace: str

    class Config:
        extra = "forbid"

    def compile(self, template: TemplateManager) -> Callable[[str], str]:
        regex = RegexOption.compile(self.find.resolve(template))
        if not regex:
            return lambda value: value
        replacement = template.render_string(self.replace)
        return lambda value: regex.sub(replacement, value)


class RenderSubstitutionOption(BaseModel):
    find: RegexOption
    render: str

    class Config:
        extra = "forbid"

    def compile(self, template: TemplateManager) -> Callable[[str], str]:
        regex = RegexOption.compile(self.find.resolve(template))
        if not regex:
            return lambda value: value
        compiled_template = template.compile(self.render)
        return lambda value: regex.sub(
            lambda match: compiled_template.render(match=match),
            value,
        )


class SubstitutionOption(BaseModel):
    __root__: ListOption[Union[TextSubstitutionOption, RenderSubstitutionOption]]

    def compile(self, template: TemplateManager) -> Callable[[str], str]:
        substitutions = [sub.compile(template) for sub in self.__root__.entries()]

        def apply(value: str) -> str:
            for substitute in substitutions:
                value = substitute(value)
            return value

        return apply


class FindReplaceOptions(PluginOptions):
    resource_pack: PackSelectOption = PackSelectOption()
    data_pack: PackSelectOption = PackSelectOption()
    substitute: ListOption[Union[SubstitutionOption, "FindReplaceOptions"]]

    def compile(
        self,
        select_assets: PackSelector[ResourcePack],
        select_data: PackSelector[DataPack],
        template: TemplateManager,
    ) -> Tuple["FindReplaceHandler[ResourcePack]", "FindReplaceHandler[DataPack]"]:
        substitute = [
            (
                sub.compile(select_assets, select_data, template)
                if isinstance(sub, FindReplaceOptions)
                else sub.compile(template)
            )
            for sub in self.substitute.entries()
        ]
        return (
            FindReplaceHandler(
                select_assets.prepare(self.resource_pack),
                [sub if callable(sub) else sub[0] for sub in substitute],
            ),
            FindReplaceHandler(
                select_data.prepare(self.data_pack),
                [sub if callable(sub) else sub[1] for sub in substitute],
            ),
        )


ListOption[Union[SubstitutionOption, "FindReplaceOptions"]].update_forward_refs()


@dataclass(frozen=True)
class FindReplaceHandler(Generic[PackType]):
    pack_selector: PreparedPackSelector[PackType]
    substitute: Sequence[Union[Callable[[str], str], "FindReplaceHandler[PackType]"]]

    def __call__(self):
        text_files = self.pack_selector.gather(extend=TextFileBase[Any])
        for find_replace in self.substitute:
            if isinstance(find_replace, FindReplaceHandler):
                find_replace()
            else:
                for file_instance in text_files:
                    file_instance.text = find_replace(file_instance.text)


def beet_default(ctx: Context):
    ctx.require(find_replace)


@configurable(validator=FindReplaceOptions)
def find_replace(ctx: Context, opts: FindReplaceOptions):
    """Plugin for performing basic substitutions."""
    resource_pack_handler, data_pack_handler = opts.compile(
        ctx.select.from_pack(ctx.assets), ctx.select.from_pack(ctx.data), ctx.template
    )
    resource_pack_handler()
    data_pack_handler()
