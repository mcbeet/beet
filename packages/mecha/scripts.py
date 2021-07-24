from pathlib import Path

import click
import mcwiki
from beet import Function

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


if __name__ == "__main__":
    cli()
