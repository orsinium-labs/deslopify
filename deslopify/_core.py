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
    coauthor: str
    committer: str
    date: str
    message: str
    files: list[str] = field(default_factory=list)


def clone_repo(url: str) -> Path:
    project_name = url.strip('/').split('/')[-1]
    out_dir = Path(gettempdir()) / project_name
    rmtree(out_dir, ignore_errors=True)
    cmd = ['git', 'clone', '--no-checkout', url, str(out_dir)]
    subprocess.run(cmd).check_returncode()
    return out_dir


def get_commits(root: Path) -> list[Commit]:
    commits = []
    fmt = r"""format:{"hash": "%H","author":"%aN <%aE>","coauthor":"%(trailers:key=Co-authored-by)","committer":"%cN <%cE>","date":"%ai","message":"%f"}%n"""
    cmd = ['git', 'log', '--pretty='+fmt]
    out = subprocess.run(cmd, stdout=subprocess.PIPE, cwd=root)
    out.check_returncode()
    for line in out.stdout.decode(encoding='utf-8').split('\n\n'):
        line = line.replace('\n', ' ').strip()
        if not line:
            continue
        parsed = json.loads(line)
        commit = Commit(**parsed)
        cmd = ['git', 'diff-tree', '--no-commit-id', '--name-status', commit.hash, '-r']
        out = subprocess.run(cmd, stdout=subprocess.PIPE, cwd=root)
        out.check_returncode()
        commit.files = out.stdout.decode(encoding='utf-8').splitlines()
        commits.append(commit)
    commits.reverse()
    return commits
