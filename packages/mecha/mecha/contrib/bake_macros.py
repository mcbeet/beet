"""Plugin for baking static macro invocations."""


__all__ = [
    "bake_macros",
    "BakeMacrosOptions",
    "MacroBaker",
    "MacroInvocation",
    "MacroInvocationArgument",
    "MacroBakerParseCallback",
]


from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Protocol, Set
from weakref import WeakKeyDictionary

from beet import (
    Context,
    Function,
    Generator,
    ListOption,
    PluginOptions,
    TextFileBase,
    configurable,
)
from beet.core.utils import required_field
from nbtlib import String
from pathspec import PathSpec
from tokenstream import INITIAL_LOCATION, Preprocessor, SourceLocation, set_location

from mecha import (
    AstChildren,
    AstCommand,
    AstMacroLine,
    AstMacroLineText,
    AstMacroLineVariable,
    AstNbtCompound,
    AstNbtCompoundEntry,
    AstNbtValue,
    AstResourceLocation,
    AstRoot,
    CompilationDatabase,
    Diagnostic,
    DiagnosticCollection,
    DiagnosticError,
    Mecha,
    Serializer,
    Visitor,
    rule,
)


class BakeMacrosOptions(PluginOptions):
    match: ListOption[str] = ListOption.parse_obj(["*"])
    macro: ListOption[str] = ListOption.parse_obj(["*"])


def beet_default(ctx: Context):
    ctx.require(bake_macros)


@configurable(validator=BakeMacrosOptions)
def bake_macros(ctx: Context, opts: BakeMacrosOptions):
    """Plugin for baking static macro invocations."""
    mc = ctx.inject(Mecha)
    mc.steps.insert(
        mc.steps.index(mc.transform) + 1,
        MacroBaker(
            match_spec=PathSpec.from_lines("gitwildmatch", opts.match.entries()),
            macro_spec=PathSpec.from_lines("gitwildmatch", opts.macro.entries()),
            database=mc.database,
            serialize=mc.serialize,
            generate=ctx.generate,
            parse_callback=mc.parse,
        ),
    )


class MacroBakerParseCallback(Protocol):
    """Callback required by the macro baker for parsing."""

    def __call__(
        self,
        source: TextFileBase[Any],
        *,
        preprocessor: Preprocessor,
    ) -> AstRoot:
        ...


@dataclass
class MacroInvocationArgument:
    """Argument provided to a static macro invocation."""

    entry: AstNbtCompoundEntry
    stringified: str


@dataclass
class MacroInvocation:
    """Static macro invocation."""

    file_instance: TextFileBase[Any]
    macro_path: str
    node: AstCommand
    arguments: Dict[str, MacroInvocationArgument]

    diagnostics: DiagnosticCollection = field(default_factory=DiagnosticCollection)
    arguments_usage: Dict[str, List[AstMacroLine]] = field(default_factory=dict)
    arguments_errors: Dict[str, Set[str]] = field(default_factory=dict)

    def add_usage(self, argument: str, node: AstMacroLine):
        self.arguments_usage.setdefault(argument, []).append(node)

    def add_error(self, argument: str, error_code: str):
        self.arguments_errors.setdefault(argument, set()).add(error_code)


