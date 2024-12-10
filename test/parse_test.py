from pycolint.parser import parse, ProblemType as P, Problem
from pycolint.tokenizer import Kind as T, Token, tokenize


class ParseHdrTest:
    def test_empty_fails(self):
        assert [
            Problem(P.EMPTY_HDR, Token(kind=T.EOL, value="", line=1, column=1))
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

    def test_no_problems_from_parentheses_after_type(self):
        assert [] == parse(tokenize("feat(parser): msg with par ()"))

    def test_exclamation_mark_is_allowed(self):
        assert [] == parse(tokenize("feat!: msg"))

    def test_detect_too_long_hdr(self):
        assert (
            Problem(P.TOO_LONG_HDR, Token(kind=T.WORD, value="bla", column=49, line=1))
            == parse(tokenize("feat:                                           bla"))[
                -1
            ]
        )

    def test_detect_too_much_whitespace_after_colon(self):
        assert (
            Problem(
                P.TOO_MUCH_WHITESPACE_AFTER_COLON,
                Token(kind=T.DIVIDER, value=":  ", column=5, line=1),
            )
            == parse(tokenize("feat:  msg"))[0]
        )

    def test_let_divider_with_whitespace_in_the_middle_of_message_pass(self):
        assert [] == parse(tokenize("feat: my new:  message"))

    def test_pass_for_msg_body(self):
        assert [] == parse(tokenize("feat: msg\n\nmy body"))

    def test_detect_msg_with_empty_body(self):
        assert [
            Problem(P.EMPTY_BODY, Token(T.EOL, value="", column=2, line=2))
        ] == parse(tokenize("feat: msg\n"))

    def test_detect_missing_separator_for_body(self):
        assert P.MISSING_BDY_SEP == parse(tokenize("feat: msg\nbody too close"))[0].type

    def test_detect_whitespaces_in_scope(self):
        assert (
            P.USE_SINGLE_WORD_FOR_SCOPE
            == parse(tokenize("feat(sc ope): scope"))[0].type
        )
