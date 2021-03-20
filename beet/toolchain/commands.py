import time
from typing import Optional, Sequence

import click

from beet import Project
from beet.toolchain.cli import beet, error_handler, message_fence

pass_project = click.make_pass_decorator(Project)


@beet.command()
@pass_project
@click.option(
    "-l",
    "--link",
    metavar="TARGET",
    help="Link the project before building.",
)
def build(project: Project, link: Optional[str]):
    """Build the current project."""
    text = "Linking and building project..." if link else "Building project..."
    with message_fence(text):
        if link:
            click.echo("\n".join(project.link(target=link)))
        project.build()


@beet.command()
@pass_project
@click.option(
    "-l",
    "--link",
    metavar="TARGET",
    help="Link the project before watching.",
)
@click.option(
    "-i",
    "--interval",
    metavar="SECONDS",
    default=0.6,
    help="Configure the polling interval.",
)
def watch(project: Project, link: Optional[str], interval: float):
    """Watch the project directory and build on file changes."""
    text = "Linking and watching project..." if link else "Watching project..."
    with message_fence(text):
        if link:
            click.echo("\n".join(project.link(target=link)))

        for changes in project.watch(interval):
            filename, action = next(iter(changes.items()))

            text = (
                f"{action.capitalize()} '{filename}'"
                if changes == {filename: action}
                else f"{len(changes)} changes detected"
            )

            now = time.strftime("%H:%M:%S")
            change_time = click.style(now, fg="green", bold=True)
            click.echo(f"{change_time} {text}")

            with error_handler(format_padding=1):
                project.build()


@beet.command()
@pass_project
@click.argument("patterns", nargs=-1)
@click.option(
    "-c",
    "--clear",
    is_flag=True,
    help="Clear the cache.",
)
def cache(project: Project, patterns: Sequence[str], clear: bool):
    """Inspect or clear the cache."""
    if clear:
        with message_fence("Clearing cache..."):
            if cache_names := ", ".join(project.clear_cache(patterns)):
                click.echo(f"Cache cleared successfully: {cache_names}.\n")
            else:
                click.echo(
                    "No matching results.\n"
                    if patterns
                    else "The cache is already cleared.\n"
                )
    else:
        with message_fence("Inspecting cache..."):
            click.echo(
                "\n".join(project.inspect_cache(patterns))
                or (
                    "No matching results.\n"
                    if patterns
                    else "The cache is completely clear.\n"
                )
            )


@beet.command()
@pass_project
@click.argument("target", required=False)
@click.option(
    "-c",
    "--clear",
    is_flag=True,
    help="Clear the link.",
)
def link(project: Project, target: Optional[str], clear: bool):
    """Link the generated resource pack and data pack to Minecraft."""
    if clear:
        with message_fence("Clearing project link..."):
            project.clear_link()
    else:
        with message_fence("Linking project..."):
            click.echo("\n".join(project.link(target)))
