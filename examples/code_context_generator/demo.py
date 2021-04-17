from beet import Context, Function


def beet_default(ctx: Context):
    for i in range(5):
        key = ctx.generate(Function(["say hello"]))
        ctx.generate["foo"](Function([f"function {key}"]))

        with ctx.override(generate_namespace="demo"):
            ctx.generate(Function(["say demo"]))

            with ctx.override(generate_prefix="thing"):
                ctx.generate(Function(["say thing"]))

                with ctx.override(generate_format="other:{namespace}/{incr}_{hash}"):
                    for j in range(3):
                        ctx.generate["fish"]["zombie"](Function([f"say {i}{j}"]))

                key = ctx.generate(
                    "{namespace}:generated/{short_hash}", Function([f"say {i}"])
                )

            ctx.generate["a"]["b"](Function(["say c", f"function {key}"]))

        ctx.generate("creeper{incr}:boom", Function(["say boom"]))

        ctx.generate["nested"](
            "{namespace}:{path}{hash}",
            Function(["say hello"]),
            hash=f"something/other thing, {i} blah",
        )

    tag1 = ctx.generate.id("foo")
    obj1 = ctx.generate.hash("foo")
    ctx.generate(Function([f"scoreboard players set @s[tag={tag1}] {obj1} 1"]))

    generate = ctx.generate["hello"]

    tag2 = generate.id("foo")
    obj2 = generate.hash("foo")
    generate(Function([f"scoreboard players set @s[tag={tag2}] {obj2} 1"]))
