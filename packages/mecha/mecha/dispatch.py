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

from .ast import AbstractChildren, AbstractNode
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
    match_types: Tuple[Type[AbstractNode], ...] = ()
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
def rule(
    *args: Type[AbstractNode], **kwargs: Any
) -> Callable[[Callable[..., Any]], Rule]:
    ...


def rule(*args: Any, **kwargs: Any) -> Any:
    """Decorator for defining rules."""
    match_types = ()
    match_fields = frozenset(kwargs.items())

    if args and isinstance(args[0], type) and issubclass(args[0], AbstractNode):
        match_types = args

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return Rule(func, match_types, match_fields)

    if len(args) == 1 and not match_types:
        return decorator(args[0])

    return decorator


@dataclass(eq=False)
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

    stack: List[AbstractNode] = extra_field(default_factory=list)

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

        for match_type in rule.match_types or [AbstractNode]:
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
        node: AbstractNode,
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

    def invoke(self, node: AbstractNode, *args: Any, **kwargs: Any) -> Any:
        """Invoke rules on the given ast node."""
        for name, rule in self.dispatch(node):
            self.process(node, name, rule, *args, **kwargs)
        return node

    def process(
        self,
        node: AbstractNode,
        name: Optional[str] = None,
        rule: Optional[Callable[..., Any]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Process the given ast node."""
        result = None

        with self.use_rule(node, name):
            result = rule(node, *args, **kwargs) if rule else (child for child in node)

        if isinstance(result, Generator):
            try:
                with self.use_rule(node, name):
                    child = next(result)

            except StopIteration as exc:
                result = exc.value

            else:
                while True:
                    child = self.handle_output(node, child, name)

                    feedback = None
                    if isinstance(child, AbstractNode):
                        feedback = self.invoke(child, *args, **kwargs)
                    elif child is not None:
                        msg = f"Invalid node of type {type(child)}."
                        if name:
                            msg += f" ({name})"
                        raise CompilationError(msg)

                    try:
                        child = result.send(feedback)
                    except StopIteration as exc:
                        result = exc.value
                        break

        return self.handle_output(node, result, name)

    def handle_output(
        self,
        node: AbstractNode,
        output: Any,
        name: Optional[str] = None,
    ) -> Any:
        """Handle rule output."""
        if isinstance(output, Diagnostic):
            override_level = self.levels.get(name or "")
            if override_level == "ignore":
                override_level = None
            if override_level:
                output.level = override_level
            self.diagnostics.add(
                output.with_defaults(
                    rule=name,
                    location=node.location,
                    end_location=node.end_location,
                )
            )
            return None

        if isinstance(output, DiagnosticCollection):
            for diagnostic in output.exceptions:
                self.handle_output(node, diagnostic, name)
            return None

        return output

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
    def use_rule(
        self, node: AbstractNode, name: Optional[str] = None
    ) -> Iterator[None]:
        """Handle rule diagnostics."""
        try:
            yield
        except (Diagnostic, DiagnosticCollection) as exc:
            self.handle_output(node, exc, name)
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

    def __call__(self, node: AbstractNode, *args: Any, **kwargs: Any) -> T:
        if not self.count:
            return node  # type: ignore
        self.stack.clear()
        result = self.invoke(node, *args, **kwargs)
        self.stack.clear()
        return result


class Visitor(Dispatcher[Any]):
    """Ast visitor."""

    def invoke(self, node: AbstractNode, *args: Any, **kwargs: Any) -> Any:
        self.stack.append(node)
        name, rule = next(self.dispatch(node), (None, None))
        node = self.process(node, name, rule, *args, **kwargs)
        self.stack.pop()
        return node


class Reducer(Dispatcher[Any]):
    """Ast reducer."""

    def invoke(self, node: AbstractNode, *args: Any, **kwargs: Any) -> Any:
        self.stack.append(node)
        for child in node:
            self.invoke(child, *args, **kwargs)
        node = super().invoke(node, *args, **kwargs)
        self.stack.pop()
        return node


class MutatingReducer(Dispatcher[Any]):
    """Mutating ast reducer."""

    def invoke(self, node: AbstractNode, *args: Any, **kwargs: Any) -> Any:
        self.stack.append(node)

        to_replace: Dict[str, Union[AbstractNode, AbstractChildren[AbstractNode]]] = {}

        for f in fields(node):
            attribute = getattr(node, f.name)
            if isinstance(attribute, AbstractChildren):
                result = type(attribute)(self.invoke(child, *args, **kwargs) for child in attribute)  # type: ignore
                if len(result) != len(attribute) or any(child is not original for child, original in zip(result, attribute)):  # type: ignore
                    to_replace[f.name] = result
            elif isinstance(attribute, AbstractNode):
                result = self.invoke(attribute, *args, **kwargs)
                if result is not attribute:
                    to_replace[f.name] = result

        if to_replace:
            node = replace(node, **to_replace)

        exhausted = False

        while not exhausted:
            exhausted = True

            for name, rule in self.dispatch(node):
                result = self.process(node, name, rule, *args, **kwargs)

                if result is not node:
                    if isinstance(result, AbstractNode):
                        exhausted = False
                        node = result
                        break
                    elif result is None or isinstance(result, AbstractChildren):
                        return result  # type: ignore
                    else:
                        msg = f"Invalid node of type {type(result)}."
                        if name:
                            msg += f" ({name})"
                        raise CompilationError(msg)

        self.stack.pop()
        return node
