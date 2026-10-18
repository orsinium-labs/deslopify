import sys
from argparse import ArgumentParser
from typing import NoReturn
from ._core import clone_repo, get_commits, detect_ai


def run() -> int:
    parser = ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args(sys.argv[1:])
    root = clone_repo(args.url)
    print('analyzing...')
    commits = get_commits(root)
    if not commits:
        print('empty repo')
        return 1
    for commit in commits:
        commit.ai = detect_ai(commit)

    print('total commits:', len(commits))
    print('first commit: ', commits[0].date)
    print('last commit:  ', commits[-1].date)
    n_ai = sum(1 for c in commits if c.ai)
    n_all = len(commits)
    print('AI commits:   ', f'{n_ai}/{n_all} ({round(n_ai/n_all*100)}%)')

    for commit in commits:
        if not commit.ai:
            continue
        print('first AI commit: ')
        print('  hash:  ', commit.hash)
        print('  date:  ', commit.date)
        print('  author:', commit.author)
        print('  reason:', commit.ai)
        break

    for commit in reversed(commits):
        if not commit.ai:
            continue
        print('last AI commit: ')
        print('  hash:  ', commit.hash)
        print('  date:  ', commit.date)
        print('  author:', commit.author)
        print('  reason:', commit.ai)
        break

    return 0


def entrypoint() -> NoReturn:
    sys.exit(run())
