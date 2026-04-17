"""Validates spec.md structure before the planner runs. Exits 0 if valid, 1 with findings on failure."""
import sys
from pathlib import Path

TEXT_EXTENSIONS = {'.md', '.py', '.txt', '.html', '.htm', '.json',
                   '.yaml', '.yml', '.toml', '.rst', '.csv'}

REQUIRED_STACK_FIELDS = ['language', 'test_runner', 'test_command']


def _parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    lines_buf: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith('## '):
            if current is not None:
                sections[current] = ''.join(lines_buf)
            current = line[3:].strip()
            lines_buf = []
        else:
            if current is not None:
                lines_buf.append(line)
    if current is not None:
        sections[current] = ''.join(lines_buf)
    return sections


def _parse_stack_fields(section_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in section_text.splitlines():
        stripped = line.strip().lstrip('- ').strip()
        if ':' in stripped:
            key, _, val = stripped.partition(':')
            fields[key.strip()] = val.strip()
    return fields


def _parse_deliverables(section_text: str) -> list[str]:
    files = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith('-'):
            item = stripped[1:].strip().split()[0].strip('`')
            if item:
                files.append(item)
    return files


def validate(spec_path: Path) -> list[str]:
    issues: list[str] = []

    if not spec_path.exists():
        issues.append("spec.md not found")
        return issues

    text = spec_path.read_text()
    sections = _parse_sections(text)

    if 'Stack' not in sections:
        issues.append("Missing ## Stack section")
    else:
        fields = _parse_stack_fields(sections['Stack'])
        for f in REQUIRED_STACK_FIELDS:
            if f not in fields or not fields[f]:
                issues.append(f"Missing required Stack field: {f}")

    if 'Deliverables' not in sections:
        issues.append("Missing ## Deliverables section")
    else:
        deliverables = _parse_deliverables(sections['Deliverables'])
        if not deliverables:
            issues.append("## Deliverables section is empty — no files listed")
        else:
            scope_text = sections.get('Scope', '')
            for fname in deliverables:
                ext = Path(fname).suffix.lower()
                if ext not in TEXT_EXTENSIONS:
                    if fname not in scope_text and ext not in scope_text:
                        issues.append(
                            f"Deliverable '{fname}' has no smoke test or out-of-scope note in ## Scope"
                        )

    if 'Scope' not in sections:
        issues.append("Missing ## Scope section")

    return issues


def main() -> None:
    issues = validate(Path("spec.md"))
    if issues:
        print(f"SPEC INVALID — {len(issues)} issue(s) found:")
        for i, issue in enumerate(issues, 1):
            print(f"  [{i}] {issue}")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
