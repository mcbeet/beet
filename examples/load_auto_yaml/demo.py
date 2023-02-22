import json

from pydantic import BaseModel

from beet import Context, DataPack, Drop, Function, JsonFileBase


class MessageData(BaseModel):
    greeting: str
    color: str = "yellow"


class MessageConfig(JsonFileBase[MessageData]):
    def bind(self, pack: DataPack, path: str):
        super().bind(pack, path)
        message = {"text": self.data.greeting, "color": self.data.color}

        pack["message:greet"] = Function(
            [f"tellraw @a {json.dumps(message)}"],
            tags=["minecraft:load"],
        )

        raise Drop()


def installation_message(ctx: Context):
    ctx.data.extend_extra["message.json"] = MessageConfig
