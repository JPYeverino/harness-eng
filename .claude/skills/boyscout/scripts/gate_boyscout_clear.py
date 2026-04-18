"""
Gate: checks that boyscout ran and human approved the review.
Usage: python gate_boyscout_clear.py
Exits 0 if clear to proceed, 1 if blocked.
"""
import json
import sys
from pathlib import Path

review_file = Path("memory/boyscout_review.json")

if not review_file.exists():
    print("BLOCKED: boyscout has not run yet — memory/boyscout_review.json not found")
    sys.exit(1)

try:
    data = json.loads(review_file.read_text())
except json.JSONDecodeError:
    print("BLOCKED: memory/boyscout_review.json is malformed")
    sys.exit(1)

required = {"status", "lore_checked", "files_scanned", "context_generated", "opportunities"}
missing = required - set(data.keys())
if missing:
    print(f"BLOCKED: boyscout_review.json is missing required keys: {', '.join(sorted(missing))}")
    print("  The boyscout output is incomplete — re-run the boyscout skill")
    sys.exit(1)

lore_exists = Path("docs/lore.md").exists()
if lore_exists and not data.get("lore_checked"):
    print("BLOCKED: docs/lore.md exists but boyscout_review.json has lore_checked: false")
    print("  The boyscout did not read lore — re-run the boyscout skill")
    sys.exit(1)

status = data.get("status")

if status == "proceed":
    print("OK: boyscout found nothing to review — proceeding")
    sys.exit(0)

if status == "approved":
    print("OK: boyscout review approved — proceeding")
    sys.exit(0)

if status == "needs_review":
    generated = data.get("context_generated", [])
    opportunities = data.get("opportunities", {})
    print("BLOCKED: boyscout review required.")
    if generated:
        print(f"  Context generated for: {', '.join(generated)}")
        print("  Review the generated docs in docs/diagrams/")
    if opportunities:
        print("  Opportunities found:")
        for fname, findings in opportunities.items():
            for f in findings:
                print(f"    {fname}: {f}")
    print("")
    print("  To approve and proceed:")
    print("    python approve_boyscout.py --proceed")
    print("  To add opportunities to scope or lore:")
    print('    python approve_boyscout.py --scope "finding" --lore "finding"')
    sys.exit(1)

print(f"BLOCKED: unknown status '{status}' in boyscout_review.json")
sys.exit(1)
