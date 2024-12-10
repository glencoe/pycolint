import re
from enum import Enum


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


class Tokenizer:
    tokens: dict[Kind, str] = {
        Kind.DIVIDER: r": (?=\S)",
        Kind.EMPTY_LINE: r"^$",
        Kind.BREAKING_CHANGE: r"BREAKING-CHANGE|(?:BREAKING CHANGE)",
        Kind.EOL: r"$",
        Kind.OP: r"\(",
        Kind.CP: r"\)",
        Kind.DOT: r"\.",
        Kind.SKIP: r"\s+",
        Kind.WORD: r"[^\s().:]+",
    }

    def __call__(self, text: str) -> list[tuple[Kind, str]]:
        regex = "|".join(
            "(?P<{name}>{token})".format(name=name.value, token=token)
            for name, token in self.tokens.items()
        )
        tokens: list[tuple[Kind, str]] = []
        for mo in re.finditer(regex, text):
            kind = Kind[mo.lastgroup] if mo.lastgroup is not None else None
            value = mo.group()
            if kind is not None and kind != Kind.SKIP:
                tokens.append((kind, value))
        return tokens
