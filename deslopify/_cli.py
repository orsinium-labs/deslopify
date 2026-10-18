import sys
from argparse import ArgumentParser
from typing import NoReturn, TextIO
from ._core import clone_repo, get_commits


def run() -> int:
    parser = ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args(sys.argv[1:])
    root = clone_repo(args.url)
    commits = get_commits(root)
    if not commits:
        print('empty repo')
        return 1
    print('total commits:', len(commits))
    print('first commit: ', commits[0].date)
    print('last commit:  ', commits[-1].date)
    return 0


def entrypoint() -> NoReturn:
    sys.exit(run())
