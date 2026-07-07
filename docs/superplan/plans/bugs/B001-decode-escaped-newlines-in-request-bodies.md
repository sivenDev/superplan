---
id: "B001"
title: "Decode Escaped Newlines in Human Request Bodies"
type: "bugfix"
status: "draft"
summary: "Normalize escaped newline sequences in recorded request bodies so generated feature and bug entries contain real Markdown line breaks."
source: "docs/superplan/human/bugs.md"
created: "2026-07-07"
depends_on: []
parent: ""
---
# Decode Escaped Newlines in Human Request Bodies Plan

**Goal:** Ensure human request intake writes multi-line body text as real Markdown lines instead of preserving literal `\n` escape text.
**Scope:** Update `record_human_request.py` body rendering for feature and bug intake, and add focused regression coverage for escaped newline body arguments.
**Non-Goals:** Do not change request numbering, worktree branch qualifiers, title handling, status fields, generated file locations, or plan generation behavior.
**Architecture:** Keep the fix local to body normalization in the recorder. Convert only escaped newline spellings that agents commonly pass through shell arguments (`\n` and `\r\n`) into real line breaks before `render_entry` trims and appends the body, avoiding broad escape decoding that could alter unrelated backslash text.
**Baseline:** `render_entry` currently trims `body` and appends it unchanged. Reproduction with `--body 'first line\nsecond line'` produces `first line\nsecond line` as one Markdown line in `docs/superplan/human/features.md`.
**Reproduction:** `tmpdir=$(mktemp -d); mkdir -p "$tmpdir/docs"; python3 skills/using-superplan/scripts/record_human_request.py --root "$tmpdir" --type feature --title "Escaped body" --date 2026-07-07 --body 'first line\nsecond line'; sed -n '1,120p' "$tmpdir/docs/superplan/human/features.md"` currently shows `first line\nsecond line`.
**Root Cause:** The recorder treats `--body` as an already-renderable Markdown string and never normalizes escaped newline sequences before writing the entry.
**Exit Criteria:** The recorder writes escaped `\n` and `\r\n` body arguments as separate Markdown lines, preserves the existing single-line body behavior, and `python3 -m unittest discover -s skills/using-superplan/scripts/tests` passes.

## Task 1: Add regression coverage for escaped newline bodies

**Outcome:** The recorder test suite captures the failed behavior before implementation and protects both feature and bug intake body rendering from regression.
**Files:**
- Modify: `skills/using-superplan/scripts/tests/test_record_human_request.py`

**Verification:**
- `python3 -m unittest skills.using-superplan.scripts.tests.test_record_human_request.RecordHumanRequestTests.test_body_escaped_newlines_render_as_markdown_lines`

- [ ] Add a focused test that runs the recorder with body arguments containing escaped LF and CRLF newline text:

```python
def test_body_escaped_newlines_render_as_markdown_lines(self) -> None:
    cases = [
        ("first line\\nsecond line", "first line\nsecond line"),
        ("first line\\r\\nsecond line", "first line\nsecond line"),
    ]
    for raw_body, expected_body in cases:
        with self.subTest(raw_body=raw_body):
            with tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                (root / "docs").mkdir()

                code = MODULE.run(
                    [
                        "--root",
                        str(root),
                        "--type",
                        "feature",
                        "--title",
                        "Multi-line",
                        "--body",
                        raw_body,
                        "--date",
                        "2026-07-07",
                    ]
                )
                self.assertEqual(code, 0)

                content = (
                    root / "docs" / "superplan" / "human" / "features.md"
                ).read_text(encoding="utf-8")
                self.assertIn(expected_body, content)
                self.assertNotIn(raw_body, content)
```

- [ ] Run the focused test and confirm it fails because the expected real newline body is missing and the escaped body text is still present.
- [ ] Keep existing numbering and worktree tests unchanged.

## Task 2: Normalize escaped newline sequences in recorder bodies

**Outcome:** Request bodies passed with escaped newline spellings are converted to real Markdown line breaks before entries are appended.
**Files:**
- Modify: `skills/using-superplan/scripts/record_human_request.py`

**Verification:**
- `python3 -m unittest skills.using-superplan.scripts.tests.test_record_human_request.RecordHumanRequestTests.test_body_escaped_newlines_render_as_markdown_lines`
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests`

- [ ] Add a small helper near `render_entry` that normalizes only newline escape spellings:

```python
def normalize_body_text(body: str) -> str:
    return body.replace("\\r\\n", "\n").replace("\\n", "\n")
```

- [ ] Call the helper inside `render_entry` before `.strip()`:

```python
body_text = normalize_body_text(body or "").strip()
```

- [ ] Run the focused test and confirm it passes.
- [ ] Run the full script test suite and confirm it passes.

## References
- `docs/superplan/human/bugs.md`
- `skills/using-superplan/scripts/record_human_request.py`
- `skills/using-superplan/scripts/tests/test_record_human_request.py`
