"""
Human-facing tool to approve the boyscout review.
Usage:
  python approve_boyscout.py --proceed
  python approve_boyscout.py --scope "finding to add as task" --lore "finding to accept as debt"
  --scope and --lore are repeatable
"""
import argparse
import json
import sys
from pathlib import Path

def _append_lore(entries: list[str]) -> None:
    lore_file = Path("docs/lore.md")
    lore_file.parent.mkdir(exist_ok=True)
    existing = lore_file.read_text() if lore_file.exists() else ""
    additions = "\n".join(f"- {e}" for e in entries)
    lore_file.write_text(existing.rstrip() + "\n\n" + additions + "\n")


parser = argparse.ArgumentParser()
parser.add_argument("--proceed", action="store_true")
parser.add_argument("--scope", action="append", default=[], metavar="FINDING")
parser.add_argument("--lore", action="append", default=[], metavar="FINDING")
args = parser.parse_args()

review_file = Path("memory/boyscout_review.json")

if not review_file.exists():
    print("ERROR: memory/boyscout_review.json not found — run the boyscout skill first")
    sys.exit(1)

data = json.loads(review_file.read_text())

if data.get("status") == "approved":
    print("ERROR: boyscout review is already approved")
    sys.exit(1)

data["status"] = "approved"
data["scope_additions"] = args.scope
data["lore_additions"] = args.lore

review_file.write_text(json.dumps(data, indent=2))

print("Approved: memory/boyscout_review.json")
if args.scope:
    print(f"  Scope additions ({len(args.scope)}): planner will include these as tasks")
    for s in args.scope:
        print(f"    + {s}")
if args.lore:
    print(f"  Lore additions ({len(args.lore)}): will be appended to docs/lore.md")
    for l in args.lore:
        print(f"    ~ {l}")
    _append_lore(args.lore)

print("Re-run the orchestrator to continue.")
