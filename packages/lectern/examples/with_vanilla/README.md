# Load vanilla resources

## Basics

The `lectern.contrib.vanilla` plugin can copy resources from the vanilla data pack and resource pack.

`@vanilla assets/minecraft/lang/en_us.json`

The directive can select multiple files at once.

`@vanilla data/minecraft/tags/items/anvil.json assets/minecraft/blockstates/anvil.json`

It's possible to specify a destination ending in `:` before the file pattern. If the pattern refers to multiple files, the destination must be a directory.

`@vanilla assets/foo/lang/dummy.json: assets/minecraft/lang/en_us.json`

File patterns are regular expressions, they can match multiple files at once.

`@vanilla assets/minecraft/lang/fr_.*`

> [!WARNING]
> Beet statically analyzes every pattern to only mount the necessary vanilla resources before matching the regex. Very generic patterns like `@vanilla data/minecraft/.*json` will be slower to execute as the static base path doesn't help much with reducing the set of files to scan.

The destination can contain references to capture groups in the pattern.

`@vanilla assets/foo/models/\1: assets/minecraft/models/(block|item)/.+_sapling.json`

## Load by resource location

The plugin also registers directives similar to `@vanilla` but that work with a specific resource type and let you specify patterns as resource locations instead of having to write out the complete file path.

`@vanilla_texture minecraft:block/stone`

Instead of regular expressions, these resource location patterns only support gitignore-like matching syntax.

`@vanilla_worldgen_noise minecraft:aquifer* minecraft:noodle`

The directives still support mounting the resource to a different destination. The destination must be a resource location too.

`@vanilla_structure foo:better_igloo: minecraft:igloo/*`

## Override minecraft version

All directives default to loading files from the minecraft version configured in the current project. You con override that by specifying the version as a modifier between parentheses right after the name of the directive.

`@vanilla(1.18.2) assets/foo/lang/old_us.json: assets/minecraft/lang/en_us.json`
