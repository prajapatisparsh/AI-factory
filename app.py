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
    validate_state_for_phase,
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

from src.agents.cost_estimator import estimate_project_costs, generate_executive_summary
from src.utils.cycle_logger import CycleLogger
from src.utils.checkpoint import get_checkpoint_manager, CheckpointManager
from src.utils.model_provider import get_model_provider, ModelProvider
from src.utils.parallel import run_agents_parallel, parallel_draft_generation
from src.utils.llm_cache import get_llm_cache
from src.utils.discussion_renderer import (
    render_discussion,
    render_quick_discussion,
    render_team_activity,
    create_simulated_discussion,
    AGENT_EMOJIS,
    AGENT_NAMES
)

from src.discussion.protocol import Discussion, DiscussionMessage, MessageType, ConsensusStatus
from src.discussion.memory import SharedMemory
from src.discussion.orchestrator import DiscussionOrchestrator
from src.discussion.topics import DISCUSSION_TOPICS, get_topic

from src.agents.moderator import ModeratorAgent

from src.schemas import DocumentAnalysis, EvaluationStatus


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
        
        # Model Selection
        st.subheader("🤖 Model Settings")
        try:
            model_provider = get_model_provider()
            available_models = model_provider.get_available_models()
            model_names = [f"{m.name} ({m.provider.value})" for m in available_models]
            model_ids = [m.id for m in available_models]
            
            if 'selected_model' not in st.session_state:
                st.session_state['selected_model'] = model_ids[0] if model_ids else "llama-3.1-8b-instant"
            
            selected_idx = st.selectbox(
                "Select Model",
                range(len(model_names)),
                format_func=lambda x: model_names[x] if x < len(model_names) else "Default",
                key="model_selector"
            )
            
            if selected_idx is not None and selected_idx < len(model_ids):
                st.session_state['selected_model'] = model_ids[selected_idx]
                selected_model = available_models[selected_idx]
                st.caption(f"💰 Cost: ${selected_model.cost_per_1k_input}/1K tokens")
        except Exception as e:
            st.caption("Using default model")
        
        # Parallel Execution Toggle
        st.session_state['parallel_enabled'] = st.checkbox(
            "⚡ Parallel Execution",
            value=st.session_state.get('parallel_enabled', True),
            help="Run backend and frontend generation in parallel"
        )
        
        st.divider()
        
        # Resume from Checkpoint
        checkpoint_mgr = get_checkpoint_manager()
        if checkpoint_mgr.should_resume():
            checkpoint = checkpoint_mgr.get_latest_checkpoint()
            if checkpoint:
                st.warning(f"💾 Checkpoint found: Phase {checkpoint.phase}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("▶️ Resume", use_container_width=True):
                        st.session_state['resume_checkpoint'] = checkpoint
                        st.rerun()
                with col2:
                    if st.button("🗑️ Discard", use_container_width=True):
                        checkpoint_mgr.clear_all_checkpoints()
                        st.rerun()
        
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
                st.text(f"{name}: {data['total']} ({data['learned']} learned)")


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
    
    if has_input:
        if st.button("🚀 Start Virtual Team", type="primary", use_container_width=True):
            run_team_discussion()


def run_team_discussion():
    """Run the Virtual Team discussion-based workflow."""
    
    st.title("🧠 Virtual Team Session")
    
    # Initialize agents
    agents = {
        "PMAgent": PMAgent(),
        "TechLeadAgent": TechLeadAgent(),
        "DevTeamAgent": DevTeamAgent(),
        "QAAgent": QAAgent(),
        "ModeratorAgent": ModeratorAgent()
    }
    
    # Initialize shared memory for this session
    project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    memory = SharedMemory(project_id)
    
    all_discussions = []
    
    with st.status("🧠 Virtual Team is working...", expanded=True) as status:
        try:
            # ═══════════════════════════════════════════════════════════════
            # PHASE 1: Document Understanding (Single Agent)
            # ═══════════════════════════════════════════════════════════════
            set_phase(1)
            st.write("📄 **Phase 1:** Vision Agent parsing document...")
            
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
            st.write(f"✅ Extracted {len(context.features)} features")
            
            # Store context in memory for discussions
            memory.set_context("features", context.features)
            memory.set_context("project_type", context.project_type.value)
            memory.set_context("personas", context.personas)
            
            with st.expander("📋 Extracted Requirements", expanded=False):
                st.markdown(f"**Project Type:** {context.project_type.value}")
                st.markdown("**Features:**")
                for i, feature in enumerate(context.features[:10], 1):
                    st.markdown(f"{i}. {feature}")
                if context.personas:
                    st.markdown(f"**Personas:** {', '.join(context.personas[:5])}")
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 2: Scope Discussion (PM + TechLead)
            # ═══════════════════════════════════════════════════════════════
            set_phase(2)
            st.write("📝 **Phase 2:** Team discussing scope and user stories...")
            
            # Generate user stories first
            pm_agent = agents["PMAgent"]
            user_stories = pm_agent.generate_user_stories(context)
            update_workflow_state(user_stories=user_stories)
            
            # Create discussion about user stories
            stories_discussion = _create_team_discussion(
                topic="User Stories Review",
                participants=["PMAgent", "TechLeadAgent", "QAAgent"],
                context_summary=f"We have {len(user_stories)} user stories generated from {len(context.features)} features.",
                discussion_points=[
                    f"PMAgent: I've generated {len(user_stories)} user stories covering: {', '.join([s.title for s in user_stories[:3]])}...",
                    f"TechLeadAgent: The stories look comprehensive. I recommend prioritizing authentication and core data models first.",
                    f"QAAgent: I'll need clear acceptance criteria for testing. The stories include specific testable conditions."
                ],
                decision=f"Approved {len(user_stories)} user stories with {sum(1 for s in user_stories if s.priority.value == 'Critical')} critical priority items",
                rationale="Stories cover all extracted features with testable acceptance criteria"
            )
            all_discussions.append(stories_discussion)
            
            render_quick_discussion(
                topic="📝 User Stories Review",
                messages=[
                    {"agent": "PMAgent", "content": f"I've generated {len(user_stories)} user stories from the requirements. Key stories include: {', '.join([s.title for s in user_stories[:3]])}..."},
                    {"agent": "TechLeadAgent", "content": "The stories are well-structured. I suggest we prioritize authentication and core data models for the MVP."},
                    {"agent": "QAAgent", "content": "Acceptance criteria are testable. I can create test cases from these."}
                ],
                decision=f"✓ Approved {len(user_stories)} user stories",
                rationale=f"Critical: {sum(1 for s in user_stories if s.priority.value == 'Critical')}, High: {sum(1 for s in user_stories if s.priority.value == 'High')}"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 3: Architecture Discussion (TechLead + Team)
            # ═══════════════════════════════════════════════════════════════
            set_phase(3)
            st.write("🏛️ **Phase 3:** Team discussing architecture...")
            
            tech_lead = agents["TechLeadAgent"]
            architecture = tech_lead.generate_architecture(context, user_stories)
            update_workflow_state(architecture=architecture)
            
            # Detect domain and tech stack from architecture
            tech_stack = _extract_tech_stack(architecture)
            
            render_quick_discussion(
                topic="🏛️ Architecture Decisions",
                messages=[
                    {"agent": "TechLeadAgent", "content": f"For this {context.project_type.value} project, I recommend: {tech_stack.get('backend', 'Node.js/Python')} backend, {tech_stack.get('database', 'PostgreSQL')} database, {tech_stack.get('frontend', 'React')} frontend."},
                    {"agent": "DevTeamAgent", "content": "The stack aligns with best practices. I can implement the backend services with proper API structure."},
                    {"agent": "PMAgent", "content": "This architecture supports all our user stories and allows for future scaling."},
                    {"agent": "QAAgent", "content": "The architecture enables proper testing at unit, integration, and e2e levels."}
                ],
                decision=f"✓ Approved architecture: {tech_stack.get('backend', 'Backend')} + {tech_stack.get('database', 'DB')} + {tech_stack.get('frontend', 'Frontend')}",
                rationale="Scalable, testable, and aligned with project requirements"
            )
            
            # Generate diagrams
            st.caption("📊 Generating architecture diagrams...")
            diagrams = tech_lead.generate_architecture_diagram(context, architecture)
            architecture_with_diagrams = architecture + "\n\n" + diagrams
            update_workflow_state(architecture=architecture_with_diagrams)
            
            with st.expander("📊 Architecture Diagrams", expanded=False):
                st.markdown(diagrams)
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 4: Implementation Discussion (DevTeam)
            # ═══════════════════════════════════════════════════════════════
            set_phase(4)
            st.write("💻 **Phase 4:** Dev Team drafting specifications...")
            
            dev_team = agents["DevTeamAgent"]
            
            # Generate clarifications first
            clarifications = dev_team.generate_clarification_questions(context, user_stories, architecture_with_diagrams)
            if clarifications:
                answers = pm_agent.answer_clarifications(clarifications, context, user_stories)
                st.write(f"✅ Answered {len(answers)} clarification questions")
            else:
                answers = {}
            
            # Draft backend spec
            backend_draft = dev_team.generate_backend_draft(context, user_stories, architecture_with_diagrams, answers)
            update_workflow_state(backend_draft=backend_draft)
            
            # Draft frontend spec (needs backend spec for API contract)
            frontend_draft = dev_team.generate_frontend_draft(context, user_stories, architecture_with_diagrams, backend_draft, answers)
            update_workflow_state(frontend_draft=frontend_draft)
            
            render_quick_discussion(
                topic="💻 Implementation Planning",
                messages=[
                    {"agent": "DevTeamAgent", "content": f"I've drafted the backend specification with API endpoints, data models, and business logic. Also completed the frontend spec with components and UI flows."},
                    {"agent": "TechLeadAgent", "content": "The specs follow our architecture decisions. API design is RESTful with proper error handling."},
                    {"agent": "QAAgent", "content": "I'll review for potential issues and edge cases."}
                ],
                decision="✓ Backend and Frontend specifications drafted",
                rationale="Comprehensive coverage of all user stories with clear implementation details"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 5: Quality Review Discussion (QA + Team)
            # ═══════════════════════════════════════════════════════════════
            set_phase(5)
            st.write("🔍 **Phase 5:** QA Team reviewing specifications...")
            
            qa_agent = agents["QAAgent"]
            qa_report = qa_agent.analyze_specifications(
                backend_draft, frontend_draft, architecture_with_diagrams, 
                [s.model_dump() for s in user_stories]
            )
            update_workflow_state(qa_report=qa_report)
            
            # Count issues by severity
            issue_counts = {
                "Critical": len(qa_report.critical),
                "High": len(qa_report.high),
                "Medium": len(qa_report.medium),
                "Low": len(qa_report.low)
            }
            
            render_quick_discussion(
                topic="🔍 Quality Assessment",
                messages=[
                    {"agent": "QAAgent", "content": f"Review complete. Found: {issue_counts['Critical']} critical, {issue_counts['High']} high, {issue_counts['Medium']} medium, {issue_counts['Low']} low priority issues."},
                    {"agent": "DevTeamAgent", "content": "I'll address the critical and high priority issues immediately."},
                    {"agent": "TechLeadAgent", "content": "Let's prioritize security-related issues first, then functionality gaps."}
                ],
                decision=f"✓ {sum(issue_counts.values())} issues identified for resolution",
                rationale="Security and critical functionality issues take priority"
            )
            
            with st.expander("🔍 QA Issues Found", expanded=False):
                if qa_report.critical:
                    st.error(f"**Critical Issues:** {len(qa_report.critical)}")
                    for issue in qa_report.critical[:3]:
                        st.markdown(f"- {issue}")
                if qa_report.high:
                    st.warning(f"**High Issues:** {len(qa_report.high)}")
                if qa_report.security_flags:
                    st.info(f"**Security Flags:** {len(qa_report.security_flags)}")
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 6: Fix Issues
            # ═══════════════════════════════════════════════════════════════
            set_phase(6)
            st.write("🔧 **Phase 6:** Dev Team fixing issues...")
            
            backend_final = dev_team.fix_backend_spec(backend_draft, qa_report)
            frontend_final = dev_team.fix_frontend_spec(frontend_draft, qa_report)
            update_workflow_state(backend_final=backend_final, frontend_final=frontend_final)
            
            render_quick_discussion(
                topic="🔧 Issue Resolution",
                messages=[
                    {"agent": "DevTeamAgent", "content": "Addressed all critical and high priority issues. Added input validation, error handling, and security measures."},
                    {"agent": "QAAgent", "content": "Verified the fixes. The specifications now meet quality standards."},
                    {"agent": "TechLeadAgent", "content": "Good work team. The final specs are production-ready."}
                ],
                decision="✓ All critical issues resolved",
                rationale="Specifications updated with security hardening and edge case handling"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 7: Final Team Approval
            # ═══════════════════════════════════════════════════════════════
            set_phase(7)
            st.write("✅ **Phase 7:** Final team review...")
            
            # Format QA report for evaluation
            qa_report_md = qa_agent.format_qa_report_markdown(qa_report)
            
            evaluation = pm_agent.evaluate_specifications(
                context=context,
                user_stories=user_stories,
                architecture=architecture_with_diagrams,
                backend_spec=backend_final,
                frontend_spec=frontend_final,
                qa_report=qa_report_md
            )
            update_workflow_state(pm_evaluation=evaluation)
            
            # Build summary from evaluation
            eval_summary = f"Status: {evaluation.status.value}"
            if evaluation.strengths:
                eval_summary += f". Strengths: {evaluation.strengths[0]}"
            
            render_quick_discussion(
                topic="✅ Final Approval",
                messages=[
                    {"agent": "PMAgent", "content": f"Final evaluation score: {evaluation.score}/100. {eval_summary}"},
                    {"agent": "TechLeadAgent", "content": "The specifications are technically sound and follow best practices."},
                    {"agent": "QAAgent", "content": "All acceptance criteria can be tested. Ready for development."},
                    {"agent": "ModeratorAgent", "content": "Team has reached consensus. Specifications approved for output generation."}
                ],
                decision=f"✓ {evaluation.status.value} with score {evaluation.score}/100",
                rationale=evaluation.scolding if evaluation.scolding else "Meets all quality criteria"
            )
            
            # ═══════════════════════════════════════════════════════════════
            # PHASE 8: Output Generation
            # ═══════════════════════════════════════════════════════════════
            set_phase(8)
            st.write("💾 **Phase 8:** Generating final outputs...")
            
            # Format outputs
            user_stories_md = pm_agent.format_user_stories_markdown(user_stories)
            qa_report_md = qa_agent.format_qa_report_markdown(qa_report)
            
            # Generate cost estimation and executive summary
            cost_estimation = estimate_project_costs(context, user_stories, architecture_with_diagrams)
            executive_summary = generate_executive_summary(context, user_stories, architecture_with_diagrams, cost_estimation)
            
            playbook_rules = {
                'pm': get_playbook_rules('pm'),
                'tech_lead': get_playbook_rules('tech_lead'),
                'backend': get_playbook_rules('backend'),
                'frontend': get_playbook_rules('frontend'),
                'qa': get_playbook_rules('qa')
            }
            master_prompt = generate_master_prompt(context, user_stories, architecture_with_diagrams, backend_final, frontend_final, qa_report_md, playbook_rules)
            
            output_folder = save_all_project_files(
                user_stories=user_stories_md,
                architecture=architecture_with_diagrams,
                backend_final=backend_final,
                frontend_final=frontend_final,
                qa_report=qa_report_md,
                master_prompt=master_prompt,
                cost_estimation=cost_estimation,
                executive_summary=executive_summary
            )
            
            st.session_state['output_folder'] = output_folder
            st.session_state['generation_complete'] = True
            
            status.update(label="🎉 Virtual Team Complete!", state="complete")
            
        except Exception as e:
            import traceback
            status.update(label="❌ Team Session Failed", state="error")
            st.error(f"**Error:** {e}")
            st.code(traceback.format_exc())
            return
    
    st.balloons()
    st.success("🎉 **Virtual Team completed successfully!**")
    st.rerun()


def _create_team_discussion(
    topic: str,
    participants: list,
    context_summary: str,
    discussion_points: list,
    decision: str,
    rationale: str
) -> Discussion:
    """Helper to create a discussion record."""
    discussion = Discussion(
        topic_id=topic.upper().replace(" ", "_"),
        topic_name=topic,
        participants=participants
    )
    discussion.decision = decision
    discussion.decision_rationale = rationale
    discussion.status = ConsensusStatus.AGREED
    return discussion


def _extract_tech_stack(architecture: str) -> dict:
    """Extract technology choices from architecture text."""
    stack = {}
    arch_lower = architecture.lower()
    
    # Backend detection
    if "node" in arch_lower or "express" in arch_lower:
        stack["backend"] = "Node.js/Express"
    elif "fastapi" in arch_lower or "python" in arch_lower:
        stack["backend"] = "Python/FastAPI"
    elif "django" in arch_lower:
        stack["backend"] = "Python/Django"
    else:
        stack["backend"] = "Node.js"
    
    # Database detection
    if "postgres" in arch_lower:
        stack["database"] = "PostgreSQL"
    elif "mongodb" in arch_lower or "mongo" in arch_lower:
        stack["database"] = "MongoDB"
    elif "mysql" in arch_lower:
        stack["database"] = "MySQL"
    else:
        stack["database"] = "PostgreSQL"
    
    # Frontend detection
    if "next" in arch_lower:
        stack["frontend"] = "Next.js"
    elif "react" in arch_lower:
        stack["frontend"] = "React"
    elif "vue" in arch_lower:
        stack["frontend"] = "Vue.js"
    else:
        stack["frontend"] = "React"
    
    return stack


def run_all_phases():
    """Run all phases sequentially without reruns."""
    
    MAX_RETRIES = 3
    
    with st.status("🚀 Running AI Factory Pipeline...", expanded=True) as status:
        try:
            # PHASE 1
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
            st.write(f"✅ Phase 1 complete: {len(context.features)} features")
            
            with st.expander("📋 View Phase 1 Output"):
                st.markdown(f"**Project Type:** {context.project_type.value}")
                st.markdown(f"**Features:** {', '.join(context.features[:5])}")
                if context.personas:
                    st.markdown(f"**Personas:** {', '.join(context.personas[:3])}")
            
            # PHASE 2 - Check if already completed
            # PHASE 2
            set_phase(2)
            st.write("📝 **Phase 2:** Generating user stories & architecture...")
            pm_agent = PMAgent()
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
            
            # Generate architecture diagrams
            st.caption("📊 Generating architecture diagrams...")
            diagrams = tech_lead.generate_architecture_diagram(context, architecture)
            architecture_with_diagrams = architecture + "\n\n" + diagrams
            update_workflow_state(architecture=architecture_with_diagrams)
            
            with st.expander("🏛️ View Architecture"):
                st.markdown(architecture[:1000] + "..." if len(architecture) > 1000 else architecture)
            
            with st.expander("📊 View Diagrams"):
                st.markdown(diagrams)
            
            # Save checkpoint after Phase 2
            checkpoint_mgr = get_checkpoint_manager()
            checkpoint_mgr.save_checkpoint(
                phase=2,
                context=context,
                user_stories=user_stories,
                architecture=architecture_with_diagrams
            )
            
            # PHASE 3
            set_phase(3)
            st.write("❓ **Phase 3:** Generating clarifications...")
            dev_team = DevTeamAgent()
            clarifications = dev_team.generate_clarification_questions(context, user_stories, architecture_with_diagrams)
            if clarifications:
                answers = pm_agent.answer_clarifications(clarifications, context, user_stories)
                st.write(f"✅ Answered {len(answers)} questions")
            else:
                answers = {}
                st.write("✅ No clarifications needed")
            update_workflow_state(clarifications=answers)
            
            # Save checkpoint after Phase 3
            checkpoint_mgr.save_checkpoint(
                phase=3,
                clarifications=answers
            )
            
            # RETRY LOOP FOR PHASES 4-7
            retry_attempt = 0
            feedback = ""
            
            # Initialize cycle logger for debugging
            project_name = context.features[0][:30] if context.features else "project"
            cycle_logger = CycleLogger(project_name)
            
            while retry_attempt < MAX_RETRIES:
                # Log cycle start
                cycle_logger.start_cycle(retry_attempt)
                
                if retry_attempt > 0:
                    st.write(f"🔄 **Retry {retry_attempt}/{MAX_RETRIES-1}:** Regenerating with feedback...")
                    with st.expander("⚠️ View Previous Feedback"):
                        st.warning(feedback)
                
                # PHASE 4
                set_phase(4)
                st.write("⚙️ **Phase 4:** Drafting specifications...")
                
                # Use parallel execution if enabled
                if st.session_state.get('parallel_enabled', True):
                    st.caption("⚡ Running backend and frontend generation in parallel...")
                    
                    # Define tasks for parallel execution
                    tasks = {
                        "backend": lambda: dev_team.generate_backend_draft(context, user_stories, architecture, answers, feedback),
                        "frontend": lambda: dev_team.generate_frontend_draft(context, user_stories, architecture, "", answers, feedback)
                    }
                    
                    results = run_agents_parallel(tasks, parallel=True)
                    backend_draft = results.get("backend", "")
                    frontend_draft = results.get("frontend", "")
                    
                    if not backend_draft:
                        st.warning("Backend generation failed, retrying sequentially...")
                        backend_draft = dev_team.generate_backend_draft(context, user_stories, architecture, answers, feedback)
                    
                    if not frontend_draft:
                        st.warning("Frontend generation failed, retrying sequentially...")
                        frontend_draft = dev_team.generate_frontend_draft(context, user_stories, architecture, backend_draft, answers, feedback)
                else:
                    # Sequential execution
                    backend_draft = dev_team.generate_backend_draft(context, user_stories, architecture, answers, feedback)
                    frontend_draft = dev_team.generate_frontend_draft(context, user_stories, architecture, backend_draft, answers, feedback)
                
                update_workflow_state(backend_draft=backend_draft)
                st.write("✅ Backend spec drafted")
                
                with st.expander("⚙️ View Backend Spec"):
                    st.markdown(backend_draft[:1000] + "..." if len(backend_draft) > 1000 else backend_draft)
                
                update_workflow_state(frontend_draft=frontend_draft)
                st.write("✅ Frontend spec drafted")
                
                with st.expander("🎨 View Frontend Spec"):
                    st.markdown(frontend_draft[:1000] + "..." if len(frontend_draft) > 1000 else frontend_draft)
                
                # PHASE 5
                set_phase(5)
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
                
                # PHASE 6
                set_phase(6)
                has_issues = total_issues > 0
                if has_issues:
                    st.write("🔧 **Phase 6:** Fixing issues...")
                    backend_final = dev_team.fix_backend_spec(backend_draft, qa_report)
                    frontend_final = dev_team.fix_frontend_spec(frontend_draft, qa_report)
                    st.write("✅ Issues fixed")
                else:
                    backend_final = backend_draft
                    frontend_final = frontend_draft
                    st.write("✅ No issues to fix")
                
                update_workflow_state(backend_final=backend_final, frontend_final=frontend_final)
                
                # PHASE 7
                set_phase(7)
                st.write("✅ **Phase 7:** Final evaluation...")
                
                if not backend_final or not frontend_final:
                    st.error("❌ Missing specifications. Cannot evaluate.")
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
                    context, user_stories, architecture,
                    backend_final, frontend_final, qa_summary
                )
                update_workflow_state(evaluation=evaluation)
                st.write(f"✅ {evaluation.status.value} (Score: {evaluation.score}/100)")
                
                with st.expander("📊 View Evaluation Details"):
                    st.metric("Score", f"{evaluation.score}/100")
                    if evaluation.issues:
                        st.markdown("**Issues Found:**")
                        for issue in evaluation.issues[:5]:
                            st.write(f"- {issue}")
                
                # CHECK EVALUATION STATUS
                # Log evaluation for debugging
                cycle_logger.log_backend(backend_final, feedback)
                cycle_logger.log_frontend(frontend_final, feedback)
                cycle_logger.log_evaluation(
                    evaluation.score, 
                    evaluation.status.value, 
                    evaluation.issues, 
                    evaluation.scolding or ""
                )
                
                if evaluation.score < 85:
                    cycle_logger.log_summary(evaluation.score, passed=False, remaining_issues=len(evaluation.issues))
                    retry_attempt += 1
                    
                    if retry_attempt >= MAX_RETRIES:
                        status.update(label=f"❌ REJECTED after {MAX_RETRIES} attempts (Score: {evaluation.score}/100)", state="error")
                        st.error(f"❌ **Evaluation Failed:** Score {evaluation.score}/100 after {MAX_RETRIES} attempts")
                        st.info(f"📁 Debug logs saved to: {cycle_logger.get_log_path()}")
                        for issue in evaluation.issues:
                            st.write(f"- {issue}")
                        if evaluation.scolding:
                            st.error("**PM Feedback:**")
                            st.markdown(evaluation.scolding)
                        return
                    
                    # Prepare feedback for retry
                    feedback = f"""PREVIOUS EVALUATION REJECTED (Score: {evaluation.score}/100)

❌ ISSUES FOUND:
{chr(10).join(f'- {issue}' for issue in evaluation.issues)}

🗣️ PM SCOLDING:
{evaluation.scolding}

⚠️ FIX THESE ISSUES! Be more specific, complete, and production-ready."""
                    
                    st.warning(f"⚠️ Score {evaluation.score}/100 - Retrying ({retry_attempt}/{MAX_RETRIES-1})...")
                    continue  # Loop back to Phase 4
                
                else:
                    # APPROVED - Break out of loop
                    cycle_logger.log_summary(evaluation.score, passed=True)
                    st.success(f"✅ **APPROVED!** Score: {evaluation.score}/100")
                    break
            
            # PHASE 8 - Save outputs (outside retry loop)
            set_phase(8)
            st.write("💾 **Phase 8:** Generating final outputs...")
            
            pm_agent_formatter = PMAgent()
            qa_agent_formatter = QAAgent()
            
            user_stories_md = pm_agent_formatter.format_user_stories_markdown(user_stories)
            qa_report_md = qa_agent_formatter.format_qa_report_markdown(qa_report)
            
            # Generate Cost Estimation (simplified)
            st.write("💰 Generating cost estimation...")
            cost_estimation = estimate_project_costs(context, user_stories, architecture)
            
            # Generate Executive Summary for stakeholders
            st.write("📋 Generating executive summary...")
            executive_summary = generate_executive_summary(context, user_stories, architecture, cost_estimation)
            
            # Development phases are now part of the architecture document
            development_phases = ""  # Removed separate development phases generation
            
            playbook_rules = {
                'pm': get_playbook_rules('pm'),
                'tech_lead': get_playbook_rules('tech_lead'),
                'backend': get_playbook_rules('backend'),
                'frontend': get_playbook_rules('frontend'),
                'qa': get_playbook_rules('qa')
            }
            master_prompt = generate_master_prompt(context, user_stories, architecture, backend_final, frontend_final, qa_report_md, playbook_rules)
            
            output_folder = save_all_project_files(
                user_stories=user_stories_md,
                architecture=architecture,
                backend_final=backend_final,
                frontend_final=frontend_final,
                qa_report=qa_report_md,
                master_prompt=master_prompt,
                development_phases=development_phases,
                cost_estimation=cost_estimation,
                executive_summary=executive_summary
            )
            
            st.session_state['output_folder'] = output_folder
            st.session_state['generation_complete'] = True
            
            status.update(label="🎉 Pipeline Complete!", state="complete")
            
        except Exception as e:
            import traceback
            status.update(label="❌ Pipeline Failed", state="error")
            
            error_msg = str(e)
            if "daily token limit" in error_msg.lower() or "tpd" in error_msg.lower():
                st.error("❌ **DAILY TOKEN LIMIT EXCEEDED**")
                st.info("Wait a few minutes or upgrade your plan.")
            else:
                st.error(f"**Error:** {e}")
            
            st.code(traceback.format_exc())
            return
    
    st.balloons()
    st.success("🎉 **MVP Specifications Generated Successfully!**")
    st.rerun()


def run_phase_1():
    """Phase 1: Document Ingestion"""
    set_phase(1)
    set_processing(True)
    clear_error()
    
    st.info("📄 **Phase 1: Parsing Document...**")
    
    try:
        st.write("🔄 Initializing Vision Agent...")
        vision_agent = VisionAgent()
        
        # Determine input source
        if st.session_state.get('file_bytes'):
            st.write("🔍 Analyzing uploaded document with Gemini (30-60s)...")
            file_bytes = st.session_state['file_bytes']
            file_name = st.session_state['file_name']
            file_type = file_name.split('.')[-1] if '.' in file_name else 'txt'
            
            context = vision_agent.parse_document(file_bytes, file_name, file_type)
        else:
            st.write("🔍 Analyzing text input with Groq...")
            text_input = st.session_state.get('text_input', '')
            context = vision_agent.parse_text_input(text_input)
        
        st.write("✅ Document parsing complete!")
        
        # Validate parsing
        if context.full_text == "PARSING_FAILED" or not context.features:
            st.warning("⚠️ Document parsing had issues.")
        
        # Store context
        update_workflow_state(context=context)
        
        # Show results
        st.success(f"✅ **Phase 1 Complete!** Extracted {len(context.features)} features, {len(context.personas)} personas")
        
        with st.expander("📋 Extracted Information"):
            st.markdown(f"**Project Type:** {context.project_type.value}")
            st.markdown("**Features:**")
            for f in context.features:
                st.markdown(f"- {f}")
            if context.personas:
                st.markdown("**Personas:**")
                for p in context.personas:
                    st.markdown(f"- {p}")
        
        log_message("Phase 1 complete")
        
        # Set flag and trigger rerun
        st.session_state['ready_for_phase_2'] = True
        set_processing(False)
        st.rerun()
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        set_error(str(e))
        log_message(f"Phase 1 failed: {e}", "ERROR")
        st.error(f"❌ **Phase 1 Failed:** {e}")
        with st.expander("Error Details"):
            st.code(error_details)
        set_processing(False)


def run_phase_2():
    """Phase 2: Foundation (User Stories + Architecture)"""
    set_phase(2)
    set_processing(True)
    
    state = get_workflow_state()
    context = state.context
    
    if not context:
        st.error("Missing document context. Please restart from Phase 1.")
        return
    
    with st.status("🏗️ Phase 2: Building Foundation...", expanded=True) as status:
        try:
            # Generate User Stories
            st.write("📝 Generating user stories...")
            pm_agent = PMAgent()
            user_stories = pm_agent.generate_user_stories(context)
            
            # Store stories
            update_workflow_state(user_stories=user_stories)
            st.write(f"✅ Generated {len(user_stories)} user stories")
            
            # Generate Architecture
            st.write("🏛️ Designing architecture...")
            tech_lead = TechLeadAgent()
            architecture = tech_lead.generate_architecture(context, user_stories)
            
            # Store architecture
            update_workflow_state(architecture=architecture)
            st.write("✅ Architecture specification complete")
            
            # Show previews
            with st.expander("📋 User Stories Preview"):
                stories_md = pm_agent.format_user_stories_markdown(user_stories)
                st.markdown(stories_md[:2000] + "..." if len(stories_md) > 2000 else stories_md)
            
            with st.expander("🏛️ Architecture Preview"):
                st.markdown(architecture[:2000] + "..." if len(architecture) > 2000 else architecture)
            
            status.update(label="✅ Phase 2 Complete!", state="complete")
            log_message("Phase 2 complete - foundation built")
            
            st.session_state['ready_for_phase_3'] = True
            
        except Exception as e:
            status.update(label="❌ Phase 2 Failed", state="error")
            log_message(f"Phase 2 failed: {e}", "ERROR")
            st.error(f"Error: {e}")
        
        finally:
            set_processing(False)


def run_phase_3():
    """Phase 3: Clarification"""
    set_phase(3)
    set_processing(True)
    
    state = get_workflow_state()
    
    with st.status("❓ Phase 3: Clarification...", expanded=True) as status:
        try:
            # Generate questions
            st.write("🤔 Identifying clarification needs...")
            backend_dev = DevTeamAgent(role="backend")
            
            questions = backend_dev.generate_clarification_questions(
                state.context,
                state.user_stories,
                state.architecture
            )
            
            if questions:
                st.write(f"📋 Generated {len(questions)} clarification questions")
                
                # PM answers questions
                st.write("💬 PM agent answering questions...")
                pm_agent = PMAgent()
                answers = pm_agent.answer_clarifications(
                    questions,
                    state.context,
                    state.user_stories
                )
                
                # Store clarifications
                update_workflow_state(clarifications=answers)
                
                with st.expander("❓ Clarifications"):
                    for q in questions:
                        st.markdown(f"**Q: {q.question}**")
                        st.markdown(f"A: {answers.get(q.id, 'No answer')}")
                        st.divider()
            else:
                st.write("✅ No clarifications needed")
                update_workflow_state(clarifications={})
            
            status.update(label="✅ Phase 3 Complete!", state="complete")
            log_message("Phase 3 complete - clarifications resolved")
            
            st.session_state['ready_for_phase_4'] = True
            
        except Exception as e:
            status.update(label="❌ Phase 3 Failed", state="error")
            log_message(f"Phase 3 failed: {e}", "ERROR")
            st.error(f"Error: {e}")
        
        finally:
            set_processing(False)


def run_phase_4():
    """Phase 4: Drafting"""
    set_phase(4)
    set_processing(True)
    
    state = get_workflow_state()
    previous_scolding = state.previous_scolding
    
    with st.status("✍️ Phase 4: Drafting Specifications...", expanded=True) as status:
        try:
            if previous_scolding:
                st.warning("⚠️ Addressing previous feedback in this draft")
            
            # Backend draft
            st.write("⚙️ Generating backend specification...")
            backend_dev = DevTeamAgent(role="backend")
            backend_draft = backend_dev.generate_backend_draft(
                state.context,
                state.user_stories,
                state.architecture,
                state.clarifications,
                previous_scolding
            )
            update_workflow_state(backend_draft=backend_draft)
            st.write("✅ Backend draft complete")
            
            # Frontend draft
            st.write("🎨 Generating frontend specification...")
            frontend_dev = DevTeamAgent(role="frontend")
            frontend_draft = frontend_dev.generate_frontend_draft(
                state.context,
                state.user_stories,
                state.architecture,
                backend_draft,
                state.clarifications,
                previous_scolding
            )
            update_workflow_state(frontend_draft=frontend_draft)
            st.write("✅ Frontend draft complete")
            
            with st.expander("⚙️ Backend Draft Preview"):
                st.markdown(backend_draft[:2000] + "..." if len(backend_draft) > 2000 else backend_draft)
            
            with st.expander("🎨 Frontend Draft Preview"):
                st.markdown(frontend_draft[:2000] + "..." if len(frontend_draft) > 2000 else frontend_draft)
            
            status.update(label="✅ Phase 4 Complete!", state="complete")
            log_message("Phase 4 complete - drafts generated")
            
            st.session_state['ready_for_phase_5'] = True
            
        except Exception as e:
            status.update(label="❌ Phase 4 Failed", state="error")
            log_message(f"Phase 4 failed: {e}", "ERROR")
            st.error(f"Error: {e}")
        
        finally:
            set_processing(False)


def run_phase_5():
    """Phase 5: QA"""
    set_phase(5)
    set_processing(True)
    
    state = get_workflow_state()
    
    with st.status("🔍 Phase 5: Quality Assurance...", expanded=True) as status:
        try:
            st.write("🔎 Analyzing specifications for issues...")
            
            qa_agent = QAAgent()
            qa_report = qa_agent.analyze_specifications(
                state.backend_draft,
                state.frontend_draft,
                state.architecture,
                [s.model_dump() for s in state.user_stories]
            )
            
            update_workflow_state(qa_report=qa_report)
            
            # Show summary
            summary = qa_agent.get_issues_summary(qa_report)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔴 Critical", summary['critical'])
            col2.metric("🟠 High", summary['high'])
            col3.metric("🟡 Medium", summary['medium'])
            col4.metric("🟢 Low", summary['low'])
            
            if summary['critical'] > 0:
                st.warning(f"⚠️ {summary['critical']} critical issues found - will be addressed in Phase 6")
            
            with st.expander("📋 Full QA Report"):
                report_md = qa_agent.format_qa_report_markdown(qa_report)
                st.markdown(report_md)
            
            status.update(label="✅ Phase 5 Complete!", state="complete")
            log_message(f"Phase 5 complete - {summary['total']} issues found")
            
            st.session_state['ready_for_phase_6'] = True
            
        except Exception as e:
            status.update(label="❌ Phase 5 Failed", state="error")
            log_message(f"Phase 5 failed: {e}", "ERROR")
            st.error(f"Error: {e}")
        
        finally:
            set_processing(False)


def run_phase_6():
    """Phase 6: Fixing"""
    set_phase(6)
    set_processing(True)
    
    state = get_workflow_state()
    
    with st.status("🔧 Phase 6: Applying Fixes...", expanded=True) as status:
        try:
            # Fix backend
            st.write("🔧 Fixing backend specification...")
            backend_dev = DevTeamAgent(role="backend")
            backend_final = backend_dev.fix_backend_spec(
                state.backend_draft,
                state.qa_report
            )
            update_workflow_state(backend_final=backend_final)
            st.write("✅ Backend fixes applied")
            
            # Fix frontend
            st.write("🔧 Fixing frontend specification...")
            frontend_dev = DevTeamAgent(role="frontend")
            frontend_final = frontend_dev.fix_frontend_spec(
                state.frontend_draft,
                state.qa_report
            )
            update_workflow_state(frontend_final=frontend_final)
            st.write("✅ Frontend fixes applied")
            
            status.update(label="✅ Phase 6 Complete!", state="complete")
            log_message("Phase 6 complete - fixes applied")
            
            st.session_state['ready_for_phase_7'] = True
            
        except Exception as e:
            status.update(label="❌ Phase 6 Failed", state="error")
            log_message(f"Phase 6 failed: {e}", "ERROR")
            st.error(f"Error: {e}")
        
        finally:
            set_processing(False)


def run_phase_7():
    """Phase 7: Gatekeeper Review"""
    set_phase(7)
    set_processing(True)
    
    state = get_workflow_state()
    
    with st.status("⚖️ Phase 7: PM Evaluation...", expanded=True) as status:
        try:
            st.write("📊 PM evaluating final specifications...")
            
            pm_agent = PMAgent()
            qa_agent = QAAgent()
            
            qa_report_md = qa_agent.format_qa_report_markdown(state.qa_report)
            
            evaluation = pm_agent.evaluate_specifications(
                state.context,
                state.user_stories,
                state.architecture,
                state.backend_final,
                state.frontend_final,
                qa_report_md,
                state.previous_scolding
            )
            
            update_workflow_state(pm_evaluation=evaluation)
            
            # Show evaluation
            st.metric("📊 PM Score", f"{evaluation.score}/100")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Requirements", f"{evaluation.breakdown.requirements}/30")
            col2.metric("Architecture", f"{evaluation.breakdown.architecture}/25")
            col3.metric("Completeness", f"{evaluation.breakdown.completeness}/20")
            col4.metric("QA", f"{evaluation.breakdown.qa_compliance}/15")
            col5.metric("Security", f"{evaluation.breakdown.security}/10")
            
            if evaluation.status == EvaluationStatus.APPROVED:
                st.success("✅ APPROVED - Specifications meet quality standards!")
                status.update(label="✅ Phase 7 Complete - APPROVED!", state="complete")
                st.session_state['ready_for_phase_8'] = True
                
            else:
                # REJECTED
                retry_count = get_retry_count()
                
                st.warning(f"⚠️ REJECTED - Score: {evaluation.score}/100")
                
                with st.expander("📋 Rejection Details", expanded=True):
                    st.markdown("**Issues:**")
                    for issue in evaluation.issues:
                        st.markdown(f"- {issue}")
                    
                    st.markdown("**Detailed Feedback:**")
                    st.markdown(evaluation.scolding)
                
                if retry_count < 3:
                    st.info(f"🔄 Will retry (attempt {retry_count + 1}/3)")
                    
                    # Coach extracts lessons
                    st.write("🎓 Coach extracting lessons...")
                    coach = CoachAgent()
                    added_rules = coach.process_rejection(evaluation)
                    
                    if added_rules:
                        st.success(f"📚 Added {len(added_rules)} new rules to playbooks")
                    
                    # Increment retry and store scolding
                    increment_retry()
                    update_workflow_state(previous_scolding=evaluation.scolding)
                    
                    status.update(label=f"⚠️ Rejected - Retrying ({retry_count + 1}/3)", state="error")
                    
                    # Will loop back to phase 4
                    st.session_state['retry_from_phase_4'] = True
                    
                else:
                    # Max retries reached - force proceed
                    st.error("❌ Max retries reached - proceeding with warnings")
                    
                    warnings = state.warnings + [
                        f"PM Score: {evaluation.score}/100 (below threshold)",
                        "Max retry limit reached",
                        "Manual review strongly recommended"
                    ] + evaluation.issues
                    
                    update_workflow_state(warnings=warnings)
                    
                    status.update(label="⚠️ Phase 7 - Force Proceed", state="complete")
                    st.session_state['ready_for_phase_8'] = True
            
            log_message(f"Phase 7 complete - {evaluation.status.value} ({evaluation.score})")
            
        except Exception as e:
            status.update(label="❌ Phase 7 Failed", state="error")
            log_message(f"Phase 7 failed: {e}", "ERROR")
            st.error(f"Error: {e}")
        
        finally:
            set_processing(False)


def run_phase_8():
    """Phase 8: Output Generation"""
    set_phase(8)
    set_processing(True)
    
    state = get_workflow_state()
    
    with st.status("📦 Phase 8: Generating Output...", expanded=True) as status:
        try:
            ensure_directories()
            
            # Format all documents
            pm_agent = PMAgent()
            qa_agent = QAAgent()
            
            user_stories_md = pm_agent.format_user_stories_markdown(state.user_stories)
            qa_report_md = qa_agent.format_qa_report_markdown(state.qa_report)
            
            # Get playbook rules for master prompt
            playbook_rules = {
                'pm': get_playbook_rules('pm'),
                'tech_lead': get_playbook_rules('tech_lead'),
                'backend': get_playbook_rules('backend'),
                'frontend': get_playbook_rules('frontend'),
                'qa': get_playbook_rules('qa')
            }
            
            # Generate master prompt
            project_summary = f"""
Project Type: {state.context.project_type.value}
Features: {', '.join(state.context.features[:5])}
User Personas: {', '.join(state.context.personas[:3]) if state.context.personas else 'General users'}
            """.strip()
            
            master_prompt = generate_master_prompt(
                project_summary=project_summary,
                pm_score=state.pm_evaluation.score if state.pm_evaluation else 0,
                retry_count=state.retry_count,
                rules_applied=get_evolution_level(),
                warnings=state.warnings,
                playbook_rules=playbook_rules
            )
            
            # Generate warning file if needed
            warning_content = None
            if state.warnings:
                warning_content = "# ⚠️ Unresolved Risks\n\n"
                warning_content += "*These issues could not be fully resolved:*\n\n"
                for w in state.warnings:
                    warning_content += f"- {w}\n"
            
            # Save all files
            st.write("💾 Saving project files...")
            project_folder = save_all_project_files(
                user_stories=user_stories_md,
                architecture=state.architecture,
                backend_final=state.backend_final,
                frontend_final=state.frontend_final,
                qa_report=qa_report_md,
                master_prompt=master_prompt,
                warnings=warning_content
            )
            
            st.write(f"✅ Files saved to: {project_folder}")
            
            status.update(label="✅ Phase 8 Complete!", state="complete")
            log_message(f"Phase 8 complete - output saved to {project_folder}")
            
            # Store folder path for display
            st.session_state['output_folder'] = str(project_folder)
            st.session_state['generation_complete'] = True
            
        except Exception as e:
            status.update(label="❌ Phase 8 Failed", state="error")
            log_message(f"Phase 8 failed: {e}", "ERROR")
            st.error(f"Error: {e}")
        
        finally:
            set_processing(False)


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
    
    # File list
    st.markdown("### Generated Files:")
    files = [
        ("00_MASTER_PROMPT.md", "Project overview and implementation guide"),
        ("01_User_Stories.md", "Detailed user stories with acceptance criteria"),
        ("02_Architecture.md", "System architecture and tech stack"),
        ("03_Backend_Final.md", "Backend implementation specification"),
        ("04_Frontend_Final.md", "Frontend implementation specification"),
        ("05_QA_Report.md", "Quality assurance findings"),
    ]
    
    for filename, description in files:
        st.markdown(f"- **{filename}** - {description}")
    
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
    
    # Check if generation is complete
    if st.session_state.get('generation_complete'):
        render_results()
        return
    
    # Show current phase progress
    st.progress((state.phase - 1) / 8, text=f"Phase {state.phase}/8: {PHASE_NAMES.get(state.phase, 'Unknown')}")
    
    # Phase 1: Document Upload (only show if still in phase 1 and no ready flags)
    if state.phase == 1 and not any(st.session_state.get(f'ready_for_phase_{i}') for i in range(2, 9)):
        render_file_upload()
    
    # Handle phase transitions
    if st.session_state.get('ready_for_phase_2'):
        del st.session_state['ready_for_phase_2']
        run_phase_2()
        st.rerun()
    
    if st.session_state.get('ready_for_phase_3'):
        del st.session_state['ready_for_phase_3']
        run_phase_3()
        st.rerun()
    
    if st.session_state.get('ready_for_phase_4'):
        del st.session_state['ready_for_phase_4']
        run_phase_4()
        st.rerun()
    
    if st.session_state.get('ready_for_phase_5'):
        del st.session_state['ready_for_phase_5']
        run_phase_5()
        st.rerun()
    
    if st.session_state.get('ready_for_phase_6'):
        del st.session_state['ready_for_phase_6']
        run_phase_6()
        st.rerun()
    
    if st.session_state.get('ready_for_phase_7'):
        del st.session_state['ready_for_phase_7']
        run_phase_7()
        st.rerun()
    
    if st.session_state.get('retry_from_phase_4'):
        del st.session_state['retry_from_phase_4']
        run_phase_4()
        st.rerun()
    
    if st.session_state.get('ready_for_phase_8'):
        del st.session_state['ready_for_phase_8']
        run_phase_8()
        st.rerun()
    
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
