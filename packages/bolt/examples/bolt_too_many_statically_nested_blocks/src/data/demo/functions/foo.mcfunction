# test file by @TheNuclearNexus

from coc:modules/on import onEvent
from coc:modules/playerdb import PlayerDB
from coc:modules/armory import ClassRegistry
from nbtlib import Byte, Compound




item_modifier coc:item/armory/set_data [
  {
    "function": "minecraft:copy_nbt",
    "source": {
      "type": "minecraft:storage",
      "source": "coc:temp"
    },
    "ops": [
      {
        "source": "data",
        "target": "{}",
        "op": "merge"
      }
    ]
  }
]

def getReplaceSlots():
    return zip([100,101,102,103,-106], ['armor.feet', 'armor.legs', 'armor.chest', 'armor.head', 'weapon.offhand'])

def slotToArmor(slot):
    if slot == 100:
        return 'netherite_boots'
    elif slot == 101:
        return 'netherite_leggings'
    elif slot == 102:
        return 'netherite_chestplate'
    elif slot == 103:
        return 'netherite_helmet'
    return 'air'

with onEvent("inventory_changed", ./armory/detect):
    store result score $hasArmory coc.dummy clear @s #coc:armory{smithed:{id: "coc:armory"}} 0

    armory_data = PlayerDB.get().data.armory

    if score $hasArmory coc.dummy matches 0 if entity @s[tag=coc.equiped] function ./armory/unequip
    if score $hasArmory coc.dummy matches 1.. function ./armory/check_hotbar:
        data modify storage coc:temp inventory set from entity @s Inventory

        scoreboard players set $slot coc.dummy -1
        for slot in range(9):
            if score $slot coc.dummy matches -1 if data storage coc:temp inventory[{Slot: Byte(slot), tag:{smithed:{id: "coc:armory"}}}]:
                scoreboard players set $slot coc.dummy slot


        append function ./armory/equip/set_item:
            data modify entity @s Item set from storage coc:temp armor
            tag @s remove coc.armor_return



        unless score $slot coc.dummy matches -1 unless data storage ./armory {class: "none"} function ./armory/equip:
            tag @s add coc.equiped

            data modify storage coc:temp filteredInventory set from storage coc:temp inventory
            for slotNum, _ in getReplaceSlots():
                data remove storage coc:temp filteredInventory[{Slot: Byte(slotNum)}]

            if data storage coc:temp filteredInventory[{tag:{coc:{armory:1b}}}] clear @s #coc:armory{coc:{armory:1b}}

            for slotNum, slotId in getReplaceSlots():
                if data storage coc:temp inventory[{Slot: Byte(slotNum)}]:
                    unless data storage coc:temp inventory[{Slot: Byte(slotNum),tag:{coc:{armory:1b}}}] function (./armory/equip/replace_ + slotId.split('.')[1]):
                        data modify storage coc:temp armor set from storage coc:temp inventory[{Slot: Byte(slotNum)}]
                        summon item ~ ~ ~ {Item:{id: "minecraft:stone", Count:1b},Tags:["coc.armor_return"], PickupDelay: 0s}
                        as @e[type=item,tag=coc.armor_return,distance=..0.5,limit=1] function ./armory/equip/set_item

            ClassRegistry.set_gear()

        if score $slot coc.dummy matches -1 function ./armory/unequip:
            tag @s remove coc.equiped
            clear @s #coc:armory{coc:{armory:1b}}

            store result score $hasTransformedArmory coc.dummy clear @s #coc:armory{coc:{transformed:1b}} 0
            if score $hasTransformedArmory coc.dummy matches 1.. function ./armory/fix_transformed:
                for i in range(36):
                    if data storage coc:temp inventory[{Slot: Byte(i),tag:{coc:{transformed:1b}}}] item replace entity @s f"container.{i}" with carrot_on_a_stick{smithed:{id: "coc:armory"}}
    if score $hasArmory coc.dummy matches 1.. unless entity @s[tag=coc.equiped] function ./armory/unequip
