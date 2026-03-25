"""Skill packaging utilities.

Creates ZIP archives from skill directories following the Agent Skills
open standard. Compatible with Claude.ai upload, agentskill.sh, and
other skill distribution platforms.
"""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path


def package_skill_zip(skill_dir: Path, output_path: Path | None = None) -> Path:
    """Create a ZIP archive from a skill directory.

    The ZIP preserves the directory structure with the skill folder as
    the root entry (e.g., ``ansible_copy/SKILL.md``).

    Args:
        skill_dir: Path to the skill directory containing SKILL.md.
        output_path: Where to write the ZIP. Defaults to
            ``<skill_dir>.zip`` alongside the skill directory.

    Returns:
        Path to the created ZIP file.
    """
    if output_path is None:
        output_path = skill_dir.parent / f"{skill_dir.name}.zip"

    buf = package_skill_zip_bytes(skill_dir)
    output_path.write_bytes(buf)
    return output_path


def package_skill_zip_bytes(skill_dir: Path) -> bytes:
    """Create a ZIP archive in memory and return the raw bytes.

    Useful for streaming HTTP responses without temp files.
    """
    buf = io.BytesIO()
    root_name = skill_dir.name

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _dirnames, filenames in os.walk(skill_dir):
            for filename in sorted(filenames):
                file_path = Path(dirpath) / filename
                arcname = f"{root_name}/{file_path.relative_to(skill_dir)}"
                zf.write(file_path, arcname)

    return buf.getvalue()
