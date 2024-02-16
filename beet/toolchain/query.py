__all__ = [
    "PackQuery",
    "PackQueryOption",
    "PreparedPackQuery",
    "PackSelection",
    "PackMatchOption",
    "ResolvedPackMatchOption",
    "CompiledPackMatchOption",
    "PreparedPackMatchQuery",
    "PackMatchSelection",
    "PathSpecOption",
    "ResolvedPathSpecOption",
    "CompiledPathSpecOption",
    "PackFilesOption",
    "ResolvedPackFilesOption",
    "CompiledPackFilesOption",
    "PreparedPackFilesQuery",
    "PackFilesSelection",
    "RegexOption",
    "ResolvedRegexOption",
    "CompiledRegexOption",
    "RegexFlagsOption",
    "RegexFlags",
]


import re
from dataclasses import dataclass, replace
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_origin,
    overload,
)

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from pydantic.v1 import BaseModel, validator

from beet.core.file import File
from beet.library.base import NamespaceFile, Pack, create_group_map

from .config import ListOption
from .template import TemplateManager

T = TypeVar("T")
PackType = TypeVar("PackType", bound=Pack[Any])
FromPackType = TypeVar("FromPackType", bound=Pack[Any])


RegexFlags = Literal["ASCII", "IGNORECASE", "MULTILINE", "DOTALL", "VERBOSE"]


class RegexFlagsOption(BaseModel):
    regex: ListOption[str] = ListOption()
    flags: ListOption[RegexFlags] = ListOption()

    class Config:
        extra = "forbid"


ResolvedRegexOption = Tuple[Sequence[str], int]
CompiledRegexOption = Optional["re.Pattern[str]"]


class RegexOption(BaseModel):
    __root__: RegexFlagsOption = RegexFlagsOption()

    @validator("__root__", pre=True)
    def validate_root(cls, value: Any) -> Any:
        if not isinstance(value, Mapping):
            return {"regex": value}
        return value  # type: ignore

    def resolve(
        self, template: Optional[TemplateManager] = None
    ) -> ResolvedRegexOption:
        patterns = self.__root__.regex.entries()
        flags = self.__root__.flags.entries()

        if template:
            patterns = template.render_json(patterns)
            flags = template.render_json(flags)

        combined_flags = 0
        for flag in flags:
            combined_flags |= getattr(re, flag)

        return patterns, combined_flags

    @staticmethod
    def compile(resolved: ResolvedRegexOption) -> CompiledRegexOption:
        if not resolved[0]:
            return None
        return re.compile("|".join(resolved[0]), resolved[1])


ResolvedPackFilesOption = Mapping[str, ResolvedRegexOption]
CompiledPackFilesOption = Mapping[str, CompiledRegexOption]


class PackFilesOption(BaseModel):
    __root__: Union[RegexOption, Dict[str, RegexOption]] = RegexOption()

    def resolve(
        self, template: Optional[TemplateManager] = None
    ) -> ResolvedPackFilesOption:
        option = self.__root__
        if isinstance(option, RegexOption):
            option = {"": option}
        return {
            prefix: regex_option.resolve(template)
            for prefix, regex_option in option.items()
        }

    @staticmethod
    def analyze_base_paths(resolved: ResolvedRegexOption) -> List[str]:
        base_paths: Set[str] = set()

        for pattern in resolved[0]:
            escaped = re.escape(pattern).replace(r"\.", ".")
            if pattern == escaped:
                base_paths.add(pattern)
                continue

            common: List[str] = []
            for part, escaped_part in zip(pattern.split("/"), escaped.split("/")):
                if not part or part != escaped_part:
                    break
                common.append(part)

            base_paths.add("/".join(common))

        return sorted(base_paths)

    @staticmethod
    def compile(resolved: ResolvedPackFilesOption) -> CompiledPackFilesOption:
        return {
            prefix: RegexOption.compile(resolved_regex)
            for prefix, resolved_regex in resolved.items()
        }


ResolvedPathSpecOption = Sequence[str]
CompiledPathSpecOption = Optional[PathSpec]


class PathSpecOption(BaseModel):
    __root__: ListOption[str] = ListOption()

    def resolve(
        self, template: Optional[TemplateManager] = None
    ) -> ResolvedPathSpecOption:
        patterns = self.__root__.entries()
        if template:
            patterns = template.render_json(patterns)
        return patterns

    @staticmethod
    def compile(patterns: ResolvedPathSpecOption) -> CompiledPathSpecOption:
        if not patterns:
            return None
        return PathSpec.from_lines("gitwildmatch", patterns)


