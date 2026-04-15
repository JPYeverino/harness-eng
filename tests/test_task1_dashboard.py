"""
Tests for task-1: dashboard.py binary/text file support in /api/deliverable/{task_id}
and dashboard.html smoke tests for required elements.
"""
import base64
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_decisions(tmp_path: Path, impl_file: str) -> Path:
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir(exist_ok=True)
    decisions = {"entries": [{"impl_file": impl_file}]}
    decisions_file = memory_dir / "task-1_decisions.json"
    decisions_file.write_text(json.dumps(decisions))
    return decisions_file


# ── Dashboard.py endpoint tests ───────────────────────────────────────────────

def test_deliverable_text_md(tmp_path):
    from dashboard import create_app

    md_file = tmp_path / "output.md"
    md_file.write_text("# Hello\nworld")
    make_decisions(tmp_path, "output.md")

    client = TestClient(create_app(root=str(tmp_path)))
    r = client.get("/api/deliverable/task-1")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "text"
    assert isinstance(data["content"], str)
    assert "Hello" in data["content"]
    assert data["filename"] == "output.md"


def test_deliverable_binary_pptx(tmp_path):
    from dashboard import create_app

    pptx_file = tmp_path / "slides.pptx"
    pptx_file.write_bytes(b"\x50\x4B\x03\x04" + b"\x00" * 100)  # PK header
    make_decisions(tmp_path, "slides.pptx")

    client = TestClient(create_app(root=str(tmp_path)))
    r = client.get("/api/deliverable/task-1")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "binary"
    assert isinstance(data["content"], str)
    # Verify it's valid base64
    decoded = base64.b64decode(data["content"])
    assert decoded[:4] == b"\x50\x4B\x03\x04"
    assert data["filename"] == "slides.pptx"


def test_deliverable_unknown_extension_is_binary(tmp_path):
    from dashboard import create_app

    bin_file = tmp_path / "data.xyz"
    bin_file.write_bytes(b"\xDE\xAD\xBE\xEF")
    make_decisions(tmp_path, "data.xyz")

    client = TestClient(create_app(root=str(tmp_path)))
    r = client.get("/api/deliverable/task-1")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "binary"


def test_deliverable_missing_decisions_404(tmp_path):
    from dashboard import create_app

    client = TestClient(create_app(root=str(tmp_path)))
    r = client.get("/api/deliverable/task-1")
    assert r.status_code == 404


def test_deliverable_missing_impl_file_on_disk_404(tmp_path):
    from dashboard import create_app

    make_decisions(tmp_path, "nonexistent.md")

    client = TestClient(create_app(root=str(tmp_path)))
    r = client.get("/api/deliverable/task-1")
    assert r.status_code == 404


# ── dashboard.html smoke tests ────────────────────────────────────────────────

DASHBOARD_HTML = Path(__file__).parent.parent / "dashboard.html"


@pytest.mark.skipif(not DASHBOARD_HTML.exists(), reason="dashboard.html not found")
def test_html_has_deliverable_download_div():
    html = DASHBOARD_HTML.read_text()
    assert 'id="deliverable-download"' in html


@pytest.mark.skipif(not DASHBOARD_HTML.exists(), reason="dashboard.html not found")
def test_html_has_download_link():
    html = DASHBOARD_HTML.read_text()
    assert 'id="download-link"' in html


@pytest.mark.skipif(not DASHBOARD_HTML.exists(), reason="dashboard.html not found")
def test_html_has_header_download_link():
    html = DASHBOARD_HTML.read_text()
    assert 'id="header-download-link"' in html


@pytest.mark.skipif(not DASHBOARD_HTML.exists(), reason="dashboard.html not found")
def test_html_uses_atob():
    html = DASHBOARD_HTML.read_text()
    assert "atob(content)" in html


@pytest.mark.skipif(not DASHBOARD_HTML.exists(), reason="dashboard.html not found")
def test_html_checks_binary_type():
    html = DASHBOARD_HTML.read_text()
    assert "type === 'binary'" in html
