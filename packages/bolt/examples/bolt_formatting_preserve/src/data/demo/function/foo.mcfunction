# top level comment
say example
function ~/test:
    #inner comment
    say test

# comment before the loop

for i in range(5):
    execute if score #test test matches i run function ~/test
    execute if score #test test matches -i run function ~/test
say command
# comment after the loop
