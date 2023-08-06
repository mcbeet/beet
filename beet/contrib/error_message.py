"""Plugin for raising an error message."""


__all__ = [
    "error_message",
    "ErrorMessageOptions",
]


from beet import Context, ErrorMessage, PluginOptions, configurable


class ErrorMessageOptions(PluginOptions):
    message: str


def beet_default(ctx: Context):
    ctx.require(error_message)


@configurable(validator=ErrorMessageOptions)
def error_message(ctx: Context, opts: ErrorMessageOptions):
    """Plugin for raising an error message."""
    raise ErrorMessage(opts.message)
