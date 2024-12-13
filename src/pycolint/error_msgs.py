from .problem_types import ProblemType as _P
from .parser import Problem
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
    _P.TOO_MUCH_WHITESPACE_AFTER_COLON: """The colon after the scope or type needs to\n be followed by exactly *one* space character.""",
    _P.ERROR: """Failed to parse msg""",
    _P.INVALID_TYPE: """Invalid type. Specify type like this '<type>: <summary>'""",
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
        cols: list[tuple[int, int, str]] = []

        arrow_line = [" " for _ in range(len(line) + 3)]
        for p_nr, (p, p_msg) in enumerate((p, mapping[p.type]) for p in local_problems):
            arrow_line[p.token.column] = "^"
            num_rows = len(p_msg.splitlines())
            if len(cols) == 0:
                target_row = 1
            else:
                target_row = cols[-1][1] + num_rows + 1
            cols.append((p.token.column, target_row, p_msg))

        last_row = cols[-1][1]
        for _ in range(last_row):
            path_lines.append([" " for _ in range(len(arrow_line))])
        for col, last_row, msg in cols:
            for row in range(last_row):
                path_lines[row][col] = "|"
            for c in range(col, len(arrow_line)):
                if path_lines[last_row - 1][c] == "|":
                    path_lines[last_row - 1][c] = "+"
                else:
                    path_lines[last_row - 1][c] = "-"
            lines = msg.splitlines()
            msg_height = len(lines)
            for msg_line, line_id in enumerate(range(last_row - msg_height, last_row)):
                path_lines[line_id].append(lines[msg_line])
        print("".join(arrow_line), file=sys.stderr)

        for msg_parts in path_lines:
            print("".join(msg_parts), file=sys.stderr)
