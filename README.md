# Superplan

Superplan packages a plan-first delivery workflow for coding agents. It is built as a small plugin/skill bundle that sits on top of [superpowers](https://github.com/obra/superpowers): Superpowers provides the generic planning, TDD, debugging, and execution workflows; this repository specializes them around `docs/superplan/human/*` and `docs/superplan/plans/*`.

The main entry skill is `$using-superplan`. The other skills in `skills/` are bundled companions that it routes into.

## Prerequisite

Install **Superpowers** first:

- Repository: <https://github.com/obra/superpowers>
- This repo includes a bundled check at `skills/using-superplan/scripts/check_superpowers.py`
- `skills/using-superplan/scripts/init_workspace.py` also fails fast when Superpowers is missing

## Repository Layout

```text
.
├── .codex-plugin/
│   └── plugin.json
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── using-superplan/
│   ├── project-bootstrap-from-prd/
│   ├── feature-plan-and-delivery/
│   └── bugfix-plan-and-delivery/
└── docs/
    └── install.md
```

## Installation

See [docs/install.md](docs/install.md) for the full flow.

The short version:

1. Install `superpowers`.
2. Install this repository as a plugin/skill bundle from the repository root when your harness supports that.
3. Use `$using-superplan` as the entry skill.

If your harness only supports raw skill installation from GitHub paths, install **all** bundled skills under `skills/`. Do not install only `skills/using-superplan`, because it routes to the companion skills in the same bundle.

## Bundled Skills

- `using-superplan`: entry skill; initializes and routes work.
- `project-bootstrap-from-prd`: turns `docs/superplan/human/prd.md` into reviewed plans.
- `feature-plan-and-delivery`: turns accepted feature entries into reviewed feature plans.
- `bugfix-plan-and-delivery`: turns accepted bug entries into reviewed bugfix plans.

## Adaptive Workflow

Superplan scales process depth to task risk instead of applying the same planning,
testing, verification, and delegation ceremony to every change:

- Low-risk documentation, configuration, template, and mechanical work uses the
  smallest relevant validator or smoke check and does not require new unit tests
  by default.
- Standard behavior changes test observable acceptance behavior, use focused
  checks while iterating, and run one relevant final regression after the
  implementation stabilizes.
- High-risk security, concurrency, migration, compatibility, data-integrity, or
  complex defect work keeps strict test-first development, debugging, regression,
  and independent review depth.

The approved Superplan plan is the persisted design and execution artifact. Plans
record outcomes, exact files, important boundaries, and evidence without copying
the complete future diff. Small and medium tasks default to one capable agent;
subagents are reserved for genuinely independent slices or high-risk review.

Task-level commit messages include the plan id when one exists, linking the human
request and plan to the actual implementation in Git.

## Dirty Worktree Safety

Before Superplan records intake, changes plans, or starts implementation, it
inspects Git status and relevant diff context for meaningful Git changes. A dirty
workspace does not trigger an automatic prompt: the agent uses semantic judgment
and asks about an isolated worktree only when existing changes could be
overwritten, mixed into the task's commit, or create an integration conflict.
Timestamp-only metadata, caches, and safely reproducible generated noise are
ignored unless they are consequential in context.

If the human accepts isolation, Superplan delegates creation to
`using-git-worktrees`, leaves the original uncommitted changes untouched, and
resumes the same route from the committed baseline in the new worktree. If the
human declines, work continues in place with unrelated-change preservation and
precise staging. Superplan never stashes, commits, or creates a worktree without
explicit consent.

## Path Convention

Agent-facing skill and reference docs use `<using-superplan-root>` for the
installed `skills/using-superplan/` directory. Human-facing repository commands
may use paths relative to the repository root.

## Development

- Unit tests: `python3 -m unittest discover -s skills/using-superplan/scripts/tests`
- Codex plugin manifest validation: use the `plugin-creator` validator from your local Codex skill installation against the repository root

Repository license: `MIT`.
