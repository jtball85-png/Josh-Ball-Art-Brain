"""commit_and_push tests — a real bare origin + working clone (same fixture
style as tests/test_sync_and_discuss.py), never subprocess mocks, since the
whole point is proving real git plumbing works end to end."""

from __future__ import annotations

import subprocess

from brain.git_sync import commit_and_push
from brain.hq import HQ
from tests.test_sync_and_discuss import git, synced_repos  # noqa: F401 (fixture)


class TestCommitAndPush:
    def test_commits_and_pushes_given_paths(self, config, synced_repos):
        clone, origin = synced_repos
        hq = HQ(config)
        target = hq.root / "decisions" / "log.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Decision Log\n\n## New entry\n", encoding="utf-8")

        result = commit_and_push(clone, [target], "Test commit")

        assert result == {"committed": True, "pushed": True, "warning": None}
        log = git("log", "origin/main", "-1", "--format=%s", cwd=clone)
        assert log.stdout.strip() == "Test commit"

    def test_noop_when_nothing_changed(self, config, synced_repos):
        clone, origin = synced_repos
        hq = HQ(config)
        # README.md exists (committed by the fixture) and is unmodified.
        result = commit_and_push(clone, [clone / "README.md"], "Nothing to see")
        assert result == {"committed": False, "pushed": False, "warning": None}

    def test_noop_when_no_paths_exist(self, config, synced_repos):
        clone, origin = synced_repos
        result = commit_and_push(clone, [clone / "hq" / "does-not-exist.md"], "N/A")
        assert result == {"committed": False, "pushed": False, "warning": None}

    def test_commits_locally_even_when_push_fails(self, config, synced_repos):
        clone, origin = synced_repos
        hq = HQ(config)
        target = hq.root / "decisions" / "log.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Decision Log\n\n## New entry\n", encoding="utf-8")

        # Break the remote so push fails, without touching the local commit.
        subprocess.run(["git", "remote", "set-url", "origin", "/nonexistent/path.git"],
                       cwd=clone, capture_output=True, text=True, check=True)

        result = commit_and_push(clone, [target], "Test commit")

        assert result["committed"] is True
        assert result["pushed"] is False
        assert result["warning"] is not None and "push" in result["warning"]
        # The commit itself really happened locally.
        log = git("log", "-1", "--format=%s", cwd=clone)
        assert log.stdout.strip() == "Test commit"
