# Update guide

```{admonition} Warning
:class: warning
This part is intended for maintainers.
```

This little guide documents  checklist to update beet when a new minecraft version came out.

## Update `LATEST_MINECRAFT_VERSION`

In `beet/library/base.py` you need to update the variable at every minor update (going from 1.21.1 to 1.21.2).



## Changing the pack format

Both in `beet/library/data_pack.py` and `beet/library/resource_pack.py` require the pack format to be changed in the `pack_format_registry` variable.

- If the new version is a patch (going from 1.21.1 to 1.21.2), you need to update the `(1, 21)` entry
- If it's a minor version (1.21.4 to 1.22), you need to add the `(1, 22)` entry


## Adding new registries

Reading the changelog, you need to add the new registries in both `beet/library/data_pack.py` and `beet/library/resource_pack.py`.

To be sure that you don't miss something, you can run : 
```bash
poetry run python tests/test_scopes.py <minecraft_version>
```


## Follow Contributing rules in the Readme
Running the test suite, code formatter and type checker.


