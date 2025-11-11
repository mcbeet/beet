# Script directive example

`@script`

```
@function demo:script_foo
say something

{% for i in range(10) %}
@function demo:script_{{ i }}
say {{ i }}
{% endfor %}
```

This one is nested 🤯

`@script`

```
@script
@@function demo:script_nested
say wow

@script
@@script
@@@script
@@@@function demo:script_please_avoid_this
say no
```
