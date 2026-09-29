"""Helper for managing singletons that persist across builds during an entire beet session."""

__all__ = [
    "singleton",
]


from collections.abc import Callable
from contextlib import AbstractContextManager, ExitStack
import inspect
from typing import Any

from beet import Connection, Context
from beet.core.utils import SENTINEL_OBJ, format_obj


type Singleton[T] = Callable[..., T | AbstractContextManager[T]]

RESOLVER_REGISTRY: dict[str, SingletonResolver[Any]] = {}


def singleton[T](factory: Singleton[T]) -> SingletonResolver[T]:
    key = format_obj(factory)
    resolver = RESOLVER_REGISTRY.get(key)
    if resolver is None:
        resolver = SingletonResolver(
            key=key,
            factory=factory,
            dependencies={
                name: singleton(param.annotation)
                for name, param in inspect.signature(factory).parameters.items()
            },
        )
        RESOLVER_REGISTRY[key] = resolver
    return resolver


class SingletonResolver[T]:
    key: str
    factory: Singleton[T]
    dependencies: dict[str, SingletonResolver[Any]]

    def __init__(
        self,
        key: str,
        factory: Singleton[T],
        dependencies: dict[str, SingletonResolver[Any]],
    ):
        self.key = key
        self.factory = factory
        self.dependencies = dependencies

    def __call__(self, ctx: Context) -> T:
        with ctx.worker(singleton_worker) as channel:
            return self.resolve(channel.recv())

    def resolve(self, container: dict[str, Any]) -> T:
        obj: Any = container.get(self.key, SENTINEL_OBJ)
        if obj is SENTINEL_OBJ:
            dependencies = {
                name: resolver.resolve(container)
                for name, resolver in self.dependencies.items()
            }
            obj = self.factory(**dependencies)
            if isinstance(obj, AbstractContextManager):
                obj = container[format_obj(ExitStack)].enter_context(obj)
            container[self.key] = obj
        return obj


def singleton_worker(connection: Connection[None, dict[str, Any]]):
    exit_stack = ExitStack()
    container = {format_obj(ExitStack): exit_stack}
    with exit_stack:
        for client in connection:
            client.send(container)
            client.close()
