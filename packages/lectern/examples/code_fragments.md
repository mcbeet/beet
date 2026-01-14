# Basic data pack

## Visible directives

`@function demo:foo`

```mcfunction
say foo
```

`@function demo:bar`

```mcfunction
say bar
```

## Hidden directives

<!-- @function demo:hidden_foo -->

```mcfunction
say hidden foo
```

<!-- @function demo:hidden_bar -->

```mcfunction
say hidden bar
```

## Embedded directives

```mcfunction
# @function demo:embedded_foo
say embedded foo

# @function demo:embedded_bar
say embedded bar
```
