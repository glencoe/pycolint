from .parser import create_parser
from .error_msgs import print_msgs, DEFAULT_PROBLEM_MAP
import sys


def main():
    msg = " ".join(sys.argv[1:])
    parse = create_parser()
    problems = parse(msg)
    print_msgs(DEFAULT_PROBLEM_MAP, msg, problems)
    if len(problems) > 0:
        exit(1)


if __name__ == "__main__":
    main()
