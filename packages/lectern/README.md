<img align="right" src="https://raw.githubusercontent.com/mcbeet/lectern/main/logo.png?sanitize=true" alt="logo" width="52">

# Lectern

[![GitHub Actions](https://github.com/mcbeet/lectern/workflows/CI/badge.svg)](https://github.com/mcbeet/lectern/actions)
[![PyPI](https://img.shields.io/pypi/v/lectern.svg)](https://pypi.org/project/lectern/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lectern.svg)](https://pypi.org/project/lectern/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

> Literate Minecraft data packs and resource packs.

`@function tutorial:greeting`

```mcfunction
say Hello, world!
```

## Introduction

This markdown file is interspersed with code fragments describing the content of a Minecraft data pack. Using `lectern`, you can turn this single file into an actual data pack that can be loaded into the game.

**Features**

- Turn markdown files into data packs and resource packs
- Merge resources from several markdown files
- Convert data packs and resource packs into markdown snapshots
- Can be used as a [`beet`](https://github.com/mcbeet/beet) plugin
- Highly extensible with custom directives
- Automatically integrates with [`pytest-insta`](https://github.com/vberlier/pytest-insta)

**Hmmkay but why?**

- Editing data packs involves a lot of jumping around between files, for simple use-cases a single file is a lot easier to work with
- Minecraft packs aggregate various types of files that can have complex interactions with each other, a literate style allows you to document these interactions fluently
- Human-readable, single-file data pack and resource pack snapshots can be really useful to diff and track regressions in Minecraft-related tooling

## Installation

The package can be installed with `pip`.

```bash
$ pip install lectern
```

## Getting started

This is an example of a markdown file that can be turned into a data pack:

    # Beginner tutorial

    Let's start by creating a simple function:

    `@function tutorial:greeting`

    ```mcfunction
    say Hello, world!
    ```

    And now we can make it run when the data pack is loaded!

    `@function_tag minecraft:load`

    ```json
    {
      "values": ["tutorial:greeting"]
    }
    ```

You can use the `lectern` command-line utility to turn the markdown file into a data pack.

```bash
$ lectern tutorial.md --data-pack path/to/tutorial_data_pack
```

If you're using [`beet`](https://github.com/mcbeet/beet) you can use `lectern` as a plugin in your pipeline.

```json
{
  "pipeline": ["lectern"],
  "meta": {
    "lectern": {
      "load": ["*.md"]
    }
  }
}
```

## Directives

Data pack and resource pack fragments are code blocks, links or images annotated with a special `lectern` directive. Directives are prefixed with the `@` symbol and can be followed by zero or more arguments.

```
@<directive_name> <arg1> <arg2> <arg3>...
```

`lectern` provides directives for including namespaced resources inside data packs and resource packs. These built-in directives all expect a single argument specifying the fully-qualified resource name.

```
@function tutorial:greeting
@function_tag minecraft:load
```

Here is a reference of all the supported resources:

| Data pack                       |     | Resource pack      |     |
| ------------------------------- | --- | ------------------ | --- |
| `@advancement`                  |     | `@blockstate`      |     |
| `@function`                     |     | `@model`           |     |
| `@loot_table`                   |     | `@font`            |     |
| `@predicate`                    |     | `@glyph_sizes`     | ⚠️  |
| `@recipe`                       |     | `@truetype_font`   | ⚠️  |
| `@structure`                    | ⚠️  | `@shader_post`     |     |
| `@block_tag`                    |     | `@shader_program`  |     |
| `@entity_type_tag`              |     | `@fragment_shader` |     |
| `@fluid_tag`                    |     | `@vertex_shader`   |     |
| `@function_tag`                 |     | `@text`            |     |
| `@item_tag`                     |     | `@texture_mcmeta`  |     |
| `@dimension_type`               |     | `@texture`         | ⚠️  |
| `@dimension`                    |     |                    |     |
| `@biome`                        |     |                    |     |
| `@configured_carver`            |     |                    |     |
| `@configured_feature`           |     |                    |     |
| `@configured_structure_feature` |     |                    |     |
| `@configured_surface_builder`   |     |                    |     |
| `@noise_settings`               |     |                    |     |
| `@processor_list`               |     |                    |     |
| `@template_pool`                |     |                    |     |

> ⚠️ Binary resources are supported but aren't compatible with code block fragments.

There are two additional built-in directives that can be used to include files using a path relative to the root of the data pack or the resource pack.

```
@data_pack pack.mcmeta
@resource_pack pack.png
@resource_pack assets/minecraft/textures/block/kelp_plant.png.mcmeta
```

This is useful for adding files that aren't part of any particular namespace.

## Code block fragments

You can include the content of a code block in a data pack or a resource pack by preceding it with a directive surrounded by backticks.

`@function tutorial:greeting`

```mcfunction
say Hello, world!
```

You can put the directive in an html comment to make it invisible.

<!-- @function_tag minecraft:load -->

```json
{
  "values": ["tutorial:greeting"]
}
```

The directive can also be embedded directly inside the code block. You can insert a directive preceded by either `#` or `//` and the following lines will be included in the specified file.

```mcfunction
# @function tutorial:obtained_dead_bush
say You obtained a dead bush!
```

Embedded directives are striped from the output. You can use multiple directives in a single code block.

```json
// @loot_table minecraft:blocks/diamond_ore
{
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:dead_bush"
        }
      ]
    }
  ]
}

// @advancement tutorial:obtained_dead_bush
{
  "criteria": {
    "dead_bush": {
      "trigger": "minecraft:inventory_changed",
      "conditions": {
        "items": [
          {
            "item": "minecraft:dead_bush"
          }
        ]
      }
    }
  },
  "requirements": [
    [
      "dead_bush"
    ]
  ],
  "rewards": {
    "function": "tutorial:obtained_dead_bush"
  }
}
```

## Link fragments

TODO

## Image fragments

TODO

## Modifiers

TODO

## Command-line utility

```bash
$ lectern --help
Usage: lectern [OPTIONS] [PATH]...

  Literate Minecraft data packs and resource packs.

Options:
  -d, --data-pack <path>       Extract data pack.
  -r, --resource-pack <path>   Extract resource pack.
  -e, --external-files <path>  Emit external files.
  -v, --version                Show the version and exit.
  -h, --help                   Show this message and exit.
```

You can extract data packs from markdown files with the `-d/--data-pack` option. If the name ends with `.zip` the generated data pack will be zipped. Multiple markdown files can be merged together into a single data pack.

```bash
$ lectern demo.md --data-pack demo_data_pack
$ lectern demo.md -d demo_data_pack
$ lectern demo.md -d demo_data_pack.zip
$ lectern foo.md bar.md -d demo_data_pack
```

The `-r/--resource-pack` option lets you do exactly the same thing but with resource packs. The two options can be combined to extract a data packs and a resource pack at the same time.

```bash
$ lectern demo.md --resource-pack demo_resource_pack
$ lectern demo.md -r demo_resource_pack
$ lectern demo.md -d demo_data_pack -r demo_resource_pack
```

You can also convert a combination of data packs and resource packs into a single markdown file.

```bash
$ lectern demo_data_pack demo.md
$ lectern demo_data_pack.zip demo.md
$ lectern demo_data_pack demo_resource_pack demo.md
$ lectern foo_data_pack bar_data_pack demo.md
```

The last argument is the name of the generated markdown file. By default, the `lectern` utility won't save the files that can't be directly defined inside the markdown file. You can use the `-o/--output-files` option to dump the files in the specified directory.

```bash
$ lectern demo_data_pack demo.md --output-files files
$ lectern demo_data_pack demo.md -o files
$ lectern demo_data_pack demo.md -o .
```

## Beet plugin

TODO

## Plain text documents

TODO

## Lectern for snapshot testing

TODO

## Contributing

Contributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org).

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
$ poetry run isort lectern tests
$ poetry run black lectern tests
$ poetry run black --check lectern tests
```

---

License - [MIT](https://github.com/mcbeet/lectern/blob/main/LICENSE)
