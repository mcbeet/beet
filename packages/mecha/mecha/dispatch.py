__all__ = [
    "Visitor",
    "Reducer",
    "Dispatcher",
    "Rule",
    "rule",
]


from dataclasses import dataclass, fields, replace
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    overload,
)

from .ast import AstChildren, AstNode


@dataclass
class Rule:
    """Rule that can be associated to an ast node by the dispatcher."""

    callback: Callable[..., Any]
    match_types: Tuple[Type[AstNode], ...] = ()
    match_fields: FrozenSet[Tuple[str, Any]] = frozenset()

    next: Optional["Rule"] = None

    def __post_init__(self):
        if isinstance(self.callback, Rule):
            self.next = self.callback
            self.callback = self.next.callback

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.callback(*args, **kwargs)


@overload
def rule(func: Callable[..., Any]) -> Rule:
    ...


@overload
def rule(
    *args: Type[AstNode],
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Rule]:
    ...


def rule(*args: Any, **kwargs: Any) -> Any:
    """Decorator for defining rules."""
    match_types = ()
    match_fields = frozenset(kwargs.items())

    if args and isinstance(args[0], type) and issubclass(args[0], AstNode):
        match_types = args

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return Rule(func, match_types, match_fields)

    if len(args) == 1 and not match_types:
        return decorator(args[0])

    return decorator


# TODO: Use dataclass?
class Dispatcher:
    """Ast node dispatcher."""

    rules: Dict[Type[Any], Dict[FrozenSet[Tuple[str, Any]], List[Callable[..., Any]]]]

    def __init__(self, rules: Iterable[Callable[..., Any]] = ()):
        self.rules = {}

        for name in dir(self):
            if isinstance(rule := getattr(self, name), Rule):
                callback = partial(rule.callback, self)

                current = rule
                while current:
                    current.callback = callback
                    current = current.next

                self.add_rule(rule)

        self.extend(rules)

    def add_rule(self, rule: Callable[..., Any]):
        """Add rule."""
        # TODO: Add rule priority that increases as rules are added
        if not isinstance(rule, Rule):
            rule = Rule(rule)

        for match_type in rule.match_types or [AstNode]:
            l = self.rules.setdefault(match_type, {}).setdefault(rule.match_fields, [])
            l.append(rule.callback)

        if rule.next:
            self.add_rule(rule.next)

    def extend(
        self,
        *args: Union["Dispatcher", Callable[..., Any], Iterable[Callable[..., Any]]],
    ):
        """Extend the dispatcher."""
        for arg in args:
            if isinstance(arg, Dispatcher):
                for key, value in arg.rules.items():
                    current = self.rules.setdefault(key, {})
                    for match_fields, callbacks in value.items():
                        current.setdefault(match_fields, []).extend(callbacks)
            elif callable(arg):
                self.add_rule(arg)
            else:
                for rule in arg:
                    self.add_rule(rule)

    def dispatch(self, node: AstNode) -> Iterator[Callable[..., Any]]:
        """Dispatch rules."""
        # TODO: Sort rules by priority
        dispatched: Set[Callable[..., Any]] = set()

        for node_type in type(node).mro():
            if value := self.rules.get(node_type):
                for match_fields, callbacks in value.items():
                    if all(
                        node == value
                        if name == "self"
                        else hasattr(node, name) and getattr(node, name) == value
                        for name, value in match_fields
                    ):
                        for callback in callbacks:
                            if callback not in dispatched:
                                dispatched.add(callback)
                                yield callback

    def invoke(self, node: AstNode, *args: Any, **kwargs: Any) -> Any:
        """Invoke rules on the given ast node."""
        for rule in self.dispatch(node):
            rule(node, *args, **kwargs)
        return node


class Visitor(Dispatcher):
    """Ast node visitor."""

    def invoke(self, node: AstNode, *args: Any, **kwargs: Any) -> Any:
        rules = list(self.dispatch(node))

        # TODO: If no rules use default implementation that joins all child nodes with space
        # TODO: If more than one rule, just use the first one with the highest priority
        if not rules:
            raise ValueError(f"No matching rule for visiting {type(node)} node.")
        if len(rules) > 1:
            raise ValueError(
                f"Matched {len(rules)} conflicting rules for visiting {type(node)} node."
            )

        if isinstance(result := rules[0](node, *args, **kwargs), Generator):
            for child in result:
                self.invoke(child, *args, **kwargs)

            # TODO: Find why this doesn't work
            # child = next(result)
            # while True:
            #     try:
            #         child = result.send(self.invoke(child, *args, **kwargs))
            #     except StopIteration as exc:
            #         return exc.value

        return result


class Reducer(Dispatcher):
    """Ast node reducer."""

    def invoke(self, node: AstNode, *args: Any, **kwargs: Any) -> Any:
        to_replace: Dict[str, Union[AstNode, AstChildren[AstNode]]] = {}

        for f in fields(node):
            attribute = getattr(node, f.name)
            if isinstance(attribute, AstChildren):
                result = AstChildren(self.invoke(child, *args, **kwargs) for child in attribute)  # type: ignore
                if any(child is not original for child, original in zip(result, attribute)):  # type: ignore
                    to_replace[f.name] = result
            elif isinstance(attribute, AstNode):
                result = self.invoke(attribute, *args, **kwargs)
                if result is not attribute:
                    to_replace[f.name] = result

        if to_replace:
            print("replacing", list(to_replace))
            node = replace(node, **to_replace)

        for rule in self.dispatch(node):
            node = rule(node, *args, **kwargs)

        return node
