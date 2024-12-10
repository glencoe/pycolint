from .parser import ProblemType as _P, Problem
import sys


DEFAULT_PROBLEM_MAP = {
    _P.EMPTY_BODY: """If you have a new line after the header you also need to add a msg body.""",
    _P.NO_TYPE: """You have to specify a type as follows
<type>[<optional-scope>]: <description>

The type will have influence on automatic versioning.
`feat` will increase the major version while `fix` will increas
the minor version.
    """,
    _P.HDR_ENDS_IN_DOT: """The commit msg header may not end with a dot""",
    _P.TOO_LONG_HDR: """Your header exceeded the maximum length of 50 characters.
If you have more to say, add an in-depth description of you changes in the msg body:

<header>
<empty-line>
<body>
""",
    _P.MISSING_BDY_SEP: """You need to add an empty line between header and body
<header>
<empty-line>
<body>""",
    _P.USE_SINGLE_WORD_FOR_SCOPE: """Scope should be specified with a single word""",
    _P.TOO_MUCH_WHITESPACE_AFTER_COLON: """The colon after the scope or type needs to be followed by exactly *one* space character.""",
}


def print_msgs(mapping: dict[_P, str], commit_msg: str, problems: list[Problem]):
    lines = commit_msg.splitlines()
    for nr, line in enumerate(lines):
        print(line, file=sys.stderr)
        local_problems = []
        for p in problems:
            if p.token.line - 1 == nr:
                local_problems.append(p)
        path_lines = []
        cols = []
        arrow_line = [" " for _ in range(len(line) + 3)]
        for p_nr, p in enumerate(local_problems):
            arrow_line[p.token.column] = "^"
            cols.append(p.token.column)
            num_rows = len(mapping[p.type].splitlines())
            for _ in range(num_rows):
                path_lines.append([" " for _ in range(len(arrow_line))])
        print("".join(arrow_line), file=sys.stderr)

        for p in local_problems:
            for pl, error in zip(path_lines, mapping[p.type].splitlines()):
                pls = "".join(pl)
                print(f"{pls} | {error}", file=sys.stderr)
