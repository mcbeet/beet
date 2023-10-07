__all__ = [
    "select_files",
    "select_all",
    "PackSelector",
    "PackSelection",
    "PackSelectOption",
    "PackMatchOption",
    "PathSpecOption",
    "RegexOption",
    "RegexFlagsOption",
    "RegexFlags",
]


import re
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Iterable,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_origin,
    overload,
)

from pathspec import PathSpec
from pydantic import BaseModel

from beet.core.file import File
from beet.library.base import NamespaceFile, Pack

from .config import ListOption
from .template import TemplateManager

T = TypeVar("T")
PackType = TypeVar("PackType", bound=Pack[Any])

PackSelection = Dict[T, Tuple[Optional[str], Optional[str]]]

RegexFlags = Literal["ASCII", "IGNORECASE", "MULTILINE", "DOTALL", "VERBOSE"]


class RegexFlagsOption(BaseModel):
    regex: ListOption[str] = ListOption()
    flags: ListOption[RegexFlags] = ListOption()

    class Config:
        extra = "forbid"


class RegexOption(BaseModel):
    __root__: Union[ListOption[str], RegexFlagsOption] = ListOption()

    def compile_regex(
        self,
        template: Optional[TemplateManager] = None,
    ) -> Optional["re.Pattern[str]"]:
        flags = 0

        if isinstance(self.__root__, RegexFlagsOption):
            patterns = self.__root__.regex.entries()
            for flag in self.__root__.flags.entries():
                flags |= getattr(re, flag)
        else:
            patterns = self.__root__.entries()

        if not patterns:
            return None
        source = "|".join(patterns)
        if template:
            source = template.render_string(source)

        return re.compile(source, flags)


class PathSpecOption(BaseModel):
    __root__: ListOption[str] = ListOption()

    def compile_spec(
        self, template: Optional[TemplateManager] = None
    ) -> Optional[PathSpec]:
        patterns = self.__root__.entries()

        if not patterns:
            return None
        if template:
            patterns = template.render_json(patterns)

        return PathSpec.from_lines("gitwildmatch", patterns)


class PackMatchOption(BaseModel):
    __root__: Union[PathSpecOption, Dict[str, PathSpecOption]] = PathSpecOption()

    def compile_match(
        self,
        template: Optional[TemplateManager] = None,
    ) -> Optional[Union[PathSpec, Dict[str, PathSpec]]]:
        if isinstance(self.__root__, PathSpecOption):
            return self.__root__.compile_spec(template)
        else:
            return {
                group_name: spec
                for group_name, match in self.__root__.items()
                if (spec := match.compile_spec(template))
            }


class PackSelectOption(BaseModel):
    files: RegexOption = RegexOption()
    match: PackMatchOption = PackMatchOption()

    class Config:
        extra = "forbid"

    def compile(
        self,
        template: Optional[TemplateManager] = None,
    ) -> Tuple[
        Optional["re.Pattern[str]"],
        Optional[Union[PathSpec, Dict[str, PathSpec]]],
    ]:
        return self.files.compile_regex(template), self.match.compile_match(template)


@dataclass(frozen=True)
class PackSelector:
    files_regex: Optional["re.Pattern[str]"] = None
    match_spec: Optional[Union[PathSpec, Dict[str, PathSpec]]] = None

    @classmethod
    def from_options(
        cls,
        select_options: Optional[
            Union[PackSelectOption, RegexOption, PackMatchOption]
        ] = None,
        *,
        files: Optional[Any] = None,
        match: Optional[Any] = None,
        template: Optional[TemplateManager] = None,
    ) -> "PackSelector":
        if isinstance(select_options, PackSelectOption):
            return PackSelector(*select_options.compile(template))
        if isinstance(select_options, RegexOption):
            return cls.from_options(PackSelectOption(files=select_options))
        if isinstance(select_options, PackMatchOption):
            return cls.from_options(PackSelectOption(match=select_options))
        values = {}
        if files:
            values["files"] = files
        if match:
            values["match"] = match
        return PackSelector(*PackSelectOption.parse_obj(values).compile(template))

    @overload
    def select_files(
        self,
        pack: Pack[Any],
        *extensions: str,
    ) -> PackSelection[File[Any, Any]]:
        ...

    @overload
    def select_files(
        self,
        pack: Pack[Any],
        *extensions: str,
        extend: Type[T],
    ) -> PackSelection[T]:
        ...

    def select_files(
        self,
        pack: Pack[Any],
        *extensions: str,
        extend: Optional[Any] = None,
    ) -> PackSelection[Any]:
        if extend and (origin := get_origin(extend)):
            extend = origin

        result: PackSelection[Any] = {}

        if self.files_regex:
            for filename, file_instance in (
                pack.list_files(*extensions, extend=extend)
                if extend
                else pack.list_files(*extensions)
            ):
                if self.files_regex.fullmatch(filename):
                    result[file_instance] = filename, None

        if self.match_spec:
            file_types = set(pack.resolve_scope_map().values())

            if extensions:
                file_types = {t for t in file_types if t.extension in extensions}
            if extend:
                file_types = {t for t in file_types if issubclass(t, extend)}

            if isinstance(self.match_spec, dict):
                group_map = {t.snake_name: t for t in file_types}
                for singular in list(group_map):
                    group_map.setdefault(f"{singular}s", group_map[singular])

                for group, spec in self.match_spec.items():
                    if file_type := group_map.get(group):
                        result.update(_gather_from_pack(pack, file_type, spec))

            else:
                for file_type in file_types:
                    result.update(_gather_from_pack(pack, file_type, self.match_spec))

        return result


@overload
def select_files(
    pack: Pack[Any],
    *extensions: str,
    files: Optional[Any] = None,
    match: Optional[Any] = None,
    template: Optional[TemplateManager] = None,
) -> PackSelection[File[Any, Any]]:
    ...


@overload
def select_files(
    pack: Pack[Any],
    *extensions: str,
    extend: Type[T],
    files: Optional[Any] = None,
    match: Optional[Any] = None,
    template: Optional[TemplateManager] = None,
) -> PackSelection[T]:
    ...


def select_files(
    pack: Pack[Any],
    *extensions: str,
    extend: Optional[Any] = None,
    files: Optional[Any] = None,
    match: Optional[Any] = None,
    template: Optional[TemplateManager] = None,
) -> PackSelection[Any]:
    selector = PackSelector.from_options(files=files, match=match, template=template)
    return (
        selector.select_files(pack, *extensions, extend=extend)
        if extend
        else selector.select_files(pack, *extensions)
    )


def select_all(pack: Pack[Any], extend: Type[T]) -> Iterable[Tuple[str, T]]:
    file_types = set(pack.resolve_scope_map().values())
    if extend:
        file_types = {t for t in file_types if issubclass(t, extend)}
    for file_type in file_types:
        yield from pack[file_type].items()  # type: ignore
        if pack.overlay_parent is None:
            for overlay in pack.overlays.values():
                yield from overlay[file_type].items()  # type: ignore


def _gather_from_pack(
    pack: Pack[Any], file_type: Type[NamespaceFile], spec: PathSpec
) -> Iterable[Tuple[NamespaceFile, Tuple[Optional[str], Optional[str]]]]:
    for path, file_instance in pack[file_type].items():
        if spec.match_file(path):
            yield file_instance, (None, path)
    if pack.overlay_parent is None:
        for overlay in pack.overlays.values():
            yield from _gather_from_pack(overlay, file_type, spec)