@dataclass(eq=False)
class MacroBaker(Visitor):
    """Visitor for baking static macro invocations."""

    match_spec: PathSpec = required_field()
    macro_spec: PathSpec = required_field()

    database: CompilationDatabase = required_field()
    serialize: Serializer = required_field()
    generate: Generator = required_field()
    parse_callback: MacroBakerParseCallback = required_field()

    invocations: WeakKeyDictionary[TextFileBase[Any], MacroInvocation] = field(
        default_factory=WeakKeyDictionary
    )

    @rule(AstRoot)
    def bake_macros(self, node: AstRoot):
        invocation = self.invocations.get(self.database.current)

        result: List[AstCommand] = []
        modified = False

        for command in node.commands:
            if isinstance(command, AstMacroLine) and invocation:
                baked_macro_line = self.bake_macro_line(command, invocation)
                modified |= baked_macro_line is not command
                command = baked_macro_line

            args = command.arguments
            stack: List[AstCommand] = [command]

            while args and isinstance(subcommand := args[-1], AstCommand):
                stack.append(subcommand)
                args = subcommand.arguments

            last = stack[-1]

            if last.identifier == "function:name:arguments":
                last = self.bake_macro_invocation(last)
                if last is not stack.pop():
                    for prefix in reversed(stack):
                        args = AstChildren([*prefix.arguments[:-1], last])
                        last = replace(prefix, arguments=args)
                    modified = True
                    command = last

            result.append(command)

        if invocation:
            invocation_compilation_unit = self.database[invocation.file_instance]

            for name, errors in invocation.arguments_errors.items():
                diagnostics = DiagnosticCollection(
                    hint=invocation_compilation_unit.resource_location,
                    filename=invocation_compilation_unit.filename,
                    file=invocation.file_instance,
                )

                if "missing" in errors:
                    d = Diagnostic(
                        "error",
                        f'Missing argument "{name}" when baking macro "{invocation.macro_path}".',
                    )
                    diagnostics.add(set_location(d, invocation.node.arguments[1]))
                if "syntax" in errors:
                    d = Diagnostic(
                        "warn",
                        f'Argument "{name}" triggers a syntax error when baking macro "{invocation.macro_path}".',
                    )
                    diagnostics.add(set_location(d, invocation.arguments[name].entry))
                if "zero" in errors:
                    d = Diagnostic(
                        "error",
                        f'Argument "{name}" results in macro line with no command when baking macro "{invocation.macro_path}".',
                    )
                    diagnostics.add(set_location(d, invocation.arguments[name].entry))
                if "many" in errors:
                    d = Diagnostic(
                        "error",
                        f'Argument "{name}" results in macro line with more than one command when baking macro "{invocation.macro_path}".',
                    )
                    diagnostics.add(set_location(d, invocation.arguments[name].entry))

                macro_lines = "".join(
                    f"\n> {self.serialize(macro_line)}"
                    for macro_line in invocation.arguments_usage[name]
                )

                for exc in diagnostics.exceptions:
                    exc.notes.append(f"Required in macro line{macro_lines}")

                yield diagnostics

            for name, invocation_argument in invocation.arguments.items():
                if name not in invocation.arguments_usage:
                    d = Diagnostic(
                        "warn",
                        f'Unused argument "{name}" when baking macro "{invocation.macro_path}".',
                        hint=invocation_compilation_unit.resource_location,
                        filename=invocation_compilation_unit.filename,
                        file=invocation.file_instance,
                    )
                    yield set_location(d, invocation_argument.entry)

            yield invocation.diagnostics

        if modified:
            node = replace(node, commands=AstChildren(result))

        return node

    def bake_macro_line(self, node: AstMacroLine, invocation: MacroInvocation):
        result: List[str] = []
        source_mappings: list[SourceLocation] = []
        preprocessed_mappings: list[SourceLocation] = []
        preprocessed_location = INITIAL_LOCATION

        used_variables: List[AstMacroLineVariable] = []
        valid = True

        for argument in node.arguments:
            if isinstance(argument, AstMacroLineVariable):
                invocation.add_usage(argument.value, node)

                invocation_argument = invocation.arguments.get(argument.value)
                if not invocation_argument:
                    invocation.add_error(argument.value, "missing")
                    valid = False
                    continue

                used_variables.append(argument)

                result.append(invocation_argument.stringified)
                source_mappings.append(argument.location)
                preprocessed_mappings.append(preprocessed_location)
                preprocessed_location = preprocessed_location.skip_over(
                    invocation_argument.stringified
                )

            elif isinstance(argument, AstMacroLineText):
                result.append(argument.value)
                source_mappings.append(argument.location)
                preprocessed_mappings.append(preprocessed_location)
                preprocessed_location = preprocessed_location.skip_over(argument.value)

        if not valid:
            return node

        source = "".join(result)

        try:
            root = self.parse_callback(
                self.database.current,
                preprocessor=lambda _: (source, source_mappings, preprocessed_mappings),
            )

        except DiagnosticError as exc:
            syntax_error = exc.diagnostics.exceptions[0]
            syntax_error.notes.append(f"Failed to parse baked macro line\n> {source}")
            invocation.diagnostics.add(syntax_error)

            for argument in used_variables:
                if (
                    syntax_error.location < argument.end_location
                    and argument.location < syntax_error.end_location
                ):
                    invocation.add_error(argument.value, "syntax")

            return node

        else:
            if len(root.commands) == 1:
                return root.commands[0]

            for argument in used_variables:
                invocation.add_error(
                    argument.value, "many" if root.commands else "zero"
                )

            return node

    def bake_macro_invocation(self, node: AstCommand):
        current_file = self.database.current
        path = self.database[current_file].resource_location

        if (
            path
            and self.match_spec.match_file(path)
            and len(node.arguments) == 2
            and isinstance(name := node.arguments[0], AstResourceLocation)
            and self.macro_spec.match_file(macro_path := name.get_canonical_value())
            and isinstance(arguments := node.arguments[1], AstNbtCompound)
            and (macro_file := self.database.index.get(macro_path))
        ):
            invocation_arguments = {
                entry.key.value: MacroInvocationArgument(
                    entry=entry,
                    stringified=(
                        nbt_tag.unpack()
                        if isinstance(entry.value, AstNbtValue)
                        and isinstance(nbt_tag := entry.value.evaluate(), String)
                        else self.serialize(entry.value)
                    ),
                )
                for entry in arguments.entries
            }

            invocation_path = self.generate.format(
                macro_path + "/baked_{hash}",
                hash=sorted(
                    (k, v.stringified) for k, v in invocation_arguments.items()
                ),
            )

            if not self.database.index.get(invocation_path):
                invocation = Function(original=macro_file.original)
                self.generate(invocation_path, invocation)
                self.database[invocation] = replace(
                    self.database[macro_file],
                    resource_location=invocation_path,
                )
                self.database.enqueue(invocation, self.database.step)
                self.invocations[invocation] = MacroInvocation(
                    file_instance=current_file,
                    macro_path=macro_path,
                    node=node,
                    arguments=invocation_arguments,
                )

            name = set_location(AstResourceLocation.from_value(invocation_path), name)
            node = replace(
                node,
                identifier="function:name",
                arguments=AstChildren([name]),
            )

        return node
