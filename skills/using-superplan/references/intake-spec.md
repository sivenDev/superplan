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
  --type feature --title "<title>" [--body "<description>"]

python3 <using-superplan-root>/scripts/record_human_request.py \
  --type bug --title "<title>" [--body "<symptom / reproduction>"]
```

## Workflow

1. Extract a short title and only useful request details.
2. Run the matching recorder; it appends the next id with `status: proposed`.
3. Stop and ask the human to review the entry. Do not debug, plan, or implement.
4. Continue only after human confirmation changes the entry to `accepted`.

Intake records intent only; it never creates plans or code.
