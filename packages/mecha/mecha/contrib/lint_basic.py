__all__ = [
    "BasicLinter",
]


from beet import Context
from tokenstream import set_location

from mecha import (
    AstCommand,
    AstSelector,
    Diagnostic,
    DiagnosticCollection,
    Mecha,
    Reducer,
    rule,
)


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.lint.extend(BasicLinter())


class BasicLinter(Reducer):
    """Linter with basic rules."""

    @rule(AstCommand, identifier="execute:subcommand")
    def execute_run(self, node: AstCommand):
        if isinstance(clause := node.arguments[0], AstCommand):
            if clause.identifier == "execute:run:subcommand":
                raise set_location(
                    Diagnostic("warn", "Redundant `execute run` clause."),
                    node,
                    clause.arguments[0].location.with_horizontal_offset(-1),
                )

    @rule(AstCommand, identifier="execute:run:subcommand")
    def run_execute(self, node: AstCommand):
        if isinstance(clause := node.arguments[0], AstCommand):
            if clause.identifier == "execute:subcommand":
                raise set_location(
                    Diagnostic("warn", "Redundant `run execute` clause."),
                    node,
                    clause.arguments[0].location.with_horizontal_offset(-1),
                )

    @rule(AstSelector)
    def selector_argument_order(self, node: AstSelector):
        order = [
            "type",
            "gamemode",
            "inverted gamemode",
            "team",
            "inverted team",
            "inverted type",
            "tag",
            "inverted tag",
            "name",
            "inverted name",
            "scores",
            "predicate",
            "inverted predicate",
            "advancements",
            "nbt",
        ]
        conflict = [-1] * len(order)

        with DiagnosticCollection() as diagnostics:
            for i, arg in enumerate(node.arguments):
                name = "inverted " * arg.inverted + arg.key.value

                try:
                    index = order.index(name)
                except ValueError:
                    continue

                j = conflict[index]

                if j >= 0:
                    bad_arg = node.arguments[j]
                    bad_arg_name = "inverted " * bad_arg.inverted + bad_arg.key.value

                    d = Diagnostic(
                        level="warn",
                        message=f"{name.capitalize()} argument should go before {bad_arg_name}.",
                    )

                    diagnostics.add(set_location(d, arg))

                for conflict_index in range(index):
                    if conflict[conflict_index] < 0:
                        conflict[conflict_index] = i
