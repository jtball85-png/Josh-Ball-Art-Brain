"""Commit-and-push automation for state a live session decided should be
saved immediately (currently: board meeting close) rather than wait for a
manual /end-of-day. Deliberately narrow: stages only the exact paths the
caller says changed (never `git add -A`, which could sweep in unrelated
in-progress work), never force-pushes, never skips hooks. A failed push is
reported, not raised — a local commit that didn't push is strictly better
than losing the record."""

from __future__ import annotations

import subprocess
from pathlib import Path


def commit_and_push(repo_root: Path, paths: list[Path], message: str,
                    timeout: int = 30) -> dict:
    """Stage the given paths (skipping any that don't exist), commit if
    anything is actually staged, then push. Returns
    {"committed": bool, "pushed": bool, "warning": str | None} and never
    raises — callers treat a bad result as a warning to surface, not a
    reason to fail the operation that produced the state being saved.
    Each phase (add/commit/push) reports its own failure independently, so
    a push-time error can never be misreported as "nothing committed" when
    the commit actually succeeded."""
    existing = [str(p) for p in paths if p.exists()]
    if not existing:
        return {"committed": False, "pushed": False, "warning": None}

    try:
        add = subprocess.run(
            ["git", "add", "--", *existing], cwd=repo_root,
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return {"committed": False, "pushed": False, "warning": f"git add error: {e}"}
    if add.returncode != 0:
        return {"committed": False, "pushed": False,
                "warning": f"git add failed: {add.stderr.strip()[:300]}"}

    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=repo_root, timeout=timeout,
    )
    if staged.returncode == 0:
        return {"committed": False, "pushed": False, "warning": None}  # nothing actually changed

    try:
        commit = subprocess.run(
            ["git", "commit", "-m", message], cwd=repo_root,
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return {"committed": False, "pushed": False, "warning": f"git commit error: {e}"}
    if commit.returncode != 0:
        return {"committed": False, "pushed": False,
                "warning": f"git commit failed: {commit.stderr.strip()[:300]}"}

    try:
        push = subprocess.run(
            ["git", "push"], cwd=repo_root, capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return {"committed": True, "pushed": False, "warning": f"committed locally but push errored: {e}"}
    if push.returncode != 0:
        return {"committed": True, "pushed": False,
                "warning": f"committed locally but push failed: {push.stderr.strip()[:300]}"}

    return {"committed": True, "pushed": True, "warning": None}
