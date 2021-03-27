import json
from pathlib import Path

from pytest_insta import Fmt

from beet import DataPack, ProjectConfig, ResourcePack
from beet.core.utils import dump_json
from beet.library.test_utils import ignore_name


class FmtResourcePack(Fmt[ResourcePack]):
    extension = ".resource_pack"

    def load(self, path: Path) -> ResourcePack:
        return ignore_name(ResourcePack(path=path))

    def dump(self, path: Path, value: ResourcePack):
        value.save(path=path, overwrite=True)


class FmtDataPack(Fmt[DataPack]):
    extension = ".data_pack"

    def load(self, path: Path) -> DataPack:
        return ignore_name(DataPack(path=path))

    def dump(self, path: Path, value: DataPack):
        value.save(path=path, overwrite=True)


class FmtConfig(Fmt[ProjectConfig]):
    extension = ".beet-config"

    def load(self, path: Path) -> ProjectConfig:
        config = ProjectConfig(**json.loads(path.read_text()))
        self.fix_paths(config)
        return config

    def dump(self, path: Path, value: ProjectConfig):
        path.write_text(dump_json(value.dict()))

    def fix_paths(self, config: ProjectConfig):
        if config.directory:
            config.directory = str(Path(config.directory))
        if config.output:
            config.output = str(Path(config.output))

        config.data_pack.load = [str(Path(p)) for p in config.data_pack.load]
        config.resource_pack.load = [str(Path(p)) for p in config.resource_pack.load]
        config.templates = [str(Path(p)) for p in config.templates]

        for entry in config.pipeline:
            if isinstance(entry, ProjectConfig):
                self.fix_paths(entry)
