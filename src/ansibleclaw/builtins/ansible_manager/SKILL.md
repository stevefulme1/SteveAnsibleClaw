---
name: ansible-manager
description: >-
  Execute any Ansible module on remote or local hosts using the standard ansible CLI.
  Use when the user asks to install packages, manage services, configure systems,
  create users, or perform any infrastructure task on remote hosts.
---

# Ansible Manager

Execute any Ansible module against remote or local hosts. This skill gives you the full
power of Ansible's 3000+ modules through the standard `ansible` CLI.

## When to Use

Use this skill when the task involves:

- **Remote hosts** -- anything that needs to happen on a machine other than this one
- **System state management** -- installing packages, starting services, creating users, managing firewall rules
- **Idempotent operations** -- ensuring a desired state rather than running a one-off command
- **Audit/dry-run needs** -- previewing changes before applying them

Do **not** use this for local file editing, reading files, or running simple CLI commands -- handle those natively.

## Ad-Hoc Command Syntax

```bash
ansible <host-pattern> -m <module> -a "<key=value args>" [flags]
```

### Essential Flags

| Flag | Purpose | Example |
|------|---------|---------|
| `-m` | Module name | `-m ansible.builtin.apt` |
| `-a` | Module arguments | `-a "name=nginx state=present"` |
| `-b` | Run with sudo (become) | Required for most system changes |
| `--check` | Dry-run -- show what would change | Always use first for destructive ops |
| `--diff` | Show before/after differences | Pair with `--check` for safe preview |
| `-i` | Inventory file path | `-i /path/to/hosts.yml` |
| `-l` | Limit to specific hosts | `-l web1.example.com` |

## Common Patterns

### Install a package
```bash
ansible webservers -m ansible.builtin.package -a "name=nginx state=present" -b
```

### Start and enable a service
```bash
ansible webservers -m ansible.builtin.systemd -a "name=nginx state=started enabled=true" -b
```

### Create a user
```bash
ansible all -m ansible.builtin.user -a "name=deploy shell=/bin/bash groups=sudo" -b
```

### Copy a file to remote hosts
```bash
ansible webservers -m ansible.builtin.copy -a "src=/local/path dest=/remote/path owner=root mode=0644" -b
```

### Run a shell command (when no module fits)
```bash
ansible dbservers -m ansible.builtin.shell -a "pg_isready" -b
```

## JSON Output

To get structured output for programmatic parsing:

```bash
ANSIBLE_STDOUT_CALLBACK=json ansible webservers -m ansible.builtin.package -a "name=nginx state=present" -b
```

If running from inside an AnsibleClaw project, `ansible.cfg` sets JSON output by default.

## Safety Protocol

1. **Always dry-run first** for destructive operations:
   ```bash
   ansible webservers -m ansible.builtin.package -a "name=nginx state=absent" -b --check --diff
   ```
2. Review the output -- look for `"changed": true` entries
3. If it looks correct, run without `--check`:
   ```bash
   ansible webservers -m ansible.builtin.package -a "name=nginx state=absent" -b --diff
   ```

## Inventory

### Inside AnsibleClaw project
The project's `ansible.cfg` sets inventory to `inventory/hosts.yml` automatically. Check it to see available hosts:

```bash
cat inventory/hosts.yml
```

### Outside AnsibleClaw project
Use one of these methods:

- **Explicit flag**: `ansible -i /path/to/inventory.yml ...`
- **Environment variable**: `export ANSIBLE_INVENTORY=/path/to/inventory.yml`
- **Default location**: Ansible looks at `/etc/ansible/hosts`
- **Single host shortcut**: `ansible myhost.example.com, -m ping` (note the trailing comma)

## Finding Modules

If you don't know which module to use, check the `ansible_search` skill for module discovery via `ansible-doc`.
