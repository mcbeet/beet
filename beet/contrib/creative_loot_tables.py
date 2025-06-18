"""Plugin that automates the creation of the creative loot table"""
# IMPORTANT : this plugin is meant to be used with the mod https://modrinth.com/mod/creative-loot-tables
# USAGE: in your beet.json file, specify a regex at meta.creative_loot_tables.pattern
# any loot table with an ID matching with this regex will be put in the creative loot table.

from beet import Context, LootTable
from re import Pattern
import re

def beet_default(ctx: Context) -> None:
    
    # get the pattern
    meta: dict = ctx.meta
    pattern: str = meta.get("creative_loot_tables", {}).get("pattern")
    if pattern is None:
        return
    regex: Pattern = re.compile(pattern)
   
    # search
    loot_tables: list[str] = [id for id in ctx.data.loot_tables if regex.match(id)]

    # no match found
    if len(loot_tables) == 0:
        return
    
    # output the loot table
    creative_loot_table: dict = {
        "pools": [{"rolls": 1, "entries": [{"type": "loot_table", "value": loot_table}] } for loot_table in loot_tables]
    }
    ctx.generate("creative_loot_tables:creative_loot_table", LootTable(creative_loot_table))