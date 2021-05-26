#!set message = "hello"

say __message__ but {{ message }} not_this__message__
say __here__ it should __stay__ the same

#!set falsy = 0

say __falsy__
