---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
---

# General overview

The `beet` project tries to provide consistent abstractions that work well together. A lot of care goes into leveraging existing patterns and intuitions to make the API as familiar as possible.

To keep the API surface manageable, abstractions are designed to provide orthogonal functionality. When things happen to fit into each other it's generally not an accident.

## Data packs and resource packs

The `beet` library allows you to work with data packs and resource packs at a high level. Data pack and resource pack objects are fast and flexible primitives that make it easy inspect, generate, merge and transform files, and perform bulk operations.

Data packs and resource packs are identical in nature and only differ in the types of resources they can contain. As a result, `beet` derives the concrete `DataPack` and `ResourcePack` classes from a generic `Pack` definition. It's the shared base class that's responsible for implementing all the operations that we'll be discussing in the next sections.

### Object hierarchy

Data packs are dict-like objects holding a collection of namespaces. Each key maps the name of the namespace to a `Namespace` instance that contains all the files within the namespace. Namespaces are created automatically and you shouldn't need to create them manually.

```{code-cell}
from beet import DataPack

pack = DataPack()
demo_namespace = pack["demo"]
demo_namespace
```

Namespaces themselves are also dict-like objects. Files inside namespaces are organized into homogeneous containers. Each key maps a file type to the associated file container that contains all the files of the given type within the namespace.

```{code-cell}
from beet import Function

demo_functions = demo_namespace[Function]
demo_functions
```

These namespace containers are dict-like objects as well. Each key corresponds to a file path from the root directory of the container and maps to the associated file instance.

```{code-cell}
demo_functions["foo"] = Function(["say hello"])
demo_functions
```

If you're already familiar with data packs, the overall structure of the object hierarchy shouldn't be surprising as it directly maps to the filesystem representation.

```{code-cell}
pack == {
    "demo": {
        Function: {
            "foo": Function(["say hello"])
        }
    }
}
```

Namespace containers are also available through attribute access. This is usually the syntax you'll be looking for as it's a bit more readable and provides better autocompletion.

```{code-cell}
demo_namespace.functions["foo"] is demo_namespace[Function]["foo"]
```

You can even omit the container entirely when adding files to the namespace. The namespace will dispatch the file to the appropriate container automatically depending on its type.

```{code-cell}
demo_namespace["bar"] = Function(["say world"])
demo_namespace.functions
```

### Resource locations

The object hierarchy is a 1-to-1 representation that lets you work with data packs as pure Python objects. However, it can be a bit tedious to navigate depending on what you're trying to do. Most of the time, it's easier to reason about files in the data pack with their namespaced location, to reflect the way we interact with them in-game.

Data pack objects let you access files in a single lookup with proxies that expose a namespaced view of all the files of a specific type over all the namespaces in the data pack.

```{code-cell}
pack = DataPack()

pack.functions["demo:foo"] = Function()
pack.functions["demo:foo"] is pack["demo"].functions["foo"]
```

Proxy attributes are always in sync with the underlying namespaces. You can also omit the attribute when adding files to data packs. The data pack object will dispatch the file to the appropriate proxy depending on its type.

```{code-cell}
pack["demo:bar"] = Function()
pack.functions == {
    "demo:foo": Function(),
    "demo:bar": Function(),
}
```

### Extra files

Unfortunately, data packs and resource packs aren't limited to neatly namespaced files and can contain extra files at the pack level and at the namespace level. Still, the `beet` library handles extra files as first-class citizens. In fact, `pack.mcmeta` and `pack.png` are both handled through this mechanism.

```{code-cell}
from beet import JsonFile

pack = DataPack()

pack.extra == {
  "pack.mcmeta": JsonFile({"pack": {"description": "", "pack_format": 6}})
}
```

The `extra` attribute maps filenames to their respective file handles. To make it easier to access, the `pack.mcmeta` file is also directly pinned to the data pack instance.

```{code-cell}
pack.mcmeta is pack.extra["pack.mcmeta"]
```

The `pack.png` file works exactly the same. It's pinned to the `icon` attribute.

```{code-cell}
from beet import PngFile
from PIL import Image

pack.icon = PngFile(Image.new("RGB", (128, 128), "red"))
pack.extra["pack.png"].image
```

