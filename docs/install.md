# Install Superplan

Install the repository root as a plugin so Codex discovers the four Superplan
workflow skills under `skills/`. Detailed route behavior lives in conditional
references inside those skills, so no supplemental runtime, Git clone,
user-skill symlink, active profile manifest, backup, or `~/.superplan` state is
required.

After installing or updating the plugin, restart Codex or open a new chat. Then
initialize a repository from its root:

```bash
python3 <using-superplan-root>/scripts/init_workspace.py
```

Initialization is offline and workspace-only. It creates missing human request
templates, synchronizes the managed `AGENTS.md` block, and generates the plans
index without replacing existing human documents or non-managed instructions.

For an existing workspace, check compatibility without writing:

```bash
python3 <using-superplan-root>/scripts/init_workspace.py --check
```

If the check reports an older/missing schema or stale generated artifacts,
inspect workspace safety and migrate explicitly:

```bash
python3 <using-superplan-root>/scripts/init_workspace.py --migrate
```

A newer workspace schema is never downgraded; update Superplan instead. Use
`--root <path>` with any command to select a target explicitly.

Harnesses that only support raw skill directories must install all four
directories under `skills/`.
