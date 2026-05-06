# Git Tools

Git mess bad. Clean tree good.

This tool check git. If dirt found, tool shout. If clean, tool happy.

Use uv. Tool install:

```sh
uv add git+https://github.com/maxfreu/git-tools
```

Use tool:

```python
from git_tools import ensure_clean_git, get_git_commit_hash, get_git_hash_safe

# check if repo clean, error if uncommitted changes
ensure_clean_git(".")

# get hash
commit = get_git_commit_hash(".")

# get hash only if clean
commit = get_git_hash_safe(".")
```
