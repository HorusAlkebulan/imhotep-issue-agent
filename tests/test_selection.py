import asyncio

import pytest

from imhotep_issue_agent.issues import Issue, get_recent_open_issues
from imhotep_issue_agent.selection import Selection, _to_selection, select_next_issue

TARGET_REPO = "HorusAlkebulan/imhotep-issue-agent-target"


def make_issue(number: int, title: str, body: str = "", labels=()) -> Issue:
    return Issue(number, title, body, f"https://github.com/o/r/issues/{number}",
                 f"2026-10-21T00:00:0{number}Z", tuple(labels))


# --- unit tests (no network / no model) ---

def test_empty_list_selects_nothing():
    selection = asyncio.run(select_next_issue([]))
    assert selection.issue is None


def test_to_selection_maps_number_to_issue():
    issues = [make_issue(1, "a"), make_issue(2, "b")]
    selection = _to_selection({"issue_number": 2, "reasoning": "why"}, issues)
    assert selection == Selection(issues[1], "why")


def test_to_selection_allows_null():
    selection = _to_selection({"issue_number": None, "reasoning": "none fit"}, [make_issue(1, "a")])
    assert selection.issue is None


def test_to_selection_rejects_unknown_number():
    with pytest.raises(RuntimeError):
        _to_selection({"issue_number": 99, "reasoning": "x"}, [make_issue(1, "a")])


# --- functional tests (call Claude) ---

def test_selects_from_target_repo():
    issues = get_recent_open_issues(TARGET_REPO, limit=10)
    selection = asyncio.run(select_next_issue(issues))
    assert selection.issue in issues
    assert selection.reasoning


def test_prefers_clear_issue_over_vague_one():
    vague = make_issue(1, "Make it better", "Improve everything.")
    clear = make_issue(2, "Typo in README heading", "README says 'Instalation'; should be 'Installation'.")
    selection = asyncio.run(select_next_issue([vague, clear]))
    assert selection.issue == clear


def test_selects_nothing_when_all_issues_are_unsuitable():
    issues = [
        make_issue(1, "Rewrite the whole app in Rust", "Big migration, no details."),
        make_issue(2, "Should we support Windows?", "Just a discussion.", labels=["question"]),
    ]
    selection = asyncio.run(select_next_issue(issues))
    assert selection.issue is None


def test_guidance_file_is_actually_used(tmp_path):
    guidance = tmp_path / "g.md"
    guidance.write_text("Always select the issue with the highest issue number. No exceptions.")
    issues = [make_issue(1, "Typo in README", "Fix 'teh' to 'the'."), make_issue(2, "Typo in docs", "Fix 'recieve'.")]
    selection = asyncio.run(select_next_issue(issues, guidance_path=guidance))
    assert selection.issue.number == 2
