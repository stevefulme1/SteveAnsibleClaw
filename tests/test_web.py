"""Smoke tests for the web UI pages."""
import pytest

try:
    from fastapi.testclient import TestClient
    from ansibleclaw.web.app import app
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

pytestmark = pytest.mark.skipif(not HAS_DEPS, reason="UI deps missing")


@pytest.fixture()
def web_client():
    return TestClient(app)


def test_skills_page(web_client):
    resp = web_client.get("/skills")
    assert resp.status_code == 200
    assert "ansible_manager" in resp.text
    assert "Skills Library" in resp.text


def test_skill_detail_page(web_client):
    resp = web_client.get("/skills/ansible_manager")
    assert resp.status_code == 200


def test_skill_not_found(web_client):
    resp = web_client.get("/skills/nonexistent_skill_xyz")
    assert resp.status_code == 404


def test_search_page(web_client):
    resp = web_client.get("/search")
    assert resp.status_code == 200
    assert "Module Search" in resp.text


def test_generate_page(web_client):
    resp = web_client.get("/generate")
    assert resp.status_code == 200
    assert "Module Name" in resp.text


def test_inventory_page(web_client):
    resp = web_client.get("/inventory")
    assert resp.status_code == 200
    assert "localhost" in resp.text


def test_cannot_delete_builtin_skill(web_client):
    resp = web_client.delete("/skills/ansible_manager")
    assert resp.status_code == 400
    assert "built-in" in resp.text.lower()


def test_root_redirects_to_skills(web_client):
    resp = web_client.get("/", follow_redirects=False)
    assert resp.status_code == 307
    assert "/skills" in resp.headers["location"]


def test_save_invalid_yaml_inventory(web_client):
    resp = web_client.put("/inventory", data={"content": "{{not valid yaml"})
    assert resp.status_code == 400
    assert "Invalid YAML" in resp.text