ResolvedPackMatchOption = Mapping[str, Mapping[str, ResolvedPathSpecOption]]
CompiledPackMatchOption = Mapping[str, Mapping[str, CompiledPathSpecOption]]


class PackMatchOption(BaseModel):
    __root__: Union[
        PathSpecOption, Dict[str, Union[PathSpecOption, Dict[str, PathSpecOption]]]
    ] = PathSpecOption()

    def resolve(
        self,
        file_types: Sequence[Type[NamespaceFile]],
        template: Optional[TemplateManager] = None,
    ) -> ResolvedPackMatchOption:
        option = self.__root__
        if isinstance(option, PathSpecOption):
            option = option.resolve(template)
            return {"": {t.snake_name: list(option) for t in file_types}}

        result: Dict[str, Dict[str, List[str]]] = {}

        for group_name, value in option.items():
            if isinstance(value, PathSpecOption):
                value = {"": value}
            for prefix, pathspec_option in value.items():
                result.setdefault(prefix, {}).setdefault(group_name, []).extend(
                    pathspec_option.resolve(template)
                )

        return result

    @staticmethod
    def analyze_base_paths(
        resolved: Mapping[str, ResolvedPathSpecOption],
        group_map: Mapping[str, Tuple[Sequence[Pack[Any]], Type[NamespaceFile]]],
    ) -> List[str]:
        base_paths: Set[str] = set()

        for group_name, patterns in resolved.items():
            packs, file_type = group_map[group_name]

            for pack in packs:
                overlay = "" if pack.overlay_name is None else f"{pack.overlay_name}/"
                directory = pack.namespace_type.directory

                for pattern in patterns:
                    namespace, _, path = pattern.partition(":")

                    escaped = GitWildMatchPattern.escape(namespace)
                    if namespace != escaped:
                        base_paths.add(f"{overlay}{directory}")
                        continue

                    escaped = GitWildMatchPattern.escape(path)
                    if path == escaped:
                        prefix = "/".join([directory, namespace, *file_type.scope])
                        base_paths.add(f"{overlay}{prefix}/{path}{file_type.extension}")
                        continue

                    common: List[str] = []
                    for part, escaped_part in zip(path.split("/"), escaped.split("/")):
                        if not part or part != escaped_part:
                            break
                        common.append(part)

                    prefix = "/".join([directory, namespace, *file_type.scope, *common])
                    base_paths.add(f"{overlay}{prefix}")

        return sorted(base_paths)

    @staticmethod
    def compile(resolved: ResolvedPackMatchOption) -> CompiledPackMatchOption:
        return {
            prefix: {
                group_name: PathSpecOption.compile(pathspec_option)
                for group_name, pathspec_option in groups.items()
            }
            for prefix, groups in resolved.items()
        }


class PackQueryOption(BaseModel):
    files: PackFilesOption = PackFilesOption()
    match: PackMatchOption = PackMatchOption()

    class Config:
        extra = "forbid"


PackFilesSelection = Mapping[Tuple[str, T], Tuple[PackType, str]]


