# Loot table with yaml

`@loot_table minecraft:blocks/yellow_shulker_box`

```yaml
type: minecraft:block
pools:
  - rolls: 1
    entries:
      - type: minecraft:alternatives
        children:
          - type: minecraft:dynamic
            name: minecraft:contents
            conditions:
              - condition: minecraft:match_tool
                predicate:
                  items: [minecraft:air]
                  nbt: "{drop_contents:1b}"
          - type: minecraft:item
            name: minecraft:yellow_shulker_box
            functions:
              - function: minecraft:copy_name
                source: block_entity
              - function: minecraft:copy_nbt
                source: block_entity
                ops:
                  - source: Lock
                    target: BlockEntityTag.Lock
                    op: replace
                  - source: LootTable
                    target: BlockEntityTag.LootTable
                    op: replace
                  - source: LootTableSeed
                    target: BlockEntityTag.LootTableSeed
                    op: replace
              - function: minecraft:set_contents
                entries:
                  - type: minecraft:dynamic
                    name: minecraft:contents
```

`@function isolated:thing`

```mcfunction
say this is not affected
```

`@function_tag minecraft:tick`

```json
{
  "values": ["isolated:thing"]
}
```

`@resource_pack assets/minecraft/sounds.yml`

```yaml
block.note_block.bit_1:
  sounds:
    - block/note_block/bit_1
  subtitle: subtitles.block.note_block.note
```
