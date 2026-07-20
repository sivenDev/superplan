#!/usr/bin/env python3
"""Supported external Superpowers profile definitions."""

from __future__ import annotations

from dataclasses import dataclass


GPT56_REPOSITORY = "https://github.com/eagleagentic/superpowers-gpt-5.6.git"
GPT56_REVISION = "aa973775906c8761a78019aaa21e4f0ccd987925"
MANIFEST_FILENAME = "active-superpowers-profile.json"
MANIFEST_SCHEMA_VERSION = 1


class ProfileSelectionError(ValueError):
    """Raised when a requested model/profile cannot be resolved safely."""


@dataclass(frozen=True)
class SuperpowersProfile:
    name: str
    repository: str
    revision: str
    skills: tuple[str, ...]
    context_budget_script: str
    removed_skills: tuple[str, ...]

    def matches_model(self, model: str) -> bool:
        return model == "gpt-5.6" or model.startswith("gpt-5.6-")


GPT56_PROFILE = SuperpowersProfile(
    name="gpt56",
    repository=GPT56_REPOSITORY,
    revision=GPT56_REVISION,
    skills=(
        "brainstorming",
        "executing-plans",
        "finishing-a-development-branch",
        "receiving-code-review",
        "requesting-code-review",
        "systematic-debugging",
        "test-driven-development",
        "using-git-worktrees",
        "using-superpowers",
        "verification-before-completion",
        "writing-implementation-logs",
        "writing-plans",
        "writing-skills",
    ),
    context_budget_script="skills/superpowers/check-context-budget.sh",
    removed_skills=("subagent-driven-development",),
)

PROFILES = {GPT56_PROFILE.name: GPT56_PROFILE}


def resolve_profile(
    *, profile_name: str | None = None, model: str | None = None
) -> SuperpowersProfile | None:
    """Resolve the only supported profile without falling back to another model."""
    if profile_name is not None:
        profile = PROFILES.get(profile_name)
        if profile is None:
            raise ProfileSelectionError(f"Unsupported Superpowers profile: {profile_name}")
        if model is not None and not profile.matches_model(model):
            raise ProfileSelectionError(
                f"Profile {profile.name} does not match model {model}"
            )
        return profile

    if model is None:
        return None
    if GPT56_PROFILE.matches_model(model):
        return GPT56_PROFILE
    raise ProfileSelectionError(f"Unsupported model: {model}")
