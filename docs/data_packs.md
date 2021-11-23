---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
---

# Data Packs

The `beet` library allows you to work with data packs at a high level. You can create data pack objects from scratch or from existing data packs on the filesystem. The library can load zipped data packs too. By representing data packs as a hierarchy of rich Python objects, you can easily inspect the content of the data pack and perform bulk operations. When you're done you can write the data pack back to the filesystem. Again, `beet` can generate a zipfile instead depending on your requirements.

## From scratch

The `DataPack` constructor lets you create data packs from scratch.

```{code-cell}
from beet import DataPack

DataPack()
```

You can specify `pack.mcmeta` information directly in the constructor or provide a `JsonFile` instance.

```{code-cell}
from beet import JsonFile

p1 = DataPack(name="my_data_pack", description="Awesome data pack", pack_format=6)
p2 = DataPack(
    name="my_data_pack",
    mcmeta=JsonFile({"pack": {"description": "Awesome data pack", "pack_format": 6}}),
)
p1 == p2
```

You can add an icon by providing a `PngFile` instance.

```{code-cell}
from beet import PngFile
from PIL import Image

pack = DataPack(icon=PngFile(Image.new("RGB", (128, 128), "red")))
pack.icon.image
```

## Loading existing data packs

If you create a data pack object with the `path` argument you will be able to load an existing data pack. The path can point to a directory or a zipfile.

```{code-cell}
example = DataPack(path="../examples/load_basic/src")
example["demo"]
```

```{code-cell}
for key, value in example.content:
    print(key, type(value))
```

```{eval-rst}
.. autoclass:: beet.library.data_pack.DataPack
  :members: save

  Data packs are dict-like objects holding a collection of namespaces. You can use the :meth:`save`
```
