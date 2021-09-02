from typing import Optional

import click
import mcwiki
from beet import Function
from beet.core.utils import dump_json
from bs4 import BeautifulSoup, Tag
from mcwiki.utils import normalize_string


class JavaExampleExtractor(mcwiki.TextExtractor):
    def scan(  # type: ignore
        self,
        html: BeautifulSoup,
        limit: Optional[int] = None,
    ) -> mcwiki.ScanResult["JavaExampleExtractor", str]:
        result = super().scan(html, limit=limit)
        result.elements[:] = [
            element
            for element in result.elements
            if not (
                isinstance(element, Tag)
                and (
                    any(
                        parent.get_text().startswith(
                            ("Bedrock Edition:", "In Bedrock Edition")
                        )
                        for parent in element.find_parents("li")
                    )
                    or element.parent
                    and (sup := element.parent.find("sup"))
                    and (annotation := sup.get_text().lower())  # type: ignore
                    and (
                        "[be only]" in annotation
                        or "[bedrock edition only]" in annotation
                    )
                )
            )
        ]
        return result


@click.group()
def cli():
    """A collection of utilities for the project."""


@cli.command()
def download_command_examples():
    """Download command examples from the wiki."""
    generated_function = Function()

    commands = [
        "advancement",
        "attribute",
        "clear",
        "data",
        "defaultgamemode",
        "effect",
        "enchant",
        # "execute",
        "experience",
        "fill",
        "function",
        "gamemode",
        "gamerule",
        "give",
        "item",
        "kill",
        "locate",
        "msg",
        # "particle",
        "setblock",
        "spreadplayers",
        "summon",
        "teleport",
        "tellraw",
        "time",
        "title",
        "weather",
    ]

    java_example = JavaExampleExtractor("li code")

    for command in commands:
        page = mcwiki.load(f"commands/{command}")
        examples = page.get("examples")

        if examples is not None:
            generated_function.append(f"# {command}")
            for code in examples.extract_all(java_example):
                if code.startswith("/"):
                    code = code[1:]
                if code.startswith(command):
                    generated_function.append(code)

    click.echo(generated_function.text, nl=False)


@cli.command()
def download_argument_examples():
    """Download argument examples from the wiki."""
    page = mcwiki.load("argument types")
    section = page["java edition"]

    argument_examples = {
        argument_type: [
            {"examples": examples}
            for ul in documentation.html.select(".collapsible-content > ul")  # type: ignore
            if not (ul.parent and (p := ul.parent.find_previous_sibling("p")) and not p.get_text().startswith("Official examples")) and (examples := [normalize_string(example.string) for example in ul.select("li > code")])  # type: ignore
        ]
        for argument_type, documentation in section.items()
    }

    click.echo(dump_json(argument_examples), nl=False)


if __name__ == "__main__":
    cli()
