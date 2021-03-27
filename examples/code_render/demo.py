from beet import Context, Function


def beet_default(ctx: Context):
    ctx.require("beet.contrib.inline_function")
    ctx.require("beet.contrib.inline_function_tag")

    ctx.data["demo:hello"] = ctx.template.render_file(
        Function(
            """
            function #demo:thing

            #!function "demo:implementation_detail"
                #!tag "demo:thing"

                say this is an implementation detail
            #!endfunction
            """
        )
    )
