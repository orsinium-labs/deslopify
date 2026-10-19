# deslopify

Analyze any git project to find out when it turned into AI slop.

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
