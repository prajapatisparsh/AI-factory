"""
AI Factory - Self-Evolving Multi-Agent MVP Generator
Streamlit Application Entry Point

This application transforms business requirements into complete MVP specifications
using collaborative AI agents with evolutionary memory.
"""

import streamlit as st
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.state import (
    init_session_state,
    get_workflow_state,
    update_workflow_state,
    set_phase,
    increment_retry,
    reset_retry_count,
    get_retry_count,
    log_message,
    get_logs,
    reset_session,
    set_processing,
    is_processing,
    set_error,
    get_error,
    clear_error,
    get_evolution_level,
    PHASE_NAMES
)

from src.utils.files import (
    get_playbook_rules,
    generate_master_prompt,
    save_all_project_files,
    ensure_directories
)

from src.agents import (
    VisionAgent,
    PMAgent,
    TechLeadAgent,
    DevTeamAgent,
    QAAgent,
    CoachAgent,
    AgentError
)

import logging
import traceback

from src.utils.checkpoint import CheckpointManager
from src.agents.cost_estimator import estimate_project_costs, generate_executive_summary
from src.schemas import DocumentAnalysis
from src.discussion.orchestrator import DiscussionOrchestrator
from src.discussion.memory import SharedMemory


# Page configuration
st.set_page_config(
    page_title="🧠 The AI Factory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .success-banner {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-banner {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-banner {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .phase-card {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with metrics and controls."""
    with st.sidebar:
        st.title("🧠 The AI Factory")
        st.caption("Self-Evolving MVP Generator")

        # ── Pipeline Mode Toggle ── prominent, top of sidebar ──────────────
        st.divider()
        st.radio(
            "⚙️ Pipeline Mode",
            options=["one_shot", "guided"],
            format_func=lambda x: "⚡ One Shot" if x == "one_shot" else "🧭 Guided",
            key="pipeline_mode",
            horizontal=True,
            help=(
                "⚡ **One Shot**: runs the full pipeline automatically.\n\n"
                "🧭 **Guided**: pauses after each phase so you can review "
                "and edit every output before the next phase runs."
            ),
        )
        st.divider()

        # Evolution Level
        evolution_level = get_evolution_level()
        st.metric("🧬 Evolution Level", f"{evolution_level} rules")
        
        # Current Phase
        state = get_workflow_state()
        phase_name = PHASE_NAMES.get(state.phase, "Unknown")
        st.metric("📍 Current Phase", f"{state.phase}/8: {phase_name}")
        
        # Progress bar
        progress = state.phase / 8
        st.progress(progress, text=f"{int(progress * 100)}% Complete")
        
        # Retry count (if any)
        if state.retry_count > 0:
            st.warning(f"⚠️ Retry Attempt: {state.retry_count}/3")
        
        st.divider()
        
        # Control buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset", use_container_width=True):
                reset_session()
                st.rerun()
        
        with col2:
            if st.button("📋 Logs", use_container_width=True):
                st.session_state['show_logs'] = not st.session_state.get('show_logs', False)

        # Show logs if toggled
        if st.session_state.get('show_logs', False):
            st.divider()
            st.subheader("📋 Activity Logs")
            logs = get_logs()
            
            if logs:
                log_container = st.container(height=300)
                with log_container:
                    for log in reversed(logs[-20:]):  # Last 20 logs
                        level_icon = {
                            "INFO": "ℹ️",
                            "WARNING": "⚠️",
                            "ERROR": "❌",
                            "DEBUG": "🔍"
                        }.get(log['level'], "📝")
                        st.text(f"{log['timestamp']} {level_icon} {log['message'][:50]}")
            else:
                st.info("No logs yet")
        
        st.divider()
        
        # Playbook stats
        with st.expander("📚 Playbook Stats"):
            coach = CoachAgent()
            stats = coach.get_playbook_stats()
            
            for name, data in stats.items():
                learned_badge = f" *(+{data['learned']} learned)*" if data['learned'] > 0 else ""
                st.markdown(f"**{name}:** {data['total']} rules{learned_badge}")
        
        # Run history
        with st.expander("📂 Previous Runs"):
            projects_dir = Path(__file__).parent / "projects"
            if projects_dir.exists():
                runs = sorted([d for d in projects_dir.iterdir() if d.is_dir()], reverse=True)
                if runs:
                    for run_dir in runs[:8]:
                        files_count = len(list(run_dir.glob("*.md")))
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.caption(f"{run_dir.name} ({files_count} files)")
                        with col_b:
                            if st.button("📂", key=f"open_{run_dir.name}", help="Open folder"):
                                if os.name == 'nt':
                                    os.startfile(str(run_dir))
                                else:
                                    import subprocess
                                    subprocess.Popen(['open', str(run_dir)])
                else:
                    st.caption("No previous runs yet.")
            else:
                st.caption("No previous runs yet.")


def render_file_upload():
    """Render the file upload section."""
    st.header("📄 Step 1: Upload Requirements Document")
    
    st.markdown("""
    Upload your business requirements document. Supported formats:
    - **PDF** - Best for formal documents
    - **Images** (PNG, JPG) - Screenshots, wireframes, diagrams
    - **Text** (TXT, MD) - Plain text requirements
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Drop your file here",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt', 'md'],
            help="Maximum file size: 10MB"
        )
        
        # C-4: Server-side validation — size and extension checks before accepting the file
        if uploaded_file:
            _MAX_BYTES = 10 * 1024 * 1024  # 10 MB
            _ALLOWED_EXT = {'pdf', 'png', 'jpg', 'jpeg', 'txt', 'md'}
            _ext = uploaded_file.name.rsplit('.', 1)[-1].lower() if '.' in uploaded_file.name else ''
            if uploaded_file.size > _MAX_BYTES:
                st.error(
                    f"❌ File exceeds the 10 MB limit "
                    f"({uploaded_file.size / 1024 / 1024:.1f} MB). Please compress or trim the document."
                )
                uploaded_file = None
            elif _ext not in _ALLOWED_EXT:
                st.error(
                    f"❌ File type '.{_ext}' is not allowed. "
                    f"Accepted formats: {', '.join(sorted(_ALLOWED_EXT))}"
                )
                uploaded_file = None

        if uploaded_file:
            st.success(f"✅ Uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

            # Store file in session
            st.session_state['uploaded_file'] = uploaded_file
            st.session_state['file_bytes'] = uploaded_file.read()
            st.session_state['file_name'] = uploaded_file.name
            uploaded_file.seek(0)  # Reset file pointer
    
    with col2:
        st.markdown("**Or enter text directly:**")
        text_input = st.text_area(
            "Requirements text",
            height=150,
            placeholder="Paste your requirements here...",
            label_visibility="collapsed"
        )
        
        if text_input and not uploaded_file:
            st.session_state['text_input'] = text_input
    
    # Process button
    has_input = (
        st.session_state.get('uploaded_file') or 
        st.session_state.get('text_input')
    )
    
    # Checkpoint resume detection — only shown when no new input provided
    if not has_input:
        _ckpt = CheckpointManager()
        _latest = _ckpt.get_latest_checkpoint()
        if _latest and 0 < _latest.phase < 8:
            st.info(
                f"💾 **Unfinished run found** — last saved at Phase {_latest.phase}: "
                f"*{PHASE_NAMES.get(_latest.phase, '?')}* ({_latest.timestamp[:16]})"
            )
            col_r, col_d = st.columns(2)
            with col_r:
                if st.button("▶️ Resume Pipeline", type="primary", use_container_width=True):
                    run_all_phases(resume_checkpoint=_latest)
            with col_d:
                if st.button("🗑️ Discard & Start Fresh", use_container_width=True):
                    _ckpt.clear_all_checkpoints()
                    st.rerun()
    
    if has_input:
        if st.button("🚀 Start Processing", type="primary", use_container_width=True):
            run_all_phases()


def render_guided_review():
    """Render the human-in-the-loop review UI when the pipeline is paused in Guided mode."""
    pause_key = st.session_state.get('guided_paused_at', '')
    data = st.session_state.get('guided_pipeline_data', {})

    LABELS = {
        'phase_2': ('📝 Review: User Stories & Architecture', 'Phase 2 complete'),
        'phase_4': ('⚙️ Review: Draft Specifications', 'Phase 4 complete'),
        'phase_5': ('🔍 Review: QA Report', 'Phase 5 complete'),
        'phase_6': ('✅ Review: Final Specifications', 'Phase 6 complete'),
    }
    title, subtitle = LABELS.get(pause_key, ('📋 Review Output', 'Paused'))

    st.subheader(title)
    st.caption(f"🧭 Guided Mode — {subtitle}. Review and edit the content below, then click **Continue Pipeline**.")
    st.info("✏️ You can freely edit any text area before continuing. Your edits will be fed into the next phase.")

    # ── PHASE 2: User Stories + Architecture ──────────────────────────────────
    if pause_key == 'phase_2':
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 📝 User Stories")
            if data.get('user_stories'):
                from src.agents import PMAgent as _PM
                from src.schemas import UserStory
                _stories = [UserStory.model_validate(s) for s in data['user_stories']]
                _us_md = _PM().format_user_stories_markdown(_stories)
                st.text_area(
                    "User Stories (read-only — structured data used by agents)",
                    value=_us_md,
                    height=420,
                    key="guided_view_user_stories",
                    disabled=True,
                    help="User stories have structured fields (IDs, acceptance criteria) that agents rely on. Free-text editing is not supported.",
                )
            else:
                st.warning("No user stories found.")
        with col_r:
            st.markdown("#### 🏛️ Architecture")
            st.text_area(
                "Architecture Spec (editable)",
                value=data.get('architecture', ''),
                height=420,
                key="guided_edit_architecture",
                help="Edit the architecture spec — your changes will be used in the drafting phase.",
            )

    # ── PHASE 4: Backend Draft + Frontend Draft ───────────────────────────────
    elif pause_key == 'phase_4':
        tab_be, tab_fe = st.tabs(["⚙️ Backend Draft", "🎨 Frontend Draft"])
        with tab_be:
            st.text_area(
                "Backend Draft (editable)",
                value=data.get('backend_draft', ''),
                height=520,
                key="guided_edit_backend_draft",
                help="Edit the backend spec draft — changes will flow into QA analysis and the fixing phase.",
            )
        with tab_fe:
            st.text_area(
                "Frontend Draft (editable)",
                value=data.get('frontend_draft', ''),
                height=520,
                key="guided_edit_frontend_draft",
                help="Edit the frontend spec draft — changes will flow into QA analysis and the fixing phase.",
            )

    # ── PHASE 5: QA Report (read-only review) ────────────────────────────────
    elif pause_key == 'phase_5':
        st.markdown("#### 🔍 QA Report")
        if data.get('qa_report'):
            from src.agents import QAAgent as _QA
            from src.schemas import QAReport
            _qa_rpt = QAReport.model_validate(data['qa_report'])
            _total = len(_qa_rpt.critical) + len(_qa_rpt.high) + len(_qa_rpt.medium) + len(_qa_rpt.low)
            st.info(
                f"**{_total} issues found** — "
                f"{len(_qa_rpt.critical)} critical, {len(_qa_rpt.high)} high, "
                f"{len(_qa_rpt.medium)} medium, {len(_qa_rpt.low)} low"
            )
            st.markdown(_QA().format_qa_report_markdown(_qa_rpt))
        else:
            st.info("No QA report data available.")
        st.caption("ℹ️ QA report is for review — click Continue to apply fixes.")

    # ── PHASE 6: Backend Final + Frontend Final ───────────────────────────────
    elif pause_key == 'phase_6':
        tab_bef, tab_fef = st.tabs(["⚙️ Backend Final", "🎨 Frontend Final"])
        with tab_bef:
            st.text_area(
                "Backend Final Spec (editable)",
                value=data.get('backend_final', ''),
                height=520,
                key="guided_edit_backend_final",
                help="Edit the final backend spec — this version goes to PM evaluation and the output files.",
            )
        with tab_fef:
            st.text_area(
                "Frontend Final Spec (editable)",
                value=data.get('frontend_final', ''),
                height=520,
                key="guided_edit_frontend_final",
                help="Edit the final frontend spec — this version goes to PM evaluation and the output files.",
            )

    st.divider()
    col_cont, col_disc = st.columns([3, 1])
    with col_cont:
        if st.button("▶️ Continue Pipeline", type="primary", use_container_width=True):
            # Harvest text-area edits from session_state widget keys
            _edits = {}
            if pause_key == 'phase_2':
                _edits['architecture'] = (
                    st.session_state.get('guided_edit_architecture') or data.get('architecture', '')
                )
            elif pause_key == 'phase_4':
                _edits['backend_draft'] = (
                    st.session_state.get('guided_edit_backend_draft') or data.get('backend_draft', '')
                )
                _edits['frontend_draft'] = (
                    st.session_state.get('guided_edit_frontend_draft') or data.get('frontend_draft', '')
                )
            elif pause_key == 'phase_6':
                _edits['backend_final'] = (
                    st.session_state.get('guided_edit_backend_final') or data.get('backend_final', '')
                )
                _edits['frontend_final'] = (
                    st.session_state.get('guided_edit_frontend_final') or data.get('frontend_final', '')
                )
            # phase_5 has no editable fields — just continue
            st.session_state['guided_edits'] = _edits
            # guided_paused_at is still set; run_all_phases() will consume it
            run_all_phases()
    with col_disc:
        if st.button("🗑️ Discard & Start Fresh", use_container_width=True):
            st.session_state.pop('guided_paused_at', None)
            st.session_state.pop('guided_pipeline_data', None)
            st.session_state.pop('guided_edits', None)
            reset_session()
            st.rerun()


def run_all_phases(resume_checkpoint=None):
    """Run all phases sequentially without reruns. Accepts optional checkpoint to resume from."""
    
    MAX_RETRIES = 3
    ckpt_mgr = CheckpointManager()
    logger = logging.getLogger(__name__)

    # ── Guided-mode state ──────────────────────────────────────────────────────
    guided_mode = st.session_state.get('pipeline_mode', 'one_shot') == 'guided'
    guided_paused_at = st.session_state.get('guided_paused_at')
    guided_data = st.session_state.get('guided_pipeline_data') or {}
    guided_edits = st.session_state.get('guided_edits') or {}
    is_guided_resume = bool(guided_paused_at and guided_data)
    # Which phase inside the retry loop to resume at (set by the pause that saved guided_data)
    _skip_to = guided_data.get('skip_to', '') if is_guided_resume else ''
    # Only restore retry counters when paused from inside the retry loop itself
    _in_retry_loop_resume = is_guided_resume and _skip_to in ('phase_5', 'phase_6', 'phase_7')
    if is_guided_resume:
        # Consume the resume flags so a subsequent page-load doesn't re-trigger
        st.session_state.pop('guided_paused_at', None)
        st.session_state.pop('guided_edits', None)

    with st.status("🚀 Running AI Factory Pipeline...", expanded=True) as status:
        try:
            # ---- Determine resume state or start fresh ----
            resume_phase = 0
            context = None
            user_stories = []
            architecture = ""
            answers = {}
            pm_agent = PMAgent()
            dev_team = DevTeamAgent()
            
            if is_guided_resume:
                # Restore pipeline state from the guided-review snapshot
                resume_phase = guided_data.get('completed_phase', 0)
                if guided_data.get('context'):
                    context = DocumentAnalysis.model_validate(guided_data['context'])
                    update_workflow_state(context=context)
                if guided_data.get('user_stories'):
                    from src.schemas import UserStory
                    user_stories = [UserStory.model_validate(s) for s in guided_data['user_stories']]
                    update_workflow_state(user_stories=user_stories)
                architecture = guided_edits.get('architecture') or guided_data.get('architecture', '')
                if architecture:
                    update_workflow_state(architecture=architecture)
                answers = guided_data.get('answers', {})
                if answers:
                    update_workflow_state(clarifications=answers)
                st.write(f"▶️ **Resuming guided pipeline** — continuing from review (Phase {resume_phase} complete)...")

            elif resume_checkpoint is not None:
                resume_phase = resume_checkpoint.phase
                st.write(f"▶️ **Resuming from checkpoint** (last completed: Phase {resume_phase})...")
                if resume_checkpoint.context:
                    context = DocumentAnalysis.model_validate(resume_checkpoint.context)
                    update_workflow_state(context=context)
                if resume_checkpoint.user_stories:
                    from src.schemas import UserStory
                    user_stories = [UserStory.model_validate(s) for s in resume_checkpoint.user_stories]
                    update_workflow_state(user_stories=user_stories)
                if resume_checkpoint.architecture:
                    architecture = resume_checkpoint.architecture
                    update_workflow_state(architecture=architecture)
                if resume_checkpoint.clarifications:
                    answers = {
                        k: (v.get('answer') or v.get('text') or str(v)) if isinstance(v, dict) else str(v)
                        for k, v in resume_checkpoint.clarifications.items()
                    }
                    update_workflow_state(clarifications=answers)
                ckpt_mgr._current_checkpoint = resume_checkpoint
            else:
                project_name = (st.session_state.get('file_name') or 'project').split('.')[0]
                ckpt_mgr.start_new_pipeline(project_name=project_name)
            
            # ------- PHASE 1 -------
            if resume_phase < 1:
                set_phase(1)
                st.write("📄 **Phase 1:** Parsing document...")
                vision_agent = VisionAgent()
                
                if st.session_state.get('file_bytes'):
                    file_bytes = st.session_state['file_bytes']
                    file_name = st.session_state['file_name']
                    file_type = file_name.split('.')[-1] if '.' in file_name else 'txt'
                    context = vision_agent.parse_document(file_bytes, file_name, file_type)
                else:
                    text_input = st.session_state.get('text_input', '')
                    context = vision_agent.parse_text_input(text_input)
                
                update_workflow_state(context=context)

                # H-5: Abort early if document parsing produced no features
                if not context.features:
                    status.update(label="❌ No features extracted from document", state="error")
                    st.error(
                        "❌ Document parsing produced no recognizable features. "
                        "Please provide a more detailed requirements document and try again."
                    )
                    return

                st.write(f"✅ Phase 1 complete: {len(context.features)} features")
                
                with st.expander("📋 View Phase 1 Output"):
                    st.markdown(f"**Project Type:** {context.project_type.value}")
                    st.markdown(f"**Features:** {', '.join(context.features[:5])}")
                    if context.personas:
                        st.markdown(f"**Personas:** {', '.join(context.personas[:3])}")
                
                ckpt_mgr.save_checkpoint(1, context=context.model_dump())
            else:
                set_phase(1)
                _restore_label = "guided review" if is_guided_resume else "checkpoint"
                st.write(f"⏩ Phase 1: Restored from {_restore_label} ({len(context.features)} features)")
            
            # ------- PHASE 2 -------
            if resume_phase < 2:
                set_phase(2)
                st.write("📝 **Phase 2:** Generating user stories & architecture...")
                user_stories = pm_agent.generate_user_stories(context)
                update_workflow_state(user_stories=user_stories)
                st.write(f"✅ Generated {len(user_stories)} user stories")
                
                with st.expander("📝 View User Stories"):
                    for story in user_stories[:5]:
                        st.write(f"**{story.id}:** {story.title}")
                
                tech_lead = TechLeadAgent()
                architecture = tech_lead.generate_architecture(context, user_stories)
                update_workflow_state(architecture=architecture)
                st.write("✅ Architecture designed")
                
                with st.expander("🏛️ View Architecture"):
                    st.markdown(architecture[:3000] + "..." if len(architecture) > 3000 else architecture)
                
                ckpt_mgr.save_checkpoint(2,
                    user_stories=[s.model_dump() for s in user_stories],
                    architecture=architecture)

                # --- Discussion: Team reviews user stories & architecture ---
                _d_project_id = (st.session_state.get('file_name') or 'project').split('.')[0]
                _d_agents = {
                    "PMAgent": pm_agent,
                    "TechLeadAgent": tech_lead,
                    "DevTeamAgent": dev_team,
                    "QAAgent": QAAgent(),
                }
                _orchestrator = DiscussionOrchestrator(
                    agents=_d_agents,
                    memory=SharedMemory(project_id=_d_project_id)
                )
                st.write("💬 **Discussion:** Team reviewing user stories & architecture...")
                for _topic_id in ("USER_STORIES_REVIEW", "ARCHITECTURE_REVIEW"):
                    try:
                        _disc_result = _orchestrator.run_discussion(
                            _orchestrator.start_discussion(_topic_id)
                        )
                        st.write(f"  ✅ {_disc_result.topic_name}: {_disc_result.status.value}")
                        if _disc_result.decision:
                            with st.expander(f"📌 {_disc_result.topic_name} Decision"):
                                st.markdown(_disc_result.decision[:500])
                    except Exception as _e:
                        logger.warning(f"Discussion {_topic_id} skipped: {_e}")
                        st.warning(f"  ⚠️ Discussion '{_topic_id}' skipped: {_e}")

                # GUIDED MODE: pause after Phase 2 for human review
                if guided_mode:
                    st.session_state['guided_paused_at'] = 'phase_2'
                    st.session_state['guided_pipeline_data'] = {
                        'completed_phase': 2,
                        'skip_to': 'phase_3',
                        'context': context.model_dump(),
                        'user_stories': [s.model_dump() for s in user_stories],
                        'architecture': architecture,
                        'answers': {},
                    }
                    status.update(label="⏸️ Guided: Review user stories & architecture", state="running")
                    st.rerun()
            else:
                set_phase(2)
                _restore_label = "guided review" if is_guided_resume else "checkpoint"
                st.write(f"⏩ Phase 2: Restored from {_restore_label} ({len(user_stories)} stories)")

            # ------- PHASE 3 -------
            if resume_phase < 3:
                set_phase(3)
                st.write("❓ **Phase 3:** Generating clarifications...")
                clarifications = dev_team.generate_clarification_questions(context, user_stories, architecture)
                if clarifications:
                    answers = pm_agent.answer_clarifications(clarifications, context, user_stories)
                    st.write(f"✅ Answered {len(answers)} questions")
                else:
                    answers = {}
                    st.write("✅ No clarifications needed")
                update_workflow_state(clarifications=answers)
                
                ckpt_mgr.save_checkpoint(3, clarifications=answers)
            else:
                set_phase(3)
                _restore_label = "guided review" if is_guided_resume else "checkpoint"
                st.write(f"⏩ Phase 3: Restored from {_restore_label} ({len(answers)} answers)")
            
            # RETRY LOOP FOR PHASES 4-7
            # Restore retry counters only when resuming from inside the retry loop (paused at phase 5/6)
            retry_attempt = guided_data.get('retry_attempt', 0) if _in_retry_loop_resume else 0
            feedback = guided_data.get('feedback', '') if _in_retry_loop_resume else ''
            backend_final = None
            frontend_final = None
            _guided_first_iter = True  # Only True on the very first pass through the while-loop

            while retry_attempt < MAX_RETRIES:
                if retry_attempt > 0:
                    st.write(f"🔄 **Retry {retry_attempt}/{MAX_RETRIES-1}:** Regenerating with feedback...")
                    with st.expander("⚠️ View Previous Feedback"):
                        st.warning(feedback)

                # ── PHASE 4 ── generate drafts, or restore from guided review ───
                set_phase(4)
                if _guided_first_iter and _in_retry_loop_resume and _skip_to in ('phase_5', 'phase_6', 'phase_7'):
                    # Restore already-reviewed drafts instead of re-generating
                    backend_draft = guided_edits.get('backend_draft') or guided_data.get('backend_draft', '')
                    frontend_draft = guided_edits.get('frontend_draft') or guided_data.get('frontend_draft', '')
                    update_workflow_state(backend_draft=backend_draft, frontend_draft=frontend_draft)
                    st.write("⏩ Phase 4: Restored from guided review")
                else:
                    st.write("⚙️ **Phase 4:** Drafting specifications...")
                    backend_draft = dev_team.generate_backend_draft(context, user_stories, architecture, answers, feedback)
                    update_workflow_state(backend_draft=backend_draft)
                    st.write("✅ Backend spec drafted")
                    logger.info(f"Phase 4: backend_draft length = {len(backend_draft) if backend_draft else 0}")

                    with st.expander("⚙️ View Backend Spec"):
                        st.markdown(backend_draft[:3000] + "..." if len(backend_draft) > 3000 else backend_draft)

                    frontend_draft = dev_team.generate_frontend_draft(context, user_stories, architecture, backend_draft, answers, feedback)
                    update_workflow_state(frontend_draft=frontend_draft)
                    st.write("✅ Frontend spec drafted")
                    logger.info(f"Phase 4: frontend_draft length = {len(frontend_draft) if frontend_draft else 0}")

                    with st.expander("🎨 View Frontend Spec"):
                        st.markdown(frontend_draft[:3000] + "..." if len(frontend_draft) > 3000 else frontend_draft)

                    # GUIDED MODE: pause after drafts for human review
                    if guided_mode:
                        st.session_state['guided_paused_at'] = 'phase_4'
                        st.session_state['guided_pipeline_data'] = {
                            'completed_phase': 3,
                            'skip_to': 'phase_5',
                            'context': context.model_dump(),
                            'user_stories': [s.model_dump() for s in user_stories],
                            'architecture': architecture,
                            'answers': answers,
                            'retry_attempt': retry_attempt,
                            'feedback': feedback,
                            'backend_draft': backend_draft,
                            'frontend_draft': frontend_draft,
                        }
                        status.update(label="⏸️ Guided: Review draft specs before QA", state="running")
                        st.rerun()

                # ── PHASE 5 ── QA analysis, or restore qa_report from guided review ─
                set_phase(5)
                if _guided_first_iter and _in_retry_loop_resume and _skip_to in ('phase_6', 'phase_7'):
                    from src.schemas import QAReport as _QAReport
                    qa_report = _QAReport.model_validate(guided_data['qa_report'])
                    total_issues = len(qa_report.critical) + len(qa_report.high) + len(qa_report.medium) + len(qa_report.low)
                    update_workflow_state(qa_report=qa_report)
                    st.write(f"⏩ Phase 5: Restored from guided review ({total_issues} issues)")
                else:
                    st.write("🔍 **Phase 5:** Quality analysis...")
                    qa_agent = QAAgent()
                    user_stories_dicts = [story.model_dump() for story in user_stories]
                    qa_report = qa_agent.analyze_specifications(backend_draft, frontend_draft, architecture, user_stories_dicts)
                    with st.expander("🔍 View QA Issues"):
                        if qa_report.critical:
                            st.markdown("**Critical:**")
                            for issue in qa_report.critical[:3]:
                                st.write(f"- [{issue.location}] {issue.desc}")
                        if qa_report.high:
                            st.markdown("**High:**")
                            for issue in qa_report.high[:3]:
                                st.write(f"- [{issue.location}] {issue.desc}")

                    total_issues = len(qa_report.critical) + len(qa_report.high) + len(qa_report.medium) + len(qa_report.low)
                    st.write(f"✅ QA complete: {total_issues} issues ({len(qa_report.critical)} critical, {len(qa_report.high)} high)")
                    update_workflow_state(qa_report=qa_report)

                    # --- Discussion: Team reviews specs before applying fixes ---
                    _d_project_id = (st.session_state.get('file_name') or 'project').split('.')[0]
                    _p5_agents = {
                        "PMAgent": pm_agent,
                        "TechLeadAgent": TechLeadAgent(),
                        "DevTeamAgent": dev_team,
                        "QAAgent": qa_agent,
                    }
                    _p5_orchestrator = DiscussionOrchestrator(
                        agents=_p5_agents,
                        memory=SharedMemory(project_id=_d_project_id)
                    )
                    st.write("💬 **Discussion:** Team reviewing specifications...")
                    try:
                        _spec_result = _p5_orchestrator.run_discussion(
                            _p5_orchestrator.start_discussion("SPEC_REVIEW")
                        )
                        st.write(f"  ✅ Spec Review: {_spec_result.status.value}")
                        if _spec_result.decision:
                            with st.expander("📌 Spec Review Decision"):
                                st.markdown(_spec_result.decision[:500])
                    except Exception as _e:
                        logger.warning(f"SPEC_REVIEW discussion skipped: {_e}")
                        st.warning(f"  ⚠️ Spec review skipped: {_e}")

                    # GUIDED MODE: pause after QA for human review
                    if guided_mode:
                        st.session_state['guided_paused_at'] = 'phase_5'
                        st.session_state['guided_pipeline_data'] = {
                            'completed_phase': 4,
                            'skip_to': 'phase_6',
                            'context': context.model_dump(),
                            'user_stories': [s.model_dump() for s in user_stories],
                            'architecture': architecture,
                            'answers': answers,
                            'retry_attempt': retry_attempt,
                            'feedback': feedback,
                            'backend_draft': backend_draft,
                            'frontend_draft': frontend_draft,
                            'qa_report': qa_report.model_dump(),
                        }
                        status.update(label="⏸️ Guided: Review QA report before applying fixes", state="running")
                        st.rerun()

                # ── PHASE 6 ── fix issues, or restore finals from guided review ──
                set_phase(6)
                if _guided_first_iter and _in_retry_loop_resume and _skip_to == 'phase_7':
                    backend_final = guided_edits.get('backend_final') or guided_data.get('backend_final', '')
                    frontend_final = guided_edits.get('frontend_final') or guided_data.get('frontend_final', '')
                    update_workflow_state(backend_final=backend_final, frontend_final=frontend_final)
                    st.write("⏩ Phase 6: Restored from guided review")
                else:
                    if total_issues > 0:
                        st.write("🔧 **Phase 6:** Fixing issues...")
                        backend_final = dev_team.fix_backend_spec(backend_draft, qa_report)
                        frontend_final = dev_team.fix_frontend_spec(frontend_draft, qa_report)
                        st.write("✅ Issues fixed")
                    else:
                        backend_final = backend_draft
                        frontend_final = frontend_draft
                        st.write("✅ No issues to fix")

                    logger.info(f"Phase 6: backend_final length = {len(backend_final) if backend_final else 0}")
                    logger.info(f"Phase 6: frontend_final length = {len(frontend_final) if frontend_final else 0}")
                    update_workflow_state(backend_final=backend_final, frontend_final=frontend_final)

                    # GUIDED MODE: pause after final specs for human review
                    if guided_mode:
                        st.session_state['guided_paused_at'] = 'phase_6'
                        st.session_state['guided_pipeline_data'] = {
                            'completed_phase': 5,
                            'skip_to': 'phase_7',
                            'context': context.model_dump(),
                            'user_stories': [s.model_dump() for s in user_stories],
                            'architecture': architecture,
                            'answers': answers,
                            'retry_attempt': retry_attempt,
                            'feedback': feedback,
                            'backend_draft': backend_draft,
                            'frontend_draft': frontend_draft,
                            'qa_report': qa_report.model_dump(),
                            'backend_final': backend_final,
                            'frontend_final': frontend_final,
                        }
                        status.update(label="⏸️ Guided: Review final specs before PM evaluation", state="running")
                        st.rerun()

                _guided_first_iter = False  # Subsequent retries always run all phases

                # PHASE 7
                set_phase(7)
                st.write("✅ **Phase 7:** Final evaluation...")
                
                if not backend_final or not frontend_final:
                    st.error("❌ Missing backend or frontend specifications. Cannot evaluate.")
                    raise ValueError("Backend or frontend specifications are missing")
                
                qa_summary = f"""QA Report Summary:
- Critical Issues: {len(qa_report.critical)}
- High Issues: {len(qa_report.high)}
- Medium Issues: {len(qa_report.medium)}
- Low Issues: {len(qa_report.low)}
- Security Flags: {len(qa_report.security_flags)}

Critical Issues:
{chr(10).join(f'- [{issue.location}] {issue.desc}' for issue in qa_report.critical[:5])}

High Issues:
{chr(10).join(f'- [{issue.location}] {issue.desc}' for issue in qa_report.high[:5])}
"""
                
                evaluation = pm_agent.evaluate_specifications(
                    context,
                    user_stories,
                    architecture,
                    backend_final,
                    frontend_final,
                    qa_summary
                )
                update_workflow_state(pm_evaluation=evaluation)
                st.write(f"✅ {evaluation.status.value} (Score: {evaluation.score}/100)")
                
                with st.expander("📊 View Evaluation Details"):
                    st.metric("Score", f"{evaluation.score}/100")
                    if evaluation.issues:
                        st.markdown("**Issues Found:**")
                        for issue in evaluation.issues[:5]:
                            st.write(f"- {issue}")
                
                # CHECK EVALUATION STATUS
                if evaluation.score < 85:
                    retry_attempt += 1
                    update_workflow_state(retry_count=retry_attempt)
                    
                    # Coach learns from rejection — activates the self-improvement loop
                    try:
                        coach = CoachAgent()
                        lessons = coach.process_rejection(evaluation)
                        if lessons:
                            st.info(f"🧠 **Coach:** Extracted {len(lessons)} lesson(s) and updated agent playbooks.")
                        else:
                            st.info("🧠 **Coach:** Processed rejection (no new lessons extracted).")
                    except Exception as coach_err:
                        logger.warning(f"Coach agent failed silently: {coach_err}")
                    
                    if retry_attempt >= MAX_RETRIES:
                        status.update(label=f"❌ REJECTED after {MAX_RETRIES} attempts (Score: {evaluation.score}/100)", state="error")
                        st.error(f"❌ **Evaluation Failed:** Score {evaluation.score}/100 after {MAX_RETRIES} attempts")
                        st.error("**Final Issues:**")
                        for issue in evaluation.issues:
                            st.write(f"- {issue}")
                        if evaluation.scolding:
                            st.error("**PM Feedback:**")
                            st.markdown(evaluation.scolding)
                        st.info("💡 **Tip:** Refine your requirements document and try again.")
                        return
                    
                    feedback = f"""PREVIOUS EVALUATION REJECTED (Score: {evaluation.score}/100)

❌ ISSUES FOUND:
{chr(10).join(f'- {issue}' for issue in evaluation.issues)}

🗣️ PM SCOLDING:
{evaluation.scolding}

⚠️ FIX THESE ISSUES! Be more specific, complete, and production-ready."""
                    
                    st.warning(f"⚠️ Score {evaluation.score}/100 - Retrying with feedback ({retry_attempt}/{MAX_RETRIES-1})...")
                    continue  # Loop back to Phase 4
                
                else:
                    # APPROVED — break out of retry loop
                    st.success(f"✅ **APPROVED!** Score: {evaluation.score}/100")
                    break
            
            # PHASE 8 — Only reached after approval (break from while loop)
            set_phase(8)
            st.write("💾 **Phase 8:** Saving outputs...")
            
            pm_agent_formatter = PMAgent()
            qa_agent_formatter = QAAgent()
            
            user_stories_md = pm_agent_formatter.format_user_stories_markdown(user_stories)
            qa_report_md = qa_agent_formatter.format_qa_report_markdown(qa_report)
            
            playbook_rules = {
                'pm': get_playbook_rules('pm'),
                'tech_lead': get_playbook_rules('tech_lead'),
                'backend': get_playbook_rules('backend'),
                'frontend': get_playbook_rules('frontend'),
                'qa': get_playbook_rules('qa')
            }
            master_prompt = generate_master_prompt(context, user_stories, architecture, backend_final, frontend_final, qa_report_md, playbook_rules)
            
            # Cost estimation + executive summary (were missing from Path A — now wired in)
            st.write("📊 Generating cost estimation & executive summary...")
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
                executive_summary=executive_summary
            )
            
            # Clear checkpoint and any guided-mode state — run completed successfully
            ckpt_mgr.clear_all_checkpoints()
            st.session_state.pop('guided_pipeline_data', None)
            st.session_state.pop('guided_paused_at', None)
            st.session_state.pop('guided_edits', None)

            st.session_state['output_folder'] = str(output_folder)
            st.session_state['generation_complete'] = True
            
            status.update(label="🎉 Pipeline Complete!", state="complete")
            
        except Exception as e:
            status.update(label="❌ Pipeline Failed", state="error")
            
            error_msg = str(e)
            if "daily token limit" in error_msg.lower() or "tpd" in error_msg.lower():
                st.error("❌ **DAILY TOKEN LIMIT EXCEEDED**")
                st.warning("🚨 You've hit your daily token limit for this model.")
                st.info("""
**Options:**
1. ⏳ Wait for token limit to reset
2. 💳 Upgrade to Dev Tier at [Groq Console](https://console.groq.com/settings/billing)
3. 🔄 Use a different model (e.g., Llama 3.1 8B)
                """)
            else:
                st.error(f"**Error:** {e}")
            
            st.code(traceback.format_exc())
            return
    
    st.balloons()
    st.success("🎉 **MVP Specifications Generated Successfully!**")
    st.rerun()


def render_results():
    """Render the final results section."""
    state = get_workflow_state()
    folder = st.session_state.get('output_folder', '')
    
    st.markdown("""
    <div class="success-banner">
        <h2>🎉 MVP Specifications Generated!</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    pm_score = state.pm_evaluation.score if state.pm_evaluation else 0
    col1.metric("📊 PM Score", f"{pm_score}%")
    col2.metric("📝 User Stories", len(state.user_stories))
    col3.metric("🔄 Iterations", state.retry_count)
    col4.metric("🧬 Rules Applied", get_evolution_level())
    
    # Output folder
    st.markdown(f"**📁 Output Folder:** `{folder}`")
    
    # File list — reflects actual save_all_project_files() output
    st.markdown("### Generated Files:")
    files = [
        ("00_EXECUTIVE_SUMMARY.md", "Stakeholder-facing summary — features, timeline, budget"),
        ("01_MASTER_PROMPT.md", "Implementation guide + active playbook rules"),
        ("02_User_Stories.md", "User stories with acceptance criteria"),
        ("03_Architecture.md", "System architecture and tech stack"),
        ("04_Backend_Final.md", "Backend implementation specification"),
        ("05_Frontend_Final.md", "Frontend implementation specification"),
        ("06_QA_Report.md", "Quality assurance findings and security flags"),
        ("08_Cost_Estimation.md", "Cost and timeline estimates (heuristic)"),
    ]
    
    folder_path = Path(folder) if folder else None
    for filename, description in files:
        exists = folder_path and (folder_path / filename).exists()
        if exists:
            st.markdown(f"- **{filename}** — {description}")
        else:
            st.markdown(f"- ~~{filename}~~ — {description} *(not generated)*")
    
    if state.warnings:
        st.warning("⚠️ WARNING_UNRESOLVED_RISKS.md was also generated - please review!")
    
    # Actions
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📂 Open Folder", use_container_width=True):
            os.startfile(folder) if os.name == 'nt' else os.system(f'open "{folder}"')
    
    with col2:
        if st.button("🆕 Start New Project", type="primary", use_container_width=True):
            reset_session()
            st.rerun()


def render_workflow():
    """Render the main workflow area."""
    state = get_workflow_state()

    # Guided mode: intercept and show editable review UI when pipeline is paused
    if st.session_state.get('guided_paused_at'):
        render_guided_review()
        return

    # Check if generation is complete
    if st.session_state.get('generation_complete'):
        render_results()
        return
    
    # Show current phase progress
    st.progress((state.phase - 1) / 8, text=f"Phase {state.phase}/8: {PHASE_NAMES.get(state.phase, 'Unknown')}")
    
    # Phase 1: Document Upload (only show if still in phase 1 and no ready flags)
    if state.phase == 1 and not any(st.session_state.get(f'ready_for_phase_{i}') for i in range(2, 9)):
        render_file_upload()
    
    # All phase transitions are handled within run_all_phases().
    # The individual run_phase_N() functions below are kept as reference
    # implementations but are not dispatched from here.
    
    # Show current state artifacts
    if state.phase > 1:
        st.divider()
        st.subheader("📋 Generated Artifacts")
        
        # Show artifacts based on phase
        if state.user_stories:
            with st.expander(f"📝 User Stories ({len(state.user_stories)})"):
                pm = PMAgent()
                st.markdown(pm.format_user_stories_markdown(state.user_stories)[:3000])
        
        if state.architecture:
            with st.expander("🏛️ Architecture"):
                st.markdown(state.architecture[:3000])
        
        if state.backend_final or state.backend_draft:
            spec = state.backend_final or state.backend_draft
            label = "⚙️ Backend (Final)" if state.backend_final else "⚙️ Backend (Draft)"
            with st.expander(label):
                st.markdown(spec[:3000])
        
        if state.frontend_final or state.frontend_draft:
            spec = state.frontend_final or state.frontend_draft
            label = "🎨 Frontend (Final)" if state.frontend_final else "🎨 Frontend (Draft)"
            with st.expander(label):
                st.markdown(spec[:3000])
        
        if state.qa_report:
            qa = QAAgent()
            with st.expander("🔍 QA Report"):
                st.markdown(qa.format_qa_report_markdown(state.qa_report))


def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    st.title("🧠 The AI Factory")
    st.caption("Transform business requirements into complete MVP specifications")
    
    # Show any errors
    error = get_error()
    if error:
        st.error(f"Error: {error}")
        if st.button("Clear Error"):
            clear_error()
            st.rerun()
    
    # Render main workflow
    render_workflow()


if __name__ == "__main__":
    main()
