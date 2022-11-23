__all__ = [
    "get_bolt_parsers",
    "get_stream_builtins",
    "get_stream_identifiers",
    "get_stream_pending_identifiers",
    "get_stream_identifiers_storage",
    "get_stream_pending_identifiers_storage",
    "get_stream_deferred_locals",
    "get_stream_branch_scope",
    "get_stream_macro_scope",
    "get_stream_pending_macros",
    "ToplevelHandler",
    "create_bolt_root_parser",
    "UndefinedIdentifier",
    "UndefinedIdentifierErrorHandler",
    "BranchScopeManager",
    "check_final_expression",
    "FinalExpressionParser",
    "InterpolationParser",
    "DisableInterpolationParser",
    "parse_statement",
    "parse_decorator",
    "AssignmentTargetParser",
    "IfElseLoweringParser",
    "BreakContinueConstraint",
    "FlushPendingIdentifiersParser",
    "parse_deferred_root",
    "parse_function_signature",
    "parse_proc_macro_signature",
    "MacroMatchParser",
    "MacroHandler",
    "ProcMacroParser",
    "ProcMacroExpansion",
    "parse_class_name",
    "parse_class_bases",
    "parse_class_root",
    "ClassBodyScoping",
    "parse_del_target",
    "parse_identifier",
    "TrailingCommaParser",
    "ImportLocationConstraint",
    "ImportStatementHandler",
    "parse_python_import",
    "parse_import_name",
    "parse_name_list",
    "GlobalNonlocalHandler",
    "StatementSubcommandHandler",
    "DeferredRootBacktracker",
    "FunctionConstraint",
    "RootScopeHandler",
    "BinaryParser",
    "UnaryParser",
    "UnpackParser",
    "UnpackConstraint",
    "KeywordParser",
    "LookupParser",
    "PrimaryParser",
    "BuiltinCallRestriction",
    "parse_dict_item",
    "LiteralParser",
]


import re
from dataclasses import dataclass, field, replace
from typing import Any, Dict, FrozenSet, Iterable, List, Optional, Set, Tuple, cast

from beet.core.utils import extra_field
from mecha import (
    AdjacentConstraint,
    AlternativeParser,
    AstChildren,
    AstCommand,
    AstJson,
    AstNode,
    AstResourceLocation,
    AstRoot,
    BasicLiteralParser,
    CommandSpec,
    CommandTree,
    CommentDisambiguation,
    CompilationDatabase,
    MultilineParser,
    Parser,
    consume_line_continuation,
    delegate,
    get_stream_properties,
    get_stream_scope,
    get_stream_spec,
)
from mecha.contrib.relative_location import resolve_using_database
from mecha.utils import (
    JsonQuoteHelper,
    QuoteHelper,
    normalize_whitespace,
    string_to_number,
)
from tokenstream import InvalidSyntax, Token, TokenStream, set_location

from .ast import (
    AstAssignment,
    AstAttribute,
    AstCall,
    AstClassBases,
    AstClassName,
    AstClassRoot,
    AstDecorator,
    AstDeferredRoot,
    AstDict,
    AstDictItem,
    AstDictUnquotedKey,
    AstExpression,
    AstExpressionBinary,
    AstExpressionUnary,
    AstFormatString,
    AstFromImport,
    AstFunctionSignature,
    AstFunctionSignatureArgument,
    AstFunctionSignatureElement,
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
    AstMacroArgument,
    AstMacroCall,
    AstMacroLiteral,
    AstMacroMatch,
    AstMacroMatchArgument,
    AstMacroMatchLiteral,
    AstModuleRoot,
    AstProcMacro,
    AstProcMacroMarker,
    AstProcMacroResult,
    AstSlice,
    AstTarget,
    AstTargetAttribute,
    AstTargetIdentifier,
    AstTargetItem,
    AstTargetUnpack,
    AstTuple,
    AstUnpack,
    AstValue,
)
from .collect import CommandCollector
from .module import Module, ModuleManager, UnusableCompilationUnit
from .pattern import (
    FALSE_PATTERN,
    IDENTIFIER_PATTERN,
    MODULE_PATTERN,
    NULL_PATTERN,
    NUMBER_PATTERN,
    RESOURCE_LOCATION_PATTERN,
    STRING_PATTERN,
    TRUE_PATTERN,
)
from .utils import internal, suggest_typo

IMPORT_REGEX = re.compile(rf"^{MODULE_PATTERN}$")


