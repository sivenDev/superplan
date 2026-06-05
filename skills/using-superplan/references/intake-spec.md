# Intake Spec

This reference defines how new human-authored feature and bug requests are
captured into `docs/superplan/human/features.md` and `docs/superplan/human/bugs.md` before they
enter the delivery loop.

It is shared by `$feature-plan-and-delivery` and `$bugfix-plan-and-delivery`.

Bundled script paths are relative to the `skills/using-superplan/` directory.

## When Intake Triggers

Run intake when the human is proposing a brand-new item rather than pointing at
an already-recorded one. Typical triggers:

- Feature: "新建 feature", "feature: ...", "新增功能 ...", "add a feature ...".
- Bug: "新建 bug", "bug: ...", "报个缺陷 ...", "report a bug ...".

If the human references an existing entry id (for example `F003` / `B002`) or an
existing description already in the file, skip intake and go straight to the
delivery loop.

## File Structure

Both files share the same layout. One entry per `##` section, in ascending id
order. Newest entries are appended at the end.

```md
# Features

## F001: <short title>

- status: proposed
- created: 2026-05-29

<optional description lines>

## F002: <short title>

- status: accepted
- created: 2026-05-29

<optional description lines>
```

`docs/superplan/human/bugs.md` uses the same shape with heading `# Bugs` and `B`-prefixed ids.

## Numbering Rule

- Ids are per-file, sequential, and stable. They are never reused or renumbered.
- Feature ids use prefix `F`; bug ids use prefix `B`.
- The numeric part is zero-padded to 3 digits: `F001`, `F002`, ... `B001`, `B002`.
- The next id is `max(existing numeric suffix) + 1`, or `001` when the file has no entries.

## Status Lifecycle (human docs)

These statuses track the human-doc lifecycle and are independent of plan
frontmatter `status` values in `plan-spec.md`.

- `proposed` — just recorded by intake, waiting for human review.
- `accepted` — human reviewed and confirmed; ready to plan.
- `done` — delivered; kept for history.

## Intake Workflow

1. Recognize a new-item trigger and extract a short title (and optional description).
2. Append a new entry with the next id and `status: proposed` using the recorder:
   - `python3 ../scripts/record_human_request.py --type feature --title "<title>" [--body "<description>"]`
   - Use `--type bug` for bugs. The command prints the new id.
3. Stop and ask the human to review the recorded entry. Do not start planning yet.
4. After the human confirms (entry moves to `status: accepted`), continue with the
   skill's normal delivery loop using that entry as the source.

## Notes

- Intake only records intent; it never writes plans or code.
- Keep titles short and specific. Put detail in the optional body, not the title.
- One trigger records one entry. Batch multiple items as separate entries.
