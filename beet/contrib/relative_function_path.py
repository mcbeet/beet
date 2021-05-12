"""Plugin that resolves relative function paths within a namespace."""


import re
from pathlib import PurePosixPath

from beet import Context

REGEX_RELATIVE_PATH = re.compile(r"^(|.*\s)function\s+(\.\.?/\S+)(\s*)$")


def beet_default(ctx: Context):
    for path, function in ctx.data.functions.items():
        namespace, _, original_path = path.partition(":")
        current_dir = PurePosixPath(original_path).parent

        for i, line in enumerate(function.lines):
            if match := REGEX_RELATIVE_PATH.match(line):
                before, relative_path, after = match.groups()

                resolved = current_dir
                for name in relative_path.split("/"):
                    if name == "..":
                        resolved = resolved.parent
                    elif name and name != ".":
                        resolved = resolved / name

                function.lines[i] = f"{before}function {namespace}:{resolved}{after}"
