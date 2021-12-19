"""Plugin that gathers statistics."""


__all__ = [
    "Analyzer",
    "Summary",
    "Statistics",
]


import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterator, List, Optional, Tuple, Union

from beet import Context
from beet.core.utils import dump_json
from pydantic import BaseModel

from mecha import (
    AstCommand,
    AstObjective,
    AstObjectiveCriteria,
    AstPlayerName,
    AstResourceLocation,
    AstRoot,
    AstSelector,
    AstWord,
    CommandSpec,
    Mecha,
    Reducer,
    rule,
)

logger = logging.getLogger("stats")


class Statistics(BaseModel):
    """Class holding all the stats gathered from the analysis."""

    function_count: int = 0
    command_count: DefaultDict[str, DefaultDict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    command_behind_execute_count: DefaultDict[str, int] = defaultdict(int)
    execute_count: int = 0
    execute_clause_count: DefaultDict[str, int] = defaultdict(int)
    selector_count: DefaultDict[str, int] = defaultdict(int)
    selector_entity_type_count: DefaultDict[str, int] = defaultdict(int)
    selector_argument_count: DefaultDict[str, DefaultDict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    scoreboard_references: DefaultDict[str, int] = defaultdict(int)
    scoreboard_fake_player_references: DefaultDict[
        str, DefaultDict[str, int]
    ] = defaultdict(lambda: defaultdict(int))
    scoreboard_objectives: Dict[str, str] = {}


class StatisticsOptions(BaseModel):
    output: Optional[str] = None


def beet_default(ctx: Context):
    ctx.inject(Analyzer)


class Analyzer(Reducer):
    """Service that collects command statistics."""

    stats: Statistics

    def __init__(self, ctx: Union[Context, Mecha, None] = None):
        super().__init__()

        if isinstance(ctx, Context):
            ctx.require(self.finalize)
            mc = ctx.inject(Mecha)
        else:
            mc = ctx

        if mc:
            mc.check.extend(self)

        self.stats = Statistics()

    def finalize(self, ctx: Context):
        mc = ctx.inject(Mecha)
        opts = ctx.validate("statistics", StatisticsOptions)
        yield
        logger.info(str(Summary(mc.spec, self.stats)))
        if opts.output:
            output = ctx.directory / opts.output
            output.write_text(dump_json(self.stats.dict()))

    @rule(AstRoot)
    def root(self, node: AstRoot):
        self.stats.function_count += 1

        for command in node.commands:
            behind_execute = False

            while command.identifier.startswith("execute"):
                behind_execute = True
                if command.identifier == "execute:subcommand":
                    self.stats.execute_count += 1
                else:
                    self.stats.execute_clause_count[command.identifier] += 1
                if isinstance(subcommand := command.arguments[-1], AstCommand):
                    command = subcommand
                else:
                    break

            name = command.identifier.partition(":")[0]
            self.stats.command_count[name][command.identifier] += 1

            if behind_execute:
                self.stats.command_behind_execute_count[name] += 1

    @rule(AstSelector)
    def selector(self, node: AstSelector):
        self.stats.selector_count[node.variable] += 1

        for argument in node.arguments:
            if (
                node.variable == "e"
                and argument.key.value == "type"
                and not argument.inverted
                and isinstance(entity_type := argument.value, AstResourceLocation)
            ):
                key = entity_type.get_canonical_value()
                self.stats.selector_entity_type_count[key] += 1
            self.stats.selector_argument_count[node.variable][argument.key.value] += 1

    @rule(AstObjective)
    def objective(self, node: AstObjective):
        self.stats.scoreboard_references[node.value] += 1

    @rule(AstCommand)
    def command(self, node: AstCommand):
        if (
            node.identifier.startswith("scoreboard:objectives:add:objective:criteria")
            and isinstance(objective := node.arguments[0], AstWord)
            and isinstance(criteria := node.arguments[1], AstObjectiveCriteria)
        ):
            self.stats.scoreboard_references[objective.value] += 1
            self.stats.scoreboard_objectives[objective.value] = criteria.value

        ref = None

        for argument in node.arguments:
            if isinstance(argument, AstPlayerName):
                ref = argument.value
            elif ref and isinstance(argument, AstObjective):
                objective = argument.value
                self.stats.scoreboard_fake_player_references[objective][ref] += 1
                ref = None


@dataclass
class Summary:
    """Formatted statistics summary."""

    spec: CommandSpec
    stats: Statistics

    indent: str = " " * 7

    def __str__(self) -> str:
        return "\n".join(self.format())

    def format(self) -> Iterator[str]:
        plural = "s" * (self.stats.function_count > 1)
        yield f"Analyzed {self.stats.function_count} function{plural}"
        results = {
            **self.format_commands(),
            **self.format_selectors(),
            **self.format_scoreboard(),
        }
        yield from self.format_table(results)

    def format_commands(self) -> Dict[Tuple[str, ...], List[Tuple[str, ...]]]:
        command_stats = {
            (
                f"/{prefix}",
                sum(stats.values()),
                self.stats.command_behind_execute_count[prefix],
            ): [
                (
                    f" {' ' * len(prefix)}{self.spec.prototypes[identifier].usage()[len(prefix):]}",
                    count,
                    0,
                )
                for identifier, count in stats.items()
            ]
            for prefix, stats in self.stats.command_count.items()
        }

        if self.stats.execute_count:
            command_stats[f"/execute", self.stats.execute_count, 0] = [
                (
                    f"         {self.spec.prototypes[clause].usage()}",
                    count,
                    0,
                )
                for clause, count in sorted(
                    self.stats.execute_clause_count.items(), key=lambda p: -p[1]
                )
            ]

        total_commands = sum(total for _, total, _ in command_stats)
        total_commands_behind_execute = sum(total for _, _, total in command_stats)
        total_commands -= total_commands_behind_execute

        return {
            (
                f"Total commands ({total_commands_behind_execute} behind execute)"
                if total_commands_behind_execute
                else "Total commands",
                str(total_commands),
            ): [
                (
                    f"{label} ({behind_execute} behind execute)"
                    if behind_execute
                    else label,
                    str(count),
                )
                for command, stats in sorted(
                    command_stats.items(), key=lambda p: -p[0][1]
                )
                for label, count, behind_execute in [command]
                + (list(sorted(stats, key=lambda p: -p[1])) if len(stats) > 1 else [])
            ],
        }

    def format_selectors(self) -> Dict[Tuple[str, ...], List[Tuple[str, ...]]]:
        selector_types = [
            (f"   [type={entity_type}]", entity_type_count)
            for entity_type, entity_type_count in sorted(
                self.stats.selector_entity_type_count.items(), key=lambda p: -p[1]
            )
        ]

        total_selector_types = sum(self.stats.selector_entity_type_count.values())

        if total_selector_types:
            selector_types.insert(0, ("@e with type", total_selector_types))

        if no_type_count := (self.stats.selector_count["e"] - total_selector_types):
            selector_types.insert(
                0, (f"@e with missing or inverted type", no_type_count)
            )

        selector_args = {
            selector: [(f"   [{arg}]", arg_count) for arg, arg_count in args.items()]
            for selector, args in self.stats.selector_argument_count.items()
        }

        return {
            ("Total selectors", str(sum(self.stats.selector_count.values()))): [
                row
                for selector, count in sorted(
                    self.stats.selector_count.items(), key=lambda p: -p[1]
                )
                if count
                for row in [(f"@{selector}", str(count))]
                + [
                    (arg, str(arg_count))
                    for arg, arg_count in sorted(
                        selector_args.get(selector, []), key=lambda p: -p[1]
                    )
                ]
            ]
            + [
                (entity_type, str(entity_type_count))
                for entity_type, entity_type_count in selector_types
            ],
        }

    def format_scoreboard(self) -> Dict[Tuple[str, ...], List[Tuple[str, ...]]]:
        objectives = {
            (
                f"{objective} ({criteria})"
                if (criteria := self.stats.scoreboard_objectives.get(objective))
                else objective,
                count,
            ): [
                (f"{' ' * len(objective)} {fake_player}", fake_player_count)
                for fake_player, fake_player_count in self.stats.scoreboard_fake_player_references[
                    objective
                ].items()
            ]
            for objective, count in self.stats.scoreboard_references.items()
        }

        return {
            ("Scoreboard objectives", str(len(self.stats.scoreboard_references))): [
                (label, str(count))
                for objective, fake_players in sorted(
                    objectives.items(), key=lambda p: -p[0][1]
                )
                for label, count in [objective]
                + list(sorted(fake_players, key=lambda p: -p[1]))
            ]
        }

    def format_table(
        self,
        sections: Dict[Tuple[str, ...], List[Tuple[str, ...]]],
    ) -> Iterator[str]:
        cols = self.compute_column_layout(sections)

        sep = "---".join("-" * col for col in cols)

        for header, rows in sections.items():
            yield sep
            yield self.format_row(header, cols, header=True)
            yield sep

            for row in rows:
                yield self.format_row(row, cols)

    def format_row(
        self,
        row: Tuple[str, ...],
        cols: List[int],
        header: bool = False,
    ) -> str:
        row = ((not header) * self.indent + row[0],) + row[1:]
        return " | ".join(
            (h.rjust(col) if h.isnumeric() else h.ljust(col))
            if len(h) < col
            else h[: col - 3] + "..."
            for h, col in zip(row, cols)
        )

    def compute_column_layout(
        self,
        sections: Dict[Tuple[str, ...], List[Tuple[str, ...]]],
    ) -> List[int]:
        column_count = max(map(len, sections))
        cols: List[int] = []

        for i in range(column_count):
            header_size = max(
                len(header[i]) if len(header) > i else 0 for header in sections
            )
            row_size = max(
                max(len(row[i]) if len(row) > i else 0 for row in rows) if rows else 0
                for rows in sections.values()
            )
            if i == 0:
                row_size += len(self.indent)
            cols.append(min(max(header_size, row_size) + 5, 70))

        return cols