def get_bolt_parsers(
    parsers: Dict[str, Parser], modules: ModuleManager
) -> Dict[str, Parser]:
    """Return the bolt parsers."""
    macro_handler = MacroHandler(
        parser=parsers["command"],
        proc_macro_overloads=(
            modules.cache.json.setdefault("proc_macro_overloads", {})
            if modules.cache
            else {}
        ),
    )

    return {
        ################################################################################
        # Command
        ################################################################################
        "root": ToplevelHandler(
            parser=create_bolt_root_parser(parsers["root"], macro_handler),
            modules=modules,
            macro_handler=macro_handler,
        ),
        "nested_root": create_bolt_root_parser(parsers["nested_root"], macro_handler),
        "command": StatementSubcommandHandler(
            UndefinedIdentifierErrorHandler(
                ImportStatementHandler(GlobalNonlocalHandler(macro_handler), modules)
            )
        ),
        "command:argument:bolt:if_block": delegate("bolt:if_block"),
        "command:argument:bolt:elif_condition": delegate("bolt:elif_condition"),
        "command:argument:bolt:elif_block": delegate("bolt:elif_block"),
        "command:argument:bolt:else_block": delegate("bolt:else_block"),
        "command:argument:bolt:statement": delegate("bolt:statement"),
        "command:argument:bolt:assignment_target": delegate("bolt:assignment_target"),
        "command:argument:bolt:with_expression": delegate("bolt:with_expression"),
        "command:argument:bolt:with_target": delegate("bolt:with_target"),
        "command:argument:bolt:import": delegate("bolt:import"),
        "command:argument:bolt:import_name": delegate("bolt:import_name"),
        "command:argument:bolt:global_name": delegate("bolt:global_name"),
        "command:argument:bolt:nonlocal_name": delegate("bolt:nonlocal_name"),
        "command:argument:bolt:expression": delegate("bolt:expression"),
        "command:argument:bolt:deferred_root": delegate("bolt:deferred_root"),
        "command:argument:bolt:function_signature": delegate("bolt:function_signature"),
        "command:argument:bolt:macro_name": delegate("bolt:macro_name"),
        "command:argument:bolt:macro_signature": delegate("bolt:macro_signature"),
        "command:argument:bolt:macro_match": delegate("bolt:macro_match"),
        "command:argument:bolt:proc_macro": delegate("bolt:proc_macro"),
        "command:argument:bolt:class_name": delegate("bolt:class_name"),
        "command:argument:bolt:class_bases": delegate("bolt:class_bases"),
        "command:argument:bolt:class_root": delegate("bolt:class_root"),
        "command:argument:bolt:del_target": delegate("bolt:del_target"),
        ################################################################################
        # Bolt
        ################################################################################
        "bolt:if_block": BranchScopeManager(
            parser=delegate("nested_root"),
            update_before=True,
        ),
        "bolt:elif_condition": BranchScopeManager(
            parser=delegate("bolt:expression"),
            mask=True,
            update_after=True,
        ),
        "bolt:elif_block": BranchScopeManager(
            parser=delegate("nested_root"),
            mask=True,
        ),
        "bolt:else_block": BranchScopeManager(
            parser=delegate("nested_root"),
            mask=True,
        ),
        "bolt:statement": parse_statement,
        "bolt:decorator": parse_decorator,
        "bolt:assignment_target": AssignmentTargetParser(
            allow_undefined_identifiers=True,
            allow_multiple=True,
        ),
        "bolt:augmented_assignment_target": AssignmentTargetParser(),
        "bolt:deferred_root": parse_deferred_root,
        "bolt:function_signature": parse_function_signature,
        "bolt_macro_literal": delegate("bolt:macro_literal"),
        "bolt:macro_literal": BasicLiteralParser(AstMacroLiteral),
        "bolt_macro_argument": delegate("bolt:macro_argument"),
        "bolt:macro_argument": BasicLiteralParser(AstMacroArgument),
        "bolt:macro_name": delegate("bolt:macro_literal"),
        "bolt:macro_signature": parse_proc_macro_signature,
        "bolt:macro_match": MacroMatchParser(
            literal_parser=delegate("bolt:macro_literal"),
            argument_parser=delegate("bolt:macro_argument"),
            resource_location_parser=DisableInterpolationParser(
                delegate("resource_location")
            ),
            json_properties_parser=DisableInterpolationParser(
                AdjacentConstraint(MultilineParser(delegate("json_object")), r"\{")
            ),
        ),
        "bolt:proc_macro": ProcMacroParser(modules),
        "bolt:class_name": parse_class_name,
        "bolt:class_bases": parse_class_bases,
        "bolt:class_root": parse_class_root,
        "bolt:del_target": parse_del_target,
        "bolt:interpolation": BuiltinCallRestriction(
            PrimaryParser(delegate("bolt:identifier"), truncate=True)
        ),
        "bolt:identifier": parse_identifier,
        "bolt:with_expression": TrailingCommaParser(delegate("bolt:expression")),
        "bolt:with_target": TrailingCommaParser(
            AssignmentTargetParser(allow_undefined_identifiers=True)
        ),
        "bolt:import": AlternativeParser(
            [
                ImportLocationConstraint(
                    DisableInterpolationParser(delegate("resource_location_or_tag"))
                ),
                parse_python_import,
            ]
        ),
        "bolt:import_name": TrailingCommaParser(parse_import_name),
        "bolt:global_name": parse_name_list,
        "bolt:nonlocal_name": parse_name_list,
        "bolt:expression": delegate("bolt:disjunction"),
        "bolt:disjunction": BinaryParser(
            operators=[r"\bor\b"],
            parser=delegate("bolt:conjunction"),
        ),
        "bolt:conjunction": BinaryParser(
            operators=[r"\band\b"],
            parser=delegate("bolt:inversion"),
        ),
        "bolt:inversion": UnaryParser(
            operators=[r"\bnot\b"],
            parser=delegate("bolt:comparison"),
        ),
        "bolt:comparison": BinaryParser(
            operators=[
                "==",
                "!=",
                "<=",
                "<",
                ">=",
                ">",
                r"\bnot\s+in\b",
                r"\bin\b",
                r"\bis\s+not\b",
                r"\bis\b",
            ],
            parser=delegate("bolt:bitwise_or"),
        ),
        "bolt:bitwise_or": BinaryParser(
            operators=[r"\|(?!=)"],
            parser=delegate("bolt:bitwise_xor"),
        ),
        "bolt:bitwise_xor": BinaryParser(
            operators=[r"\^(?!=)"],
            parser=delegate("bolt:bitwise_and"),
        ),
        "bolt:bitwise_and": BinaryParser(
            operators=[r"&(?!=)"],
            parser=delegate("bolt:shift_expr"),
        ),
        "bolt:shift_expr": BinaryParser(
            operators=[r"<<(?!=)", r">>(?!=)"],
            parser=delegate("bolt:sum"),
        ),
        "bolt:sum": BinaryParser(
            operators=[r"\+(?!=)", r"-(?!=)"],
            parser=delegate("bolt:term"),
        ),
        "bolt:term": BinaryParser(
            operators=[r"\*(?!=)", r"//(?!=)", r"/(?!=)", r"%(?!=)"],
            parser=delegate("bolt:factor"),
        ),
        "bolt:factor": UnaryParser(
            operators=[r"\+", "-"],
            parser=delegate("bolt:power"),
        ),
        "bolt:power": BinaryParser(
            operators=[r"\*\*(?!=)"],
            parser=delegate("bolt:primary"),
            right_associative=True,
        ),
        "bolt:lookup_argument": LookupParser(delegate("bolt:expression")),
        "bolt:call_argument": AlternativeParser(
            [
                KeywordParser(delegate("bolt:expression")),
                UnpackParser(delegate("bolt:expression")),
                delegate("bolt:expression"),
            ]
        ),
        "bolt:primary": PrimaryParser(delegate("bolt:atom")),
        "bolt:atom": AlternativeParser(
            [
                delegate("bolt:identifier"),
                delegate("bolt:literal"),
            ]
        ),
        "bolt:list_item": AlternativeParser(
            [
                UnpackConstraint(
                    type="list",
                    parser=UnpackParser(delegate("bolt:expression")),
                ),
                delegate("bolt:expression"),
            ]
        ),
        "bolt:dict_item": AlternativeParser(
            [
                UnpackConstraint(
                    type="dict",
                    parser=UnpackParser(delegate("bolt:expression")),
                ),
                parse_dict_item,
            ]
        ),
        "bolt:literal": LiteralParser(modules.database),
        ################################################################################
        # Interpolation
        ################################################################################
        "bool": AlternativeParser([parsers["bool"], InterpolationParser("bool")]),
        "numeric": AlternativeParser(
            [parsers["numeric"], InterpolationParser("numeric", prefix="-")]
        ),
        "coordinate": AlternativeParser(
            [
                parsers["coordinate"],
                InterpolationParser("coordinate", prefix="[~^]-?|-"),
            ]
        ),
        "time": AlternativeParser([parsers["time"], InterpolationParser("time")]),
        "word": AlternativeParser([InterpolationParser("word"), parsers["word"]]),
        "phrase": AlternativeParser([InterpolationParser("phrase"), parsers["phrase"]]),
        "greedy": AlternativeParser([InterpolationParser("greedy"), parsers["greedy"]]),
        "json": AlternativeParser([InterpolationParser("json"), parsers["json"]]),
        "json_object_entry": AlternativeParser(
            [InterpolationParser("json", unpack=r"\*\*"), parsers["json_object_entry"]]
        ),
        "json_array_element": AlternativeParser(
            [InterpolationParser("json", unpack=r"\*"), parsers["json_array_element"]]
        ),
        "json_object": AlternativeParser(
            [InterpolationParser("json_object"), parsers["json_object"]]
        ),
        "nbt": AlternativeParser([InterpolationParser("nbt"), parsers["nbt"]]),
        "nbt_compound_entry": AlternativeParser(
            [InterpolationParser("nbt", unpack=r"\*\*"), parsers["nbt_compound_entry"]]
        ),
        "nbt_list_or_array_element": AlternativeParser(
            [
                InterpolationParser("nbt", unpack=r"\*"),
                parsers["nbt_list_or_array_element"],
            ]
        ),
        "nbt_compound": AlternativeParser(
            [InterpolationParser("nbt_compound"), parsers["nbt_compound"]]
        ),
        "nbt_path": AlternativeParser(
            [InterpolationParser("nbt_path"), parsers["nbt_path"]]
        ),
        "range": AlternativeParser([parsers["range"], InterpolationParser("range")]),
        "resource_location_or_tag": CommentDisambiguation(
            AlternativeParser(
                [
                    InterpolationParser("resource_location", prefix=r"#"),
                    parsers["resource_location_or_tag"],
                ]
            )
        ),
        "item_slot": AlternativeParser(
            [parsers["item_slot"], InterpolationParser("item_slot")]
        ),
        "uuid": AlternativeParser([InterpolationParser("uuid"), parsers["uuid"]]),
        "objective": AlternativeParser(
            [InterpolationParser("objective"), parsers["objective"]]
        ),
        "objective_criteria": AlternativeParser(
            [InterpolationParser("objective_criteria"), parsers["objective_criteria"]]
        ),
        "scoreboard_slot": AlternativeParser(
            [parsers["scoreboard_slot"], InterpolationParser("scoreboard_slot")]
        ),
        "swizzle": AlternativeParser(
            [parsers["swizzle"], InterpolationParser("swizzle")]
        ),
        "team": AlternativeParser([InterpolationParser("team"), parsers["team"]]),
        "advancement_predicate": AlternativeParser(
            [
                InterpolationParser("advancement_predicate"),
                parsers["advancement_predicate"],
            ]
        ),
        "color": AlternativeParser([InterpolationParser("color"), parsers["color"]]),
        "sort_order": AlternativeParser(
            [parsers["sort_order"], InterpolationParser("sort_order")]
        ),
        "gamemode": AlternativeParser(
            [parsers["gamemode"], InterpolationParser("gamemode")]
        ),
        "message": AlternativeParser(
            [FinalExpressionParser(InterpolationParser("message")), parsers["message"]]
        ),
        "block_pos": AlternativeParser(
            [parsers["block_pos"], InterpolationParser("vec3")]
        ),
        "column_pos": AlternativeParser(
            [parsers["column_pos"], InterpolationParser("vec2")]
        ),
        "rotation": AlternativeParser(
            [parsers["rotation"], InterpolationParser("vec2")]
        ),
        "vec2": AlternativeParser([parsers["vec2"], InterpolationParser("vec2")]),
        "vec3": AlternativeParser([parsers["vec3"], InterpolationParser("vec3")]),
        "entity": CommentDisambiguation(
            AlternativeParser([InterpolationParser("entity"), parsers["entity"]])
        ),
        "score_holder": CommentDisambiguation(
            AlternativeParser([InterpolationParser("entity"), parsers["score_holder"]])
        ),
        "game_profile": CommentDisambiguation(
            AlternativeParser([InterpolationParser("entity"), parsers["game_profile"]])
        ),
    }


def get_stream_builtins(stream: TokenStream) -> Set[str]:
    """Return the set of builtin identifiers currently associated with the token stream."""
    return stream.data.setdefault("builtins", set())


def get_stream_identifiers(stream: TokenStream) -> Set[str]:
    """Return the set of accessible identifiers currently associated with the token stream."""
    return stream.data.setdefault("identifiers", set())


