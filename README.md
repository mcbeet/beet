# <img src="https://github.com/vberlier/beet/blob/master/docs/assets/logo.svg" alt="beet logo" width="30"> beet

[![Build Status](https://travis-ci.com/vberlier/beet.svg?token=HSyYhdxSKy5kTTrkmWq7&branch=master)](https://travis-ci.com/vberlier/beet)
[![PyPI](https://img.shields.io/pypi/v/beet.svg)](https://pypi.org/project/beet/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beet.svg)](https://pypi.org/project/beet/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

> The Minecraft pack development kit.

## Introduction

Over the years, Minecraft [resource packs](https://minecraft.gamepedia.com/Resource_Pack) and [data packs](https://minecraft.gamepedia.com/Data_Pack) evolved into really powerful tools that anyone can use to customize the vanilla experience. It's now possible to implement almost any game mechanic imaginable using a resource pack and a data pack.

With the growing number of capabilities, there's been a matching drive from the community when it comes to establishing interoperability standards and developing reusable data pack libraries. As the community tries to create more and more things with these capabilities, it's becoming more and more apparent that resource packs and data packs aren't really suited as an _authoring_ format. They're simple and straight-forward to parse, which means that they fulfill their initial objective as a _distribution_ format, but they weren't created with a specific developer experience in mind.

Many people started tackling the problem by building tools, from command pre-processors to full-blown programming languages and all kinds of frameworks, but none of these solutions could really talk to each other. Depending on the situation, some tools would provide more suitable abstractions than others, but most of them would be difficult to use together. Another problem is that by focusing on the abstractions, some of these tools either left out crucial quality-of-life features or each had to re-implement very similar development workflows.

The `beet` project is meant to serve as a platform for building interoperable higher-level frameworks by providing low-level abstractions, a composition model and a unified development workflow.

### Features

- The `beet` library provides carefully crafted abstractions for working with Minecraft resource packs and data packs in Python.

  ```python
  from beet import ResourcePack, Texture

  with ResourcePack(path="stone.zip") as assets:
      assets["minecraft:block/stone"] = Texture(source_path="custom.png")
  ```

  - Create, read, edit and merge resource packs and data packs
  - Handle zipped and unzipped packs
  - Fast and lazy by default, files are transparently loaded when accessing their content
  - Statically typed API enabling rich intellisense and autocompletion

- The `beet` toolchain makes it easy to create configurable resource packs and data packs by composing pack generators.

  ```python
  from beet import Context, Function

  def greet(ctx: Context):
      ctx.data["greet:hello"] = Function(["say hello"], tags=["minecraft:load"])
  ```

  - Generators are simple functions that can edit or inspect the generated resource pack and data pack
  - Watch mode for building the project on file changes
  - Link the project to Minecraft to automatically synchronize the generated resource pack and data pack
  - Versatile caching API to prevent repeating expensive computations
  - Simple use-cases like merging packs are built into the prelude and don't require any code

## Installation

The package can be installed with `pip`.

```bash
$ pip install beet
```

You can make sure that `beet` was successfully installed by trying to use the toolchain from the command-line.

```bash
$ beet --version
```

## Documentation

The project documentation is available at https://vberlier.github.io/beet/.

### Library

- [Getting Started]()
- [Resource packs]()
- [Data packs]()
- [Generic file types]()
- [Generic packs and namespaces]()

### Toolchain

- [Getting Started]()
- [Writing generators]()
- [Command-line interface]()
- [Configuration]()
- [The beet prelude]()
- [Using the cache]()

## Contributing

Contributions are welcome. This project uses [`poetry`](https://python-poetry.org).

```bash
$ poetry install
```

You can run the tests with `poetry run pytest`. We use [`pytest-minecraft`](https://github.com/vberlier/pytest-minecraft) to run tests against actual Minecraft releases.

```bash
$ poetry run pytest
$ poetry run pytest --minecraft-latest
```

The project must type-check with [`mypy`](http://mypy-lang.org) and [`pylint`](https://www.pylint.org) shouldn't report any error.

```bash
$ poetry run mypy
$ poetry run pylint beet tests
```

The code follows the [`black`](https://github.com/psf/black) code style.

```bash
$ poetry run black beet tests
$ poetry run black --check beet tests
```

---

License - [MIT](https://github.com/vberlier/beet/blob/master/LICENSE)
