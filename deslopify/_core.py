import json
import subprocess
from pathlib import Path
from tempfile import gettempdir
from shutil import rmtree
from dataclasses import dataclass, field


@dataclass
class Commit:
    hash: str
    author: str
    trailers: str
    committer: str
    date: str
    message: str
    files: list[str] = field(default_factory=list)
    ai: str | None = None


def clone_repo(url: str) -> Path:
    project_name = url.strip('/').split('/')[-1]
    out_dir = Path(gettempdir()) / project_name
    rmtree(out_dir, ignore_errors=True)
    cmd = ['git', 'clone', '--no-checkout', url, str(out_dir)]
    subprocess.run(cmd).check_returncode()
    return out_dir


def get_commits(root: Path) -> list[Commit]:
    commits = []
    fmt = r"""format:{"hash": "%H","author":"%aN <%aE>","trailers":"%(trailers:separator=%x2c)","committer":"%cN <%cE>","date":"%ai","message":"%f"}%n"""
    cmd = ['git', 'log', '--pretty='+fmt]
    out = subprocess.run(cmd, stdout=subprocess.PIPE, cwd=root)
    out.check_returncode()
    for line in out.stdout.decode(encoding='utf-8').split('\n\n'):
        line = line.replace('\n', ' ').strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.decoder.JSONDecodeError:
            continue
        commit = Commit(**parsed)
        cmd = ['git', 'diff-tree', '--no-commit-id', '--name-status', commit.hash, '-r']
        out = subprocess.run(cmd, stdout=subprocess.PIPE, cwd=root)
        out.check_returncode()
        commit.files = out.stdout.decode(encoding='utf-8').splitlines()
        commits.append(commit)
    commits.reverse()
    return commits


TELLTALES = (
    # names
    ('Claude', 'Claude'),
    ('Cursor Agent', 'Cursor'),
    ('Copilot', 'Github Copilot'),

    # emails
    ('<noreply@anthropic.com>', 'Claude'),
    ('<cursoragent@cursor.com>', 'Cursor'),
    ('<noreply@aider.chat>', 'Aider'),

    # custom trailers
    ('aider:', 'Aider'),
    ('Made-with:', 'an LLM'),
    ('Generated-by:', 'an LLM'),
    ('Assisted-by:', 'an LLM'),
)


def detect_ai(commit: Commit) -> str | None:
    for telltale, name in TELLTALES:
        if telltale in commit.author:
            return f'authored by {name}'
        if telltale in commit.trailers:
            return f'co-authored by {name}'
    if 'AGENTS.md' in commit.files:
        return 'introduced AGENTS.md'
    if 'CLAUDE.md' in commit.files:
        return 'introduced CLAUDE.md'
    for file in commit.files:
        if file.startswith('.agents/'):
            return 'introduced agents files'
    return None
