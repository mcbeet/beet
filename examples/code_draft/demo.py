from beet import Context, Function


def beet_default(ctx: Context):
    message = "potato"

    draft = ctx.generate.draft()
    draft.data["demo:foo"] = Function(["say hello"])
    draft.apply()

    for draft in ctx.generate.draft().cache("demo_draft", f"{message=}", apply=True):
        draft.data["demo:message"] = Function([f"say {message}"])

    ctx.data.functions["demo:message"].lines *= 2
