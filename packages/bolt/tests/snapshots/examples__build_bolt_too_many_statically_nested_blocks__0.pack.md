# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 26,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
_bolt_lineno = [1, 15, 16, 17, 18, 23, 40, 48, 58, 68, 79, 85, 99, 106, 113, 126, 129, 135, 140, 149, 166, 174, 191, 197], [1, 3, 4, 5, 6, 29, 32, 34, 36, 38, 42, 45, 52, 53, 54, 67, 68, 72, 73, 74, 75, 79, 87, 88]
_bolt_helper_import_module = _bolt_runtime.helpers['import_module']
_bolt_helper_get_attribute_handler = _bolt_runtime.helpers['get_attribute_handler']
_bolt_helper_children = _bolt_runtime.helpers['children']
_bolt_helper_operator_not = _bolt_runtime.helpers['operator_not']
_bolt_helper_branch = _bolt_runtime.helpers['branch']
_bolt_helper_interpolate_nbt = _bolt_runtime.helpers['interpolate_nbt']
_bolt_helper_replace = _bolt_runtime.helpers['replace']
_bolt_helper_interpolate_numeric = _bolt_runtime.helpers['interpolate_numeric']
_bolt_helper_interpolate_resource_location = _bolt_runtime.helpers['interpolate_resource_location']
_bolt_helper_interpolate_item_slot = _bolt_runtime.helpers['interpolate_item_slot']
_bolt_helper_exit_stack = _bolt_runtime.helpers['exit_stack']
with _bolt_helper_exit_stack() as _bolt_fused_with_statement8:
    _bolt_var37 = _bolt_fused_with_statement8.enter_context(_bolt_runtime.scope())
    onEvent = _bolt_runtime.from_module_import('coc:modules/on', 'onEvent')
    PlayerDB = _bolt_runtime.from_module_import('coc:modules/playerdb', 'PlayerDB')
    ClassRegistry = _bolt_runtime.from_module_import('coc:modules/armory', 'ClassRegistry')
    _bolt_from_import = _bolt_helper_import_module('nbtlib')
    Byte = _bolt_helper_get_attribute_handler(_bolt_from_import)["Byte"]
    Compound = _bolt_helper_get_attribute_handler(_bolt_from_import)["Compound"]
    _bolt_runtime.commands.append(_bolt_refs[0])
    def getReplaceSlots():
        _bolt_var0 = zip
        _bolt_var1 = 100
        _bolt_var2 = 101
        _bolt_var3 = 102
        _bolt_var4 = 103
        _bolt_var5 = 106
        _bolt_var5 = - _bolt_var5
        _bolt_var6 = [_bolt_var1, _bolt_var2, _bolt_var3, _bolt_var4, _bolt_var5]
        _bolt_var7 = 'armor.feet'
        _bolt_var8 = 'armor.legs'
        _bolt_var9 = 'armor.chest'
        _bolt_var10 = 'armor.head'
        _bolt_var11 = 'weapon.offhand'
        _bolt_var12 = [_bolt_var7, _bolt_var8, _bolt_var9, _bolt_var10, _bolt_var11]
        _bolt_var0 = _bolt_var0(_bolt_var6, _bolt_var12)
        return _bolt_var0
    def slotToArmor(slot):
        _bolt_var0 = slot
        _bolt_var1 = 100
        _bolt_var0 = _bolt_var0 == _bolt_var1
        _bolt_var0_inverse = _bolt_helper_operator_not(_bolt_var0)
        with _bolt_helper_branch(_bolt_var0) as _bolt_condition:
            if _bolt_condition:
                _bolt_var2 = 'netherite_boots'
                return _bolt_var2
        with _bolt_helper_branch(_bolt_var0_inverse) as _bolt_condition:
            if _bolt_condition:
                _bolt_var3 = slot
                _bolt_var4 = 101
                _bolt_var3 = _bolt_var3 == _bolt_var4
                _bolt_var3_inverse = _bolt_helper_operator_not(_bolt_var3)
                with _bolt_helper_branch(_bolt_var3) as _bolt_condition:
                    if _bolt_condition:
                        _bolt_var5 = 'netherite_leggings'
                        return _bolt_var5
                with _bolt_helper_branch(_bolt_var3_inverse) as _bolt_condition:
                    if _bolt_condition:
                        _bolt_var6 = slot
                        _bolt_var7 = 102
                        _bolt_var6 = _bolt_var6 == _bolt_var7
                        _bolt_var6_inverse = _bolt_helper_operator_not(_bolt_var6)
                        with _bolt_helper_branch(_bolt_var6) as _bolt_condition:
                            if _bolt_condition:
                                _bolt_var8 = 'netherite_chestplate'
                                return _bolt_var8
                        with _bolt_helper_branch(_bolt_var6_inverse) as _bolt_condition:
                            if _bolt_condition:
                                _bolt_var9 = slot
                                _bolt_var10 = 103
                                _bolt_var9 = _bolt_var9 == _bolt_var10
                                with _bolt_helper_branch(_bolt_var9) as _bolt_condition:
                                    if _bolt_condition:
                                        _bolt_var11 = 'netherite_helmet'
                                        return _bolt_var11
        _bolt_var12 = 'air'
        return _bolt_var12
    _bolt_var0 = onEvent
    _bolt_var1 = 'inventory_changed'
    _bolt_var2 = 'demo:armory/detect'
    _bolt_var0 = _bolt_var0(_bolt_var1, _bolt_var2)
    _bolt_fused_with_statement8.enter_context(_bolt_var0)
    _bolt_runtime.commands.append(_bolt_refs[1])
    _bolt_var3 = PlayerDB
    _bolt_var3 = _bolt_helper_get_attribute_handler(_bolt_var3)["get"]
    _bolt_var3 = _bolt_var3()
    _bolt_var3 = _bolt_helper_get_attribute_handler(_bolt_var3)["data"]
    _bolt_var3 = _bolt_helper_get_attribute_handler(_bolt_var3)["armory"]
    armory_data = _bolt_var3
    _bolt_runtime.commands.append(_bolt_refs[130])
    with _bolt_helper_exit_stack() as _bolt_fused_with_statement7:
        _bolt_fused_with_statement7.enter_context(_bolt_runtime.push_nesting('execute:subcommand'))
        _bolt_fused_with_statement7.enter_context(_bolt_runtime.push_nesting('execute:if:score:target:targetObjective:matches:range:subcommand', *_bolt_refs[125:128]))
        _bolt_fused_with_statement7.enter_context(_bolt_runtime.push_nesting('execute:run:subcommand'))
        _bolt_fused_with_statement7.enter_context(_bolt_runtime.push_nesting('function:name:commands', *_bolt_refs[122:123]))
        _bolt_var36 = _bolt_fused_with_statement7.enter_context(_bolt_runtime.scope())
        _bolt_runtime.commands.extend(_bolt_refs[22:24])
        _bolt_var4 = range
        _bolt_var5 = 9
        _bolt_var4 = _bolt_var4(_bolt_var5)
        for slot in _bolt_var4:
            with _bolt_helper_exit_stack() as _bolt_fused_with_statement0:
                _bolt_fused_with_statement0.enter_context(_bolt_runtime.push_nesting('execute:subcommand'))
                _bolt_fused_with_statement0.enter_context(_bolt_runtime.push_nesting('execute:if:score:target:targetObjective:matches:range:subcommand', *_bolt_refs[17:20]))
                _bolt_var6 = Byte
                _bolt_var7 = slot
                _bolt_var6 = _bolt_var6(_bolt_var7)
                _bolt_var6 = _bolt_helper_interpolate_nbt(_bolt_var6, _bolt_refs[2])
                _bolt_fused_with_statement0.enter_context(_bolt_runtime.push_nesting('execute:if:data:storage:source:path:subcommand', *_bolt_helper_children([_bolt_refs[9], _bolt_helper_replace(_bolt_refs[8], components=_bolt_helper_children([_bolt_refs[7], _bolt_helper_replace(_bolt_refs[6], index=_bolt_helper_replace(_bolt_refs[5], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[3], value=_bolt_var6), _bolt_refs[4]])))]))])))
                _bolt_fused_with_statement0.enter_context(_bolt_runtime.push_nesting('execute:commands'))
                _bolt_var9 = _bolt_fused_with_statement0.enter_context(_bolt_runtime.scope())
                _bolt_var8 = slot
                _bolt_var8 = _bolt_helper_interpolate_numeric(_bolt_var8, _bolt_refs[10])
                _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[13], arguments=_bolt_helper_children([_bolt_refs[11], _bolt_refs[12], _bolt_var8])))
            _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[21], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[20], arguments=_bolt_helper_children([*_bolt_refs[17:20], _bolt_helper_replace(_bolt_refs[16], arguments=_bolt_helper_children([*_bolt_helper_children([_bolt_refs[9], _bolt_helper_replace(_bolt_refs[8], components=_bolt_helper_children([_bolt_refs[7], _bolt_helper_replace(_bolt_refs[6], index=_bolt_helper_replace(_bolt_refs[5], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[3], value=_bolt_var6), _bolt_refs[4]])))]))]), _bolt_helper_replace(_bolt_refs[15], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[14], commands=_bolt_helper_children(_bolt_var9))]))]))]))])))
        _bolt_runtime.commands.append(_bolt_refs[84])
        with _bolt_helper_exit_stack() as _bolt_fused_with_statement3:
            _bolt_fused_with_statement3.enter_context(_bolt_runtime.push_nesting('execute:subcommand'))
            _bolt_fused_with_statement3.enter_context(_bolt_runtime.push_nesting('execute:unless:score:target:targetObjective:matches:range:subcommand', *_bolt_refs[79:82]))
            _bolt_fused_with_statement3.enter_context(_bolt_runtime.push_nesting('execute:unless:data:storage:source:path:subcommand', *_bolt_refs[76:78]))
            _bolt_fused_with_statement3.enter_context(_bolt_runtime.push_nesting('execute:run:subcommand'))
            _bolt_fused_with_statement3.enter_context(_bolt_runtime.push_nesting('function:name:commands', *_bolt_refs[73:74]))
            _bolt_var27 = _bolt_fused_with_statement3.enter_context(_bolt_runtime.scope())
            _bolt_runtime.commands.extend(_bolt_refs[32:34])
            _bolt_var10 = getReplaceSlots
            _bolt_var10 = _bolt_var10()
            for slotNum, _ in _bolt_var10:
                _bolt_var11 = Byte
                _bolt_var12 = slotNum
                _bolt_var11 = _bolt_var11(_bolt_var12)
                _bolt_var11 = _bolt_helper_interpolate_nbt(_bolt_var11, _bolt_refs[24])
                _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[31], arguments=_bolt_helper_children([_bolt_refs[30], _bolt_helper_replace(_bolt_refs[29], components=_bolt_helper_children([_bolt_refs[28], _bolt_helper_replace(_bolt_refs[27], index=_bolt_helper_replace(_bolt_refs[26], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[25], value=_bolt_var11)])))]))])))
            _bolt_runtime.commands.append(_bolt_refs[71])
            _bolt_var13 = getReplaceSlots
            _bolt_var13 = _bolt_var13()
            for slotNum, slotId in _bolt_var13:
                with _bolt_helper_exit_stack() as _bolt_fused_with_statement2:
                    _bolt_fused_with_statement2.enter_context(_bolt_runtime.push_nesting('execute:subcommand'))
                    _bolt_var14 = Byte
                    _bolt_var15 = slotNum
                    _bolt_var14 = _bolt_var14(_bolt_var15)
                    _bolt_var14 = _bolt_helper_interpolate_nbt(_bolt_var14, _bolt_refs[34])
                    _bolt_fused_with_statement2.enter_context(_bolt_runtime.push_nesting('execute:if:data:storage:source:path:subcommand', *_bolt_helper_children([_bolt_refs[40], _bolt_helper_replace(_bolt_refs[39], components=_bolt_helper_children([_bolt_refs[38], _bolt_helper_replace(_bolt_refs[37], index=_bolt_helper_replace(_bolt_refs[36], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[35], value=_bolt_var14)])))]))])))
                    _bolt_fused_with_statement2.enter_context(_bolt_runtime.push_nesting('execute:commands'))
                    _bolt_var25 = _bolt_fused_with_statement2.enter_context(_bolt_runtime.scope())
                    with _bolt_helper_exit_stack() as _bolt_fused_with_statement1:
                        _bolt_fused_with_statement1.enter_context(_bolt_runtime.push_nesting('execute:subcommand'))
                        _bolt_var16 = Byte
                        _bolt_var17 = slotNum
                        _bolt_var16 = _bolt_var16(_bolt_var17)
                        _bolt_var16 = _bolt_helper_interpolate_nbt(_bolt_var16, _bolt_refs[41])
                        _bolt_fused_with_statement1.enter_context(_bolt_runtime.push_nesting('execute:unless:data:storage:source:path:subcommand', *_bolt_helper_children([_bolt_refs[48], _bolt_helper_replace(_bolt_refs[47], components=_bolt_helper_children([_bolt_refs[46], _bolt_helper_replace(_bolt_refs[45], index=_bolt_helper_replace(_bolt_refs[44], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[42], value=_bolt_var16), _bolt_refs[43]])))]))])))
                        _bolt_fused_with_statement1.enter_context(_bolt_runtime.push_nesting('execute:run:subcommand'))
                        _bolt_var18 = 'demo:armory/equip/replace_'
                        _bolt_var19 = slotId
                        _bolt_var19 = _bolt_helper_get_attribute_handler(_bolt_var19)["split"]
                        _bolt_var20 = '.'
                        _bolt_var19 = _bolt_var19(_bolt_var20)
                        _bolt_var21 = 1
                        _bolt_var19 = _bolt_var19[_bolt_var21]
                        _bolt_var18 = _bolt_var18 + _bolt_var19
                        _bolt_var18 = _bolt_helper_interpolate_resource_location(_bolt_var18, _bolt_refs[49])
                        _bolt_fused_with_statement1.enter_context(_bolt_runtime.push_nesting('function:name:commands', *_bolt_helper_children([_bolt_var18])))
                        _bolt_var24 = _bolt_fused_with_statement1.enter_context(_bolt_runtime.scope())
                        _bolt_var22 = Byte
                        _bolt_var23 = slotNum
                        _bolt_var22 = _bolt_var22(_bolt_var23)
                        _bolt_var22 = _bolt_helper_interpolate_nbt(_bolt_var22, _bolt_refs[50])
                        _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[59], arguments=_bolt_helper_children([_bolt_refs[56], _bolt_refs[57], _bolt_refs[58], _bolt_helper_replace(_bolt_refs[55], components=_bolt_helper_children([_bolt_refs[54], _bolt_helper_replace(_bolt_refs[53], index=_bolt_helper_replace(_bolt_refs[52], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[51], value=_bolt_var22)])))]))])))
                        _bolt_runtime.commands.extend(_bolt_refs[60:62])
                    _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[66], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[65], arguments=_bolt_helper_children([*_bolt_helper_children([_bolt_refs[48], _bolt_helper_replace(_bolt_refs[47], components=_bolt_helper_children([_bolt_refs[46], _bolt_helper_replace(_bolt_refs[45], index=_bolt_helper_replace(_bolt_refs[44], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[42], value=_bolt_var16), _bolt_refs[43]])))]))]), _bolt_helper_replace(_bolt_refs[64], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[63], arguments=_bolt_helper_children([*_bolt_helper_children([_bolt_var18]), _bolt_helper_replace(_bolt_refs[62], commands=_bolt_helper_children(_bolt_var24))]))]))]))])))
                _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[70], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[69], arguments=_bolt_helper_children([*_bolt_helper_children([_bolt_refs[40], _bolt_helper_replace(_bolt_refs[39], components=_bolt_helper_children([_bolt_refs[38], _bolt_helper_replace(_bolt_refs[37], index=_bolt_helper_replace(_bolt_refs[36], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[35], value=_bolt_var14)])))]))]), _bolt_helper_replace(_bolt_refs[68], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[67], commands=_bolt_helper_children(_bolt_var25))]))]))])))
            _bolt_var26 = ClassRegistry
            _bolt_var26 = _bolt_helper_get_attribute_handler(_bolt_var26)["set_gear"]
            _bolt_var26 = _bolt_var26()
        _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[83], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[82], arguments=_bolt_helper_children([*_bolt_refs[79:82], _bolt_helper_replace(_bolt_refs[78], arguments=_bolt_helper_children([*_bolt_refs[76:78], _bolt_helper_replace(_bolt_refs[75], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[74], arguments=_bolt_helper_children([*_bolt_refs[73:74], _bolt_helper_replace(_bolt_refs[72], commands=_bolt_helper_children(_bolt_var27))]))]))]))]))])))
        with _bolt_helper_exit_stack() as _bolt_fused_with_statement6:
            _bolt_fused_with_statement6.enter_context(_bolt_runtime.push_nesting('execute:subcommand'))
            _bolt_fused_with_statement6.enter_context(_bolt_runtime.push_nesting('execute:if:score:target:targetObjective:matches:range:subcommand', *_bolt_refs[116:119]))
            _bolt_fused_with_statement6.enter_context(_bolt_runtime.push_nesting('execute:run:subcommand'))
            _bolt_fused_with_statement6.enter_context(_bolt_runtime.push_nesting('function:name:commands', *_bolt_refs[113:114]))
            _bolt_var35 = _bolt_fused_with_statement6.enter_context(_bolt_runtime.scope())
            _bolt_runtime.commands.extend(_bolt_refs[109:112])
            with _bolt_helper_exit_stack() as _bolt_fused_with_statement5:
                _bolt_fused_with_statement5.enter_context(_bolt_runtime.push_nesting('execute:subcommand'))
                _bolt_fused_with_statement5.enter_context(_bolt_runtime.push_nesting('execute:if:score:target:targetObjective:matches:range:subcommand', *_bolt_refs[104:107]))
                _bolt_fused_with_statement5.enter_context(_bolt_runtime.push_nesting('execute:run:subcommand'))
                _bolt_fused_with_statement5.enter_context(_bolt_runtime.push_nesting('function:name:commands', *_bolt_refs[101:102]))
                _bolt_var34 = _bolt_fused_with_statement5.enter_context(_bolt_runtime.scope())
                _bolt_var28 = range
                _bolt_var29 = 36
                _bolt_var28 = _bolt_var28(_bolt_var29)
                for i in _bolt_var28:
                    with _bolt_helper_exit_stack() as _bolt_fused_with_statement4:
                        _bolt_fused_with_statement4.enter_context(_bolt_runtime.push_nesting('execute:subcommand'))
                        _bolt_var30 = Byte
                        _bolt_var31 = i
                        _bolt_var30 = _bolt_var30(_bolt_var31)
                        _bolt_var30 = _bolt_helper_interpolate_nbt(_bolt_var30, _bolt_refs[85])
                        _bolt_fused_with_statement4.enter_context(_bolt_runtime.push_nesting('execute:if:data:storage:source:path:subcommand', *_bolt_helper_children([_bolt_refs[92], _bolt_helper_replace(_bolt_refs[91], components=_bolt_helper_children([_bolt_refs[90], _bolt_helper_replace(_bolt_refs[89], index=_bolt_helper_replace(_bolt_refs[88], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[86], value=_bolt_var30), _bolt_refs[87]])))]))])))
                        _bolt_fused_with_statement4.enter_context(_bolt_runtime.push_nesting('execute:run:subcommand'))
                        _bolt_var32 = i
                        _bolt_var33 = 'container.{}'.format(_bolt_var32)
                        _bolt_var33 = _bolt_helper_interpolate_item_slot(_bolt_var33, _bolt_refs[93])
                    _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[99], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[98], arguments=_bolt_helper_children([*_bolt_helper_children([_bolt_refs[92], _bolt_helper_replace(_bolt_refs[91], components=_bolt_helper_children([_bolt_refs[90], _bolt_helper_replace(_bolt_refs[89], index=_bolt_helper_replace(_bolt_refs[88], entries=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[86], value=_bolt_var30), _bolt_refs[87]])))]))]), _bolt_helper_replace(_bolt_refs[97], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[96], arguments=_bolt_helper_children([_bolt_refs[94], _bolt_var33, _bolt_refs[95]]))]))]))])))
            _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[108], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[107], arguments=_bolt_helper_children([*_bolt_refs[104:107], _bolt_helper_replace(_bolt_refs[103], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[102], arguments=_bolt_helper_children([*_bolt_refs[101:102], _bolt_helper_replace(_bolt_refs[100], commands=_bolt_helper_children(_bolt_var34))]))]))]))])))
        _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[120], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[119], arguments=_bolt_helper_children([*_bolt_refs[116:119], _bolt_helper_replace(_bolt_refs[115], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[114], arguments=_bolt_helper_children([*_bolt_refs[113:114], _bolt_helper_replace(_bolt_refs[112], commands=_bolt_helper_children(_bolt_var35))]))]))]))])))
    _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[129], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[128], arguments=_bolt_helper_children([*_bolt_refs[125:128], _bolt_helper_replace(_bolt_refs[124], arguments=_bolt_helper_children([_bolt_helper_replace(_bolt_refs[123], arguments=_bolt_helper_children([*_bolt_refs[122:123], _bolt_helper_replace(_bolt_refs[121], commands=_bolt_helper_children(_bolt_var36))]))]))]))])))
    _bolt_runtime.commands.append(_bolt_refs[131])
_bolt_var38 = _bolt_helper_replace(_bolt_refs[132], commands=_bolt_helper_children(_bolt_var37))
```
