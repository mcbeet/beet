function ~/
function ~/thing
function ~/../thing

function demo:bar:
    function ~/
    function ~/thing
    function ~/../thing

    append function ~/thing:
        function #~/aaa

function ./wat:
    function ~/
    function ~/thing
    function ~/../thing

    append function ~/thing:
        function #~/bbb

function ~/this:
    function ~/
    function ~/thing
    function ~/../thing

    append function ~/thing:
        function #~/ccc

function ~/../upthis:
    function ~/
    function ~/thing
    function ~/../thing

    append function ~/thing:
        function #~/ddd
