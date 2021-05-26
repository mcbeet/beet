"""Plugin that installs a Jinja extension for turning __foo__ into {{ foo }}."""


__all__ = [
    "DundervarExtension",
]


import re

from jinja2.lexer import Token, TokenStream, count_newlines

from beet import Context, JinjaExtension

REGEX_DUNDER = re.compile(r"\b__(\w+)__\b")


def beet_default(ctx: Context):
    ctx.template.env.add_extension(DundervarExtension)


class DundervarExtension(JinjaExtension):
    """A Jinja extension for interpolating variables surrounded by double underscores."""

    def filter_stream(self, stream: TokenStream):
        for token in stream:
            if token.type != "data":
                yield token
                continue

            pos = 0
            lineno = token.lineno

            while match := REGEX_DUNDER.search(token.value, pos):
                new_pos = match.start()

                if new_pos > pos:
                    preval = token.value[pos:new_pos]
                    yield Token(lineno, "data", preval)
                    lineno += count_newlines(preval)

                yield Token(lineno, "variable_begin", "")
                yield Token(lineno, "name", match[1])
                yield Token(lineno, "pipe", "|")
                yield Token(lineno, "name", "default")
                yield Token(lineno, "lparen", "(")
                yield Token(lineno, "string", match[0])
                yield Token(lineno, "rparen", ")")
                yield Token(lineno, "variable_end", "")

                pos = match.end()

            if pos < len(token.value):
                yield Token(lineno, "data", token.value[pos:])
