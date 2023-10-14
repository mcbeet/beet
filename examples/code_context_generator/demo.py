from beet import Context, Function, FunctionTag


def beet_default(ctx: Context):
    for i in range(5):
        key = ctx.generate(Function(["say hello"]))
        ctx.generate["foo"](Function([f"function {key}"]))

        with ctx.override(generate_namespace="demo"):
            ctx.generate(Function(["say demo"]))

            with ctx.override(generate_prefix="thing"):
                ctx.generate(Function(["say thing"]))

                with ctx.override(generate_path="other:{namespace}/"):
                    for j in range(3):
                        ctx.generate["foo"]("{incr}_{hash}", Function([f"say {i}{j}"]))

                with ctx.override(generate_path="{namespace}:generated/"):
                    key = ctx.generate("{short_hash}", Function([f"say {i}"]))

            with ctx.generate["a"].push():
                ctx.generate["b"](Function(["say c", f"function {key}"]))

        with ctx.override(generate_path="creeper{incr}:"):
            ctx.generate("boom", Function(["say boom"]))

        ctx.generate["nested"](
            "{hash}",
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

    func = ctx.generate(
        "hoisted:{namespace}/{path}{hash}",
        Function(["say hoisted"], tags=["minecraft:load"]),
    )

    for i in range(3):
        ctx.generate("hoisted:foo", merge=FunctionTag({"values": [f"demo:foo{i}"]}))
        ctx.generate("hoisted:abc", default=Function).append(f"function {func}")
        ctx.generate("hoisted:def", default=Function("say init")).prepend(f"say {i+1}")

    with ctx.generate.overlays["foo"].push():
        ctx.generate("bop{incr}", Function(["say hello"]))
    ctx.generate("bop{incr}", Function(["say goodbye"]))
