__all__ = [
    "Codegen",
    "Accumulator",
    "CodegenStatement",
    "WithStatementFusion",
    "ChildrenCollector",
    "CommandCollector",
    "RootCommandCollector",
    "visit_single",
    "visit_multiple",
    "visit_generic",
    "visit_body",
    "visit_binding",
]


from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field, fields, replace
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
    overload,
)

from mecha import (
    AstChildren,
    AstCommand,
    AstNode,
    AstResourceLocation,
    AstRoot,
    Visitor,
    rule,
)

from .ast import (
    AstAssignment,
    AstAttribute,
    AstCall,
    AstChainedComparison,
    AstClassBases,
    AstClassName,
    AstDict,
    AstDictItem,
    AstDocstring,
    AstEscapeRoot,
    AstExpressionBinary,
    AstExpressionUnary,
    AstFormatString,
    AstFormattedLocation,
    AstFromImport,
    AstFunctionSignature,
    AstFunctionSignatureArgument,
    AstFunctionSignaturePositionalMarker,
    AstFunctionSignatureVariadicArgument,
    AstFunctionSignatureVariadicKeywordArgument,
    AstFunctionSignatureVariadicMarker,
    AstIdentifier,
    AstImportedItem,
    AstImportedMacro,
    AstInterpolation,
    AstKeyword,
    AstList,
    AstLookup,
    AstMacro,
    AstMacroCall,
    AstMacroMatchArgument,
    AstMemo,
    AstPrelude,
    AstProcMacro,
    AstSlice,
    AstStatement,
    AstTargetAttribute,
    AstTargetIdentifier,
    AstTargetItem,
    AstTargetUnpack,
    AstTuple,
    AstTypeDeclaration,
    AstUnpack,
    AstValue,
    AstWithContext,
)
from .module import CodegenResult, MacroLibrary


@dataclass(slots=True)
class CodegenStatement:
    """Python statement emitted by the codegen, which can recursively contain other statements."""

    code: Tuple[str, ...]
    lineno: Optional[int] = None
    children: List["CodegenStatement"] = field(default_factory=list)

    def flatten(self, indent: str = "") -> Iterable[Tuple[str, Optional[int]]]:
        """Yield the indented statements with their associated line number."""
        if self.code:
            statement = " ".join(self.code)
            if self.children:
                statement += ":"
            yield f"{indent}{statement}", self.lineno
        if self.children:
            indent += 4 * " "
            for child_statement in self.children:
                yield from child_statement.flatten(indent)


