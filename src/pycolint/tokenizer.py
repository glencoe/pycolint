import re
from enum import Enum
from dataclasses import dataclass


class Kind(Enum):
    BREAKING_CHANGE = "BREAKING_CHANGE"
    DIVIDER = "DIVIDER"
    EMPTY_LINE = "EMPTY_LINE"
    EOL = "EOL"
    OPAR = "OPAR"
    CPAR = "CPAR"
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
        Kind.DIVIDER: r": ",
        Kind.NL: r"\n",
        Kind.BREAKING_CHANGE: r"BREAKING-CHANGE|(?:BREAKING CHANGE)",
        Kind.OPAR: r"\(",
        Kind.CPAR: r"\)",
        Kind.DOT: r"\.",
        Kind.SKIP: r"\s+",
        Kind.EXCL: r"!",
        Kind.WORD: r"[^\s().:!]+",
        Kind.EOL: r"$",
    }

    def __call__(self, text: str) -> list[Token]:
        regex = "|".join(
            "(?P<{name}>{token})".format(name=name.value, token=token)
            for name, token in self.tokens.items()
        )
        tokens: list[Token] = []
        line_start = 0
        line = 1
        last_kind = Kind.NL
        for mo in re.finditer(regex, text):
            kind = Kind[mo.lastgroup] if mo.lastgroup is not None else None
            value = mo.group()
            column = mo.start() - line_start + 1
            if kind is not None:
                if last_kind == Kind.SKIP and kind == Kind.SKIP:
                    continue
                else:
                    tokens.append(Token(kind, value, column, line))
                    if kind == Kind.NL:
                        line_start = mo.start()
                        line += 1

        return tokens


def tokenize(text: str) -> list[Token]:
    t = Tokenizer()
    return t(text)
