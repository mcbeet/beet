# Testing the define directive

`@define abc`

```
azertyuiop
```

`@define def`

```
{{ abc.strip() }}qsdfghjklm
```

`@define(strip_final_newline) math_message`

```
2 + 2 is {{ 2 + 2 }}
```

`@script`

```
@function demo:define_1
say {{ abc.strip() }}

@function demo:define_2
say {{ def.strip() }}

@function demo:define_3
say {{ math_message }} (end of citation)
```