@dataclass(frozen=True, slots=True)
class PreparedPackFilesQuery(Generic[PackType]):
    packs: Sequence[PackType]
    files: ResolvedPackFilesOption
    files_regex: CompiledPackFilesOption

    def analyze_base_paths(self) -> Sequence[str]:
        return [
            base_path
            for resolved in self.files.values()
            for base_path in PackFilesOption.analyze_base_paths(resolved)
        ]

    @overload
    def select(
        self,
        *extensions: str,
    ) -> PackFilesSelection[File[Any, Any], PackType]: ...

    @overload
    def select(
        self,
        *extensions: str,
        extend: Type[T],
    ) -> PackFilesSelection[T, PackType]: ...

    def select(
        self,
        *extensions: str,
        extend: Optional[Any] = None,
    ) -> PackFilesSelection[Any, PackType]:
        if not any(self.files_regex.values()):
            return {}

        if extend and (origin := get_origin(extend)):
            extend = origin

        selected: Dict[str, List[Tuple[PackType, Any, str]]] = {}

        for pack in self.packs:
            for filename, file_instance in (
                pack.list_files(*extensions, extend=extend)
                if extend
                else pack.list_files(*extensions)
            ):
                for prefix, regex in self.files_regex.items():
                    if (
                        regex
                        and (m := regex.match(filename))
                        and (m.endpos == len(filename) or filename[m.endpos] == "/")
                    ):
                        selected.setdefault(regex.sub(prefix, filename), []).append(
                            (pack, file_instance, filename)
                        )

        result: Dict[Tuple[str, Any], Tuple[PackType, str]] = {}

        for prefix, entries in selected.items():
            for pack, file_instance, filename in entries:
                if not prefix:
                    dst = filename
                elif len(entries) > 1:
                    dst = "/".join([prefix, filename.rpartition("/")[-1]])
                else:
                    dst = prefix
                result[dst, file_instance] = (pack, filename)

        return result

    def copy_to(self, *args: Union[PackType, Sequence[PackType]]):
        packs = [p for arg in args for p in ([arg] if isinstance(arg, Pack) else arg)]

        result = self.select()

        while result:
            pack_origin: Dict[Type[Pack[Any]], Dict[str, File[Any, Any]]] = {}
            remaining: Dict[Tuple[str, File[Any, Any]], Tuple[PackType, str]] = dict(
                result
            )

            for (filename, file_instance), (pack, _) in result.items():
                origin = pack_origin.setdefault(type(pack), {})
                if filename not in origin:
                    remaining.pop((filename, file_instance))
                    origin[filename] = file_instance

            for pack in packs:
                if origin := pack_origin.get(type(pack)):
                    pack.load(origin)

            result = remaining

    def distinct(self) -> "PreparedPackQuery[PackType]":
        return PreparedPackQuery([self])


PackMatchSelection = Mapping[
    Type[NamespaceFile], Mapping[Tuple[str, T], Tuple[PackType, str]]
]


@dataclass(frozen=True, slots=True)
class PreparedPackMatchQuery(Generic[PackType]):
    packs: Sequence[PackType]
    match: ResolvedPackMatchOption
    match_spec: CompiledPackMatchOption

    def analyze_base_paths(self) -> Sequence[str]:
        group_map = create_group_map(
            {pack: pack.get_file_types() for pack in self.packs},
            plural=True,
        )
        return [
            base_path
            for resolved in self.match.values()
            for base_path in PackMatchOption.analyze_base_paths(resolved, group_map)
        ]

    @overload
    def select(
        self,
        *extensions: str,
    ) -> PackMatchSelection[File[Any, Any], PackType]: ...

    @overload
    def select(
        self,
        *extensions: str,
        extend: Type[T],
    ) -> PackMatchSelection[T, PackType]: ...

    def select(
        self,
        *extensions: str,
        extend: Optional[Any] = None,
    ) -> PackMatchSelection[Any, PackType]:
        if not any(self.match_spec.values()):
            return {}

        if extend and (origin := get_origin(extend)):
            extend = origin

        selected: Dict[
            Type[NamespaceFile], Dict[str, List[Tuple[PackType, Any, str]]]
        ] = {}

        group_map = create_group_map(
            {
                pack: pack.get_file_types(*extensions, extend=extend)
                for pack in self.packs
            },
            plural=True,
        )

        for prefix, value in self.match_spec.items():
            for group_name, pathspec in value.items():
                if pathspec and group_name in group_map:
                    packs, file_type = group_map[group_name]

                    for pack in packs:
                        pack_and_overlays = [pack]
                        if pack.overlay_parent is None:
                            pack_and_overlays.extend(pack.overlays.values())  # type: ignore

                        for p in pack_and_overlays:
                            for path, file_instance in p[file_type].items():
                                if pathspec.match_file(path):
                                    selected.setdefault(file_type, {}).setdefault(
                                        prefix, []
                                    ).append((p, file_instance, path))

        result: Dict[
            Type[NamespaceFile], Dict[Tuple[str, Any], Tuple[PackType, str]]
        ] = {}

        for file_type, value in selected.items():
            file_type_result = result.setdefault(file_type, {})
            for prefix, entries in value.items():
                for pack, file_instance, path in entries:
                    if not prefix:
                        dst = path
                    elif len(entries) > 1:
                        dst = ("/" if ":" in prefix else ":").join(
                            [prefix, path.partition(":")[-1].rpartition("/")[-1]]
                        )
                    else:
                        dst = prefix
                    file_type_result[dst, file_instance] = (pack, path)

        return result

    def copy_to(self, *args: Union[PackType, Sequence[PackType]]):
        packs = [p for arg in args for p in ([arg] if isinstance(arg, Pack) else arg)]

        result = self.select()

        for file_type, selection in result.items():
            pack_type = None

            while selection:
                content: Dict[str, File[Any, Any]] = {}
                remaining: Dict[Tuple[str, File[Any, Any]], Tuple[PackType, str]] = (
                    dict(selection)
                )

                for (path, file_instance), (pack, _) in selection.items():
                    if path not in content:
                        pack_type = type(pack)
                        remaining.pop((path, file_instance))
                        content[path] = file_instance

                for pack in packs:
                    if type(pack) is pack_type:
                        pack[file_type].merge({k: v.copy() for k, v in content.items()})

                selection = remaining

    def distinct(self) -> "PreparedPackQuery[PackType]":
        return PreparedPackQuery([self])


