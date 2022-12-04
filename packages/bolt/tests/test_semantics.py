import pytest

from bolt import (
    AstIdentifier,
    Binding,
    FunctionScope,
    GlobalScope,
    InconsistentIdentifierStorage,
    LexicalScope,
    UnboundLocalIdentifier,
    UndefinedIdentifier,
    Variable,
)


def test_variable():
    lexical_scope = LexicalScope()
    assert not lexical_scope.has_variable("foo")

    lexical_scope.bind_variable("foo", AstIdentifier(value="foo"))
    assert lexical_scope.has_variable("foo")
    assert lexical_scope.list_variables() == {"foo"}

    lexical_scope.reference_variable("foo", AstIdentifier(value="foo"))
    assert lexical_scope.variables == {
        "foo": Variable(
            bindings=[
                Binding(
                    origin=AstIdentifier(value="foo"),
                    references=[AstIdentifier(value="foo")],
                )
            ]
        )
    }


def test_global():
    global_scope = GlobalScope(identifiers={"THING"})

    assert global_scope.has_variable("THING")
    assert global_scope.list_variables() == {"THING"}

    assert not global_scope.has_binding("THING")

    lexical_scope = global_scope.push(LexicalScope)
    assert lexical_scope.has_variable("THING")
    assert lexical_scope.list_variables() == {"THING"}

    lexical_scope.reference_variable("THING", AstIdentifier(value="THING"))
    assert lexical_scope.variables == {}
    assert global_scope.variables == {}


def test_children():
    lexical_scope = LexicalScope()

    with pytest.raises(UndefinedIdentifier, match='"foo" is not defined'):
        lexical_scope.reference_variable("foo", AstIdentifier(value="foo"))
    with pytest.raises(UnboundLocalIdentifier, match='"foo" is not defined'):
        lexical_scope.reference_binding("foo", AstIdentifier(value="foo"))

    lexical_scope.bind_variable("foo", AstIdentifier(value="foo"))

    child_scope = lexical_scope.push(FunctionScope)

    with pytest.raises(UnboundLocalIdentifier) as exc_info:
        child_scope.reference_binding("foo", AstIdentifier(value="foo"))
    assert exc_info.value.notes == [
        'Use "global foo" or "nonlocal foo" to mutate the variable defined in outer scope.'
    ]

    alternative_scope = child_scope.fork()

    child_scope.bind_variable("foo", AstIdentifier(value="foo"))

    with pytest.raises(InconsistentIdentifierStorage):
        child_scope.bind_storage("foo", "nonlocal", AstIdentifier(value="foo"))

    alternative_scope.bind_storage("foo", "nonlocal", AstIdentifier(value="foostorage"))
    alternative_scope.reference_variable("foo", AstIdentifier(value="fooparent"))
    alternative_scope.bind_variable("foo", AstIdentifier(value="foovalue"))
    alternative_scope.reference_variable("foo", AstIdentifier(value="fooref"))

    assert alternative_scope.variables == {
        "foo": Variable(
            storage="nonlocal",
            bindings=[
                Binding(
                    origin=AstIdentifier(value="foostorage"),
                    references=[
                        AstIdentifier(value="fooparent"),
                        AstIdentifier(value="foovalue"),
                    ],
                ),
                Binding(
                    origin=AstIdentifier(value="foovalue"),
                    references=[AstIdentifier(value="fooref")],
                ),
            ],
        )
    }

    assert lexical_scope.variables == {
        "foo": Variable(
            bindings=[
                Binding(
                    origin=AstIdentifier(value="foo"),
                    references=[],
                )
            ]
        )
    }

    child_scope.reconcile(alternative_scope)

    assert lexical_scope.variables == {
        "foo": Variable(
            bindings=[
                Binding(
                    origin=AstIdentifier(value="foo"),
                    references=[
                        AstIdentifier(value="foostorage"),
                        AstIdentifier(value="fooparent"),
                        AstIdentifier(value="foovalue"),
                    ],
                ),
                Binding(
                    origin=AstIdentifier(value="foovalue"),
                    references=[AstIdentifier(value="fooref")],
                ),
            ]
        )
    }
