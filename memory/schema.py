from dataclasses import dataclass


@dataclass
class Task:
    id: str
    title: str
    description: str


@dataclass
class ContextDoc:
    task_id: str
    what: str        # what needs to be built
    approach: str    # brute force / junior / senior — and why
    notes: str       # anything else the next agent should know


@dataclass
class TDDResult:
    task_id: str
    success: bool
    test_file: str
    impl_file: str
    decisions: list[str]
