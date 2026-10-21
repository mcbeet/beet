__all__ = [
    "CompiledPackFilesOption",
    "CompiledPackMatchOption",
    "CompiledPathSpecOption",
    "CompiledRegexOption",
    "PackFilesOption",
    "PackFilesSelection",
    "PackMatchOption",
    "PackMatchSelection",
    "PackQuery",
    "PackQueryOption",
    "PackSelection",
    "PathSpecOption",
    "PreparedPackFilesQuery",
    "PreparedPackMatchQuery",
    "PreparedPackQuery",
    "RegexFlags",
    "RegexFlagsOption",
    "RegexOption",
    "ResolvedPackFilesOption",
    "ResolvedPackMatchOption",
    "ResolvedPathSpecOption",
    "ResolvedRegexOption",
]


import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Literal,
    Self,
    TypeVar,
    get_origin,
    overload,
)

from pathspec import PathSpec
from pathspec.patterns.gitignore.spec import GitIgnoreSpecPattern
from pydantic import BaseModel, ConfigDict, RootModel, field_validator

from beet.core.file import File
from beet.library.base import NamespaceFile, Pack, create_group_map, get_output_scope

from .config import ListOption
from .template import TemplateManager

T = TypeVar("T")
PackType = TypeVar("PackType", bound=Pack[Any])
FromPackType = TypeVar("FromPackType", bound=Pack[Any])


type RegexFlags = Literal["ASCII", "IGNORECASE", "MULTILINE", "DOTALL", "VERBOSE"]


class RegexFlagsOption(BaseModel):
    regex: ListOption[str] = ListOption()
    flags: ListOption[RegexFlags] = ListOption()
    model_config = ConfigDict(extra="forbid")


type ResolvedRegexOption = tuple[Sequence[str], int]
type CompiledRegexOption = re.Pattern[str] | None


class RegexOption(RootModel[RegexFlagsOption]):
    root: RegexFlagsOption = RegexFlagsOption()

    @field_validator("root", mode="before")
    @classmethod
    def validate_root(cls, value: Any) -> Any:
        if not isinstance(value, Mapping):
            return {"regex": value}
        return value

    def resolve(self, template: TemplateManager | None = None) -> ResolvedRegexOption:
        patterns = self.root.regex.entries()
        flags = self.root.flags.entries()

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


type ResolvedPackFilesOption = Mapping[str, ResolvedRegexOption]
type CompiledPackFilesOption = Mapping[str, CompiledRegexOption]


class PackFilesOption(RootModel[RegexOption | dict[str, RegexOption]]):
    root: RegexOption | dict[str, RegexOption] = RegexOption()

    def resolve(
        self, template: TemplateManager | None = None
    ) -> ResolvedPackFilesOption:
        option = self.root
        if isinstance(option, RegexOption):
            option = {"": option}
        return {
            prefix: regex_option.resolve(template)
            for prefix, regex_option in option.items()
        }

    @staticmethod
    def analyze_base_paths(resolved: ResolvedRegexOption) -> list[str]:
        base_paths: set[str] = set()

        for pattern in resolved[0]:
            escaped = re.escape(pattern).replace(r"\.", ".")
            if pattern == escaped:
                base_paths.add(pattern)
                continue

            common: list[str] = []
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


type ResolvedPathSpecOption = Sequence[str]
type CompiledPathSpecOption = PathSpec[Any] | None


class PathSpecOption(RootModel[ListOption[str]]):
    root: ListOption[str] = ListOption()

    def resolve(
        self, template: TemplateManager | None = None
    ) -> ResolvedPathSpecOption:
        patterns = self.root.entries()
        if template:
            patterns = template.render_json(patterns)
        return patterns

    @staticmethod
    def compile(patterns: ResolvedPathSpecOption) -> CompiledPathSpecOption:
        if not patterns:
            return None
        return PathSpec.from_lines("gitignore", patterns)


type ResolvedPackMatchOption = Mapping[str, Mapping[str, ResolvedPathSpecOption]]
type CompiledPackMatchOption = Mapping[str, Mapping[str, CompiledPathSpecOption]]


