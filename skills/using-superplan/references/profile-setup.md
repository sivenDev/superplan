# GPT-5.6 Profile Setup

Use dependency checks for initialization, installation, diagnostics, unresolved dependency state, or after the model, profile manifest, skill locations, or supporting environment changes. Reuse a still-current successful check otherwise.

The installer supports only `gpt-5.6` and `gpt-5.6-*`; it does not select the active Codex model.

1. Preview the resolved target and conflicts without writing:

   `python3 <using-superplan-root>/scripts/install_superpowers_profile.py --model gpt-5.6 --dry-run`

2. For a clean target, install without `--dry-run`. If conflicts require replacement, present the dry-run target and conflicts and obtain explicit approval before adding `--replace-existing`. Verified same-name skills are backed up before replacement.
3. Restart Codex or open a new chat, select GPT-5.6, then verify:

   `python3 <using-superplan-root>/scripts/check_superpowers.py --model gpt-5.6`

For non-profile dependency diagnosis, run `check_superpowers.py` without `--model` and pass explicit `--superpowers-root` or `--skills-dir` locations when needed.
