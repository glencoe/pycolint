import re
from enum import Enum
from dataclasses import dataclass


class Kind(Enum):
    BREAKING_CHANGE = "BREAKING_CHANGE"
    DIVIDER = "DIVIDER"
    EMPTY_LINE = "EMPTY_LINE"
    EOL = "EOL"
    OP = "OP"
    CP = "CP"
    DOT = "DOT"
    SKIP = "SKIP"
    WORD = "WORD"
    EOF = "EOF"
    START = "START"
    EXCL = "EXCL"
    NL = "NL"


@dataclass(frozen=True, eq=True)
class Token:
    kind: Kind
    value: str
    column: int
    line: int


class Tokenizer:
    tokens: dict[Kind, str] = {
        Kind.DIVIDER: r": \s*",
        Kind.NL: r"\n",
        Kind.BREAKING_CHANGE: r"BREAKING-CHANGE|(?:BREAKING CHANGE)",
        Kind.EOL: r"$",
        Kind.OP: r"\(",
        Kind.CP: r"\)",
        Kind.DOT: r"\.",
        Kind.SKIP: r"\s+",
        Kind.EXCL: r"!",
        Kind.WORD: r"[^\s().:!]+",
    }

    def __call__(self, text: str) -> list[Token]:
        regex = "|".join(
            "(?P<{name}>{token})".format(name=name.value, token=token)
            for name, token in self.tokens.items()
        )
        tokens: list[Token] = []
        line_start = 0
        line = 1
        for mo in re.finditer(regex, text):
            kind = Kind[mo.lastgroup] if mo.lastgroup is not None else None
            value = mo.group()
            column = mo.start() - line_start + 1
            if kind is not None:
                match kind:
                    case Kind.SKIP:
                        continue
                    case _:
                        tokens.append(Token(kind, value, column, line))
                        if kind == Kind.NL:
                            line_start = mo.start()
                            line += 1

        return tokens


def tokenize(text: str) -> list[Token]:
    t = Tokenizer()
    return t(text)