class PackMatchOption(
    RootModel[PathSpecOption | dict[str, PathSpecOption | dict[str, PathSpecOption]]]
):
    root: PathSpecOption | dict[str, PathSpecOption | dict[str, PathSpecOption]] = (
        PathSpecOption()
    )

    def resolve(
        self,
        file_types: Sequence[type[NamespaceFile]],
        template: TemplateManager | None = None,
    ) -> ResolvedPackMatchOption:
        option = self.root
        if isinstance(option, PathSpecOption):
            option = option.resolve(template)
            return {"": {t.snake_name: list(option) for t in file_types}}

        result: dict[str, dict[str, list[str]]] = {}

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
        group_map: Mapping[str, tuple[Sequence[Pack[Any]], type[NamespaceFile]]],
    ) -> list[str]:
        base_paths: set[str] = set()

        for group_name, patterns in resolved.items():
            packs, file_type = group_map[group_name]

            for pack in packs:
                overlay = "" if pack.overlay_name is None else f"{pack.overlay_name}/"
                directory = pack.namespace_type.directory

                for pattern in patterns:
                    namespace, _, path = pattern.partition(":")

                    escaped = GitIgnoreSpecPattern.escape(namespace)
                    if namespace != escaped:
                        base_paths.add(f"{overlay}{directory}")
                        continue

                    escaped = GitIgnoreSpecPattern.escape(path)
                    if path == escaped:
                        scope = get_output_scope(file_type.scope, pack)
                        prefix = "/".join([directory, namespace, *scope])
                        base_paths.add(f"{overlay}{prefix}/{path}{file_type.extension}")
                        continue

                    common: list[str] = []
                    for part, escaped_part in zip(path.split("/"), escaped.split("/")):
                        if not part or part != escaped_part:
                            break
                        common.append(part)

                    scope = get_output_scope(file_type.scope, pack)
                    prefix = "/".join([directory, namespace, *scope, *common])
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
    model_config = ConfigDict(extra="forbid")


