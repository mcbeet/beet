from nbtlib import List, String

SUMMON_INIT_TAG = "custom_summon_init"

macro
    summon
        entity=minecraft:entity_summon
        pos=minecraft:vec3
        nbt=minecraft:nbt_compound_tag
        body=mecha:nested_root:
    nbt = nbt.evaluate()
    nbt.setdefault("Tags", List[String]()).append(String(SUMMON_INIT_TAG))
    summon entity pos nbt
    as @e[type=entity.get_canonical_value(), tag=SUMMON_INIT_TAG] at @s:
        yield body
        tag @s remove SUMMON_INIT_TAG

# Overload to make nbt optional
macro
    summon
        entity=minecraft:entity_summon
        pos=minecraft:vec3
        body=mecha:nested_root:
    summon entity pos {}:
        yield body

# Overload to make pos optional
macro
    summon
        entity=minecraft:entity_summon
        body=mecha:nested_root:
    summon entity ~ ~ ~:
        yield body

summon zombie ~ ~ ~ {Tags: ["my_custom_mob"]}:
    say Hello I just spawned!
    effect give @e[distance=..3] poison

summon zombie 1 2 3:
    say no nbt

summon zombie 1 2 3:
    Tags: ["using_nested_yaml"]

summon zombie:
    say no position or nbt

def wtf():
    say hello

summon zombie ~1 ~2 ~3:
    wtf()
