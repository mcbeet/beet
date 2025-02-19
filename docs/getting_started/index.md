# Getting Started
```{toctree}
:hidden:

plugins
```
Beet is a development toolkit for working with Minecraft data and resource packs. This section will explain how to install beet and get started with a first project.

## Installation
To start, you will need [Python 3.10+](https://python.org/). Then, you can install beet via pip. This will give you access to the CLI command that you can use inside your terminal.
```bash
pip install beet
```

## Creating a project
Beet projects start with a configuration file, `beet.json`, in the root of your project.

```{tab} beet.json
```json
{
  "name": "My First Pack",
  "description": "Learning beet!",

  "data_pack": {
    "load": ["src"]
  },

  "output": "build"
}
```

This beet config describes a basic data pack which has a name, description, where to load in the data pack, and finally, where the output pack will be produced. To test it out, you can create a data pack function inside the `src` folder.

```{tab} src/data/example/function/hello.mcfunction
```mcfunction
say hello beet
```

## Building the pack
Now, navigating back to the root directory, you can invoke the build process and your pack will build, check it out in the output directory!
```bash
beet build
```

Alternatively, beet can watch the source files and automatically build the pack when it detects changes:
```bash
beet watch
```

## Linking to a world
It is possible to automatically link the output pack to a world in your saves folder.
```bash
beet build --link "My World"
```

This will automatically look for the minecraft folder. If you are using a third party launcher, you can override this with the `MINECRAFT_PATH` environment variable.
