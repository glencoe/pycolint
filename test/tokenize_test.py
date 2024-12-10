from pycolint.tokenizer import Tokenizer, Kind as T
from pytest import fixture


class CommitSummaryTest:
    @fixture
    def t(self) -> Tokenizer:
        return Tokenizer()

    def test_type_and_scope(self, t):
        msg = "feat(graphs)"
        assert [
            (T.WORD, "feat"),
            (T.OP, "("),
            (T.WORD, "graphs"),
            (T.CP, ")"),
            (T.EOL, ""),
        ] == t(msg)

    def test_type_scope_and_text(self, t):
        msg = "feat(graphs): my message"
        assert [
            (T.WORD, "feat"),
            (T.OP, "("),
            (T.WORD, "graphs"),
            (T.CP, ")"),
            (T.DIVIDER, ": "),
            (T.WORD, "my"),
            (T.WORD, "message"),
            (T.EOL, ""),
        ] == t(msg)

    def test_text_with_dot(self, t):
        msg = "my . text."
        assert [
            (T.WORD, "my"),
            (T.DOT, "."),
            (T.WORD, "text"),
            (T.DOT, "."),
            (T.EOL, ""),
        ] == t(msg)

    def test_breaking_change(self, t):
        msg = "BREAKING CHANGE"
        assert [(T.BREAKING_CHANGE, "BREAKING CHANGE"), (T.EOL, "")] == t(msg)

    def test_empty_line(self, t):
        assert [(T.EMPTY_LINE, ""), (T.EOL, "")] == t("\n")
