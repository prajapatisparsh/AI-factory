"""
FastAPI server — AI Factory pipeline bridge.

Exposes the existing Python agent pipeline over HTTP/SSE so the
Next.js frontend can call real agents instead of using mock data.

Endpoints:
  POST /api/pipeline/start          → { run_id, mode }
  GET  /api/pipeline/stream/{run_id} → SSE stream of pipeline events
  POST /api/pipeline/{run_id}/resume → resume a guided-mode pause
  GET  /api/health                   → { status: "ok" }
"""

from __future__ import annotations

import json
import logging
import os
import queue
import sys
import threading
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, Generator, Optional

# ---------------------------------------------------------------------------
# Path setup — ensure project root is importable
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# ---------------------------------------------------------------------------
# FastAPI imports
# ---------------------------------------------------------------------------

from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Project imports (agents, utils, schemas)
# ---------------------------------------------------------------------------

from src.agents import VisionAgent, PMAgent, TechLeadAgent, DevTeamAgent, QAAgent, CoachAgent, AgentError
from src.agents.cost_estimator import estimate_project_costs, generate_executive_summary
from src.utils.files import get_playbook_rules, generate_master_prompt, save_all_project_files, ensure_directories
from src.discussion.orchestrator import DiscussionOrchestrator
from src.discussion.memory import SharedMemory
from src.schemas import DocumentAnalysis, UserStory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("api.server")

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="AI Factory API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_directories()

# ---------------------------------------------------------------------------
# In-memory run registry
# { run_id: { "queue": Queue, "resume_event": Event, "thread": Thread } }
# ---------------------------------------------------------------------------

_runs: Dict[str, Dict[str, Any]] = {}
_runs_lock = threading.Lock()  # guards all _runs mutations
# Persists output folder path after run is cleaned up (needed for download endpoint)
_output_folders: Dict[str, str] = {}

MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Pipeline runner (runs in a separate thread)
# ---------------------------------------------------------------------------