For extra files at the namespace level we can look at the `sounds.json` file in resource packs. The file is pinned to the `sound_config` attribute.

```{code-cell}
from beet import ResourcePack, SoundConfig

pack = ResourcePack()

pack["minecraft"].sound_config = SoundConfig()
pack["minecraft"].sound_config is pack["minecraft"].extra["sounds.json"]
```

Extra files are loaded according to the schema returned by the `get_extra_info` function. The returned dictionary tells the code that loads the data pack or the resource pack what files it should be looking for in addition to namespaced files, and how to load them depending on the associated type. You can add arbitrary files to the `extra` container when saving.

```{code-cell}
DataPack.get_extra_info()
```

```{code-cell}
from beet import ResourcePackNamespace

ResourcePackNamespace.get_extra_info()
```

### Mcmeta accessors

Data pack metadata is stored in the `pack.mcmeta` file in the `extra` container. The file is pinned to the `mcmeta` attribute, but to make things even more convenient data pack objects let you access the description and the pack format directly through pinned attributes.

```{code-cell}
pack = DataPack()

pack.description = "My awesome pack"
pack.pack_format = 42

print(pack.mcmeta.text)
```

With resource packs you can use the pinned `language_config` attribute to register custom languages.

```{code-cell}
from beet import Language

pack = ResourcePack()

pack["minecraft:custom"] = Language({"menu.singleplayer": "Modified singleplayer button"})
pack.language_config["custom"] = {
    "name": "Custom",
    "region": "Custom",
    "bidirectional": False,
}

print(pack.mcmeta.text)
```

### Namespace binding callbacks

Data packs and resource packs feature certain types of files that have a special kind of relationship and that are often created together. One example would be functions and function tags. Namespaced files have a binding callback that can run arbitrary code when they're added to data packs. For example the `Function` constructor allows you to specify a list of function tags that will be associated with the function once it's added to the data pack.

```{code-cell}
from beet import FunctionTag

pack = DataPack()
pack["demo:foo"] = Function(["say hello"], tags=["minecraft:tick"])

pack.function_tags == {
    "minecraft:tick": FunctionTag({"values": ["demo:foo"]}),
}
```

The same thing works with textures and texture mcmeta in resource packs. Sound files can also automatically register themselves in `sounds.json`.

```{code-cell}
from beet import Texture, TextureMcmeta
from PIL.ImageDraw import Draw

pack = ResourcePack()

image = Image.new("RGB", (16, 32), "green")
d = Draw(image)
d.rectangle([0, 16, 16, 32], fill="yellow")

pack["minecraft:block/dirt"] = Texture(image, mcmeta={"animation": {"frametime": 20}})

pack.textures_mcmeta == {
    "minecraft:block/dirt": TextureMcmeta({"animation": {"frametime": 20}}),
}
```

You can also create files with a custom `on_bind` callback.

```{code-cell}
pack = DataPack()

def on_bind(function: Function, pack: DataPack, path: str):
    print(function)
    print(pack)
    print(path)

pack["demo:foo"] = Function(["say hello"], on_bind=on_bind)
```

### Merging

Because all the data stored in data packs is ultimately represented by file instances, `beet` can implement a very straight-forward merging strategy that lets conflicting files decide if they should overwrite or merge with existing ones. For example, tag files will be merged together.

```{code-cell}
p1 = DataPack()
p1["demo:foo"] = Function(["say hello"], tags=["minecraft:tick"])

p2 = DataPack()
p2["demo:bar"] = Function(["say world"], tags=["minecraft:tick"])

p1.merge(p2)

dict(p1.content) == {
    "demo:foo": Function(["say hello"]),
    "demo:bar": Function(["say world"]),
    "minecraft:tick": FunctionTag({"values": ["demo:foo", "demo:bar"]}),
}
```

In resource packs, conflicting languages will preserve translations from both files.

```{code-cell}
p1 = ResourcePack()
p1["minecraft:custom"] = Language({"demo.foo": "hello"})

p2 = ResourcePack()
p2["minecraft:custom"] = Language({"demo.bar": "world"})

p1.merge(p2)

print(p1.languages["minecraft:custom"].text)
```

### Matching key patterns

