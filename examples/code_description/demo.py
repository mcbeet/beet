from beet import Context


def beet_default(ctx: Context):
    ctx.project_id = "something_else"
    ctx.project_name = "Something else"
    ctx.project_description = {"text": "bold description", "bold": True}
    ctx.project_author = "Fizzy"
    ctx.project_version = "1.2.3"

    ctx.data.description = ["override for ", {"text": "data pack", "color": "red"}]