def get_stream_pending_identifiers(stream: TokenStream) -> Set[str]:
    """Return the set of pending identifiers currently associated with the token stream."""
    return stream.data.setdefault("pending_identifiers", set())


def get_stream_identifiers_storage(stream: TokenStream) -> Dict[str, str]:
    """Return a dict that associates storage type to identifiers."""
    return stream.data.setdefault("identifiers_storage", {})


def get_stream_pending_identifiers_storage(stream: TokenStream) -> Dict[str, str]:
    """Return a dict that associates pending storage type to identifiers."""
    return stream.data.setdefault("pending_identifiers_storage", {})


def get_stream_deferred_locals(stream: TokenStream) -> Set[str]:
    """Return a set of identifiers that will be available in the next deferred root."""
    return stream.data.setdefault("deferred_locals", set())


def get_stream_branch_scope(stream: TokenStream) -> Set[str]:
    """Return the identifiers available inside the branch."""
    return stream.data.setdefault("branch_scope", set())


def get_stream_macro_scope(stream: TokenStream) -> Dict[str, AstMacro]:
    """Return the macro identifiers currently available."""
    return stream.data.setdefault("macro_scope", {})


def get_stream_pending_macros(stream: TokenStream) -> List[AstMacro]:
    """Return pending macro declarations."""
    return stream.data.setdefault("pending_macros", [])


def get_stream_class_scope(stream: TokenStream) -> Optional[Set[str]]:
    """Return the set of outer identifiers available inside the class."""
    return stream.data.get("class_scope")


@dataclass
class ToplevelHandler:
    """Handle toplevel root node."""

    parser: Parser

    modules: ModuleManager
    macro_handler: "MacroHandler"

    def __call__(self, stream: TokenStream) -> Any:
        current = self.modules.database.current

        with self.modules.parse_push(current), stream.provide(
            resource_location=self.modules.database[current].resource_location,
            builtins=self.modules.builtins,
            identifiers=set(self.modules.globals)
            | self.modules.builtins
            | {"__name__"},
        ):
            node = self.parser(stream)

        self.macro_handler.cache_local_spec(stream)

        if isinstance(node, AstRoot) and isinstance(current, Module):
            node = set_location(AstModuleRoot(commands=node.commands), node)

        return node


def create_bolt_root_parser(parser: Parser, macro_handler: "MacroHandler"):
    """Return parser for the root node for bolt."""
    parser = IfElseLoweringParser(parser)
    parser = BreakContinueConstraint(
        parser,
        allowed_scopes={
            ("while", "condition", "body"),
            ("for", "target", "in", "iterable", "body"),
        },
    )
    parser = FunctionConstraint(
        parser,
        command_identifiers={
            "return",
            "return:value",
            "yield",
            "yield:value",
            "yield:from:value",
            "global:subcommand",
            "nonlocal:subcommand",
        },
    )
    parser = FlushPendingIdentifiersParser(parser)
    parser = ClassBodyScoping(parser)
    parser = DeferredRootBacktracker(parser, macro_handler=macro_handler)
    parser = DecoratorResolver(parser)
    parser = ProcMacroExpansion(parser)
    parser = RootScopeHandler(parser)
    return parser


class UndefinedIdentifier(InvalidSyntax):
    """Raised when an identifier is not defined."""

    identifier: str
    possible_identifiers: Iterable[str]

    def __init__(self, identifier: str, identifiers: Iterable[str]):
        super().__init__(identifier, identifiers)
        self.identifier = identifier
        self.identifiers = identifiers

    def __str__(self) -> str:
        msg = f'Identifier "{self.identifier}" is not defined.'
        if suggestion := suggest_typo(self.identifier, self.identifiers):
            msg += f" Did you mean {suggestion}?"
        return msg


@dataclass
class UndefinedIdentifierErrorHandler:
    """Parser that provides hints for errors involving undefined identifiers."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        try:
            return self.parser(stream)
        except UndefinedIdentifier:
            raise
        except InvalidSyntax as exc:
            for alt in exc.alternatives.get(UndefinedIdentifier, []):
                if alt.end_location.pos + 1 >= exc.location.pos:  # kind of a cheat
                    alt.notes.append(str(exc))
                    raise alt from None
            raise


@dataclass
class BranchScopeManager:
    """Parser that manages accessible identifiers for conditional branches."""

    parser: Parser
    mask: bool = False
    update_before: bool = False
    update_after: bool = False

    def __call__(self, stream: TokenStream) -> Any:
        identifiers = get_stream_identifiers(stream)
        identifiers_storage = get_stream_identifiers_storage(stream)
        branch_scope = get_stream_branch_scope(stream)

        mask = branch_scope and identifiers - branch_scope
        mask_storage = {
            identifier: identifiers_storage[identifier]
            for identifier in set(identifiers_storage) & mask
        }

        if self.mask:
            identifiers -= mask
            for identifier in mask_storage:
                del identifiers_storage[identifier]

        if self.update_before:
            branch_scope = identifiers.copy()

        try:
            return self.parser(stream)
        finally:
            if self.update_after:
                branch_scope = identifiers.copy()

            if self.mask:
                identifiers.update(mask)
                identifiers_storage.update(mask_storage)

            stream.data["branch_scope"] = branch_scope


def check_final_expression(stream: TokenStream):
    current_index = stream.index

    if consume_line_continuation(stream):
        exc = InvalidSyntax("Invalid indent following final expression.")
        raise set_location(exc, stream.get())

    next_token = stream.get()
    if next_token and not next_token.match("newline", "eof"):
        exc = InvalidSyntax("Trailing input following final expression.")
        raise set_location(exc, next_token)

    stream.index = current_index


@dataclass
class FinalExpressionParser:
    """Parser that verifies that the expression isn't followed by anything."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node = self.parser(stream)

        current_index = stream.index

        if consume_line_continuation(stream):
            exc = InvalidSyntax("Invalid indent following final expression.")
            raise set_location(exc, stream.get())

        next_token = stream.get()
        if next_token and not next_token.match("newline", "eof"):
            exc = InvalidSyntax("Trailing input following final expression.")
            raise set_location(exc, next_token)

        stream.index = current_index

        return node


@dataclass
class InterpolationParser:
    """Parser for interpolation."""

    converter: str
    prefix: Optional[str] = None
    unpack: Optional[str] = None

    def __call__(self, stream: TokenStream) -> Any:
        if stream.data.get("disable_interpolation"):
            token = stream.expect()
            raise set_location(InvalidSyntax("Interpolation disabled."), token)

        with stream.syntax(prefix=self.prefix, unpack=self.unpack):
            prefix = stream.get("prefix")
            unpack = self.unpack is not None and stream.expect("unpack")

        node = delegate("bolt:interpolation", stream)
        node = AstInterpolation(
            prefix=prefix.value if prefix else None,
            unpack=unpack.value if unpack else None,
            converter=self.converter,
            value=node,
        )
        return set_location(node, prefix or node.value, node.value)


@dataclass
class DisableInterpolationParser:
    """Parser that disables interpolation."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.provide(disable_interpolation=True):
            return self.parser(stream)


def parse_statement(stream: TokenStream) -> Any:
    """Parse statement."""
    identifiers = get_stream_identifiers(stream)
    pending_identifiers = get_stream_pending_identifiers(stream)
    identifiers_storage = get_stream_identifiers_storage(stream)
    pending_identifiers_storage = get_stream_pending_identifiers_storage(stream)

    for parser, alternative in stream.choose(
        "bolt:augmented_assignment_target",
        "bolt:assignment_target",
        "bolt:expression",
        "bolt:decorator",
    ):
        with alternative:
            pending_identifiers.clear()
            pending_identifiers_storage.clear()
            node = delegate(parser, stream)

            pattern = r"=(?!=)|\+=|-=|\*=|//=|/=|%=|&=|\|=|\^=|<<=|>>=|\*\*="

            if isinstance(node, AstTarget):
                if parser == "bolt:assignment_target":
                    pattern = r"=(?!=)"
                with stream.syntax(assignment=pattern):
                    op = stream.expect("assignment")

                expression = delegate("bolt:expression", stream)

                identifiers |= pending_identifiers
                pending_identifiers.clear()
                identifiers_storage.update(pending_identifiers_storage)
                pending_identifiers_storage.clear()

                node = AstAssignment(operator=op.value, target=node, value=expression)
                node = set_location(node, node.target, node.value)

            elif isinstance(node, AstAttribute):
                with stream.syntax(assignment=pattern):
                    op = stream.get("assignment")

                if op:
                    expression = delegate("bolt:expression", stream)
                    target = AstTargetAttribute(
                        name=node.name,
                        value=node.value,
                    )
                    node = AstAssignment(
                        operator=op.value,
                        target=set_location(target, node),
                        value=expression,
                    )
                    node = set_location(node, node.target, node.value)

            elif isinstance(node, AstLookup):
                with stream.syntax(assignment=pattern):
                    op = stream.get("assignment")

                if op:
                    expression = delegate("bolt:expression", stream)
                    target = AstTargetItem(
                        value=node.value,
                        arguments=node.arguments,
                    )
                    node = AstAssignment(
                        operator=op.value,
                        target=set_location(target, node),
                        value=expression,
                    )
                    node = set_location(node, node.target, node.value)

            # Make sure that the statement is not followed by anything.
            check_final_expression(stream)

            return node


def parse_decorator(stream: TokenStream) -> Any:
    """Parse decorator."""
    with stream.syntax(decorator="@"):
        token = stream.expect("decorator")
        expression = delegate("bolt:expression", stream)
        return set_location(AstDecorator(expression=expression), token, expression)


@dataclass
class DecoratorResolver:
    """Parser for resolving decorators."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> AstRoot:
        node: AstRoot = self.parser(stream)

        stack: List[AstDecorator] = []

        changed = False
        result: List[AstCommand] = []

        for command in node.commands:
            if command.identifier == "statement" and isinstance(
                decorator := command.arguments[0], AstDecorator
            ):
                changed = True
                stack.append(decorator)
            elif stack and isinstance(
                target := command.arguments[0], (AstFunctionSignature, AstClassName)
            ):
                arg = replace(target, decorators=AstChildren(stack))
                result.append(
                    replace(
                        command, arguments=AstChildren([arg, *command.arguments[1:]])
                    )
                )
                stack.clear()
            elif stack:
                message = "Decorators can only be applied to functions or classes."
                raise set_location(InvalidSyntax(message), stack[-1])
            else:
                result.append(command)

        if stack:
            exc = InvalidSyntax("Can't apply decorator to nothing.")
            raise set_location(exc, stack[-1])

        if changed:
            node = replace(node, commands=AstChildren(result))

        return node


