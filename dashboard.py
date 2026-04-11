"""
Harness Dashboard — FastAPI backend.

Usage:
    uvicorn dashboard:app --reload

Or create a custom root:
    from dashboard import create_app
    app = create_app(root="/path/to/project")
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse


async def tasks_sse_stream(tasks_file: Path) -> AsyncGenerator[str, None]:
    """Async generator that emits an SSE event whenever tasks.json changes."""
    last_mtime: float = 0.0
    while True:
        try:
            mtime = tasks_file.stat().st_mtime if tasks_file.exists() else 0.0
            if mtime != last_mtime:
                last_mtime = mtime
                data = tasks_file.read_text() if tasks_file.exists() else "{}"
                yield f"data: {data}\n\n"
        except Exception:
            pass
        await asyncio.sleep(1)


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

    @app.get("/api/events")
    async def sse_events():
        return StreamingResponse(
            tasks_sse_stream(root_path / "tasks.json"),
            media_type="text/event-stream",
        )

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

        sentinel = root_path / "memory" / "waiting_for_human.json"
        if sentinel.exists():
            sentinel.unlink()

        return JSONResponse({"human_approved": True})

    return app


# Default app instance for `uvicorn dashboard:app`
app = create_app()
