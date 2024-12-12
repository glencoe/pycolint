from functools import partial, singledispatch, singledispatchmethod
from enum import Enum, auto
from typing import NamedTuple, Union, Callable
from dataclasses import dataclass
from .tokenizer import Token, Kind as T, tokenize
import logging
from .problem_types import ProblemType as P


class ExpressionType(Enum):
    START = auto()
    MSG = auto()
    HDR = auto()
    REST = auto()
    TYPE = auto()
    SCOPE = auto()
    DESCR = auto()
    BDY_MSG_SEP = auto()
    BODY = auto()
    TRAIL = auto()
    FOOTER = auto()


_E = ExpressionType


@dataclass
class Problem:
    type: P
    token: Token


class Expression(NamedTuple):
    type: ExpressionType
    sub: list[Union["Expression", Token]]


class Stack:
    def __init__(self) -> None:
        self.data: list[Expression | Token] = []

    def push(self, x: Expression | Token) -> None:
        self.data.append(x)

    def pop(self) -> Expression | Token:
        return self.data.pop(-1)

    def get_expressions(self) -> tuple[Expression, ...]:
        return tuple(e for e in self.data if isinstance(e, Expression))

    def last_expression(self) -> Expression | None:
        exprs = self.get_expressions()
        if len(exprs) > 0:
            return exprs[-1]
        return None

    def reduce(
        self,
        exp: ExpressionType,
        remove: int,
        select: tuple[int, ...],
    ) -> None:
        removed = list(reversed([self.pop() for _ in range(remove)]))
        selected = []
        for s in select:
            selected.append(removed[s])
        self.push(Expression(exp, selected))

    def top(self) -> Expression | Token:
        return self.data[-1]


class TokenQueue:
    def __init__(self, data: list[Token]):
        self._data = data

    def current(self) -> Token:
        return self._data[0]

    def advance(self) -> None:
        self._data.pop(0)

    def before_eof(self) -> bool:
        return self._data[0].kind == T.EOF


class ProblemList:
    def __init__(self, q: TokenQueue, data: list[Problem]):
        self._q = q
        self._data = data

    def add_problem(self, p: P) -> None:
        self._data.append(Problem(p, self._q.current()))


@dataclass
class Rule:
    """
    Empty set matches nothing, None matches everything
    """

    top_of_stack: Expression | ExpressionType | None | Token | T
    current_token: Token | T | None
    applicable_lhs: ExpressionType
    fn: Callable[[], None]

    def __str__(self) -> str:
        def get_simplified_str(item) -> str:
            if hasattr(item, "kind"):
                t = item.kind.name
            elif hasattr(item, "type"):
                t = item.type.name
            elif item is not None:
                t = item.name
            else:
                t = "None"
            return t

        top = get_simplified_str(self.top_of_stack)
        ct = get_simplified_str(self.current_token)
        applicable_lhs = (
            self.applicable_lhs if self.applicable_lhs is not None else None
        )
        return f"Rule:\n\ttop: {top}\n\tcurrent_token: {ct}\n\tapplicable lhs: {applicable_lhs}"


