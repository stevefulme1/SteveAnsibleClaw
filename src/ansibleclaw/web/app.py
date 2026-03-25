"""AnsibleClaw Web Dashboard.

FastAPI application with routes for skills management, module search,
skill generation with preview, and ZIP download.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml
from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ansibleclaw.config import BUILTINS_DIR, INSTALL_PATHS, SKILLS_DIR, TEMPLATE_DIR, TEMPLATE_PATH
from ansibleclaw.core.packager import package_skill_zip_bytes
from ansibleclaw.core.parser import (
    AnsibleDocError,
    extract_module_metadata,
    get_module_doc,
    search_modules,
)

WEB_DIR = Path(__file__).parent
TEMPLATES = Jinja2Templates(directory=str(WEB_DIR / "templates"))

app = FastAPI(title="AnsibleClaw", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")


def _read_skill_frontmatter(skill_dir: Path) -> dict:
    """Read YAML frontmatter from a SKILL.md file."""
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return {"name": skill_dir.name, "description": ""}
    content = skill_file.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                return fm if isinstance(fm, dict) else {}
            except yaml.YAMLError:
                pass
    return {"name": skill_dir.name, "description": ""}


def _scan_skill_dirs(base: Path, skill_type: str) -> dict[str, dict]:
    """Scan a directory for skill subdirectories and return {name: info}."""
    results: dict[str, dict] = {}
    if not base.exists():
        return results
    for d in sorted(base.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            fm = _read_skill_frontmatter(d)
            results[d.name] = {
                "dir_name": d.name,
                "name": fm.get("name", d.name),
                "description": fm.get("description", ""),
                "type": skill_type,
                "path": str(d),
            }
    return results


def _list_skills() -> list[dict]:
    """List all skills from builtins and user SKILLS_DIR (user overrides builtins)."""
    merged = _scan_skill_dirs(BUILTINS_DIR, "built-in")
    merged.update(_scan_skill_dirs(SKILLS_DIR, "generated"))
    return list(merged.values())


def _resolve_skill_dir(name: str) -> Path | None:
    """Find a skill directory by name, checking SKILLS_DIR first then BUILTINS_DIR."""
    user_dir = SKILLS_DIR / name
    if user_dir.exists() and (user_dir / "SKILL.md").exists():
        return user_dir
    builtin_dir = BUILTINS_DIR / name
    if builtin_dir.exists() and (builtin_dir / "SKILL.md").exists():
        return builtin_dir
    return None


def _is_builtin(name: str) -> bool:
    """Check whether a skill lives in the builtins directory."""
    return (BUILTINS_DIR / name / "SKILL.md").exists()


def _render_skill_md(metadata: dict) -> str:
    """Render skill template -- reuses the same logic as CLI."""
    from jinja2 import Environment, FileSystemLoader
    from ansibleclaw.cli import _build_example_args, _module_to_skill_name

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_PATH.parent)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(TEMPLATE_PATH.name)
    skill_name = _module_to_skill_name(metadata["module_name"]).replace("ansible_", "")
    example_args = _build_example_args(metadata["params"], metadata.get("examples", ""))

    return template.render(
        module_name=metadata["module_name"],
        skill_name=skill_name,
        short_description=metadata["short_description"],
        params=metadata["params"],
        examples=metadata["examples"].strip() if metadata["examples"] else "",
        example_args=example_args,
    )


# --- Routes ---

@app.get("/", response_class=RedirectResponse)
async def index():
    return RedirectResponse(url="/skills")


@app.get("/skills", response_class=HTMLResponse)
async def skills_page(request: Request):
    skills = _list_skills()
    return TEMPLATES.TemplateResponse(request, "skills.html", {
        "skills": skills,
        "page": "skills",
    })


@app.get("/skills/{name}", response_class=HTMLResponse)
async def skill_detail(request: Request, name: str):
    skill_dir = _resolve_skill_dir(name)
    if skill_dir is None:
        return HTMLResponse("Skill not found", status_code=404)
    content = (skill_dir / "SKILL.md").read_text()
    return TEMPLATES.TemplateResponse(request, "skill_detail.html", {
        "name": name,
        "content": content,
        "page": "skills",
    })


@app.delete("/skills/{name}", response_class=HTMLResponse)
async def delete_skill(name: str):
    if _is_builtin(name):
        return HTMLResponse("Cannot delete built-in skills", status_code=400)
    skill_dir = SKILLS_DIR / name
    if not skill_dir.exists():
        return HTMLResponse("Skill not found", status_code=404)
    shutil.rmtree(skill_dir)
    return HTMLResponse("")


@app.post("/skills/{name}/install", response_class=HTMLResponse)
async def install_skill(name: str, platform: str = Form(...)):
    skill_dir = _resolve_skill_dir(name)
    if skill_dir is None:
        return HTMLResponse("Skill not found", status_code=404)
    platform = platform.lower()
    if platform not in INSTALL_PATHS:
        return HTMLResponse(f"Unknown platform: {platform}", status_code=400)
    target = INSTALL_PATHS[platform] / name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(skill_dir, target)
    return HTMLResponse(
        f'<span class="success">\u2713 Installed to {target}</span>'
    )


@app.get("/skills/{name}/download")
async def download_skill(name: str):
    skill_dir = _resolve_skill_dir(name)
    if skill_dir is None:
        return HTMLResponse("Skill not found", status_code=404)
    zip_bytes = package_skill_zip_bytes(skill_dir)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{name}.zip"'},
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    return TEMPLATES.TemplateResponse(request, "search.html", {
        "page": "search",
    })


@app.get("/search/results", response_class=HTMLResponse)
async def search_results(request: Request, q: str = "", ns: str = ""):
    if not q and not ns:
        return HTMLResponse("")
    try:
        if q:
            results = search_modules(q, namespace=ns or None)
        else:
            from ansibleclaw.core.parser import list_modules
            results = list_modules(namespace=ns or None)
    except AnsibleDocError as exc:
        return HTMLResponse(f'<p class="error">{exc}</p>')
    return TEMPLATES.TemplateResponse(request, "_search_results.html", {
        "results": results,
        "query": q,
    })


@app.get("/search/detail/{module:path}", response_class=HTMLResponse)
async def module_detail(request: Request, module: str):
    try:
        doc = get_module_doc(module)
        metadata = extract_module_metadata(doc)
    except AnsibleDocError as exc:
        return HTMLResponse(f'<p class="error">{exc}</p>')
    return TEMPLATES.TemplateResponse(request, "_module_detail.html", {
        "metadata": metadata,
    })


@app.get("/generate", response_class=HTMLResponse)
async def generate_page(request: Request):
    return TEMPLATES.TemplateResponse(request, "generate.html", {
        "page": "generate",
        "platforms": list(INSTALL_PATHS.keys()),
    })


@app.get("/generate/preview", response_class=HTMLResponse)
async def generate_preview(request: Request, module: str = ""):
    if not module:
        return HTMLResponse("")
    try:
        doc = get_module_doc(module)
        metadata = extract_module_metadata(doc)
        preview = _render_skill_md(metadata)
    except AnsibleDocError as exc:
        return HTMLResponse(f'<p class="error">{exc}</p>')
    return HTMLResponse(f"<pre><code>{preview}</code></pre>")


@app.post("/generate", response_class=HTMLResponse)
async def generate_skill(
    module: str = Form(...),
    target: str = Form("project"),
    custom_path: str = Form(""),
):
    try:
        doc = get_module_doc(module)
        metadata = extract_module_metadata(doc)
    except AnsibleDocError as exc:
        return HTMLResponse(f'<p class="error">{exc}</p>', status_code=400)

    from ansibleclaw.cli import _module_to_skill_name, _write_skill_package
    skill_name = _module_to_skill_name(metadata["module_name"])

    if target == "project":
        output_dir = SKILLS_DIR / skill_name
    elif target in INSTALL_PATHS:
        output_dir = INSTALL_PATHS[target] / skill_name
    elif target == "custom" and custom_path:
        output_dir = Path(custom_path) / skill_name
    else:
        return HTMLResponse("Invalid target", status_code=400)

    _write_skill_package(output_dir, metadata)

    download_link = ""
    if target == "project":
        download_link = (
            f' &mdash; <a href="/skills/{skill_name}/download">Download ZIP</a>'
        )

    return HTMLResponse(
        f'<p class="success">Skill generated: <code>{output_dir}</code>'
        f" (SKILL.md, scripts/, assets/){download_link}</p>"
    )


