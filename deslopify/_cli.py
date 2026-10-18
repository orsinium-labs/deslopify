from pathlib import Path
import sys
from argparse import ArgumentParser
from typing import NoReturn
from ._core import clone_repo, get_commits, detect_ai, Commit, get_tag_for


def run() -> int:
    parser = ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args(sys.argv[1:])
    print('cloning...')
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
    if not n_ai:
        print('no AI usage detected')
        return 0
    n_all = len(commits)
    print('AI commits:   ', f'{n_ai}/{n_all} ({round(n_ai/n_all*100)}%)')

    for commit in commits:
        if not commit.ai:
            continue
        print('first AI commit: ')
        print_commit(commit, root)
        break

    for commit in reversed(commits):
        if not commit.ai:
            continue
        print('last AI commit: ')
        print_commit(commit, root)
        break

    return 0


def print_commit(commit: Commit, root: Path) -> None:
    print('  hash:   ', commit.hash)
    print('  date:   ', commit.date)
    print('  author: ', commit.author)
    tag = get_tag_for(commit, root)
    if tag:
        print('  release:', tag)
    print('  reason: ', commit.ai)


def entrypoint() -> NoReturn:
    sys.exit(run())
