from pycolint.parser import (
    Stack as _Stack,
    Expression,
    ExpressionType as E,
    create_parser,
)
from pycolint.problem_types import ProblemType as P
from pycolint.tokenizer import Kind as T, Token as _Token
import pytest


def token(t: T) -> _Token:
    return _Token(t, "", 0, 0)


def expression(t: E) -> Expression:
    return Expression(t, [])


def stack_item(t: T | E) -> _Token | Expression:
    if isinstance(t, T):
        return token(t)
    return expression(t)


def unwrap_type(item: _Token | Expression) -> T | E:
    if isinstance(item, _Token):
        return item.kind
    else:
        return item.type


class SimplifiedStack:
    def __init__(self, s: _Stack) -> None:
        self.s = s

    def push(self, item: T | E):
        self.s.push(stack_item(item))

    def pop(self) -> T | E:
        return unwrap_type(self.s.pop())

    def reduce(self, type: E, remove: int, select: tuple[int, ...]) -> None:
        self.s.reduce(type, remove, select)


class StackTest:
    def test_stack_is_lifo(self):
        s = SimplifiedStack(_Stack())
        s.push(E.BODY)
        s.push(E.DESCR)
        s.push(T.CPAR)

        assert [T.CPAR, E.DESCR] == [s.pop() for _ in range(2)]

    def test_can_reduce_stack(self):
        _s = _Stack()
        s = SimplifiedStack(_s)
        for t in (E.TYPE, T.OPAR, T.WORD, T.CPAR):
            s.push(t)
        s.reduce(E.SCOPE, 3, (1,))
        assert Expression(E.SCOPE, [token(T.WORD)]) == _s.top()


class NewParserCorrectStringsTest:
    @pytest.fixture
    def parse(self) -> None:
        return create_parser()

    def test_single_word_correct_hdr(self, parse) -> None:
        assert [] == parse("feat: descr")

    def test_multi_word_hdr(self, parse) -> None:
        assert [] == parse("feat: one two")

    def test_scope(self, parse) -> None:
        assert [] == parse("feat(s): msg")

    def test_excl_after_type(self, parse) -> None:
        assert [] == parse("feat!: msg")

    def test_excl_after_scope(self, parse) -> None:
        assert [] == parse("feat(s)!: msg")

    def test_msg_with_body(self, parse) -> None:
        assert [] == parse("feat: msg\n\nmy body")

    def test_multiples_newlines_with_body_are_ok(self, parse) -> None:
        assert [] == parse("feat: msg\n\n\n\nmy body")


class NewParserFindProblemsTest:
    @pytest.fixture
    def parse(self) -> None:
        return create_parser()

    @pytest.fixture
    def find_problems(self, parse):
        def f(text):
            problems = parse(text)
            return [p.type for p in problems]

        return f

    def test_empty_string_fails(self, find_problems) -> None:
        assert [P.EMPTY_HDR] == find_problems("")

    def test_double_space_after_colon_is_error(self, find_problems) -> None:
        assert [P.TOO_MUCH_WHITESPACE_AFTER_COLON] == find_problems(
            "feat:  double white"
        )

    def test_space_before_type(self, find_problems) -> None:
        assert [P.INVALID_TYPE] == find_problems(" feat: msg")

    def test_double_space_before_type(self, find_problems) -> None:
        assert [P.INVALID_TYPE] == find_problems("  feat: msg")

    def test_space_before_divider(self, find_problems) -> None:
        assert [P.INVALID_TYPE] == find_problems("feat : msg")

    def test_double_word_before_divider(self, find_problems) -> None:
        assert [P.INVALID_TYPE, P.INVALID_TYPE] == find_problems("a b: msg")

    def test_invalid_type_for_opar(self, find_problems) -> None:
        assert [P.INVALID_TYPE] == find_problems("f(: a")

    def test_missing_close_scope(self, find_problems) -> None:
        assert [P.UNCLOSED_SCOPE] == find_problems("feat(s: descr")

    def test_missing_open_scope(self, find_problems) -> None:
        assert [P.UNOPENED_SCOPE] == find_problems("feats): descr")

    def test_missing_descr(self, find_problems) -> None:
        assert [P.MISSING_DESCRIPTION] == find_problems("feats: ")

    def test_end_with_dot(self, find_problems) -> None:
        assert [P.HDR_ENDS_IN_DOT] == find_problems("feats: a.")

    def test_empty_body(self, find_problems) -> None:
        assert [P.EMPTY_BODY] == find_problems("feats: a\n")

    def test_empty_body_with_double_nl(self, find_problems) -> None:
        assert [P.EMPTY_BODY] == find_problems("feats: a\n\n")
