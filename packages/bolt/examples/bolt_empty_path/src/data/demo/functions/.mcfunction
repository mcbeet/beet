

# defining a function inline to run it
execute run function ./bar:
    say fooo

# just defining a function
function ./foo:
    say barr

# calling an empty function
function dm:

# next command
say YOLO

# defining a function
function namespace:error:
    say error
    execute run function ~/nested:
        say from nested 1
        execute run function ~/nested:
            say from nested 2


#defining an empty function
function namespace::
    say hello from empty function
    execute run function ~/nested:
        say from nested 1
        execute run function ~/nested:
            say from nested 2


function namespace:defining/:
    say weird syntax but it work
    execute run function ~/nested:
        say from nested 1
        execute run function ~/nested:
            say from nested 2


function dm::
    say definig this function referenced

    execute run function ~/nested:
        say from nested 1
        execute run function ~/nested:
            say from nested 2



#calling an empty tag
function #name:




#calling an empty tag
function #name:name/



