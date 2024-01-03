from dataclasses import dataclass, replace
from typing import ClassVar

from beet import Context, Function, Generator, TextFile
from beet.core.utils import required_field
from tokenstream import TokenStream, set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstResourceLocation,
    AstRoot,
    CompilationDatabase,
    FileTypeCompilationUnitProvider,
    Mecha,
    MutatingReducer,
    Parser,
    rule,
)
from mecha.contrib.nested_location import NestedLocationResolver


class Test(TextFile):
    scope: ClassVar[tuple[str, ...]] = ("tests",)
    extension: ClassVar[str] = ".mcfunction"


COMMAND_TREE = {
    "type": "root",
    "children": {
        "test": {
            "type": "literal",
            "children": {
                "function": {
                    "type": "argument",
                    "parser": "minecraft:function",
                    "children": {
                        "commands": {
                            "type": "argument",
                            "parser": "mecha:nested_root",
                            "executable": True,
                        }
                    },
                },
                "commands": {
                    "type": "argument",
                    "parser": "mecha:nested_root",
                    "executable": True,
                },
            },
        }
    },
}


def beet_default(ctx: Context):
    ctx.data.extend_namespace.append(Test)

    mc = ctx.inject(Mecha)
    mc.providers.append(FileTypeCompilationUnitProvider([Test]))
    mc.spec.add_commands(COMMAND_TREE)
    mc.spec.parsers["root"] = TestRootParser(mc.database, mc.spec.parsers["root"])
    mc.transform.extend(
        NestedTestTransformer(
            transform=mc.transform,
            database=mc.database,
            generate=ctx.generate,
            nested_location_resolver=ctx.inject(NestedLocationResolver),
        )
    )


@dataclass(frozen=True, slots=True)
class AstTestRoot(AstRoot):
    """Ast test root node.

    Technically not required but it's good practice to have custom root nodes for custom
    file types. Makes it easier to target with @rule and bolt won't treat it as a plain module.
    """


@dataclass
class TestRootParser:
    """Parser for test root."""

    database: CompilationDatabase
    root_parser: Parser

    def __call__(self, stream: TokenStream):
        if "test_file" not in stream.data:
            test_file = isinstance(self.database.current, Test)
            with stream.provide(test_file=test_file):
                node = self.root_parser(stream)
            if test_file and isinstance(node, AstRoot):
                test_root = AstTestRoot(commands=node.commands)
                node = set_location(test_root, node)
            return node
        return self.root_parser(stream)


@dataclass
class NestedTestTransformer(MutatingReducer):
    """Emit actual test files from nested test definitions."""

    transform: object = required_field()
    database: CompilationDatabase = required_field()
    generate: Generator = required_field()
    nested_location_resolver: NestedLocationResolver = required_field()

    @rule(AstCommand, identifier="test:commands")
    def anonymous_nested_test(self, node: AstCommand):
        namespace, resolved = self.nested_location_resolver.resolve()
        full_name = self.generate.format(f"{namespace}:{resolved}/generated_{{incr}}")
        return replace(
            node,
            identifier="test:function:commands",
            arguments=AstChildren(
                [AstResourceLocation.from_value(full_name), node.arguments[0]]
            ),
        )

    @rule(AstCommand, identifier="test:function:commands")
    def nested_test(self, node: AstCommand):
        if isinstance(resource_location := node.arguments[0], AstResourceLocation):
            full_name = resource_location.get_canonical_value()
            target = self.generate(
                full_name, default=Test(original=self.database.current.original)
            )
            self.database[target] = replace(
                self.database[self.database.current],
                ast=node.arguments[1],
                resource_location=full_name,
                no_index=True,
            )
            self.database.enqueue(target, self.database.step + 1)
            return None


def convert_tests(ctx: Context):
    """Convert to regular functions to be able to load the resulting test snapshot."""
    for name, test in ctx.data[Test].items():
        ctx.data[name] = Function(test.text)
    ctx.data[Test].clear()
