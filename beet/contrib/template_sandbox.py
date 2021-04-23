"""Plugin that configures the sandboxed jinja environment."""


from jinja2.sandbox import SandboxedEnvironment

from beet import Context


def beet_default(ctx: Context):
    ctx.template.reset_environment(SandboxedEnvironment)
