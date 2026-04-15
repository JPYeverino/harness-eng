"""
Smoke tests for dashboard.html run-level result hero.

Tests must FAIL before dashboard.html is updated.
They verify that:
- id="run-summary" exists in the HTML
- /api/run appears in the JS
- id="run-approve-btn" exists
- id="run-reject-btn" exists
"""
from pathlib import Path

HTML = (Path(__file__).parent.parent / "dashboard.html").read_text()


def test_run_summary_id_exists():
    assert 'id="run-summary"' in HTML


def test_api_run_referenced_in_js():
    assert "/api/run" in HTML


def test_run_approve_btn_id_exists():
    assert 'id="run-approve-btn"' in HTML


def test_run_reject_btn_id_exists():
    assert 'id="run-reject-btn"' in HTML