@dataclass
class Accumulator:
    """Utility for generating python code."""

    refs: List[Any] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    prelude_imports: List[AstPrelude] = field(default_factory=list)
    macros: MacroLibrary = field(default_factory=dict)
    macro_ids: Dict[str, int] = field(default_factory=dict)
    memo_index: Dict[AstMemo, int] = field(default_factory=dict)
    statements: List["CodegenStatement"] = field(default_factory=list)
    counter: int = 0
    header: Dict[str, str] = field(default_factory=dict)
    root_scope: bool = True

    current_siblings: Tuple[AstNode, ...] = ()
    current_sibling_index: int = 0
    condition_inverse: Optional[str] = None

    def get_source(self) -> str:
        """Return the source code."""
        header = [
            CodegenStatement((variable, "=", expression))
            for variable, expression in self.header.items()
        ]

        lines: List[str] = ["_bolt_lineno = "]
        numbers1: List[int] = [1]
        numbers2: List[int] = [1]

        for statement in header + self.statements:
            for code, lineno in statement.flatten():
                if lineno and numbers2[-1] != lineno:
                    numbers1.append(len(lines) + 1)
                    numbers2.append(lineno)
                lines.append(code)

        lines[0] += f"{numbers1}, {numbers2}"

        return "\n".join(lines) + "\n"

    def helper(self, name: str, *args: Any) -> str:
        """Emit helper."""
        helper = f"_bolt_helper_{name}"

        if helper not in self.header:
            self.header[helper] = f"_bolt_runtime.helpers[{name!r}]"

        return f"{helper}({', '.join(map(str, args))})"

    def replace(self, node: str, **kwargs: str) -> str:
        """Emit replace helper."""
        return self.helper("replace", node, *(f"{k}={v}" for k, v in kwargs.items()))

    def missing(self) -> str:
        """Emit missing sentinel."""
        self.header["_bolt_helper_missing"] = "_bolt_runtime.helpers['missing']"
        return "_bolt_helper_missing"

    def children(self, nodes: Iterable[str]) -> str:
        """Emit children helper."""
        return self.helper("children", f"[{', '.join(nodes)}]")

    def get_attribute_handler(self, obj: str, name: str) -> str:
        """Emit get_attribute_handler helper."""
        attribute_handler = self.helper("get_attribute_handler", obj)
        return f'{attribute_handler}["{name}"]'

    def import_module(self, name: str) -> str:
        """Emit import_module helper."""
        return self.helper("import_module", repr(name))

    def make_ref(self, obj: Any) -> str:
        """Register ref."""
        index = len(self.refs)
        self.refs.append(obj)
        return f"_bolt_refs[{index}]"

    def make_ref_slice(self, objs: Iterable[Any]) -> str:
        """Register ref slice."""
        start = len(self.refs)
        self.refs.extend(objs)
        stop = len(self.refs)
        return f"_bolt_refs[{start}:{stop}]"

    def make_variable(self) -> str:
        """Create a unique variable name."""
        name = f"__bolt_var{self.counter}"
        self.counter += 1
        return name

    def make_macro(self, node: AstMacro) -> str:
        """Add macro to macro library."""
        macro = self.get_macro(node.identifier)
        group = node.identifier.partition(":")[0]
        if self.root_scope:
            self.macros.setdefault(group, {})[macro, node] = None
        return macro

    def import_macro(self, resource_location: str, node: AstImportedMacro) -> str:
        """Import macro into macro library."""
        macro = self.get_macro(node.declaration.identifier)
        group = node.declaration.identifier.partition(":")[0]
        if self.root_scope:
            self.macros.setdefault(group, {})[macro, node.declaration] = (
                resource_location,
                node.name,
            )
        return macro

    def get_macro(self, name: str) -> str:
        """Get macro."""
        if name not in self.macro_ids:
            self.macro_ids[name] = len(self.macro_ids)
        return f"_bolt_macro{self.macro_ids[name]}"

    def extract_lineno(self, lineno: Any):
        """Utility to extract the line number."""
        if isinstance(lineno, AstNode) and not lineno.location.unknown:
            lineno = lineno.location.lineno
        if isinstance(lineno, int):
            return lineno
        return None

    @contextmanager
    def block(self):
        """Wrap statements in an indented block."""
        previous_statements = self.statements
        self.statements = self.statements[-1].children
        try:
            yield
        finally:
            self.statements = previous_statements

    def statement(self, *code: str, lineno: Any = None):
        """Emit statement."""
        self.statements.append(CodegenStatement(code, self.extract_lineno(lineno)))

    @contextmanager
    def function(self, name: str, *args: str, return_type: str = ""):
        """Emit function."""
        return_type_annotation = return_type and f" -> {return_type}"
        self.statement(f"def {name}({', '.join(args)}){return_type_annotation}")
        with self.block():
            previous_root = self.root_scope
            self.root_scope = False
            temp_counter = self.counter
            yield
            self.counter = temp_counter
            self.root_scope = previous_root

    @contextmanager
    def if_statement(
        self,
        condition: str,
        inverse: Optional[str] = None,
        *,
        lineno: Any = None,
    ):
        """Emit if statement."""
        branch = self.helper("branch", condition)
        self.statement("with", branch, "as", "_bolt_condition", lineno=lineno)
        with self.block():
            self.statement("if", "_bolt_condition")
            with self.block():
                yield
        self.condition_inverse = inverse

    @contextmanager
    def else_statement(self, *, lineno: Any = None):
        """Emit else statement."""
        if not self.condition_inverse:
            raise ValueError("Condition inverse unavailable.")
        with self.if_statement(self.condition_inverse, lineno=lineno):
            yield

    def binary(self, left: str, op: str, right: str, *, lineno: Any = None):
        """Emit binary operator."""
        if op in ["in", "not_in"]:
            value = self.helper(f"operator_{op}", left, right)
            self.statement(f"{left} = {value}", lineno=lineno)
        else:
            op = op.replace("_", " ")
            self.statement(f"{left} = {left} {op} {right}", lineno=lineno)

    def dup(self, target: str, *, lineno: Any = None) -> str:
        """Emit __dup__()."""
        dup = self.make_variable()
        value = self.helper("get_dup", target)
        self.statement(f"{dup} = {value}", lineno=lineno)
        self.statement("if", f"{dup} is not None")
        with self.block():
            self.statement(f"{target} = {dup}()")
        return dup

    def rebind(self, target: str, op: str, value: str, *, lineno: Any = None):
        """Emit __rebind__()."""
        rebind = self.helper("get_rebind", target)
        self.statement(f"_bolt_rebind = {rebind}", lineno=lineno)
        self.statement(f"{target} {op} {value}")
        self.statement("if", "_bolt_rebind is not None")
        with self.block():
            self.statement(f"{target} = _bolt_rebind({target})")

    def rebind_dup(self, target: str, dup: str, value: str, *, lineno: Any = None):
        """Emit __rebind__() if target was __dup__()."""
        self.statement("if", f"{dup} is not None")
        with self.block():
            self.rebind(target, "=", value, lineno=lineno)
        self.statement("else")
        with self.block():
            self.statement(f"{target} = {value}")

    def enclose(self, *code: str, from_index: int, lineno: Any = None):
        """Enclose statements starting from the given index."""
        self.statements[from_index:] = [
            CodegenStatement(
                code, self.extract_lineno(lineno), self.statements[from_index:]
            )
        ]


