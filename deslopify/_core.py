import json
import subprocess
from pathlib import Path
from tempfile import gettempdir
from shutil import rmtree
from dataclasses import dataclass


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

AI_FILES = (
    '.claude-plugin/',
    '.codex-plugin/',
    '.devin-plugin/',
    '.grok-plugin/',
    '.kimi-plugin/',
    '.qoder-plugin/',

    '.agents/',
    '.clinerules/',
    '.cursor/',
    '.kiro/',
    '.openclaw/',
    '.opencode/',
    '.qoder/',
    '.windsurf/',
    'skills/',

    'AGENTS.md',
    'CLAUDE.md',
    'gemini-extension.json',
    'opencode.json',
)


@dataclass
class Commit:
    hash: str
    author: str
    trailers: str
    committer: str
    date: str
    message: str
    ai: str | None = None
    ai_files: bool = False


def clone_repo(url: str) -> Path:
    project_name = url.strip('/').split('/')[-1]
    out_dir = Path(gettempdir()) / project_name
    if not (out_dir / '.git' / 'config').exists():
        rmtree(out_dir, ignore_errors=True)
        cmd = ['git', 'clone', '--no-checkout', url, str(out_dir)]
        subprocess.run(cmd, stderr=subprocess.DEVNULL).check_returncode()
    return out_dir


def get_commits(root: Path) -> list[Commit]:
    commits: list[Commit] = []
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
        commit.date = commit.date.split()[0]
        commits.append(commit)

    cmd = ['git', 'log', '--diff-filter=A', '--pretty=format:%H', '--']
    cmd.extend(AI_FILES)
    out = subprocess.run(cmd, stdout=subprocess.PIPE, cwd=root)
    out.check_returncode()
    hashes = set(out.stdout.decode('utf-8').splitlines())
    for commit in commits:
        commit.ai_files = commit.hash in hashes

    commits.reverse()
    return commits


def detect_ai(commit: Commit) -> str | None:
    for telltale, name in TELLTALES:
        if telltale in commit.author:
            return f'authored by {name}'
        if telltale in commit.committer:
            return f'committed by {name}'
        if telltale in commit.trailers:
            return f'co-authored by {name}'
    if commit.ai_files:
        return 'introduced AI prompts'
    return None


def get_tag_for(commit: Commit, root: Path) -> str | None:
    cmd = ['git', 'describe', '--contains', commit.hash]
    out = subprocess.run(cmd, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if out.returncode != 0:
        return None
    return out.stdout.decode(encoding='utf-8').split('~')[0]


def find_tag_before(tag: str, root: Path) -> str | None:
    cmd = ['git', 'tag', '--sort=version:refname']
    out = subprocess.run(cmd, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if out.returncode != 0:
        return None
    tags = out.stdout.decode(encoding='utf-8').splitlines()
    try:
        i = tags.index(tag)
    except ValueError:
        return None
    if i == 0:
        return None
    return tags[i-1]
