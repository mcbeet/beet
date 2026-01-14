from beet import Context, subproject

from .resources import UiScreen


def beet_default(ctx: Context):
    all_screens = {
        name: screen_file.text for name, screen_file in ctx.data[UiScreen].items()
    }
    ctx.data[UiScreen].clear()

    ctx.require(
        subproject(
            {
                "require": ["bolt"],
                "data_pack": {"load": {"data/sample_ui/modules": "@sample_ui/modules"}},
                "pipeline": ["mecha"],
                "meta": {
                    "bolt": {"entrypoint": "sample_ui:main"},
                    "sample_ui": {"all_screens": all_screens},
                },
            }
        )
    )