@dataclass
class WithStatementFusion:
    """Finalizer for fusing nested with statements."""

    counter: int = 0

    @classmethod
    def finalize(cls, acc: Accumulator):
        with_statement_fusion = cls()
        acc.statements = [
            with_statement_fusion.fuse(statement, acc) for statement in acc.statements
        ]

    def convert(self, statement: CodegenStatement, exit_stack: str) -> CodegenStatement:
        code = (f"{exit_stack}.enter_context({statement.code[1]})",)
        if len(statement.code) > 2:
            code = (statement.code[3], "=", *code)
        return replace(statement, code=code, children=[])

    def fuse(self, statement: CodegenStatement, acc: Accumulator) -> CodegenStatement:
        children = [self.fuse(child, acc) for child in statement.children]

        if statement.code[0] != "with":
            return replace(statement, children=children)

        nested_children = children
        while nested_children[-1].code[0] == "if":
            nested_children = nested_children[-1].children

        if nested_children[-1].code[0] != "with":
            return replace(statement, children=children)

        nested_statement = nested_children.pop()

        if nested_statement.code[1] == acc.helper("exit_stack"):
            exit_stack = nested_statement.code[3]
            code = nested_statement.code
        else:
            exit_stack = f"_bolt_fused_with_statement{self.counter}"
            self.counter += 1
            code = ("with", acc.helper("exit_stack"), "as", exit_stack)
            nested_children.append(self.convert(nested_statement, exit_stack))

        children.insert(0, self.convert(statement, exit_stack))
        nested_children.extend(nested_statement.children)

        return replace(statement, code=code, children=children)


@dataclass
class ChildrenCollector:
    """Generic children collector."""

    acc: Accumulator
    start_index: int
    children: List[str] = field(default_factory=list)

    def add_static(self, *args: AstNode):
        self.children.extend(self.acc.make_ref(node) for node in args)

    def add_dynamic(self, *args: str):
        self.children.extend(args)

    def flush(self) -> str:
        return self.acc.children(self.children)


class CommandCollector(ChildrenCollector):
    """Collector for commands."""

    def add_static(self, *args: AstNode):
        if len(args) > 1:
            self.acc.statement(
                f"_bolt_runtime.commands.extend({self.acc.make_ref_slice(args)})"
            )
        elif args:
            self.acc.statement(
                f"_bolt_runtime.commands.append({self.acc.make_ref(args[0])})"
            )

    def add_dynamic(self, *args: str):
        for arg in args:
            if arg.startswith("*"):
                self.acc.statement(f"_bolt_runtime.commands.extend({arg[1:]})")
            else:
                self.acc.statement(f"_bolt_runtime.commands.append({arg})")


class RootCommandCollector(CommandCollector):
    """Collector for commands in a standalone root node."""

    def flush(self) -> str:
        commands = self.acc.make_variable()
        self.acc.enclose(
            "with",
            "_bolt_runtime.scope()",
            "as",
            commands,
            from_index=self.start_index,
        )
        return self.acc.helper("children", commands)


@overload
def visit_single(
    node: AstNode,
) -> Generator[AstNode, Optional[List[str]], Optional[str]]: ...


@overload
def visit_single(
    node: AstNode,
    required: Literal[True],
) -> Generator[AstNode, Optional[List[str]], str]: ...


def visit_single(
    node: AstNode,
    required: bool = False,
) -> Generator[AstNode, Optional[List[str]], Optional[str]]:
    """Yield the node and make sure that it returns a single result."""
    result = yield node

    if result is None:
        if required:
            raise ValueError(
                f"Result required for {node.__class__.__name__} {result!r}."
            )
        return None

    if len(result) != 1:
        raise ValueError(
            f"Expected single result for {node.__class__.__name__} {result!r}."
        )

    return result[0]


def visit_multiple(
    children: Tuple[AstNode, ...],
    acc: Accumulator,
    children_collector: Type[ChildrenCollector] = ChildrenCollector,
) -> Generator[AstNode, Optional[List[str]], Optional[str]]:
    """Yield all the nodes and return a single result pointing to the new children."""
    current_count = 0
    collector: Optional[ChildrenCollector] = None
    index = len(acc.statements)

    previous_siblings = acc.current_siblings
    previous_sibling_index = acc.current_sibling_index
    acc.current_siblings = children

    for i, child in enumerate(children):
        acc.current_sibling_index = i

        result = yield child
        if result is None:
            continue
        if not collector:
            collector = children_collector(acc, index)

        statements = acc.statements[index:]
        del acc.statements[index:]
        collector.add_static(*children[current_count:i])
        acc.statements.extend(statements)
        collector.add_dynamic(*result)

        current_count = i + 1
        index = len(acc.statements)

    acc.current_siblings = previous_siblings
    acc.current_sibling_index = previous_sibling_index

    if collector:
        collector.add_static(*children[current_count:])
        return collector.flush()

    return None


def visit_generic(
    node: AstNode,
    acc: Accumulator,
    children_collector: Type[ChildrenCollector] = ChildrenCollector,
) -> Generator[AstNode, Optional[List[str]], Optional[str]]:
    """Recursively yield all the fields and return a result pointing to the updated node."""
    to_replace: Dict[str, str] = {}

    for f in fields(node):
        attribute = getattr(node, f.name)
        result = None

        if isinstance(attribute, AstChildren):
            attribute = cast(AstChildren[AstNode], attribute)
            result = yield from visit_multiple(attribute, acc, children_collector)

        elif isinstance(attribute, AstNode):
            result = yield from visit_single(attribute)

        if result is not None:
            to_replace[f.name] = result

    if not to_replace:
        return None

    return acc.replace(acc.make_ref(node), **to_replace)


def visit_body(
    node: AstRoot,
    acc: Accumulator,
) -> Generator[AstNode, Optional[List[str]], None]:
    """Emit each individual command in the current scope."""
    result = yield from visit_multiple(node.commands, acc, CommandCollector)
    if result is None:
        acc.statement(f"_bolt_runtime.commands.extend({acc.make_ref(node)}.commands)")


