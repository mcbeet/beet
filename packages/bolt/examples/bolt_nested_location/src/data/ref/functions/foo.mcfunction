x = ""

function ~/{x}
function ~/thing{x}
function ~/../thing{x}

function ref:bar:
    function ~/{x}
    function ~/thing{x}
    function ~/../thing{x}

    append function ~/thing{x}:
        function #~/aaa{x}

function ./wat:
    function ~/{x}
    function ~/thing{x}
    function ~/../thing{x}

    append function ~/thing{x}:
        function #~/bbb{x}

function ~/this{x}:
    function ~/{x}
    function ~/thing{x}
    function ~/../thing{x}

    append function ~/thing{x}:
        function #~/ccc{x}

function ~/../upthis{x}:
    function ~/{x}
    function ~/thing{x}
    function ~/../thing{x}

    append function ~/thing{x}:
        function #~/ddd{x}

execute if function ~/condition{x} run function ~/action{x}
