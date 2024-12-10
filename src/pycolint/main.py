from .parser import parse
from .tokenizer import tokenize
from .error_msgs import print_msgs, DEFAULT_PROBLEM_MAP
import sys

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:])
    tokens = tokenize(msg)
    problems = parse(tokens)
    print_msgs(DEFAULT_PROBLEM_MAP, msg, problems)
    if len(problems) > 0:
        exit(1)
