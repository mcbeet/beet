from typing import Any

import click


class HelpColorsGroup(click.Group):
    def __init__(self, *args: Any, **kwargs: Any):
        ...


class HelpColorsCommand(click.Command):
    def __init__(self, *args: Any, **kwargs: Any):
        ...
