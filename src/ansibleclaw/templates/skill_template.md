---
name: ansible-{{ skill_name }}
description: >-
  {{ short_description }}
  Use when managing {{ skill_name | replace('_', ' ') }} resources on remote hosts via Ansible.
---

# {{ module_name }}

{{ short_description }}

## When to Use This Skill

Use the `{{ module_name }}` Ansible module when you need to manage {{ skill_name | replace('_', ' ') }} on remote hosts. This is preferable to local CLI commands when:

- Targeting one or more **remote** hosts over SSH
- You need **idempotent** state management (ensure a desired state, not just run a command)
- You want **audit trails** and **dry-run** capability via `--check`

Do **not** use this for basic local file operations or CLI tasks that the agent can handle natively.

## Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
{% for p in params -%}
| `{{ p.name }}` | {{ p.type }} | {{ "yes" if p.required else "no" }} | {{ p.default if p.default is not none else "-" }} | {{ p.description | truncate(120) }} |
{% endfor %}
{% if params | selectattr("choices") | list %}
### Parameter Choices

{% for p in params %}{% if p.choices %}
- **{{ p.name }}**: {{ p.choices | join(", ") }}
{% endif %}{% endfor %}
{% endif %}

## Usage

Run this module using the `ansible` CLI (from `ansible-core`):

```bash
ansible <host-pattern> -m {{ module_name }} -a "<key=value arguments>" -b --check --diff
```

### Quick Examples

```bash
# Dry-run first (always recommended for destructive operations)
ansible webservers -m {{ module_name }} -a "{{ example_args }}" -b --check --diff

# Apply the change
ansible webservers -m {{ module_name }} -a "{{ example_args }}" -b --diff
```

{% if examples %}
### Examples from Ansible Documentation

```yaml
{{ examples }}
```
{% endif %}

## Key Flags

| Flag | Purpose |
|------|---------|
| `-b` | Run with sudo/become (required for most system changes) |
| `--check` | Dry-run mode -- shows what **would** change without applying |
| `--diff` | Shows detailed before/after differences |
| `-i <path>` | Specify inventory file (see Inventory section below) |
| `-l <pattern>` | Limit to specific hosts within a group |

## JSON Output

To get structured JSON output for programmatic parsing:

```bash
ANSIBLE_STDOUT_CALLBACK=json ansible <hosts> -m {{ module_name }} -a "<args>" -b
```

Or set `stdout_callback = json` in your `ansible.cfg` (AnsibleClaw projects include this by default).

## Safety

- **Always dry-run first**: Use `--check --diff` before applying destructive changes
- **Become/sudo**: Most system-level modules require `-b`. Check the parameters above for guidance.
- **Idempotency**: This module is idempotent -- running it multiple times with the same arguments produces the same result

## Inventory

When running from inside the AnsibleClaw project, `ansible.cfg` sets the default inventory automatically. When using this skill from another location:

- Specify inventory explicitly: `-i /path/to/inventory.yml`
- Set environment variable: `export ANSIBLE_INVENTORY=/path/to/inventory.yml`
- Use Ansible's default: `/etc/ansible/hosts`
- Target a single host directly: `ansible <hostname>, -m {{ module_name }} -a "..."` (note the trailing comma)
