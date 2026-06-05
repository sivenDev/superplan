# Install Superplan

## 1. Install Superpowers first

Superplan depends on the workflow skills from Superpowers and does not try to vendor or replace them.

- Superpowers repository: <https://github.com/obra/superpowers>
- Required by this bundle: `using-superpowers`, `brainstorming`, `writing-plans`, `subagent-driven-development`, `executing-plans`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `using-git-worktrees`, `finishing-a-development-branch`

You can verify the dependency at any time with:

```bash
python3 <using-superplan-root>/scripts/check_superpowers.py
```

## 2. Install this repository

Preferred path: install the **repository root** as a plugin or skill bundle so the whole `skills/` directory is available together.

This repository includes:

- `.codex-plugin/plugin.json` for Codex-compatible plugin packaging
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for Claude Code packaging

If you are asking an agent to install from a Git URL, give it the repository root URL and tell it to install the plugin/skill bundle from that repository.

## 3. Fallback for raw-skill installers

If your harness can only install raw skill directories from GitHub paths, install every skill under `skills/` from this repository:

- `skills/using-superplan`
- `skills/project-bootstrap-from-prd`
- `skills/feature-plan-and-delivery`
- `skills/bugfix-plan-and-delivery`

Do not install only `skills/using-superplan`; it routes to the three companion skills above.

## 4. Start using it

Use `$using-superplan` as the main entry skill.

When initializing a repository:

```bash
python3 <using-superplan-root>/scripts/init_workspace.py
```

That command:

- checks that Superpowers is installed
- creates `docs/superplan/human/{prd.md,features.md,bugs.md}` when missing
- creates `docs/superplan/plans/README.md`
- syncs the managed `AGENTS.md` guardrails block
