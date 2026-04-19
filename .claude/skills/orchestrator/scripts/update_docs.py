"""
Post-run docs updater. Runs after all tasks are approved.
Finds every impl_file from completed task decisions and removes its
stale docs/diagrams/ entry so the boyscout regenerates it on the next run.
Usage: python update_docs.py
Exits 0 always (non-blocking).
"""
import json
from pathlib import Path


def _impl_files_from_decisions() -> list[str]:
    files = []
    for decisions_file in sorted(Path("memory").glob("*_decisions.json")):
        try:
            entries = json.loads(decisions_file.read_text())
            for entry in entries if isinstance(entries, list) else [entries]:
                impl = entry.get("impl_file")
                if impl:
                    files.append(impl)
        except (json.JSONDecodeError, KeyError):
            continue
    return files


def _diagram_path(impl_file: str) -> Path:
    name = Path(impl_file).name.replace("/", "_")
    return Path("docs/diagrams") / f"{name}.md"


def main() -> None:
    impl_files = _impl_files_from_decisions()
    if not impl_files:
        print("update_docs: no completed tasks found, nothing to update")
        return

    staled = []
    for impl_file in impl_files:
        diagram = _diagram_path(impl_file)
        if diagram.exists():
            diagram.unlink()
            staled.append(str(diagram))

    if staled:
        print(f"update_docs: marked {len(staled)} diagram(s) stale for regeneration on next run:")
        for s in staled:
            print(f"  - {s}")
    else:
        print("update_docs: no existing diagrams needed updating")


if __name__ == "__main__":
    main()
