from pathlib import Path

import click
from beet import ErrorMessage, Project
from beet.toolchain.cli import beet

from mecha import AstCacheBackend

pass_project = click.make_pass_decorator(Project)  # type: ignore


@beet.command()
@pass_project
@click.argument("filename", type=click.Path(exists=True, dir_okay=False))
def ast(project: Project, filename: str):
    """Inspect cached mecha ast."""
    source_path = Path(filename).resolve()
    ast_path = project.cache["mecha"].get_path(f"{source_path}-ast")

    try:
        with ast_path.open("rb") as f:
            click.echo(AstCacheBackend().load(f).dump())
    except FileNotFoundError as exc:
        raise ErrorMessage(f'No cached ast for "{filename}".') from exc
