"""Shared test fixtures for AnsibleClaw."""

import json

import pytest

SAMPLE_MODULE_DOC = {
    "ansible.builtin.package": {
        "doc": {
            "module": "ansible.builtin.package",
            "short_description": "Generic OS package manager",
            "description": ["Installs, upgrades, removes packages using the OS package manager."],
            "options": {
                "name": {
                    "description": [
                        "Package name, or package specifier with version."
                    ],
                    "type": "str",
                    "required": True,
                },
                "state": {
                    "description": [
                        "Whether to install (present), or remove (absent) a package."
                    ],
                    "type": "str",
                    "required": True,
                    "choices": ["present", "absent", "latest"],
                },
                "use": {
                    "description": [
                        "The required package manager module to use."
                    ],
                    "type": "str",
                    "required": False,
                    "default": "auto",
                    "choices": ["auto", "apt", "dnf", "yum"],
                },
            },
        },
        "examples": (
            "- name: Install ntpdate\n"
            "  ansible.builtin.package:\n"
            "    name: ntpdate\n"
            "    state: present\n"
        ),
    }
}

SAMPLE_MODULE_LIST = {
    "ansible.builtin.package": "Generic OS package manager",
    "ansible.builtin.apt": "Manages apt-packages",
    "ansible.builtin.yum": "Manages packages with the yum package manager",
    "community.general.redis": "Various redis commands, replica and flush",
}


@pytest.fixture
def sample_module_doc():
    return SAMPLE_MODULE_DOC


@pytest.fixture
def sample_module_doc_json():
    return json.dumps(SAMPLE_MODULE_DOC)


@pytest.fixture
def sample_module_list():
    return SAMPLE_MODULE_LIST


@pytest.fixture
def sample_module_list_json():
    return json.dumps(SAMPLE_MODULE_LIST)
