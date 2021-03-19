import pytest

from beet import Connection, WorkerError, WorkerPool


def worker1(connection: Connection[int, str]):
    for client in connection:
        for number in client:
            client.send(" ".join(map(str, range(number))))


def test_basic():
    pool = WorkerPool()

    with pool.handle() as handle:
        with handle(worker1) as channel:
            channel.send(2)
            channel.send(3)

    assert list(channel) == ["0 1", "0 1 2"]


def test_nested():
    pool = WorkerPool()

    with pool.handle() as handle1:
        with pool.handle() as handle2:
            assert handle1 is handle2

            with handle2(worker1) as channel2:
                channel2.send(2)

        with handle1(worker1) as channel1:
            channel1.send(3)

    assert list(channel1) == ["0 1 2"]
    assert list(channel2) == ["0 1"]


def worker2(connection: Connection[None, float]):
    for client in connection:
        client.send(1 / 0)


def test_error():
    msg = "Worker 'tests.test_worker.worker2' raised an exception."

    with pytest.raises(WorkerError) as outer:
        with WorkerPool().handle() as handle:
            with handle(worker2) as channel:
                channel.send(None)

            with pytest.raises(WorkerError) as inner:
                next(channel)

            assert inner.value.message == msg
    assert outer.value.message == msg
