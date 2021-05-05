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

Data packs and resource packs are identical in nature and only differ in the types of resources they can contain. As a result, `beet` derives the concrete `DataPack` and `ResourcePack` classes from a generic `Pack` definition. It's the shared base class that's responsible for implementing all the operations that we'll be discussing in the next sections, so the examples will only be focusing on data packs as resource packs would work exactly the same.

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

<!--
## File handles

The core `beet` file handles make all the interactions with the filesystem lazy and as efficient as possible. They're responsible for exposing files in their serialized or deserialized state transparently.
-->
