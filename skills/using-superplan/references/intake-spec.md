# Intake Spec

This is the canonical capture contract for new feature and bug requests before
they enter planning.

## When to Run Intake

Run intake when the human proposes a new item rather than referencing an existing
entry id or description. Feature examples include "新建 feature" and "新增功能";
bug examples include "新建 bug" and "报个缺陷".

If the request already exists in the matching human file, skip intake and enter
the delivery loop.

## Record Contract

Entries live in `docs/superplan/human/features.md` or `bugs.md`, one ascending
`## <id>: <title>` section per item, with `status` and `created` fields plus an
optional body.

- Feature ids use `F`; bug ids use `B`; numeric parts are zero-padded and never
  reused.
- The next number is the maximum existing numeric part plus one.
- In a linked worktree, append the sanitized branch slug, for example
  `F003@feature-x`. The recorder guards suffixes that could be confused with plan
  split ids.
- Human statuses are `proposed -> accepted -> done`; they are independent of plan
  statuses.

Use the canonical request command rather than editing numbering manually:

```bash
python3 <using-superplan-root>/scripts/human_requests.py record \
  --type feature --title "<title>" [--body "<description>"] \
  [--status proposed|accepted]

python3 <using-superplan-root>/scripts/human_requests.py record \
  --type bug --title "<title>" [--body "<symptom / reproduction>"] \
  [--status proposed|accepted]
```

`record_human_request.py` remains a compatibility entry point. Use
`human_requests.py set-status --id <id> --status <status>` for lifecycle updates.
If strict validation finds only legacy entries missing `status` or `created`,
run `migrate-legacy --check` before the explicit `--write`; unresolved evidence
or any other registry error requires manual repair. Workspace migration never
changes human request history, and recording never triggers this repair.

The recorder defaults to `proposed`. Use `--status accepted` only when all of
these are true:

- The human explicitly authorized recording the request and proceeding to
  planning.
- The extracted title and body faithfully represent the request without adding
  material assumptions.
- Scope, constraints, acceptance, and workspace decisions contain no material
  ambiguity that requires a human answer.

Direct acceptance applies only to the human request. It never approves an
implementation plan.

## Workflow

1. Run `human_requests.py validate`, then use `summary`, filtered `list`, and
   exact `show` to select existing state without loading the whole registry.
2. Extract a short title and the smallest body that faithfully distinguishes a
   new request. For a feature, prefer one concise paragraph covering the
   requested outcome, main scope, observable acceptance, and key constraints.
   When that is sufficient, do not expand the entry into RFC-style sections or
   add design decisions, alternatives, risk analysis, or implementation steps;
   those belong in an RFC or executable plan when applicable.
3. Apply the direct-accept conditions. If all pass, record `accepted` and enter
   planning. Otherwise record the default `proposed` status.
4. For `proposed`, stop and ask the human to review the entry. Do not debug,
   plan, or implement until confirmation changes it to `accepted`.
5. For `accepted`, continue through the selected route and still present the
   resulting draft implementation plan for separate human approval.

Intake records intent only; it never creates plans or code.
