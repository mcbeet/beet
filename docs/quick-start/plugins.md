---
icon: lucide/blocks
---

# Plugins
A beet plugin is essentially a Python function that takes the build context as an argument.

```py title="my_plugins.py"
from beet import Context, Function

def add_greeting(ctx: Context):
    ctx.data["example:hello"] = Function(["say hello from a plugin"])
```

The `Context` object lets you access the data pack with the `data` attribute. Similarly, you are able to get the resource pack with the `assets` attribute.

Just adding this file won't change anything. That's because plugins need to be used inside the beet pipeline in the config:

```json title="beet.json"
{
    "data_pack": {
        "load": ["src"]
    },
    "pipeline": [
        "my_plugins.add_greeting"
    ],
    "output": "build"
}
```

## Modifying existing files
Plugins can introspect and modify any part of the build. For example, the following plugin prepends every function with its name:

```py title="my_plugins.py"
from beet import Context, Function

def function_headers(ctx: Context):
    for name, func in ctx.data.functions.items():
        func.lines.insert(0, f"# {name}")
```