The object hierarchy that represents data packs and resource packs contains dict-like objects that have a few extra utilities compared to regular Python dictionaries. Data packs, namespace containers and proxies are all dict-like objects with string keys that expose a `match` method that returns a set of all the keys matching the given patterns.

```{code-cell}
pack = DataPack()
pack["demo:foo"] = Function(["say hello"])
pack["demo:bar"] = Function(["say world"])

pack.match("d*")
```

```{code-cell}
pack["demo"].functions.match("f*")
```

```{code-cell}
pack.functions.match("demo:*")
```

You can specify multiple patterns. The exclamation mark lets you invert a pattern.

```{code-cell}
pack.functions.match("demo:*", "!demo:foo")
```

## File handles

The core `beet` file handles make all the interactions with the filesystem lazy and as efficient as possible. They're responsible for exposing files in their serialized or deserialized state transparently and avoiding deserialization entirely whenever possible. This allows `beet` to load data packs and resource packs with thousands of files instantly.

### Text files and binary files

The implementation defines a base `File` class that's generic over the types of its serialized and deserialized representation. Files that inherit from `TextFileBase` store their serialized content as strings while files that inherit from `BinaryFileBase` store their serialized content as bytes. All concrete file types are then derived from one or the other. The most straight-forward concrete file types are `TextFile` and `BinaryFile`.

```{code-cell}
from beet import TextFile

TextFile("hello")
```

```{code-cell}
from beet import BinaryFile

BinaryFile(b"\x00\x01\x02\x03")
```

You can create files by providing the serialized or deserialized content to the constructor, or specifying a source path to an existing file. `TextFile` and `BinaryFile` are a bit special though because their serialized and deserialized state are identical.

```{code-cell}
handle = TextFile(source_path="../examples/load_basic/beet.json")
handle
```

Note that this didn't perform any filesystem operation. The file handle is still in an unloaded state. Accessing the content in one way or another will load the file and discard the source path.

```{code-cell}
print(handle.text)
handle
```

### File states

File handles can be in three distinct states:

- Unloaded

  Files with a source path are unloaded. You can use the `ensure_source_path()` method to make sure that files are in an unloaded state and retrieve the source path.

- Serialized

  Files with plain string or bytes content are treated as serialized. You can use the `ensure_serialized()` method to get the serialized content of the file no matter the state it's currently in. Text files let you access the string content through the `text` attribute and binary files let you access the raw bytes through the `blob` attribute.

- Deserialized

  Files with a content that's different from a plain string or bytes are treated as deserialized. You can use the `ensure_deserialized()` method to get the deserialized content of the file no matter the state it's currently in. Classes deriving from `TextFile` and `BinaryFile` will expose the most suited and practical deserialized representation depending on the type of file.

Most of the time, code that works with files doesn't need to know about the state it's currently in. If the file is already deserialized then accessing the deserialized representation will simply return the current content of the file, otherwise `beet` will transparently load the file if necessary and turn the string or bytes into the deserialized representation. The same thing happens when trying to access the string or bytes content. If the file is not loaded then `beet` will transparently load it on the fly and if the file is in its deserialized state it will automatically turn it into its serialized representation.

The different states make it possible to optimize various operations. For instance, dumping an unloaded file to the filesystem results in a native file copy operation, so if you're shuffling files around in a data pack you're not incurring extra loading and parsing costs by using the provided abstractions. Similarly, if you're using `beet` to zip a data pack the file handles won't needlessly turn any of the files into their deserialized representation. Another example would be equality checks. If two files are unloaded and point to the same source path they're considered equal.

### Json files

With the `JsonFile` class we can play around and see the differences between the unloaded, serialized, and deserialized states.

```{code-cell}
from beet import JsonFile

handle = JsonFile(source_path="../examples/load_basic/beet.json")
handle
```

The file is currently unloaded. By accessing the `text` attribute, which is the same as calling the `ensure_serialized()` method, `beet` will load the file and return the string content.

```{code-cell}
print(handle.text)
handle
```

We can see that now the content of the file holds the string representing the json file. Json files expose their deserialized content as a dictionary of plain Python objects. By accessing the `data` attribute, which is the same as calling the `ensure_deserialized()` method, `beet` will parse the json and return the deserialized content.

