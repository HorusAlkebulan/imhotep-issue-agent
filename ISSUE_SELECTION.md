# ISSUE_SELECTION.md

Guidance for choosing the next issue the agent should tackle. This file is read at runtime and
passed to Claude as the selection criteria, so edit it freely as we learn what works.

## Goal

Pick the single open issue the agent is most likely to fix **correctly, in one small pull
request, without a human clarifying anything first.** A confident small win beats an ambitious
attempt that stalls.

## Prefer issues that are

1. **Clear and specific.** The expected behavior or desired outcome is stated, or can be
   inferred without guessing. Bug reports with steps to reproduce or an error message rank high.
2. **Small in scope.** Likely touches one or a few files and can be done in a single focused
   change (docs fixes, small helpers, off-by-one or typo-class bugs, missing validation).
3. **Self-contained.** No dependency on other issues, external services, credentials, design
   decisions, or access to systems the agent does not have.
4. **Verifiable.** The result can be checked, ideally by an existing or easily added test, or
   by an obvious inspection of the diff.
5. **Fresh.** Break ties in favor of more recently created issues, since they are more likely to
   still be relevant to the current code.

## Avoid issues that are

- **Vague or open-ended** ("improve performance", "refactor everything", "make it better").
- **Questions, discussions, or feature requests needing a product decision** rather than a fix.
- **Large or cross-cutting**: architecture changes, migrations, dependency upgrades, or anything
  that would need a multi-PR plan.
- **Blocked or contested**: labeled `blocked`, `wontfix`, `duplicate`, `question`, or
  `needs-discussion`, or with comments suggesting disagreement about the approach.
- **Security-sensitive** (auth, secrets, vulnerabilities). Leave these to a human.
- **Already being addressed**: assigned to someone, or linked to an open pull request.

## Duplicates

If several issues describe the same problem, pick only the **oldest** one, because it is the
canonical report. Mention the duplicates in your reasoning so they can be closed after the fix.

## Ties

If candidates are genuinely close, choose the one with the smallest likely change. If still
tied, choose the lowest issue number.

## If nothing qualifies

It is acceptable, and correct, to select **no issue**. Say why, so the criteria or the issue
tracker can be improved. Do not force a pick from a list of poor candidates.