@dataclass
class AssignmentTargetParser:
    """Parser for assignment targets."""

    allow_undefined_identifiers: bool = False
    allow_multiple: bool = False

    def __call__(self, stream: TokenStream) -> AstTarget:
        identifiers = get_stream_identifiers(stream)
        pending_identifiers = get_stream_pending_identifiers(stream)
        identifiers_storage = get_stream_identifiers_storage(stream)
        pending_identifiers_storage = get_stream_pending_identifiers_storage(stream)

        nodes: List[AstTarget] = []

        with stream.syntax(identifier=IDENTIFIER_PATTERN, comma=r","):
            while True:
                token = stream.expect("identifier")
                is_defined = token.value in identifiers
                with_storage = token.value in identifiers_storage
                rebind = is_defined and with_storage

                if self.allow_undefined_identifiers:
                    pending_identifiers.add(token.value)
                    if not with_storage:
                        pending_identifiers_storage[token.value] = "local"
                elif not rebind:
                    exc = UndefinedIdentifier(token.value, list(identifiers_storage))
                    if is_defined and not with_storage:
                        exc.notes.append(
                            f"Use 'global {token.value}' or 'nonlocal {token.value}' to mutate the variable defined in outer scope."
                        )
                    raise set_location(exc, token)

                target = AstTargetIdentifier(value=token.value, rebind=rebind)
                nodes.append(set_location(target, token))

                if not self.allow_multiple or not stream.get("comma"):
                    break

        if len(nodes) == 1:
            return nodes[0]

        node = AstTargetUnpack(targets=AstChildren(nodes))
        return set_location(node, nodes[0], nodes[-1])


@dataclass
class IfElseLoweringParser:
    """Parser that turns elif statements into if statements in an else clause."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> AstRoot:
        node: AstRoot = self.parser(stream)

        changed = False
        result: List[AstCommand] = []

        commands = iter(node.commands)
        previous = ""

        for command in commands:
            if command.identifier in ["elif:condition:body", "else:body"]:
                if previous not in ["if:condition:body", "elif:condition:body"]:
                    exc = InvalidSyntax(
                        "Conditional branch must be part of an if statement."
                    )
                    raise set_location(exc, command, command.arguments[-1].location)

            if command.identifier == "elif:condition:body":
                changed = True
                elif_chain = [command]

                for command in commands:
                    if command.identifier not in ["elif:condition:body", "else:body"]:
                        break
                    elif_chain.append(command)
                else:
                    command = None

                if elif_chain[-1].identifier == "else:body":
                    last = [elif_chain.pop()]
                else:
                    last = []

                for stmt in reversed(elif_chain):
                    stmt = replace(stmt, identifier="if:condition:body")
                    stmt = AstRoot(commands=AstChildren([stmt, *last]))
                    stmt = set_location(stmt, stmt.commands[0], stmt.commands[-1])
                    stmt = AstCommand(
                        identifier="else:body",
                        arguments=AstChildren([stmt]),
                    )
                    last = [set_location(stmt, stmt.arguments[0])]

                result.append(last[0])

            if not command:
                break

            previous = command.identifier
            result.append(command)

        if changed:
            node = replace(node, commands=AstChildren(result))

        return node


@dataclass
class BreakContinueConstraint:
    """Constraint that makes sure that break and continue statements only occur in loops."""

    parser: Parser
    allowed_scopes: Set[Tuple[str, ...]]

    def __call__(self, stream: TokenStream) -> AstRoot:
        scope = get_stream_scope(stream)
        loop = stream.data.get("loop") or scope in self.allowed_scopes

        with stream.provide(loop=loop):
            node: AstRoot = self.parser(stream)

        if not loop:
            for command in node.commands:
                if command.identifier in ["break", "continue"]:
                    exc = InvalidSyntax(
                        f'Can only use "{command.identifier}" in loops.'
                    )
                    raise set_location(exc, command)

        return node


@dataclass
class FlushPendingIdentifiersParser:
    """Parser that flushes pending identifiers."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        identifiers = get_stream_identifiers(stream)
        pending_identifiers = get_stream_pending_identifiers(stream)
        identifiers_storage = get_stream_identifiers_storage(stream)
        pending_identifiers_storage = get_stream_pending_identifiers_storage(stream)

        identifiers |= pending_identifiers
        pending_identifiers.clear()
        identifiers_storage.update(pending_identifiers_storage)
        pending_identifiers_storage.clear()

        return self.parser(stream)


def parse_deferred_root(stream: TokenStream) -> AstDeferredRoot:
    """Parse deferred root."""
    identifiers = get_stream_identifiers(stream)
    pending_identifiers = get_stream_pending_identifiers(stream)
    deferred_locals = get_stream_deferred_locals(stream)
    class_scope = get_stream_class_scope(stream)

    identifiers.update(pending_identifiers)
    pending_identifiers.clear()

    if class_scope is not None:
        identifiers = class_scope

    stream_copy = stream.copy()

    with stream.syntax(colon=r":"):
        token = stream.expect("colon")

    with stream.syntax(statement=r"[^\s#].*"):
        while consume_line_continuation(stream):
            stream.expect("statement")

    stream_copy.data["identifiers"] = identifiers | deferred_locals
    stream_copy.data["pending_identifiers"] = set()
    stream_copy.data["identifiers_storage"] = {loc: "local" for loc in deferred_locals}
    stream_copy.data["pending_identifiers_storage"] = {}
    stream_copy.data["deferred_locals"] = set()
    stream_copy.data["branch_scope"] = set()
    stream_copy.data["class_scope"] = None
    del stream_copy.data["root_scope"]

    deferred_locals.clear()

    node = AstDeferredRoot(stream=stream_copy)
    return set_location(node, token, stream.current)


