from pathlib import Path

import click
import mcwiki
from beet import Function
from beet.core.utils import dump_json

PROJECT_DIRECTORY = Path(__file__).parent


@click.group()
def cli():
    """A collection of utilities for the project."""


@cli.command()
def download_wiki_examples():
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

    generated_function.dump(
        PROJECT_DIRECTORY / "mecha/resources",
        "wiki_examples.mcfunction",
    )


@cli.command()
def download_wiki_argument_types():
    """Download argument type examples from the wiki."""
    page = mcwiki.load("argument types")
    section = page["java edition"]

    examples = mcwiki.TextExtractor(".collapsible-content > ul > li > code")
    output_file = PROJECT_DIRECTORY / "mecha/resources/wiki_argument_types.json"

    output_file.write_text(
        dump_json(
            {
                argument_type: list(documentation.extract_all(examples))
                for argument_type, documentation in section.items()
            }
        )
    )


if __name__ == "__main__":
    cli()
