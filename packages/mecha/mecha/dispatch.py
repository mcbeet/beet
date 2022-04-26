__all__ = [
    "Dispatcher",
    "Visitor",
    "Reducer",
    "MutatingReducer",
    "Rule",
    "rule",
    "CompilationError",
]


from contextlib import contextmanager
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
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from beet import BubbleException, WrappedException
from beet.core.utils import extra_field

from .ast import AstChildren, AstNode
from .diagnostic import Diagnostic, DiagnosticCollection

T = TypeVar("T")


class CompilationError(WrappedException):
    """Raised when an error occurs in a rule."""

    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


@dataclass
class Rule:
    """Rule that can be associated to an ast node by the dispatcher."""

    callback: Callable[..., Any]
    match_types: Tuple[Type[AstNode], ...] = ()
    match_fields: FrozenSet[Tuple[str, Any]] = frozenset()

    name: Optional[str] = None
    next: Optional["Rule"] = None

    def __post_init__(self):
        if isinstance(self.callback, Rule):
            self.next = self.callback
            self.callback = self.next.callback
        if not self.name:
            self.name = (
                self.next.name
                if self.next
                else getattr(self.callback, "__name__", None)
            )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.callback(*args, **kwargs)

    def with_callback(self, callback: Callable[..., Any]) -> "Rule":
        """Recursively update callback."""
        return replace(
            self,
            callback=callback,
            next=self.next.with_callback(callback) if self.next else None,
        )

    def bake(self, *args: Any, **kwargs: Any) -> "Rule":
        """Bake arguments."""
        return self.with_callback(partial(self.callback, *args, **kwargs))


@overload
def rule(func: Callable[..., Any]) -> Rule:
    ...


@overload
def rule(*args: Type[AstNode], **kwargs: Any) -> Callable[[Callable[..., Any]], Rule]:
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

    levels: Dict[str, Literal["ignore", "info", "warn", "error"]] = extra_field(
        default_factory=dict
    )

    rules: Dict[
        Type[Any],
        Dict[
            FrozenSet[Tuple[str, Any]],
            List[Tuple[int, Optional[str], Callable[..., Any]]],
        ],
    ] = extra_field(init=False, default_factory=dict)

    count: int = extra_field(init=False, default=0)
    diagnostics: DiagnosticCollection = extra_field(
        default_factory=DiagnosticCollection
    )

    def __post_init__(self):
        for name in dir(self):
            if isinstance(rule := getattr(self, name), Rule):
                self.add_rule(rule.bake(self))

    def add_rule(self, rule: Callable[..., Any]):
        """Add rule."""
        if not isinstance(rule, Rule):
            rule = Rule(rule)

        if rule.name and self.levels.get(rule.name) == "ignore":
            return

        for match_type in rule.match_types or [AstNode]:
            l = self.rules.setdefault(match_type, {}).setdefault(rule.match_fields, [])
            l.append((self.count, rule.name, rule.callback))
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

                        for priority, name, callback in callbacks:
                            if name and self.levels.get(name) == "ignore":
                                continue
                            priority += offset
                            l.append((priority, name, callback))
                            self.count = max(self.count, priority) + 1

            elif callable(arg):
                self.add_rule(arg)

            else:
                for rule in arg:
                    self.add_rule(rule)

    def reset(self):
        """Remove all rules."""
        self.rules.clear()
        self.count = 0

    def dispatch(
        self,
        node: AstNode,
    ) -> Iterator[Tuple[Optional[str], Callable[..., Any]]]:
        """Dispatch rules."""
        priority_queue: List[
            Tuple[int, int, int, Optional[str], Callable[..., Any]]
        ] = []

        for i, node_type in enumerate(type(node).mro()):
            if value := self.rules.get(node_type):
                for match_fields, callbacks in value.items():
                    if all(
                        node == value
                        if name == "self"
                        else hasattr(node, name) and getattr(node, name) == value
                        for name, value in match_fields
                    ):
                        for priority, name, callback in callbacks:
                            heappush(
                                priority_queue,
                                (i, -len(match_fields), -priority, name, callback),
                            )

        dispatched: Set[Callable[..., Any]] = set()

        while priority_queue:
            _, _, _, name, callback = heappop(priority_queue)

            if callback not in dispatched:
                dispatched.add(callback)
                yield name, callback

    def invoke(self, node: AstNode, *args: Any, **kwargs: Any) -> Any:
        """Invoke rules on the given ast node."""
        for name, rule in self.dispatch(node):
            with self.use_rule(node, name):
                rule(node, *args, **kwargs)
        return node

    @contextmanager
    def use_diagnostics(self, diagnostics: DiagnosticCollection) -> Iterator[None]:
        """Temporarily gather diagnostics in the specified diagnostic collection."""
        previous_diagnostics = self.diagnostics
        self.diagnostics = diagnostics

        try:
            yield
        finally:
            self.diagnostics = previous_diagnostics

    @contextmanager
    def use_rule(self, node: AstNode, name: Optional[str] = None) -> Iterator[None]:
        """Handle rule diagnostics."""
        override_level = self.levels.get(name or "")
        if override_level == "ignore":
            override_level = None

        try:
            yield
        except Diagnostic as diagnostic:
            if override_level:
                diagnostic.level = override_level
            self.diagnostics.add(
                diagnostic.with_defaults(
                    rule=name,
                    location=node.location,
                    end_location=node.end_location,
                )
            )
        except DiagnosticCollection as diagnostic:
            for diagnostic in diagnostic.exceptions:
                if override_level:
                    diagnostic.level = override_level
                self.diagnostics.add(
                    diagnostic.with_defaults(
                        rule=name,
                        location=node.location,
                        end_location=node.end_location,
                    )
                )
        except StopIteration:
            raise
        except BubbleException:
            raise
        except Exception as exc:
            msg = "Compilation raised an exception."
            if name:
                msg += f" ({name})"
            tb = exc.__traceback__ and exc.__traceback__.tb_next
            raise CompilationError(msg) from exc.with_traceback(tb)

    def __call__(self, node: AstNode) -> T:
        if not self.count:
            return node  # type: ignore
        return self.invoke(node)


class Visitor(Dispatcher[Any]):
    """Ast visitor."""

    def invoke(self, node: AstNode, *args: Any, **kwargs: Any) -> Any:
        rules = list(self.dispatch(node))

        if rules:
            name, rule = rules[0]
        else:
            name, rule = None, None

        result = None

        with self.use_rule(node, name):
            result = rule(node, *args, **kwargs) if rule else (child for child in node)

        if isinstance(result, Generator):
            try:
                with self.use_rule(node, name):
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
        return super().invoke(node, *args, **kwargs)


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
            node = replace(node, **to_replace)

        exhausted = False

        while not exhausted:
            exhausted = True

            for name, rule in self.dispatch(node):
                with self.use_rule(node, name):
                    result = rule(node, *args, **kwargs)

                if result is not node:
                    exhausted = False
                    node = result
                    break

        return node
