<img align="right" src="https://raw.githubusercontent.com/mcbeet/lectern/main/logo.png?sanitize=true" alt="logo" width="76">

# Lectern

[![GitHub Actions](https://github.com/mcbeet/lectern/workflows/CI/badge.svg)](https://github.com/mcbeet/lectern/actions)
[![PyPI](https://img.shields.io/pypi/v/lectern.svg)](https://pypi.org/project/lectern/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lectern.svg)](https://pypi.org/project/lectern/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Discord](https://img.shields.io/discord/900530660677156924?color=7289DA&label=discord&logo=discord&logoColor=fff)](https://discord.gg/98MdSGMm8j)

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

## Document formats

`lectern` implements two closely-related document formats: markdown and plain text. The markdown format builds upon the plain text format.

The markdown format lets you present the various elements of your data pack or resource pack and how they fit together. It's a format that's meant to support [literate programming](https://en.wikipedia.org/wiki/Literate_programming). You can use it when your document is meant to be read by other people. It allows you to emphasize the important parts, explain tradeoffs and discuss alternatives, implementation details, etc...

    `@function tutorial:greeting`

    ```mcfunction
    say Hello, world!
    ```

On the other hand if you don't intend to produce literate documents you can use the plain text format to author data packs and resource packs as a single file without having to deal with markdown formatting.

<!-- @skip -->

```
@function tutorial:greeting
say Hello, world!
```

## Directives

Data pack and resource pack fragments are code blocks, links or images annotated with a special `lectern` directive. Directives are prefixed with the `@` symbol and can be followed by zero or more arguments.

```
@<directive_name> <arg1> <arg2> <arg3>...
```

`lectern` provides directives for including namespaced resources inside data packs and resource packs. These built-in directives all expect a single argument specifying the fully-qualified resource name.

<!-- @skip -->

```
@function tutorial:greeting
@function_tag minecraft:load
```

Here is a reference of all the supported resources:

| Data pack                       | Resource pack      |
| ------------------------------- | ------------------ |
| `@advancement`                  | `@blockstate`      |
| `@function`                     | `@model`           |
| `@loot_table`                   | `@language`        |
| `@predicate`                    | `@font`            |
| `@recipe`                       | `@glyph_sizes`     |
| `@structure`                    | `@true_type_font`  |
| `@block_tag`                    | `@shader_post`     |
| `@entity_type_tag`              | `@shader`          |
| `@fluid_tag`                    | `@fragment_shader` |
| `@function_tag`                 | `@vertex_shader`   |
| `@game_event_tag`               | `@glsl_shader`     |
| `@item_tag`                     | `@text`            |
| `@dimension_type`               | `@texture_mcmeta`  |
| `@dimension`                    | `@texture`         |
| `@biome`                        | `@sound`           |
| `@configured_carver`            | `@particle`        |
| `@configured_feature`           |                    |
| `@configured_structure_feature` |                    |
| `@configured_surface_builder`   |                    |
| `@noise_settings`               |                    |
| `@processor_list`               |                    |
| `@template_pool`                |                    |
| `@item_modifier`                |                    |

> Note that these directives are resolved automatically. If you're working with pack extensions your custom namespaced resources will have their own directives as well.

There are also two built-in directives that can be used to include files using a path relative to the root of the data pack or the resource pack.

<!-- @skip -->

```
@data_pack pack.mcmeta
@resource_pack pack.png
@resource_pack assets/minecraft/textures/block/kelp_plant.png.mcmeta
```

This is useful for adding files that aren't part of any particular namespace.

In case you need to bundle existing resource packs or data packs, you can use the `@merge_zip` directive.

<!-- @skip -->

```
@merge_zip(download)
https://example.com/my_zipped_data_pack.zip
```

Finally, the `@skip` directive is simply ignored and allows you to end a previous fragment in the plain text format.

<!-- @skip -->

```
@function tutorial:greeting
say Hello, world!

@skip
This will not be included in the output.
```

## Code block fragments

You can include the content of a code block in a data pack or a resource pack by preceding it with a directive surrounded by backticks.

`@function tutorial:greeting`

```mcfunction
say Hello, world!
```

You can put the directive in an html comment to make it invisible. Here the code block is annotated with the following comment:

```html
<!-- @function_tag minecraft:load -->
```

<!-- @function_tag minecraft:load -->

```json
{
  "values": ["tutorial:greeting"]
}
```

When using backticks you can surround the code block in a `<details>` element to make the code fragment foldable.

`@function tutorial:greeting`

<details>

```mcfunction
say Hello, world!
```

</details>

The directive can also be embedded directly inside the code block. You can insert a directive preceded by either `#` or `//` and the following lines will be included in the specified file.

```mcfunction
# @function tutorial:obtained_dead_bush
say You obtained a dead bush!
```

Embedded directives are stripped from the output. You can use multiple directives in a single code block.

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

It's also possible to use the lectern text format directly inside code blocks.

```mcfunction
@function text_in_block:foo
say foo
```

## Link fragments

Link fragments make it possible to refer to external files, online assets, and to embed binary files in the markdown as data urls. You can create a link fragment by turning a directive surrounded by backticks into a markdown link.

[`@loot_table minecraft:blocks/yellow_shulker_box`](examples/with_links/yellow_shulker_box.json)

The link itself can be a path to a local file or any url supported by the built-in [`urlopen`](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen) function.

## Image fragments

You can include inline markdown images in the output data pack or resource pack by preceding the image with a directive surrounded by backticks.

`@data_pack pack.png`

![](https://static.wikia.nocookie.net/minecraft_gamepedia/images/3/3a/Pack.png/revision/20210509190015)

Image fragments support the same variations as code block fragments. You can put the directive in a comment or surround the image with a `<details>` element to make it foldable.

## Hidden fragments

You can use html comments to add fragments that will be completely hidden in the rendered markdown.

```html
<!--
@function tutorial:hidden
say This will not appear in the rendered markdown.

@function tutorial:also_hidden
say This is also hidden.
-->
```

<!--
@function tutorial:hidden
say This will not appear in the rendered markdown.

@function tutorial:also_hidden
say This is also hidden.
-->

## Modifiers

The behavior of particular directives can be adjusted with modifiers. A modifier is specified between parentheses right after the name of the directive.

```
@<directive_name>(<modifier>) <arg1> <arg2> <arg3>...
```

The `append` modifier is implemented by all the text-based built-in namespaced resource directives and makes it possible to concatenate the content of the fragment to the already-existing content.

`@function(append) tutorial:greeting`

```mcfunction
say This is added afterwards.
```

You can also use `prepend` to add the fragment before the already-existing content.

`@function(prepend) tutorial:greeting`

```mcfunction
say This is added before.
```

The `merge` modifier is similar but instead of concatenating the contents it uses the `beet` merging strategy to combine the fragment with the existing file.

`@function_tag(merge) minecraft:load`

```json
{
  "values": ["#tutorial:something_else"]
}
```

There are also modifiers that are applied to the content of the fragment directly. The `base64` modifier will decode the content of the code fragment as [base64](https://en.wikipedia.org/wiki/Base64).

`@function_tag(base64) tutorial:something_else`

```json
ewogICJ2YWx1ZXMiOiBbInR1dG9yaWFsOnN0cmlwcGVkIl0KfQ==
```

You can use block fragments to download remote files with the `download` modifier.

`@function_tag(download) tutorial:from_github`

```json
https://raw.githubusercontent.com/mcbeet/beet/main/examples/load_basic/src/data/demo/functions/foo.mcfunction
```

Finally, there's a `strip_final_newline` modifier that removes the final newline at the end of code block fragments. It's mostly used to make sure that `lectern` snapshots can reconstruct the original content byte for byte in case the file wasn't terminated by a newline.

`@function(strip_final_newline) tutorial:stripped`

```mcfunction
say This function doesn't have a final newline.
```

## Overlays

You can use the `@overlay` directive to make the following directives apply to a specific pack overlay. Overlays were introduced in [Java Edition 1.20.2](https://minecraft.wiki/w/Java_Edition_1.20.2).

`@overlay({"min_inclusive": 16, "max_inclusive": 17}) dummy_overlay`

You can specify the `formats` supported by this overlay as a modifier. From now on, all the directives will apply to the overlay `dummy_overlay`.

`@function tutorial:greeting`

```mcfunction
say Hello from overlay!
```

You can switch to another overlay at any time by using the `@overlay` directive again. To go back to the main pack, use the `@endoverlay` directive.

`@endoverlay`

## Command-line utility

```bash
$ lectern --help
Usage: lectern [OPTIONS] [PATH]...

  Literate Minecraft data packs and resource packs.

Options:
  -d, --data-pack <path>       Extract data pack.
  -r, --resource-pack <path>   Extract resource pack.
  -e, --external-files <path>  Emit external files.
  -p, --prefetch-urls <path>   Prefetch markdown links.
  -f, --flat                   Use the flat markdown format.
  -o, --overwrite              Overwrite the output pack.
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

If you want to overwrite an existing data pack or resource pack you need to specify the `-o/--overwrite` option explicitly.

```bash
$ lectern demo.md --overwrite --data-pack demo_data_pack
```

You can also convert a combination of data packs and resource packs into a single markdown file.

```bash
$ lectern demo_data_pack demo.md
$ lectern demo_data_pack.zip demo.md
$ lectern demo_data_pack demo_resource_pack demo.md
$ lectern foo_data_pack bar_data_pack demo.md
```

The last argument is the name of the generated markdown file. By default, the `lectern` utility will bundle binary files into the markdown file as data urls. You can use the `-e/--external-files` option to dump the binary files in a given directory instead.

```bash
$ lectern demo_data_pack demo.md --external-files files
$ lectern demo_data_pack demo.md -e files
$ lectern demo_data_pack demo.md -e .
```

All these commands also work with plain text files. `lectern` will only use the markdown document format when the filename ends with `.md`.

Finally, you can also use the command-line utility to prefetch markdown urls. The `-p/--prefetch-urls` option can replace the urls in-place or in a copy.

```bash
$ lectern --prefetch-urls demo.md
$ lectern --prefetch-urls demo.md demo_prefetched.md
$ lectern -p demo.md demo_prefetched.md
$ lectern -p demo.md
```

By default, the remote files will be bundled as data urls but you can use the `-e/--external-files` option to dump everything in a given directory.

```bash
$ lectern --prefetch-urls demo.md --external-files files
$ lectern --prefetch-urls demo.md demo_prefetched.md --external-files files
$ lectern -p demo.md demo_prefetched.md -e files
$ lectern -p demo.md -e .
```

## Python API

The API revolves around `Document` objects. A `lectern` document holds a `DataPack` and a `ResourcePack`, as well as a dictionary defining the usable directives. The extractors and serializers are also exposed on the document to make it possible to swap them out with custom ones if needed.

```python
from beet import DataPack, ResourcePack
from lectern import Document

document = Document()
assert document.data == DataPack()
assert document.assets == ResourcePack()
```

The constructor makes it possible to provide existing `DataPack` and `ResourcePack` instances, some initial text or markdown content, or a path from which to load an existing `lectern` document.

```python
Document(data=DataPack(), assets=ResourcePack())
Document(text=...)
Document(markdown=...)
Document(path="path/to/document.md")
```

`Document` instances will compare equal if the underlying data packs and resource packs also compare equal.

You can use the `load` method to read a markdown or a plain text file and update the internal data pack and resource pack with the extracted fragments.

```python
document.load("path/to/document.md")
```

If you already have some text or markdown ready to go, you can use the `add_text` and `add_markdown` methods.

```python
document.add_text(...)
document.add_markdown(...)
```

If the markdown content refers to local files you can specify the directory from which the external files should be loaded from with the `external_files` argument.

```python
document.add_markdown(..., external_files="path/to/directory")
```

If you're handling user input and you don't know which document format is being provided you can use the `add` method and `lectern` will detect if the input is markdown or plain text.

```python
document.add(...)
```

You can use the `get_text` and `get_markdown` methods to serialize the entire content of the internal data pack and resource pack. By default the `get_markdown` method will produce markdown that embeds binary files as data urls. You can enable `emit_external_files` and optionally provide a path prefix to generate a dictionary of associated files instead.

```python
text = document.get_text()
markdown = document.get_markdown()
markdown, external_files = document.get_markdown(emit_external_files=True)
markdown, external_files = document.get_markdown(emit_external_files=True, prefix="path/to/directory")
```

Finally, the `save` method lets you serialize and write the document to a given path. If the filename ends with `.md` the generated markdown will bundle binary files as data urls by default. You can use the `external_files` argument to emit the binary files in the given directory instead.

```python
document.save("path/to/document.txt")
document.save("path/to/document.md")
document.save("path/to/document.md", external_files="path/to/files")
```

## Custom directives

Directives are simply callable objects that receive the document fragment, the resource pack, and the data pack as arguments.

```python
from beet import DataPack, ResourcePack, Function
from lectern import Document, Fragment

def my_directive(fragment: Fragment, assets: ResourcePack, data: DataPack):
    num1, num2 = fragment.expect("num1", "num2")
    result = int(num1) + int(num2)
    data["demo:output_result"] = Function([f"say {result}"])

document = Document()
document.directives["my_directive"] = my_directive
document.add_text("@my_directive 32 10")
assert document.data.functions["demo:output_result"] == Function(["say 42"])
```

The `expect` method allows you to unpack the directive arguments and automatically raises an error if the user didn't specify the arguments properly. You can use the `as_file` method to get the content of the fragment as a specific type of file.

```python
def repeated_function(fragment: Fragment, assets: ResourcePack, data: DataPack):
    full_name, count = fragment.expect("full_name", "count")
    function = fragment.as_file(Function)
    function.lines *= int(count)
    data[full_name] = function
```

The `as_file` method will take care of reading the file or downloading it if the directive is used with a link fragment. It will also handle the `base64` and `strip_final_newline` modifiers.

You can handle custom modifiers by checking the content of the `modifier` attribute.

## Fragment loaders

The `Document` object lets you register fragment loaders that intercept and potentially modify fragments before they're handled by directives. The `loaders` attribute is a list of callable objects that receive the fragment and the available directives as arguments. Each loader can then forward the fragment as-is or return a modified fragment. You can also return `None` to drop the fragment.

```python
from typing import Mapping, Optional
from lectern import Directive, Document, Fragment

def handle_ignore_modifier(
    fragment: Fragment,
    directives: Mapping[str, Directive],
) -> Optional[Fragment]:
    if fragment.modifier == "ignore":
        return None
    return fragment

document = Document()
document.loaders.append(handle_ignore_modifier)
document.add_text("@function(ignore) demo:foo\nsay hello")
assert not document.data
```

## Beet plugin

Using `lectern` as a `beet` plugin makes it possible to combine your markdown files with arbitrary `beet` plugins for further processing. The plugin can load files using the plain text and markdown document formats and emit a snapshot of the `beet` context at the end of the build.

```json
{
  "pipeline": ["lectern"],
  "meta": {
    "lectern": {
      "load": ["*.md"],
      "snapshot": "out/snapshot.md",
      "external_files": "out"
    }
  }
}
```

You can require the plugin programmatically by using the `lectern` plugin factory.

```python
from beet import Context
from lectern import lectern

def my_plugin(ctx: Context):
    ctx.require(
        lectern(
            load=["*.md"],
            snapshot="out/snapshot.md",
            external_files="out",
        )
    )
```

All the configuration is optional. The plugin is a no-op if the `load` or `snapshot` options are not specified.

You can retrieve the `Document` instance with the `inject` method. This is useful for adding custom directives.

```python
from beet import Context, DataPack, ResourcePack, Function
from lectern import Document, Fragment

def hello_directive(ctx: Context):
    """Plugin that defines the `@hello <name>` directive."""
    document = ctx.inject(Document)
    document.directives["hello"] = hello

def hello(fragment: Fragment, assets: ResourcePack, data: DataPack):
    name = fragment.expect("name")
    function = data.functions.setdefault("hello:greetings", Function([]))
    function.lines.append(f"say Hello, {name}!")
```

It's worth mentioning that `lectern` uses the `beet` cache to avoid downloading link fragments repeatedly and keeping your build snappy, especially in watch mode. If you need to re-download link fragments you can clear the `lectern` cache.

```bash
$ beet cache --clear lectern
```

You can also use a plugin to configure a custom cache timeout if you want to make sure that your assets are re-downloaded periodically.

```python
from beet import Context

def download_every_day(ctx: Context):
    ctx.cache["lectern"].timeout(hours=24)
```

## Extra directives

If you're using `lectern` as a `beet` plugin you will be able to use additional directives by adding the corresponding plugins to the `require` option.

```json
{
  "require": [
    "lectern.contrib.require",
    "lectern.contrib.script",
    "lectern.contrib.define"
  ],
  "pipeline": ["lectern"],
  "meta": {
    "lectern": {
      "load": ["*.md"]
    }
  }
}
```

The `lectern.contrib.require` plugin adds a directive that lets you require plugins dynamically.

`@require my_plugins.hello`

The `lectern.contrib.script` plugin adds a directive that renders a fragment with Jinja and interprets the result as `lectern` text.

`@script`

<!-- @skip -->

```
{% for i in range(10) %}
@function demo:script_{{ i }}
say {{ i }}
{% endfor %}
```

Note that using `@script` with the text format requires you to escape the directives in the fragment with an additional `@` symbol.

<!-- @skip -->

```
@script
{% for i in range(10) %}
@@function demo:script_{{ i }}
say {{ i }}
{% endfor %}
```

The `lectern.contrib.define` plugin adds a directive that renders a fragment with Jinja and stores the resulting string as a template global.

`@define(strip_final_newline) math_message`

<!-- @skip -->

```
2 + 2 is {{ 2 + 2 }}
```

## Lectern scripts

The text format is pretty well-suited for writing basic data pack and resource pack generators. You can very easily write scripts that produce lectern syntax that can then be turned into a data pack or a resource pack.

```python
# my_script.py
print("@function tutorial:count")

for i in range(10):
    print(f"say {i}")
```

```bash
$ python my_script.py > output.txt
$ lectern output.txt -d my_data_pack
```

The `beet` plugin supports this use-case natively and allows you to run lectern scripts within your pipeline.

```json
// beet.json
{
  "pipeline": ["lectern"],
  "meta": {
    "lectern": {
      "scripts": [["python", "my_script.py"]]
    }
  }
}
```

The `scripts` option lets you specify the command-line arguments for your scripts. The scripts don't even have to be written in Python. As long as the command prints out valid `lectern` syntax you can use any language you want.

## Relative resource locations

The `lectern.contrib.relative_location` plugin uses the `beet` context generator to generate namespaced resources in a default location automatically if you don't specify any namespace.

<!-- @skip -->

```
@function foo
function tutorial:bar

@function bar
say hello
```

You can customize the root of unqualified resource locations by using the `generate_namespace` and `generate_prefix` meta variables. By default, `generate_namespace` is set to the `project_id` and `generate_prefix` is empty.

The plugin works pretty nicely with `beet.contrib.relative_function_path`.

```json
// beet.json
{
  "require": ["lectern.contrib.relative_location"],
  "pipeline": ["lectern", "beet.contrib.relative_function_path"],
  "meta": {
    "lectern": {
      "load": ["*.md"]
    }
  }
}
```

<!-- @skip -->

```
@function foo
function ./bar

@function bar
say hello
```

## Using YAML

You can use the `lectern.contrib.yaml_to_json` plugin to author JSON files with YAML. Since YAML is a superset of JSON, you don't have to do anything when you use the plugin. YAML fragments are transparently converted to JSON.

```json
{
  "require": ["lectern.contrib.yaml_to_json"],
  "pipeline": ["lectern"],
  "meta": {
    "lectern": {
      "load": ["*.md"]
    }
  }
}
```

<!-- @skip -->

```
@function_tag minecraft:tick
values:
  - demo:foo
```

The `@data_pack` and `@resource_pack` directives will also convert the fragment to JSON if the file extension matches `.yml` or `.yaml`.

<!-- @skip -->

```
@resource_pack assets/minecraft/sounds.yml
block.note_block.bit_1:
  sounds:
    - block/note_block/bit_1
  subtitle: subtitles.block.note_block.note
```

## Snapshot testing

A lot of Minecraft tooling involves generating data packs and resource packs. Writing tests for this kind of tooling takes time because you need to painstakingly compare everything that you care about with a reference value. This makes it hard to get good coverage, and then even harder to keep making changes to the code being tested afterwards. You're trading robustness and stability for a shackle that massively slows down development.

That's where snapshot testing comes into play. Snapshot testing allows you to record a reference value and then make sure that your code keeps producing the same results. It provides the necessary tools for reviewing snapshots and updating them as your project evolves.

`lectern` documents are useful as snapshot formats because they represent entire data packs and resource packs in a single file that's human-readable and diff-friendly.

[`pytest-insta`](https://github.com/vberlier/pytest-insta) is an extensible snapshot testing plugin for [`pytest`](https://docs.pytest.org/en/stable/). When it's installed, `lectern` defines three additional snapshot formats.

| Extension                 | Format description                                               |
| ------------------------- | ---------------------------------------------------------------- |
| `.pack.txt`               | Plain text snapshot.                                             |
| `.pack.md`                | Markdown snapshot with bundled binary files.                     |
| `.pack.md_external_files` | Directory with a README.md that refers to external binary files. |

You can use these snapshot formats when comparing `Document` objects with the `snapshot` fixture.

```python
def test_generate(snapshot):
    data = generate_some_data_pack()
    assert snapshot("pack.txt") == Document(data=data)
```

If you're using the `beet` toolchain, keep in mind that you can get a `Document` instance bound to the context object by using the `inject` method.

```python
def test_generate_with_beet(snapshot):
    with run_beet(...) as ctx:
        assert snapshot("pack.txt") == ctx.inject(Document)
```

This will save the entire data pack and resource pack in the snapshot. For more details about working with the generated snapshots check out the [`pytest-insta` documentation](https://github.com/vberlier/pytest-insta#command-line-options).

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
