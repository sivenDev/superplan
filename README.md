# Superplan

Superplan packages a plan-first delivery workflow for coding agents around
`docs/superplan/human/*` and `docs/superplan/plans/*`.

The main entry skill is `$using-superplan`. Four route skills stay discoverable;
detailed debugging, worktree, planning, and verification guidance is loaded from
their references only when the route needs it.

## Focused Skill Set

Superplan exposes only four skills:

- `using-superplan`: initializes workspaces and routes requests.
- `project-bootstrap-from-prd`: turns a PRD into reviewed mainline plans.
- `feature-plan-and-delivery`: plans and delivers accepted features.
- `bugfix-plan-and-delivery`: diagnoses, plans, and delivers accepted bugs.

The route skills own conditional references for specialized behavior. This keeps
generic workflow descriptions out of global skill discovery without losing the
debugging, worktree-safety, test-first, review, or verification boundaries that
materially affect delivery.

## Repository Layout

```text
.
├── .codex-plugin/
│   └── plugin.json
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
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

If your harness only supports raw skill installation, install the four
directories under `skills/`.

## Versioned Workspaces

Initialized repositories store a machine-readable marker inside the managed
`AGENTS.md` block:

```text
<!-- superplan-workspace: schema=1; generated-by=0.6.0 -->
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

Routing trusts fresh checks: a compatible workspace continues even if an older
diagnosis named historical blockers, and Superplan does not suggest an older
version fallback. Evidence-backed legacy omissions are recovered through the
existing preview/write flow. Explicit auto-recovery authorization is reused
without asking again; parallel repair is allowed only with an independent write
set and isolated worktree/commit. A genuinely required unsafe migration stops
with the current evidence and one concise decision.

Initialization and migration are offline and workspace-only. They never inspect
or change user-level profiles, skills, backups, or `~/.superplan` state. A newer
schema is not downgraded.

## Progressive State Discovery

Normal feature and bug routing does not need to load the complete cumulative
human registry. Use the deterministic request interface instead:

```bash
python3 <using-superplan-root>/scripts/human_requests.py validate
python3 <using-superplan-root>/scripts/human_requests.py summary
python3 <using-superplan-root>/scripts/human_requests.py list --type feature
python3 <using-superplan-root>/scripts/human_requests.py show --id F012
```

It also provides `record`, monotonic `require-rfc`, and forward-only
`set-status` commands.
`record_human_request.py` remains as a compatibility adapter.

### Optional Feature RFCs

Features normally proceed directly to implementation planning. Use an RFC when
the human explicitly requests one or when unresolved architecture, ownership,
public contracts, migration, security, concurrency, data integrity, release, or
rollback decisions would materially change the plan. The agent states its
reason before autonomously enabling RFC; task size alone is not a trigger.

RFC-backed features keep the same feature id and lifecycle. Set
`requires_rfc: true`, then maintain the design at:

```text
docs/superplan/rfcs/<feature-id>.md
```

RFCs default to Chinese unless the human or project language policy says
otherwise. New RFCs start at `version: 1`; draft edits before first approval do
not increment it. A material change to an approved RFC returns it to `draft`,
increments the version once, and requires reapproval. Git records revisions;
conversation transcripts are omitted unless an audit requirement says
otherwise.

The gates remain separate: approve the RFC before creating development plans,
then approve the plans before coding. Each RFC-backed plan references the exact
RFC path.

### Legacy Registry Recovery

Older registries may predate required `status` and `created` fields. Preview the
evidence-backed repair before writing it:

```bash
python3 <using-superplan-root>/scripts/human_requests.py migrate-legacy --check
python3 <using-superplan-root>/scripts/human_requests.py migrate-legacy --write
```

The command repairs only missing metadata, rejects every other registry error,
and refuses all writes when a creation date lacks plan or Git evidence. Status
comes from related plan progress; creation dates prefer the earliest related
plan and then the request's first Git appearance. Existing request text and
metadata remain unchanged. `init_workspace.py --migrate` never performs this
semantic migration, and `record` remains strict until recovery succeeds.

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
  complex defect work uses test-first development when a trustworthy focused
  failure distinguishes the change, plus deeper debugging, regression, and
  independent review.

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

If the human accepts isolation, Superplan loads its local worktree reference,
leaves the original uncommitted changes untouched, and resumes the same route
from the committed baseline in the new worktree. If the human declines, work
continues in place with unrelated-change preservation and precise staging.
Superplan never stashes, commits, or creates a worktree without explicit consent.

## Path Convention

Agent-facing skill and reference docs use `<using-superplan-root>` for the
installed `skills/using-superplan/` directory. Human-facing repository commands
may use paths relative to the repository root.

## Development

Superplan supports Python 3.10 through 3.14. Local development and CI use one
authoritative, standard-library-only verification command:

```bash
python3 tools/verify_repo.py
```

Focused unittest modules remain useful while iterating; run the command above
once after implementation stabilizes.

Repository license: `MIT`.
