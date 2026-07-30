# Superplan

Superplan packages a plan-first delivery workflow for coding agents. It bundles a pinned Superpowers runtime for generic planning, TDD, debugging, and execution, then specializes it around `docs/superplan/human/*` and `docs/superplan/plans/*`.

The main entry skill is `$using-superplan`. The other skills in `skills/` are bundled companions that it routes into.

## Bundled Runtime

Superplan includes its required Superpowers runtime directly under
`deps/superpowers/`. Workspace initialization uses these repository files and
does not download or install an external profile.

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
├── deps/
│   ├── superpowers/            # pinned runtime Superpowers skills
│   └── superpowers.lock.json   # provenance, inventory, and integrity hashes
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
3. From the target repository, run:

   ```bash
   python3 <using-superplan-root>/scripts/init_workspace.py
   ```

4. Use `$using-superplan` as the entry skill.

The Codex manifest adds `deps/superpowers/` as a supplemental skill path;
default plugin discovery still loads the four Superplan skills under `skills/`.

If your harness only supports raw skill installation, install all four skills
under `skills/` and all 13 runtime skills under `deps/superpowers/`.

## Bundled Skills

- `using-superplan`: entry skill; initializes and routes work.
- `project-bootstrap-from-prd`: turns `docs/superplan/human/prd.md` into reviewed plans.
- `feature-plan-and-delivery`: turns accepted feature entries into reviewed feature plans.
- `bugfix-plan-and-delivery`: turns accepted bug entries into reviewed bugfix plans.

## Versioned Workspaces

Initialized repositories store a machine-readable marker inside the managed
`AGENTS.md` block:

```text
<!-- superplan-workspace: schema=1; generated-by=0.2.0 -->
```

Check compatibility without writing:

```bash
python3 <using-superplan-root>/scripts/init_workspace.py --check
```

For an older/missing schema or stale generated artifacts, inspect workspace
safety and migrate explicitly:

```bash
python3 <using-superplan-root>/scripts/init_workspace.py --migrate
```

Initialization and migration are offline and workspace-only. They never inspect
or change user-level Superpowers profiles, skills, backups, or `~/.superplan`
state. A newer schema is not downgraded.

## Progressive State Discovery

Normal feature and bug routing does not need to load the complete cumulative
human registry. Use the deterministic request interface instead:

```bash
python3 <using-superplan-root>/scripts/human_requests.py validate
python3 <using-superplan-root>/scripts/human_requests.py summary
python3 <using-superplan-root>/scripts/human_requests.py list --type feature
python3 <using-superplan-root>/scripts/human_requests.py show --id F012
```

It also provides `record` and forward-only `set-status` commands.
`record_human_request.py` remains as a compatibility adapter.

For structural plan work, validate all metadata and inspect compact candidates
before loading related plan bodies:

```bash
python3 <using-superplan-root>/scripts/generate_plans_readme.py --catalog
python3 <using-superplan-root>/scripts/generate_plans_readme.py --active
python3 <using-superplan-root>/scripts/generate_plans_readme.py --source-id F012
python3 <using-superplan-root>/scripts/generate_plans_readme.py --depends-on F012-01
python3 <using-superplan-root>/scripts/generate_plans_readme.py --artifact path/to/file
python3 <using-superplan-root>/scripts/generate_plans_readme.py --search "decision text"
```

Catalog and search commands validate the complete plan set first. Searches cover
all statuses—including completed and superseded plans—unless explicitly
filtered. Agents then read the changed plan and discovered related closure in
full; compact metadata does not replace semantic review.

## Runtime Scripts

The top-level Python scripts are organized by workspace responsibility:

- `init_workspace.py`: initialize, check, and migrate versioned workspaces.
- `human_requests.py`: canonical human request query and mutation interface.
- `record_human_request.py`: compatibility adapter for the previous recorder CLI.
- `generate_plans_readme.py`: global plan validation, compact discovery, and index generation.
- `sync_agents_guardrails.py`: low-level managed guardrail synchronization.
- `workspace_paths.py`: shared Git/Superplan root resolution.
- `superplan_version.py`: plugin and workspace schema version contract.

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
directly and refresh the index once. Structural changes use exhaustive global
validation plus compact candidate discovery followed by full-text review of the
related closure; routine progress updates use local plan/index checks.
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
- Bundled runtime/package contract: `python3 -m unittest discover -s tests/scripts -p 'test_bundled_superpowers.py'`
- Skill validation: run `quick_validate.py` for all directories under `skills/` and `deps/superpowers/`

The current local `plugin-creator` validator may reject the documented custom
supplemental `skills` path because it still hard-codes `./skills/`; the bundled
runtime test verifies the actual manifest path, synchronized versions, exact
inventory, duplicate-name boundary, and dependency integrity.

Repository license: `MIT`.
