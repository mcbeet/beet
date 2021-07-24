<img align="right" src="https://raw.githubusercontent.com/vberlier/mecha/main/logo.png" alt="logo" width="76">

# Mecha

[![GitHub Actions](https://github.com/vberlier/mecha/workflows/CI/badge.svg)](https://github.com/vberlier/mecha/actions)
[![PyPI](https://img.shields.io/pypi/v/mecha.svg)](https://pypi.org/project/mecha/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mecha.svg)](https://pypi.org/project/mecha/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

> A powerful Minecraft command library.

## Introduction

This package provides a versatile API for generating Minecraft commands in Python. It uses the [`beet`](https://github.com/vberlier/beet) library to generate functions and integrates natively with the `beet` pipeline.

```python
from beet import Context
from mecha import Mecha

def my_plugin(ctx: Context):
    mc = ctx.inject(Mecha)

    with mc.function("foo"):
        mc.say("hello")
```

You can directly create handles from data pack instances. The library can be used on its own without being part of a `beet` pipeline.

```python
from beet import DataPack
from mecha import Mecha

with DataPack(path="demo") as data:
    mc = Mecha(data)

    with mc.function("foo"):
        mc.say("hello")
```

## Installation

The package can be installed with `pip`.

```bash
$ pip install mecha
```

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

License - [MIT](https://github.com/vberlier/mecha/blob/main/LICENSE)
