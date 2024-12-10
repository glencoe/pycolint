from typing import TypeAlias, NamedTuple, Protocol
from pycolint.msg_types import get_msg_types
from pycolint.tokenizer import Kind as K
from collections.abc import Iterable
from enum import Enum

Token: TypeAlias = tuple[str, str]


class CommitMsgError(Exception):
    pass


class Problem(Enum):
    EMPTY_HDR = 0
    NO_TYPE = 1
    HDR_ENDS_IN_DOT = 2


def _create_msg(p: Problem) -> str:
    def empty_hdr() -> str:
        return "commit msg header may not be empty"

    def no_type() -> str:
        return "no type specified, valid types are {}".format(
            ", ".join(get_msg_types())
        )

    return (empty_hdr, no_type)[p.value]()


def parse(msg: Iterable[tuple[K, str]]) -> list[Problem]:
    msg_iter = iter(msg)
    problems = []
    problems.extend(_parse_header(msg_iter))
    return problems


def _parse_header(h: Iterable[tuple[K, str]]) -> list[Problem]:
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

    stack: list[Expression | tuple[K, str]] = []
    problems = []

    class ExprType:
        def __init__(self, t: str):
            self._t = t

        def matches(self, o: object) -> bool:
            return matches_expr(o, self._t)

        def in_stack(self) -> bool:
            return any(map(self.matches, stack))

        def __call__(self, sub: list["Expression"] | None = None) -> Expression:
            return expr(self._t, sub)

    (HDR, TYPE) = tuple(map(ExprType, ("HDR", "TYPE")))

    def unwind_stack(unwind_position):
        num_unwinds = len(stack) - unwind_position
        taken = []
        for _ in range(num_unwinds):
            taken.append(stack.pop(-1))
        return taken

    def add(token):
        stack.append(token)

    def eol(token):
        print(stack)

        if not HDR.in_stack():
            if len(stack) == 1 and stack[-1][0] == K.EMPTY_LINE:
                problems.append(Problem.EMPTY_HDR)
            elif stack[-1][0] == K.DOT:
                problems.append(Problem.HDR_ENDS_IN_DOT)
            elif not TYPE.in_stack():
                problems.append(Problem.NO_TYPE)

            hdr = HDR(unwind_stack(0))
            stack.append(hdr)

    def divider(_):
        if not TYPE.in_stack() and not HDR.in_stack():
            stack.append(TYPE(unwind_stack(0)))

    handlers = {
        K.EMPTY_LINE: add,
        K.DIVIDER: add,
        K.DOT: add,
        K.WORD: add,
        K.EOL: eol,
    }
    for token in h:
        kind, _ = token
        handlers[kind](token)

    return problems
