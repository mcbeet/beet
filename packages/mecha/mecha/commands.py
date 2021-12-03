import os

import click
from beet import ErrorMessage, Project
from beet.toolchain.cli import beet, echo

from mecha import AstCacheBackend

pass_project = click.make_pass_decorator(Project)  # type: ignore


@beet.command()
@pass_project
@click.argument("filename", type=click.Path(exists=True, dir_okay=False))
def ast(project: Project, filename: str):
    """Inspect cached mecha ast."""
    filename = os.path.relpath(filename, project.directory)
    ast_path = project.cache["mecha"].get_path(f"{filename}-ast")

    try:
        with ast_path.open("rb") as f:
            echo(AstCacheBackend().load(f).dump())
    except FileNotFoundError as exc:
        raise ErrorMessage(f"No cached ast for {filename!r}.") from exc
