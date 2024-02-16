"""Plugin for compiling json files with mecha."""

__all__ = [
    "JsonFileCompilation",
    "AstJsonRoot",
    "AstJsonContent",
    "AstMergeJsonContent",
    "AstAppendJsonContent",
    "AstPrependJsonContent",
    "JsonRootParser",
    "JsonContentParser",
    "JsonFileHandler",
]


from dataclasses import dataclass
from typing import Any, Set, Type, Union

from beet import Context, DataPack, JsonFileBase, ResourcePack
from beet.core.utils import required_field
from tokenstream import TokenStream, set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstCommandSentinel,
    AstJson,
    AstRoot,
    CompilationDatabase,
    Diagnostic,
    Dispatcher,
    FileTypeCompilationUnitProvider,
    Mecha,
    Parser,
    Visitor,
    delegate,
    rule,
)


@dataclass(frozen=True, slots=True)
class AstJsonRoot(AstRoot):
    """Ast json root node."""


@dataclass(frozen=True, slots=True)
class AstJsonContent(AstCommandSentinel):
    """Ast json content node."""

    @classmethod
    def create_root_node(cls, value: AstJson):
        content_node = cls(arguments=AstChildren([value]))
        content_node = set_location(content_node, value)
        root_node = AstJsonRoot(commands=AstChildren([content_node]))
        root_node = set_location(root_node, content_node)
        return root_node


@dataclass(frozen=True, slots=True)
class AstMergeJsonContent(AstJsonContent):
    """Ast merge json content node."""


@dataclass(frozen=True, slots=True)
class AstAppendJsonContent(AstJsonContent):
    """Ast append json content node."""


@dataclass(frozen=True, slots=True)
class AstPrependJsonContent(AstJsonContent):
    """Ast prepend json content node."""


def beet_default(ctx: Context):
    ctx.inject(JsonFileCompilation).activate()


class JsonFileCompilation:
    """Service for managing json file compilation."""

    mc: Mecha
    handler: Dispatcher[AstRoot]
    file_types: Set[Type[JsonFileBase[Any]]]
    active: bool

    def __init__(
        self,
        arg: Union[Context, Mecha],
        *packs: Union[ResourcePack, DataPack],
    ):
        if isinstance(arg, Context):
            packs += arg.packs
            self.mc = arg.inject(Mecha)
        else:
            self.mc = arg

        self.handler = JsonFileHandler(database=self.mc.database)
        self.mc.steps.append(self.handler)

        self.file_types = {  # type: ignore
            file_type
            for pack in packs
            for file_type in pack.get_file_types(extend=JsonFileBase)
        }

        self.active = False

    def activate(self):
        if self.active:
            return
        self.active = True

        self.mc.spec.parsers["root"] = JsonRootParser(
            database=self.mc.database,
            json_file_compilation=self,
            root_parser=self.mc.spec.parsers["root"],
        )

        self.mc.spec.parsers["root_item"] = JsonContentParser(
            root_item_parser=self.mc.spec.parsers["root_item"],
            json_parser=delegate("json"),
        )

        self.mc.providers.append(
            FileTypeCompilationUnitProvider(
                sorted(self.file_types, key=lambda t: t.snake_name),  # type: ignore
                no_index=True,
            )
        )


@dataclass
class JsonRootParser:
    """Parser for json root."""

    database: CompilationDatabase
    json_file_compilation: JsonFileCompilation
    root_parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if "json_content" not in stream.data:
            json_content = (
                type(self.database.current) in self.json_file_compilation.file_types
            )
            with stream.provide(json_content=json_content):
                node = self.root_parser(stream)
            if json_content and isinstance(node, AstRoot):
                json_root = AstJsonRoot(commands=node.commands)
                node = set_location(json_root, node)
            return node
        return self.root_parser(stream)


@dataclass
class JsonContentParser:
    """Parser for json content."""

    root_item_parser: Parser
    json_parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if stream.data.get("json_content"):
            with stream.syntax(json=r"\{|\["):
                hint = stream.peek()
            if hint and hint.match("json"):
                with stream.ignore("newline"):
                    node = self.json_parser(stream)
                root_item = AstJsonContent(arguments=AstChildren([node]))
                return set_location(root_item, node)
        return self.root_item_parser(stream)


@dataclass
class JsonFileHandler(Visitor):
    """Handler for json files."""

    database: CompilationDatabase = required_field()

    @rule(AstRoot)
    def root(self, node: AstRoot):
        return node

    @rule(AstJsonRoot)
    def json_root(self, node: AstJsonRoot):
        for command in node.commands:
            yield command
        return None

    @rule(AstCommand)
    def command(self, node: AstCommand):
        d = Diagnostic(
            "error",
            f'Unexpected "{node.identifier.split(":")[0]}" command in json file.',
        )
        return set_location(d, node)

    @rule(AstJsonContent)
    def json_content(self, node: AstJsonContent):
        if node.arguments and isinstance(content := node.arguments[0], AstJson):
            target = self.database.current
            if isinstance(target, JsonFileBase):
                file_instance = type(target)(content.evaluate())
                if isinstance(node, AstMergeJsonContent):
                    if not target.merge(file_instance):
                        target.data = file_instance.data
                elif isinstance(node, AstAppendJsonContent):
                    target.append(file_instance)  # type: ignore
                elif isinstance(node, AstPrependJsonContent):
                    target.prepend(file_instance)  # type: ignore
                else:
                    target.data = file_instance.data
