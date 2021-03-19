<img align="right" src="https://raw.githubusercontent.com/mcbeet/beet/main/logo.png?sanitize=true" alt="logo" width="76">

# Beet

[![GitHub Actions](https://github.com/mcbeet/beet/workflows/CI/badge.svg)](https://github.com/mcbeet/beet/actions)
[![PyPI](https://img.shields.io/pypi/v/beet.svg)](https://pypi.org/project/beet/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beet.svg)](https://pypi.org/project/beet/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

> The Minecraft pack development kit.

## Introduction

Minecraft [resource packs](https://minecraft.gamepedia.com/Resource_Pack) and [data packs](https://minecraft.gamepedia.com/Data_Pack) work well as _distribution_ formats but can be pretty limiting as _authoring_ formats. Without the ability to parametrize or create abstractions over assets and data pack resources, projects and libraries created by the community are greatly limited when it comes to reusability and interoperability.

There's been a lot of attempts at establishing standardized tooling to improve the development experience and it's becoming more and more apparent that the problem space is fundamentally multi-paradigm. Different problems require different solutions, so providing unified cross-project reusability needs to involve an interoperability layer that's sufficiently unopinionated to let all these paradigms shine through.

The `beet` project is meant to serve as a platform for building a cooperative tooling ecosystem by providing a flexible composition model and a user-friendly development workflow.

### Screencasts

- **Quick start** [https://youtu.be/JGrJTOhG3pY](https://youtu.be/JGrJTOhG3pY)
- **Command-line** [https://youtu.be/fQ9up0ELPNE](https://youtu.be/fQ9up0ELPNE)
- **Library overview** [https://youtu.be/LDvV4_l-PSc](https://youtu.be/LDvV4_l-PSc)
- **Plugins basics** [https://youtu.be/XTzKmvHqd1g](https://youtu.be/XTzKmvHqd1g)
- **Pipeline configuration** [https://youtu.be/QsnQncGxAAs](https://youtu.be/QsnQncGxAAs)

### Library

> [Documentation](https://mcbeet.dev/library/)

```python
from beet import ResourcePack, Texture

# Open a zipped resource pack and add a custom stone texture
with ResourcePack(path="stone.zip") as assets:
    assets["minecraft:block/stone"] = Texture(source_path="custom.png")
```

The `beet` library provides carefully crafted primitives for working with Minecraft resource packs and data packs.

- Create, read, edit and merge resource packs and data packs
- Handle zipped and unzipped packs
- Fast and lazy by default, files are transparently loaded when needed
- Statically typed API enabling rich intellisense and autocompletion

### Toolchain

> [Documentation](https://mcbeet.dev/toolchain/)

```python
from beet import Context, Function

def greet(ctx: Context):
    """Plugin that adds a function for greeting the player."""
    ctx.data["greet:hello"] = Function(["say hello"], tags=["minecraft:load"])
```

The `beet` toolchain is designed to support a wide range of use-cases. The most basic pipeline will let you create configurable resource packs and data packs, but plugins make it easy to implement arbitrarily advanced workflows and tools like linters, asset generators and function pre-processors.

- Compose plugins that can inspect and edit the generated resource pack and data pack
- Configure powerful build systems for development and creating releases
- First-class template integration approachable without prior Python knowledge
- Link the generated resource pack and data pack to Minecraft
- Automatically rebuild the project on file changes with watch mode

## Installation

The package can be installed with `pip`.

```bash
$ pip install beet
```

You can make sure that `beet` was successfully installed by trying to use the toolchain from the command-line.

```bash
$ beet --help
Usage: beet [OPTIONS] COMMAND [ARGS]...

  The beet toolchain.

Options:
  -d, --directory DIRECTORY  Use the specified project directory.
  -c, --config FILE          Use the specified config file.
  -l, --log LEVEL            Configure output verbosity.
  -v, --version              Show the version and exit.
  -h, --help                 Show this message and exit.

Commands:
  build  Build the current project.
  cache  Inspect or clear the cache.
  link   Link the generated resource pack and data pack to Minecraft.
  watch  Watch the project directory and build on file changes.
```

## Status

You can expect current releases to be pretty stable, but the project as a whole should still be considered alpha.

The main reason is that resource pack and data pack coverage is currently lacking in certain areas. Exposing a consistent interface for every data pack and resource pack feature can involve design decisions that aren't immediately obvious. You're welcome to open an issue to discuss the implementation of currently unsupported resources. And feel free to ask questions, report bugs, and share your thoughts and impressions.

## Contributing

Contributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org).

```bash
$ poetry install
```

You can run the tests with `poetry run pytest`. We use [`pytest-minecraft`](https://github.com/vberlier/pytest-minecraft) to run tests against actual Minecraft releases.

```bash
$ poetry run pytest
$ poetry run pytest --minecraft-latest
```

We also use [`pytest-insta`](https://github.com/vberlier/pytest-minecraft) for snapshot testing. Data pack and resource pack snapshots make it easy to monitor and review changes.

```bash
$ poetry run pytest --insta review
```

The project must type-check with [`pyright`](https://github.com/microsoft/pyright). If you're using VSCode the [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension should report diagnostics automatically. You can also install the type-checker locally with `npm install` and run it from the command-line.

```bash
$ npm run watch
$ npm run check
```

The code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).

```bash
$ poetry run isort beet tests
$ poetry run black beet tests
$ poetry run black --check beet tests
```

---

License - [MIT](https://github.com/mcbeet/beet/blob/main/LICENSE)
