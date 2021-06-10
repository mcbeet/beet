from beet import Context, Function


def beet_default(ctx: Context):
    function_path = ctx.cache.generated.directory / "foo.mcfunction"

    if not function_path.is_file():
        function_path.write_text("say hello\n")

    ctx.data["demo:foo"] = Function(source_path=function_path)
