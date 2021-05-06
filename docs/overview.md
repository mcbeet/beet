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

### Namespaced file identifiers

The object hierarchy is a 1-to-1 representation that lets you work with data packs as pure Python objects. However, it can be a bit tedious to navigate depending on what you're trying to do. Most of the time, it's easier to reason about files in the data pack with their namespaced identifiers, to reflect the way we interact with them in-game.

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

def on_bind(function: Function, pack: DataPack, namespace: str, path: str):
    print(function)
    print(pack)
    print(namespace)
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
