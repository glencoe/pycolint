from pycolint.parser import parse, ProblemType as P, Problem
from pycolint.tokenizer import Kind as T, Token, tokenize


class ParseTest:
    def test_empty_header_fails(self):
        assert [
            Problem(P.EMPTY_HDR, Token(kind=T.EMPTY_LINE, value="", line=0, column=0))
        ] == parse(tokenize(""))

    def test_header_without_type_fails(self):
        assert [
            Problem(P.NO_TYPE, Token(kind=T.WORD, value="mytext", column=1, line=1))
        ] == parse(tokenize("mytext"))

    def test_header_ending_with_dot_fails(self):
        assert [
            Problem(P.HDR_ENDS_IN_DOT, Token(T.DOT, value=".", column=10, line=1))
        ] == parse(tokenize("feat: msg."))

    def test_header_empty_scope(self):
        assert [
            Problem(P.EMPTY_SCOPE, Token(T.CP, value=")", column=6, line=1))
        ] == parse(tokenize("feat(): msg"))