def parse_function_signature(stream: TokenStream) -> AstFunctionSignature:
    """Parse function signature."""
    identifiers = get_stream_identifiers(stream)
    pending_identifiers = get_stream_pending_identifiers(stream)
    deferred_locals = get_stream_deferred_locals(stream)
    class_scope = get_stream_class_scope(stream)

    if class_scope is not None:
        identifiers = class_scope

    scoped_identifiers = set(identifiers)

    arguments: List[AstFunctionSignatureElement] = []
    new_locals: Set[str] = set()

    encountered_positional = False
    encountered_default = False
    encountered_variadic = False
    encountered_variadic_keyword = False
    expect_named_argument = False

    with stream.syntax(
        comma=r",",
        equal=r"=(?!=)",
        brace=r"\(|\)",
        separator=r"/",
        kwargs=r"\*\*",
        args=r"\*",
        identifier=IDENTIFIER_PATTERN,
    ):
        identifier = stream.expect("identifier")
        stream.expect(("brace", "("))

        scoped_identifiers.add(identifier.value)

        with stream.ignore("newline"):
            for token in stream.peek_until(("brace", ")")):
                if encountered_variadic_keyword:
                    exc = InvalidSyntax(
                        "Variadic keyword arguments should not be followed by anything."
                    )
                    raise set_location(exc, token)

                name, separator, kwargs, args = stream.expect(
                    "identifier",
                    "separator",
                    "kwargs",
                    "args",
                )

                if name:
                    expect_named_argument = False

                    default = None
                    if stream.get("equal"):
                        encountered_default = True
                        with stream.provide(
                            identifiers=scoped_identifiers | new_locals
                        ):
                            default = delegate("bolt:expression", stream)
                    elif encountered_default:
                        exc = InvalidSyntax(
                            "Argument without default can not appear after arguments with default values."
                        )
                        raise set_location(exc, token)

                    argument = AstFunctionSignatureArgument(
                        name=name.value,
                        default=default,
                    )
                    arguments.append(set_location(argument, name, stream.current))
                    new_locals.add(argument.name)

                elif separator:
                    if encountered_positional:
                        exc = InvalidSyntax(
                            "Positional marker already present in function signature."
                        )
                        raise set_location(exc, separator)
                    if encountered_variadic:
                        exc = InvalidSyntax(
                            "Positional marker can not appear after variadic arguments."
                        )
                        raise set_location(exc, separator)
                    if not arguments:
                        exc = InvalidSyntax(
                            "Positional marker can not appear directly at the beginning of the argument list."
                        )
                        raise set_location(exc, separator)
                    encountered_positional = True
                    argument = AstFunctionSignaturePositionalMarker()
                    arguments.append(set_location(argument, separator))

                elif kwargs:
                    encountered_variadic_keyword = True
                    name = stream.expect("identifier")
                    argument = AstFunctionSignatureVariadicKeywordArgument(
                        name=name.value
                    )
                    arguments.append(set_location(argument, kwargs, name))
                    new_locals.add(argument.name)

                elif args:
                    if encountered_variadic:
                        exc = InvalidSyntax("Variadic arguments already specified.")
                        raise set_location(exc, args)
                    encountered_variadic = True
                    if name := stream.get("identifier"):
                        argument = AstFunctionSignatureVariadicArgument(name=name.value)
                        arguments.append(set_location(argument, args, name))
                        new_locals.add(argument.name)
                    else:
                        expect_named_argument = True
                        argument = AstFunctionSignatureVariadicMarker()
                        arguments.append(set_location(argument, args))

                if not stream.get("comma"):
                    stream.expect(("brace", ")"))
                    break

        if expect_named_argument:
            for argument in arguments:
                if isinstance(argument, AstFunctionSignatureVariadicMarker):
                    exc = InvalidSyntax(
                        "Expected at least one named argument after bare variadic marker."
                    )
                    raise set_location(exc, argument)

    pending_identifiers.add(identifier.value)
    deferred_locals |= new_locals

    node = AstFunctionSignature(name=identifier.value, arguments=AstChildren(arguments))
    return set_location(node, identifier, stream.current)


def parse_proc_macro_signature(stream: TokenStream):
    """Parse proc macro signature."""
    with stream.syntax(brace=r"\(|\)", identifier=IDENTIFIER_PATTERN):
        begin = stream.expect(("brace", "("))
        stream.expect(("identifier", "stream"))
        end = stream.expect(("brace", ")"))

    get_stream_pending_identifiers(stream).add("stream")
    get_stream_deferred_locals(stream).add("stream")

    return set_location(AstProcMacroMarker(), begin, end)


@dataclass
class MacroMatchParser:
    """Parser for macro matching."""

    literal_parser: Parser
    argument_parser: Parser
    resource_location_parser: Parser
    json_properties_parser: Parser

    def __call__(self, stream: TokenStream) -> AstMacroMatch:
        spec = get_stream_spec(stream)
        pending_identifiers = get_stream_pending_identifiers(stream)
        deferred_locals = get_stream_deferred_locals(stream)

        with stream.syntax(equal=r"(?<!\s)=(?!\s)"), stream.checkpoint() as commit:
            argument = self.argument_parser(stream)
            stream.expect("equal")
            commit()

            pending_identifiers.add(argument.value)
            deferred_locals.add(argument.value)

            node = AstMacroMatchArgument(
                match_identifier=argument,
                match_argument_parser=self.resource_location_parser(stream),
                match_argument_properties=self.json_properties_parser(stream),
            )
            node = set_location(
                node,
                argument,
                node.match_argument_properties or node.match_argument_parser,
            )

            parser_name = node.match_argument_parser.get_canonical_value()
            if f"command:argument:{parser_name}" not in spec.parsers:
                exc = InvalidSyntax(f'Unrecognized argument parser "{parser_name}".')
                raise set_location(exc, node.match_argument_parser)

        if commit.rollback:
            literal = self.literal_parser(stream)
            node = set_location(AstMacroMatchLiteral(match=literal), literal)

        return node


@dataclass
class MacroHandler:
    """Handle macros."""

    parser: Parser

    proc_macro_overloads: Dict[str, Dict[str, int]] = extra_field(default_factory=dict)
    spec_cache: Dict[FrozenSet[AstMacro], CommandSpec] = extra_field(
        default_factory=dict
    )

    def __call__(self, stream: TokenStream) -> Any:
        should_flush = not (
            scope[0] in ["macro", "from"]
            if (scope := get_stream_scope(stream))
            else (
                (token := stream.peek())
                and token.match(("literal", "macro"), ("literal", "from"))
            )
        )
        if should_flush:
            self.flush_pending_macros(stream)

        node = self.parser(stream)

        if not isinstance(node, AstCommand):
            return node

        if node.identifier == "macro:name:subcommand":
            self.check_root_scope(stream, node)
            node = self.create_macro(node, stream.data.get("resource_location"))
            if not isinstance(node, AstProcMacro):
                declaration = replace(node, arguments=AstChildren(node.arguments[:-1]))
                get_stream_pending_macros(stream).append(declaration)

        elif macro := get_stream_macro_scope(stream).get(node.identifier):
            if not isinstance(macro, AstProcMacro):
                node = set_location(
                    AstMacroCall(identifier=node.identifier, arguments=node.arguments),
                    node,
                )

        return node

    def check_root_scope(self, stream: TokenStream, node: AstCommand):
        if not stream.data.get("root_scope"):
            message = "Macro definition can only appear directly at scope level."
            raise set_location(InvalidSyntax(message), node, node.arguments[0])

    def create_macro(
        self,
        command: AstCommand,
        resource_location: Optional[str] = None,
    ) -> AstMacro:
        identifier_parts: List[str] = []
        arguments: List[AstNode] = []

        node = command
        while isinstance(subcommand := node.arguments[-1], AstCommand):
            if isinstance(literal := node.arguments[0], AstMacroLiteral):
                if literal.value in ["macro", "from"]:
                    exc = InvalidSyntax(f'Forbidden literal "{literal.value}".')
                    raise set_location(exc, literal)
                identifier_parts.append(literal.value)
            elif isinstance(literal := node.arguments[0], AstMacroMatchLiteral):
                identifier_parts.append(literal.match.value)
            elif isinstance(argument := node.arguments[0], AstMacroMatchArgument):
                identifier_parts.append(argument.match_identifier.value)
            arguments.append(node.arguments[0])
            node = subcommand

        if isinstance(marker := node.arguments[0], AstProcMacroMarker):
            identifier = ":".join(identifier_parts)

            if not resource_location:
                message = f'Can\'t define proc macro "{identifier_parts[0]}" without resource location information.'
                raise set_location(InvalidSyntax(message), arguments[0], marker)

            for argument in arguments:
                if isinstance(argument, AstMacroMatchArgument):
                    message = f'Proc macro "{identifier_parts[0]}" contains non-literal match.'
                    raise set_location(InvalidSyntax(message), argument)

            macro_overload = self.proc_macro_overloads.setdefault(resource_location, {})
            overload_id = macro_overload.setdefault(identifier, 0)
            macro_overload[identifier] += 1

            argument = f"proc_macro_overload{overload_id}"
            identifier = f"{identifier}:{argument}"

            match_node = AstMacroMatchArgument(
                match_identifier=AstMacroArgument(value=argument),
                match_argument_parser=AstResourceLocation.from_value("bolt:proc_macro"),
                match_argument_properties=AstJson.from_value(
                    {
                        "resource_location": resource_location,
                        "identifier": identifier,
                    }
                ),
            )
            arguments.append(match_node)
            arguments.append(node.arguments[-1])

            macro = AstProcMacro(
                identifier=identifier,
                arguments=AstChildren(arguments),
            )
            return set_location(macro, command)

        arguments.append(node.arguments[0])

        macro = AstMacro(
            identifier=":".join(identifier_parts),
            arguments=AstChildren(arguments),
        )

        return set_location(macro, command)

    def flush_pending_macros(self, stream: TokenStream):
        if pending_macros := get_stream_pending_macros(stream):
            self.inject_syntax(stream, *pending_macros)
            pending_macros.clear()

    def cache_local_spec(self, stream: TokenStream):
        if stream.data.get("local_spec"):
            scope_key = frozenset(get_stream_macro_scope(stream).values())
            self.spec_cache[scope_key] = get_stream_spec(stream)
            stream.data["local_spec"] = False

    def inject_syntax(self, stream: TokenStream, *macros: AstMacro):
        macro_scope = get_stream_macro_scope(stream)
        scope_key = frozenset(macros) | frozenset(macro_scope.values())

        if len(macro_scope) == len(scope_key):
            return

        if spec := self.spec_cache.get(scope_key):
            stream.data["local_spec"] = False
            stream.data["spec"] = spec
            stream.data["macro_scope"] = {
                macro.identifier: macro for macro in scope_key
            }
            return

        spec = get_stream_spec(stream)

        if not stream.data.get("local_spec"):
            stream.data["local_spec"] = True
            spec = replace(spec, tree=spec.tree.copy(deep=True), prototypes={})
            stream.data["spec"] = spec
            macro_scope = macro_scope.copy()
            stream.data["macro_scope"] = macro_scope

        for macro in macros:
            spec.tree.extend(CommandTree.parse_obj(macro.get_command_tree()))
            macro_scope[macro.identifier] = macro

        spec.update()


