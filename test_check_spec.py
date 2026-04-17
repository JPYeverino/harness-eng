"""Tests for check_spec.py — runs the script as a subprocess in a tmp directory."""
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).parent / "check_spec.py"


def run(spec_content: str | None, tmp_path: Path) -> subprocess.CompletedProcess:
    if spec_content is not None:
        (tmp_path / "spec.md").write_text(spec_content)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


VALID_SPEC = """\
## Stack

- language: Python
- test_runner: pytest
- test_command: pytest -v

## Deliverables

- `check_spec.py`
- `README.md`

## Scope

- check_spec.py: exits 1 when spec is invalid
"""


def test_exits_1_when_spec_missing(tmp_path):
    result = run(None, tmp_path)
    assert result.returncode == 1
    assert "spec.md" in result.stdout.lower() or "spec.md" in result.stderr.lower()


def test_exits_1_when_stack_missing(tmp_path):
    spec = """\
## Deliverables

- `check_spec.py`

## Scope

- smoke test
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "Stack" in result.stdout


def test_exits_1_when_language_missing(tmp_path):
    spec = """\
## Stack

- test_runner: pytest
- test_command: pytest -v

## Deliverables

- `check_spec.py`

## Scope

- smoke test
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "language" in result.stdout


def test_exits_1_when_test_runner_missing(tmp_path):
    spec = """\
## Stack

- language: Python
- test_command: pytest -v

## Deliverables

- `check_spec.py`

## Scope

- smoke test
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "test_runner" in result.stdout


def test_exits_1_when_test_command_missing(tmp_path):
    spec = """\
## Stack

- language: Python
- test_runner: pytest

## Deliverables

- `check_spec.py`

## Scope

- smoke test
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "test_command" in result.stdout


def test_exits_1_when_deliverables_missing(tmp_path):
    spec = """\
## Stack

- language: Python
- test_runner: pytest
- test_command: pytest -v

## Scope

- smoke test
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "Deliverables" in result.stdout


def test_exits_1_when_deliverables_empty(tmp_path):
    spec = """\
## Stack

- language: Python
- test_runner: pytest
- test_command: pytest -v

## Deliverables

## Scope

- smoke test
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "Deliverables" in result.stdout


def test_exits_1_when_scope_missing(tmp_path):
    spec = """\
## Stack

- language: Python
- test_runner: pytest
- test_command: pytest -v

## Deliverables

- `check_spec.py`
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "Scope" in result.stdout


def test_exits_1_when_binary_deliverable_uncovered(tmp_path):
    spec = """\
## Stack

- language: Python
- test_runner: pytest
- test_command: pytest -v

## Deliverables

- `slides.pptx`

## Scope

- check_spec.py is covered
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "slides.pptx" in result.stdout


def test_exits_0_when_valid_spec(tmp_path):
    result = run(VALID_SPEC, tmp_path)
    assert result.returncode == 0


def test_exits_0_when_all_text_extensions_no_scope_needed(tmp_path):
    spec = """\
## Stack

- language: Python
- test_runner: pytest
- test_command: pytest -v

## Deliverables

- `app.py`
- `README.md`
- `config.json`
- `styles.html`

## Scope

- something unrelated
"""
    result = run(spec, tmp_path)
    assert result.returncode == 0


def test_exits_0_when_binary_deliverable_covered_in_scope(tmp_path):
    spec = """\
## Stack

- language: Python
- test_runner: pytest
- test_command: pytest -v

## Deliverables

- `slides.pptx`

## Scope

- slides.pptx: out of scope for unit tests
"""
    result = run(spec, tmp_path)
    assert result.returncode == 0


def test_output_format_on_failure(tmp_path):
    spec = """\
## Stack

- language: Python
- test_runner: pytest

## Deliverables

- `slides.pptx`

## Scope

- nothing about pptx
"""
    result = run(spec, tmp_path)
    assert result.returncode == 1
    assert "SPEC INVALID" in result.stdout
    assert "issue(s) found" in result.stdout
    assert "[1]" in result.stdout
