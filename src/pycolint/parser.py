from typing import NamedTuple, Protocol, cast
from pycolint.msg_types import get_msg_types
from pycolint.tokenizer import Kind as K, Token
from enum import Enum
from dataclasses import dataclass
import logging


class CommitMsgError(Exception):
    pass


class ProblemType(Enum):
    EMPTY_HDR = 0
    NO_TYPE = 1
    HDR_ENDS_IN_DOT = 2


@dataclass
class Problem:
    type: ProblemType
    token: Token


def _create_msg(p: ProblemType) -> str:
    def empty_hdr() -> str:
        return "commit msg header may not be empty"

    def no_type() -> str:
        return "no type specified, valid types are {}".format(
            ", ".join(get_msg_types())
        )

    return (empty_hdr, no_type)[p.value]()


def parse(msg: list[Token]) -> list[Problem]:
    problems = []
    problems.extend(_parse_header(msg))
    return problems


def _parse_header(h: list[Token]) -> list[Problem]:
    class ExpressionP(Protocol):
        type: str
        sub: list["ExpressionP"]

    class Expression(NamedTuple):
        type: str
        sub: list["ExpressionP"]

    def matches_expr(o: object, type: str) -> bool:
        return isinstance(o, Expression) and o.type == type

    def expr(type: str, sub=None):
        return Expression(type, sub=sub if sub is not None else list())

    stack: list[Expression | Token] = []
    problems = []
    start = Token(K.START, value="", line=-1, column=-1)
    end = Token(K.EOF, value="", column=-1, line=-1)
    h.append(end)
    h.insert(0, start)

    def consume_token():
        h.pop(0)

    def current_token():
        return h[0]

    def next_token():
        return h[1]

    class ExprType:
        def __init__(self, t: str):
            self._t = t

        def matches(self, o: object) -> bool:
            return matches_expr(o, self._t)

        def in_stack(self) -> bool:
            return any(map(self.matches, stack))

        def __call__(self, sub: list["Expression"] | None = None) -> Expression:
            return expr(self._t, sub)

    (MSG, HDR, TYPE) = tuple(map(ExprType, ("MSG", "HDR", "TYPE")))

    def unwind_stack(unwind_position):
        num_unwinds = len(stack) - unwind_position
        taken = []
        for _ in range(num_unwinds):
            taken.append(stack.pop(-1))
        return taken

    def to_stack():
        stack.append(current_token())
        consume_token()

    def empty_line():
        if next_token().kind == K.EOF:
            stack.append(MSG(unwind_stack(0)))
        consume_token()

    def eol():
        if not HDR.in_stack():
            if len(stack) == 0 or (
                len(stack) == 1
                and isinstance(stack[-1], Token)
                and stack[-1].kind == K.EMPTY_LINE
            ):
                problems.append(Problem(ProblemType.EMPTY_HDR, cast(Token, stack[-1])))
            elif isinstance(stack[-1], Token) and stack[-1].kind == K.DOT:
                problems.append(
                    Problem(ProblemType.HDR_ENDS_IN_DOT, cast(Token, stack[-1]))
                )
            elif not TYPE.in_stack():
                problems.append(Problem(ProblemType.NO_TYPE, cast(Token, stack[-1])))

            hdr = HDR(unwind_stack(0))
            stack.append(hdr)
        if next_token().kind == K.EOF:
            stack.append(MSG(unwind_stack(0)))
        consume_token()

    def divider():
        consume_token()
        if not TYPE.in_stack() and not HDR.in_stack():
            stack.append(TYPE(unwind_stack(0)))

    actions = {
        K.START: to_stack,
        K.EMPTY_LINE: empty_line,
        K.DIVIDER: divider,
        K.DOT: to_stack,
        K.WORD: to_stack,
        K.EOL: eol,
    }
    log = logging.getLogger(__name__)

    def build_debug_msg():
        return """
Stack:
------
{}

Queue:
------
{}


            """.format("\n".join(map(str, stack)), "\n".join(map(str, h)))

    while current_token().kind != K.EOF:
        log.debug(build_debug_msg())
        actions[h[0].kind]()

    log.debug(build_debug_msg())
    if not MSG.matches(stack[0]):
        raise ValueError("failed to parse msg")
    else:
        if cast(Expression, stack[0]).sub == [start]:
            problems.append(
                Problem(
                    ProblemType.EMPTY_HDR,
                    Token(K.EMPTY_LINE, value="", column=0, line=0),
                )
            )
    return problems
