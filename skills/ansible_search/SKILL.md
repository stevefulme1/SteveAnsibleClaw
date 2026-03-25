---
name: ansible-search
description: >-
  Discover available Ansible modules using ansible-doc. Use when you need to find
  the right module for a task, explore what modules exist in a namespace,
  or get detailed parameter documentation for a specific module.
---

# Ansible Search

Discover and explore Ansible modules using the `ansible-doc` CLI from `ansible-core`.

## Namespace-First Strategy

Ansible has 3000+ modules. Always filter by namespace first to avoid overwhelming output.

### Common Namespaces

| Namespace | Domain |
|-----------|--------|
| `ansible.builtin` | Core modules (package, service, user, file, copy, template, git, cron, ...) |
| `ansible.posix` | POSIX systems (firewalld, sysctl, mount, selinux, ...) |
| `community.general` | Broad community collection (redis, ufw, htpasswd, timezone, ...) |
| `community.docker` | Docker containers, images, networks, volumes |
| `community.mysql` | MySQL/MariaDB databases and users |
| `community.postgresql` | PostgreSQL databases, users, schemas |
| `amazon.aws` | AWS EC2, S3, RDS, IAM, etc. |
| `google.cloud` | GCP compute, storage, networking |
| `azure.azcollection` | Azure VMs, storage, networking |

## How to Search

### Step 1: List modules in a namespace

```bash
ansible-doc --list community.docker
```

This returns a compact list of module names + short descriptions.

### Step 2: Get details for a specific module

```bash
ansible-doc community.docker.docker_container
```

This shows full documentation: description, parameters, examples, and return values.

### Step 3: Get machine-readable JSON (optional)

```bash
ansible-doc community.docker.docker_container --json
```

Useful for programmatic parsing. Returns structured parameter specs.

## Quick Search by Keyword

If you're not sure which namespace to look in:

```bash
ansible-doc --list | grep -i redis
```

Or search across a specific namespace:

```bash
ansible-doc --list community.general | grep -i redis
```

## Reading Module Documentation

When you run `ansible-doc <module>`, look for these sections:

- **DESCRIPTION** -- What the module does
- **OPTIONS** -- Parameters with types, defaults, and whether they're required
- **EXAMPLES** -- Ready-to-use YAML snippets (adapt these to CLI `-a` syntax)
- **RETURN VALUES** -- What the module returns after execution

### Translating YAML examples to CLI

Documentation examples use YAML playbook syntax:
```yaml
- name: Install nginx
  ansible.builtin.package:
    name: nginx
    state: present
```

Convert to CLI ad-hoc command:
```bash
ansible webservers -m ansible.builtin.package -a "name=nginx state=present" -b
```

## When to Generate a Dedicated Skill

After finding a module, consider using the `ansible_skills_factory` skill to generate a dedicated SKILL.md if:

- The module has **many parameters** (10+) that are hard to remember
- You will use the module **repeatedly** across different tasks
- The module has **complex parameter interactions** (e.g., mutually exclusive options)

For simple modules (3-5 parameters), just use the `ansible_manager` skill directly.
