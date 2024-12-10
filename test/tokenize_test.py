from pycolint.tokenizer import tokenize, Kind as T, Token
from pytest import fixture
from collections.abc import Callable


class CommitSummaryTest:
    @fixture
    def t(self) -> Callable[[str], list[Token]]:
        return tokenize

    def test_type_and_scope(self, t):
        msg = "feat(graphs)"
        assert [
            Token(*x, 1)
            for x in (
                (T.WORD, "feat", 1),
                (T.OP, "(", 5),
                (T.WORD, "graphs", 6),
                (T.CP, ")", 12),
                (T.EOL, "", 13),
            )
        ] == t(msg)

    def test_type_scope_and_text(self, t):
        msg = "feat(graphs): my message"
        assert [
            T.WORD,
            T.OP,
            T.WORD,
            T.CP,
            T.DIVIDER,
            T.WORD,
            T.WORD,
            T.EOL,
        ] == [x.kind for x in t(msg)]

    def test_find_exclamation(self, t):
        msg = "feat!: my feature"
        assert [T.WORD, T.EXCL, T.DIVIDER, T.WORD, T.WORD, T.EOL] == [
            x.kind for x in t(msg)
        ]

    def test_text_with_dot(self, t):
        msg = "my . text."
        assert [
            T.WORD,
            T.DOT,
            T.WORD,
            T.DOT,
            T.EOL,
        ] == [x.kind for x in t(msg)]

    def test_breaking_change(self, t):
        msg = "BREAKING CHANGE"
        assert [T.BREAKING_CHANGE, T.EOL] == [x.kind for x in t(msg)]

    def test_new_line(self, t):
        assert [T.NL, T.EOL] == [x.kind for x in t("\n")]

    def test_empty_string(self, t):
        assert [T.EOL] == [x.kind for x in t("")]

    def test_find_divider_with_more_whitespace(self, t):
        assert T.DIVIDER == t("feat:  ")[1].kind

    def test_parse_three_newline_as_three_newline_followed_by_eol(self, t):
        assert [T.NL, T.NL, T.NL, T.EOL] == [x.kind for x in t("\n\n\n")]
