# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      88,
      0
    ],
    "max_format": [
      88,
      0
    ],
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say 1
say 2
scoreboard players set global tmp0 0
execute if score global seven = global seven run scoreboard players set global tmp0 1
scoreboard players operation global tmp1 = global tmp0
execute unless score global tmp0 matches 0 run function demo:foo/nested_execute_0
scoreboard players operation global tmp3 = global tmp1
execute unless score global tmp1 matches 0 run function demo:foo/nested_execute_1
execute unless score global tmp3 matches 0 run say 1
scoreboard players set global tmp5 0
execute if score global seven = global seven run scoreboard players set global tmp5 1
scoreboard players operation global tmp6 = global tmp5
execute unless score global tmp5 matches 0 run function demo:foo/nested_execute_2
scoreboard players operation global tmp8 = global tmp6
execute unless score global tmp6 matches 0 run function demo:foo/nested_execute_3
execute unless score global tmp8 matches 0 run say 2
scoreboard players set global tmp10 0
execute if score global foo = global bar run scoreboard players set global tmp10 1
scoreboard players set global tmp11 0
execute if score global tmp10 matches 1 run scoreboard players set global tmp11 1
scoreboard players operation global tmp12 = global tmp11
execute unless score global tmp11 matches 0 run function demo:foo/nested_execute_4
execute unless score global tmp12 matches 0 run say 3
#
# check 123, 456
say True
say False
say False
say False
say False
say False
say False
say False
say False
say False
say False
say False
say False
say False
say False
say True
#
# check 123, foo
say True
scoreboard players set global tmp14 0
execute if score global foo matches 123 run scoreboard players set global tmp14 1
say tmp14
scoreboard players set global tmp15 0
execute if score global foo matches 123 run scoreboard players set global tmp15 1
scoreboard players operation global tmp16 = global tmp15
execute unless score global tmp15 matches 0 run function demo:foo/nested_execute_5
say tmp16
scoreboard players set global tmp18 0
execute if score global foo matches 123 run scoreboard players set global tmp18 1
scoreboard players operation global tmp19 = global tmp18
execute unless score global tmp18 matches 0 run function demo:foo/nested_execute_6
say tmp19
scoreboard players set global tmp21 0
execute if score global foo matches 123 run scoreboard players set global tmp21 1
scoreboard players operation global tmp22 = global tmp21
execute unless score global tmp21 matches 0 run function demo:foo/nested_execute_7
scoreboard players operation global tmp24 = global tmp22
execute unless score global tmp22 matches 0 run scoreboard players set global tmp24 1
say tmp24
scoreboard players set global tmp25 0
execute if score global foo matches 123 run scoreboard players set global tmp25 1
scoreboard players operation global tmp26 = global tmp25
execute unless score global tmp25 matches 0 run function demo:foo/nested_execute_8
scoreboard players operation global tmp28 = global tmp26
execute unless score global tmp26 matches 0 run function demo:foo/nested_execute_9
say tmp28
scoreboard players set global tmp30 0
execute if score global foo matches 123 run scoreboard players set global tmp30 1
scoreboard players operation global tmp31 = global tmp30
execute unless score global tmp30 matches 0 run function demo:foo/nested_execute_10
scoreboard players operation global tmp33 = global tmp31
execute unless score global tmp31 matches 0 run function demo:foo/nested_execute_11
say tmp33
scoreboard players set global tmp35 0
execute if score global foo matches 123 run scoreboard players set global tmp35 1
scoreboard players operation global tmp36 = global tmp35
execute unless score global tmp35 matches 0 run function demo:foo/nested_execute_12
scoreboard players operation global tmp38 = global tmp36
execute unless score global tmp36 matches 0 run function demo:foo/nested_execute_13
say tmp38
scoreboard players set global tmp40 0
execute if score global foo matches 123 run scoreboard players set global tmp40 1
scoreboard players operation global tmp41 = global tmp40
execute unless score global tmp40 matches 0 run scoreboard players set global tmp41 1
scoreboard players operation global tmp42 = global tmp41
execute unless score global tmp41 matches 0 run scoreboard players set global tmp42 1
say tmp42
scoreboard players set global tmp43 0
execute if score global foo matches 123 run scoreboard players set global tmp43 1
scoreboard players operation global tmp44 = global tmp43
execute unless score global tmp43 matches 0 run scoreboard players set global tmp44 1
scoreboard players operation global tmp45 = global tmp44
execute unless score global tmp44 matches 0 run function demo:foo/nested_execute_14
say tmp45
scoreboard players set global tmp47 0
execute if score global foo matches 123 run scoreboard players set global tmp47 1
scoreboard players operation global tmp48 = global tmp47
execute unless score global tmp47 matches 0 run function demo:foo/nested_execute_15
scoreboard players operation global tmp50 = global tmp48
execute unless score global tmp48 matches 0 run function demo:foo/nested_execute_16
say tmp50
scoreboard players set global tmp52 0
execute if score global foo matches 123 run scoreboard players set global tmp52 1
scoreboard players operation global tmp53 = global tmp52
execute unless score global tmp52 matches 0 run function demo:foo/nested_execute_17
scoreboard players operation global tmp55 = global tmp53
execute unless score global tmp53 matches 0 run function demo:foo/nested_execute_18
say tmp55
scoreboard players set global tmp57 0
execute if score global foo = global foo run scoreboard players set global tmp57 1
scoreboard players operation global tmp58 = global tmp57
execute unless score global tmp57 matches 0 run function demo:foo/nested_execute_19
scoreboard players operation global tmp60 = global tmp58
execute unless score global tmp58 matches 0 run scoreboard players set global tmp60 1
say tmp60
scoreboard players set global tmp61 0
execute if score global foo = global foo run scoreboard players set global tmp61 1
scoreboard players operation global tmp62 = global tmp61
execute unless score global tmp61 matches 0 run function demo:foo/nested_execute_20
scoreboard players operation global tmp64 = global tmp62
execute unless score global tmp62 matches 0 run function demo:foo/nested_execute_21
say tmp64
scoreboard players set global tmp66 0
execute if score global foo = global foo run scoreboard players set global tmp66 1
scoreboard players operation global tmp67 = global tmp66
execute unless score global tmp66 matches 0 run function demo:foo/nested_execute_22
scoreboard players operation global tmp69 = global tmp67
execute unless score global tmp67 matches 0 run function demo:foo/nested_execute_23
say tmp69
scoreboard players set global tmp71 0
execute if score global foo = global foo run scoreboard players set global tmp71 1
scoreboard players operation global tmp72 = global tmp71
execute unless score global tmp71 matches 0 run function demo:foo/nested_execute_24
scoreboard players operation global tmp74 = global tmp72
execute unless score global tmp72 matches 0 run function demo:foo/nested_execute_25
say tmp74
#
# check 123, bar
say True
scoreboard players set global tmp76 0
execute if score global bar matches 123 run scoreboard players set global tmp76 1
say tmp76
scoreboard players set global tmp77 0
execute if score global bar matches 123 run scoreboard players set global tmp77 1
scoreboard players operation global tmp78 = global tmp77
execute unless score global tmp77 matches 0 run function demo:foo/nested_execute_26
say tmp78
scoreboard players set global tmp80 0
execute if score global bar matches 123 run scoreboard players set global tmp80 1
scoreboard players operation global tmp81 = global tmp80
execute unless score global tmp80 matches 0 run function demo:foo/nested_execute_27
say tmp81
scoreboard players set global tmp83 0
execute if score global bar matches 123 run scoreboard players set global tmp83 1
scoreboard players operation global tmp84 = global tmp83
execute unless score global tmp83 matches 0 run function demo:foo/nested_execute_28
scoreboard players operation global tmp86 = global tmp84
execute unless score global tmp84 matches 0 run scoreboard players set global tmp86 1
say tmp86
scoreboard players set global tmp87 0
execute if score global bar matches 123 run scoreboard players set global tmp87 1
scoreboard players operation global tmp88 = global tmp87
execute unless score global tmp87 matches 0 run function demo:foo/nested_execute_29
scoreboard players operation global tmp90 = global tmp88
execute unless score global tmp88 matches 0 run function demo:foo/nested_execute_30
say tmp90
scoreboard players set global tmp92 0
execute if score global bar matches 123 run scoreboard players set global tmp92 1
scoreboard players operation global tmp93 = global tmp92
execute unless score global tmp92 matches 0 run function demo:foo/nested_execute_31
scoreboard players operation global tmp95 = global tmp93
execute unless score global tmp93 matches 0 run function demo:foo/nested_execute_32
say tmp95
scoreboard players set global tmp97 0
execute if score global bar matches 123 run scoreboard players set global tmp97 1
scoreboard players operation global tmp98 = global tmp97
execute unless score global tmp97 matches 0 run function demo:foo/nested_execute_33
scoreboard players operation global tmp100 = global tmp98
execute unless score global tmp98 matches 0 run function demo:foo/nested_execute_34
say tmp100
scoreboard players set global tmp102 0
execute if score global bar matches 123 run scoreboard players set global tmp102 1
scoreboard players operation global tmp103 = global tmp102
execute unless score global tmp102 matches 0 run scoreboard players set global tmp103 1
scoreboard players operation global tmp104 = global tmp103
execute unless score global tmp103 matches 0 run scoreboard players set global tmp104 1
say tmp104
scoreboard players set global tmp105 0
execute if score global bar matches 123 run scoreboard players set global tmp105 1
scoreboard players operation global tmp106 = global tmp105
execute unless score global tmp105 matches 0 run scoreboard players set global tmp106 1
scoreboard players operation global tmp107 = global tmp106
execute unless score global tmp106 matches 0 run function demo:foo/nested_execute_35
say tmp107
scoreboard players set global tmp109 0
execute if score global bar matches 123 run scoreboard players set global tmp109 1
scoreboard players operation global tmp110 = global tmp109
execute unless score global tmp109 matches 0 run function demo:foo/nested_execute_36
scoreboard players operation global tmp112 = global tmp110
execute unless score global tmp110 matches 0 run function demo:foo/nested_execute_37
say tmp112
scoreboard players set global tmp114 0
execute if score global bar matches 123 run scoreboard players set global tmp114 1
scoreboard players operation global tmp115 = global tmp114
execute unless score global tmp114 matches 0 run function demo:foo/nested_execute_38
scoreboard players operation global tmp117 = global tmp115
execute unless score global tmp115 matches 0 run function demo:foo/nested_execute_39
say tmp117
scoreboard players set global tmp119 0
execute if score global bar = global bar run scoreboard players set global tmp119 1
scoreboard players operation global tmp120 = global tmp119
execute unless score global tmp119 matches 0 run function demo:foo/nested_execute_40
scoreboard players operation global tmp122 = global tmp120
execute unless score global tmp120 matches 0 run scoreboard players set global tmp122 1
say tmp122
scoreboard players set global tmp123 0
execute if score global bar = global bar run scoreboard players set global tmp123 1
scoreboard players operation global tmp124 = global tmp123
execute unless score global tmp123 matches 0 run function demo:foo/nested_execute_41
scoreboard players operation global tmp126 = global tmp124
execute unless score global tmp124 matches 0 run function demo:foo/nested_execute_42
say tmp126
scoreboard players set global tmp128 0
execute if score global bar = global bar run scoreboard players set global tmp128 1
scoreboard players operation global tmp129 = global tmp128
execute unless score global tmp128 matches 0 run function demo:foo/nested_execute_43
scoreboard players operation global tmp131 = global tmp129
execute unless score global tmp129 matches 0 run function demo:foo/nested_execute_44
say tmp131
scoreboard players set global tmp133 0
execute if score global bar = global bar run scoreboard players set global tmp133 1
scoreboard players operation global tmp134 = global tmp133
execute unless score global tmp133 matches 0 run function demo:foo/nested_execute_45
scoreboard players operation global tmp136 = global tmp134
execute unless score global tmp134 matches 0 run function demo:foo/nested_execute_46
say tmp136
#
# check 456, foo
say True
scoreboard players set global tmp138 0
execute if score global foo matches 456 run scoreboard players set global tmp138 1
say tmp138
scoreboard players set global tmp139 0
execute if score global foo matches 456 run scoreboard players set global tmp139 1
scoreboard players operation global tmp140 = global tmp139
execute unless score global tmp139 matches 0 run function demo:foo/nested_execute_47
say tmp140
scoreboard players set global tmp142 0
execute if score global foo matches 456 run scoreboard players set global tmp142 1
scoreboard players operation global tmp143 = global tmp142
execute unless score global tmp142 matches 0 run function demo:foo/nested_execute_48
say tmp143
scoreboard players set global tmp145 0
execute if score global foo matches 456 run scoreboard players set global tmp145 1
scoreboard players operation global tmp146 = global tmp145
execute unless score global tmp145 matches 0 run function demo:foo/nested_execute_49
scoreboard players operation global tmp148 = global tmp146
execute unless score global tmp146 matches 0 run scoreboard players set global tmp148 1
say tmp148
scoreboard players set global tmp149 0
execute if score global foo matches 456 run scoreboard players set global tmp149 1
scoreboard players operation global tmp150 = global tmp149
execute unless score global tmp149 matches 0 run function demo:foo/nested_execute_50
scoreboard players operation global tmp152 = global tmp150
execute unless score global tmp150 matches 0 run function demo:foo/nested_execute_51
say tmp152
scoreboard players set global tmp154 0
execute if score global foo matches 456 run scoreboard players set global tmp154 1
scoreboard players operation global tmp155 = global tmp154
execute unless score global tmp154 matches 0 run function demo:foo/nested_execute_52
scoreboard players operation global tmp157 = global tmp155
execute unless score global tmp155 matches 0 run function demo:foo/nested_execute_53
say tmp157
scoreboard players set global tmp159 0
execute if score global foo matches 456 run scoreboard players set global tmp159 1
scoreboard players operation global tmp160 = global tmp159
execute unless score global tmp159 matches 0 run function demo:foo/nested_execute_54
scoreboard players operation global tmp162 = global tmp160
execute unless score global tmp160 matches 0 run function demo:foo/nested_execute_55
say tmp162
scoreboard players set global tmp164 0
execute if score global foo matches 456 run scoreboard players set global tmp164 1
scoreboard players operation global tmp165 = global tmp164
execute unless score global tmp164 matches 0 run scoreboard players set global tmp165 1
scoreboard players operation global tmp166 = global tmp165
execute unless score global tmp165 matches 0 run scoreboard players set global tmp166 1
say tmp166
scoreboard players set global tmp167 0
execute if score global foo matches 456 run scoreboard players set global tmp167 1
scoreboard players operation global tmp168 = global tmp167
execute unless score global tmp167 matches 0 run scoreboard players set global tmp168 1
scoreboard players operation global tmp169 = global tmp168
execute unless score global tmp168 matches 0 run function demo:foo/nested_execute_56
say tmp169
scoreboard players set global tmp171 0
execute if score global foo matches 456 run scoreboard players set global tmp171 1
scoreboard players operation global tmp172 = global tmp171
execute unless score global tmp171 matches 0 run function demo:foo/nested_execute_57
scoreboard players operation global tmp174 = global tmp172
execute unless score global tmp172 matches 0 run function demo:foo/nested_execute_58
say tmp174
scoreboard players set global tmp176 0
execute if score global foo matches 456 run scoreboard players set global tmp176 1
scoreboard players operation global tmp177 = global tmp176
execute unless score global tmp176 matches 0 run function demo:foo/nested_execute_59
scoreboard players operation global tmp179 = global tmp177
execute unless score global tmp177 matches 0 run function demo:foo/nested_execute_60
say tmp179
scoreboard players set global tmp181 0
execute if score global foo = global foo run scoreboard players set global tmp181 1
scoreboard players operation global tmp182 = global tmp181
execute unless score global tmp181 matches 0 run function demo:foo/nested_execute_61
scoreboard players operation global tmp184 = global tmp182
execute unless score global tmp182 matches 0 run scoreboard players set global tmp184 1
say tmp184
scoreboard players set global tmp185 0
execute if score global foo = global foo run scoreboard players set global tmp185 1
scoreboard players operation global tmp186 = global tmp185
execute unless score global tmp185 matches 0 run function demo:foo/nested_execute_62
scoreboard players operation global tmp188 = global tmp186
execute unless score global tmp186 matches 0 run function demo:foo/nested_execute_63
say tmp188
scoreboard players set global tmp190 0
execute if score global foo = global foo run scoreboard players set global tmp190 1
scoreboard players operation global tmp191 = global tmp190
execute unless score global tmp190 matches 0 run function demo:foo/nested_execute_64
scoreboard players operation global tmp193 = global tmp191
execute unless score global tmp191 matches 0 run function demo:foo/nested_execute_65
say tmp193
scoreboard players set global tmp195 0
execute if score global foo = global foo run scoreboard players set global tmp195 1
scoreboard players operation global tmp196 = global tmp195
execute unless score global tmp195 matches 0 run function demo:foo/nested_execute_66
scoreboard players operation global tmp198 = global tmp196
execute unless score global tmp196 matches 0 run function demo:foo/nested_execute_67
say tmp198
#
# check 456, bar
say True
scoreboard players set global tmp200 0
execute if score global bar matches 456 run scoreboard players set global tmp200 1
say tmp200
scoreboard players set global tmp201 0
execute if score global bar matches 456 run scoreboard players set global tmp201 1
scoreboard players operation global tmp202 = global tmp201
execute unless score global tmp201 matches 0 run function demo:foo/nested_execute_68
say tmp202
scoreboard players set global tmp204 0
execute if score global bar matches 456 run scoreboard players set global tmp204 1
scoreboard players operation global tmp205 = global tmp204
execute unless score global tmp204 matches 0 run function demo:foo/nested_execute_69
say tmp205
scoreboard players set global tmp207 0
execute if score global bar matches 456 run scoreboard players set global tmp207 1
scoreboard players operation global tmp208 = global tmp207
execute unless score global tmp207 matches 0 run function demo:foo/nested_execute_70
scoreboard players operation global tmp210 = global tmp208
execute unless score global tmp208 matches 0 run scoreboard players set global tmp210 1
say tmp210
scoreboard players set global tmp211 0
execute if score global bar matches 456 run scoreboard players set global tmp211 1
scoreboard players operation global tmp212 = global tmp211
execute unless score global tmp211 matches 0 run function demo:foo/nested_execute_71
scoreboard players operation global tmp214 = global tmp212
execute unless score global tmp212 matches 0 run function demo:foo/nested_execute_72
say tmp214
scoreboard players set global tmp216 0
execute if score global bar matches 456 run scoreboard players set global tmp216 1
scoreboard players operation global tmp217 = global tmp216
execute unless score global tmp216 matches 0 run function demo:foo/nested_execute_73
scoreboard players operation global tmp219 = global tmp217
execute unless score global tmp217 matches 0 run function demo:foo/nested_execute_74
say tmp219
scoreboard players set global tmp221 0
execute if score global bar matches 456 run scoreboard players set global tmp221 1
scoreboard players operation global tmp222 = global tmp221
execute unless score global tmp221 matches 0 run function demo:foo/nested_execute_75
scoreboard players operation global tmp224 = global tmp222
execute unless score global tmp222 matches 0 run function demo:foo/nested_execute_76
say tmp224
scoreboard players set global tmp226 0
execute if score global bar matches 456 run scoreboard players set global tmp226 1
scoreboard players operation global tmp227 = global tmp226
execute unless score global tmp226 matches 0 run scoreboard players set global tmp227 1
scoreboard players operation global tmp228 = global tmp227
execute unless score global tmp227 matches 0 run scoreboard players set global tmp228 1
say tmp228
scoreboard players set global tmp229 0
execute if score global bar matches 456 run scoreboard players set global tmp229 1
scoreboard players operation global tmp230 = global tmp229
execute unless score global tmp229 matches 0 run scoreboard players set global tmp230 1
scoreboard players operation global tmp231 = global tmp230
execute unless score global tmp230 matches 0 run function demo:foo/nested_execute_77
say tmp231
scoreboard players set global tmp233 0
execute if score global bar matches 456 run scoreboard players set global tmp233 1
scoreboard players operation global tmp234 = global tmp233
execute unless score global tmp233 matches 0 run function demo:foo/nested_execute_78
scoreboard players operation global tmp236 = global tmp234
execute unless score global tmp234 matches 0 run function demo:foo/nested_execute_79
say tmp236
scoreboard players set global tmp238 0
execute if score global bar matches 456 run scoreboard players set global tmp238 1
scoreboard players operation global tmp239 = global tmp238
execute unless score global tmp238 matches 0 run function demo:foo/nested_execute_80
scoreboard players operation global tmp241 = global tmp239
execute unless score global tmp239 matches 0 run function demo:foo/nested_execute_81
say tmp241
scoreboard players set global tmp243 0
execute if score global bar = global bar run scoreboard players set global tmp243 1
scoreboard players operation global tmp244 = global tmp243
execute unless score global tmp243 matches 0 run function demo:foo/nested_execute_82
scoreboard players operation global tmp246 = global tmp244
execute unless score global tmp244 matches 0 run scoreboard players set global tmp246 1
say tmp246
scoreboard players set global tmp247 0
execute if score global bar = global bar run scoreboard players set global tmp247 1
scoreboard players operation global tmp248 = global tmp247
execute unless score global tmp247 matches 0 run function demo:foo/nested_execute_83
scoreboard players operation global tmp250 = global tmp248
execute unless score global tmp248 matches 0 run function demo:foo/nested_execute_84
say tmp250
scoreboard players set global tmp252 0
execute if score global bar = global bar run scoreboard players set global tmp252 1
scoreboard players operation global tmp253 = global tmp252
execute unless score global tmp252 matches 0 run function demo:foo/nested_execute_85
scoreboard players operation global tmp255 = global tmp253
execute unless score global tmp253 matches 0 run function demo:foo/nested_execute_86
say tmp255
scoreboard players set global tmp257 0
execute if score global bar = global bar run scoreboard players set global tmp257 1
scoreboard players operation global tmp258 = global tmp257
execute unless score global tmp257 matches 0 run function demo:foo/nested_execute_87
scoreboard players operation global tmp260 = global tmp258
execute unless score global tmp258 matches 0 run function demo:foo/nested_execute_88
say tmp260
#
# check foo, bar
scoreboard players set global tmp262 0
execute if score global foo = global foo run scoreboard players set global tmp262 1
scoreboard players operation global tmp263 = global tmp262
execute unless score global tmp262 matches 0 run function demo:foo/nested_execute_89
scoreboard players operation global tmp265 = global tmp263
execute unless score global tmp263 matches 0 run function demo:foo/nested_execute_90
say tmp265
scoreboard players set global tmp267 0
execute if score global foo = global foo run scoreboard players set global tmp267 1
scoreboard players operation global tmp268 = global tmp267
execute unless score global tmp267 matches 0 run function demo:foo/nested_execute_91
scoreboard players operation global tmp270 = global tmp268
execute unless score global tmp268 matches 0 run function demo:foo/nested_execute_92
say tmp270
scoreboard players set global tmp272 0
execute if score global foo = global foo run scoreboard players set global tmp272 1
scoreboard players operation global tmp273 = global tmp272
execute unless score global tmp272 matches 0 run function demo:foo/nested_execute_93
scoreboard players operation global tmp275 = global tmp273
execute unless score global tmp273 matches 0 run function demo:foo/nested_execute_94
say tmp275
scoreboard players set global tmp277 0
execute if score global foo = global foo run scoreboard players set global tmp277 1
scoreboard players operation global tmp278 = global tmp277
execute unless score global tmp277 matches 0 run function demo:foo/nested_execute_95
scoreboard players operation global tmp280 = global tmp278
execute unless score global tmp278 matches 0 run function demo:foo/nested_execute_96
say tmp280
scoreboard players set global tmp282 0
execute if score global foo = global bar run scoreboard players set global tmp282 1
scoreboard players operation global tmp283 = global tmp282
execute unless score global tmp282 matches 0 run function demo:foo/nested_execute_97
scoreboard players operation global tmp285 = global tmp283
execute unless score global tmp283 matches 0 run function demo:foo/nested_execute_98
say tmp285
scoreboard players set global tmp287 0
execute if score global foo = global bar run scoreboard players set global tmp287 1
scoreboard players operation global tmp288 = global tmp287
execute unless score global tmp287 matches 0 run function demo:foo/nested_execute_99
scoreboard players operation global tmp290 = global tmp288
execute unless score global tmp288 matches 0 run function demo:foo/nested_execute_100
say tmp290
scoreboard players set global tmp292 0
execute if score global foo = global bar run scoreboard players set global tmp292 1
scoreboard players operation global tmp293 = global tmp292
execute unless score global tmp292 matches 0 run function demo:foo/nested_execute_101
scoreboard players operation global tmp295 = global tmp293
execute unless score global tmp293 matches 0 run function demo:foo/nested_execute_102
say tmp295
scoreboard players set global tmp297 0
execute if score global foo = global bar run scoreboard players set global tmp297 1
scoreboard players operation global tmp298 = global tmp297
execute unless score global tmp297 matches 0 run function demo:foo/nested_execute_103
scoreboard players operation global tmp300 = global tmp298
execute unless score global tmp298 matches 0 run function demo:foo/nested_execute_104
say tmp300
scoreboard players set global tmp302 0
execute if score global bar = global foo run scoreboard players set global tmp302 1
scoreboard players operation global tmp303 = global tmp302
execute unless score global tmp302 matches 0 run function demo:foo/nested_execute_105
scoreboard players operation global tmp305 = global tmp303
execute unless score global tmp303 matches 0 run function demo:foo/nested_execute_106
say tmp305
scoreboard players set global tmp307 0
execute if score global bar = global foo run scoreboard players set global tmp307 1
scoreboard players operation global tmp308 = global tmp307
execute unless score global tmp307 matches 0 run function demo:foo/nested_execute_107
scoreboard players operation global tmp310 = global tmp308
execute unless score global tmp308 matches 0 run function demo:foo/nested_execute_108
say tmp310
scoreboard players set global tmp312 0
execute if score global bar = global foo run scoreboard players set global tmp312 1
scoreboard players operation global tmp313 = global tmp312
execute unless score global tmp312 matches 0 run function demo:foo/nested_execute_109
scoreboard players operation global tmp315 = global tmp313
execute unless score global tmp313 matches 0 run function demo:foo/nested_execute_110
say tmp315
scoreboard players set global tmp317 0
execute if score global bar = global foo run scoreboard players set global tmp317 1
scoreboard players operation global tmp318 = global tmp317
execute unless score global tmp317 matches 0 run function demo:foo/nested_execute_111
scoreboard players operation global tmp320 = global tmp318
execute unless score global tmp318 matches 0 run function demo:foo/nested_execute_112
say tmp320
scoreboard players set global tmp322 0
execute if score global bar = global bar run scoreboard players set global tmp322 1
scoreboard players operation global tmp323 = global tmp322
execute unless score global tmp322 matches 0 run function demo:foo/nested_execute_113
scoreboard players operation global tmp325 = global tmp323
execute unless score global tmp323 matches 0 run function demo:foo/nested_execute_114
say tmp325
scoreboard players set global tmp327 0
execute if score global bar = global bar run scoreboard players set global tmp327 1
scoreboard players operation global tmp328 = global tmp327
execute unless score global tmp327 matches 0 run function demo:foo/nested_execute_115
scoreboard players operation global tmp330 = global tmp328
execute unless score global tmp328 matches 0 run function demo:foo/nested_execute_116
say tmp330
scoreboard players set global tmp332 0
execute if score global bar = global bar run scoreboard players set global tmp332 1
scoreboard players operation global tmp333 = global tmp332
execute unless score global tmp332 matches 0 run function demo:foo/nested_execute_117
scoreboard players operation global tmp335 = global tmp333
execute unless score global tmp333 matches 0 run function demo:foo/nested_execute_118
say tmp335
scoreboard players set global tmp337 0
execute if score global bar = global bar run scoreboard players set global tmp337 1
scoreboard players operation global tmp338 = global tmp337
execute unless score global tmp337 matches 0 run function demo:foo/nested_execute_119
scoreboard players operation global tmp340 = global tmp338
execute unless score global tmp338 matches 0 run function demo:foo/nested_execute_120
say tmp340
```

`@function demo:foo/nested_execute_0`

```mcfunction
scoreboard players set global tmp2 0
execute if score global seven = global seven run scoreboard players set global tmp2 1
scoreboard players operation global tmp1 = global tmp2
```

`@function demo:foo/nested_execute_1`

```mcfunction
scoreboard players set global tmp4 0
execute if score global seven = global seven run scoreboard players set global tmp4 1
scoreboard players operation global tmp3 = global tmp4
```

`@function demo:foo/nested_execute_10`

```mcfunction
scoreboard players set global tmp32 0
execute if score global foo = global foo run scoreboard players set global tmp32 1
scoreboard players operation global tmp31 = global tmp32
```

`@function demo:foo/nested_execute_100`

```mcfunction
scoreboard players set global tmp291 0
execute if score global foo = global bar run scoreboard players set global tmp291 1
scoreboard players operation global tmp290 = global tmp291
```

`@function demo:foo/nested_execute_101`

```mcfunction
scoreboard players set global tmp294 0
execute if score global bar = global bar run scoreboard players set global tmp294 1
scoreboard players operation global tmp293 = global tmp294
```

`@function demo:foo/nested_execute_102`

```mcfunction
scoreboard players set global tmp296 0
execute if score global bar = global foo run scoreboard players set global tmp296 1
scoreboard players operation global tmp295 = global tmp296
```

`@function demo:foo/nested_execute_103`

```mcfunction
scoreboard players set global tmp299 0
execute if score global bar = global bar run scoreboard players set global tmp299 1
scoreboard players operation global tmp298 = global tmp299
```

`@function demo:foo/nested_execute_104`

```mcfunction
scoreboard players set global tmp301 0
execute if score global bar = global bar run scoreboard players set global tmp301 1
scoreboard players operation global tmp300 = global tmp301
```

`@function demo:foo/nested_execute_105`

```mcfunction
scoreboard players set global tmp304 0
execute if score global foo = global foo run scoreboard players set global tmp304 1
scoreboard players operation global tmp303 = global tmp304
```

`@function demo:foo/nested_execute_106`

```mcfunction
scoreboard players set global tmp306 0
execute if score global foo = global foo run scoreboard players set global tmp306 1
scoreboard players operation global tmp305 = global tmp306
```

`@function demo:foo/nested_execute_107`

```mcfunction
scoreboard players set global tmp309 0
execute if score global foo = global foo run scoreboard players set global tmp309 1
scoreboard players operation global tmp308 = global tmp309
```

`@function demo:foo/nested_execute_108`

```mcfunction
scoreboard players set global tmp311 0
execute if score global foo = global bar run scoreboard players set global tmp311 1
scoreboard players operation global tmp310 = global tmp311
```

`@function demo:foo/nested_execute_109`

```mcfunction
scoreboard players set global tmp314 0
execute if score global foo = global bar run scoreboard players set global tmp314 1
scoreboard players operation global tmp313 = global tmp314
```

`@function demo:foo/nested_execute_11`

```mcfunction
scoreboard players set global tmp34 0
execute if score global foo matches 123 run scoreboard players set global tmp34 1
scoreboard players operation global tmp33 = global tmp34
```

`@function demo:foo/nested_execute_110`

```mcfunction
scoreboard players set global tmp316 0
execute if score global bar = global foo run scoreboard players set global tmp316 1
scoreboard players operation global tmp315 = global tmp316
```

`@function demo:foo/nested_execute_111`

```mcfunction
scoreboard players set global tmp319 0
execute if score global foo = global bar run scoreboard players set global tmp319 1
scoreboard players operation global tmp318 = global tmp319
```

`@function demo:foo/nested_execute_112`

```mcfunction
scoreboard players set global tmp321 0
execute if score global bar = global bar run scoreboard players set global tmp321 1
scoreboard players operation global tmp320 = global tmp321
```

`@function demo:foo/nested_execute_113`

```mcfunction
scoreboard players set global tmp324 0
execute if score global bar = global foo run scoreboard players set global tmp324 1
scoreboard players operation global tmp323 = global tmp324
```

`@function demo:foo/nested_execute_114`

```mcfunction
scoreboard players set global tmp326 0
execute if score global foo = global foo run scoreboard players set global tmp326 1
scoreboard players operation global tmp325 = global tmp326
```

`@function demo:foo/nested_execute_115`

```mcfunction
scoreboard players set global tmp329 0
execute if score global bar = global foo run scoreboard players set global tmp329 1
scoreboard players operation global tmp328 = global tmp329
```

`@function demo:foo/nested_execute_116`

```mcfunction
scoreboard players set global tmp331 0
execute if score global foo = global bar run scoreboard players set global tmp331 1
scoreboard players operation global tmp330 = global tmp331
```

`@function demo:foo/nested_execute_117`

```mcfunction
scoreboard players set global tmp334 0
execute if score global bar = global bar run scoreboard players set global tmp334 1
scoreboard players operation global tmp333 = global tmp334
```

`@function demo:foo/nested_execute_118`

```mcfunction
scoreboard players set global tmp336 0
execute if score global bar = global foo run scoreboard players set global tmp336 1
scoreboard players operation global tmp335 = global tmp336
```

`@function demo:foo/nested_execute_119`

```mcfunction
scoreboard players set global tmp339 0
execute if score global bar = global bar run scoreboard players set global tmp339 1
scoreboard players operation global tmp338 = global tmp339
```

`@function demo:foo/nested_execute_12`

```mcfunction
scoreboard players set global tmp37 0
execute if score global foo = global foo run scoreboard players set global tmp37 1
scoreboard players operation global tmp36 = global tmp37
```

`@function demo:foo/nested_execute_120`

```mcfunction
scoreboard players set global tmp341 0
execute if score global bar = global bar run scoreboard players set global tmp341 1
scoreboard players operation global tmp340 = global tmp341
```

`@function demo:foo/nested_execute_13`

```mcfunction
scoreboard players set global tmp39 0
execute if score global foo = global foo run scoreboard players set global tmp39 1
scoreboard players operation global tmp38 = global tmp39
```

`@function demo:foo/nested_execute_14`

```mcfunction
scoreboard players set global tmp46 0
execute if score global foo matches 123 run scoreboard players set global tmp46 1
scoreboard players operation global tmp45 = global tmp46
```

`@function demo:foo/nested_execute_15`

```mcfunction
scoreboard players set global tmp49 0
execute if score global foo matches 123 run scoreboard players set global tmp49 1
scoreboard players operation global tmp48 = global tmp49
```

`@function demo:foo/nested_execute_16`

```mcfunction
scoreboard players set global tmp51 0
execute if score global foo matches 123 run scoreboard players set global tmp51 1
scoreboard players operation global tmp50 = global tmp51
```

`@function demo:foo/nested_execute_17`

```mcfunction
scoreboard players set global tmp54 0
execute if score global foo matches 123 run scoreboard players set global tmp54 1
scoreboard players operation global tmp53 = global tmp54
```

`@function demo:foo/nested_execute_18`

```mcfunction
scoreboard players set global tmp56 0
execute if score global foo = global foo run scoreboard players set global tmp56 1
scoreboard players operation global tmp55 = global tmp56
```

`@function demo:foo/nested_execute_19`

```mcfunction
scoreboard players set global tmp59 0
execute if score global foo matches 123 run scoreboard players set global tmp59 1
scoreboard players operation global tmp58 = global tmp59
```

`@function demo:foo/nested_execute_2`

```mcfunction
scoreboard players set global tmp7 0
execute if score global seven = global seven run scoreboard players set global tmp7 1
scoreboard players operation global tmp6 = global tmp7
```

`@function demo:foo/nested_execute_20`

```mcfunction
scoreboard players set global tmp63 0
execute if score global foo matches 123 run scoreboard players set global tmp63 1
scoreboard players operation global tmp62 = global tmp63
```

`@function demo:foo/nested_execute_21`

```mcfunction
scoreboard players set global tmp65 0
execute if score global foo matches 123 run scoreboard players set global tmp65 1
scoreboard players operation global tmp64 = global tmp65
```

`@function demo:foo/nested_execute_22`

```mcfunction
scoreboard players set global tmp68 0
execute if score global foo = global foo run scoreboard players set global tmp68 1
scoreboard players operation global tmp67 = global tmp68
```

`@function demo:foo/nested_execute_23`

```mcfunction
scoreboard players set global tmp70 0
execute if score global foo matches 123 run scoreboard players set global tmp70 1
scoreboard players operation global tmp69 = global tmp70
```

`@function demo:foo/nested_execute_24`

```mcfunction
scoreboard players set global tmp73 0
execute if score global foo = global foo run scoreboard players set global tmp73 1
scoreboard players operation global tmp72 = global tmp73
```

`@function demo:foo/nested_execute_25`

```mcfunction
scoreboard players set global tmp75 0
execute if score global foo = global foo run scoreboard players set global tmp75 1
scoreboard players operation global tmp74 = global tmp75
```

`@function demo:foo/nested_execute_26`

```mcfunction
scoreboard players set global tmp79 0
execute if score global bar matches 123 run scoreboard players set global tmp79 1
scoreboard players operation global tmp78 = global tmp79
```

`@function demo:foo/nested_execute_27`

```mcfunction
scoreboard players set global tmp82 0
execute if score global bar = global bar run scoreboard players set global tmp82 1
scoreboard players operation global tmp81 = global tmp82
```

`@function demo:foo/nested_execute_28`

```mcfunction
scoreboard players set global tmp85 0
execute if score global bar matches 123 run scoreboard players set global tmp85 1
scoreboard players operation global tmp84 = global tmp85
```

`@function demo:foo/nested_execute_29`

```mcfunction
scoreboard players set global tmp89 0
execute if score global bar matches 123 run scoreboard players set global tmp89 1
scoreboard players operation global tmp88 = global tmp89
```

`@function demo:foo/nested_execute_3`

```mcfunction
scoreboard players set global tmp9 0
execute if score global seven = global seven run scoreboard players set global tmp9 1
scoreboard players operation global tmp8 = global tmp9
```

`@function demo:foo/nested_execute_30`

```mcfunction
scoreboard players set global tmp91 0
execute if score global bar matches 123 run scoreboard players set global tmp91 1
scoreboard players operation global tmp90 = global tmp91
```

`@function demo:foo/nested_execute_31`

```mcfunction
scoreboard players set global tmp94 0
execute if score global bar = global bar run scoreboard players set global tmp94 1
scoreboard players operation global tmp93 = global tmp94
```

`@function demo:foo/nested_execute_32`

```mcfunction
scoreboard players set global tmp96 0
execute if score global bar matches 123 run scoreboard players set global tmp96 1
scoreboard players operation global tmp95 = global tmp96
```

`@function demo:foo/nested_execute_33`

```mcfunction
scoreboard players set global tmp99 0
execute if score global bar = global bar run scoreboard players set global tmp99 1
scoreboard players operation global tmp98 = global tmp99
```

`@function demo:foo/nested_execute_34`

```mcfunction
scoreboard players set global tmp101 0
execute if score global bar = global bar run scoreboard players set global tmp101 1
scoreboard players operation global tmp100 = global tmp101
```

`@function demo:foo/nested_execute_35`

```mcfunction
scoreboard players set global tmp108 0
execute if score global bar matches 123 run scoreboard players set global tmp108 1
scoreboard players operation global tmp107 = global tmp108
```

`@function demo:foo/nested_execute_36`

```mcfunction
scoreboard players set global tmp111 0
execute if score global bar matches 123 run scoreboard players set global tmp111 1
scoreboard players operation global tmp110 = global tmp111
```

`@function demo:foo/nested_execute_37`

```mcfunction
scoreboard players set global tmp113 0
execute if score global bar matches 123 run scoreboard players set global tmp113 1
scoreboard players operation global tmp112 = global tmp113
```

`@function demo:foo/nested_execute_38`

```mcfunction
scoreboard players set global tmp116 0
execute if score global bar matches 123 run scoreboard players set global tmp116 1
scoreboard players operation global tmp115 = global tmp116
```

`@function demo:foo/nested_execute_39`

```mcfunction
scoreboard players set global tmp118 0
execute if score global bar = global bar run scoreboard players set global tmp118 1
scoreboard players operation global tmp117 = global tmp118
```

`@function demo:foo/nested_execute_4`

```mcfunction
scoreboard players set global tmp13 0
execute if score global tmp10 = global thing run scoreboard players set global tmp13 1
scoreboard players operation global tmp12 = global tmp13
```

`@function demo:foo/nested_execute_40`

```mcfunction
scoreboard players set global tmp121 0
execute if score global bar matches 123 run scoreboard players set global tmp121 1
scoreboard players operation global tmp120 = global tmp121
```

`@function demo:foo/nested_execute_41`

```mcfunction
scoreboard players set global tmp125 0
execute if score global bar matches 123 run scoreboard players set global tmp125 1
scoreboard players operation global tmp124 = global tmp125
```

`@function demo:foo/nested_execute_42`

```mcfunction
scoreboard players set global tmp127 0
execute if score global bar matches 123 run scoreboard players set global tmp127 1
scoreboard players operation global tmp126 = global tmp127
```

`@function demo:foo/nested_execute_43`

```mcfunction
scoreboard players set global tmp130 0
execute if score global bar = global bar run scoreboard players set global tmp130 1
scoreboard players operation global tmp129 = global tmp130
```

`@function demo:foo/nested_execute_44`

```mcfunction
scoreboard players set global tmp132 0
execute if score global bar matches 123 run scoreboard players set global tmp132 1
scoreboard players operation global tmp131 = global tmp132
```

`@function demo:foo/nested_execute_45`

```mcfunction
scoreboard players set global tmp135 0
execute if score global bar = global bar run scoreboard players set global tmp135 1
scoreboard players operation global tmp134 = global tmp135
```

`@function demo:foo/nested_execute_46`

```mcfunction
scoreboard players set global tmp137 0
execute if score global bar = global bar run scoreboard players set global tmp137 1
scoreboard players operation global tmp136 = global tmp137
```

`@function demo:foo/nested_execute_47`

```mcfunction
scoreboard players set global tmp141 0
execute if score global foo matches 456 run scoreboard players set global tmp141 1
scoreboard players operation global tmp140 = global tmp141
```

`@function demo:foo/nested_execute_48`

```mcfunction
scoreboard players set global tmp144 0
execute if score global foo = global foo run scoreboard players set global tmp144 1
scoreboard players operation global tmp143 = global tmp144
```

`@function demo:foo/nested_execute_49`

```mcfunction
scoreboard players set global tmp147 0
execute if score global foo matches 456 run scoreboard players set global tmp147 1
scoreboard players operation global tmp146 = global tmp147
```

`@function demo:foo/nested_execute_5`

```mcfunction
scoreboard players set global tmp17 0
execute if score global foo matches 123 run scoreboard players set global tmp17 1
scoreboard players operation global tmp16 = global tmp17
```

`@function demo:foo/nested_execute_50`

```mcfunction
scoreboard players set global tmp151 0
execute if score global foo matches 456 run scoreboard players set global tmp151 1
scoreboard players operation global tmp150 = global tmp151
```

`@function demo:foo/nested_execute_51`

```mcfunction
scoreboard players set global tmp153 0
execute if score global foo matches 456 run scoreboard players set global tmp153 1
scoreboard players operation global tmp152 = global tmp153
```

`@function demo:foo/nested_execute_52`

```mcfunction
scoreboard players set global tmp156 0
execute if score global foo = global foo run scoreboard players set global tmp156 1
scoreboard players operation global tmp155 = global tmp156
```

`@function demo:foo/nested_execute_53`

```mcfunction
scoreboard players set global tmp158 0
execute if score global foo matches 456 run scoreboard players set global tmp158 1
scoreboard players operation global tmp157 = global tmp158
```

`@function demo:foo/nested_execute_54`

```mcfunction
scoreboard players set global tmp161 0
execute if score global foo = global foo run scoreboard players set global tmp161 1
scoreboard players operation global tmp160 = global tmp161
```

`@function demo:foo/nested_execute_55`

```mcfunction
scoreboard players set global tmp163 0
execute if score global foo = global foo run scoreboard players set global tmp163 1
scoreboard players operation global tmp162 = global tmp163
```

`@function demo:foo/nested_execute_56`

```mcfunction
scoreboard players set global tmp170 0
execute if score global foo matches 456 run scoreboard players set global tmp170 1
scoreboard players operation global tmp169 = global tmp170
```

`@function demo:foo/nested_execute_57`

```mcfunction
scoreboard players set global tmp173 0
execute if score global foo matches 456 run scoreboard players set global tmp173 1
scoreboard players operation global tmp172 = global tmp173
```

`@function demo:foo/nested_execute_58`

```mcfunction
scoreboard players set global tmp175 0
execute if score global foo matches 456 run scoreboard players set global tmp175 1
scoreboard players operation global tmp174 = global tmp175
```

`@function demo:foo/nested_execute_59`

```mcfunction
scoreboard players set global tmp178 0
execute if score global foo matches 456 run scoreboard players set global tmp178 1
scoreboard players operation global tmp177 = global tmp178
```

`@function demo:foo/nested_execute_6`

```mcfunction
scoreboard players set global tmp20 0
execute if score global foo = global foo run scoreboard players set global tmp20 1
scoreboard players operation global tmp19 = global tmp20
```

`@function demo:foo/nested_execute_60`

```mcfunction
scoreboard players set global tmp180 0
execute if score global foo = global foo run scoreboard players set global tmp180 1
scoreboard players operation global tmp179 = global tmp180
```

`@function demo:foo/nested_execute_61`

```mcfunction
scoreboard players set global tmp183 0
execute if score global foo matches 456 run scoreboard players set global tmp183 1
scoreboard players operation global tmp182 = global tmp183
```

`@function demo:foo/nested_execute_62`

```mcfunction
scoreboard players set global tmp187 0
execute if score global foo matches 456 run scoreboard players set global tmp187 1
scoreboard players operation global tmp186 = global tmp187
```

`@function demo:foo/nested_execute_63`

```mcfunction
scoreboard players set global tmp189 0
execute if score global foo matches 456 run scoreboard players set global tmp189 1
scoreboard players operation global tmp188 = global tmp189
```

`@function demo:foo/nested_execute_64`

```mcfunction
scoreboard players set global tmp192 0
execute if score global foo = global foo run scoreboard players set global tmp192 1
scoreboard players operation global tmp191 = global tmp192
```

`@function demo:foo/nested_execute_65`

```mcfunction
scoreboard players set global tmp194 0
execute if score global foo matches 456 run scoreboard players set global tmp194 1
scoreboard players operation global tmp193 = global tmp194
```

`@function demo:foo/nested_execute_66`

```mcfunction
scoreboard players set global tmp197 0
execute if score global foo = global foo run scoreboard players set global tmp197 1
scoreboard players operation global tmp196 = global tmp197
```

`@function demo:foo/nested_execute_67`

```mcfunction
scoreboard players set global tmp199 0
execute if score global foo = global foo run scoreboard players set global tmp199 1
scoreboard players operation global tmp198 = global tmp199
```

`@function demo:foo/nested_execute_68`

```mcfunction
scoreboard players set global tmp203 0
execute if score global bar matches 456 run scoreboard players set global tmp203 1
scoreboard players operation global tmp202 = global tmp203
```

`@function demo:foo/nested_execute_69`

```mcfunction
scoreboard players set global tmp206 0
execute if score global bar = global bar run scoreboard players set global tmp206 1
scoreboard players operation global tmp205 = global tmp206
```

`@function demo:foo/nested_execute_7`

```mcfunction
scoreboard players set global tmp23 0
execute if score global foo matches 123 run scoreboard players set global tmp23 1
scoreboard players operation global tmp22 = global tmp23
```

`@function demo:foo/nested_execute_70`

```mcfunction
scoreboard players set global tmp209 0
execute if score global bar matches 456 run scoreboard players set global tmp209 1
scoreboard players operation global tmp208 = global tmp209
```

`@function demo:foo/nested_execute_71`

```mcfunction
scoreboard players set global tmp213 0
execute if score global bar matches 456 run scoreboard players set global tmp213 1
scoreboard players operation global tmp212 = global tmp213
```

`@function demo:foo/nested_execute_72`

```mcfunction
scoreboard players set global tmp215 0
execute if score global bar matches 456 run scoreboard players set global tmp215 1
scoreboard players operation global tmp214 = global tmp215
```

`@function demo:foo/nested_execute_73`

```mcfunction
scoreboard players set global tmp218 0
execute if score global bar = global bar run scoreboard players set global tmp218 1
scoreboard players operation global tmp217 = global tmp218
```

`@function demo:foo/nested_execute_74`

```mcfunction
scoreboard players set global tmp220 0
execute if score global bar matches 456 run scoreboard players set global tmp220 1
scoreboard players operation global tmp219 = global tmp220
```

`@function demo:foo/nested_execute_75`

```mcfunction
scoreboard players set global tmp223 0
execute if score global bar = global bar run scoreboard players set global tmp223 1
scoreboard players operation global tmp222 = global tmp223
```

`@function demo:foo/nested_execute_76`

```mcfunction
scoreboard players set global tmp225 0
execute if score global bar = global bar run scoreboard players set global tmp225 1
scoreboard players operation global tmp224 = global tmp225
```

`@function demo:foo/nested_execute_77`

```mcfunction
scoreboard players set global tmp232 0
execute if score global bar matches 456 run scoreboard players set global tmp232 1
scoreboard players operation global tmp231 = global tmp232
```

`@function demo:foo/nested_execute_78`

```mcfunction
scoreboard players set global tmp235 0
execute if score global bar matches 456 run scoreboard players set global tmp235 1
scoreboard players operation global tmp234 = global tmp235
```

`@function demo:foo/nested_execute_79`

```mcfunction
scoreboard players set global tmp237 0
execute if score global bar matches 456 run scoreboard players set global tmp237 1
scoreboard players operation global tmp236 = global tmp237
```

`@function demo:foo/nested_execute_8`

```mcfunction
scoreboard players set global tmp27 0
execute if score global foo matches 123 run scoreboard players set global tmp27 1
scoreboard players operation global tmp26 = global tmp27
```

`@function demo:foo/nested_execute_80`

```mcfunction
scoreboard players set global tmp240 0
execute if score global bar matches 456 run scoreboard players set global tmp240 1
scoreboard players operation global tmp239 = global tmp240
```

`@function demo:foo/nested_execute_81`

```mcfunction
scoreboard players set global tmp242 0
execute if score global bar = global bar run scoreboard players set global tmp242 1
scoreboard players operation global tmp241 = global tmp242
```

`@function demo:foo/nested_execute_82`

```mcfunction
scoreboard players set global tmp245 0
execute if score global bar matches 456 run scoreboard players set global tmp245 1
scoreboard players operation global tmp244 = global tmp245
```

`@function demo:foo/nested_execute_83`

```mcfunction
scoreboard players set global tmp249 0
execute if score global bar matches 456 run scoreboard players set global tmp249 1
scoreboard players operation global tmp248 = global tmp249
```

`@function demo:foo/nested_execute_84`

```mcfunction
scoreboard players set global tmp251 0
execute if score global bar matches 456 run scoreboard players set global tmp251 1
scoreboard players operation global tmp250 = global tmp251
```

`@function demo:foo/nested_execute_85`

```mcfunction
scoreboard players set global tmp254 0
execute if score global bar = global bar run scoreboard players set global tmp254 1
scoreboard players operation global tmp253 = global tmp254
```

`@function demo:foo/nested_execute_86`

```mcfunction
scoreboard players set global tmp256 0
execute if score global bar matches 456 run scoreboard players set global tmp256 1
scoreboard players operation global tmp255 = global tmp256
```

`@function demo:foo/nested_execute_87`

```mcfunction
scoreboard players set global tmp259 0
execute if score global bar = global bar run scoreboard players set global tmp259 1
scoreboard players operation global tmp258 = global tmp259
```

`@function demo:foo/nested_execute_88`

```mcfunction
scoreboard players set global tmp261 0
execute if score global bar = global bar run scoreboard players set global tmp261 1
scoreboard players operation global tmp260 = global tmp261
```

`@function demo:foo/nested_execute_89`

```mcfunction
scoreboard players set global tmp264 0
execute if score global foo = global foo run scoreboard players set global tmp264 1
scoreboard players operation global tmp263 = global tmp264
```

`@function demo:foo/nested_execute_9`

```mcfunction
scoreboard players set global tmp29 0
execute if score global foo matches 123 run scoreboard players set global tmp29 1
scoreboard players operation global tmp28 = global tmp29
```

`@function demo:foo/nested_execute_90`

```mcfunction
scoreboard players set global tmp266 0
execute if score global foo = global foo run scoreboard players set global tmp266 1
scoreboard players operation global tmp265 = global tmp266
```

`@function demo:foo/nested_execute_91`

```mcfunction
scoreboard players set global tmp269 0
execute if score global foo = global foo run scoreboard players set global tmp269 1
scoreboard players operation global tmp268 = global tmp269
```

`@function demo:foo/nested_execute_92`

```mcfunction
scoreboard players set global tmp271 0
execute if score global foo = global bar run scoreboard players set global tmp271 1
scoreboard players operation global tmp270 = global tmp271
```

`@function demo:foo/nested_execute_93`

```mcfunction
scoreboard players set global tmp274 0
execute if score global foo = global bar run scoreboard players set global tmp274 1
scoreboard players operation global tmp273 = global tmp274
```

`@function demo:foo/nested_execute_94`

```mcfunction
scoreboard players set global tmp276 0
execute if score global bar = global foo run scoreboard players set global tmp276 1
scoreboard players operation global tmp275 = global tmp276
```

`@function demo:foo/nested_execute_95`

```mcfunction
scoreboard players set global tmp279 0
execute if score global foo = global bar run scoreboard players set global tmp279 1
scoreboard players operation global tmp278 = global tmp279
```

`@function demo:foo/nested_execute_96`

```mcfunction
scoreboard players set global tmp281 0
execute if score global bar = global bar run scoreboard players set global tmp281 1
scoreboard players operation global tmp280 = global tmp281
```

`@function demo:foo/nested_execute_97`

```mcfunction
scoreboard players set global tmp284 0
execute if score global bar = global foo run scoreboard players set global tmp284 1
scoreboard players operation global tmp283 = global tmp284
```

`@function demo:foo/nested_execute_98`

```mcfunction
scoreboard players set global tmp286 0
execute if score global foo = global foo run scoreboard players set global tmp286 1
scoreboard players operation global tmp285 = global tmp286
```

`@function demo:foo/nested_execute_99`

```mcfunction
scoreboard players set global tmp289 0
execute if score global bar = global foo run scoreboard players set global tmp289 1
scoreboard players operation global tmp288 = global tmp289
```
