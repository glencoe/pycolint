from enum import Enum, auto


class ProblemType(Enum):
    EMPTY_HDR = 0
    NO_TYPE = 1
    HDR_ENDS_IN_DOT = 2
    EMPTY_SCOPE = 3
    TOO_LONG_HDR = 4
    TOO_MUCH_WHITESPACE_AFTER_COLON = 5
    EMPTY_BODY = 6
    MISSING_BDY_SEP = 7
    USE_SINGLE_WORD_FOR_SCOPE = 8
    INVALID_TYPE = 9
    MISSING_DESCRIPTION = auto()
    MISSING_HDR = auto()
    EMPTY_MSG = auto()
    ERROR = auto()
    UNCLOSED_SCOPE = auto()
    UNOPENED_SCOPE = auto()
