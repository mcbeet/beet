# Plugin test

```python
# @plugin

# Wait for lectern to be done
yield

# Copy all functions
for name, function in list(ctx.data.functions.items()):
    ctx.data[f"{name}_copy"] = function
```

`@plugin`

```python
from typing import Mapping
from dataclasses import replace

from beet import Function
from lectern import Directive, Document, Fragment

def handle_with_logging_modifier(
    fragment: Fragment,
    directives: Mapping[str, Directive],
) -> Fragment:
    if fragment.modifier == "with_logging":
        function = fragment.as_file(Function)
        function.prepend(f"say running {fragment.arguments[0]}")
        fragment = replace(fragment, file=function)
    return fragment

ctx.inject(Document).loaders.append(handle_with_logging_modifier)
```

`@function(with_logging) foo`

```mcfunction
say hello
```