def _run_pipeline(
    run_id: str,
    text: str,
    mode: str,
    eq: queue.Queue,
    resume_event: threading.Event,
) -> None:
    """Full 8-phase pipeline. Emits JSON events to *eq*. Sentinel None = done."""

    def emit(event_type: str, **kwargs: Any) -> None:
        eq.put({"type": event_type, **kwargs})

    def maybe_pause(phase: int) -> None:
        """In guided mode, signal a pause and block until the client resumes."""
        if mode == "guided":
            emit("pause", phase=phase)
            resume_event.wait()   # Block thread until /resume is called
            resume_event.clear()

    try:
        logger.info(f"[{run_id}] Pipeline starting (mode={mode})")

        # ── PHASE 1 — Document parsing ─────────────────────────────────────
        emit("phase_start", phase=1, message="VisionAgent: Reading document structure…", agent="VisionAgent")
        vision = VisionAgent()
        context: DocumentAnalysis = vision.parse_text_input(text)
        emit("phase_complete", phase=1, data=context.model_dump())
        emit("log", phase=1, message=f"Extracted {len(context.features)} features, {len(context.personas)} personas, {len(context.ambiguities)} ambiguities", agent="VisionAgent")

        # ── PHASE 2 — User Stories + Architecture ──────────────────────────
        emit("phase_start", phase=2, message="PMAgent: Generating user stories…", agent="PMAgent")
        pm_agent = PMAgent()
        user_stories: list[UserStory] = pm_agent.generate_user_stories(context)
        emit("log", phase=2, message=f"Generated {len(user_stories)} user stories", agent="PMAgent")

        emit("log", phase=2, message="TechLeadAgent: Designing system architecture…", agent="TechLeadAgent")
        tech_lead = TechLeadAgent()
        architecture: str = tech_lead.generate_architecture(context, user_stories)
        emit("log", phase=2, message="Architecture designed", agent="TechLeadAgent")

        # Team discussion
        try:
            project_id = run_id[:20]
            orchestrator = DiscussionOrchestrator(
                agents={"PMAgent": pm_agent, "TechLeadAgent": tech_lead},
                memory=SharedMemory(project_id=project_id),
            )
            for topic_id in ("USER_STORIES_REVIEW", "ARCHITECTURE_REVIEW"):
                disc = orchestrator.run_discussion(orchestrator.start_discussion(topic_id))
                emit("log", phase=2, message=f"Discussion '{disc.topic_name}': {disc.status.value}", agent="Team")
                if disc.decision:
                    emit("discussion", phase=2, topic=disc.topic_name, consensus=disc.decision[:500])
        except Exception as disc_err:
            logger.warning(f"[{run_id}] Phase-2 discussion skipped: {disc_err}")

        emit("phase_complete", phase=2, data={
            "user_stories": [s.model_dump() for s in user_stories],
            "architecture": architecture,
        })

        maybe_pause(2)

        # ── PHASE 3 — Clarifications ───────────────────────────────────────
        emit("phase_start", phase=3, message="DevTeamAgent: Generating clarification questions…", agent="DevTeamAgent")
        dev_team = DevTeamAgent()
        clarifications = dev_team.generate_clarification_questions(context, user_stories, architecture)
        answers: dict = {}  # always defined; populated below if clarifications exist
        if clarifications:
            answers = pm_agent.answer_clarifications(clarifications, context, user_stories)
            emit("log", phase=3, message=f"Resolved {len(answers)} clarifications", agent="PMAgent")
            clarification_list = [
                {
                    "id": q.id,
                    "question": q.question,
                    "context": q.context,
                    "source_agent": q.source_agent,
                    "answer": answers.get(q.id, ""),
                }
                for q in clarifications
            ]
        else:
            emit("log", phase=3, message="No clarifications needed", agent="PMAgent")
            clarification_list = []
        emit("phase_complete", phase=3, data={"clarifications": clarification_list})

        # ── Pre-create agents reused across all retry cycles ───────────────
        qa_agent = QAAgent()
        user_stories_dicts = [s.model_dump() for s in user_stories]

        # ── RETRY LOOP (Phases 4-7) ─────────────────────────────────────────
        retry_attempt = 0
        feedback = ""
        backend_final: Optional[str] = None
        frontend_final: Optional[str] = None
        evaluation = None  # initialised here; assigned inside Phase 7

        while retry_attempt < MAX_RETRIES:
            if retry_attempt > 0:
                emit("retry", phase=4, cycle=retry_attempt, feedback=feedback[:1000])

            # ── PHASE 4 — Draft Specs ───────────────────────────────────────
            emit("phase_start", phase=4, message="DevTeamAgent: Drafting backend specification…", agent="DevTeamAgent")
            backend_draft: str = dev_team.generate_backend_draft(context, user_stories, architecture, answers, feedback)
            emit("log", phase=4, message=f"Backend spec drafted ({len(backend_draft):,} chars)", agent="DevTeamAgent")

            frontend_draft: str = dev_team.generate_frontend_draft(context, user_stories, architecture, backend_draft, answers, feedback)
            emit("log", phase=4, message=f"Frontend spec drafted ({len(frontend_draft):,} chars)", agent="DevTeamAgent")
            emit("phase_complete", phase=4, data={
                "backend_spec": backend_draft,
                "frontend_spec": frontend_draft,
            })

            maybe_pause(4)

            # Apply any spec overrides the client submitted during the guided pause
            _override = _runs.get(run_id, {}).pop("spec_override", {})
            if _override.get("backend_spec"):
                backend_draft = _override["backend_spec"]
                emit("log", phase=4, message="Backend spec updated from guided edit", agent="System")
            if _override.get("frontend_spec"):
                frontend_draft = _override["frontend_spec"]
                emit("log", phase=4, message="Frontend spec updated from guided edit", agent="System")

            # ── PHASE 5 — QA Analysis ───────────────────────────────────────
            emit("phase_start", phase=5, message="QAAgent: Running quality analysis…", agent="QAAgent")
            qa_report = qa_agent.analyze_specifications(backend_draft, frontend_draft, architecture, user_stories_dicts)
            total_issues = len(qa_report.critical) + len(qa_report.high) + len(qa_report.medium) + len(qa_report.low)
            emit("log", phase=5, message=f"QA complete: {len(qa_report.critical)} critical, {len(qa_report.high)} high, {len(qa_report.medium)} medium, {len(qa_report.low)} low", agent="QAAgent")

            # QA team discussion
            try:
                qa_orchestrator = DiscussionOrchestrator(
                    agents={"PMAgent": pm_agent, "TechLeadAgent": tech_lead, "DevTeamAgent": dev_team, "QAAgent": qa_agent},
                    memory=SharedMemory(project_id=run_id[:20]),
                )
                spec_review = qa_orchestrator.run_discussion(qa_orchestrator.start_discussion("SPEC_REVIEW"))
                emit("log", phase=5, message=f"Spec review: {spec_review.status.value}", agent="Team")
                if spec_review.decision:
                    emit("discussion", phase=5, topic=spec_review.topic_name, consensus=spec_review.decision[:500])
            except Exception as disc_err:
                logger.warning(f"[{run_id}] Phase-5 discussion skipped: {disc_err}")

            emit("phase_complete", phase=5, data={
                "qa_report": qa_report.model_dump(),
                "total_issues": total_issues,
            })

            maybe_pause(5)

            # ── PHASE 6 — Fix Issues ────────────────────────────────────────
            emit("phase_start", phase=6, message="DevTeamAgent: Applying QA fixes…", agent="DevTeamAgent")
            if total_issues > 0:
                backend_final = dev_team.fix_backend_spec(backend_draft, qa_report)
                frontend_final = dev_team.fix_frontend_spec(frontend_draft, qa_report)
                emit("log", phase=6, message=f"Fixed {total_issues} QA issues", agent="DevTeamAgent")
            else:
                backend_final = backend_draft
                frontend_final = frontend_draft
                emit("log", phase=6, message="No issues to fix", agent="DevTeamAgent")
            emit("phase_complete", phase=6, data={
                "backend_spec": backend_final,
                "frontend_spec": frontend_final,
            })

            maybe_pause(6)

            # Apply any spec overrides the client submitted during the guided pause
            _override6 = _runs.get(run_id, {}).pop("spec_override", {})
            if _override6.get("backend_spec"):
                backend_final = _override6["backend_spec"]
                emit("log", phase=6, message="Backend spec updated from guided edit", agent="System")
            if _override6.get("frontend_spec"):
                frontend_final = _override6["frontend_spec"]
                emit("log", phase=6, message="Frontend spec updated from guided edit", agent="System")

            # ── PHASE 7 — PM Evaluation ─────────────────────────────────────
            emit("phase_start", phase=7, message="PMAgent: Evaluating final specifications…", agent="PMAgent")
            qa_summary = (
                f"Critical: {len(qa_report.critical)}, High: {len(qa_report.high)}, "
                f"Medium: {len(qa_report.medium)}, Low: {len(qa_report.low)}, "
                f"Security: {len(qa_report.security_flags)}"
            )
            evaluation = pm_agent.evaluate_specifications(
                context, user_stories, architecture, backend_final, frontend_final, qa_summary
            )
            emit("phase_complete", phase=7, data={
                "pm_evaluation": evaluation.model_dump(),
                "score": evaluation.score,
                "status": evaluation.status.value,
            })
            emit("log", phase=7, message=f"PM score: {evaluation.score}/100 — {evaluation.status.value}", agent="PMAgent")

            if evaluation.score < 85:
                retry_attempt += 1

                # Coach learns from rejection
                try:
                    coach = CoachAgent()
                    lessons = coach.process_rejection(evaluation)
                    if lessons:
                        emit("coach", phase=7, message=f"Coach extracted {len(lessons)} lesson(s) and updated playbooks", rules_count=len(lessons))
                except Exception as coach_err:
                    logger.warning(f"[{run_id}] Coach agent failed: {coach_err}")

                if retry_attempt >= MAX_RETRIES:
                    emit("error", phase=7, message=f"REJECTED after {MAX_RETRIES} attempts. Score: {evaluation.score}/100. Issues: {evaluation.issues}")
                    break

                feedback = (
                    f"REJECTED (Score {evaluation.score}/100)\n"
                    f"Issues: {chr(10).join(f'- {i}' for i in evaluation.issues)}\n"
                    f"PM Feedback: {evaluation.scolding}"
                )
                emit("log", phase=7, message=f"Score {evaluation.score}/100 — Retry {retry_attempt}/{MAX_RETRIES - 1}", agent="PMAgent")
                continue  # retry phases 4-7

            else:
                emit("log", phase=7, message=f"APPROVED! Score {evaluation.score}/100", agent="PMAgent")
                break  # exit retry loop — proceed to Phase 8

        # ── PHASE 8 — Save Outputs ──────────────────────────────────────────
        if backend_final is None or frontend_final is None:
            emit("error", phase=8, message="Pipeline ended before generating final specs. Cannot save.")
            return

        emit("phase_start", phase=8, message="System: Generating output files…", agent="System")

        pm_formatter = PMAgent()
        qa_formatter = QAAgent()
        user_stories_md = pm_formatter.format_user_stories_markdown(user_stories)
        qa_report_md = qa_formatter.format_qa_report_markdown(qa_report)

        playbook_rules = {
            "pm":        get_playbook_rules("pm"),
            "tech_lead": get_playbook_rules("tech_lead"),
            "backend":   get_playbook_rules("backend"),
            "frontend":  get_playbook_rules("frontend"),
            "qa":        get_playbook_rules("qa"),
        }
        master_prompt = generate_master_prompt(context, user_stories, architecture, backend_final, frontend_final, qa_report_md, playbook_rules)

        cost_estimation = estimate_project_costs(context, user_stories, architecture)
        executive_summary = generate_executive_summary(context, user_stories, architecture, cost_estimation)

        output_folder = save_all_project_files(
            user_stories=user_stories_md,
            architecture=architecture,
            backend_final=backend_final,
            frontend_final=frontend_final,
            qa_report=qa_report_md,
            master_prompt=master_prompt,
            cost_estimation=cost_estimation,
            executive_summary=executive_summary,
        )

        # Build file list for the frontend
        # Persist output_folder so the download endpoint can serve it after run cleanup
        _output_folders[run_id] = str(output_folder)

        output_files = []
        for fname, desc in [
            ("00_EXECUTIVE_SUMMARY.md",  "Stakeholder-facing summary — features, timeline, budget"),
            ("01_MASTER_PROMPT.md",       "Implementation guide + active playbook rules"),
            ("02_User_Stories.md",        "User stories with acceptance criteria"),
            ("03_Architecture.md",        "System architecture and tech stack"),
            ("04_Backend_Final.md",       "Backend implementation specification"),
            ("05_Frontend_Final.md",      "Frontend implementation specification"),
            ("06_QA_Report.md",           "Quality assurance findings and security flags"),
            ("08_Cost_Estimation.md",     "Cost and timeline estimates"),
        ]:
            full_path = Path(output_folder) / fname
            output_files.append({
                "name": fname.replace("_", " ").replace(".md", ""),
                "filename": fname,
                "description": desc,
                "exists": full_path.exists(),
            })

        emit("phase_complete", phase=8, data={"output_files": output_files, "output_folder": str(output_folder)})
        emit("complete", data={
            "output_folder": str(output_folder),
            "output_files": output_files,
            "score": evaluation.score if evaluation else 0,
            "user_stories_count": len(user_stories),
            "retry_count": retry_attempt,
        })

        logger.info(f"[{run_id}] Pipeline complete → {output_folder}")

    except AgentError as ae:
        logger.error(f"[{run_id}] AgentError: {ae}")
        emit("error", message=str(ae))
    except Exception as exc:
        logger.error(f"[{run_id}] Unhandled exception: {exc}\n{traceback.format_exc()}")
        emit("error", message=str(exc), traceback=traceback.format_exc())
    finally:
        eq.put(None)  # Sentinel — tells SSE generator to close


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class StartRequest(BaseModel):
    text: str = Field(..., max_length=500_000, description="Raw requirements text (max 500 KB)")
    mode: str = "auto"


