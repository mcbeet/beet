__all__ = [
    "Dispatcher",
    "Visitor",
    "Reducer",
    "MutatingReducer",
    "Rule",
    "rule",
]


from dataclasses import dataclass, fields, replace
from functools import partial
from heapq import heappop, heappush
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from beet.core.utils import extra_field

from .ast import AstChildren, AstNode

T = TypeVar("T")


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


@dataclass
class Dispatcher(Generic[T]):
    """Ast dispatcher."""

    rules: Dict[
        Type[Any],
        Dict[
            FrozenSet[Tuple[str, Any]],
            List[Tuple[int, Callable[..., Any]]],
        ],
    ] = extra_field(init=False, default_factory=dict)

    count: int = extra_field(init=False, default=0)

    def __post_init__(self):
        for name in dir(self):
            if isinstance(rule := getattr(self, name), Rule):
                callback = partial(rule.callback, self)

                current = rule
                while current:
                    current.callback = callback
                    current = current.next

                self.add_rule(rule)

    def add_rule(self, rule: Callable[..., Any]):
        """Add rule."""
        if not isinstance(rule, Rule):
            rule = Rule(rule)

        for match_type in rule.match_types or [AstNode]:
            l = self.rules.setdefault(match_type, {}).setdefault(rule.match_fields, [])
            l.append((self.count, rule.callback))
            self.count += 1

        if rule.next:
            self.add_rule(rule.next)

    def extend(
        self,
        *args: Union[
            "Dispatcher[Any]",
            Callable[..., Any],
            Iterable[Callable[..., Any]],
        ],
    ):
        """Extend the dispatcher."""
        for arg in args:
            if isinstance(arg, Dispatcher):
                offset = self.count
                for key, value in arg.rules.items():
                    current = self.rules.setdefault(key, {})
                    for match_fields, callbacks in value.items():
                        l = current.setdefault(match_fields, [])
                        for priority, callback in callbacks:
                            priority += offset
                            l.append((priority, callback))
                            self.count = max(self.count, priority) + 1
            elif callable(arg):
                self.add_rule(arg)
            else:
                for rule in arg:
                    self.add_rule(rule)

    def dispatch(self, node: AstNode) -> Iterator[Callable[..., Any]]:
        """Dispatch rules."""
        priority_queue: List[Tuple[int, int, Callable[..., Any]]] = []

        for i, node_type in enumerate(type(node).mro()):
            if value := self.rules.get(node_type):
                for match_fields, callbacks in value.items():
                    if all(
                        node == value
                        if name == "self"
                        else hasattr(node, name) and getattr(node, name) == value
                        for name, value in match_fields
                    ):
                        for priority, callback in callbacks:
                            heappush(priority_queue, (i, -priority, callback))

        dispatched: Set[Callable[..., Any]] = set()

        while priority_queue:
            _, _, callback = heappop(priority_queue)

            if callback not in dispatched:
                dispatched.add(callback)
                yield callback

    def invoke(self, node: AstNode, *args: Any, **kwargs: Any) -> Any:
        """Invoke rules on the given ast node."""
        for rule in self.dispatch(node):
            rule(node, *args, **kwargs)
        return node

    def __call__(self, node: AstNode) -> T:
        return self.invoke(node)


class Visitor(Dispatcher[Any]):
    """Ast visitor."""

    def invoke(self, node: AstNode, *args: Any, **kwargs: Any) -> Any:
        rules = list(self.dispatch(node))

        if rules:
            result = rules[0](node, *args, **kwargs)
        else:
            result = (child for child in node)

        if isinstance(result, Generator):
            try:
                child = next(result)
            except StopIteration as exc:
                return exc.value

            while True:
                feedback = self.invoke(child, *args, **kwargs)
                try:
                    child = result.send(feedback)
                except StopIteration as exc:
                    return exc.value

        return result


class Reducer(Dispatcher[Any]):
    """Ast reducer."""

    def invoke(self, node: AstNode, *args: Any, **kwargs: Any) -> Any:
        for child in node:
            self.invoke(child, *args, **kwargs)

        for rule in self.dispatch(node):
            rule(node, *args, **kwargs)

        return node


class MutatingReducer(Dispatcher[Any]):
    """Mutating ast reducer."""

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
