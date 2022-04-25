<img align="right" src="https://raw.githubusercontent.com/mcbeet/mecha/main/logo.png" alt="logo" width="76">

# Mecha

[![GitHub Actions](https://github.com/mcbeet/mecha/workflows/CI/badge.svg)](https://github.com/mcbeet/mecha/actions)
[![PyPI](https://img.shields.io/pypi/v/mecha.svg)](https://pypi.org/project/mecha/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mecha.svg)](https://pypi.org/project/mecha/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Discord](https://img.shields.io/discord/900530660677156924?color=7289DA&label=discord&logo=discord&logoColor=fff)](https://discord.gg/98MdSGMm8j)

> A powerful Minecraft command library.

```python
from mecha import Mecha

mc = Mecha()

function = """
    execute
        as @a                        # For each "player",
        at @s                        # start at their feet.
        anchored eyes                # Looking through their eyes,
        facing 0 0 0                 # face perfectly at the target
        anchored feet                # (go back to the feet)
        positioned ^ ^ ^1            # and move one block forward.
        rotated as @s                # Face the direction the player
                                     # is actually facing,
        positioned ^ ^ ^-1           # and move one block back.
        if entity @s[distance=..0.6] # Check if we're close to the
                                     # player's feet.
        run
            say I'm facing the target!
"""

ast = mc.parse(function, multiline=True)
print(mc.serialize(ast))  # execute as @a at @s anchored eyes facing ...
```

## Introduction

This package provides everything you need for working with Minecraft commands in Python, whether you're looking to process commands or build abstractions on top.

### Features

- Extensible and version-agnostic `mcfunction` parser
- Clean, immutable and hashable abstract syntax tree with source location
- Command config resolver that flattens and enumerates all the valid command prototypes
- Powerful rule dispatcher for processing specific ast nodes
- Composable ast visitors and reducers
- Comes with useful syntactic extensions like relative locations, nesting and implicit execute
- Compile-time scripting with [Bolt](https://github.com/mcbeet/bolt), a subset of Python integrated into command syntax
- Rich function analyzer for keeping track of command statistics
- Execute arbitrary compilation passes in your [`beet`](https://github.com/mcbeet/beet) pipeline
- _(soon)_ Expressive command API for writing commands in Python

## Credits

- [A few test cases are adapted from `SPYGlass`](https://github.com/SPYGlassMC/SPYGlass)
- [Multiline example by `AjaxGb` (MCC discord)](https://discord.com/channels/154777837382008833/157097006500806656/539318174466703361)
- [Multiline syntax derived from the `hangman` plugin](https://github.com/mcbeet/beet/blob/main/beet/contrib/hangman.py)
- [Partially inspired by `Trident`](https://energyxxer.com/trident/)

## Installation

The package can be installed with `pip`.

```bash
$ pip install mecha
```

## Command-line utility

```bash
$ mecha --help
Usage: mecha [OPTIONS] [SOURCE]...

  Validate data packs and .mcfunction files.

Options:
  -m, --minecraft VERSION  Minecraft version.
  -l, --log LEVEL          Configure output verbosity.
  -s, --stats              Collect statistics.
  -j, --json FILENAME      Output json.
  -v, --version            Show the version and exit.
  -h, --help               Show this message and exit.
```

You can use the command-line utility to check data packs and function files for errors. The command arguments can be zipped and unzipped data packs, individual function files, and if you specify a directory that's not a data pack it will recursively grab all the `.mcfunction` files in the directory. You can use the `--minecraft` option to select between versions `1.16`, `1.17`, and `1.18`.

```bash
$ mecha path/to/my_data_pack
Validating with mecha vX.X.X

ERROR  | mecha  Expected curly '}' but got bracket ']'.
       | path/to/my_data_pack/data/demo/functions/foo.mcfunction:5:34
       |      4 |
       |      5 |  say hello @a[scores={foo=1, bar=2]
       |        :                                   ^

Error: Reported 1 error.
```

The `--stats` option will output a report that shows how many commands, selectors and scoreboards were used. You can also use the `--json` option to output the raw statistics in a json file.

```
INFO   | stats  Analyzed 1 function
       | -------------------------------------------------------------------------------
       | Total commands (1 behind execute)                                      |      4
       | -------------------------------------------------------------------------------
       |        /scoreboard                                                     |      3
       |                    objectives add <objective> <criteria>               |      1
       |                    players set <targets> <objective> <score>           |      1
       |                    players operation <targets> <targetObjective> <o... |      1
       |        /setblock (1 behind execute)                                    |      1
       |        /execute                                                        |      1
       |                 if score <target> <targetObjective> matches <range>... |      1
       |                 as <targets> <subcommand>                              |      1
       |                 run <subcommand>                                       |      1
       | -------------------------------------------------------------------------------
       | Total selectors                                                        |      3
       | -------------------------------------------------------------------------------
       |        @e                                                              |      2
       |           [tag]                                                        |      2
       |           [scores]                                                     |      1
       |        @s                                                              |      1
       |        @e with missing or inverted type                                |      2
       | -------------------------------------------------------------------------------
       | Scoreboard objectives                                                  |      2
       | -------------------------------------------------------------------------------
       |        my_consts (dummy)                                               |      3
       |                  10                                                    |      2
       |        foo                                                             |      3
```

## Github action

You can use `mecha` to check your data packs and function files for errors without having to install anything using the [`mcbeet/check-commands`](https://github.com/mcbeet/check-commands) github action.

```yml
# .github/workflows/check-commands.yml
name: Check commands
on: [push]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: mcbeet/check-commands@v1
        with:
          source: .
```

This allows you to make sure that your commands don't contain any error when you push to your repository. For more details check out the [action README](https://github.com/mcbeet/check-commands#usage).

## Contributing

Contributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org/).

```bash
$ poetry install
```

You can run the tests with `poetry run pytest`.

```bash
$ poetry run pytest
```

The project must type-check with [`pyright`](https://github.com/microsoft/pyright). If you're using VSCode the [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension should report diagnostics automatically. You can also install the type-checker locally with `npm install` and run it from the command-line.

```bash
$ npm run watch
$ npm run check
```

The code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).

```bash
$ poetry run isort mecha tests
$ poetry run black mecha tests
$ poetry run black --check mecha tests
```

---

License - [MIT](https://github.com/mcbeet/mecha/blob/main/LICENSE)
