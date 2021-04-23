from beet import Context, Function, FunctionTag


def beet_default(ctx: Context):
    ctx.require("beet.contrib.inline_function_tag")

    ctx.generate(render=Function(["say {{ 6 * 7 }}"]))
    ctx.generate("foo", render=Function(source_path="foo.mcfunction"), message="hello")

    ctx.require(plugin1)

    with ctx.override(generate_namespace="other"):
        ctx.generate["thing"](
            render=Function(
                ['#!include "foo.mcfunction"'],
                tags=[ctx.generate(FunctionTag())],
            ),
            message="world",
        )


def plugin1(ctx: Context):
    ctx.require(plugin2)

    for i in range(5):
        with ctx.generate[f"part{i}"].push():
            loop = ctx.generate(
                "{short_hash}",
                render=Function(source_path=ctx.directory / "main.mcfunction"),
                hash=i,
                count=i + 1,
            )

            ctx.generate("init", render=Function(["function {{ loop }}"]), loop=loop)


def plugin2(ctx: Context):
    with ctx.override(generate_prefix="nested"):
        yield
