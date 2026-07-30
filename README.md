# Superplan

Superplan packages a plan-first delivery workflow for coding agents. It bundles a pinned Superpowers runtime for generic planning, TDD, debugging, and execution, then specializes it around `docs/superplan/human/*` and `docs/superplan/plans/*`.

The main entry skill is `$using-superplan`. The other skills in `skills/` are bundled companions that it routes into.

## Bundled GPT-5.6 Superpowers

For Codex running GPT-5.6, Superplan vendors the runtime skills from
[`eagleagentic/superpowers-gpt-5.6`](https://github.com/eagleagentic/superpowers-gpt-5.6)
profile at the pinned revision
`aa973775906c8761a78019aaa21e4f0ccd987925` under `deps/superpowers`.

- The lock artifact records the source revision, exact skill inventory, file
  hashes, and deterministic tree hash.
- Plugin discovery exposes the four root Superplan skills plus the 13 bundled
  Superpowers skills without cloning, symlinks, or user-profile changes.
- Workspace initialization is offline and checks only repository artifacts.

## Repository Layout

```text
.
├── .codex-plugin/
│   └── plugin.json
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── deps/superpowers/           # pinned runtime Superpowers skills
├── skills/
│   ├── using-superplan/        # runtime scripts, references, and output assets
│   ├── project-bootstrap-from-prd/
│   ├── feature-plan-and-delivery/
│   └── bugfix-plan-and-delivery/
├── tests/
│   ├── scripts/                # repository unit tests
│   └── behavior/               # fresh-context workflow scenarios
└── docs/
    └── install.md
```

## Installation

See [docs/install.md](docs/install.md) for the full flow.

The short version:

1. Install this repository as a plugin/skill bundle from the repository root.
2. Restart Codex or open a new chat so plugin discovery loads the bundled skills.
3. Run `init_workspace.py` in the target repository and use `$using-superplan`
   as the entry skill.

If your harness only supports raw skill installation, install all four skills
under `skills/` and all 13 runtime skills under `deps/superpowers/`.

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

Human approval remains the gate out of `draft`. Approved work that stays queued
is persisted as `approved`; work starting immediately can persist `in_progress`
directly and refresh the index once. Full related-plan review is reserved for
structural changes, while routine progress updates use local plan/index checks.
Still-current safety, dependency, and test evidence is reused until relevant
workspace, file, or environment state changes. The canonical verification matrix
selects checks by artifact type and risk.

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

- Unit tests: `python3 -m unittest discover -s tests/scripts`
- Codex plugin manifest validation: use the `plugin-creator` validator from your local Codex skill installation against the repository root

Repository license: `MIT`.
