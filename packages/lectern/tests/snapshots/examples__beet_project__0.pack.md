# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 7,
      "description": ""
    }
  }
  ```

  </details>

### with_beet

- `@function with_beet:abc`

  <details>

  ```mcfunction
  function with_beet:def
  ```

  </details>

- `@function with_beet:def`

  <details>

  ```mcfunction
  say relative
  ```

  </details>

### demo

- `@function demo:foo`

  <details>

  ```mcfunction
  say foo
  ```

  </details>

- `@function demo:bar`

  <details>

  ```mcfunction
  say bar
  ```

  </details>

- `@function demo:script_foo`

  <details>

  ```mcfunction
  say something

  ```

  </details>

- `@function demo:script_0`

  <details>

  ```mcfunction
  say 0
  ```

  </details>

- `@function demo:script_1`

  <details>

  ```mcfunction
  say 1
  ```

  </details>

- `@function demo:script_2`

  <details>

  ```mcfunction
  say 2
  ```

  </details>

- `@function demo:script_3`

  <details>

  ```mcfunction
  say 3
  ```

  </details>

- `@function demo:script_4`

  <details>

  ```mcfunction
  say 4
  ```

  </details>

- `@function demo:script_5`

  <details>

  ```mcfunction
  say 5
  ```

  </details>

- `@function demo:script_6`

  <details>

  ```mcfunction
  say 6
  ```

  </details>

- `@function demo:script_7`

  <details>

  ```mcfunction
  say 7
  ```

  </details>

- `@function demo:script_8`

  <details>

  ```mcfunction
  say 8
  ```

  </details>

- `@function demo:script_9`

  <details>

  ```mcfunction
  say 9

  ```

  </details>

- `@function demo:script_nested`

  <details>

  ```mcfunction
  say wow
  ```

  </details>

- `@function demo:script_please_avoid_this`

  <details>

  ```mcfunction
  say no
  ```

  </details>

- `@function demo:define_1`

  <details>

  ```mcfunction
  say azertyuiop
  ```

  </details>

- `@function demo:define_2`

  <details>

  ```mcfunction
  say azertyuiopqsdfghjklm
  ```

  </details>

- `@function demo:define_3`

  <details>

  ```mcfunction
  say 2 + 2 is 4 (end of citation)
  ```

  </details>

### embedded

- `@function embedded:foo`

  <details>

  ```mcfunction
  say foo
  ```

  </details>

- `@function embedded:bar`

  <details>

  ```mcfunction
  say bar
  ```

  </details>

### custom

- `@function custom:hello`

  <details>

  ```mcfunction
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  say hello
  say bye
  ```

  </details>

### hello

- `@function hello:greetings`

  <details>

  ```mcfunction
  say Hello, Alice!
  say Hello, Bob!
  ```

  </details>

### from_script

- `@function from_script:hello`

  <details>

  ```mcfunction
  say hello
  ```

  </details>

- `@function from_script:thing`

  <details>

  ```mcfunction
  say 0
  say 1
  say 2
  say 3
  say 4
  say 5
  say 6
  say 7
  say 8
  say 9
  ```

  </details>

### minecraft

- `@loot_table minecraft:blocks/yellow_shulker_box`

  <details>

  ```json
  {
    "type": "minecraft:block",
    "pools": [
      {
        "rolls": 1,
        "entries": [
          {
            "type": "minecraft:alternatives",
            "children": [
              {
                "type": "minecraft:dynamic",
                "name": "minecraft:contents",
                "conditions": [
                  {
                    "condition": "minecraft:match_tool",
                    "predicate": {
                      "items": [
                        "minecraft:air"
                      ],
                      "nbt": "{drop_contents:1b}"
                    }
                  }
                ]
              },
              {
                "type": "minecraft:item",
                "name": "minecraft:yellow_shulker_box",
                "functions": [
                  {
                    "function": "minecraft:copy_name",
                    "source": "block_entity"
                  },
                  {
                    "function": "minecraft:copy_nbt",
                    "source": "block_entity",
                    "ops": [
                      {
                        "source": "Lock",
                        "target": "BlockEntityTag.Lock",
                        "op": "replace"
                      },
                      {
                        "source": "LootTable",
                        "target": "BlockEntityTag.LootTable",
                        "op": "replace"
                      },
                      {
                        "source": "LootTableSeed",
                        "target": "BlockEntityTag.LootTableSeed",
                        "op": "replace"
                      }
                    ]
                  },
                  {
                    "function": "minecraft:set_contents",
                    "entries": [
                      {
                        "type": "minecraft:dynamic",
                        "name": "minecraft:contents"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
  ```

  </details>

- `@function_tag minecraft:tick`

  <details>

  ```json
  {
    "values": [
      "isolated:thing"
    ]
  }
  ```

  </details>

### isolated

- `@function isolated:thing`

  <details>

  ```mcfunction
  say this is not affected
  ```

  </details>

## Resource pack

- `@resource_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 7,
      "description": ""
    }
  }
  ```

  </details>

- `@resource_pack pack.png`

  <details>

  ![resource_pack.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAMAAABOo35HAAAAk1BMVEUAAAAiQGUoUYY1KBU6RRA/MRtAHAZENR1NPCJNXQtRIQRTQSVUQSRcRyhgdA5hJwZjTCtlTzBmTyxnUC1tVjNvVjFwWjt2YUJ3Dg53XTV7XzZ8Ghp8YTd+HR2IakCUZCiUckGUc0KWeU6YIyOaEhKeglekgEyonCKyi0+1kl6+nWm/mWOsh1CceES8klSDZjnIpW+rp5F9AAAAAXRSTlMAQObYZgAAETlJREFUeF7s0EEKgDAMRFEPlKS9/+lUkIokwNCd5P/1MMA7fhBF6FusQufCSufCSufCSufCSufCSufCSuSiOafOhZXOhZXOhdUGF1ZjDJ0LK50LK50Lqw0urNw9qsyKE6xKLjPLXFiVXPbU3cqTVeayt95WV8vqW2VlEa2tFpenCqu7vlaLy6uyVSuukxw7vI0YhmEoPFBYtvtPVyLAwclRrnJGgMbW28DfL1ok3UptX3FmVYiLe4GVyrh4DFWslFulXDYmqlgps0q4zEqVtlLscEVWqraVSrlwrLRVzoW36lrlXPCqWJF0K7X1uBBWxUq5VTIkPFaxUm71GRdVCSsv3V2RlapiBcCsLnM15ipWyqyucfFYFSvlVjkX31pxX0VWyqQyLnorblGzGuFi2Iq7vVllXMknyFvOSpGICqwW58qtFDqZ1QBXFStlVgNcVaxUsxrmQhUr1awGuQAsaPXT46Ia5sLeclYKcRznwqvVrD7jknXOhUNLWSVcbpVz4dw6VimXWaVcsJaz6u+Jk1XOhajlrFKuqxeJCbiA2AoXrVIu+YxzkXyUlYqs1BWrlEs441zce5SViqzUdav+kNjGuZ71Z0QrslJnK/xhdT8XDz3KCmZlJVa3c/HczFYwq5u5aM1rpczqTi5GzWulmtUo1xznQZKhVXcExBrNaohrjmsq9yIr1XlnSCGsca45js98FVmpziMDq4Z48c9oVgNcT/sPdl4YWKnIKufiod6Q+P53rl/u7SjFcRgIg/C8D4ERJM4hMnH2/qfbAowbk9LSRpaSbB3h439pGSesbm5FvhKzqnOJFZkVmdU0fbAVLPtuRrEisyKxmj7aivbdjGJFZkVPVtOoG6eTFe27GcWKxIr+bK1ojBV1sqJ9N6NYkVnR1moaZUXNVli74b6bEStJrFau07Q0zIqarShrRZB6N82saLWiYVZ0gBXlrSjPxbbEisJqemer2awob5XnworCKgqry+WNrWiP1SxWaa770j+tLm9tRXkrqjyqutYsVlS3ovFvMvOct6K8FZkVmRWFVVS3op5WZFaUt6K8FZkVmRXtsaLRbzKbi6PFChi3NSsyK9phRS/7b6LZisRq+74TqRXlrWi0VdRuRWJFh1qdLtEnW9VBW62u19VKsP4vK2qzWrFO1BHrd7yVg6oV0/XVb61oteo4rV8yK1TGWpFZkVnR1uq6WPWc1iJgVrTDCjll2AdqVmRWFFYUVr2mFQhmRXkrclvlAnfX4W1WtFoRVoI19ht93ooqtmZFWStyK7qunaLAGmsFoltVPilUbM2Kmq2mGNZkWGWwFZkVidXNrcisqNFqCqtJplXKcCsyK2q0ojYrWqwUq9B4KzIr6mSFRMaKFqutVliV8Vb0eLhJLytKWNFi9TwtpOg1VjTWihJWYOEk0ypLL7KisVZUt5JOEVZL462it7O6qFZZG2HFIWFW5Cbzq6wMiwZbkVmRWZFYUZtVVLEixQqrpvJWZFZkViRWZFZ0lJVPK6ya+v42q7ta0cMzK8JKMivaYQWjW1WndRAW5a2gUKz7vXLKeFhZeSsyq/q0wqpRi/JWZFbkVl5NMW9FZuVYhNVBWJS3IrOivBU1W5FYkWJhdZzWz49a3W5iRWZFeStqtKKNlWCVwPo6EgutH7MisSKz4g7KW1EXq9AqRawOmhaZFYkVmRWlraiDVWAVCqvDscisCCvJrKif1exWilWoiFUrVmhR5Y39ppkV9bIiszItpCisukyLzMrHUr8Ze1nRk5VhlaWw6jMtEivjspvRucKk2Yo2VhZWS2HVa1pkViRWZFZkVtRqRW4VlehrANb5bFYkVvTwzIqaraLRVmCp1tmsKKwyXG4y0GrMtMisKKwSXIdb/eXeXnLkhmEoig564JEAFaJ2w95CVT77X10SK9ZT50kg6Qxi8i7hQK4SBfD/WKGcO62l0yrfxsFKwRXFCloZR2tZgLVtE64fFq4IVuhAAtZvrlLbTFx1COK+hrACFlqO2tEycGFm5EecIFbQ+vMlLjVoKblOA7KqBbACVvvhWs6AtRWZ64nIqiZa1W5uhaN1cC2tpjX/ZxzvKPVW6HsEKxyto6WrYQlcNAgNrOjehTxZAYu5oDXlIqsjtuJ7F/Jjhe9wxlVq24Srt0JshXsX58SKjxZzSfcuWPXBiu9dnAsr1mIu+d4FqwEX3btGObAC1phLf++CVR9Z1TxaAUvkApZxZiSrmjsrlBVc0Lo8M34icWVl5wLWtZnxb5LJqsI9rexcwDLOjGRVm6wq3NrKzmWfGcmqRlY1u9WtuewzI1vxyh4yWt2eyzwzylbow2R1Y67rM6PeClgpiVYOuC7NjFqrfrtEsnLAdW1mfL2UVv3akmDlgqvULDPjYTF5v4LVEaySYOWCyz4znhwjq8bFm5aClSuurTbR6q0QWTWu0QrvP1h5mhk/fYeaefADpdZ1K08z47Omt1phtSZ01crTzPhsaa265XDCIqtQXM8+lRWwaCeVrWJwWaxe9H7VXRwQrIAVhUtv9SveDeflcFgBKw6X2qpxrbwcnhCsgBWHq+isGtcKrLXFu+HACsVVimyF1mEJecOyv3ddsXp/D4Jlf++yW/VYq4AVgwta2WwlHC1gReIqtZwtVsImfQJWMK4TK2eLFWNBK3nE2r9ouAq0ssFq/h0mn1i7gSvXtFbz7zB5xTJwNVLZirUeCbnFsnCBVLTi3fBHFKz9bddw5S7RqgarQFhvdi7RClqPYFh6LoAOrH6Sb8esDcQwGIaHLs3gXN1iCLcEw0Fy/v8/sP2Iic4SQhEdarvvJKTtwau1v+FoHiw/F/aGFYLVbFg+LjpbVglWpBWnwHJxNcfX/wJAaGCsTFgeruZmWlESK42ElTNhObgYlmGlYqU0FBYSWDZXszesVKyUhsNCwHJxNWuPFWGlNChWvrw5uZqlbSWx0sBYFydXs9OspsXycjUbxWpaLD+XgRWnxkKLl0vFiv8Aa3Fy1UFaTYi1CiwPFyWspsRaV4bl5aozs5oTCzEsH1edmdWsWIhhubgeM7OaFgvdCMvLVWdmZWHFkbFuN8JycjGsEGysGIfGQsBinU0u/rSCjYVhQKz7AQtJrPMLXIQFK0MLxyPWPgrVnbBqV4GlcH198KqVgZUix9r3EaiQwLpeGZbCta6CC1YGVkoSC/VPhTLHQhwLSSzBBauaRqVg9c2132s5Z46FJNbpxLEkV3imUGlYqPRKhSoW4lhIYrVcay3YWGSjYxXUKxWqWIiwKI6FJFYIQWIpVCpWQahHKuLKtY2wKI6FBBZiWgqVhlVQh1xlZz2xto2wqJew0BFLoVKwCq8XKqRgIWCxbKza+1NLUnleFuqFCilY6BdY7+GBxalsrP64yjEVa1vcWMd+sASVjdUb12dhqVjL4scCUagpVBaW5Nr/iOqbWDtabRwGojBMSwnE0BsDYdkWSA0WUd7/AVcHBU59JjvyyMT+b3xj0PAhg7E8opU7C8WwAEQsWoSwbiUz4VFUiFQuFgpggWcr1u2RmXB/KkYqDwsNa7EAswkLVMxMuD8Vy8zHGoadsG5S1nZ8W3e57ndAoT+KhV6J9cmX0mO5SOVy3Uu/TqQVC1ms9/fNWJWWWMdzZeRx3RGxkGAhi1XahgUqwTqWK0ujBijBQmuw0AYsUAnWoVxmrZTSqFksNLSxakEstVIspFZ7cJnlEnrOZbGGYR3Wz08PFlQNFhMq24uoEKn+y/VXsdAqrFIUi6qCxUj1eq6bVKkcLv2LZqhZrI8PxUIWy6NysBipXssFeeVaWOWcFQsJFjoZrJJiIcVqUFms72/lyjtwZeRx5ZpiIYt1OikWamO5VM+x9ufKyOPKTLDQrFhIsVALy6VCtCLWvlwZeVxyg8WaZ8VCQSzuK6VipCLWnlxjyeXKNsVCgoXOESxcDZVWqQxWmcXlqs8Gu5Y6qVyu/DzFQhbrfF6LVa9CZQOVwRqRw5VqpHrUQeVyZaYpFlIs5GJJLhUx2YPK40rsQcWCVC5X9iMWUyzUwiJMiApVKocrLSNVlGsatRwIcxCLKRbysH7TBKnw7W9scCVpaXVZjzVt4Eo1YrEI1hInTIX6uS6XCFY3V2LAkqa1WLqTwlT9XKCKYXVyydoWa5r6sKJU/VygimPFuZL29aVYqAerTcVDnQhX2UdpEZyiWA5XgAopFrJYb28O1noqFOC61oQqjOVxRaiQYKHZYJXaWG2qCNeVkaoXy+dqUzGLNc+KhSxWjCrC9Y9VO1xxEAaiKPw3QANIoUA3FWmhdN//BTcS7DA57rV2PA+g8AFyjU6+RhXAElya6vH46QJWDVg1haXHgn7pXzmh9FjDJYaluQRVjVzAqhHrehVYciwormdNcg3D91inOyOXoFrlAlYNWDVibVMpLnH+vVARK32OdfqMS1CtchmWBawasTSV4nr6yDW0PFXag/URVymFVJrLsCxg1QxLU5XSP5v0osGQeN/BUe3E2uYqLVJpLsOyFJammvPPJsWFIWF3GBzVbizNVSxSaS7DsgSWpGoZleJ6WQsVsXL6AktzFR+pNBex7neBJalajUpxvXwzFbFy/gZLc43FB51NLmDV1rD+naDFN03EkjMVh4mNKoLVItY4girG1a5LLLHWHdWcp2KOilg5h7AsYNVAFeFartxjyRcbRzVnVJJLfP4PY5FrbBlVmItYmsq4JheoyKV+KyFWnGtcMocA1x4srM6p71cH/EZlGVWMi1i3W5hLY3Gth7guF2Jln1FFuYh1AJfAAtUuLlIRK+UuUAW4gHUEl8AC1Q4uUAErJWABIcQFrCO4trD6mfTc4CoFVMRKc5oqzgWsI7gUVj+TVheCo5pzVMRKLVAdzXUG1jFc61g2k4xKcZV3RgWstASqaMA6n4F1DBexHMdCJbiKq1EBK1mgitdj1YgV55p6rNJz/FFrxzoSwjAURVNuk2aKrbwoVcT/f+GQEZY9z4DlDUTK7Sg5hQmGCqEWQb8QUwFWujfAagFWN1dpaSxqBbhKC6ggoVJY6f4UFidI/VyFYyxqBbgKJ1S2H4ypbs/B6uEquoZFrQBX0Z1R5Wyw0nMZrHu4aoEI8rgKdkxlsNKzGax+LnO761aEq2A5H1IhVno+wOrlqpyminBZqi1LZbDSmACrh6vqmCrCZak+IZXBSuMSrC6uiq0QQS/UMlR7QIVYaWyM5RSiagC4XCAV/pNiBpbAIBXHVKNjLKcQlebia6HawwkvVBYrQ0w1PsZyClAJl74WKuGqOqZCrGwSqvH9/Y+LDJXTC6sQziemghI3DRe1rqiAz+eyE8qhmoWLuCuqEJdQAZGlmouLdGdUIa7jc7pDNQNX9JXP5zp7/3OoZuBaFsJzUxfX+V7BUM3HtWx9UXVxXe2rgGpGruWTUHVwnVBxQDUj17K3U3VweVtQoJqJC7HgV15v1JuP0P7CWKgm5EIsxeU9Gdc9jwqx3u3bMY7EIAxGYTeWKOjQ+Axz/xOuFHlDdt4ODmUM7whfgf7CyDO6heVc0ZB4XxpQAUueU4jlXNHuen8UUnnyrCIsD7tryPVKQsUiLC/cXdez2TxUMVdrHasX7q5+NpuIigGrtY7VC3fX79lsXipytSNghd8/7eXlpSJX82A15DIDVhoqBqxa73OZEUuVVHkC1l0uM2KpAktyBaw7XGbEUgWW5AtYEZcZsdQDVbqAVQdPvRmxigJL8gas9oXLjFilAEtyB6x/uYxYpQBL8gcschGrFGDJGgGr1TGWFmDJOgGr1u9YqsCStQKWcwFLFViyXsCqlViqwJI1A9bJdVIBS9YNWM7lVMCStQPWwXVQAUt2Hatzmf7tpNoBq+pHF6pdhDUA2FwTVJtrgmpzTVBtrgmqzTVBtbkmqDbX46l2P2oqW1bzOq0nAAAAAElFTkSuQmCC)

  </details>

### minecraft

- `@resource_pack assets/minecraft/sounds.json`

  <details>

  ```json
  {
    "block.note_block.bit_1": {
      "sounds": [
        "block/note_block/bit_1"
      ],
      "subtitle": "subtitles.block.note_block.note"
    }
  }
  ```

  </details>
