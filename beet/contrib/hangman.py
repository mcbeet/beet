"""Plugin that provides indentation-based syntactic extensions for functions.

With this plugin, commands can spread over multiple lines by using
hanging indents. Interspersed and trailing comments are hoisted above
the current command. The plugin tries its best to keep blank lines
and retain the original formatting of the function.

The plugin also supports the "run commands" syntax suggested here:
https://feedback.minecraft.net/hc/en-us/community/posts/360077450811-In-line-functions-in-mcfunction-files
"""


__all__ = [
    "HangmanOptions",
    "hangman",
    "parse_lines",
    "parse_trailing_comment",
    "fold_hanging_commands",
]


import logging
import re
from typing import Iterable, Iterator, List, Literal, Optional, Tuple

from beet import Context, Function, PluginOptions, configurable
from beet.toolchain.utils import stable_hash

logger = logging.getLogger(__name__)


REGEX_COMMENT = re.compile(r"(\s+#(?:\s+.*)?$)")
REGEX_QUOTE = re.compile(r"(\"(?:.*?[^\\])?\"|'(?:.*?[^\\])?')")
REGEX_EXECUTE_RUN = re.compile(
    r"(\s*execute\b(?:.*)\b)run\s+(commands|sequentially)(\s+\w+|)(\s*)"
)
REGEX_FOLD_COMMENT = re.compile(r"\s*#\s*fold\s*:\s*(\w+)\s*")


TokenType = Literal[
    "TEXT",
    "BLANK",
    "COMMENT",
    "INDENT",
    "DEDENT",
]
Token = Tuple[TokenType, str]


class HangmanOptions(PluginOptions):
    match: List[str] = []


def beet_default(ctx: Context):
    ctx.require(hangman)


@configurable(validator=HangmanOptions)
def hangman(ctx: Context, opts: HangmanOptions):
    """Plugin that provides indentation-based syntactic extensions for functions."""
    logger.warning("Deprecated in favor of mecha (https://github.com/mcbeet/mecha).")

    for path in ctx.data.functions.match(*opts.match):
        function = ctx.data.functions[path]
        function.lines = list(
            fold_hanging_commands(ctx, parse_lines(function.lines), path)
        )


def fold_hanging_commands(
    ctx: Context,
    tokens: Iterable[Token],
    original_function: str,
) -> Iterator[str]:
    """Fold hanging commands on a single line."""
    tokens = iter(tokens)

    current = ""
    indent_level = 0

    for token_type, value in tokens:
        if token_type == "DEDENT":
            indent_level -= 1
            if indent_level < 0:
                break

        elif token_type == "INDENT":
            if match := REGEX_EXECUTE_RUN.match(current):
                nested_commands = list(
                    fold_hanging_commands(ctx, tokens, original_function)
                )
                if match[2] == "commands":
                    name = match[3].strip() or stable_hash(nested_commands)
                    key = f"{original_function}/{name}"
                    ctx.data[key] = Function(nested_commands)
                    current = REGEX_EXECUTE_RUN.sub(rf"\1run function {key}\4", current)

                elif match[2] == "sequentially":
                    for nested_command in nested_commands:
                        yield REGEX_EXECUTE_RUN.sub(
                            rf"\1{nested_command[8:]}\4"
                            if nested_command.startswith("execute")
                            else rf"\1run {nested_command}\4",
                            current,
                        )
                    current = ""

            else:
                indent_level += 1

        else:
            if indent_level:
                if token_type == "TEXT":
                    current += " " + value
                elif token_type != "BLANK":
                    yield value
            else:
                if current:
                    yield current
                if token_type == "TEXT":
                    current = value
                else:
                    current = ""
                    yield value

    if current:
        yield current


def parse_lines(lines: Iterable[str]) -> Iterator[Token]:
    """Split the input lines into tokens."""
    indentation = [0]
    blanks: List[Token] = []
    fold_off = False

    for line in lines:
        if match := REGEX_FOLD_COMMENT.match(line):
            if match[1] in ["on", "off"]:
                fold_off = match[1] == "off"
            continue

        if fold_off:
            while len(indentation) > 1:
                yield "DEDENT", ""
                indentation.pop()
            yield from blanks
            blanks = []
            yield "TEXT", line
            continue

        stripped = line.lstrip()

        if not stripped:
            blanks.append(("BLANK", stripped))
            continue

        indent = len(line[: -len(stripped)].expandtabs())

        while indent < indentation[-1]:
            yield "DEDENT", ""
            indentation.pop()

        if indent > indentation[-1]:
            yield "INDENT", ""
            indentation.append(indent)

        yield from blanks
        blanks = []

        if stripped.startswith("#"):
            yield "COMMENT", stripped
        else:
            stripped, comment = parse_trailing_comment(stripped)
            if comment:
                yield "COMMENT", comment
            yield "TEXT", stripped

    while len(indentation) > 1:
        yield "DEDENT", ""
        indentation.pop()

    yield from blanks


def parse_trailing_comment(line: str) -> Tuple[str, Optional[str]]:
    """Split the line and return the extracted trailing comment."""
    chunks = REGEX_QUOTE.split(line)
    result = ""

    while chunks:
        text, *comment = REGEX_COMMENT.split(chunks.pop(0))
        result += text
        if comment:
            return result, comment[0].lstrip() + "".join(chunks)
        if chunks:
            result += chunks.pop(0)

    return result, None
