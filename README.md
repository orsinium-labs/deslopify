# deslopify

Analyze any git project to find out when it turned into AI slop.

AI detection is done based on git commit author, co-author, committer, agent files, etc. If the project author deliberately hides AI usage, we cannot detect it.

## Installation

```bash
git clone https://github.com/orsinium-labs/deslopify
cd deslopify
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
