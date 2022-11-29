"""Plugin that loads translations from csv files.

Adapted from https://github.com/OrangeUtan/babelbox
Credit: Oran9eUtan <Oran9eUtan@gmail.com>
"""


__all__ = [
    "BabelboxOptions",
    "babelbox",
    "load_languages",
]


import logging
from csv import Dialect, DictReader, Sniffer
from glob import glob
from pathlib import Path
from typing import Dict, Optional, Type, Union

from beet import (
    Context,
    Language,
    ListOption,
    PackageablePath,
    PluginOptions,
    configurable,
)
from beet.core.utils import FileSystemPath

DialectLike = Union[str, Dialect, Type[Dialect]]


logger = logging.getLogger(__name__)


class BabelboxOptions(PluginOptions):
    load: ListOption[PackageablePath] = ListOption()
    dialect: Optional[str] = None
    namespace: str = "minecraft"
    filename_prefix: bool = False


def beet_default(ctx: Context):
    ctx.require(babelbox)


@configurable(validator=BabelboxOptions)
def babelbox(ctx: Context, opts: BabelboxOptions):
    """Plugin that loads translations from csv files."""
    namespace = ctx.assets[opts.namespace]

    for pattern in opts.load.entries():
        for path in glob(str(ctx.directory / pattern)):
            namespace.languages.merge(
                load_languages(
                    path=path,
                    dialect=opts.dialect,
                    prefix=Path(path).stem + "." if opts.filename_prefix else "",
                )
            )


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

        reader: DictReader[str] = DictReader(csv_file, dialect=dialect)

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
                    logger.warning(
                        'Locale "%s" has no translation for "%s".', code, identifier
                    )

        return languages
