# Importing multiple macros in a row will update the command tree in a single batch

from ./lib import foo1, foo2
from ./lib import foo3

foo1
foo2
foo3
