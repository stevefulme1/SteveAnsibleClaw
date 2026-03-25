"""Central configuration for AnsibleClaw."""

import os
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent

TEMPLATE_DIR = _PKG_DIR / "templates"
TEMPLATE_PATH = TEMPLATE_DIR / "skill_template.md"

BUILTINS_DIR = _PKG_DIR / "builtins"

SKILLS_DIR = Path(os.environ.get(
    "ANSIBLECLAW_SKILLS_DIR",
    Path.cwd() / "skills",
))

INSTALL_PATHS: dict[str, Path] = {
    "cursor": Path.home() / ".cursor" / "skills",
    "claude": Path.home() / ".claude" / "skills",
}
