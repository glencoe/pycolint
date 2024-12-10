from pycolint.parser import parse, ProblemType as P, Problem
from pycolint.tokenizer import Kind as T, Token, tokenize


class ParseHdrTest:
    def test_empty_fails(self):
        assert [
            Problem(P.EMPTY_HDR, Token(kind=T.EMPTY_LINE, value="", line=0, column=0))
        ] == parse(tokenize(""))

    def test_without_type_fails(self):
        assert [
            Problem(P.NO_TYPE, Token(kind=T.WORD, value="mytext", column=1, line=1))
        ] == parse(tokenize("mytext"))

    def test_ending_with_dot_fails(self):
        assert [
            Problem(P.HDR_ENDS_IN_DOT, Token(T.DOT, value=".", column=10, line=1))
        ] == parse(tokenize("feat: msg."))

    def test_empty_scope_fails(self):
        assert [
            Problem(P.EMPTY_SCOPE, Token(T.CP, value=")", column=6, line=1))
        ] == parse(tokenize("feat(): msg"))

    def test_no_problems_from_later_parentheses(self):
        assert [] == parse(tokenize("feat: my ()"))

    def test_no_problems_from_parentheses_after_scope(self):
        assert [] == parse(tokenize("feat(parser): msg with par ()"))

    def test_exclamation_mark_is_allowed(self):
        assert [] == parse(tokenize("feat!: msg"))

    def test_detect_too_long_hdr(self):
        assert [
            Problem(P.TOO_LONG_HDR, Token(kind=T.WORD, value="bla", column=49, line=1))
        ] == parse(tokenize("feat:                                           bla"))
