import os
from pathlib import Path
from pprint import pformat
from typing import Iterable, Optional, Tuple

import click
from beet import Project
from beet.core.utils import format_directory
from beet.toolchain.cli import beet, message_fence

from bolt import AstMemo, MemoRegistry, MemoStorage

pass_project = click.make_pass_decorator(Project)  # type: ignore


@beet.command()
@pass_project
@click.option(
    "-c",
    "--clear",
    is_flag=True,
    help="Clear cached memo.",
)
@click.option(
    "--gc",
    is_flag=True,
    help="Garbage-collect unused invocations.",
)
@click.option(
    "--gc-interval",
    type=int,
    help="Set garbage collection interval.",
)
@click.option(
    "--gc-max-age",
    type=int,
    help="Set garbage collection max age.",
)
@click.argument(
    "filenames",
    nargs=-1,
)
def memo(
    project: Project,
    clear: bool,
    gc: bool,
    gc_interval: Optional[int],
    gc_max_age: Optional[int],
    filenames: Tuple[str, ...],
):
    """Inspect and manage bolt memo storage."""
    memo_registry = MemoRegistry(project.cache)

    if gc_interval is not None or gc_max_age is not None:
        if clear or gc or filenames:
            raise click.UsageError(
                "GC settings must be provided without any other argument.",
            )
        with message_fence("Updating GC settings..."):
            if gc_interval is not None:
                memo_registry.gc_interval = gc_interval
                click.echo(
                    f"Set garbage collection interval to {gc_interval} epoch{(gc_interval > 1) * 's'}.\n"
                )
            if gc_max_age is not None:
                memo_registry.gc_max_age = gc_max_age
                click.echo(
                    f"Set garbage collection max age to {gc_max_age} epoch{(gc_max_age > 1) * 's'}.\n"
                )
            project.cache.flush()
            return

    keys = [
        str(path) if (path := Path(filename).resolve()).is_file() else filename
        for filename in filenames
    ] or list(memo_registry.keys())

    with message_fence(
        "Clearing memo..."
        if clear
        else "Running garbage collection..."
        if gc
        else "Inspecting memo..."
    ):
        if not keys:
            click.echo("The memo registry is empty.\n")
            return

        if clear:
            for key in keys:
                click.echo(
                    f'Clear memo for "{os.path.relpath(key, project.directory)}".\n'
                )
                del memo_registry[key]
            memo_registry.flush()
            project.cache.flush()
            return

        if gc:
            for memo_id, state_id in memo_registry.garbage_collect(*keys):
                click.echo(f'GC "{memo_id.hex}/{hex(state_id)}".\n')
            memo_registry.flush()
            project.cache.flush()
            return

        n = len(keys)
        click.echo(f"Looking up {n} file{(n > 1) * 's'} in the registry.\n")

        for key in keys:
            memo_file_index = memo_registry[key]
            if not memo_file_index:
                click.echo(
                    f'No entries associated with "{os.path.relpath(key, project.directory)}".\n'
                )
                continue

            click.echo(
                os.path.relpath(key, project.directory) if os.path.isabs(key) else key
            )

            for key, storage in memo_file_index.items():
                if isinstance(key, tuple):
                    click.echo("  |")
                    for line in generate_summary(project.directory, key[0], storage):
                        click.echo(f"  |  {line}".rstrip())

            click.echo()


def generate_summary(
    project_directory: Path,
    memo: AstMemo,
    storage: MemoStorage,
) -> Iterable[str]:
    yield f"line {storage.memo_lineno}:"
    yield f"  id = {storage.memo_id.hex}"

    yield ""
    yield from memo.dump(
        prefix="  ",
        shallow=True,
        exclude={"location", "end_location", "persistent_id"},
    ).splitlines()

    yield ""
    yield "  invocations ="

    if not storage:
        yield "    None"
        return

    for variable, invocation in storage.items():
        for line in pformat(variable).splitlines():
            yield f"    {line}"
        yield f"      cached = {invocation.cached}"
        yield f"      epoch = {invocation.epoch}"

        directory = invocation.locate_directory()

        if directory and directory.is_dir():
            yield f"      directory = {os.path.relpath(directory, project_directory)}"
            for line in format_directory(directory):  # type: ignore
                yield f"        {line}"
        else:
            yield f"      directory = None"
