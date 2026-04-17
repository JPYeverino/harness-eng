"""Smoke tests for memory/planner_observations.json — written by the planner boyscout pass."""
import json
from pathlib import Path


OBS_FILE = Path("memory/planner_observations.json")


def test_file_exists():
    assert OBS_FILE.exists(), "memory/planner_observations.json not found — planner boyscout pass has not run"


def test_top_level_files_key():
    data = json.loads(OBS_FILE.read_text())
    assert "files" in data, f"Expected top-level key 'files', got: {list(data.keys())}"


def test_each_value_is_list():
    data = json.loads(OBS_FILE.read_text())
    for fname, observations in data["files"].items():
        assert isinstance(observations, list), (
            f"Expected list for '{fname}', got {type(observations).__name__}"
        )
