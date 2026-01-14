# This file is part of a beet project

The @require directive calls `ctx.require()` and allows you to load arbitrary plugins.

> `@require plugin1`
>
> `@require plugin2`

The @skip directive does nothing, but it can be useful with the plain text embedded syntax to skip certain sections.

```mcfunction
# @function embedded:foo
say foo
# @skip
This won't be included anywhere
# @function embedded:bar
say bar
```

Check out the [next file](hello.md) we're going to try our custom directive.
