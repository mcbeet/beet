---
icon: lucide/rocket
---

# Get started

Beet is a development toolkit for working with Minecraft data and resource packs. This section will explain how to install beet and get started with a first project.

## Installation

Beet is written in Python, and is published as a [Python package].
We  recommend to use a Python _virtual environment_ when installing [with
`pip`](#install-with-pip) or [with `uv`](#install-with-uv).

[Python package]: https://pypi.org/project/beet

!!! note "Prerequisites"
    You need to have Python and a Python package manager installed on your
    system before you install Beet. We recommend you follow the [Python
    Setup and Usage] instructions for your operating system provided on the
    [Python website].

[Python Setup and Usage]: https://docs.python.org/3/using
[Python website]: https://www.python.org/

### Install with pip

Beet can be installed into a virtual environment with pip.

Open up a terminal window and install Beet by first setting up a virtual
environment and then using `pip` to install the Beet package into it:

=== ":fontawesome-brands-windows: Windows"
    ```
    python3 -m venv .venv
    .venv\Scripts\activate
    pip install beet
    ```

=== ":material-apple: macOS"
    ``` sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install beet
    ```

=== ":material-linux: Linux"
    ``` sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install beet
    ```

### Install with uv

If you are developing software using Python, chances are you're already using
[`uv`][uv] as a package manager, which has become popular in recent years. To
install Beet with `uv`, use:

[uv]: https://docs.astral.sh/uv/

```
uv init
uv add beet
```

## Create a project

Beet projects start with a configuration file in the root of your project.

```json title="beet.json"
{
    "name": "My First Pack",
    "description": "Learning beet!",

    "data_pack": {
        "load": ["src"]
    },

    "output": "build"
}
```

This describes a basic data pack which has a name, description, where to load in the data pack, and finally, where the output pack will be produced.

To test it out, you can create a data pack function inside the `src` folder.

```mcfunction title="src/data/example/function/hello.mcfunction"
say hello beet
```

## Build the pack

Now, navigating back to the root directory, you can invoke the build process and your pack will build, check it out in the output directory!

```sh
beet build
```

Alternatively, beet can watch the source files and automatically build the pack when it detects changes:

```sh
beet watch
```

## Link to a world

It is possible to automatically link the output pack to a world in your saves folder.

```sh
beet build --link "My World"
```

This will automatically look for the minecraft folder. If you are using a third party launcher, you can override this with the `MINECRAFT_PATH` environment variable.