```{code-cell}
del handle.data["data_pack"]["load"]
handle
```

Now the file is in its deserialized state, and any further code accessing the `data` attribute will be able to operate directly on the parsed dictionary. However, accessing the `text` attribute will transform the file into its serialized state again.

```{code-cell}
print(handle.text)
handle
```

The different states aren't something you explicitly need to worry about in code that works with files but it's good to keep in mind that it doesn't play well with weird access patterns.

```{code-cell}
handle.data["data_pack"]["pack_format"] = 0

for i in range(3):
    handle.data["data_pack"]["pack_format"] += 1
    print(handle.text)
```

As you could've guessed, this kind of code is pretty problematic because even though it doesn't look like there's much going on, each iteration of the loop actually ends up parsing and serializing json.

### Png files

Another example of files with really distinct unloaded, serialized and deserialized states are png files.

```{code-cell}
from beet import PngFile

handle = PngFile(source_path="../logo.png")
handle
```

As usual, the file starts out unloaded. Because images are binary files, we need to access the `blob` attribute to get the serialized content.

```{code-cell}
handle.blob[:20]
```

Now the file is loaded and isn't linked to the original source file anymore.

```{code-cell}
handle.source_path is None
```

Accessing the `image` attribute will deserialize the file into a `PIL` image, which makes it possible to edit the image programmatically.

```{code-cell}
handle.image = handle.image.rotate(45)
handle.image.thumbnail((128, 128))
handle.image
```

### Files and data packs

The files used in data packs and resource packs are derived from the core file handles. For example, you can create function files from a source path, a string representing the content of the function, or a list of strings corresponding to the lines of the function.

```{code-cell}
pack = DataPack(path="../examples/load_basic/src")
pack.functions["demo:foo"]
```

As you can see, when we load an unzipped data pack all the files remain in their unloaded state. The moment we start interacting with the content of the function `beet` will load the file automatically.

```{code-cell}
pack.functions["demo:foo"].lines.append("say bar")
pack.functions["demo:foo"]
```

## The toolchain

In the previous sections we briefly introduced some of the operations that you can do with data packs and resource packs. For example, you can easily add generated resources to a data pack by writing a simple script that uses the previously mentioned APIs. The problem is that none of these scripts are likely to be reusable.

The `beet` toolchain is a fully-fledged build system that lets you implement the behavior you need as plugins that can be composed with one another. It helps with making your code reusable and not just one-off scripts, and provides a cohesive developer experience.

The idea is that each plugin is a callable Python object that accepts a context that exposes a data pack and a resource pack. The toolchain initializes the context with an empty data pack and an empty resource pack, and then feeds it to the plugins one by one. When a plugin is called it can load and merge existing data packs into the context, inspect the various files, or generate resources programmatically. When all the plugins are done, the toolchain can then output the generated data pack or link it to a Minecraft world.

### Plugins

We're going to transform a simple script into a plugin to introduce the concept one step at a time.

```python
from beet import DataPack, Function

with DataPack(path="out/greeting_data_pack") as data:
    data["greeting:hello"] = Function(["say hello"] * 5, tags=["minecraft:load"])
```

If you download and run this script with the Python interpreter, it will create a data pack in a new "out" directory called "greeting_data_pack". The script generates a function that says "hello" five times when the data pack is loaded.

```
$ tree out
out
└── greeting_data_pack
    ├── data
    │   ├── greeting
    │   │   └── functions
    │   │       └── hello.mcfunction
    │   └── minecraft
    │       └── tags
    │           └── functions
    │               └── load.json
    └── pack.mcmeta

7 directories, 3 files
```

Now, let's say you want to be able to greet players like this in another data pack. The first thing to do would be to separate the logic in its own function.

```python
from beet import DataPack, Function

def add_greeting(data: DataPack):
    data["greeting:hello"] = Function(["say hello"] * 5, tags=["minecraft:load"])

with DataPack(path="out/greeting_data_pack") as data:
    add_greeting(data)
```

Running the script still does the same thing as before, but now if you wanted to create a second data pack you could use the `add_greeting` function to add the same greeting to the second data pack.

It turns out that now that we have extracted the logic into a function that takes a data pack as input, we can easily turn it into a `beet` plugin.