@dataclass
class ProcMacroParser:
    """Parser for invoking proc macros."""

    modules: ModuleManager

    @internal
    def __call__(self, stream: TokenStream) -> AstProcMacroResult:
        properties = get_stream_properties(stream)
        resource_location: str = properties["resource_location"]
        identifier: str = properties["identifier"]

        module = self.modules[resource_location]
        runtime: CommandCollector = module.namespace["_bolt_runtime"]
        macro = module.namespace["_bolt_proc_macros"][identifier]

        with self.modules.error_handler(
            f'Proc macro "{identifier}" raised an exception.', resource_location
        ):
            result = runtime.capture_output(macro, stream)

        return AstProcMacroResult(commands=AstChildren(result))


@dataclass
class ProcMacroExpansion:
    """Expand proc macro results."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> AstRoot:
        should_replace = False
        commands: List[AstCommand] = []

        node: AstRoot = self.parser(stream)

        for command in node.commands:
            stack: List[AstCommand] = [command]

            while command.arguments and isinstance(
                command := command.arguments[-1], AstCommand
            ):
                stack.append(command)

            command = stack.pop()

            if command.arguments and isinstance(
                result := command.arguments[-1], AstProcMacroResult
            ):
                should_replace = True

                for expansion in result.commands:
                    for prefix in reversed(stack):
                        args = AstChildren([*prefix.arguments[:-1], expansion])
                        expansion = replace(prefix, arguments=args)
                    commands.append(expansion)

                continue

            elif stack:
                command = stack[0]

            commands.append(command)

        if should_replace:
            return replace(node, commands=AstChildren(commands))

        return node


def parse_class_name(stream: TokenStream) -> AstClassName:
    """Parse class name."""
    with stream.syntax(identifier=IDENTIFIER_PATTERN):
        token = stream.expect("identifier")

    get_stream_pending_identifiers(stream).add(token.value)
    return set_location(AstClassName(value=token.value), token)


def parse_class_bases(stream: TokenStream) -> AstClassBases:
    """Parse class bases."""
    inherit: List[AstExpression] = []

    with stream.syntax(brace=r"\(|\)", comma=","):
        token = stream.expect(("brace", "("))

        with stream.ignore("newline"):
            for _ in stream.peek_until(("brace", ")")):
                inherit.append(delegate("bolt:expression", stream))

                if not stream.get("comma"):
                    stream.expect(("brace", ")"))
                    break

    node = AstClassBases(inherit=AstChildren(inherit))
    return set_location(node, token, stream.current)


def parse_class_root(stream: TokenStream) -> AstRoot:
    """Parse class root."""
    with stream.provide(class_scope=get_stream_identifiers(stream)):
        return delegate("nested_root", stream)


@dataclass
class ClassBodyScoping:
    """Handle class body scoping."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        class_scope = get_stream_class_scope(stream)
        if class_scope is None:
            return self.parser(stream)

        identifiers = get_stream_identifiers(stream)
        pending_identifiers = get_stream_pending_identifiers(stream)
        identifiers_storage = get_stream_identifiers_storage(stream)
        pending_identifiers_storage = get_stream_pending_identifiers_storage(stream)

        with stream.provide(
            function=False,
            identifiers=identifiers.copy(),
            pending_identifiers=set(),
            identifiers_storage=identifiers_storage.copy(),
            pending_identifiers_storage={},
        ):
            node = self.parser(stream)
            identifiers.update(pending_identifiers)
            pending_identifiers.clear()
            identifiers_storage.update(pending_identifiers_storage)
            pending_identifiers_storage.clear()

        return set_location(AstClassRoot(commands=node.commands), node)


def parse_del_target(stream: TokenStream) -> AstTarget:
    node = delegate("bolt:expression", stream)

    if isinstance(node, AstIdentifier):
        return set_location(AstTargetIdentifier(value=node.value), node)
    elif isinstance(node, AstAttribute):
        return set_location(AstTargetAttribute(name=node.name, value=node.value), node)
    elif isinstance(node, AstLookup):
        return set_location(
            AstTargetItem(value=node.value, arguments=node.arguments), node
        )

    exc = InvalidSyntax("Can only delete variables, attributes, or subscripted items.")
    raise set_location(exc, node)


def parse_identifier(stream: TokenStream) -> AstIdentifier:
    """Parse identifier."""
    identifiers = get_stream_identifiers(stream)

    with stream.syntax(
        true=TRUE_PATTERN,
        false=FALSE_PATTERN,
        null=NULL_PATTERN,
        identifier=IDENTIFIER_PATTERN,
    ):
        token = stream.expect("identifier")

    if token.value not in identifiers:
        exc = UndefinedIdentifier(token.value, list(identifiers))
        raise set_location(exc, token)

    return set_location(AstIdentifier(value=token.value), token)


@dataclass
class TrailingCommaParser:
    """Parser for discarding trailing comma."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node = self.parser(stream)
        with stream.syntax(comma=r","):
            stream.get("comma")
        return node


@dataclass
class ImportLocationConstraint:
    """Constraint for import location."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstResourceLocation = self.parser(stream)

        if node.is_tag or node.namespace is None and not IMPORT_REGEX.match(node.path):
            exc = InvalidSyntax(f'Invalid module location "{node.get_value()}".')
            raise set_location(exc, node)

        return node


@dataclass
class ImportStatementHandler:
    """Handle import statements."""

    parser: Parser
    modules: ModuleManager

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstCommand):
            if node.identifier in ["import:module", "import:module:as:alias"]:
                self.check_root_scope(stream, node)
                return self.handle_import(stream, node)
            elif node.identifier == "from:module:import:subcommand":
                self.check_root_scope(stream, node)
                return self.handle_from_import(stream, node)
        return node

    def check_root_scope(self, stream: TokenStream, node: AstCommand):
        if not stream.data.get("root_scope"):
            message = "Import statement can only appear directly at scope level."
            raise set_location(InvalidSyntax(message), node)

    def handle_import(self, stream: TokenStream, node: AstCommand) -> AstCommand:
        identifiers = get_stream_identifiers(stream)
        identifiers_storage = get_stream_identifiers_storage(stream)

        if node.identifier == "import:module":
            if isinstance(module := node.arguments[0], AstResourceLocation):
                if module.namespace:
                    message = f'Can\'t import "{module.get_value()}" without alias.'
                    raise set_location(InvalidSyntax(message), module)
                identifiers.add(module.path.partition(".")[0])

        elif node.identifier == "import:module:as:alias":
            if isinstance(alias := node.arguments[1], AstImportedItem):
                if not alias.identifier:
                    exc = InvalidSyntax(f'Invalid identifier "{alias.name}".')
                    raise set_location(exc, alias)
                identifiers.add(alias.name)
                identifiers_storage.setdefault(alias.name, "local")

        return node

    @internal
    def handle_from_import(self, stream: TokenStream, node: AstCommand) -> AstCommand:
        identifiers = get_stream_identifiers(stream)
        identifiers_storage = get_stream_identifiers_storage(stream)
        pending_macros = get_stream_pending_macros(stream)

        module = cast(AstResourceLocation, node.arguments[0])
        target_name = module.get_value()
        target = self.modules.database.index.get(target_name)

        try:
            compiled_module = (
                target
                and target not in self.modules.parse_stack
                and self.modules.get(target)
            )
        except UnusableCompilationUnit:
            compiled_module = None

        arguments: List[AstNode] = [module]

        subcommand = cast(AstCommand, node.arguments[1])
        while True:
            if isinstance(item := subcommand.arguments[0], AstImportedItem):
                if compiled_module and item.name in compiled_module.macros:
                    for name, macro in compiled_module.macros[item.name]:
                        imported_macro = AstImportedMacro(name=name, declaration=macro)
                        arguments.append(set_location(imported_macro, item))
                        pending_macros.append(macro)

                        if not compiled_module.executed and isinstance(
                            macro, AstProcMacro
                        ):
                            with self.modules.error_handler(
                                "Top-level statement raised an exception.",
                                target_name,
                            ), self.modules.parse_push(
                                target  # type: ignore
                            ):
                                self.modules.eval(compiled_module)

                elif item.identifier:
                    arguments.append(item)
                    identifiers.add(item.name)
                    identifiers_storage.setdefault(item.name, "local")

                else:
                    exc = InvalidSyntax(f'Invalid identifier "{item.name}".')
                    raise set_location(exc, item)

            if subcommand.identifier == "from:module:import:name:subcommand":
                subcommand = cast(AstCommand, subcommand.arguments[1])
            else:
                break

        return set_location(AstFromImport(arguments=AstChildren(arguments)), node)


