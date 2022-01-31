mykey1 = "foo"

if data storage some:path/to/storage f"some.{mykey1}.path"
if data storage some:path/to/storage f"some.{mykey1}.path" run say hi
if data storage some:path/to/storage f'some.{mykey1}.path{{my: "compound"}}'
if data storage some:path/to/storage f'some.{mykey1}.path{{my: "compound"}}' run say hi

mykey2 = "bar"

mypath1 = f"some.{mykey2}.path"
if data storage some:path/to/storage (mypath1)
if data storage some:path/to/storage (mypath1) run say hi

mypath2 = f'some.{mykey2}.path{{my: "compound"}}'
if data storage some:path/to/storage (mypath2)
if data storage some:path/to/storage (mypath2) run say hi

myindex = 42

if data storage some:path/to/storage f'some.{mykey1}.path{{my: "compound"}}.stuff[{myindex}].beep.{mykey2}.boop' run say hi