```python
from beet import Context, Function

def add_greeting(ctx: Context):
    ctx.data["greeting:hello"] = Function(["say hello"] * 5, tags=["minecraft:load"])
```

The plugin takes a `Context` object that lets you access the data pack with the `data` attribute. Implementing our logic as a plugin means that we no longer need to create the data pack ourselves and call the function manually. Instead, we can create a `beet.json` config file and let the toolchain create the data pack for us. The toolchain knows how to call our plugin on its own so we removed the rest of the code.

```json
{
  "name": "greeting",
  "output": "out",
  "pipeline": ["my_plugins.add_greeting"]
}
```

The `name` option sets the name of the project to "greeting". The `output` option tells the toolchain to output the generated data pack into a directory called "out". The `pipeline` option lets you specify the plugins that should be called when building the data pack. If you save the `add_greeting` plugin in a file called "my_plugins.py", you'll be able to run the `beet` command to generate the data pack.

```
$ beet
Building project...

Done!
```

We can see that again, this results in the exact same data pack as before, but with the added benefit that now we can potentially reuse our plugin in other projects.

```
$ tree out
out
└── greeting_data_pack
    ├── data
    │   ├── greeting
    │   │   └── functions
    │   │       └── hello.mcfunction
    │   └── minecraft
    │       └── tags
    │           └── functions
    │               └── load.json
    └── pack.mcmeta

7 directories, 3 files
```

### The context object

We've seen that plugins take a `Context` object as input, but what exactly is it? What can you do with it?

So far we know there's a `data` attribute that holds a `DataPack` instance. This data pack starts out completely empty, and then as plugins get called, they can inspect the content of the data pack and change it. When the build ends the toolchain then outputs the resulting data pack in one way or another.

The `assets` attribute holds a `ResourcePack` instance. It works exactly like the `data` attribute and plugins can generate assets that the toolchain outputs alongside the data pack at the end of the build. We can try this out by making the `add_greeting` plugin greet players in their own language.

```python
from beet import Context, Function, Language

def add_greeting(ctx: Context):
    ctx.assets["minecraft:en_us"] = Language({"greeting.hello": "hello"})
    ctx.assets["minecraft:fr_fr"] = Language({"greeting.hello": "bonjour"})

    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * 5,
        tags=["minecraft:load"],
    )
```

We're using the `assets` attribute to add language files to the resource pack. We also changed the function to use the `tellraw` command to translate the message depending on the player's language.

```
$ tree out
out
├── greeting_data_pack
│   ├── data
│   │   ├── greeting
│   │   │   └── functions
│   │   │       └── hello.mcfunction
│   │   └── minecraft
│   │       └── tags
│   │           └── functions
│   │               └── load.json
│   └── pack.mcmeta
└── greeting_resource_pack
    ├── assets
    │   └── minecraft
    │       └── lang
    │           ├── en_us.json
    │           └── fr_fr.json
    └── pack.mcmeta

11 directories, 6 files
```

After running the `beet` command we can see that the toolchain generated a resource pack called "greeting_resource_pack" in the output directory.

Now, let's say the translated message could be used on its own in another project that greets players differently. We can extract the code that adds the language files into its own plugin.

```python
from beet import Context, Function, Language

def add_greeting_translations(ctx: Context):
    ctx.assets["minecraft:en_us"] = Language({"greeting.hello": "hello"})
    ctx.assets["minecraft:fr_fr"] = Language({"greeting.hello": "bonjour"})

def add_greeting(ctx: Context):
    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * 5,
        tags=["minecraft:load"],
    )
```

The `add_greeting_translations` plugin is now responsible for adding our translations to the generated resource pack. We can add it to the `pipeline` option in the `beet.json` config file.

```json
{
  "name": "greeting",
  "output": "out",
  "pipeline": [
    "my_plugins.add_greeting_translations",
    "my_plugins.add_greeting"
  ]
}
```

The resulting data pack and resource pack didn't change, but now we're composing the behavior of two plugins together.

The basic idea behind the `Context` object is that it's responsible for holding the shared state that makes it possible for plugins to cooperate. In addition to the data pack and the resource pack, plugins can use the `Context` object to access a bunch of other things such as the caching and generator APIs, the template manager, background workers and pipeline metadata.