def visit_binding(
    target_node: AstNode,
    op: str,
    value: str,
    acc: Accumulator,
) -> Generator[AstNode, Optional[List[str]], None]:
    """Emit variable binding."""
    targets = yield target_node

    if not targets:
        return

    if len(targets) > 1 and isinstance(target_node, AstTargetUnpack):
        nodes = target_node.targets
        values = [f"_bolt_unpack{i}" for i in range(len(targets))]
        acc.statement(f"{', '.join(values)} = {value}", lineno=target_node)
    else:
        nodes = [target_node]
        values = [value]

    for node, target, value in zip(nodes, targets, values):
        if isinstance(node, AstTargetIdentifier) and node.rebind:
            acc.rebind(target, op, value, lineno=node)
        else:
            acc.statement(f"{target} {op} {value}", lineno=node)


@dataclass(eq=False)
class Codegen(Visitor):
    """Code generator."""

    accumulator_factory: Callable[[], Accumulator] = Accumulator
    finalizers: List[Callable[[Accumulator], None]] = field(
        default_factory=lambda: [WithStatementFusion.finalize]
    )

    def __call__(self, node: AstRoot) -> CodegenResult:
        acc = self.accumulator_factory()
        result = self.invoke(node, acc)

        if result is None:
            return CodegenResult()

        if len(result) != 1:
            raise ValueError(
                f"Expected single result for {node.__class__.__name__} {result!r}."
            )

        output = acc.make_variable()
        acc.statement(f"{output} = {result[0]}")

        for finalizer in self.finalizers:
            finalizer(acc)

        return CodegenResult(
            source=acc.get_source(),
            output=output,
            refs=acc.refs,
            dependencies=acc.dependencies,
            prelude_imports=tuple(acc.prelude_imports),
            macros=acc.macros,
        )

    @rule(AstNode)
    def fallback(
        self,
        node: AstNode,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_generic(node, acc)
        if result is None:
            return None
        return [result]

    @rule(AstRoot)
    def root(
        self,
        node: AstRoot,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_generic(node, acc, RootCommandCollector)
        if result is None:
            return None
        return [result]

    @rule(AstCommand)
    def command(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        if not node.arguments:
            return None

        if not isinstance(node.arguments[-1], (AstCommand, AstRoot)):
            arguments = yield from visit_multiple(node.arguments, acc)
            if arguments is None:
                return None
            return [acc.replace(acc.make_ref(node), arguments=arguments)]

        arguments = yield from visit_multiple(node.arguments[:-1], acc)
        nesting_index = len(acc.statements)
        nesting = yield from visit_single(node.arguments[-1])

        if nesting is None:
            if arguments is None:
                return None
            nesting = acc.make_ref(node.arguments[-1])
        else:
            if arguments is None and len(node.arguments) > 1:
                arguments = acc.make_ref_slice(node.arguments[:-1])
            push_arguments = f", *{arguments}" if arguments else ""
            acc.enclose(
                "with",
                f"_bolt_runtime.push_nesting({node.identifier!r}{push_arguments})",
                from_index=nesting_index,
            )

        arguments = acc.children([f"*{arguments}", nesting] if arguments else [nesting])
        return [acc.replace(acc.make_ref(node), arguments=arguments)]

    @rule(AstStatement)
    def statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        yield node.arguments[0]
        return []

    @rule(AstMemo)
    def memo(
        self,
        node: AstMemo,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        file_index = acc.memo_index.setdefault(node, 0)
        acc.memo_index[node] = file_index + 1

        keys: List[str] = []

        *arguments, body = node.arguments
        cached_identifiers = (
            "".join(f"{name}," for name in body.identifiers)
            if isinstance(body, AstEscapeRoot)
            else None
        )

        for arg in arguments:
            if isinstance(arg, AstAssignment):
                target = cast(AstTargetIdentifier, arg.target)
                yield arg
                keys.append(f"{target.value},")
            else:
                value = yield from visit_single(arg, required=True)
                keys.append(f"{value},")

        storage = f"_bolt_memo_storage_{node.persistent_id.hex}"
        acc.header[storage] = "None"
        if not acc.root_scope:
            acc.statement(f"global {storage}", lineno=node)
        acc.statement("if", f"{storage} is None")
        with acc.block():
            acc.statement(
                f"{storage} = _bolt_runtime.memo.registry[__file__][{acc.make_ref(node)}, {file_index}]"
            )

        path = f"_bolt_memo_invocation_path_{node.persistent_id.hex}"
        acc.statement(f"{path} = _bolt_runtime.get_nested_location()")

        invocation = f"_bolt_memo_invocation_{node.persistent_id.hex}"
        acc.statement(f"{invocation} = {storage}[({path}, {' '.join(keys)})]")

        acc.statement("if", f"{invocation}.cached")
        with acc.block():
            acc.statement(f"_bolt_runtime.memo.restore(_bolt_runtime, {invocation})")
            if cached_identifiers:
                acc.statement(f"({cached_identifiers}) = {invocation}.bindings")

        acc.statement("else")
        with acc.block():
            acc.statement(
                "with",
                f"_bolt_runtime.memo.record(_bolt_runtime, {invocation}, {path}, __name__)",
            )
            with acc.block():
                yield from visit_body(cast(AstRoot, body), acc)
            if cached_identifiers:
                acc.statement(f"{invocation}.bindings = ({cached_identifiers})")

        return []

    @rule(AstCommand, identifier="def:function:body")
    def function(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        signature = cast(AstFunctionSignature, node.arguments[0])
        body = cast(AstRoot, node.arguments[1])

        decorators: List[str] = []
        for decorator in signature.decorators:
            value = yield from visit_single(decorator.expression, required=True)
            decorators.append(value)

        arguments: List[str] = []
        for arg in signature.arguments:
            if isinstance(arg, AstFunctionSignatureArgument):
                a = arg.name
                if arg.type_annotation:
                    a = f"{a}: {arg.type_annotation.string}"
                if arg.default:
                    padding = " " * bool(arg.type_annotation)
                    a = f"{a}{padding}={padding}{acc.missing()}"
                arguments.append(a)
                f"{arg.name}={acc.missing()}" if arg.default else arg.name
            elif isinstance(arg, AstFunctionSignaturePositionalMarker):
                arguments.append("/")
            elif isinstance(arg, AstFunctionSignatureVariadicArgument):
                a = f"*{arg.name}"
                if arg.type_annotation:
                    a = f"{a}: {arg.type_annotation.string}"
                arguments.append(a)
            elif isinstance(arg, AstFunctionSignatureVariadicMarker):
                arguments.append("*")
            elif isinstance(arg, AstFunctionSignatureVariadicKeywordArgument):
                a = f"**{arg.name}"
                if arg.type_annotation:
                    a = f"{a}: {arg.type_annotation.string}"
                arguments.append(a)

        return_type = ""
        if signature.return_type_annotation:
            return_type = signature.return_type_annotation.string

        with acc.function(signature.name, *arguments, return_type=return_type):
            if body.commands and isinstance(body.commands[0], AstDocstring):
                yield body.commands[0]
                body = replace(body, commands=AstChildren(body.commands[1:]))

            for arg in signature.arguments:
                if isinstance(arg, AstFunctionSignatureArgument) and arg.default:
                    acc.statement("if", f"{arg.name} is {acc.missing()}")
                    with acc.block():
                        value = yield from visit_single(arg.default, required=True)
                        acc.statement(f"{arg.name} = {value}")

            yield from visit_body(body, acc)

        for decorator, value in list(zip(signature.decorators, decorators))[::-1]:
            acc.statement(
                f"{signature.name} = {value}({signature.name})",
                lineno=decorator,
            )

        return []

    @rule(AstCommand, identifier="return")
    @rule(AstCommand, identifier="return:pythonresult")
    def return_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        statement = "return"
        if node.arguments:
            value = yield from visit_single(node.arguments[0], required=True)
            statement += f" {value}"
        acc.statement(statement)
        return []

    @rule(AstCommand, identifier="yield")
    @rule(AstCommand, identifier="yield:value")
    @rule(AstCommand, identifier="yield:from:value")
    def yield_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        statement = "yield from" if node.identifier == "yield:from:value" else "yield"
        if node.arguments:
            value = yield from visit_single(node.arguments[0], required=True)
            statement += f" {value}"
        acc.statement(statement)
        return []

    @rule(AstMacro)
    def macro(
        self,
        node: AstMacro,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        macro = acc.make_macro(
            replace(node, arguments=AstChildren(node.arguments[:-1]))
        )
        arguments = [
            arg.match_identifier.value
            for arg in node.arguments
            if isinstance(arg, AstMacroMatchArgument)
        ]

        with acc.function(macro, *arguments):
            yield from visit_body(cast(AstRoot, node.arguments[-1]), acc)

        return []

    @rule(AstMacroCall)
    def macro_call(
        self,
        node: AstMacroCall,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        macro = acc.get_macro(node.identifier)
        result = yield from visit_generic(node, acc)
        if result is None:
            result = acc.make_ref(node)

        macro_call = acc.helper("macro_call", "_bolt_runtime", macro, result)
        result = acc.make_variable()
        acc.statement(f"{result} = {macro_call}", lineno=node)

        return [f"*{result}"]

    @rule(AstProcMacro)
    def proc_macro(
        self,
        node: AstProcMacro,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        macro = acc.make_macro(
            replace(node, arguments=AstChildren(node.arguments[:-1]))
        )

        with acc.function(macro, "stream"):
            yield from visit_body(cast(AstRoot, node.arguments[-1]), acc)

        if acc.root_scope:
            acc.header["_bolt_proc_macros"] = "{}"
            acc.statement(f"_bolt_proc_macros[{node.identifier!r}] = {macro}")

        return []

    @rule(AstCommand, identifier="class:name:bases:body")
    @rule(AstCommand, identifier="class:name:body")
    def class_definition(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        name = cast(AstClassName, node.arguments[0])
        body = cast(AstRoot, node.arguments[-1])

        decorators: List[str] = []
        for decorator in name.decorators:
            value = yield from visit_single(decorator.expression, required=True)
            decorators.append(value)

        class_args: List[str] = []

        if isinstance(bases := node.arguments[1], AstClassBases):
            for base in bases.inherit:
                result = yield from visit_single(base, required=True)
                class_args.append(result)
            for kwarg in bases.kwargs:
                result = yield from visit_single(kwarg, required=True)
                class_args.append(result)

        joined_args = f"({', '.join(class_args)})" if class_args else ""
        acc.statement(f"class {name.value}{joined_args}", lineno=node)

        with acc.block():
            temp_start = acc.counter
            yield from visit_body(body, acc)
            temp_stop = acc.counter

            for i in range(temp_start, temp_stop):
                acc.statement(f"del __bolt_var{i}")

            acc.counter = temp_start

        for decorator, value in list(zip(name.decorators, decorators))[::-1]:
            acc.statement(
                f"{name.value} = {value}({name.value})",
                lineno=decorator,
            )

        return []

    @rule(AstDocstring)
    def docstring(
        self,
        node: AstDocstring,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        acc.statement(repr(cast(AstValue, node.arguments[0]).value))
        return []

    @rule(AstCommand, identifier="del:target")
    def del_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        targets = yield node.arguments[0]
        for target in targets or []:
            acc.statement(f"del {target}")
        return []

    @rule(AstCommand, identifier="if:condition:body")
    def if_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        condition = yield from visit_single(node.arguments[0], required=True)
        inverse = None

        else_index = acc.current_sibling_index + 1
        if (
            else_index < len(acc.current_siblings)
            and isinstance(else_node := acc.current_siblings[else_index], AstCommand)
            and else_node.identifier == "else:body"
        ):
            inverse = f"{condition}_inverse"
            value = acc.helper("operator_not", condition)
            acc.statement(f"{inverse} = {value}", lineno=node.arguments[0])

        with acc.if_statement(condition, inverse, lineno=node):
            yield from visit_body(cast(AstRoot, node.arguments[1]), acc)
        return []

    @rule(AstCommand, identifier="else:body")
    def else_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        with acc.else_statement(lineno=node):
            yield from visit_body(cast(AstRoot, node.arguments[0]), acc)
        return []

    @rule(AstCommand, identifier="while:condition:body")
    def while_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        acc.statement("while True", lineno=node)
        with acc.block():
            acc.statement(
                "with", "_bolt_runtime.scope()", "as", "_bolt_condition_commands"
            )
            with acc.block():
                condition = yield from visit_single(node.arguments[0], required=True)

            again = acc.make_variable()
            loop = acc.helper("loop", condition)
            acc.statement(
                "with",
                loop,
                "as",
                f"(_bolt_loop_overridden, {again})",
                lineno=node.arguments[0],
            )
            with acc.block():
                acc.statement("_bolt_runtime.commands.extend(_bolt_condition_commands)")

                acc.statement(
                    "if", "not _bolt_loop_overridden", lineno=node.arguments[0]
                )
                with acc.block():
                    acc.statement(f"{condition} = bool({condition})")

                with acc.if_statement(condition, lineno=node.arguments[0]):
                    yield from visit_body(cast(AstRoot, node.arguments[1]), acc)

                    acc.statement("if", again, lineno=node.arguments[0])
                    with acc.block():
                        acc.statement("continue")

            acc.statement("break")

        return []

    @rule(AstCommand, identifier="for:target:in:iterable:body")
    def for_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        iterable = yield from visit_single(node.arguments[1], required=True)
        targets = yield node.arguments[0]
        acc.statement(f"for {', '.join(targets or ['_'])} in {iterable}")
        with acc.block():
            yield from visit_body(cast(AstRoot, node.arguments[2]), acc)
        return []

    @rule(AstCommand, identifier="break")
    def break_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        acc.statement("break")
        return []

    @rule(AstCommand, identifier="continue")
    def continue_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        acc.statement("continue")
        return []

    @rule(AstCommand, identifier="with:context:body")
    def with_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        context = cast(AstWithContext, node.arguments[0])
        body = cast(AstRoot, node.arguments[1])

        with ExitStack() as exit_stack:
            for clause in context.clauses:
                value = yield from visit_single(clause.value, required=True)

                if clause.target:
                    acc.statement("with", value, "as", "_bolt_with", lineno=clause)
                    exit_stack.enter_context(acc.block())
                    yield from visit_binding(clause.target, "=", "_bolt_with", acc)
                else:
                    acc.statement("with", value, lineno=clause)
                    exit_stack.enter_context(acc.block())

            yield from visit_body(body, acc)

        return []

    @rule(AstCommand, identifier="import:module")
    @rule(AstCommand, identifier="import:module:as:alias")
    def import_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        module = cast(AstResourceLocation, node.arguments[0])

        if node.identifier == "import:module:as:alias":
            alias = cast(AstImportedItem, node.arguments[1]).name

            if module.namespace:
                full_path = module.get_value()
                acc.statement(
                    f"{alias} = _bolt_runtime.import_module({full_path!r}).namespace",
                    lineno=node,
                )
                acc.dependencies.add(full_path)
            else:
                rhs = acc.import_module(module.path)
                acc.statement(f"{alias} = {rhs}", lineno=node)

        else:
            name = module.path.partition(".")[0]
            rhs = acc.import_module(module.path)
            if name == module.path:
                acc.statement(f"{name} = {rhs}", lineno=node)
            else:
                acc.statement(rhs, lineno=node)
                acc.statement(f"{name} = {acc.import_module(name)}")

        return []

    @rule(AstFromImport)
    def from_import_statement(
        self,
        node: AstFromImport,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        if isinstance(node, AstPrelude):
            acc.prelude_imports.append(node)

        module = cast(AstResourceLocation, node.arguments[0])
        items = cast(
            AstChildren[Union[AstImportedItem, AstImportedMacro]], node.arguments[1:]
        )
        names = [item.name for item in items]

        if module.namespace:
            full_path = module.get_value()
            targets: List[str] = []
            for item in items:
                if isinstance(item, AstImportedMacro):
                    targets.append(acc.import_macro(full_path, item))
                else:
                    targets.append(item.name)
            stmt = f"{', '.join(targets)} = _bolt_runtime.from_module_import({full_path!r}, {', '.join(map(repr, names))})"
            acc.statement(stmt, lineno=node)
            acc.dependencies.add(full_path)
        else:
            stmt = f"_bolt_from_import = {acc.import_module(module.path)}"
            acc.statement(stmt, lineno=node)
            for name in names:
                rhs = acc.get_attribute_handler("_bolt_from_import", name)
                acc.statement(f"{name} = {rhs}", lineno=node)

        return []

    @rule(AstCommand, identifier="global:subcommand")
    @rule(AstCommand, identifier="nonlocal:subcommand")
    def global_nonlocal_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        storage, _, _ = node.identifier.partition(":")

        names: List[str] = []
        subcommand = cast(AstCommand, node.arguments[0])

        while True:
            if isinstance(name := subcommand.arguments[0], AstIdentifier):
                names.append(name.value)
            if subcommand.identifier == f"{storage}:name:subcommand":
                subcommand = cast(AstCommand, subcommand.arguments[1])
            else:
                break

        acc.statement(f"{storage} {', '.join(names)}", lineno=node)

        return []

    @rule(AstInterpolation)
    def interpolation(
        self,
        node: AstInterpolation,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_single(node.value, required=True)
        value = "f" + repr(node.prefix + "{" + result + "}") if node.prefix else result

        if node.unpack == "**":
            value = f"{{**{value}}}"
        elif node.unpack == "*":
            value = f"[*{value}]"

        rhs = acc.helper(f"interpolate_{node.converter}", value, acc.make_ref(node))
        acc.statement(f"{result} = {rhs}", lineno=node)

        if node.unpack:
            result = f"*{result}"

        return [result]

    @rule(AstExpressionBinary)
    def binary(
        self,
        node: AstExpressionBinary,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        left = yield from visit_single(node.left, required=True)
        right = yield from visit_single(node.right, required=True)
        acc.binary(left, node.operator, right, lineno=node)
        return [left]

    @rule(AstExpressionBinary, operator="and")
    @rule(AstExpressionBinary, operator="or")
    def binary_logical(
        self,
        node: AstExpressionBinary,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        left = yield from visit_single(node.left, required=True)

        condition = acc.make_variable()
        value = acc.helper("operator_not", left) if node.operator == "or" else left
        acc.statement(f"{condition} = {value}", lineno=node.left)

        dup = acc.dup(left, lineno=node)

        with acc.if_statement(condition, lineno=node):
            right = yield from visit_single(node.right, required=True)
            acc.rebind_dup(left, dup, right, lineno=node.right)

        return [left]

    @rule(AstExpressionUnary)
    def unary(
        self,
        node: AstExpressionUnary,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_single(node.value, required=True)
        if node.operator in ["not"]:
            value = acc.helper(f"operator_{node.operator}", result)
            acc.statement(f"{result} = {value}", lineno=node)
        else:
            op = node.operator.replace("_", " ")
            acc.statement(f"{result} = {op} {result}", lineno=node)
        return [result]

    @rule(AstChainedComparison)
    def chained_comparison(
        self,
        node: AstChainedComparison,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        left = yield from visit_single(node.operands[0], required=True)
        right = yield from visit_single(node.operands[1], required=True)
        acc.binary(left, node.operators[0], right, lineno=node)

        condition = acc.make_variable()

        for op, operand in zip(node.operators[1:], node.operands[2:]):
            acc.statement(f"{condition} = {left}")

            dup = acc.dup(left, lineno=node)

            with acc.if_statement(condition, lineno=node):
                current = right
                right = yield from visit_single(operand, required=True)
                acc.binary(current, op, right, lineno=node)
                acc.rebind_dup(left, dup, current, lineno=operand)

        return [left]

    @rule(AstValue)
    def value(self, node: AstValue, acc: Accumulator) -> Optional[List[str]]:
        result = acc.make_variable()
        acc.statement(f"{result} = {node.literal}")
        return [result]

    @rule(AstIdentifier)
    def identifier(self, node: AstIdentifier, acc: Accumulator) -> Optional[List[str]]:
        result = acc.make_variable()
        acc.statement(f"{result} = {node.value}", lineno=node)
        return [result]

    @rule(AstFormatString)
    def format_string(
        self,
        node: AstFormatString,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        values: List[str] = []

        for value in node.values:
            result = yield from visit_single(value, required=True)
            values.append(result)

        result = acc.make_variable()
        acc.statement(
            f"{result} = {node.fmt!r}.format({', '.join(values)})", lineno=node
        )
        return [result]

    @rule(AstFormattedLocation)
    def formatted_location(
        self,
        node: AstFormattedLocation,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        values: List[str] = []

        for value in node.values:
            result = yield from visit_single(value, required=True)
            values.append(result)

        result = acc.make_variable()
        resolved = acc.helper(
            "resolve_formatted_location",
            "_bolt_runtime",
            f"{node.fmt!r}.format({', '.join(values)})" if values else repr(node.fmt),
        )
        acc.statement(f"{result} = {resolved}", lineno=node)
        return [result]

    @rule(AstTuple)
    def tuple(
        self,
        node: AstTuple,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        items: List[str] = []

        for item in node.items:
            value = yield from visit_single(item, required=True)
            items.append(f"{value},")

        result = acc.make_variable()
        acc.statement(f"{result} = ({''.join(items)})", lineno=node)
        return [result]

    @rule(AstList)
    def list(
        self,
        node: AstList,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        items: List[str] = []

        for item in node.items:
            value = yield from visit_single(item, required=True)
            items.append(value)

        result = acc.make_variable()
        acc.statement(f"{result} = [{', '.join(items)}]", lineno=node)
        return [result]

    @rule(AstDict)
    def dict(
        self,
        node: AstDict,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        items: List[str] = []

        for item in node.items:
            value = yield from visit_single(item, required=True)
            items.append(value)

        result = acc.make_variable()
        acc.statement(f"{result} = {{{', '.join(items)}}}", lineno=node)
        return [result]

    @rule(AstDictItem)
    def dict_item(
        self,
        node: AstDictItem,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        key = yield from visit_single(node.key, required=True)
        value = yield from visit_single(node.value, required=True)
        return [f"{key}: {value}"]

    @rule(AstSlice)
    def slice(
        self,
        node: AstSlice,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        start = ""
        stop = ""
        step = ""

        if node.start:
            start = yield from visit_single(node.start, required=True)
        if node.stop:
            stop = yield from visit_single(node.stop, required=True)
        if node.step:
            step = yield from visit_single(node.step, required=True)

        result = f"{start}:{stop}"
        if step:
            result += f":{step}"

        return [result]

    @rule(AstUnpack)
    def unpack(
        self,
        node: AstUnpack,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        value = yield from visit_single(node.value, required=True)
        prefix = "**" if node.type == "dict" else "*"
        return [f"{prefix}{value}"]

    @rule(AstKeyword)
    def keyword(
        self,
        node: AstKeyword,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        value = yield from visit_single(node.value, required=True)
        return [f"{node.name}={value}"]

    @rule(AstAttribute)
    def attribute(
        self,
        node: AstAttribute,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        value = yield from visit_single(node.value, required=True)
        rhs = acc.get_attribute_handler(value, node.name)
        acc.statement(f"{value} = {rhs}", lineno=node)
        return [value]

    @rule(AstLookup)
    def lookup(
        self,
        node: AstLookup,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_single(node.value, required=True)
        arguments: List[str] = []

        for arg in node.arguments:
            value = yield from visit_single(arg, required=True)
            arguments.append(value)

        acc.statement(f"{result} = {result}[{', '.join(arguments)}]", lineno=node)
        return [result]

    @rule(AstCall)
    def call(
        self,
        node: AstCall,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_single(node.value, required=True)
        arguments: List[str] = []

        for arg in node.arguments:
            value = yield from visit_single(arg, required=True)
            arguments.append(value)

        acc.statement(f"{result} = {result}({', '.join(arguments)})", lineno=node)
        return [result]

    @rule(AstAssignment)
    def assignment(
        self,
        node: AstAssignment,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        if node.type_annotation and isinstance(node.target, AstTargetIdentifier):
            value = node.type_annotation.string
            acc.statement(f"{node.target.value}: {value}")
        value = yield from visit_single(node.value, required=True)
        yield from visit_binding(node.target, node.operator, value, acc)
        return []

    @rule(AstTypeDeclaration)
    def type_declaration(
        self,
        node: AstTypeDeclaration,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        value = node.type_annotation.string
        acc.statement(f"{node.identifier.value}: {value}")
        return []

    @rule(AstTargetIdentifier)
    def target_identifier(
        self,
        node: AstTargetIdentifier,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        return [node.value]

    @rule(AstTargetUnpack)
    def target_destructure(
        self,
        node: AstTargetUnpack,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        targets: List[str] = []
        for target in node.targets:
            result = yield from visit_single(target, required=True)
            targets.append(result)
        return targets

    @rule(AstTargetAttribute)
    def target_attribute(
        self,
        node: AstTargetAttribute,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        value = yield from visit_single(node.value, required=True)
        target = acc.get_attribute_handler(value, node.name)
        return [target]

    @rule(AstTargetItem)
    def target_item(
        self,
        node: AstTargetItem,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_single(node.value, required=True)
        arguments: List[str] = []

        for arg in node.arguments:
            value = yield from visit_single(arg, required=True)
            arguments.append(value)

        return [f"{result}[{', '.join(arguments)}]"]

    @rule(AstCommand, identifier="pass")
    def pass_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        acc.statement("pass")
        return []

    @rule(AstCommand, identifier="raise")
    def raise_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Optional[List[str]]:
        acc.statement("raise")
        return []

    @rule(AstCommand, identifier="raise:exception")
    def raise_exc_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_single(node.arguments[0], required=True)
        acc.statement(f"raise {result}")
        return []

    @rule(AstCommand, identifier="raise:exception:from:cause")
    def raise_exc_from_statement(
        self,
        node: AstCommand,
        acc: Accumulator,
    ) -> Generator[AstNode, Optional[List[str]], Optional[List[str]]]:
        result = yield from visit_single(node.arguments[0], required=True)
        cause = yield from visit_single(node.arguments[1], required=True)
        acc.statement(f"raise {result} from {cause}")
        return []
