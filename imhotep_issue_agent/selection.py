import json
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from imhotep_issue_agent.issues import Issue

DEFAULT_GUIDANCE_PATH = Path(__file__).resolve().parent.parent / "ISSUE_SELECTION.md"

_SYSTEM_PROMPT = """\
You select the next GitHub issue for an automated coding agent to fix.
Apply the selection guidance below. Choose only from the issues provided; never invent a number.
Select no issue (null) if none qualifies under the guidance.

# Selection guidance

{guidance}
"""

_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "issue_number": {"type": ["integer", "null"]},
        "reasoning": {"type": "string"},
    },
    "required": ["issue_number", "reasoning"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class Selection:
    issue: Issue | None
    reasoning: str


async def select_next_issue(
    issues: list[Issue],
    guidance_path: Path = DEFAULT_GUIDANCE_PATH,
) -> Selection:
    """Ask Claude to pick the best issue from `issues` using the guidance in `guidance_path`.

    The guidance file is re-read on every call so edits take effect immediately.
    """
    if not issues:
        return Selection(issue=None, reasoning="No issues provided.")

    options = ClaudeAgentOptions(
        system_prompt=_SYSTEM_PROMPT.format(guidance=guidance_path.read_text()),
        output_format={"type": "json_schema", "schema": _OUTPUT_SCHEMA},
        allowed_tools=[],
        max_turns=3,
    )

    result: ResultMessage | None = None
    async for message in query(prompt=_format_issues(issues), options=options):
        if isinstance(message, ResultMessage):
            result = message

    if result is None or result.is_error or result.structured_output is None:
        detail = result.errors if result else "no result message"
        raise RuntimeError(f"Issue selection failed: {detail}")

    return _to_selection(result.structured_output, issues)


def _to_selection(output: dict, issues: list[Issue]) -> Selection:
    number = output["issue_number"]
    reasoning = output["reasoning"]
    if number is None:
        return Selection(issue=None, reasoning=reasoning)
    by_number = {i.number: i for i in issues}
    if number not in by_number:
        raise RuntimeError(f"Claude selected #{number}, which is not among the candidates")
    return Selection(issue=by_number[number], reasoning=reasoning)


def _format_issues(issues: list[Issue]) -> str:
    payload = [
        {
            "number": i.number,
            "title": i.title,
            "body": i.body,
            "labels": list(i.labels),
            "created_at": i.created_at,
        }
        for i in issues
    ]
    return "Candidate issues:\n" + json.dumps(payload, indent=2)
