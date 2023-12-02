__all__ = [
    "VanillaFilesDirective",
    "VanillaMatchDirective",
]


from dataclasses import dataclass
from typing import Union

from beet import Context, DataPack, PackQuery, ResourcePack
from beet.contrib.vanilla import Vanilla

from lectern import Document, Fragment, InvalidFragment


def beet_default(ctx: Context):
    vanilla = ctx.inject(Vanilla)
    document = ctx.inject(Document)
    document.directives["vanilla"] = VanillaFilesDirective(vanilla, ctx.query)
    for file_type in ctx.get_file_types():
        document.directives[f"vanilla_{file_type.snake_name}"] = VanillaMatchDirective(
            file_type.snake_name, vanilla, ctx.query
        )


@dataclass
class VanillaFilesDirective:
    vanilla: Vanilla
    query: PackQuery[Union[ResourcePack, DataPack]]

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        release = self.vanilla.releases[
            fragment.modifier or self.vanilla.minecraft_version
        ]

        if not fragment.arguments:
            raise InvalidFragment(
                "Missing arguments for directive @vanilla.", fragment.start_line
            )

        head, *tail = fragment.arguments

        client_jar = release.client_jar
        query = self.query.from_pack(client_jar.assets, client_jar.data).prepare(
            files={head[:-1]: tail} if head.endswith(":") else fragment.arguments
        )

        for base_path in query.analyze_base_paths():
            release.mount(base_path, fetch_objects=True)

        query.copy_to(assets, data)


@dataclass
class VanillaMatchDirective:
    group: str
    vanilla: Vanilla
    query: PackQuery[Union[ResourcePack, DataPack]]

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        release = self.vanilla.releases[
            fragment.modifier or self.vanilla.minecraft_version
        ]

        args = fragment.arguments or ["*"]
        head, *tail = args

        client_jar = release.client_jar
        query = self.query.from_pack(client_jar.assets, client_jar.data).prepare(
            match={self.group: {head[:-1]: tail} if head.endswith(":") else args}
        )

        for base_path in query.analyze_base_paths():
            release.mount(base_path, fetch_objects=True)

        query.copy_to(assets, data)
