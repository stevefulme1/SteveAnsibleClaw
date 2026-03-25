"""Tests for skill template rendering."""

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

from ansibleclaw.config import TEMPLATE_DIR, TEMPLATE_PATH


@pytest.fixture
def render_template():
    """Helper to render the skill template with given context."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(TEMPLATE_PATH.name)

    def _render(**kwargs):
        return template.render(**kwargs)

    return _render


class TestSkillTemplate:
    def test_renders_frontmatter(self, render_template):
        result = render_template(
            module_name="ansible.builtin.package",
            skill_name="package",
            short_description="Generic OS package manager",
            params=[],
            examples="",
            example_args="name=nginx state=present",
        )
        assert "name: ansible-package" in result
        assert "Generic OS package manager" in result

    def test_renders_parameters_table(self, render_template):
        params = [
            {
                "name": "name",
                "type": "str",
                "required": True,
                "default": None,
                "choices": None,
                "description": "Package name",
                "aliases": [],
            },
            {
                "name": "state",
                "type": "str",
                "required": True,
                "default": None,
                "choices": ["present", "absent"],
                "description": "Whether to install or remove",
                "aliases": [],
            },
        ]
        result = render_template(
            module_name="ansible.builtin.package",
            skill_name="package",
            short_description="Generic OS package manager",
            params=params,
            examples="",
            example_args="name=nginx state=present",
        )
        assert "| `name` |" in result
        assert "| `state` |" in result
        assert "| yes |" in result

    def test_renders_choices_section(self, render_template):
        params = [
            {
                "name": "state",
                "type": "str",
                "required": True,
                "default": None,
                "choices": ["present", "absent", "latest"],
                "description": "Desired state",
                "aliases": [],
            },
        ]
        result = render_template(
            module_name="ansible.builtin.package",
            skill_name="package",
            short_description="Test",
            params=params,
            examples="",
            example_args="state=present",
        )
        assert "present, absent, latest" in result

    def test_renders_examples_section(self, render_template):
        examples_yaml = "- name: Install nginx\n  ansible.builtin.package:\n    name: nginx\n"
        result = render_template(
            module_name="ansible.builtin.package",
            skill_name="package",
            short_description="Test",
            params=[],
            examples=examples_yaml,
            example_args="name=nginx",
        )
        assert "Examples from Ansible Documentation" in result
        assert "Install nginx" in result

    def test_no_examples_section_when_empty(self, render_template):
        result = render_template(
            module_name="ansible.builtin.package",
            skill_name="package",
            short_description="Test",
            params=[],
            examples="",
            example_args="name=nginx",
        )
        assert "Examples from Ansible Documentation" not in result

    def test_renders_inventory_section(self, render_template):
        result = render_template(
            module_name="ansible.builtin.package",
            skill_name="package",
            short_description="Test",
            params=[],
            examples="",
            example_args="name=nginx",
        )
        assert "## Inventory" in result
        assert "-i /path/to/inventory.yml" in result
        assert "ANSIBLE_INVENTORY" in result
        assert "/etc/ansible/hosts" in result

    def test_renders_safety_section(self, render_template):
        result = render_template(
            module_name="ansible.builtin.package",
            skill_name="package",
            short_description="Test",
            params=[],
            examples="",
            example_args="name=nginx",
        )
        assert "## Safety" in result
        assert "--check --diff" in result
        assert "idempotent" in result

    def test_renders_json_output_section(self, render_template):
        result = render_template(
            module_name="ansible.builtin.package",
            skill_name="package",
            short_description="Test",
            params=[],
            examples="",
            example_args="name=nginx",
        )
        assert "ANSIBLE_STDOUT_CALLBACK=json" in result
