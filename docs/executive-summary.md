# AnsibleClaw: Bringing Ansible to the AI Agent Era

## Executive Summary

AnsibleClaw is an open-source framework that converts Ansible's 3,000+ modules into portable AI agent skills. It bridges the gap between Ansible's mature infrastructure automation ecosystem and the rapidly growing AI agent skills standard, enabling AI coding assistants to manage infrastructure using battle-tested, idempotent Ansible modules instead of generating ad-hoc scripts.

---

## Why Now

### Agent Skills Are the New Plugin System

Agent Skills -- the open standard for packaging task knowledge into portable `SKILL.md` files -- have become the primary extension mechanism for AI coding assistants. The numbers tell the story:

- **ClawHub** (OpenClaw's marketplace) hosts **26,000+ skills** with 2,100+ new skills added per week
- **25+ compatible platforms**: Claude Code, Cursor, GitHub Copilot, Gemini CLI, OpenClaw, and more
- **NVIDIA NemoClaw** (announced GTC 2026) builds enterprise security around OpenClaw's skill system
- Agent skills are to AI agents what packages are to programming languages -- the standard unit of capability distribution

Every major AI platform now loads skills from `~/.cursor/skills/`, `~/.claude/skills/`, or equivalent directories. The ecosystem is growing exponentially, but **infrastructure automation is underrepresented**. Most skills focus on development workflows, not operations.

### Ansible Is Naturally Agentic

Ansible was built with properties that map perfectly to what AI agents need:

| Ansible Property | Agent Benefit |
|-----------------|---------------|
| **`ansible-doc` structured documentation** | Every module has machine-readable parameter specs, types, defaults, choices, and examples -- exactly what a skill definition requires |
| **Declarative, idempotent modules** | Agents declare desired state instead of writing imperative scripts. Running the same command twice produces the same result with no side effects |
| **Ad-hoc CLI interface** | A single `ansible <hosts> -m <module> -a "<args>"` command maps directly to a skill's "how to use" section |
| **3,000+ modules across 50+ namespaces** | Instant coverage of packages, services, users, files, Docker, AWS, GCP, Azure, databases, networking, and more |
| **Built-in safety mechanisms** | `--check --diff` provides dry-run previews before any change is applied |

No other infrastructure tool combines structured documentation, declarative execution, a flat CLI interface, and a massive module library this cleanly.

### The Cost and Reliability Problem

When AI agents manage infrastructure by generating shell scripts on the fly:

- **Every invocation costs tokens** -- the agent reasons about the script, writes it, handles edge cases
- **Scripts are fragile** -- they lack idempotency, error handling, and cross-platform support
- **Outcomes are unpredictable** -- running the same script twice may break things
- **No dry-run capability** -- there's no safe way to preview changes

Ansible modules solve all of these. A skill that teaches `ansible webservers -m apt -a "name=nginx state=present" -b` is:

- **Cheaper** -- the agent reads a skill once and issues a one-liner; no script generation
- **Idempotent** -- running it twice is safe; Ansible checks current state first
- **Predictable** -- the module's behavior is well-defined and documented
- **Auditable** -- `--check --diff` shows exactly what would change before applying

---

## How It Works

### Architecture: Build-Time Generation, Runtime Simplicity

AnsibleClaw operates on the Ansible control plane as a **build-time tool**. It scrapes `ansible-doc`, generates skill packages, and gets out of the way. At runtime, only `ansible-core` is needed.

```
┌─────────────────────────────────────────────────────────┐
│  Build-Time (ansibleclaw)                               │
│                                                         │
│  ansible-doc --json ──▶ parser ──▶ templates ──▶ SKILL  │
│                                                         │
│  Input: module FQCN    Output: SKILL.md + scripts/      │
│         (e.g. ansible.builtin.apt)   + playbook         │
└────────────────────────┬────────────────────────────────┘
                         │ copy / --install
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Runtime (ansible-core only)                            │
│                                                         │
│  AI Agent reads SKILL.md                                │
│       │                                                 │
│       ▼                                                 │
│  ansible <hosts> -m <module> -a "<args>" --check --diff │
│       │                                                 │
│       ▼                                                 │
│  Remote Hosts (via SSH)                                 │
└─────────────────────────────────────────────────────────┘
```

### Injecting into Existing Ansible Workflows

AnsibleClaw does not replace or wrap Ansible. It sits alongside existing workflows:

- **Users keep their `ansible.cfg`, inventory, and playbooks** -- AnsibleClaw doesn't touch them
- **`ansible-core` is the only runtime dependency** -- already installed on every control plane
- **Generated skills use standard `ansible` CLI commands** -- no proprietary wrapper
- **Skills are portable files** -- copy them anywhere, no daemon or server required

An operator installs AnsibleClaw on their control plane, generates skills for the modules their team uses, and distributes them to AI agents. The agents then execute standard Ansible commands, inheriting all of Ansible's safety and idempotency guarantees.

### Generated Skill Package

Each skill is a complete Agent Skills package:

```
ansible_apt/
├── SKILL.md              # Agent instructions: parameters, usage, safety rules
├── scripts/
│   ├── run.sh            # Wrapper (dry-run by default, --apply to execute)
│   └── check.sh          # Prerequisite validator (ansible installed? module available?)
└── assets/
    └── playbook.yml      # Ready-to-use Ansible playbook
```

The `SKILL.md` is auto-generated from `ansible-doc` and includes:

- YAML frontmatter for agent auto-discovery
- Complete parameter table (type, required, default, choices, description)
- CLI usage examples translated from playbook YAML to ad-hoc commands
- Safety protocol (always `--check --diff` first)
- JSON output instructions for structured results

### Built-In Skills: The Bootstrap Layer

Three built-in skills ship with the package, forming a self-expanding capability system:

| Skill | What It Teaches | Dependency |
|-------|----------------|------------|
| `ansible_manager` | Execute any module via `ansible` CLI | `ansible-core` |
| `ansible_search` | Discover modules via `ansible-doc` | `ansible-core` |
| `ansible_skills_factory` | Generate new skills on-demand via `ansibleclaw generate` | `ansible-claw` |

The workflow is self-expanding: the agent searches for a module, generates a skill, reads it, and uses it. Each subsequent use costs minimal tokens because the skill is already materialized.

### Web Dashboard

A built-in web UI (`ansibleclaw ui`) provides:

- **Skills Library** -- browse, search, install to agents, download as ZIP
- **Module Search** -- search Ansible modules by keyword/namespace with inline details
- **Skill Generator** -- preview and generate skills from the browser

### CLI

```bash
pip install ansible-claw            # install
ansibleclaw search "redis"          # find modules
ansibleclaw generate "community.general.redis"           # generate skill
ansibleclaw generate "ansible.builtin.apt" --install cursor  # generate + install
ansibleclaw generate "ansible.builtin.apt" --zip         # generate + package
ansibleclaw ui                      # launch web dashboard
```

---

## Roadmap

### Phase 1: Skill Generation (Current)

Convert Ansible modules into AI agent skills using `ansible-doc` and module metadata.

- Generate SKILL.md + companion scripts from any Ansible module
- CLI and web dashboard for generation, search, and distribution
- ZIP packaging for portable distribution via ClawHub or direct sharing
- Built-in skills that bootstrap the search-generate-use workflow
- Published as `ansible-claw` on PyPI

**Status**: Functional. Generates skills for any installed Ansible module.

### Phase 2: Autonomous Agent Integration

Integrate with OpenClaw and NemoClaw to create fully autonomous infrastructure agents.

- **OpenClaw native skill**: Publish AnsibleClaw skills to ClawHub so OpenClaw agents can discover and install them automatically
- **NemoClaw security integration**: Leverage NemoClaw's OpenShell runtime for policy-based guardrails -- control which hosts, modules, and operations an agent is allowed to execute
- **Autonomous loop**: Agent receives a high-level objective ("set up a production Redis cluster"), plans the required modules, generates skills as needed, executes with dry-run safety, and reports results
- **Feedback-driven refinement**: Agent learns from execution results and adjusts parameters, building operational knowledge over time

The combination of Ansible's idempotent execution model and NemoClaw's security guardrails creates a uniquely safe foundation for autonomous infrastructure agents -- the agent can try, verify, and retry without risk of inconsistent state, and the security layer ensures it stays within defined boundaries.

---

## Why Ansible Should Care

1. **Distribution channel**: 26,000+ skills on ClawHub, growing at 2,100/week. Ansible modules as skills puts Ansible in front of every AI agent user.

2. **Competitive moat**: Ansible's `ansible-doc` + idempotent modules + ad-hoc CLI is a combination no other infrastructure tool can match for skill generation. This is a structural advantage.

3. **Zero friction adoption**: AnsibleClaw requires no changes to Ansible itself. It reads `ansible-doc`, generates files, and uses standard `ansible` commands. It works with every existing Ansible installation.

4. **New user funnel**: Developers using AI agents discover Ansible through skills before they learn playbooks. The agent teaches them Ansible organically.

5. **Enterprise story with NemoClaw**: NVIDIA's investment in NemoClaw validates the agent + skills model for enterprise. Ansible skills running inside NemoClaw's security boundary is a compelling enterprise narrative.

---

## Links

- **Repository**: [github.com/micytao/AnsibleClaw](https://github.com/micytao/AnsibleClaw)
- **PyPI**: `pip install ansible-claw`
- **Agent Skills Standard**: [agentskill.sh](https://agentskill.sh/readme)
- **OpenClaw**: [openclawlab.com](https://openclawlab.com)
- **NemoClaw**: [nvidia.com/nemoclaw](https://www.nvidia.com/nemoclaw)
