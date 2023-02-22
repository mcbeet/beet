"""Plugin for handling data pack messages."""


__all__ = [
    "Message",
    "MessageManager",
]


import json
import re
from dataclasses import dataclass
from typing import Any, ClassVar, Optional

from beet import Context, JsonFileBase
from beet.core.utils import TextComponent

PATH_REGEX = re.compile(r"\w+")


class Message(JsonFileBase[TextComponent]):
    """Class representing a message file."""

    scope: ClassVar[tuple[str, ...]] = ("messages",)
    extension: ClassVar[str] = ".json"


def beet_default(ctx: Context):
    messages = ctx.inject(MessageManager)
    ctx.template.env.filters["msg"] = messages.get_as_string  # type: ignore


@dataclass
class MessageManager:
    """Service for managing json messages."""

    ctx: Context

    def __post_init__(self):
        self.ctx.require(self.cleanup)
        self.ctx.data.extend_namespace.append(Message)

    def get(self, name: str, path: Optional[str] = None) -> TextComponent:
        """Retrieve a message."""
        message: Any = self.ctx.data[Message][name].data

        if path:
            for key in PATH_REGEX.findall(path):
                match message:
                    case list():
                        message = message[int(key)]
                    case dict():
                        message = message[key]
                    case _:
                        raise KeyError(
                            "Tried to index into a JSON element that isn't an object or a list"
                        )

        return message

    def get_as_string(self, name: str, path: Optional[str] = None) -> str:
        """Retrieve a message and serialize it."""
        return json.dumps(self.get(name, path))

    def cleanup(self, ctx: Context):
        """Plugin that removes all messages at the end of the build."""
        yield
        ctx.data[Message].clear()
