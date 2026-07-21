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

Use the recorder rather than editing numbering manually:

```bash
python3 <using-superplan-root>/scripts/record_human_request.py \
  --type feature --title "<title>" [--body "<description>"] \
  [--status proposed|accepted]

python3 <using-superplan-root>/scripts/record_human_request.py \
  --type bug --title "<title>" [--body "<symptom / reproduction>"] \
  [--status proposed|accepted]
```

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

1. Extract a short title and only useful request details.
2. Apply the direct-accept conditions. If all pass, record `accepted` and enter
   planning. Otherwise record the default `proposed` status.
3. For `proposed`, stop and ask the human to review the entry. Do not debug,
   plan, or implement until confirmation changes it to `accepted`.
4. For `accepted`, continue through the selected route and still present the
   resulting draft implementation plan for separate human approval.

Intake records intent only; it never creates plans or code.
