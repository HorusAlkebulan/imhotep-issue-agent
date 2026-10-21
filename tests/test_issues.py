import pytest

from imhotep_issue_agent.issues import get_recent_open_issues

TARGET_REPO = "HorusAlkebulan/imhotep-issue-agent-target"


def test_defaults_to_three_most_recent_issues():
    issues = get_recent_open_issues(TARGET_REPO)
    assert len(issues) == 3


def test_issues_are_newest_first():
    issues = get_recent_open_issues(TARGET_REPO, limit=10)
    created = [i.created_at for i in issues]
    assert created == sorted(created, reverse=True)


def test_limit_larger_than_issue_count_returns_all():
    issues = get_recent_open_issues(TARGET_REPO, limit=1000)
    assert 0 < len(issues) < 1000


def test_issue_fields_are_populated():
    (issue,) = get_recent_open_issues(TARGET_REPO, limit=1)
    assert issue.number > 0
    assert issue.title
    assert issue.url.startswith("https://github.com/")


def test_zero_limit_returns_empty():
    assert get_recent_open_issues(TARGET_REPO, limit=0) == []


def test_negative_limit_raises():
    with pytest.raises(ValueError):
        get_recent_open_issues(TARGET_REPO, limit=-1)


def test_unknown_repo_raises():
    with pytest.raises(RuntimeError):
        get_recent_open_issues("HorusAlkebulan/this-repo-does-not-exist-xyz")
