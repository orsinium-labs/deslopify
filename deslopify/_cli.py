import sys
from argparse import ArgumentParser
from collections import Counter
from typing import NoReturn, TextIO
from ._core import Commit, clone_repo, find_tag_before, get_commits, detect_ai, get_tag_for

NO_AI = 0
AI = 1
ERR = 2

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
END = '\033[0m'


def entrypoint() -> NoReturn:
    sys.exit(run(sys.stdout))


def run(stdout: TextIO) -> int:
    parser = ArgumentParser()
    parser.add_argument('urls', nargs='+')
    args = parser.parse_args(sys.argv[1:])
    max_code = 0
    for url in args.urls:
        code = run_one(url, stdout)
        max_code = max(max_code, code)
    return max_code


def run_one(url: str, stdout: TextIO) -> int:
    def show(field: str, *args: str):
        if args:
            field = f'{MAGENTA}{field}{END}'
        elif field.endswith('...'):
            field = f'{BLUE}{field}{END}'
        print(' ', field, *args, file=stdout)

    print(f'{GREEN}{url}{END}', file=stdout)
    show('cloning...')
    root = clone_repo(url)
    show('analyzing...')
    commits = get_commits(root)
    if not commits:
        show('empty repo')
        return NO_AI
    for commit in commits:
        commit.ai = detect_ai(commit)

    show('total commits:', f'{len(commits):>6}     from {commits[0].date} to {commits[-1].date}')
    n_ai = sum(1 for c in commits if c.ai)
    if not n_ai:
        show('no AI usage detected')
        return NO_AI

    first_ai: Commit | None = None
    for commit in commits:
        if commit.ai:
            first_ai = commit
            break
    assert first_ai
    last_ai: Commit | None = None
    for commit in reversed(commits):
        if commit.ai:
            last_ai = commit
            break
    assert last_ai

    n_all = len(commits)
    percent = round(n_ai/n_all*100)
    show('AI commits:   ', f'{n_ai:>6} {BLUE}{percent:>2}%{END} from {first_ai.date} to {last_ai.date}')
    for reason, n in Counter(c.ai for c in commits).most_common():
        if reason is not None:
            show(f'  {n:>5} {YELLOW}{reason}{END}')

    for commit in commits:
        if not commit.ai:
            continue
        show(f'{MAGENTA}first AI commit:{END}')
        show('  hash:   ', commit.hash)
        show('  date:   ', commit.date)
        show('  author: ', commit.author)
        tag = get_tag_for(commit, root)
        if tag:
            show('  release:', f'{RED}{tag}{END}')
        show('  reason: ', f'{YELLOW}{commit.ai}{END}')
        break

    for commit in commits:
        if commit.ai:
            ai_tag = get_tag_for(commit, root)
            if ai_tag:
                prev_tag = find_tag_before(ai_tag, root)
                if prev_tag:
                    show('last AI-free release:', f'{GREEN}{prev_tag}{END}')
            break

    return AI
