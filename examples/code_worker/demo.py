from typing import Tuple

from beet import Connection, Context, Function


def beet_default(ctx: Context):
    ctx.require(other)

    with ctx.worker(thing) as channel:
        channel.send(2)
        channel.send(3)

    for name, function in channel:
        ctx.data[name] = function


def other(ctx: Context):
    with ctx.worker(thing) as channel:
        channel.send(4)

    yield

    ctx.data["demo:function_count"] = Function([f"say {len(ctx.data.function)}"])

    for name, function in channel:
        ctx.data[name] = function


def thing(connection: Connection[int, Tuple[str, Function]]):
    counter = 0
    for client in connection:
        for number in client:
            client.send((f"demo:foo_{counter}", Function([f"say {counter}"] * number)))
            counter += 1
