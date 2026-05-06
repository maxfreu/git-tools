import subprocess
from pathlib import Path
from typing import Union


def ensure_clean_git(
    repo_path: Union[str, Path] = ".",
    ignore_untracked: bool = False,
) -> None:
    """Raise an error if `repo_path` is not a git repo or has uncommitted changes.

    Args:
        repo_path: Path to the git repository. Defaults to the current directory.
        ignore_untracked: If True, untracked files do not count as uncommitted
            changes. Defaults to False.

    Raises:
        FileNotFoundError: If the path does not exist.
        RuntimeError: If git is not installed, the path is not a git repo, or
            the repo has uncommitted changes.
    """
    repo_path = Path(repo_path).resolve()
    if not repo_path.is_dir():
        raise FileNotFoundError("{} is not a directory".format(repo_path))

    def _run_git(*args):
        try:
            return subprocess.run(
                ["git", "-C", str(repo_path)] + list(args),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
        except FileNotFoundError:
            raise RuntimeError("git executable not found on PATH")

    # Check that this is a git working tree.
    result = _run_git("rev-parse", "--is-inside-work-tree")
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise RuntimeError("{} is not a git repository".format(repo_path))

    # Check for uncommitted changes (staged, unstaged, and optionally untracked).
    status_args = ["status", "--porcelain"]
    if ignore_untracked:
        status_args.append("--untracked-files=no")
    result = _run_git(*status_args)
    if result.returncode != 0:
        raise RuntimeError(
            "git status failed: {}".format(result.stderr.strip())
        )
    changes = result.stdout.splitlines()
    if changes:
        raise RuntimeError(
            "{} has {} uncommitted change(s)".format(repo_path, len(changes))
        )


def get_git_commit_hash(repo_path: Union[str, Path] = ".") -> str:
    """Return the full SHA-1 hash of the current commit (HEAD).

    Args:
        repo_path: Path to the git repository. Defaults to the current directory.

    Returns:
        The 40-character commit hash of HEAD.

    Raises:
        FileNotFoundError: If the path does not exist.
        RuntimeError: If git is not installed, the path is not a git repo, or
            HEAD cannot be resolved (e.g. an empty repo with no commits yet).
    """
    repo_path = Path(repo_path).resolve()
    if not repo_path.is_dir():
        raise FileNotFoundError("{} is not a directory".format(repo_path))

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except FileNotFoundError:
        raise RuntimeError("git executable not found on PATH")

    if result.returncode != 0:
        raise RuntimeError(
            "could not resolve HEAD in {}: {}".format(
                repo_path, result.stderr.strip()
            )
        )
    return result.stdout.strip()


def get_git_hash_safe(
    repo_path: Union[str, Path] = ".",
    ignore_untracked: bool = False,
) -> str:
    """Return the full commit hash of HEAD, ensuring the repo is clean first.

    Args:
        repo_path: Path to the git repository. Defaults to the current directory.
        ignore_untracked: If True, untracked files do not count as uncommitted
            changes. Defaults to False.

    Returns:
        The 40-character commit hash of HEAD.

    Raises:
        FileNotFoundError: If the path does not exist.
        RuntimeError: If git is not installed, the path is not a git repo, the
            repo has uncommitted changes, or HEAD cannot be resolved.
    """
    ensure_clean_git(repo_path, ignore_untracked=ignore_untracked)
    return get_git_commit_hash(repo_path)


if __name__ == "__main__":
    print(get_git_hash_safe())
