"""Plugin that sandboxes the bolt runtime."""

__all__ = [
    "Sandbox",
    "SandboxedAttributeHandler",
    "SandboxedImportModule",
    "SecurityError",
    "public_attrs",
]


import bisect
import collections
import copy
import heapq
import itertools
import json
import math
import random
from collections import defaultdict, deque
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Callable, DefaultDict, Set, Type, Union, get_type_hints

from beet import Context, TreeData, TreeNode
from mecha import MechaError

from bolt import LoopInfo, Runtime
from bolt.utils import internal


class SecurityError(MechaError):
    """Raised when the sandboxed runtime attempts to perform a forbidden operation."""


def beet_default(ctx: Context):
    ctx.require("beet.contrib.template_sandbox")
    sandbox = ctx.inject(Sandbox)
    sandbox.allow_basics()
    sandbox.allow_pipeline_context()
    sandbox.activate()


def public_attrs(obj: Any) -> Set[str]:
    """List public object attributes."""
    attrs = dir(obj)
    obj_type = obj if isinstance(obj, type) else type(obj)
    if is_dataclass(obj_type):
        attrs.extend(f.name for f in fields(obj_type))
    else:
        attrs.extend(k for t in type.mro(obj_type) for k in get_type_hints(t))
    return {name for name in attrs if not name.startswith("_")}


class Sandbox:
    """Bolt sandbox."""

    runtime: Runtime
    active: bool

    allowed_builtins: Set[str]
    allowed_imports: Set[str]
    allowed_obj_attrs: DefaultDict[Any, Set[str]]
    allowed_type_attrs: DefaultDict[Type[Any], Set[str]]

    def __init__(self, ctx: Union[Context, Runtime]):
        if isinstance(ctx, Context):
            self.runtime = ctx.inject(Runtime)
        else:
            self.runtime = ctx

        self.active = False

        self.allowed_builtins = set()
        self.allowed_imports = set()
        self.allowed_obj_attrs = defaultdict(set)
        self.allowed_type_attrs = defaultdict(set)

    def allow_basics(self):
        self.allowed_builtins |= {
            "abs",
            "all",
            "any",
            "ascii",
            "bin",
            "bool",
            "callable",
            "chr",
            "dict",
            "divmod",
            "enumerate",
            "filter",
            "float",
            "frozenset",
            "hasattr",
            "hash",
            "hex",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "map",
            "max",
            "min",
            "next",
            "object",
            "oct",
            "ord",
            "pow",
            "print",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "slice",
            "sorted",
            "str",
            "sum",
            "tuple",
            "type",
            "zip",
        }

        self.allowed_imports |= {
            "json",
            "math",
            "collections",
            "itertools",
            "bisect",
            "heapq",
            "copy",
            "random",
        }

        self.allowed_obj_attrs |= {
            dict: {"fromkeys"},
            defaultdict: {"fromkeys"},
            json: {"loads", "dumps"},
            math: public_attrs(math),
            collections: {"deque", "defaultdict"},
            itertools: public_attrs(itertools),
            bisect: public_attrs(bisect),
            heapq: public_attrs(heapq),
            copy: {"copy", "deepcopy"},
            random: public_attrs(random),
        }

        self.allowed_type_attrs |= {
            str: public_attrs(str)
            ^ {
                "maketrans",
                "translate",
                "encode",
                "format",
                "format_map",
            },
            tuple: public_attrs(tuple),
            list: public_attrs(list),
            dict: public_attrs(dict),
            set: public_attrs(set),
            TreeNode: public_attrs(TreeNode),
            TreeData: public_attrs(TreeData),
            LoopInfo: public_attrs(LoopInfo),
            deque: public_attrs(deque),
            defaultdict: public_attrs(defaultdict),
        }

    def allow_pipeline_context(self):
        self.allowed_type_attrs[Context] |= {
            "project_id",
            "project_name",
            "project_description",
            "project_author",
            "project_version",
            "project_root",
            "minecraft_version",
        }

    def activate(self):
        """Activate the sandbox."""
        if self.active:
            return
        self.active = True

        self.runtime.builtins &= self.allowed_builtins

        get_attribute_handler = self.runtime.helpers["get_attribute_handler"]

        self.runtime.helpers.update(
            get_attribute_handler=lambda obj: SandboxedAttributeHandler(
                obj=obj,
                handler=get_attribute_handler(obj),
                sandbox=self,
            ),
            import_module=SandboxedImportModule(
                sandbox=self,
                import_module=self.runtime.helpers["import_module"],
            ),
        )


@dataclass
class SandboxedAttributeHandler:
    """Sandboxed attribute handler helper."""

    obj: Any
    handler: Any
    sandbox: Sandbox

    @internal
    def __getitem__(self, attr: str) -> Any:
        if not hasattr(self.obj, attr):
            return self.handler[attr]

        try:
            if allowed := self.sandbox.allowed_obj_attrs.get(self.obj):
                if attr in allowed:
                    return self.handler[attr]
        except TypeError:
            pass

        for cls in type.mro(type(self.obj)):
            if allowed := self.sandbox.allowed_type_attrs.get(cls):
                if attr in allowed:
                    return self.handler[attr]

        raise SecurityError(f"Access forbidden attribute {attr!r} of {type(self.obj)}.")


@dataclass
class SandboxedImportModule:
    """Sandboxed import_module helper."""

    sandbox: Sandbox
    import_module: Callable[[str], Any]

    @internal
    def __call__(self, name: str) -> Any:
        if name in self.sandbox.allowed_imports:
            return self.import_module(name)
        raise SecurityError(f"Access forbidden module {name!r}.")