PackFilesSelection = Mapping[tuple[str, T], tuple[PackType, str]]


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
        extend: type[T],
    ) -> PackFilesSelection[T, PackType]: ...

    def select(
        self,
        *extensions: str,
        extend: Any | None = None,
    ) -> PackFilesSelection[Any, PackType]:
        if not any(self.files_regex.values()):
            return {}

        if extend and (origin := get_origin(extend)):
            extend = origin

        selected: dict[str, list[tuple[PackType, Any, str]]] = {}

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

        result: dict[tuple[str, Any], tuple[PackType, str]] = {}

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

    def copy_to(self, *args: PackType | Sequence[PackType]):
        packs = [p for arg in args for p in ([arg] if isinstance(arg, Pack) else arg)]

        result = self.select()

        while result:
            pack_origin: dict[type[Pack[Any]], dict[str, File[Any, Any]]] = {}
            remaining: dict[tuple[str, File[Any, Any]], tuple[PackType, str]] = dict(
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

    def distinct(self) -> PreparedPackQuery[PackType]:
        return PreparedPackQuery([self])


PackMatchSelection = Mapping[
    type[NamespaceFile], Mapping[tuple[str, T], tuple[PackType, str]]
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
        extend: type[T],
    ) -> PackMatchSelection[T, PackType]: ...

    def select(
        self,
        *extensions: str,
        extend: Any | None = None,
    ) -> PackMatchSelection[Any, PackType]:
        if not any(self.match_spec.values()):
            return {}

        if extend and (origin := get_origin(extend)):
            extend = origin

        selected: dict[
            type[NamespaceFile], dict[str, list[tuple[PackType, Any, str]]]
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
                            pack_and_overlays.extend(pack.overlays.values())

                        for p in pack_and_overlays:
                            for path, file_instance in p[file_type].items():
                                if pathspec.match_file(path):
                                    selected.setdefault(file_type, {}).setdefault(
                                        prefix, []
                                    ).append((p, file_instance, path))

        result: dict[
            type[NamespaceFile], dict[tuple[str, Any], tuple[PackType, str]]
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

    def copy_to(self, *args: PackType | Sequence[PackType]):
        packs = [p for arg in args for p in ([arg] if isinstance(arg, Pack) else arg)]

        result = self.select()

        for file_type, selection in result.items():
            pack_type = None

            while selection:
                content: dict[str, File[Any, Any]] = {}
                remaining: dict[tuple[str, File[Any, Any]], tuple[PackType, str]] = (
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

    def distinct(self) -> PreparedPackQuery[PackType]:
        return PreparedPackQuery([self])


PackSelection = Mapping[T, PackType]


@dataclass(frozen=True, slots=True)
class PreparedPackQuery(Generic[PackType]):
    queries: Sequence[
        PreparedPackFilesQuery[PackType]
        | PreparedPackMatchQuery[PackType]
        | PreparedPackQuery[PackType]
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
        extend: type[T],
    ) -> PackSelection[T, PackType]: ...

    def select(
        self,
        *extensions: str,
        extend: Any | None = None,
    ) -> PackSelection[Any, PackType]:
        result: dict[Any, PackType] = {}

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

    def copy_to(self, *args: PackType | Sequence[PackType]):
        for query in self.queries:
            query.copy_to(*args)

    def distinct(self) -> PreparedPackQuery[PackType]:
        return self


@dataclass(frozen=True, slots=True)
class PackQuery(Generic[PackType]):
    packs: Sequence[PackType]
    template: TemplateManager | None = None

    def from_pack(
        self,
        *args: FromPackType | Sequence[FromPackType],
    ) -> PackQuery[FromPackType]:
        packs = [p for arg in args for p in ([arg] if isinstance(arg, Pack) else arg)]
        return PackQuery(packs, self.template)

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
        pack_options: PackQueryOption
        | Sequence[PackFilesOption | PackMatchOption | PackQueryOption],
    ) -> PreparedPackQuery[PackType]: ...

    @overload
    def prepare(
        self,
        pack_options: PackFilesOption
        | PackMatchOption
        | PackQueryOption
        | Sequence[PackFilesOption | PackMatchOption | PackQueryOption]
        | None = None,
        *,
        files: Any,
        match: Any,
    ) -> PreparedPackQuery[PackType]: ...

    def prepare(
        self,
        pack_options: PackFilesOption
        | PackMatchOption
        | PackQueryOption
        | Sequence[PackFilesOption | PackMatchOption | PackQueryOption]
        | None = None,
        *,
        files: Any | None = None,
        match: Any | None = None,
    ) -> (
        PreparedPackFilesQuery[PackType]
        | PreparedPackMatchQuery[PackType]
        | PreparedPackQuery[PackType]
    ):
        if files:
            if match:
                return PreparedPackQuery(
                    [
                        *([self.prepare(pack_options)] if pack_options else []),
                        self.prepare(files=files),
                        self.prepare(match=match),
                    ]
                )
            return self.prepare(PackFilesOption.model_validate(files))
        if match:
            return self.prepare(PackMatchOption.model_validate(match))
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
    def select(self) -> Self:
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
        extend: type[T],
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
        extend: type[T],
        match: Any,
    ) -> PackMatchSelection[T, PackType]: ...

    def __call__(
        self,
        *extensions: str,
        extend: Any | None = None,
        files: Any | None = None,
        match: Any | None = None,
    ) -> PackFilesSelection[Any, PackType] | PackMatchSelection[Any, PackType]:
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
        *args: str
        | PackFilesOption
        | PackMatchOption
        | PackQueryOption
        | Sequence[PackFilesOption | PackMatchOption | PackQueryOption],
        files: Any | None = None,
        match: Any | None = None,
    ) -> PackSelection[File[Any, Any], PackType]: ...

    @overload
    def distinct(
        self,
        *args: str
        | PackFilesOption
        | PackMatchOption
        | PackQueryOption
        | Sequence[PackFilesOption | PackMatchOption | PackQueryOption],
        extend: type[T],
        files: Any | None = None,
        match: Any | None = None,
    ) -> PackSelection[T, PackType]: ...

    def distinct(
        self,
        *args: str
        | PackFilesOption
        | PackMatchOption
        | PackQueryOption
        | Sequence[PackFilesOption | PackMatchOption | PackQueryOption],
        extend: Any | None = None,
        files: Any | None = None,
        match: Any | None = None,
    ) -> PackSelection[Any, PackType]:
        extensions: list[str] = []
        queries: list[PreparedPackQuery[PackType]] = []

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
