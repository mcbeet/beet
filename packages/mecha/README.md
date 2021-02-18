<img align="right" src="docs/assets/logo.svg" alt="logo" width="76">

# Mecha

[![GitHub Actions](https://github.com/vberlier/mecha/workflows/CI/badge.svg)](https://github.com/vberlier/mecha/actions)
[![PyPI](https://img.shields.io/pypi/v/mecha.svg)](https://pypi.org/project/mecha/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mecha.svg)](https://pypi.org/project/mecha/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

> A flexible Minecraft command generation library.

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

---

License - [MIT](https://github.com/vberlier/mecha/blob/main/LICENSE)
