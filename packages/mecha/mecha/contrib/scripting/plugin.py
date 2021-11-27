__all__ = [
    "beet_default",
]


from beet import Context

from mecha import Mecha

from .parse import get_scripting_parsers

COMMAND_TREE = {
    "type": "root",
    "children": {
        "statement": {
            "type": "argument",
            "parser": "mecha:scripting:statement",
            "executable": True,
        },
        "if": {
            "type": "literal",
            "children": {
                "condition": {
                    "type": "argument",
                    "parser": "mecha:scripting:expression",
                    "children": {
                        "body": {
                            "type": "argument",
                            "parser": "mecha:nested_root",
                            "executable": True,
                        }
                    },
                }
            },
        },
        "elif": {
            "type": "literal",
            "children": {
                "condition": {
                    "type": "argument",
                    "parser": "mecha:scripting:expression",
                    "children": {
                        "body": {
                            "type": "argument",
                            "parser": "mecha:nested_root",
                            "executable": True,
                        }
                    },
                }
            },
        },
        "else": {
            "type": "literal",
            "children": {
                "body": {
                    "type": "argument",
                    "parser": "mecha:nested_root",
                    "executable": True,
                }
            },
        },
        "while": {
            "type": "literal",
            "children": {
                "condition": {
                    "type": "argument",
                    "parser": "mecha:scripting:expression",
                    "children": {
                        "body": {
                            "type": "argument",
                            "parser": "mecha:nested_root",
                            "executable": True,
                        }
                    },
                }
            },
        },
        "for": {
            "type": "literal",
            "children": {
                "target": {
                    "type": "argument",
                    "parser": "mecha:scripting:assignment_target",
                    "children": {
                        "in": {
                            "type": "literal",
                            "children": {
                                "iterable": {
                                    "type": "argument",
                                    "parser": "mecha:scripting:expression",
                                    "children": {
                                        "body": {
                                            "type": "argument",
                                            "parser": "mecha:nested_root",
                                            "executable": True,
                                        }
                                    },
                                }
                            },
                        }
                    },
                }
            },
        },
        "break": {
            "type": "literal",
            "executable": True,
        },
        "continue": {
            "type": "literal",
            "executable": True,
        },
    },
}


def beet_default(ctx: Context):
    ctx.require(
        "mecha.contrib.relative_location",
        "mecha.contrib.implicit_execute",
        "mecha.contrib.nesting",
    )

    mc = ctx.inject(Mecha)

    mc.spec.add_commands(COMMAND_TREE)
    mc.spec.parsers.update(get_scripting_parsers(mc.spec.parsers))
