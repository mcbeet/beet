"""Plugin that loads translations from csv files.

Adapted from https://github.com/OrangeUtan/babelbox
Credit: Oran9eUtan <Oran9eUtan@gmail.com>
"""


__all__ = [
    "babelbox",
    "load_languages",
]


import logging
from csv import Dialect, DictReader, Sniffer
from typing import Dict, Iterable, Optional, Type, Union, cast

from beet import Context, Language, Plugin
from beet.core.utils import FileSystemPath, JsonDict

DialectLike = Union[str, Dialect, Type[Dialect]]


logger = logging.getLogger(__name__)


def beet_default(ctx: Context):
    config = ctx.meta.get("babelbox", cast(JsonDict, {}))

    load = config.get("load", ())
    dialect = config.get("dialect")
    filename_prefix = config.get("filename_prefix", False)

    ctx.require(babelbox(load, dialect, filename_prefix))


def babelbox(
    load: Iterable[str] = (),
    dialect: Optional[str] = None,
    filename_prefix: bool = False,
) -> Plugin:
    """Return a plugin that loads translations from csv files."""

    def plugin(ctx: Context):
        minecraft = ctx.assets["minecraft"]

        for pattern in load:
            for path in ctx.directory.glob(pattern):
                minecraft.languages.merge(
                    load_languages(
                        path=path,
                        dialect=dialect,
                        prefix=path.stem + "." if filename_prefix else "",
                    )
                )

    return plugin


def load_languages(
    path: FileSystemPath,
    dialect: Optional[DialectLike] = None,
    prefix: str = "",
) -> Dict[str, Language]:
    """Return a dictionnary mapping each column to a language file."""
    with open(path, newline="") as csv_file:
        if not dialect:
            dialect = Sniffer().sniff(csv_file.read(1024))
            csv_file.seek(0)

        reader = DictReader(csv_file, dialect=dialect)

        key, *language_codes = reader.fieldnames or [""]
        languages = {code: Language() for code in language_codes}

        for row in reader:
            if not (identifier := row[key]):
                continue

            identifier = prefix + identifier

            for code in language_codes:
                if value := row[code]:
                    languages[code].data[identifier] = value
                else:
                    msg = f"Locale {code!r} has no translation for {identifier!r}"
                    logger.warning(msg)

        return languages
