"""
Harness Dashboard — FastAPI backend.

Usage:
    uvicorn dashboard:app --reload

Or create a custom root:
    from dashboard import create_app
    app = create_app(root="/path/to/project")
"""
import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse

TEXT_EXTENSIONS = {'.md', '.txt', '.html', '.htm', '.csv', '.json', '.yaml', '.yml', '.toml', '.rst'}


def create_app(root: str = ".") -> FastAPI:
    app = FastAPI(title="Harness Dashboard")
    root_path = Path(root)

    def _read_json(path: Path) -> Any:
        if not path.exists():
            return None
        return json.loads(path.read_text())

    @app.get("/")
    def serve_dashboard():
        html_file = root_path / "dashboard.html"
        if not html_file.exists():
            raise HTTPException(status_code=404, detail="dashboard.html not found")
        return FileResponse(str(html_file), media_type="text/html")

    @app.get("/api/tasks")
    def get_tasks():
        data = _read_json(root_path / "tasks.json")
        if data is None:
            raise HTTPException(status_code=404, detail="tasks.json not found")
        return JSONResponse(data)

    @app.get("/api/memory/{task_id}")
    def get_memory(task_id: str):
        memory_dir = root_path / "memory"
        slots = {
            "context": _read_json(memory_dir / f"{task_id}_context.json"),
            "decisions": _read_json(memory_dir / f"{task_id}_decisions.json"),
            "validation": _read_json(memory_dir / f"{task_id}_validation.json"),
        }
        result = {k: v for k, v in slots.items() if v is not None}
        if not result:
            raise HTTPException(status_code=404, detail=f"No memory found for {task_id}")
        return JSONResponse(result)

    @app.get("/api/logs")
    def get_logs():
        log_file = root_path / "memory" / "run_log.jsonl"
        if not log_file.exists():
            return JSONResponse([])
        entries = []
        for line in log_file.read_text().splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
        return JSONResponse(entries)

    @app.get("/api/deliverable/{task_id}")
    def get_deliverable(task_id: str):
        decisions = _read_json(root_path / "memory" / f"{task_id}_decisions.json")
        if not decisions or not decisions.get("entries"):
            raise HTTPException(status_code=404, detail="No decisions file")
        impl_file = decisions["entries"][0].get("impl_file")
        if not impl_file:
            raise HTTPException(status_code=404, detail="No impl_file recorded")
        path = root_path / impl_file
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"{impl_file} not found")
        suffix = Path(impl_file).suffix.lower()
        mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if suffix in TEXT_EXTENSIONS:
            return JSONResponse({
                "filename": impl_file,
                "type": "text",
                "content": path.read_text(),
                "mime_type": mime_type,
            })
        else:
            return JSONResponse({
                "filename": impl_file,
                "type": "binary",
                "content": base64.b64encode(path.read_bytes()).decode("ascii"),
                "mime_type": mime_type,
            })

    @app.get("/api/run")
    def get_run():
        data = _read_json(root_path / "tasks.json")
        if data is None or not data.get("tasks"):
            raise HTTPException(status_code=404, detail="No tasks found")

        tasks = data["tasks"]
        task_ids = [t["id"] for t in tasks]
        summaries = []
        total_checks = 0
        checks_passed = 0
        awaiting_approval = False
        all_approved = True
        any_rejected = False

        for task in tasks:
            task_id = task["id"]
            validation = _read_json(root_path / "memory" / f"{task_id}_validation.json")

            # Check if tdd gate is stamped for this task
            subtasks = task.get("subtasks", [])
            gate_tdd_done = any(
                g.get("gate_tdd_done")
                for sub in subtasks
                for g in [sub.get("gates", {})]
            )

            if validation:
                summary = validation.get("summary", "")
                if summary:
                    summaries.append(summary)

                checks = validation.get("checks", {})
                total_checks += len(checks)
                checks_passed += sum(1 for c in checks.values() if c.get("passed"))

                human_approved = bool(validation.get("human_approved"))
                human_rejected = bool(validation.get("human_rejected"))

                if not human_approved:
                    all_approved = False
                if human_rejected:
                    any_rejected = True
                if gate_tdd_done and not human_approved and not human_rejected:
                    awaiting_approval = True
            else:
                all_approved = False
                if gate_tdd_done:
                    awaiting_approval = True

        return JSONResponse({
            "task_ids": task_ids,
            "summaries": summaries,
            "total_checks": total_checks,
            "checks_passed": checks_passed,
            "awaiting_approval": awaiting_approval,
            "all_approved": all_approved,
            "any_rejected": any_rejected,
        })

    @app.get("/api/tasks/{task_id}/approval")
    def get_approval(task_id: str):
        validation_file = root_path / "memory" / f"{task_id}_validation.json"
        data = _read_json(validation_file)
        if data is None:
            return JSONResponse({"human_approved": False})
        return JSONResponse({"human_approved": bool(data.get("human_approved", False))})

    @app.post("/api/approve/{task_id}")
    def approve(task_id: str):
        validation_file = root_path / "memory" / f"{task_id}_validation.json"
        data = _read_json(validation_file)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No validation file for {task_id}")
        data["human_approved"] = True
        validation_file.write_text(json.dumps(data, indent=2))

        waiting_file = root_path / "memory" / "waiting_for_human.json"
        if waiting_file.exists():
            waiting = json.loads(waiting_file.read_text())
            waiting_ids = set(waiting.get("task_ids", []))
            all_resolved = all(
                (d := _read_json(root_path / "memory" / f"{tid}_validation.json")) is not None
                and (d.get("human_approved") or d.get("human_rejected"))
                for tid in waiting_ids
            )
            if all_resolved:
                waiting_file.unlink()

        return JSONResponse({"human_approved": True})

    @app.post("/api/reject/{task_id}")
    def reject(task_id: str):
        validation_file = root_path / "memory" / f"{task_id}_validation.json"
        data = _read_json(validation_file)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No validation file for {task_id}")
        data["human_rejected"] = True
        validation_file.write_text(json.dumps(data, indent=2))
        # Do NOT delete the sentinel — Stop hook needs to detect rejection and run cleanup
        return JSONResponse({"human_rejected": True})

    return app


# Default app instance for `uvicorn dashboard:app`
app = create_app()
