from pycolint.tokenizer import Tokenizer, Kind as T, Token
from pytest import fixture


class CommitSummaryTest:
    @fixture
    def t(self) -> Tokenizer:
        return Tokenizer()

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

    def test_empty_line(self, t):
        assert [T.EMPTY_LINE, T.EOL] == [x.kind for x in t("\n")]
