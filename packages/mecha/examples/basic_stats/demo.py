from beet import Context

from mecha import Mecha
from mecha.contrib.statistics import Analyzer, Summary


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    analyzer = ctx.inject(Analyzer)
    summary = Summary(mc.spec, analyzer.stats)
    header = [f"# {line}" for line in str(summary).splitlines()]
    ctx.data.functions["demo:foo"].prepend(header)