class Parser:
    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)
        self._tokens = TokenQueue([])
        self._stack = Stack()
        self._stack.push(Expression(_E.START, []))
        self._currently_parsing_lhs: dict[ExpressionType, int] = {
            _E.MSG: 0,
            _E.HDR: 0,
            _E.TYPE: 0,
        }
        self._p = ProblemList(self._tokens, [])
        self._rules: list[Rule] = []

        def noop():
            pass

        self._current_rule: Rule = Rule(None, None, _E.MSG, noop)

    def pretty_print_state(self) -> str:
        token = self._tokens.current()
        stack = "\n".join([str(d) for d in self._stack.data])
        lhs = {k.name: v for k, v in self._currently_parsing_lhs.items()}
        return f"""
current token
-------------
{token}

current stack
------------
{stack}


active lhs
-----------
{lhs}
        """

    def advance(self) -> None:
        self._tokens.advance()

    def reduce(self) -> None:
        new_type = self._current_rule.applicable_lhs
        num_symbols = self._currently_parsing_lhs[new_type]
        self._stack.reduce(new_type, num_symbols, tuple(range(num_symbols)))
        for k in self._currently_parsing_lhs:
            self._currently_parsing_lhs[k] -= num_symbols - 1
        self._currently_parsing_lhs.pop(new_type)

    def update_currently_parsing_lhs(self, lhs: ExpressionType) -> None:
        self._currently_parsing_lhs[lhs] = self._currently_parsing_lhs.get(lhs, 0)

    def push_token(self) -> None:
        c = self._tokens.current()
        for k in self._currently_parsing_lhs:
            self._currently_parsing_lhs[k] += 1
        self._stack.push(c)

    def add_problem(self, p: P):
        self._p.add_problem(p)

    def done(self) -> bool:
        t = self._stack.top()
        return isinstance(t, Expression) and t.type == _E.MSG

    def register_rule(self, handler: Rule) -> None:
        if handler not in self._rules:
            self._rules.append(handler)

    def parse(self, tokens: TokenQueue, problems: ProblemList):
        self._tokens = tokens
        self._p = problems
        while not self.done():
            for h in self._rules:
                if self.matches(h):
                    self._log.debug(self.pretty_print_state())
                    self._log.debug(f"\napplying {str(h)}\n\n")
                    self._current_rule = h
                    self._current_rule.fn()
                    break

    def matches(self, h: Rule) -> bool:
        match_top_of_stack = self._create_matcher(h.top_of_stack)
        match_current_token = self._create_matcher(h.current_token)

        def match_lhs(currently_parsing_lhs):
            if h.applicable_lhs is not None:
                return h.applicable_lhs in currently_parsing_lhs.keys()
            return True

        return (
            match_top_of_stack(self._stack.top())
            and match_current_token(self._tokens.current())
            and match_lhs(self._currently_parsing_lhs)
        )

    @singledispatchmethod
    def _create_matcher(self, left): ...

    @_create_matcher.register
    def _(self, left: Expression):
        @singledispatch
        def m(right):
            pass

        @m.register
        def _(right: Expression) -> bool:
            return left == right

        @m.register
        def _(right: object) -> bool:
            return False

        return m

    @_create_matcher.register
    def _(self, left: ExpressionType):
        @singledispatch
        def m(right):
            pass

        @m.register
        def _(right: Expression):
            return left == right.type

        @m.register
        def _(right: ExpressionType):
            return left == right

        @m.register
        def _(right: object):
            return False

        return m

    @_create_matcher.register
    def _(self, left: T):
        @singledispatch
        def m(right):
            pass

        @m.register
        def _(right: Token):
            return left == right.kind

        @m.register
        def _(right: T):
            return left == right

        @m.register
        def _(right: object):
            return False

        return m

    @_create_matcher.register
    def _(self, left: Token):
        @singledispatch
        def m(right):
            pass

        @m.register
        def _(right: Token):
            return left == right

        @m.register
        def _(right: object):
            return False

        return m

    @_create_matcher.register
    def _(self, left: None):
        def m(x):
            return True

        return m


