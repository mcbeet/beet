compute default integer example:integer
compute default integer {type:constant, value:256}
compute default float example:integer
compute default float {type:constant, value:143.221}


execute positioned ~ ~3 ~ run place feature {
    "type": "minecraft:tree",
    "below_trunk_provider": "minecraft:soil_beneath_tree",
    "decorators": [],
    "foliage_placer": {
        "type": "minecraft:acacia_foliage_placer",
        "offset": 0,
        "radius": 2
    },
    "foliage_provider": {
        "id": "minecraft:acacia_leaves",
        "properties": {
            "distance": "7",
            "persistent": "false",
            "waterlogged": "false"
        }
    },
    "ignore_vines": 1,
    "minimum_size": {
        "type": "minecraft:two_layers_feature_size",
        "upper_size": 2
    },
    "trunk_placer": {
        "type": "minecraft:forking_trunk_placer",
        "base_height": 5,
        "height_rand_a": 2,
        "height_rand_b": 2
    },
    "trunk_provider": {
        "id": "minecraft:acacia_log",
        "properties": {
            "axis": "y"
        }
    }
}

swing @s mainhand stab 500t

execute store success score $has_hand_item gm4_binder_data if items entity @s weapon.* *