class StartResponse(BaseModel):
    run_id: str
    mode: str


class ResumeRequest(BaseModel):
    """Optional body for /resume — carries spec overrides from guided-mode edits."""
    spec_override: Dict[str, str] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "runs_active": len(_runs)}


@app.post("/api/pipeline/start", response_model=StartResponse)
async def start_pipeline(body: StartRequest) -> StartResponse:
    """Start a new pipeline run with plain-text requirements."""
    if not body.text.strip():
        raise HTTPException(400, "text must not be empty")

    run_id = uuid.uuid4().hex[:12]
    eq: queue.Queue = queue.Queue()
    resume_event = threading.Event()

    with _runs_lock:
        _runs[run_id] = {"queue": eq, "resume_event": resume_event}

    thread = threading.Thread(
        target=_run_pipeline,
        args=(run_id, body.text, body.mode, eq, resume_event),
        daemon=True,
        name=f"pipeline-{run_id}",
    )
    with _runs_lock:
        _runs[run_id]["thread"] = thread
    thread.start()

    # Safety cleanup: remove leaked run entry if client never connects to SSE
    def _ttl_cleanup():
        with _runs_lock:
            entry = _runs.get(run_id)
        if entry and not entry.get("_sse_connected"):
            with _runs_lock:
                _runs.pop(run_id, None)
            logger.warning(f"[{run_id}] TTL cleanup: no SSE consumer connected within 5 minutes")
    threading.Timer(300, _ttl_cleanup).start()

    logger.info(f"Started run {run_id} (mode={body.mode})")
    return StartResponse(run_id=run_id, mode=body.mode)


