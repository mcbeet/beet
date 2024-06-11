from beet import Context, Function


def beet_default(ctx: Context):
    message = "potato"

    with ctx.generate.draft() as draft:
        draft.data["demo:foo"] = Function(["say hello"])

    with ctx.generate.draft() as draft:
        draft.cache("demo", f"{message=}", zipped=True)
        draft.data["demo:message"] = Function([f"say {message}"])

    ctx.data.function["demo:message"].lines *= 2