def parse_python_import(stream: TokenStream) -> Any:
    """Parse python import."""
    with stream.syntax(module=rf"{MODULE_PATTERN}(?=\s)"):
        token = stream.expect("module")
        return set_location(AstResourceLocation(path=token.value), token)


def parse_import_name(stream: TokenStream) -> AstImportedItem:
    """Parse import name."""
    with stream.syntax(name=IDENTIFIER_PATTERN, literal=r"[^#:\s]+(?<!,)"):
        token = stream.get("name")

        if token:
            node = AstImportedItem(name=token.value)
        else:
            token = stream.expect("literal")
            node = AstImportedItem(name=token.value, identifier=False)

        return set_location(node, token)


def parse_name_list(stream: TokenStream) -> AstIdentifier:
    """Parse name list."""
    node = delegate("bolt:identifier", stream)
    with stream.syntax(comma=r","):
        stream.get("comma")
    return node


@dataclass
class GlobalNonlocalHandler:
    """Handle global and nonlocal declarations."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        identifiers_storage = get_stream_identifiers_storage(stream)

        if isinstance(node := self.parser(stream), AstCommand):
            if node.identifier in ["global:subcommand", "nonlocal:subcommand"]:
                storage, _, _ = node.identifier.partition(":")
                subcommand = cast(AstCommand, node.arguments[0])
                while True:
                    if isinstance(name := subcommand.arguments[0], AstIdentifier):
                        s = identifiers_storage.setdefault(name.value, storage)
                        if s != storage:
                            exc = InvalidSyntax(f"Can't make {s} identifier {storage}.")
                            raise set_location(exc, name)
                    if subcommand.identifier == f"{storage}:name:subcommand":
                        subcommand = cast(AstCommand, subcommand.arguments[1])
                    else:
                        break

        return node


@dataclass
class StatementSubcommandHandler:
    """Prevent statements as subcommands."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if (
            isinstance(node := self.parser(stream), AstCommand)
            and node.arguments
            and isinstance(child := node.arguments[-1], AstCommand)
            and child.identifier == "statement"
        ):
            exc = InvalidSyntax("Can't use statement as a subcommand.")
            raise set_location(exc, child)
        return node


@dataclass
class DeferredRootBacktracker:
    """Parser for backtracking over deferred root nodes."""

    parser: Parser
    macro_handler: MacroHandler

    def __call__(self, stream: TokenStream) -> AstRoot:
        node: AstRoot = self.parser(stream)

        if isinstance(node, AstClassRoot):
            return node

        return self.resolve_deferred(node, stream)

    def resolve_deferred(self, node: AstRoot, stream: TokenStream) -> AstRoot:
        should_replace = False
        commands: List[AstCommand] = []

        for command in node.commands:
            if command.arguments and isinstance(
                body := command.arguments[-1], AstClassRoot
            ):
                resolved_body = self.resolve_deferred(body, stream)
                if resolved_body is not body:
                    should_replace = True
                    command = replace(
                        command,
                        arguments=AstChildren([*command.arguments[:-1], resolved_body]),
                    )

            stack: List[AstCommand] = [command]

            while command.arguments and isinstance(
                command := command.arguments[-1], AstCommand
            ):
                stack.append(command)

            command = stack.pop()

            if command.arguments and isinstance(
                deferred_root := command.arguments[-1], AstDeferredRoot
            ):
                should_replace = True

                self.macro_handler.flush_pending_macros(stream)

                deferred_stream = deferred_root.stream
                deferred_stream.data["local_spec"] = False
                deferred_stream.data["spec"] = get_stream_spec(stream)
                deferred_stream.data["identifiers"] |= get_stream_identifiers(stream)
                deferred_stream.data["function"] = True
                deferred_stream.data["macro_scope"] = get_stream_macro_scope(stream)
                deferred_stream.data["pending_macros"] = []
                nested_root = delegate("nested_root", deferred_stream)

                self.macro_handler.cache_local_spec(deferred_stream)

                command = replace(
                    command,
                    arguments=AstChildren([*command.arguments[:-1], nested_root]),
                )
                while stack:
                    parent = stack.pop()
                    command = replace(
                        parent,
                        arguments=AstChildren([*parent.arguments[:-1], command]),
                    )

            elif stack:
                command = stack[0]

            commands.append(command)

        if should_replace:
            return replace(node, commands=AstChildren(commands))

        return node


@dataclass
class FunctionConstraint:
    """Constraint that makes sure that the given statements only occur in functions."""

    parser: Parser
    command_identifiers: Set[str]

    def __call__(self, stream: TokenStream) -> AstRoot:
        node = self.parser(stream)

        if stream.data.get("function"):
            return node

        if isinstance(node, AstRoot):
            for command in node.commands:
                if command.identifier in self.command_identifiers:
                    name, _, _ = command.identifier.partition(":")
                    exc = InvalidSyntax(f'Can only use "{name}" in functions.')
                    raise set_location(exc, command)

        return node


@dataclass
class RootScopeHandler:
    """Handle root scope."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.provide(root_scope="root_scope" not in stream.data):
            # Resetting the underlying token generator shouldn't be necessary but
            # currently overloading between nested_root/nested_yaml drops tokens
            # for some reason (see summon macro example).
            stream.generator = stream.generate_tokens()
            return self.parser(stream)


@dataclass
class BinaryParser:
    """Parser for binary expressions."""

    operators: List[str]
    parser: Parser
    right_associative: bool = False

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(operator="|".join(self.operators)):
            nodes = [self.parser(stream)]
            operations: List[str] = []

            for op in stream.collect("operator"):
                nodes.append(self.parser(stream))
                operations.append(normalize_whitespace(op.value))

        if self.right_associative:
            result = nodes[-1]
            nodes = nodes[-2::-1]
            operations = operations[::-1]
        else:
            result = nodes[0]
            nodes = nodes[1:]

        for op, node in zip(operations, nodes):
            if self.right_associative:
                result, node = node, result
            result = AstExpressionBinary(operator=op, left=result, right=node)
            result = set_location(result, result.left, result.right)

        return result


@dataclass
class UnaryParser:
    """Parser for unary expressions."""

    operators: List[str]
    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(operator="|".join(self.operators)):
            if op := stream.get("operator"):
                operator = normalize_whitespace(op.value)
                node = AstExpressionUnary(operator=operator, value=self(stream))
                return set_location(node, op, node.value)
            return self.parser(stream)


@dataclass
class UnpackParser:
    """Parser for unpacking."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(prefix=r"\*\*|\*"):
            prefix = stream.expect("prefix")

        node = self.parser(stream)

        node = AstUnpack(type="dict" if prefix.value == "**" else "list", value=node)
        return set_location(node, prefix, node.value)


@dataclass
class UnpackConstraint:
    """Constraint for unpacking."""

    type: str
    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstUnpack):
            if node.type != self.type:
                exc = InvalidSyntax(f"{node.type.capitalize()} unpacking not allowed.")
                raise node.emit_error(exc)
        return node


@dataclass
class KeywordParser:
    """Parser for keywords."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(name=IDENTIFIER_PATTERN, equal=r"=(?!=)"):
            name = stream.expect("name")
            stream.expect("equal")

        node = self.parser(stream)

        node = AstKeyword(name=name.value, value=node)
        return set_location(node, name, node.value)


@dataclass
class LookupParser:
    """Parser for lookups."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        start = None
        stop = None
        step = None

        with stream.provide(bolt_lookup=True), stream.syntax(
            colon=r":",
            comma=r",",
            bracket=r"\]",
        ):
            colon1 = stream.get("colon")

            if not colon1:
                start = self.parser(stream)
                location = start.location
                colon1 = stream.get("colon")
            else:
                location = colon1.location

            if not colon1:
                return start

            colon2 = stream.get("colon")

            if not colon2:
                with stream.checkpoint():
                    sep = stream.get("comma", "bracket")
                if not sep:
                    stop = self.parser(stream)
                    colon2 = stream.get("colon")

            if colon2:
                with stream.checkpoint():
                    sep = stream.get("comma", "bracket")
                if not sep:
                    step = self.parser(stream)

        node = AstSlice(start=start, stop=stop, step=step)
        return set_location(node, location, stream.location)


