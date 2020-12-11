from typing import List

from beet.toolchain.pipeline import GenericPipeline

TestPipeline = GenericPipeline[List[str]]


def test_empty():
    pipeline = TestPipeline([])
    pipeline.run()
    assert pipeline.ctx == []


def test_basic():
    pipeline = TestPipeline([])

    def p1(ctx: List[str]):
        ctx.append("p1")

    def p2(ctx: List[str]):
        ctx.append("p2")

    pipeline.run([p1, p2])
    assert pipeline.ctx == ["p1", "p2"]


def test_with_yield():
    pipeline = TestPipeline([])

    def p1(ctx: List[str]):
        ctx.append("p1")
        yield
        ctx.append("p1-bis")

    def p2(ctx: List[str]):
        ctx.append("p2")
        yield
        ctx.append("p2-bis")

    pipeline.run([p1, p2])
    assert pipeline.ctx == ["p1", "p2", "p2-bis", "p1-bis"]


def test_with_multiple_yield():
    pipeline = TestPipeline([])

    def p1(ctx: List[str]):
        ctx.append("p1")
        yield
        ctx.append("p1-bis")
        yield
        ctx.append("p1-bis-bis")

    def p2(ctx: List[str]):
        ctx.append("p2")
        yield
        ctx.append("p2-bis")
        yield
        ctx.append("p2-bis-bis")

    pipeline.run([p1, p2])
    assert pipeline.ctx == ["p1", "p2", "p2-bis", "p2-bis-bis", "p1-bis", "p1-bis-bis"]


def test_with_multiple_yield_and_nested_require():
    pipeline = TestPipeline([])

    def p1(ctx: List[str]):
        ctx.append("p1")
        yield
        pipeline.require(p3)
        ctx.append("p1-bis")
        yield
        ctx.append("p1-bis-bis")

    def p2(ctx: List[str]):
        ctx.append("p2")
        yield
        ctx.append("p2-bis")
        yield
        ctx.append("p2-bis-bis")

    def p3(ctx: List[str]):
        ctx.append("p3")
        yield
        ctx.append("p3-bis")

    pipeline.run([p1, p2])
    assert pipeline.ctx == [
        "p1",
        "p2",
        "p2-bis",
        "p2-bis-bis",
        "p3",
        "p1-bis",
        "p1-bis-bis",
        "p3-bis",
    ]


def test_self_require():
    pipeline = TestPipeline([])

    def p1(ctx: List[str]):
        pipeline.require(p1)
        ctx.append("p1")

    pipeline.run([p1])
    assert pipeline.ctx == ["p1"]
