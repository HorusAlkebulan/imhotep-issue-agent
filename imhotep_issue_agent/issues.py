import json
import subprocess
from dataclasses import dataclass

DEFAULT_LIMIT = 3


@dataclass(frozen=True)
class Issue:
    number: int
    title: str
    body: str
    url: str
    created_at: str
    labels: tuple[str, ...]


def get_recent_open_issues(repo: str, limit: int = DEFAULT_LIMIT) -> list[Issue]:
    """Return the `limit` most recently created open issues of `repo` ("owner/name"), newest first."""
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")
    if limit == 0:
        return []

    result = subprocess.run(
        [
            "gh", "issue", "list",
            "--repo", repo,
            "--state", "open",
            "--limit", str(limit),
            "--json", "number,title,body,url,createdAt,labels",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh issue list failed for {repo}: {result.stderr.strip()}")

    issues = [
        Issue(
            number=raw["number"],
            title=raw["title"],
            body=raw["body"],
            url=raw["url"],
            created_at=raw["createdAt"],
            labels=tuple(label["name"] for label in raw["labels"]),
        )
        for raw in json.loads(result.stdout)
    ]
    # Sort explicitly rather than relying on gh's default ordering.
    issues.sort(key=lambda i: i.created_at, reverse=True)
    return issues[:limit]
