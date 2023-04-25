# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 12,
    "description": ""
  }
}
```

### demo

`@function(strip_final_newline) demo:ref/bar`

```mcfunction

```

`@function demo:ref/foo`

```mcfunction
say !!!
say hello anonymous
summon minecraft:squid
say !!!
say ok ok
say hello steve
say AstResourceLocation(is_tag=False, namespace='minecraft', path='becomeduck')
say !!!
```

`@function demo:codegen/bar`

```mcfunction
_bolt_lineno = [1], [1]
_bolt_helper_children = _bolt_runtime.helpers['children']
_bolt_helper_replace = _bolt_runtime.helpers['replace']
with _bolt_runtime.scope() as _bolt_var1:
    CALAMAR, dump_ast, anonymous, _bolt_macro0, _bolt_macro1 = _bolt_runtime.from_module_import('demo:codegen/prelude', 'CALAMAR', 'dump_ast', 'anonymous', '_bolt_macro0', '_bolt_macro1')
    alright_then, _bolt_macro2 = _bolt_runtime.from_module_import('no_idea:prelude', 'alright_then', '_bolt_macro0')
    _bolt_var0 = dump_ast
    _bolt_var0 = _bolt_var0()
_bolt_var2 = _bolt_helper_replace(_bolt_refs[0], commands=_bolt_helper_children(_bolt_var1))
```

`@function demo:codegen/foo`

```mcfunction
_bolt_lineno = [1, 13, 18, 22, 26, 28, 31, 33], [1, 2, 3, 4, 6, 7, 10, 11]
_bolt_helper_macro_call = _bolt_runtime.helpers['macro_call']
_bolt_helper_interpolate_word = _bolt_runtime.helpers['interpolate_word']
_bolt_helper_children = _bolt_runtime.helpers['children']
_bolt_helper_replace = _bolt_runtime.helpers['replace']
_bolt_helper_interpolate_resource_location = _bolt_runtime.helpers['interpolate_resource_location']
_bolt_helper_get_rebind = _bolt_runtime.helpers['get_rebind']
with _bolt_runtime.scope() as _bolt_var9:
    CALAMAR, dump_ast, anonymous, _bolt_macro0, _bolt_macro1 = _bolt_runtime.from_module_import('demo:codegen/prelude', 'CALAMAR', 'dump_ast', 'anonymous', '_bolt_macro0', '_bolt_macro1')
    alright_then, _bolt_macro2 = _bolt_runtime.from_module_import('no_idea:prelude', 'alright_then', '_bolt_macro0')
    _bolt_var0 = _bolt_helper_macro_call(_bolt_runtime, _bolt_macro1, _bolt_refs[0])
    _bolt_runtime.commands.extend(_bolt_var0)
    _bolt_var1 = anonymous
    _bolt_var1 = _bolt_var1()
    _bolt_var1 = _bolt_helper_interpolate_word(_bolt_var1, _bolt_refs[1])
    _bolt_var2 = _bolt_helper_macro_call(_bolt_runtime, _bolt_macro0, _bolt_helper_replace(_bolt_refs[2], arguments=_bolt_helper_children([_bolt_var1])))
    _bolt_runtime.commands.extend(_bolt_var2)
    _bolt_var3 = CALAMAR
    _bolt_var3 = _bolt_helper_interpolate_resource_location(_bolt_var3, _bolt_refs[3])
    _bolt_runtime.commands.append(_bolt_helper_replace(_bolt_refs[4], arguments=_bolt_helper_children([_bolt_var3])))
    _bolt_var4 = None
    _bolt_rebind = _bolt_helper_get_rebind(CALAMAR)
    CALAMAR = _bolt_var4
    if _bolt_rebind is not None:
        CALAMAR = _bolt_rebind(CALAMAR)
    _bolt_var5 = _bolt_helper_macro_call(_bolt_runtime, _bolt_macro1, _bolt_refs[5])
    _bolt_runtime.commands.extend(_bolt_var5)
    _bolt_var6 = alright_then
    _bolt_var6 = _bolt_var6()
    _bolt_runtime.commands.append(_bolt_refs[7])
    _bolt_var7 = _bolt_helper_macro_call(_bolt_runtime, _bolt_macro1, _bolt_refs[6])
    _bolt_runtime.commands.extend(_bolt_var7)
    _bolt_var8 = dump_ast
    _bolt_var8 = _bolt_var8()
