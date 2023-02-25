from typing import Generic, TypeVar

from beet.core.container import resolve_base_generics


def test_resolve_direct_generics():
    T1 = TypeVar("T1")
    T2 = TypeVar("T2")

    class Base(Generic[T1, T2]):
        pass

    assert resolve_base_generics(Base[T1, T2], Base) == {T1: T1, T2: T2}


def test_resolve_fully_generic_child():
    T1 = TypeVar("T1")
    T2 = TypeVar("T2")

    class Base(Generic[T1, T2]):
        pass

    class Child(Base[T1, T2]):
        pass

    assert resolve_base_generics(Child, Base) == {T1: T1, T2: T2}


def test_resolve_fully_generic_child_reversed():
    T1 = TypeVar("T1")
    T2 = TypeVar("T2")

    class Base(Generic[T1, T2]):
        pass

    class Child(Base[T2, T1]):
        pass

    assert resolve_base_generics(Child, Base) == {T1: T2, T2: T1}


def test_resolve_generic1_child():
    T1 = TypeVar("T1")
    T2 = TypeVar("T2")

    class Base(Generic[T1, T2]):
        pass

    class Child(Base[T1, int]):
        pass

    assert resolve_base_generics(Child, Base) == {T1: T1, T2: int}


def test_resolve_generic2_child():
    T1 = TypeVar("T1")
    T2 = TypeVar("T2")

    class Base(Generic[T1, T2]):
        pass

    class Child(Base[int, T1]):
        pass

    assert resolve_base_generics(Child, Base) == {T1: int, T2: T1}


def test_resolve_fixed_child():
    T1 = TypeVar("T1")
    T2 = TypeVar("T2")

    class Base(Generic[T1, T2]):
        pass

    class Child(Base[int, float]):
        pass

    assert resolve_base_generics(Child, Base) == {T1: int, T2: float}


# TODO: Add more test cases
