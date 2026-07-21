# Install Superplan for GPT-5.6

This flow supports Codex with `gpt-5.6` and `gpt-5.6-*` only. The external
Superpowers profile is cloned and pinned; its skills are not vendored into
Superplan, and the installer does not modify Codex model configuration.

## 1. Install the Superplan bundle

Preferred path: install the repository root as a plugin or skill bundle so the
whole `skills/` directory is available together.

This repository includes:

- `.codex-plugin/plugin.json` for Codex-compatible plugin packaging
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for
  compatible bundle packaging

If the harness only supports raw skill directories, install all four bundled
skills instead of only `using-superplan`:

- `skills/using-superplan`
- `skills/project-bootstrap-from-prd`
- `skills/feature-plan-and-delivery`
- `skills/bugfix-plan-and-delivery`

## 2. Inspect the GPT-5.6 activation

Run a dry-run first. It resolves the target skills directory and lists existing
conflicts without cloning or changing files:

```bash
python3 <using-superplan-root>/scripts/install_superpowers_profile.py \
  --model gpt-5.6 \
  --dry-run
```

The target directory is selected in this order:

1. Explicit `--skills-dir`
2. The one user skills directory already containing `using-superpowers`
3. `$HOME/.agents/skills` when no existing installation is found

Multiple discovered installations stop the operation so Codex does not load
duplicate same-name skills ambiguously.

## 3. Install and activate the pinned profile

After reviewing the dry-run, a conflict-free target can be activated by rerunning
the command without `--dry-run` or `--replace-existing`. If conflicts require
replacement, explicitly approve the resolved skills directory and every listed
conflict before activating with:

```bash
python3 <using-superplan-root>/scripts/install_superpowers_profile.py \
  --model gpt-5.6 \
  --replace-existing
```

The installer clones
`https://github.com/eagleagentic/superpowers-gpt-5.6.git` at revision
`aa973775906c8761a78019aaa21e4f0ccd987925`, validates its 13 skills and
`skills/superpowers/check-context-budget.sh`, then links the skills into the
resolved user directory.

Default local state:

```text
~/.superplan/
├── dependencies/superpowers-gpt-5.6/<commit>/
├── backups/<timestamp>/skills/
└── active-superpowers-profile.json
```

Existing same-name entries are never overwritten in place. With
`--replace-existing`, verified Superpowers skill directories are moved into one
timestamped backup before the new links are created. Unknown files, malformed
skill directories, or ambiguous installations block activation. Any failure
during activation automatically restores moved skills and the previous
manifest. Successful backups are retained for deliberate manual recovery.

Use `--state-root <path>` and `--skills-dir <path>` to isolate verification or
CI smoke runs from live user state.

## 4. Restart Codex and select GPT-5.6

Restart Codex or open a new chat so skill discovery sees the activated links.
Then select the model independently:

```bash
codex --model gpt-5.6
```

In an interactive session, `/model` can select GPT-5.6. The installer requires
an explicit model argument because it cannot read the session-local `/model`
selection reliably, and it never edits `config.toml`.

## 5. Verify the active profile

```bash
python3 <using-superplan-root>/scripts/check_superpowers.py \
  --model gpt-5.6
```

The check validates the active manifest, fixed revision, exact inventory,
skills directory, and every symlink target. A manifest/link mismatch fails with
diagnostic output; it is not repaired silently.

## 6. Initialize the target repository

From the target repository:

```bash
python3 <using-superplan-root>/scripts/init_workspace.py \
  --model gpt-5.6
```

Initialization validates the active profile before writing anything, then:

- creates `docs/superplan/human/{prd.md,features.md,bugs.md}` when missing
- creates `docs/superplan/plans/README.md`
- synchronizes the managed `AGENTS.md` guardrails block

Use `$using-superplan` as the main entry skill after initialization. The GPT-5.6
profile intentionally relies on Codex-native delegation and does not install or
require `subagent-driven-development`.
