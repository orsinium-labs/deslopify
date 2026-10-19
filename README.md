# deslopify

Analyze a project to find out when it turned into AI slop. Can scan git repos (local or remote), and Go (`go.mod`) and Rust (`Cargo.toml`) dependencies.

AI detection is done based on git commit author, co-author, committer, agent files, etc. If the project author deliberately hides AI usage, we cannot detect it. False-positives are also possible (but rare): some anti-AI projects include an `AGENTS.md` file telling AI agents that the project is not open to AI contributions.

## Installation

```bash
python3 -m pip install --break-system-packages deslopify
```

## Usage

Clone and analyze remote repository (can pass multiple space-separated URLs):

```bash
python3 -m deslopify https://github.com/sqlc-dev/sqlc
```

Analyze local repository:

```bash
python3 -m deslopify ~/Documents/sqlc
```

Analyze Go project dependencies:

```bash
python3 -m deslopify ./go.mod
```

Analyze Rust project dependencies:

```bash
python3 -m deslopify ./Cargo.toml
```