def create_parser():
    """
    last reduce expression uniquely determines what right hand rule we're building
    at each moment, because

    MSG := HDR [REST]
    HDR := TYPE [SCOPE] ': ' DESCR
    SCOPE := '(' word ')'
    DESCR := word | DESCR word
    REST := '\n\n' BODY [FOOTER]
    BODY := ANY_SYMBOLS
    FOOTER := FOOTER_TAIL ': ' footer_tail ['\n' FOOTER]
    FOOTER_TAIL := any_symbol_except_new_line | FOOTER_TAIL any_symbol_except_new_line

    Tokens written in lowercase
    """
    E = _E
    p = Parser()

    def register_handler(
        top_of_stack: ExpressionType | None | Token | T,
        current_token: Token | T | None,
        valid_lhs: ExpressionType,
    ) -> Callable[[Callable[[], None]], Callable[[], None]]:
        def _r(fn: Callable[[], None]):
            p.register_rule(Rule(top_of_stack, current_token, valid_lhs, fn))
            return fn

        return _r

    rh = register_handler

    @rh(E.START, T.SKIP, E.TYPE)
    @rh(T.WORD, T.SKIP, E.TYPE)
    @rh(T.WORD, T.WORD, E.TYPE)
    def _():
        p.add_problem(P.INVALID_TYPE)
        p.advance()

    @rh(T.WORD, T.DIVIDER, E.TYPE)
    def _():
        p.reduce()
        p.update_currently_parsing_lhs(E.DESCR)

    @rh(E.START, T.WORD, E.HDR)
    @rh(E.TYPE, T.WORD, E.HDR)
    @rh(T.WORD, T.SKIP, E.HDR)
    @rh(T.SKIP, T.WORD, E.HDR)
    @rh(E.TYPE, T.WORD, E.DESCR)
    @rh(E.TYPE, T.DOT, E.DESCR)
    @rh(T.WORD, T.DOT, E.DESCR)
    @rh(E.SCOPE, T.DOT, E.DESCR)
    @rh(E.SCOPE, T.WORD, E.DESCR)
    @rh(E.TYPE, T.EXCL, E.HDR)
    @rh(E.SCOPE, T.EXCL, E.HDR)
    @rh(T.EXCL, T.WORD, E.DESCR)
    @rh(E.HDR, T.NL, E.BDY_MSG_SEP)
    @rh(E.BDY_MSG_SEP, T.WORD, E.BODY)
    @rh(T.WORD, T.WORD, E.BODY)
    def _():
        p.push_token()
        p.advance()

    @rh(E.HDR, T.NL, E.MSG)
    def _():
        p.update_currently_parsing_lhs(E.BDY_MSG_SEP)

    @rh(T.WORD, T.SKIP, E.BODY)
    @rh(T.WORD, T.EOL, E.BODY)
    @rh(E.TYPE, T.OPAR, E.SCOPE)
    @rh(E.TYPE, T.DIVIDER, E.DESCR)
    @rh(E.BDY_MSG_SEP, T.EOL, E.MSG)
    def _():
        p.advance()

    @rh(T.NL, T.EOL, E.BDY_MSG_SEP)
    @rh(E.HDR, T.EOL, E.BDY_MSG_SEP)
    @rh(T.NL, T.NL, E.BDY_MSG_SEP)
    @rh(T.WORD, T.CPAR, E.SCOPE)
    @rh(E.DESCR, T.EOL, E.HDR)
    @rh(E.BDY_MSG_SEP, T.NL, E.MSG)
    def _():
        p.reduce()
        p.advance()

    @rh(E.BDY_MSG_SEP, T.EOF, E.MSG)
    def _():
        p.add_problem(P.EMPTY_BODY)
        p.reduce()

    @rh(E.BDY_MSG_SEP, T.WORD, E.MSG)
    def _():
        p.update_currently_parsing_lhs(E.BODY)

    @rh(E.TYPE, T.SKIP, E.HDR)
    def _():
        p.add_problem(P.TOO_MUCH_WHITESPACE_AFTER_COLON)
        p.advance()

    @rh(T.WORD, T.CPAR, E.TYPE)
    def _():
        p.add_problem(P.UNOPENED_SCOPE)
        p.reduce()
        p.update_currently_parsing_lhs(E.DESCR)
        p.advance()

    @rh(E.TYPE, T.OPAR, E.HDR)
    def _():
        p.update_currently_parsing_lhs(E.SCOPE)

    @rh(E.TYPE, T.EOL, E.DESCR)
    def _():
        p.add_problem(P.MISSING_DESCRIPTION)
        p.reduce()

    @rh(T.WORD, T.DIVIDER, E.SCOPE)
    def _():
        p.add_problem(P.UNCLOSED_SCOPE)
        p.reduce()

    @rh(E.SCOPE, T.DIVIDER, E.HDR)
    @rh(T.EXCL, T.DIVIDER, E.HDR)
    def _():
        p.update_currently_parsing_lhs(E.DESCR)
        p.advance()

    @rh(T.DOT, T.EOL, E.DESCR)
    def _():
        p.add_problem(P.HDR_ENDS_IN_DOT)
        p.reduce()

    @rh(E.START, T.EOL, E.MSG)
    @rh(E.START, T.EOL, E.HDR)
    @rh(E.START, T.EOL, E.DESCR)
    def _():
        p.add_problem(P.EMPTY_HDR)
        p.push_token()
        p.advance()

    @rh(E.TYPE, T.DIVIDER, E.SCOPE)
    def _():
        p.add_problem(P.INVALID_TYPE)
        p.reduce()
        p.update_currently_parsing_lhs(E.DESCR)
        p.advance()

    @rh(E.TYPE, T.DIVIDER, E.HDR)
    def _():
        p.update_currently_parsing_lhs(E.DESCR)
        p.advance()

    @rh(T.WORD, T.EXCL, E.TYPE)
    @rh(T.NL, T.WORD, E.BDY_MSG_SEP)
    @rh(T.WORD, T.OPAR, E.TYPE)
    @rh(T.EOL, T.EOF, E.TYPE)
    @rh(T.EOL, T.EOF, E.HDR)
    @rh(T.EOL, T.EOF, E.MSG)
    @rh(T.WORD, T.EOF, E.BODY)
    @rh(E.BODY, T.EOF, E.MSG)
    @rh(E.HDR, T.EOF, E.MSG)
    @rh(T.WORD, T.NL, E.DESCR)
    @rh(T.WORD, T.EOL, E.DESCR)
    @rh(E.DESCR, T.NL, E.HDR)
    def _():
        p.reduce()

    rh = partial(register_handler, valid_lhs=E.MSG)

    @rh(None, None)
    def default():
        p.add_problem(P.ERROR)
        p.reduce()

    def parse(text: str) -> list[Problem]:
        token_list = tokenize(text)
        token_list.append(Token(T.EOF, value="", column=-1, line=-1))
        tokens = TokenQueue(token_list)

        problems: list[Problem] = []
        p.parse(tokens, ProblemList(tokens, problems))
        return problems

    return parse
