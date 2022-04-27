__all__ = [
    "Worker",
    "WorkerThread",
    "WorkerError",
    "WorkerPool",
    "WorkerPoolHandle",
    "MessageQueue",
    "Channel",
    "Connection",
]


import logging
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from queue import Queue
from threading import Thread
from typing import (
    Any,
    Dict,
    Generic,
    Iterator,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from beet.core.error import BubbleException, WrappedException
from beet.core.utils import SENTINEL_OBJ, Sentinel, format_obj, pop_traceback

T = TypeVar("T")
U = TypeVar("U")
SendType = TypeVar("SendType")
RecvType = TypeVar("RecvType")
SelfType = TypeVar("SelfType")


logger = logging.getLogger(__name__)


class Worker(Protocol[SendType, RecvType]):
    """Protocol for detecting workers.

    Workers can be arbitrary objects as long as they can be called with
    a connection. The connection can be used to listen and respond to
    clients.
    """

    def __call__(self, connection: "Connection[SendType, RecvType]") -> Any:
        ...


class WorkerError(WrappedException):
    """Raised when a worker raises an exception."""

    worker: Any

    def __init__(self, worker: Any):
        super().__init__(worker)
        self.worker = worker

    def __str__(self) -> str:
        return f"Worker {format_obj(self.worker)} raised an exception."


@dataclass
class MessageQueue(Generic[T]):
    """Closeable threadsafe queue.

    This class is a small wrapper around the builtin Queue. The API is
    designed to work like a python generator instance. The queue can be
    used as a context manager, and will prevent you from sending more
    messages once the queue is closed.
    """

    queue: "Queue[Union[T, Sentinel, BaseException]]" = field(default_factory=Queue)
    closed: bool = False

    def send(self, message: T):
        """Send a message.

        If the queue is closed the method will raise an exception.
        """
        if self.closed:
            raise ValueError("Message queue is closed.")
        self.queue.put(message, block=False)

    def throw(self, exc: BaseException):
        """Throw an exception.

        If the queue is closed the method will raise an exception.
        """
        if self.closed:
            raise ValueError("Message queue is closed.")
        self.queue.put(exc, block=False)

    def close(self):
        """Close the queue.

        If the queue is already closed this is a no-op.
        """
        if not self.closed:
            self.closed = True
            self.queue.put(SENTINEL_OBJ, block=False)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        message = self.queue.get()
        if isinstance(message, Sentinel):
            raise StopIteration()
        if isinstance(message, BaseException):
            raise message
        return message

    def __enter__(self: SelfType) -> SelfType:
        return self

    def __exit__(self, *_):
        self.close()


@dataclass
class Channel(Generic[T, U]):
    """A bidirectional communication channel.

    Channels are meant to be created entangled with one another, meaning
    that messages sent in one channel will be received in the other.
    """

    send_queue: MessageQueue[U]
    recv_queue: MessageQueue[T]

    def send(self, message: U):
        """Send a message to the receiver.

        If the channel is closed the method will raise an exception.
        """
        self.send_queue.send(message)

    def throw(self, exc: BaseException):
        """Throw an exception to the receiver.

        If the channel is closed the method will raise an exception.
        """
        self.send_queue.throw(exc)

    def close(self):
        """Close the channel.

        If the channel is already closed this is a no-op.
        """
        self.send_queue.close()

    @property
    def closed(self) -> bool:
        return self.send_queue.closed

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        try:
            return next(self.recv_queue)
        except:
            self.close()
            raise

    def __enter__(self: SelfType) -> SelfType:
        return self

    def __exit__(self, *_):
        self.close()

    @classmethod
    def entangled_pair(cls) -> Tuple["Channel[Any, Any]", "Channel[Any, Any]"]:
        """Return a pair of channels that can communicate with each other.

        Messages sent from one channel will be received by the other.
        """
        q1 = MessageQueue[Any]()
        q2 = MessageQueue[Any]()
        return cls(q1, q2), cls(q2, q1)


@dataclass
class Connection(MessageQueue[Channel[T, U]]):
    """The connection that allows workers to interact with clients.

    The worker connection is a queue of channels. By iterating over the
    connection itself, you can listen and communicate with clients.

    The connection can also be used to figure out if the worker will be
    long-lived. Although this is simply a hint, it can be used to decide
    whether to spawn a long-lived task like a background server.
    """

    long_lived: bool = False
    current_client: Optional[Channel[T, U]] = None

    def __next__(self) -> Channel[T, U]:
        self.current_client = super().__next__()
        return self.current_client

    def wait(self):
        """Wait until there are no more incoming clients."""
        for client in self:
            client.close()


class WorkerThread(Thread, Generic[T, U]):
    """The thread that runs the worker.

    Worker threads can be used as context managers. When exiting the
    scope the thread will be joined automatically.
    """

    func: Worker[T, U]
    connection: Connection[T, U]
    exc: Optional[Exception]

    def __init__(self, func: Worker[T, U], connection: Connection[T, U]):
        super().__init__()
        self.func = func
        self.connection = connection
        self.exc = None

    def run(self) -> None:
        try:
            self.func(self.connection)
        except BubbleException as exc:
            self.exc = exc
        except Exception as exc:
            self.exc = WorkerError(self.func)
            self.exc.__cause__ = pop_traceback(exc)
        if (
            self.exc
            and self.connection.current_client
            and not self.connection.current_client.closed
        ):
            self.connection.current_client.throw(self.exc)

    def join(self, timeout: Optional[float] = None):
        super().join(timeout=timeout)
        if self.exc:
            raise self.exc

    def __enter__(self: SelfType) -> SelfType:
        return self

    def __exit__(self, *_):
        self.join()


@dataclass
class WorkerPoolHandle:
    """Persistent handle that spawns and manages worker threads."""

    exit_stack: Optional[ExitStack]
    long_lived: bool = False
    connections: Dict[Worker[Any, Any], Connection[Any, Any]] = field(
        default_factory=dict
    )
    active_workers: Dict[str, Worker[Any, Any]] = field(default_factory=dict)
    reload_skipped: Set[str] = field(default_factory=set)

    def __call__(self, func: Worker[T, U]) -> Channel[U, T]:
        if self.exit_stack is None:
            raise ValueError("Worker pool has shut down.")

        if active_func := self.active_workers.get(ident := format_obj(func)):
            if active_func is not func:
                if ident not in self.reload_skipped:
                    logger.warning("Skipping worker reload %s.", ident)
                    self.reload_skipped.add(ident)
                func = active_func

        connection = self.connections.get(func)

        if connection is None:
            connection = self.exit_stack.enter_context(self.spawn(func))

        channel1, channel2 = Channel.entangled_pair()
        connection.send(channel1)

        return channel2

    @contextmanager
    def spawn(self, func: Worker[T, U]) -> Iterator[Connection[T, U]]:
        """Create a worker thread and return the connection.

        The thread will be joined at the end of the scope.
        """
        ident = format_obj(func)
        self.active_workers[ident] = func

        connection = Connection[Any, Any](long_lived=self.long_lived)
        self.connections[func] = connection

        try:
            with WorkerThread(func, connection) as thread:
                with connection:
                    thread.start()
                    yield connection
        finally:
            del self.connections[func]
            del self.active_workers[ident]


@dataclass
class WorkerPool:
    """Class that creates and keeps a reference to the pool handle."""

    resolved_handle: Optional[WorkerPoolHandle] = None

    @contextmanager
    def handle(self) -> Iterator[WorkerPoolHandle]:
        """Ensure that the pool is active and return the handle."""
        if self.resolved_handle is None:
            with ExitStack() as stack:
                self.resolved_handle = WorkerPoolHandle(stack)

                try:
                    yield self.resolved_handle
                finally:
                    self.resolved_handle.exit_stack = None
                    self.resolved_handle = None
        else:
            yield self.resolved_handle

    @contextmanager
    def long_lived_session(self) -> Iterator[None]:
        """Ensure that the pool is active and mark the handle as long-lived."""
        with self.handle() as handle:
            previous_value = handle.long_lived
            handle.long_lived = True

            try:
                yield
            finally:
                handle.long_lived = previous_value
