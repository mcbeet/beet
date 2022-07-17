from mecha import delegate, AstCommand, AstChildren
from bolt import AstExpressionUnary

macro repeat(stream):
    with stream.syntax(count="[0-9]+"):
        token = stream.expect("count")
    body = delegate("nested_root", stream)
    return int(token.value) * [body]

macro repeat until(stream):
    condition = delegate("bolt:expression", stream)
    body = delegate("nested_root", stream)
    return AstCommand(
        identifier="while:condition:body",
        arguments=AstChildren([
            AstExpressionUnary(operator="not", value=condition),
            body,
        ])
    )

macro repeat until(stream):
    entity = delegate("selector", stream)
    body = delegate("nested_root", stream)
    path = generate_path()
    execute function path:
        yield body
        unless entity entity function path
