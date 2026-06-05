# Superplan Repository

- This repository packages `superplan` as a Codex/Claude-compatible plugin bundle with skills under `skills/`.
- `skills/using-superplan` is the main entry skill. The other bundled skills are required companions and should ship together.
- Superplan depends on `superpowers`. Keep the dependency explicit in docs and scripts; do not vendor Superpowers skills into this repository.
- In skill and reference docs, use the placeholder `<using-superplan-root>` for bundled script paths instead of hard-coding local install paths.
- Validate script behavior with `python3 -m unittest discover -s skills/using-superplan/scripts/tests`.


<claude-mem-context>
# Memory Context

# [superplan] recent context, 2026-06-05 4:17pm GMT+8

No previous sessions found.
</claude-mem-context>
