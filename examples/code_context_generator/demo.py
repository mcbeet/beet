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
