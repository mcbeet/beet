"""Plugin that sandboxes the bolt runtime."""


__all__ = [
    "Sandbox",
    "SandboxedGetAttribute",
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
from typing import Any, Callable, Dict, Set, Type, Union

from beet import Context, TreeData, TreeNode
from mecha import MechaError

from bolt import LoopInfo, Runtime
from bolt.utils import internal


class SecurityError(MechaError):
    """Raised when the sandboxed runtime attempts to perform a forbidden operation."""


def beet_default(ctx: Context):
    ctx.inject(Sandbox).activate()


def public_attrs(obj: Any) -> Set[str]:
    """List public object attributes."""
    attrs = dir(obj)
    if is_dataclass(obj):
        attrs.extend(f.name for f in fields(obj))
    return {name for name in attrs if not name.startswith("_")}


class Sandbox:
    """Bolt sandbox."""

    runtime: Runtime
    active: bool

    allowed_builtins: Set[str]
    allowed_imports: Set[str]
    allowed_obj_attrs: Dict[Any, Set[str]]
    allowed_type_attrs: Dict[Type[Any], Set[str]]

    def __init__(self, ctx: Union[Context, Runtime]):
        if isinstance(ctx, Context):
            self.runtime = ctx.inject(Runtime)
        else:
            self.runtime = ctx

        self.active = False

        self.allowed_builtins = {
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
        self.allowed_imports = {
            "json",
            "math",
            "collections",
            "itertools",
            "bisect",
            "heapq",
            "copy",
            "random",
        }
        self.allowed_obj_attrs = {
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
        self.allowed_type_attrs = {
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

    def activate(self):
        """Activate the sandbox."""
        if self.active:
            return
        self.active = True
        self.runtime.builtins &= self.allowed_builtins
        self.runtime.globals["ctx"] = None
        self.runtime.helpers.update(
            get_attribute=SandboxedGetAttribute(
                sandbox=self,
                get_attribute=self.runtime.helpers["get_attribute"],
            ),
            import_module=SandboxedImportModule(
                sandbox=self,
                import_module=self.runtime.helpers["import_module"],
            ),
        )


@dataclass
class SandboxedGetAttribute:
    """Sandboxed get_attribute helper."""

    sandbox: Sandbox
    get_attribute: Callable[[Any, str], Any]

    @internal
    def __call__(self, obj: Any, attr: str) -> Any:
        if not hasattr(obj, attr):
            return self.get_attribute(obj, attr)

        try:
            if allowed := self.sandbox.allowed_obj_attrs.get(obj):
                if attr in allowed:
                    return self.get_attribute(obj, attr)
        except TypeError:
            pass

        for cls in type.mro(type(obj)):
            if allowed := self.sandbox.allowed_type_attrs.get(cls):
                if attr in allowed:
                    return self.get_attribute(obj, attr)

        raise SecurityError(f"Access forbidden attribute {attr!r} of {type(obj)}.")


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