_bolt_var10 = _bolt_helper_replace(_bolt_refs[8], commands=_bolt_helper_children(_bolt_var9))
```

`@function(strip_final_newline) demo:bar`

```mcfunction

```

`@function demo:foo`

```mcfunction
say !!!
say hello anonymous
summon minecraft:squid
say !!!
say ok ok
say hello steve
say AstResourceLocation(is_tag=False, namespace='minecraft', path='becomeduck')
say !!!
```

### bolt_prelude

`@function bolt_prelude:generated_0`

```mcfunction
# <class 'mecha.ast.AstRoot'>
#   location: SourceLocation(pos=0, lineno=1, colno=1)
#   end_location: SourceLocation(pos=11, lineno=2, colno=1)
#   commands:
#     <class 'bolt.ast.AstPrelude'>
#       location: SourceLocation(pos=-1, lineno=0, colno=0)
#       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#       identifier: ''
#       arguments:
#         <class 'mecha.ast.AstResourceLocation'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           is_tag: False
#           namespace: 'demo'
#           path: 'prelude'
#         <class 'bolt.ast.AstImportedItem'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: 'CALAMAR'
#           identifier: True
#         <class 'bolt.ast.AstImportedItem'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: 'dump_ast'
#           identifier: True
#         <class 'bolt.ast.AstImportedItem'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: 'anonymous'
#           identifier: True
#         <class 'bolt.ast.AstImportedMacro'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: '_bolt_macro0'
#           declaration:
#             <class 'bolt.ast.AstMacro'>
#               location: SourceLocation(pos=0, lineno=1, colno=1)
#               end_location: SourceLocation(pos=80, lineno=2, colno=30)
#               identifier: 'greet:name'
#               arguments:
#                 <class 'bolt.ast.AstMacroLiteral'>
#                   location: SourceLocation(pos=6, lineno=1, colno=7)
#                   end_location: SourceLocation(pos=11, lineno=1, colno=12)
#                   value: 'greet'
#                 <class 'bolt.ast.AstMacroMatchArgument'>
#                   location: SourceLocation(pos=12, lineno=1, colno=13)
#                   end_location: SourceLocation(pos=49, lineno=1, colno=50)
#                   match_identifier:
#                     <class 'bolt.ast.AstMacroArgument'>
#                       location: SourceLocation(pos=12, lineno=1, colno=13)
#                       end_location: SourceLocation(pos=16, lineno=1, colno=17)
#                       value: 'name'
#                   match_argument_parser:
#                     <class 'mecha.ast.AstResourceLocation'>
#                       location: SourceLocation(pos=17, lineno=1, colno=18)
#                       end_location: SourceLocation(pos=33, lineno=1, colno=34)
#                       is_tag: False
#                       namespace: 'brigadier'
#                       path: 'string'
#                   match_argument_properties:
#                     <class 'mecha.ast.AstJsonObject'>
#                       location: SourceLocation(pos=33, lineno=1, colno=34)
#                       end_location: SourceLocation(pos=49, lineno=1, colno=50)
#                       entries:
#                         <class 'mecha.ast.AstJsonObjectEntry'>
#                           location: SourceLocation(pos=34, lineno=1, colno=35)
#                           end_location: SourceLocation(pos=48, lineno=1, colno=49)
#                           key:
#                             <class 'mecha.ast.AstJsonObjectKey'>
#                               location: SourceLocation(pos=34, lineno=1, colno=35)
#                               end_location: SourceLocation(pos=40, lineno=1, colno=41)
#                               value: 'type'
#                           value:
#                             <class 'mecha.ast.AstJsonValue'>
#                               location: SourceLocation(pos=42, lineno=1, colno=43)
#                               end_location: SourceLocation(pos=48, lineno=1, colno=49)
#                               value: 'word'
#         <class 'bolt.ast.AstImportedMacro'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: '_bolt_macro1'
#           declaration:
#             <class 'bolt.ast.AstMacro'>
#               location: SourceLocation(pos=66, lineno=4, colno=1)
#               end_location: SourceLocation(pos=88, lineno=5, colno=12)
#               identifier: '!!!'
#               arguments:
#                 <class 'bolt.ast.AstMacroLiteral'>
#                   location: SourceLocation(pos=72, lineno=4, colno=7)
#                   end_location: SourceLocation(pos=75, lineno=4, colno=10)
#                   value: '!!!'
#     <class 'bolt.ast.AstPrelude'>
#       location: SourceLocation(pos=-1, lineno=0, colno=0)
#       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#       identifier: ''
#       arguments:
#         <class 'mecha.ast.AstResourceLocation'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           is_tag: False
#           namespace: 'no_idea'
#           path: 'prelude'
#         <class 'bolt.ast.AstImportedItem'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: 'alright_then'
#           identifier: True
#         <class 'bolt.ast.AstImportedMacro'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: '_bolt_macro0'
#           declaration:
#             <class 'bolt.ast.AstProcMacro'>
#               location: SourceLocation(pos=32, lineno=3, colno=1)
#               end_location: SourceLocation(pos=156, lineno=6, colno=19)
#               identifier: 'what:about:proc_macro_overload0'
#               arguments:
#                 <class 'bolt.ast.AstMacroLiteral'>
#                   location: SourceLocation(pos=38, lineno=3, colno=7)
#                   end_location: SourceLocation(pos=42, lineno=3, colno=11)
#                   value: 'what'
#                 <class 'bolt.ast.AstMacroMatchLiteral'>
#                   location: SourceLocation(pos=43, lineno=3, colno=12)
#                   end_location: SourceLocation(pos=48, lineno=3, colno=17)
#                   match:
#                     <class 'bolt.ast.AstMacroLiteral'>
#                       location: SourceLocation(pos=43, lineno=3, colno=12)
#                       end_location: SourceLocation(pos=48, lineno=3, colno=17)
#                       value: 'about'
#                 <class 'bolt.ast.AstMacroMatchArgument'>
#                   location: SourceLocation(pos=-1, lineno=0, colno=0)
#                   end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                   match_identifier:
#                     <class 'bolt.ast.AstMacroArgument'>
#                       location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       value: 'proc_macro_overload0'
#                   match_argument_parser:
#                     <class 'mecha.ast.AstResourceLocation'>
#                       location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       is_tag: False
#                       namespace: 'bolt'
#                       path: 'proc_macro'
#                   match_argument_properties:
#                     <class 'mecha.ast.AstJsonObject'>
#                       location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       entries:
#                         <class 'mecha.ast.AstJsonObjectEntry'>
#                           location: SourceLocation(pos=-1, lineno=0, colno=0)
#                           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                           key:
#                             <class 'mecha.ast.AstJsonObjectKey'>
#                               location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               value: 'resource_location'
#                           value:
#                             <class 'mecha.ast.AstJsonValue'>
#                               location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               value: 'no_idea:prelude'
#                         <class 'mecha.ast.AstJsonObjectEntry'>
#                           location: SourceLocation(pos=-1, lineno=0, colno=0)
#                           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                           key:
#                             <class 'mecha.ast.AstJsonObjectKey'>
#                               location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               value: 'identifier'
#                           value:
#                             <class 'mecha.ast.AstJsonValue'>
#                               location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               value: 'what:about:proc_macro_overload0'
#     <class 'mecha.ast.AstCommand'>
#       location: SourceLocation(pos=0, lineno=1, colno=1)
#       end_location: SourceLocation(pos=10, lineno=1, colno=11)
#       identifier: 'statement'
#       arguments:
#         <class 'bolt.ast.AstCall'>
#           location: SourceLocation(pos=0, lineno=1, colno=1)
#           end_location: SourceLocation(pos=10, lineno=1, colno=11)
#           value:
#             <class 'bolt.ast.AstIdentifier'>
#               location: SourceLocation(pos=0, lineno=1, colno=1)
#               end_location: SourceLocation(pos=8, lineno=1, colno=9)
#               value: 'dump_ast'
#           arguments:
#             <empty>
```

`@function bolt_prelude:generated_1`

```mcfunction
# <class 'mecha.ast.AstRoot'>
#   location: SourceLocation(pos=0, lineno=1, colno=1)
#   end_location: SourceLocation(pos=120, lineno=12, colno=1)
#   commands:
#     <class 'bolt.ast.AstPrelude'>
#       location: SourceLocation(pos=-1, lineno=0, colno=0)
#       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#       identifier: ''
#       arguments:
#         <class 'mecha.ast.AstResourceLocation'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           is_tag: False
#           namespace: 'demo'
#           path: 'prelude'
#         <class 'bolt.ast.AstImportedItem'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: 'CALAMAR'
#           identifier: True
#         <class 'bolt.ast.AstImportedItem'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: 'dump_ast'
#           identifier: True
#         <class 'bolt.ast.AstImportedItem'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: 'anonymous'
#           identifier: True
#         <class 'bolt.ast.AstImportedMacro'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: '_bolt_macro0'
#           declaration:
#             <class 'bolt.ast.AstMacro'>
#               location: SourceLocation(pos=0, lineno=1, colno=1)
#               end_location: SourceLocation(pos=80, lineno=2, colno=30)
#               identifier: 'greet:name'
#               arguments:
#                 <class 'bolt.ast.AstMacroLiteral'>
#                   location: SourceLocation(pos=6, lineno=1, colno=7)
#                   end_location: SourceLocation(pos=11, lineno=1, colno=12)
#                   value: 'greet'
#                 <class 'bolt.ast.AstMacroMatchArgument'>
#                   location: SourceLocation(pos=12, lineno=1, colno=13)
#                   end_location: SourceLocation(pos=49, lineno=1, colno=50)
#                   match_identifier:
#                     <class 'bolt.ast.AstMacroArgument'>
#                       location: SourceLocation(pos=12, lineno=1, colno=13)
#                       end_location: SourceLocation(pos=16, lineno=1, colno=17)
#                       value: 'name'
#                   match_argument_parser:
#                     <class 'mecha.ast.AstResourceLocation'>
#                       location: SourceLocation(pos=17, lineno=1, colno=18)
#                       end_location: SourceLocation(pos=33, lineno=1, colno=34)
#                       is_tag: False
#                       namespace: 'brigadier'
#                       path: 'string'
#                   match_argument_properties:
#                     <class 'mecha.ast.AstJsonObject'>
#                       location: SourceLocation(pos=33, lineno=1, colno=34)
#                       end_location: SourceLocation(pos=49, lineno=1, colno=50)
#                       entries:
#                         <class 'mecha.ast.AstJsonObjectEntry'>
#                           location: SourceLocation(pos=34, lineno=1, colno=35)
#                           end_location: SourceLocation(pos=48, lineno=1, colno=49)
#                           key:
#                             <class 'mecha.ast.AstJsonObjectKey'>
#                               location: SourceLocation(pos=34, lineno=1, colno=35)
#                               end_location: SourceLocation(pos=40, lineno=1, colno=41)
#                               value: 'type'
#                           value:
#                             <class 'mecha.ast.AstJsonValue'>
#                               location: SourceLocation(pos=42, lineno=1, colno=43)
#                               end_location: SourceLocation(pos=48, lineno=1, colno=49)
#                               value: 'word'
#         <class 'bolt.ast.AstImportedMacro'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: '_bolt_macro1'
#           declaration:
#             <class 'bolt.ast.AstMacro'>
#               location: SourceLocation(pos=66, lineno=4, colno=1)
#               end_location: SourceLocation(pos=88, lineno=5, colno=12)
#               identifier: '!!!'
#               arguments:
#                 <class 'bolt.ast.AstMacroLiteral'>
#                   location: SourceLocation(pos=72, lineno=4, colno=7)
#                   end_location: SourceLocation(pos=75, lineno=4, colno=10)
#                   value: '!!!'
#     <class 'bolt.ast.AstPrelude'>
#       location: SourceLocation(pos=-1, lineno=0, colno=0)
#       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#       identifier: ''
#       arguments:
#         <class 'mecha.ast.AstResourceLocation'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           is_tag: False
#           namespace: 'no_idea'
#           path: 'prelude'
#         <class 'bolt.ast.AstImportedItem'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: 'alright_then'
#           identifier: True
#         <class 'bolt.ast.AstImportedMacro'>
#           location: SourceLocation(pos=-1, lineno=0, colno=0)
#           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#           name: '_bolt_macro0'
#           declaration:
#             <class 'bolt.ast.AstProcMacro'>
#               location: SourceLocation(pos=32, lineno=3, colno=1)
#               end_location: SourceLocation(pos=156, lineno=6, colno=19)
#               identifier: 'what:about:proc_macro_overload0'
#               arguments:
#                 <class 'bolt.ast.AstMacroLiteral'>
#                   location: SourceLocation(pos=38, lineno=3, colno=7)
#                   end_location: SourceLocation(pos=42, lineno=3, colno=11)
#                   value: 'what'
#                 <class 'bolt.ast.AstMacroMatchLiteral'>
#                   location: SourceLocation(pos=43, lineno=3, colno=12)
#                   end_location: SourceLocation(pos=48, lineno=3, colno=17)
#                   match:
#                     <class 'bolt.ast.AstMacroLiteral'>
#                       location: SourceLocation(pos=43, lineno=3, colno=12)
#                       end_location: SourceLocation(pos=48, lineno=3, colno=17)
#                       value: 'about'
#                 <class 'bolt.ast.AstMacroMatchArgument'>
#                   location: SourceLocation(pos=-1, lineno=0, colno=0)
#                   end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                   match_identifier:
#                     <class 'bolt.ast.AstMacroArgument'>
#                       location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       value: 'proc_macro_overload0'
#                   match_argument_parser:
#                     <class 'mecha.ast.AstResourceLocation'>
#                       location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       is_tag: False
#                       namespace: 'bolt'
#                       path: 'proc_macro'
#                   match_argument_properties:
#                     <class 'mecha.ast.AstJsonObject'>
#                       location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                       entries:
#                         <class 'mecha.ast.AstJsonObjectEntry'>
#                           location: SourceLocation(pos=-1, lineno=0, colno=0)
#                           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                           key:
#                             <class 'mecha.ast.AstJsonObjectKey'>
#                               location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               value: 'resource_location'
#                           value:
#                             <class 'mecha.ast.AstJsonValue'>
#                               location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               value: 'no_idea:prelude'
#                         <class 'mecha.ast.AstJsonObjectEntry'>
#                           location: SourceLocation(pos=-1, lineno=0, colno=0)
#                           end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                           key:
#                             <class 'mecha.ast.AstJsonObjectKey'>
#                               location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               value: 'identifier'
#                           value:
#                             <class 'mecha.ast.AstJsonValue'>
#                               location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#                               value: 'what:about:proc_macro_overload0'
#     <class 'bolt.ast.AstMacroCall'>
#       location: SourceLocation(pos=0, lineno=1, colno=1)
#       end_location: SourceLocation(pos=3, lineno=1, colno=4)
#       identifier: '!!!'
#       arguments:
#         <empty>
#     <class 'bolt.ast.AstMacroCall'>
#       location: SourceLocation(pos=4, lineno=2, colno=1)
#       end_location: SourceLocation(pos=21, lineno=2, colno=18)
#       identifier: 'greet:name'
#       arguments:
#         <class 'bolt.ast.AstInterpolation'>
#           location: SourceLocation(pos=10, lineno=2, colno=7)
#           end_location: SourceLocation(pos=21, lineno=2, colno=18)
#           prefix: None
#           unpack: None
#           converter: 'word'
#           value:
#             <class 'bolt.ast.AstCall'>
#               location: SourceLocation(pos=10, lineno=2, colno=7)
#               end_location: SourceLocation(pos=21, lineno=2, colno=18)
#               value:
#                 <class 'bolt.ast.AstIdentifier'>
#                   location: SourceLocation(pos=10, lineno=2, colno=7)
#                   end_location: SourceLocation(pos=19, lineno=2, colno=16)
#                   value: 'anonymous'
#               arguments:
#                 <empty>
#     <class 'mecha.ast.AstCommand'>
#       location: SourceLocation(pos=22, lineno=3, colno=1)
#       end_location: SourceLocation(pos=36, lineno=3, colno=15)
#       identifier: 'summon:entity'
#       arguments:
#         <class 'bolt.ast.AstInterpolation'>
#           location: SourceLocation(pos=29, lineno=3, colno=8)
#           end_location: SourceLocation(pos=36, lineno=3, colno=15)
#           prefix: None
#           unpack: None
#           converter: 'resource_location'
#           value:
#             <class 'bolt.ast.AstIdentifier'>
#               location: SourceLocation(pos=29, lineno=3, colno=8)
#               end_location: SourceLocation(pos=36, lineno=3, colno=15)
#               value: 'CALAMAR'
#     <class 'mecha.ast.AstCommand'>
#       location: SourceLocation(pos=37, lineno=4, colno=1)
#       end_location: SourceLocation(pos=51, lineno=4, colno=15)
#       identifier: 'statement'
#       arguments:
#         <class 'bolt.ast.AstAssignment'>
#           location: SourceLocation(pos=37, lineno=4, colno=1)
#           end_location: SourceLocation(pos=51, lineno=4, colno=15)
#           operator: '='
#           target:
#             <class 'bolt.ast.AstTargetIdentifier'>
#               location: SourceLocation(pos=37, lineno=4, colno=1)
#               end_location: SourceLocation(pos=44, lineno=4, colno=8)
#               value: 'CALAMAR'
#               rebind: True
#           value:
#             <class 'bolt.ast.AstValue'>
#               location: SourceLocation(pos=47, lineno=4, colno=11)
#               end_location: SourceLocation(pos=51, lineno=4, colno=15)
#               value: None
#           type_annotation: None
#     <class 'bolt.ast.AstMacroCall'>
#       location: SourceLocation(pos=53, lineno=6, colno=1)
#       end_location: SourceLocation(pos=56, lineno=6, colno=4)
#       identifier: '!!!'
#       arguments:
#         <empty>
#     <class 'mecha.ast.AstCommand'>
#       location: SourceLocation(pos=57, lineno=7, colno=1)
#       end_location: SourceLocation(pos=71, lineno=7, colno=15)
#       identifier: 'statement'
#       arguments:
#         <class 'bolt.ast.AstCall'>
#           location: SourceLocation(pos=57, lineno=7, colno=1)
#           end_location: SourceLocation(pos=71, lineno=7, colno=15)
#           value:
#             <class 'bolt.ast.AstIdentifier'>
#               location: SourceLocation(pos=57, lineno=7, colno=1)
#               end_location: SourceLocation(pos=69, lineno=7, colno=13)
#               value: 'alright_then'
#           arguments:
#             <empty>
#     <class 'mecha.ast.AstCommand'>
#       location: SourceLocation(pos=142, lineno=6, colno=5)
#       end_location: SourceLocation(pos=156, lineno=6, colno=19)
#       identifier: 'say:message'
#       arguments:
#         <class 'mecha.ast.AstMessage'>
#           location: SourceLocation(pos=146, lineno=6, colno=9)
#           end_location: SourceLocation(pos=156, lineno=6, colno=19)
#           fragments:
#             <class 'mecha.ast.AstMessageText'>
#               location: SourceLocation(pos=-1, lineno=0, colno=0)
#               end_location: SourceLocation(pos=-1, lineno=0, colno=0)
#               value: "AstResourceLocation(is_tag=False, namespace='minecraft', path='becomeduck')"
#     <class 'bolt.ast.AstMacroCall'>
#       location: SourceLocation(pos=105, lineno=10, colno=1)
#       end_location: SourceLocation(pos=108, lineno=10, colno=4)
#       identifier: '!!!'
#       arguments:
#         <empty>
#     <class 'mecha.ast.AstCommand'>
#       location: SourceLocation(pos=109, lineno=11, colno=1)
#       end_location: SourceLocation(pos=119, lineno=11, colno=11)
#       identifier: 'statement'
#       arguments:
#         <class 'bolt.ast.AstCall'>
#           location: SourceLocation(pos=109, lineno=11, colno=1)
#           end_location: SourceLocation(pos=119, lineno=11, colno=11)
#           value:
#             <class 'bolt.ast.AstIdentifier'>
#               location: SourceLocation(pos=109, lineno=11, colno=1)
#               end_location: SourceLocation(pos=117, lineno=11, colno=9)
#               value: 'dump_ast'
#           arguments:
#             <empty>
```
