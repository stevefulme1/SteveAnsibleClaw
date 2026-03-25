---
name: ansible-copy
description: >-
  Copy files to remote locations
  Use when managing copy resources on remote hosts via Ansible.
---

# ansible.builtin.copy

Copy files to remote locations

## When to Use This Skill

Use the `ansible.builtin.copy` Ansible module when you need to manage copy on remote hosts. This is preferable to local CLI commands when:

- Targeting one or more **remote** hosts over SSH
- You need **idempotent** state management (ensure a desired state, not just run a command)
- You want **audit trails** and **dry-run** capability via `--check`

Do **not** use this for basic local file operations or CLI tasks that the agent can handle natively.

## Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `dest` | path | yes | - | Remote absolute path where the file should be copied to. If O(src) is a directory, this must be a directory too. If... |
| `attributes` | str | no | - | The attributes the resulting filesystem object should have. To get supported flags look at the man page for... |
| `backup` | bool | no | False | Create a backup file including the timestamp information so you can get the original file back if you somehow... |
| `checksum` | str | no | - | SHA1 checksum of the file being transferred. Used to validate that the copy of the file was successful. If this is... |
| `content` | str | no | - | When used instead of O(src), sets the contents of a file directly to the specified value. Works only when O(dest) is... |
| `decrypt` | bool | no | True | This option controls the auto-decryption of source files using vault. |
| `directory_mode` | raw | no | - | Set the access permissions of newly created directories to the given mode. Permissions on existing directories do... |
| `follow` | bool | no | False | This flag indicates that filesystem links in the destination, if they exist, should be followed. |
| `force` | bool | no | True | Influence whether the remote file must always be replaced. If V(true), the remote file will be replaced when... |
| `group` | str | no | - | Name of the group that should own the filesystem object, as would be fed to C(chown). When left unspecified, it uses... |
| `local_follow` | bool | no | - | This flag indicates that filesystem links in the source tree, if they exist, should be followed. |
| `mode` | raw | no | - | The permissions of the destination file or directory. For those used to C(/usr/bin/chmod) remember that modes are... |
| `owner` | str | no | - | Name of the user that should own the filesystem object, as would be fed to C(chown). When left unspecified, it uses... |
| `remote_src` | bool | no | False | Influence whether O(src) needs to be transferred or already is present remotely. If V(false), it will search for... |
| `selevel` | str | no | - | The level part of the SELinux filesystem object context. This is the MLS/MCS attribute, sometimes known as the... |
| `serole` | str | no | - | The role part of the SELinux filesystem object context. When set to V(_default), it will use the C(role) portion of... |
| `setype` | str | no | - | The type part of the SELinux filesystem object context. When set to V(_default), it will use the C(type) portion of... |
| `seuser` | str | no | - | The user part of the SELinux filesystem object context. By default it uses the V(system) policy, where applicable.... |
| `src` | path | no | - | Local path to a file to copy to the remote server. This can be absolute or relative. If path is a directory, it is... |
| `unsafe_writes` | bool | no | False | Influence when to use atomic operation to prevent data corruption or inconsistent reads from the target filesystem... |
| `validate` | str | no | - | The validation command to run before copying the updated file into the final destination. A temporary file path is... |

## Usage

Run this module using the `ansible` CLI (from `ansible-core`):

```bash
ansible <host-pattern> -m ansible.builtin.copy -a "<key=value arguments>" -b --check --diff
```

### Quick Examples

```bash
# Dry-run first (always recommended for destructive operations)
ansible webservers -m ansible.builtin.copy -a "dest=/etc/foo.conf" -b --check --diff

# Apply the change
ansible webservers -m ansible.builtin.copy -a "dest=/etc/foo.conf" -b --diff
```

### Examples from Ansible Documentation

```yaml
- name: Copy file with owner and permissions
  ansible.builtin.copy:
    src: /srv/myfiles/foo.conf
    dest: /etc/foo.conf
    owner: foo
    group: foo
    mode: '0644'

- name: Copy file with owner and permission, using symbolic representation
  ansible.builtin.copy:
    src: /srv/myfiles/foo.conf
    dest: /etc/foo.conf
    owner: foo
    group: foo
    mode: u=rw,g=r,o=r

- name: Another symbolic mode example, adding some permissions and removing others
  ansible.builtin.copy:
    src: /srv/myfiles/foo.conf
    dest: /etc/foo.conf
    owner: foo
    group: foo
    mode: u+rw,g-wx,o-rwx

- name: Copy a new "ntp.conf" file into place, backing up the original if it differs from the copied version
  ansible.builtin.copy:
    src: /mine/ntp.conf
    dest: /etc/ntp.conf
    owner: root
    group: root
    mode: '0644'
    backup: yes

- name: Copy a new "sudoers" file into place, after passing validation with visudo
  ansible.builtin.copy:
    src: /mine/sudoers
    dest: /etc/sudoers
    validate: /usr/sbin/visudo -csf %s

- name: Copy a "sudoers" file on the remote machine for editing
  ansible.builtin.copy:
    src: /etc/sudoers
    dest: /etc/sudoers.edit
    remote_src: yes
    validate: /usr/sbin/visudo -csf %s

- name: Copy using inline content
  ansible.builtin.copy:
    content: '# This file was moved to /etc/other.conf'
    dest: /etc/mine.conf

- name: If follow=yes, /path/to/file will be overwritten by contents of foo.conf
  ansible.builtin.copy:
    src: /etc/foo.conf
    dest: /path/to/link  # link to /path/to/file
    follow: yes

- name: If follow=no, /path/to/link will become a file and be overwritten by contents of foo.conf
  ansible.builtin.copy:
    src: /etc/foo.conf
    dest: /path/to/link  # link to /path/to/file
    follow: no
```

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
ANSIBLE_STDOUT_CALLBACK=json ansible <hosts> -m ansible.builtin.copy -a "<args>" -b
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
- Target a single host directly: `ansible <hostname>, -m ansible.builtin.copy -a "..."` (note the trailing comma)
