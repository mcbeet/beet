execute 
    if 
    entity @
    run tp ~ ~ ~

execute unless block ~ ~ ~ stone
    if block ~ ~1 ~ air
    run invalid

execute if predicate foo:bar run say valid

summon ~ ~ ~ {}
data modify storage foo:bar baz set {}
