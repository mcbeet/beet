from dataclasses import dataclass, field

from beet import Context, Function

from mecha import AstObjective, Mecha, Reducer, rule


@dataclass
class ObjectiveCollector(Reducer):
    objectives: set[str] = field(default_factory=set)

    @rule(AstObjective)
    def objective(self, node: AstObjective):
        self.objectives.add(node.value)


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    objective_collector = ObjectiveCollector()
    mc.check.extend(objective_collector)
    yield
    ctx.generate(Function([f"say {', '.join(sorted(objective_collector.objectives))}"]))