An example would be using the `meta` attribute to make the `add_greeting` plugin configurable. Right now it always shows the message five times but by using pipeline metadata we can configure how many repetitions we want right from the config file.

```python
from beet import Context, Function, Language

def add_greeting_translations(ctx: Context):
    ctx.assets["minecraft:en_us"] = Language({"greeting.hello": "hello"})
    ctx.assets["minecraft:fr_fr"] = Language({"greeting.hello": "bonjour"})

def add_greeting(ctx: Context):
    greeting_count = ctx.meta["greeting_count"]

    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * greeting_count,
        tags=["minecraft:load"],
    )
```

Now in the config file we can use the `meta` option to specify the "greeting_count" used by the `add_greeting` plugin.

```json
{
  "name": "greeting",
  "output": "out",
  "pipeline": [
    "my_plugins.add_greeting_translations",
    "my_plugins.add_greeting"
  ],
  "meta": {
    "greeting_count": 7
  }
}
```

The generated data pack now shows the greeting seven times when the data pack is loaded.

### Plugin dependencies

You might have noticed that in the previous example, when we separated the code that adds the translations into its own plugin, we made it easy to introduce a potential bug.

The `add_greeting_translations` plugin can be used on its own, it simply adds language files to the resource pack. However, the `add_greeting` plugin relies on being able to use the message defined in the language files. Now that the translations are in their own plugin, the `add_greeting` plugin can't be used on its own anymore in the `pipeline` option.

```json
{
  "name": "greeting",
  "output": "out",
  "pipeline": ["my_plugins.add_greeting"],
  "meta": {
    "greeting_count": 7
  }
}
```

If we forget to use `add_greeting_translations` we won't see any output in-game. The `add_greeting` plugin requires you to use `add_greeting_translations` as well.

It's not always this trivial to keep track of plugin dependencies manually so the `Context` object provides a `require()` method that adds a given plugin to the pipeline if it hasn't already been called.

```python
from beet import Context, Function, Language

def add_greeting_translations(ctx: Context):
    ctx.assets["minecraft:en_us"] = Language({"greeting.hello": "hello"})
    ctx.assets["minecraft:fr_fr"] = Language({"greeting.hello": "bonjour"})

def add_greeting(ctx: Context):
    ctx.require(add_greeting_translations)
    greeting_count = ctx.meta["greeting_count"]

    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * greeting_count,
        tags=["minecraft:load"],
    )
```

Now the resource pack gets generated again and the message properly shows up in-game. The `add_greeting_translations` plugin can still be used on its own if we want to use the translated message for something else, but using the `add_greeting` plugin will now make sure that the `add_greeting_translations` plugin has been called before adding the function that greets players.

### The pipeline

We've seen how plugins can cooperate with the `Context` object, and we just learned how to make plugins that depend on other plugins. In these sections we mentioned the pipeline a few times already but never actually explained what it is.

To put it simply, the pipeline is the thing that runs plugins. Plugins can only run once per pipeline. The pipeline can import plugins dynamically and knows when a plugin has already been executed. This means that if a plugin is required multiple times, it will still only be executed once.

One thing that we didn't experiment with until now is that plugins are actually wrapping each other, and not just being called sequentially. Each plugin in the pipeline surrounds the ones after, like layers. The last plugin in the pipeline is the innermost layer.

```
┌────────────────────────┐
│ Context initialization │
└─┬──────────────────────┘
  │
  │   ┌──────────────────────────────────────────────┐
  │   │ def add_greeting_translations(ctx: Context): │
  │   │     ...                                      │
  │   │   ┌─────────────────────────────────┐        │
  │   │   │ def add_greeting(ctx: Context): │        │
  │   │   │     ...                         │        │
  │   │   │                                 │        │
  └───┼───┼───► Entry phase ────────────────┼────────┼───► Exit phase
      │   │                                 │        │
      │   └─────────────────────────────────┘        │
      └──────────────────────────────────────────────┘
```

If we apply this to the example we've been using so far, `add_greeting_translations` conceptually surrounds `add_greeting`, because the `add_greeting_translations` plugin is required by `add_greeting`.