PackSelection = Mapping[T, PackType]


@dataclass(frozen=True, slots=True)
class PreparedPackQuery(Generic[PackType]):
    queries: Sequence[
        Union[
            PreparedPackFilesQuery[PackType],
            PreparedPackMatchQuery[PackType],
            "PreparedPackQuery[PackType]",
        ]
    ]

    def analyze_base_paths(self) -> Sequence[str]:
        return [
            base_path
            for query in self.queries
            for base_path in query.analyze_base_paths()
        ]

    @overload
    def select(
        self,
        *extensions: str,
    ) -> PackSelection[File[Any, Any], PackType]: ...

    @overload
    def select(
        self,
        *extensions: str,
        extend: Type[T],
    ) -> PackSelection[T, PackType]: ...

    def select(
        self,
        *extensions: str,
        extend: Optional[Any] = None,
    ) -> PackSelection[Any, PackType]:
        result: Dict[Any, PackType] = {}

        for query in self.queries:
            if isinstance(query, PreparedPackFilesQuery):
                for (_, file_instance), (pack, _) in (
                    query.select(*extensions, extend=extend)
                    if extend
                    else query.select(*extensions)
                ).items():
                    result[file_instance] = pack
            elif isinstance(query, PreparedPackMatchQuery):
                for _, entries in (
                    query.select(*extensions, extend=extend)
                    if extend
                    else query.select(*extensions)
                ).items():
                    for (_, file_instance), (pack, _) in entries.items():
                        result[file_instance] = pack
            else:
                result.update(
                    query.select(*extensions, extend=extend)
                    if extend
                    else query.select(*extensions)
                )

        return result

    def copy_to(self, *args: Union[PackType, Sequence[PackType]]):
        for query in self.queries:
            query.copy_to(*args)

    def distinct(self) -> "PreparedPackQuery[PackType]":
        return self