@app.post("/api/pipeline/start-file", response_model=StartResponse)
async def start_pipeline_file(
    file: UploadFile = File(...),
    mode: str = Form("auto"),
) -> StartResponse:
    """Start a new pipeline run from an uploaded file (reads as UTF-8 text)."""
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    if not text.strip():
        raise HTTPException(400, "Uploaded file is empty")

    run_id = uuid.uuid4().hex[:12]
    eq: queue.Queue = queue.Queue()
    resume_event = threading.Event()

    _runs[run_id] = {"queue": eq, "resume_event": resume_event}

    thread = threading.Thread(
        target=_run_pipeline,
        args=(run_id, text, mode, eq, resume_event),
        daemon=True,
        name=f"pipeline-{run_id}",
    )
    _runs[run_id]["thread"] = thread
    thread.start()

    logger.info(f"Started file-based run {run_id} (mode={mode}, file={file.filename})")
    return StartResponse(run_id=run_id, mode=mode)


def _sse_generator(run_id: str) -> Generator[str, None, None]:
    """Yield SSE-formatted lines from the run's event queue."""
    with _runs_lock:
        run = _runs.get(run_id)
        if run is None:
            yield f"data: {json.dumps({'type': 'error', 'message': 'run not found'})}\n\n"
            return
        # Mark SSE consumer connected so TTL cleanup won't fire
        run["_sse_connected"] = True

    eq: queue.Queue = run["queue"]

    while True:
        try:
            event = eq.get(timeout=60)  # 60 s max wait between events
        except queue.Empty:
            # Keep-alive ping so the connection does not time out
            yield ": ping\n\n"
            continue

        if event is None:
            # Sentinel — pipeline finished (success or unhandled error)
            yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"
            # Clean up the run registry after a short delay so the client
            # can still call /resume if it arrived late
            with _runs_lock:
                _runs.pop(run_id, None)
            break

        yield f"data: {json.dumps(event)}\n\n"


