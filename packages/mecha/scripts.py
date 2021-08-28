import click
import mcwiki
from beet import Function
from beet.core.utils import dump_json


@click.group()
def cli():
    """A collection of utilities for the project."""


@cli.command()
def download_command_examples():
    """Download command examples from the wiki."""
    generated_function = Function()

    commands = [
        "gamerule",
    ]

    ignored_examples = {
        "gamerule tntExplodes false",
    }

    for command in commands:
        page = mcwiki.load(f"commands/{command}")
        examples = page.get("examples")

        if examples is not None:
            for code in examples.extract_all(mcwiki.CODE):
                if code.startswith("/"):
                    code = code[1:]
                if code.startswith(command) and code not in ignored_examples:
                    generated_function.lines.append(code)

    click.echo(generated_function.text, nl=False)


@cli.command()
def download_argument_examples():
    """Download argument examples from the wiki."""
    page = mcwiki.load("argument types")
    section = page["java edition"]

    argument_examples = {
        argument_type: [
            {"examples": examples}
            for ul in documentation.html.select_one(".collapsible-content").select("ul")  # type: ignore
            if (examples := [example.string for example in ul.select("li > code")])  # type: ignore
        ]
        for argument_type, documentation in section.items()
    }

    click.echo(dump_json(argument_examples), nl=False)


if __name__ == "__main__":
    cli()
