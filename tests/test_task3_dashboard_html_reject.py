"""
Smoke tests for task-3: dashboard.html reject button.
Read the file as text and assert the required elements exist.
These must fail before dashboard.html is updated.
"""
from pathlib import Path

HTML_PATH = Path("dashboard.html")


def _html() -> str:
    return HTML_PATH.read_text()


def test_reject_btn_id_exists():
    assert 'id="run-reject-btn"' in _html(), (
        'dashboard.html must contain id="run-reject-btn"'
    )


def test_reject_api_endpoint_in_js():
    assert "/api/reject/" in _html(), (
        "dashboard.html JS must POST to /api/reject/{task_id}"
    )
