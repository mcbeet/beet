"""Plugin for handling data pack messages."""


__all__ = [
    "Message",
    "MsgFilter",
]


import json
import re
from dataclasses import dataclass
from typing import Optional

from beet import Context, JsonFile, NamespaceFile

PATH_REGEX = re.compile(r"\w+")


class Message(JsonFile, NamespaceFile):
    """Class representing a message file."""

    scope = ("messages",)
    extension = ".json"


def beet_default(ctx: Context):
    ctx.data.extend_namespace.append(Message)
    ctx.template.env.filters["msg"] = MsgFilter(ctx)  # type: ignore

    yield

    ctx.data[Message].clear()


@dataclass
class MsgFilter:
    """Jinja filter for including data pack messages."""

    ctx: Context

    def __call__(self, name: str, path: Optional[str] = None) -> str:
        message = self.ctx.data[Message][name].data

        if path:
            for key in PATH_REGEX.findall(path):
                if isinstance(message, list):
                    key = int(key)
                message = message[key]  # type: ignore

        return json.dumps(message)