@dataclass(frozen=True, slots=True)
class PackQuery(Generic[PackType]):
    packs: Sequence[PackType]
    template: Optional[TemplateManager] = None

    def from_pack(
        self,
        *args: Union[FromPackType, Sequence[FromPackType]],
    ) -> "PackQuery[FromPackType]":
        packs = [p for arg in args for p in ([arg] if isinstance(arg, Pack) else arg)]
        return replace(self, packs=packs)  # type: ignore

    @overload
    def prepare(
        self, pack_options: PackFilesOption
    ) -> PreparedPackFilesQuery[PackType]: ...

    @overload
    def prepare(self, *, files: Any) -> PreparedPackFilesQuery[PackType]: ...

    @overload
    def prepare(
        self, pack_options: PackMatchOption
    ) -> PreparedPackMatchQuery[PackType]: ...

    @overload
    def prepare(self, *, match: Any) -> PreparedPackMatchQuery[PackType]: ...

    @overload
    def prepare(
        self,
        pack_options: Union[
            PackQueryOption,
            Sequence[Union[PackFilesOption, PackMatchOption, PackQueryOption]],
        ],
    ) -> PreparedPackQuery[PackType]: ...

    @overload
    def prepare(
        self,
        pack_options: Optional[
            Union[
                PackFilesOption,
                PackMatchOption,
                PackQueryOption,
                Sequence[Union[PackFilesOption, PackMatchOption, PackQueryOption]],
            ]
        ] = None,
        *,
        files: Any,
        match: Any,
    ) -> PreparedPackQuery[PackType]: ...

    def prepare(
        self,
        pack_options: Optional[
            Union[
                PackFilesOption,
                PackMatchOption,
                PackQueryOption,
                Sequence[Union[PackFilesOption, PackMatchOption, PackQueryOption]],
            ]
        ] = None,
        *,
        files: Optional[Any] = None,
        match: Optional[Any] = None,
    ) -> Union[
        PreparedPackFilesQuery[PackType],
        PreparedPackMatchQuery[PackType],
        PreparedPackQuery[PackType],
    ]:
        if files:
            if match:
                return PreparedPackQuery(
                    [
                        *([self.prepare(pack_options)] if pack_options else []),
                        self.prepare(files=files),
                        self.prepare(match=match),
                    ]
                )
            return self.prepare(PackFilesOption.parse_obj(files))
        if match:
            return self.prepare(PackMatchOption.parse_obj(match))
        if isinstance(pack_options, PackFilesOption):
            resolved = pack_options.resolve(self.template)
            return PreparedPackFilesQuery(
                self.packs,
                resolved,
                PackFilesOption.compile(resolved),
            )
        if isinstance(pack_options, PackMatchOption):
            resolved = pack_options.resolve(
                sorted(
                    {t for p in self.packs for t in p.get_file_types()},
                    key=lambda t: t.snake_name,
                ),
                self.template,
            )
            return PreparedPackMatchQuery(
                self.packs,
                resolved,
                PackMatchOption.compile(resolved),
            )
        if pack_options:
            options = (
                (pack_options.files, pack_options.match)
                if isinstance(pack_options, PackQueryOption)
                else pack_options
            )
            return PreparedPackQuery([self.prepare(opts) for opts in options])
        raise ValueError("Invalid arguments")

    @property
    def select(self: T) -> T:
        return self

    @overload
    def __call__(
        self,
        *extensions: str,
        files: Any,
    ) -> PackFilesSelection[File[Any, Any], PackType]: ...

    @overload
    def __call__(
        self,
        *extensions: str,
        extend: Type[T],
        files: Any,
    ) -> PackFilesSelection[T, PackType]: ...

    @overload
    def __call__(
        self,
        *extensions: str,
        match: Any,
    ) -> PackMatchSelection[File[Any, Any], PackType]: ...

    @overload
    def __call__(
        self,
        *extensions: str,
        extend: Type[T],
        match: Any,
    ) -> PackMatchSelection[T, PackType]: ...

    def __call__(
        self,
        *extensions: str,
        extend: Optional[Any] = None,
        files: Optional[Any] = None,
        match: Optional[Any] = None,
    ) -> Union[PackFilesSelection[Any, PackType], PackMatchSelection[Any, PackType]]:
        query = (
            self.prepare(files=files)
            if files is not None
            else self.prepare(match=match)
        )
        return (
            query.select(*extensions, extend=extend)
            if extend
            else query.select(*extensions)
        )

    @overload
    def distinct(
        self,
        *args: Union[
            str,
            PackFilesOption,
            PackMatchOption,
            PackQueryOption,
            Sequence[Union[PackFilesOption, PackMatchOption, PackQueryOption]],
        ],
        files: Optional[Any] = None,
        match: Optional[Any] = None,
    ) -> PackSelection[File[Any, Any], PackType]: ...

    @overload
    def distinct(
        self,
        *args: Union[
            str,
            PackFilesOption,
            PackMatchOption,
            PackQueryOption,
            Sequence[Union[PackFilesOption, PackMatchOption, PackQueryOption]],
        ],
        extend: Type[T],
        files: Optional[Any] = None,
        match: Optional[Any] = None,
    ) -> PackSelection[T, PackType]: ...

    def distinct(
        self,
        *args: Union[
            str,
            PackFilesOption,
            PackMatchOption,
            PackQueryOption,
            Sequence[Union[PackFilesOption, PackMatchOption, PackQueryOption]],
        ],
        extend: Optional[Any] = None,
        files: Optional[Any] = None,
        match: Optional[Any] = None,
    ) -> PackSelection[Any, PackType]:
        extensions: List[str] = []
        queries: List[PreparedPackQuery[PackType]] = []

        for arg in args:
            if isinstance(arg, str):
                extensions.append(arg)
            else:
                queries.append(self.prepare(arg).distinct())

        if files or match:
            queries.append(self.prepare(files=files, match=match).distinct())

        return (
            PreparedPackQuery(queries).select(*extensions, extend=extend)
            if extend
            else PreparedPackQuery(queries).select(*extensions)
        )