The pipeline runs all plugins from the outermost layer until it reaches the innermost layer. Then the execution goes back through each plugin in reverse, like nested context managers. Because of this each plugin has an entry phase and an exit phase. Plugins can run code during the exit phase by using the `yield` statement to wait for the execution to come back, when all the dependent plugins are done.

```python
from beet import Context, Function, Language

def add_greeting_translations(ctx: Context):                              # [3]
    ctx.meta["greeting_translations"] = {}

    yield                                                                 # [4]

    for key, translations in ctx.meta["greeting_translations"].items():   # [6]
        for code, value in translations.items():
            ctx.assets.languages.merge(
                {f"minecraft:{code}": Language({f"greeting.{key}": value})}
            )

def add_greeting(ctx: Context):                                           # [1]
    ctx.require(add_greeting_translations)                                # [2]
    greeting_count = ctx.meta["greeting_count"]

    ctx.meta["greeting_translations"]["hello"] = {                        # [5]
        "en_us": "hello",
        "fr_fr": "bonjour",
    }

    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * greeting_count,
        tags=["minecraft:load"],
    )
```

To illustrate the idea, we made a few changes to the `add_greeting_translations` plugin. We now generate the language files depending on the messages added to the `greeting_translations` dictionary by dependent plugins. This definitely adds a lot of unnecessary complexity to our simple example, but you could imagine the pattern being useful on a larger scale.

Let's walk through the example step by step:

1. The pipeline first begins with `add_greeting`.
2. `add_greeting` requires `add_greeting_translations`, so all the remaining code gets conceptually surrounded by `add_greeting_translations`.
3. The execution then jumps to `add_greeting_translations` and the `greeting_translations` dictionary gets initialized.
4. Next, since the yield statement waits for dependent plugins to be done, the pipeline resumes the execution of the `add_greeting` plugin.
5. The `add_greeting` plugin runs to completion and the `greeting_translations` dictionary now contains the message needed by the tellraw command.
6. All the plugins that require `add_greeting_translations` are done so the execution resumes and the plugin generates language files according to the updated `greeting_translations` dictionary.

This is a pretty advanced topic. Most plugins don't actually need to care about any of this, but it can be helpful to remember that the `yield` statement lets you wait for dependent plugins to be done.

### Service injection

Our previous attempt at generalizing the plugin responsible for generating language files helped us introduce the `yield` statement, but it's ultimately not that much of an improvement compared to dealing with the language files directly. The API is also kind of implicit so it would be nice if we could package everything into a proper abstraction.

The context object acts as a very basic service container. The `inject()` method lets you instantiate and retrieve service objects that live for the duration of the current pipeline.

```python
from beet import Context, Function

def add_greeting(ctx: Context):
    i18n = ctx.inject(Internationalization)
    i18n.set("greeting.hello", en_us="hello", fr_fr="bonjour")

    greeting_count = ctx.meta["greeting_count"]

    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * greeting_count,
        tags=["minecraft:load"],
    )
```

Let's try to come up with an `Internationalization` service that can be used to create translated messages. We removed the `add_greeting_translations` plugin and instead of having to populate some arbitrary context metadata, we're going to implement a more explicit `set()` method for creating translated messages.

```python
from collections import defaultdict
from typing import DefaultDict

from beet import Language

class Internationalization:
    languages: DefaultDict[str, Language]

    def __init__(self, ctx: Context):
        self.languages = defaultdict(Language)
        ctx.require(self.add_translations)

    def add_translations(self, ctx: Context):
        yield
        ctx.assets["minecraft"].languages.merge(self.languages)

    def set(self, key: str, **kwargs: str):
        for code, message in kwargs.items():
            self.languages[code].data[key] = message
```

Services are instantiated when they're injected for the first time with the context object as argument. The `set()` method adds translated messages to the language files stored in the `languages` attribute. When the `Internationalization` service is created, the constructor requires its `add_translations` method as a plugin. The plugin uses the `yield` statement to wait for all the plugins using the `Internationalization` service to be done and then merges the generated language files.

In general, service injection makes it possible to package context operations into proper abstractions. With the `inject()` method we refactored the awkward `add_greeting_translations` plugin into a decoupled, strongly-typed `Internationalization` service with an explicit API.
