# AnsibleClaw User Guide

This guide covers everything you need to install, configure, and use AnsibleClaw -- both the command-line interface and the web dashboard.

---

## Table of Contents

- [Installation](#installation)
- [Concepts](#concepts)
- [CLI Reference](#cli-reference)
  - [ansibleclaw generate](#ansibleclaw-generate)
  - [ansibleclaw search](#ansibleclaw-search)
  - [ansibleclaw ui](#ansibleclaw-ui)
- [Web Dashboard](#web-dashboard)
  - [Skills Library](#skills-library)
  - [Module Search](#module-search)
  - [Skill Generator](#skill-generator)
  - [Inventory Manager](#inventory-manager)
- [Built-In Skills](#built-in-skills)
- [Inventory Setup](#inventory-setup)
- [End-to-End Workflows](#end-to-end-workflows)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.10 or later
- `uv` or `pip` package manager

### Install the core CLI

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

This installs `ansibleclaw` and its core dependencies: `ansible-core`, `jinja2`, and `pyyaml`.

### Install with the web dashboard

```bash
uv pip install -e ".[ui]"
```

This adds `fastapi`, `uvicorn`, and `python-multipart` for the web UI.

### Install with development tools

```bash
uv pip install -e ".[dev]"
```

This adds `pytest` for running the test suite.

### Verify installation

```bash
ansibleclaw --version
```

---

## Concepts

AnsibleClaw has a clean two-phase model:

**Build-time** -- You (or an AI agent) run `ansibleclaw` to scrape Ansible module documentation and generate SKILL.md files. This requires the `ansibleclaw` package.

**Runtime** -- The generated SKILL.md files teach AI agents to use standard `ansible` CLI commands. The only requirement on the target system is `ansible-core`.

### What is a SKILL.md?

A SKILL.md is a markdown file with YAML frontmatter that teaches an AI agent how to use a specific Ansible module. Each one contains:

- Module description and when to use it
- Parameters table (name, type, required, default, choices)
- Ready-to-use `ansible` CLI examples
- Safety guidance (dry-run, become/sudo, idempotency)
- Inventory portability instructions

### Where do skills live?

By default, generated skills are written to the `skills/` directory inside the project. You can also install them directly into agent-specific directories:

| Platform | Path |
|----------|------|
| Project (default) | `skills/<skill_name>/SKILL.md` |
| Cursor | `~/.cursor/skills/<skill_name>/SKILL.md` |
| Claude Code | `~/.claude/skills/<skill_name>/SKILL.md` |
| Custom | Any path you specify with `--output` |

---

## CLI Reference

AnsibleClaw provides three subcommands: `generate`, `search`, and `ui`.

### ansibleclaw generate

Generate a SKILL.md file for any Ansible module.

```
ansibleclaw generate <module> [--install PLATFORM] [--output DIR]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `module` | Fully-qualified module name (e.g., `ansible.builtin.apt`) |
| `--install PLATFORM` | Install directly to an agent platform (`cursor` or `claude`) |
| `--output DIR` | Write to a custom directory instead of the project `skills/` |

**Examples:**

```bash
# Generate into the project's skills/ directory
ansibleclaw generate "ansible.builtin.apt"
# Output: skills/ansible_apt/SKILL.md

# Generate and install directly into Cursor
ansibleclaw generate "community.general.redis" --install cursor
# Output: ~/.cursor/skills/ansible_redis/SKILL.md

# Generate and install directly into Claude Code
ansibleclaw generate "community.docker.docker_container" --install claude
# Output: ~/.claude/skills/ansible_docker_container/SKILL.md

# Generate to a custom location
ansibleclaw generate "ansible.builtin.user" --output /tmp/my-skills/
# Output: /tmp/my-skills/ansible_user/SKILL.md
```

**Batch generation:**

```bash
for module in ansible.builtin.apt ansible.builtin.systemd ansible.builtin.user; do
    ansibleclaw generate "$module"
done
```

**What happens under the hood:**

1. Runs `ansible-doc <module> --json` to fetch structured documentation
2. Extracts parameters, examples, and description
3. Renders the Jinja2 skill template with the extracted data
4. Writes the SKILL.md to the target directory
5. Prints the output path so you (or an AI agent) can immediately read the result

### ansibleclaw search

Search for Ansible modules by keyword.

```
ansibleclaw search [keyword] [--namespace NS] [--detail MODULE]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `keyword` | Search term to match against module names and descriptions |
| `--namespace`, `-n` | Filter results to a specific namespace (e.g., `community.docker`) |
| `--detail MODULE` | Show full JSON documentation for a specific module |

**Examples:**

```bash
# Search for modules related to "redis"
ansibleclaw search "redis"
#   community.general.redis            Various redis commands, replica and flush
#   community.general.redis_data       Set key value pairs in Redis
#   community.general.redis_info       Gather Redis server information
#   3 module(s) found.

# Search within a specific namespace
ansibleclaw search "container" --namespace community.docker
#   community.docker.docker_container  Manage Docker containers
#   1 module(s) found.

# Browse all modules in a namespace (no keyword)
ansibleclaw search --namespace ansible.builtin

# Get full JSON docs for a module
ansibleclaw search --detail "community.general.redis"
```

**Tip:** Ansible has 3000+ modules. Always use `--namespace` to narrow results when you know the domain (e.g., `community.docker` for Docker, `amazon.aws` for AWS).

### ansibleclaw ui

Launch the web management dashboard.

```
ansibleclaw ui [--port PORT]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--port PORT` | Port to listen on (default: `8600`) |

**Examples:**

```bash
# Start with default port
ansibleclaw ui
# Starting AnsibleClaw UI at http://localhost:8600

# Start on a custom port
ansibleclaw ui --port 9000
```

**Note:** Requires the UI extras to be installed (`uv pip install -e ".[ui]"`). If FastAPI is not available, you'll see a helpful error message telling you how to install it.

---

## Web Dashboard

The web dashboard provides a graphical interface for all AnsibleClaw operations. Start it with `ansibleclaw ui` and open `http://localhost:8600` in your browser.

The dashboard has four pages, accessible from the navigation bar.

### Skills Library

**URL:** `http://localhost:8600/skills`

This is the home page. It shows all installed skills in a table with:

- **Name** -- Click to view the full SKILL.md content
- **Description** -- Short summary from the YAML frontmatter
- **Type** -- `built-in` (ships with AnsibleClaw) or `generated` (created by the factory)
- **Actions:**
  - **Delete** -- Remove a generated skill (built-in skills cannot be deleted)
  - **Install** -- Copy a skill to Cursor or Claude Code's skill directory with one click

Clicking a skill name opens the detail view showing the raw SKILL.md content.

### Module Search

**URL:** `http://localhost:8600/search`

Search for Ansible modules interactively:

1. Enter a **keyword** (e.g., "redis", "docker", "firewall")
2. Optionally enter a **namespace** to filter results (e.g., `community.general`)
3. Click **Search**

Results appear in a table without a page reload (powered by HTMX). For each module you can:

- Click **Details** to expand the module's parameters and examples inline
- Click **Generate Skill** to jump to the generator page pre-filled with that module name

### Skill Generator

**URL:** `http://localhost:8600/generate`

Generate new skills through the browser:

1. Enter the **module name** (e.g., `community.general.redis`)
2. Select a **target**:
   - **Project (skills/)** -- write to the project's skills directory
   - **Cursor** -- install directly to `~/.cursor/skills/`
   - **Claude** -- install directly to `~/.claude/skills/`
   - **Custom path** -- specify any directory
3. Click **Preview** to see what the SKILL.md will look like before generating
4. Click **Generate** to create the skill

The preview pane shows the full rendered SKILL.md in real time without writing any files.

**Tip:** If you arrived from the Search page via a "Generate Skill" link, the module name is pre-filled automatically.

### Inventory Manager

**URL:** `http://localhost:8600/inventory`

View and edit your Ansible inventory (`inventory/hosts.yml`) directly in the browser:

- The current inventory content is displayed in a monospace text editor
- Edit the YAML content as needed
- Click **Save** to write the changes

The editor validates YAML syntax before saving -- if the content is not valid YAML, you'll see an error message and the file won't be overwritten.

---

## Built-In Skills

AnsibleClaw ships with four skills out of the box. These are located in the `skills/` directory and are immediately available when you load the project in an AI agent.

### ansible_manager -- The Executor

Teaches an AI agent to run any Ansible module using the `ansible` CLI. Covers:

- Ad-hoc command syntax: `ansible <hosts> -m <module> -a "<args>" -b`
- Essential flags (`-b`, `--check`, `--diff`, `-i`, `-l`)
- Common patterns (packages, services, users, files, shell commands)
- Safety protocol (always dry-run first)
- JSON output for programmatic parsing
- Inventory portability (inside vs. outside the project)

**Runtime dependency:** `ansible-core` only

### ansible_search -- The Scout

Teaches an AI agent to discover Ansible modules using `ansible-doc`. Covers:

- Namespace-first search strategy (avoid 3000+ module dumps)
- Common namespace reference table (builtin, posix, docker, aws, etc.)
- Step-by-step workflow: list -> inspect -> get JSON
- How to translate playbook YAML examples to CLI ad-hoc commands
- When to escalate to the factory for complex modules

**Runtime dependency:** `ansible-core` only

### ansible_skills_factory -- The Architect

Teaches an AI agent to generate new skills on-demand using `ansibleclaw generate`. Covers:

- When to generate vs. using the manager skill directly
- All output targets (project, Cursor, Claude, custom)
- The self-expansion workflow: search -> generate -> read -> use
- What each generated SKILL.md contains

**Runtime dependency:** `ansibleclaw` (this is the only skill that requires the build tool)

### ansible_package -- OOTB Showcase

A pre-generated skill for `ansible.builtin.package`, demonstrating what factory output looks like. Covers:

- OS-agnostic package management (auto-detects apt, dnf, yum, etc.)
- Parameters: `name`, `state` (present/absent/latest), `use`
- Concrete CLI examples with real values

**Runtime dependency:** `ansible-core` only

---

## Inventory Setup

AnsibleClaw includes a starter inventory at `inventory/hosts.yml`:

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
  children:
    webservers:
      hosts:
        web1.example.com:
        web2.example.com:
    dbservers:
      hosts:
        db1.example.com:
```

### Editing the inventory

**Via CLI:** Edit `inventory/hosts.yml` with any text editor.

**Via Web UI:** Navigate to the Inventory page and edit directly in the browser.

### How ansible.cfg helps

The project's `ansible.cfg` sets two defaults:

```ini
[defaults]
inventory = inventory/hosts.yml
stdout_callback = json
```

This means any `ansible` command run from the project directory automatically uses the local inventory and returns JSON output. No `-i` flag or environment variables needed.

### Using skills outside the project

When a generated SKILL.md is used outside the AnsibleClaw project directory, the inventory section in each skill explains how to specify inventory:

```bash
# Explicit flag
ansible -i /path/to/inventory.yml webservers -m ansible.builtin.package -a "name=nginx state=present" -b

# Environment variable
export ANSIBLE_INVENTORY=/path/to/inventory.yml

# Single host shortcut (note the trailing comma)
ansible myhost.example.com, -m ansible.builtin.package -a "name=nginx state=present" -b
```

---

## End-to-End Workflows

### Workflow 1: Generate a skill from the CLI

```bash
# 1. Search for the module you need
ansibleclaw search "docker" --namespace community.docker

# 2. Generate a skill for it
ansibleclaw generate "community.docker.docker_container"
# Skill generated: /path/to/skills/ansible_docker_container/SKILL.md

# 3. Read the generated skill
cat skills/ansible_docker_container/SKILL.md

# 4. Use it (or let your AI agent use it)
ansible webservers -m community.docker.docker_container \
  -a "name=myapp image=nginx state=started" -b --check --diff
```

### Workflow 2: Generate a skill from the web UI

1. Run `ansibleclaw ui`
2. Go to **Search** -- search for "docker container"
3. Click **Details** on `community.docker.docker_container`
4. Click **Generate Skill**
5. On the Generate page, click **Preview** to inspect the output
6. Select **Cursor** as the target and click **Generate**
7. The skill is now at `~/.cursor/skills/ansible_docker_container/SKILL.md`

### Workflow 3: AI agent self-expansion

When an AI agent encounters a task requiring an unfamiliar Ansible module:

1. Agent reads `ansible_search` skill and runs `ansible-doc --list community.general | grep redis`
2. Agent reads `ansible_skills_factory` skill and runs `ansibleclaw generate "community.general.redis"`
3. CLI prints: `Skill generated: skills/ansible_redis/SKILL.md`
4. Agent reads the new `skills/ansible_redis/SKILL.md` for parameter guidance
5. Agent runs: `ansible redis_cluster -m community.general.redis -a "..." -b`

### Workflow 4: Batch generate for a team

```bash
# Generate skills for your team's most-used modules
for module in \
    ansible.builtin.apt \
    ansible.builtin.systemd \
    ansible.builtin.user \
    ansible.builtin.copy \
    ansible.builtin.template \
    community.docker.docker_container \
    community.general.ufw \
    community.mysql.mysql_db; do
    ansibleclaw generate "$module" --install cursor
done
```

Every developer on the team now has these skills available in Cursor.

---

## Configuration

AnsibleClaw reads configuration from environment variables with sensible defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| `ANSIBLECLAW_SKILLS_DIR` | `<project>/skills/` | Where generated skills are written |
| `ANSIBLECLAW_INVENTORY` | `<project>/inventory/hosts.yml` | Path to the Ansible inventory file |

**Example:**

```bash
export ANSIBLECLAW_SKILLS_DIR=/opt/shared-skills/
ansibleclaw generate "ansible.builtin.apt"
# Writes to /opt/shared-skills/ansible_apt/SKILL.md
```

### Install paths

Skills can be installed directly to agent platforms:

| Platform | Install Path |
|----------|-------------|
| `cursor` | `~/.cursor/skills/` |
| `claude` | `~/.claude/skills/` |

---

## Troubleshooting

### "ansible-doc not found"

AnsibleClaw needs `ansible-core` installed in the same Python environment. Verify:

```bash
which ansible-doc
ansible-doc --version
```

If using a virtual environment, make sure `ansible-core` is installed there:

```bash
uv pip install ansible-core
```

### "Web UI dependencies not installed"

The web dashboard requires extra packages. Install them:

```bash
uv pip install -e ".[ui]"
```

### "No modules found" when searching

Ansible collections need to be installed for their modules to appear in `ansible-doc`. The built-in modules (`ansible.builtin.*`) are always available with `ansible-core`. For community modules:

```bash
ansible-galaxy collection install community.general
ansible-galaxy collection install community.docker
```

### Module not found during generation

Same as above -- the collection containing the module must be installed:

```bash
ansible-galaxy collection install <namespace.collection>
ansibleclaw generate "<namespace.collection.module>"
```

### Inventory not found when running ansible commands

If you're running `ansible` commands outside the AnsibleClaw project directory, `ansible.cfg` won't be picked up. Use `-i` to specify the inventory path explicitly:

```bash
ansible -i /path/to/AnsibleClaw/inventory/hosts.yml webservers -m ping
```

### Running tests

```bash
uv pip install -e ".[dev]"
python -m pytest tests/ -v
```
