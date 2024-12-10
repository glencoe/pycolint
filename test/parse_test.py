from pycolint.parser import parse, Problem as P
from pycolint.tokenizer import Kind as T


class ParseTest:
    def test_empty_header_fails(self):
        assert [P.EMPTY_HDR] == parse([(T.EMPTY_LINE, ""), (T.EOL, "")])

    def test_header_without_type_fails(self):
        assert [P.NO_TYPE] == parse(
            [(T.WORD, "mytext"), (T.EOL, "")],
        )

    def test_header_ending_with_dot_fails(self):
        assert [P.HDR_ENDS_IN_DOT] == parse(
            [
                (T.WORD, "feat"),
                (T.DIVIDER, ": "),
                (T.WORD, "description"),
                (T.DOT, "."),
                (T.EOL, ""),
            ]
        )
