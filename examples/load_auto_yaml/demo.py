import json

from pydantic import BaseModel

from beet import Context, DataPack, Drop, FileDeserialize, Function, JsonFileBase


class Options(BaseModel):
    greeting: str
    color: str = "yellow"


class MessageConfig(JsonFileBase[Options]):
    model = Options

    options = FileDeserialize[Options]()

    def bind(self, pack: DataPack, path: str):
        super().bind(pack, path)
        message = {"text": self.options.greeting, "color": self.options.color}

        pack["message:greet"] = Function(
            [f"tellraw @a {json.dumps(message)}"],
            tags=["minecraft:load"],
        )

        raise Drop()


def installation_message(ctx: Context):
    ctx.data.extend_extra["message.json"] = MessageConfig
