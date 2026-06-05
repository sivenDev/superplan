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

## Path Convention

Agent-facing skill docs use paths relative to the installed skill directory.
Human-facing installation docs may still refer to the installed `using-superplan`
location conceptually when an absolute path is needed.

## Development

- Unit tests: `python3 -m unittest discover -s skills/using-superplan/scripts/tests`
- Codex plugin manifest validation: use the `plugin-creator` validator from your local Codex skill installation against the repository root

Repository license: `MIT`.