@dataclass
class PrimaryParser:
    """Parser for primary expressions."""

    parser: Parser
    truncate: bool = False

    quote_helper: QuoteHelper = field(default_factory=JsonQuoteHelper)

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(brace=r"\(|\)", comma=r",", format_string=r"f['\"]"):
            token = stream.get(("brace", "("), "format_string")

            if token and token.match("brace"):
                with stream.ignore("newline"):
                    comma = None
                    items: List[AstExpression] = []

                    for _ in stream.peek_until(("brace", ")")):
                        items.append(delegate("bolt:expression", stream))

                        if not (comma := stream.get("comma")):
                            stream.expect(("brace", ")"))
                            break

                    if len(items) == 1 and not comma:
                        node = items[0]
                    else:
                        node = AstTuple(items=AstChildren(items))
                        node = set_location(node, token, stream.current)

                if self.truncate:
                    return node

            elif token and token.match("format_string"):
                quote = token.value[-1]

                with stream.provide(bolt_format_string=True), stream.syntax(
                    escape=rf"\\.",
                    double_brace=r"\{\{|\}\}",
                    brace=r"\{|\}",
                    quote=quote,
                    text=r"[^\\]+?",
                ):
                    fmt = quote
                    values: List[AstExpression] = []

                    for escape, double_brace, brace, text in stream.collect(
                        "escape",
                        "double_brace",
                        ("brace", "{"),
                        "text",
                    ):
                        if escape:
                            fmt += escape.value
                        elif double_brace:
                            fmt += double_brace.value
                        elif brace:
                            fmt += "{"
                            with stream.syntax(text=None):
                                values.append(delegate("bolt:expression", stream))
                            with stream.syntax(spec=r"[:!][^\}]+", double_brace=None):
                                if spec := stream.get("spec"):
                                    fmt += spec.value
                                stream.expect(("brace", "}"))
                            fmt += "}"
                        elif text:
                            fmt += text.value

                    end_quote = stream.expect("quote")
                    fmt += end_quote.value

                    fmt = self.quote_helper.unquote_string(
                        Token(
                            "format_string",
                            fmt,
                            token.location.with_horizontal_offset(1),
                            end_quote.end_location,
                        )
                    )

                    node = AstFormatString(fmt=fmt, values=AstChildren(values))
                    node = set_location(node, token, end_quote)

                if self.truncate:
                    return node

            else:
                node = self.parser(stream)

        with stream.syntax(
            dot=r"\.",
            comma=r",",
            brace=r"\(|\)",
            bracket=r"\[|\]",
            identifier=IDENTIFIER_PATTERN,
            string=STRING_PATTERN,
            number=r"(?:0|[1-9][0-9]*)",
        ):
            while token := stream.get("dot", ("brace", "("), ("bracket", "[")):
                arguments: List[Any] = []

                if token.match("dot"):
                    identifier, string, number = stream.expect(
                        "identifier",
                        "string",
                        "number",
                    )

                    if identifier:
                        node = AstAttribute(value=node, name=identifier.value)
                        node = set_location(node, node.value, identifier)
                        continue

                    if string:
                        value = (
                            string.value[2:-1]
                            if string.value.startswith("r")
                            else self.quote_helper.unquote_string(string)
                        )
                    elif number:
                        value = int(number.value)

                    arguments.append(set_location(AstValue(value=value), stream.current))  # type: ignore

                else:
                    if token.match("brace"):
                        close = ("brace", ")")
                        argument_parser = delegate("bolt:call_argument")
                    else:
                        close = ("bracket", "]")
                        argument_parser = delegate("bolt:lookup_argument")

                    allow_positional = True

                    with stream.ignore("newline"):
                        for _ in stream.peek_until(close):
                            argument = argument_parser(stream)

                            if isinstance(argument, AstKeyword):
                                allow_positional = False
                            elif isinstance(argument, AstUnpack):
                                if argument.type == "dict":
                                    allow_positional = False
                                elif not allow_positional:
                                    exc = InvalidSyntax(
                                        "List unpacking not allowed after keyword arguments."
                                    )
                                    raise argument.emit_error(exc)
                            elif not allow_positional:
                                exc = InvalidSyntax(
                                    "Positional argument not allowed after keyword arguments."
                                )
                                raise argument.emit_error(exc)

                            arguments.append(argument)

                            if not stream.get("comma"):
                                stream.expect(close)
                                break

                if token.match("brace"):
                    node = AstCall(value=node, arguments=AstChildren(arguments))
                else:
                    if not arguments:
                        arguments = [
                            set_location(AstSlice(), node.end_location, stream.current)
                        ]
                    node = AstLookup(value=node, arguments=AstChildren(arguments))

                node = set_location(node, node.value, stream.current)

        return node


@dataclass
class BuiltinCallRestriction:
    """Only allow call expressions on builtins."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        parent = None
        node = self.parser(stream)
        original = node

        while isinstance(node, (AstAttribute, AstLookup, AstCall)):
            parent = node
            node = node.value

        if (
            isinstance(node, AstIdentifier)
            and not isinstance(parent, AstCall)
            and node.value in get_stream_builtins(stream)
            and node.value not in get_stream_identifiers_storage(stream)
        ):
            # Reset the underlying token generator so that the identifier can
            # be re-parsed as a different token. That shouldn't be necessary
            # but otherwise this currently induces an error in files that aren't
            # terminated by a newline.
            stream.generator = stream.generate_tokens()
            msg = f'Expected call expression on builtin "{node.value}".'
            raise set_location(InvalidSyntax(msg), parent)

        return original


def parse_dict_item(stream: TokenStream) -> Any:
    """Parse dict item node."""
    with stream.syntax(colon=r":", identifier=IDENTIFIER_PATTERN):
        with stream.checkpoint() as commit:
            identifier = stream.expect("identifier")
            stream.expect("colon")
            commit()

            if identifier.value in get_stream_identifiers(stream) and (
                not identifier.value in get_stream_builtins(stream)
                or identifier.value in get_stream_identifiers_storage(stream)
            ):
                key = AstIdentifier(value=identifier.value)
            else:
                key = AstDictUnquotedKey(value=identifier.value)

            key = set_location(key, identifier)

        if commit.rollback:
            key = delegate("bolt:expression", stream)
            stream.expect("colon")

        value = delegate("bolt:expression", stream)

    item = AstDictItem(key=key, value=value)
    return set_location(item, key, value)


@dataclass
class LiteralParser:
    """Parser for literals."""

    database: CompilationDatabase
    quote_helper: QuoteHelper = field(default_factory=JsonQuoteHelper)

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(
            curly=r"\{|\}",
            bracket=r"\[|\]",
            comma=r",",
            true=TRUE_PATTERN,
            false=FALSE_PATTERN,
            null=NULL_PATTERN,
            string=STRING_PATTERN,
            resource=(
                None
                if stream.data.get("bolt_lookup")
                or stream.data.get("bolt_format_string")
                else RESOURCE_LOCATION_PATTERN
            ),
            number=NUMBER_PATTERN,
        ):
            curly, bracket, true, false, null, string, resource, number = stream.expect(
                ("curly", "{"),
                ("bracket", "["),
                "true",
                "false",
                "null",
                "string",
                "resource",
                "number",
            )

            if curly:
                items: List[Any] = []
                unquoted = False

                with stream.ignore("newline"):
                    for _ in stream.peek_until(("curly", "}")):
                        items.append(item := delegate("bolt:dict_item", stream))
                        unquoted = unquoted or (
                            isinstance(item, AstDictItem)
                            and isinstance(item.key, AstDictUnquotedKey)
                        )

                        if not stream.get("comma"):
                            stream.expect(("curly", "}"))
                            break

                if unquoted:
                    for i, item in enumerate(items):
                        if isinstance(item, AstDictItem):
                            if isinstance(item.key, AstIdentifier):
                                key = AstDictUnquotedKey(value=item.key.value)
                                key = set_location(key, item.key)
                                items[i] = replace(item, key=key)
                            elif not isinstance(item.key, AstDictUnquotedKey):
                                exc = InvalidSyntax(
                                    "Forbidden dynamic key in dict without quotes."
                                )
                                raise set_location(exc, item.key)

                node = AstDict(items=AstChildren(items))
                return set_location(node, curly, stream.current)

            if bracket:
                elements: List[Any] = []

                with stream.ignore("newline"):
                    for _ in stream.peek_until(("bracket", "]")):
                        elements.append(delegate("bolt:list_item", stream))

                        if not stream.get("comma"):
                            stream.expect(("bracket", "]"))
                            break

                node = AstList(items=AstChildren(elements))
                return set_location(node, bracket, stream.current)

            if true:
                value = True
            elif false:
                value = False
            elif null:
                value = None
            elif string:
                value = (
                    string.value[2:-1]
                    if string.value.startswith("r")
                    else self.quote_helper.unquote_string(string)
                )
            elif resource:
                if resource.value.startswith(("./", "../")):
                    value = ":".join(
                        resolve_using_database(
                            relative_path=resource.value,
                            database=self.database,
                            location=resource.location,
                            end_location=resource.end_location,
                        )
                    )
                else:
                    value = resource.value
            elif number:
                value = string_to_number(number.value)

            node = AstValue(value=value)  # type: ignore
            return set_location(node, stream.current)