@app.get("/api/pipeline/stream/{run_id}")
async def stream_pipeline(run_id: str) -> StreamingResponse:
    """SSE endpoint — streams pipeline events to the frontend."""
    if run_id not in _runs:
        raise HTTPException(404, f"run '{run_id}' not found")

    return StreamingResponse(
        _sse_generator(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/pipeline/{run_id}/resume")
async def resume_pipeline(run_id: str, body: ResumeRequest = ResumeRequest()) -> dict:
    """Signal a guided-mode pause to continue. Optionally pass edited spec overrides."""
    run = _runs.get(run_id)
    if run is None:
        raise HTTPException(404, f"run '{run_id}' not found")
    if body.spec_override:
        run["spec_override"] = body.spec_override
    resume_event: threading.Event = run["resume_event"]
    resume_event.set()
    return {"status": "resumed", "run_id": run_id}


@app.get("/api/pipeline/{run_id}/download")
async def download_outputs(run_id: str) -> StreamingResponse:
    """Download all generated markdown files for a run as a ZIP archive."""
    import io
    import zipfile

    folder_str = _output_folders.get(run_id)
    if not folder_str:
        raise HTTPException(404, f"Outputs not yet available for run '{run_id}'")

    folder_path = Path(folder_str)
    if not folder_path.exists():
        raise HTTPException(404, "Output folder not found on server")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(folder_path.glob("*.md")):
            zf.write(file_path, file_path.name)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{folder_path.name}.zip"'},
    )


@app.delete("/api/pipeline/{run_id}")
async def cancel_pipeline(run_id: str) -> dict:
    """Cancel a running pipeline (best-effort: unblocks guided pause and removes from registry)."""
    run = _runs.pop(run_id, None)
    if run is None:
        raise HTTPException(404, f"run '{run_id}' not found")
    # Unblock any waiting pause so the thread can exit
    run["resume_event"].set()
    return {"status": "cancelled", "run_id": run_id}
