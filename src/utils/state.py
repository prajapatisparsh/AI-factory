"""
Session state manager for Streamlit.
Handles state persistence, validation, and recovery.
"""

import streamlit as st
from typing import Any, Optional, Dict
from datetime import datetime
import json
import os

from src.schemas import WorkflowState, DocumentAnalysis, PMEvaluation, QAReport


# Phase names for UI display
PHASE_NAMES = {
    1: "Document Ingestion",
    2: "Foundation (Stories & Architecture)",
    3: "Clarification",
    4: "Drafting",
    5: "Quality Assurance",
    6: "Fixing",
    7: "Gatekeeper Review",
    8: "Output Generation"
}


def init_session_state() -> None:
    """Initialize session state with defaults if not exists."""
    defaults = {
        'workflow': WorkflowState().model_dump(),
        'uploaded_file': None,
        'file_bytes': None,
        'file_name': None,
        'logs': [],
        'processing': False,
        'error': None,
        'start_time': None,
        'phase_times': {},
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_workflow_state() -> WorkflowState:
    """Get current workflow state as Pydantic model."""
    init_session_state()
    try:
        return WorkflowState.model_validate(st.session_state.get('workflow', {}))
    except Exception as e:
        # State corruption - reset to defaults
        log_message(f"State corruption detected, resetting: {str(e)}", "ERROR")
        st.session_state['workflow'] = WorkflowState().model_dump()
        return WorkflowState()


def update_workflow_state(**kwargs) -> None:
    """Update workflow state with validation."""
    init_session_state()
    current = st.session_state.get('workflow', {})
    
    # Update with new values
    for key, value in kwargs.items():
        if hasattr(WorkflowState, key):
            # Convert Pydantic models to dict for storage
            if hasattr(value, 'model_dump'):
                current[key] = value.model_dump()
            else:
                current[key] = value
    
    # Validate the updated state
    try:
        validated = WorkflowState.model_validate(current)
        st.session_state['workflow'] = validated.model_dump()
    except Exception as e:
        log_message(f"State validation failed: {str(e)}", "ERROR")
        raise


def set_phase(phase: int) -> None:
    """Set current workflow phase with timing."""
    current_phase = get_workflow_state().phase
    
    # Record time for previous phase
    if st.session_state.get('start_time'):
        elapsed = (datetime.now() - st.session_state['start_time']).total_seconds()
        st.session_state['phase_times'][current_phase] = elapsed
    
    # Update phase
    update_workflow_state(phase=phase)
    st.session_state['start_time'] = datetime.now()
    log_message(f"Entered Phase {phase}: {PHASE_NAMES.get(phase, 'Unknown')}", "INFO")


def increment_retry() -> int:
    """Increment retry counter and return new value."""
    state = get_workflow_state()
    new_count = min(state.retry_count + 1, 3)
    update_workflow_state(retry_count=new_count)
    log_message(f"Retry count increased to {new_count}/3", "WARNING")
    return new_count


def reset_retry_count() -> None:
    """Reset retry counter to 0."""
    update_workflow_state(retry_count=0)


def get_retry_count() -> int:
    """Get current retry count."""
    return get_workflow_state().retry_count


def store_artifact(name: str, content: Any) -> None:
    """Store an artifact in workflow state."""
    state = get_workflow_state()
    artifacts = state.artifacts.copy()
    artifacts[name] = content
    update_workflow_state(artifacts=artifacts)
    log_message(f"Stored artifact: {name}", "DEBUG")


def get_artifact(name: str, default: Any = None) -> Any:
    """Get an artifact from workflow state."""
    state = get_workflow_state()
    return state.artifacts.get(name, default)


def cache_tavily_result(query: str, result: str) -> None:
    """Cache a Tavily API result."""
    state = get_workflow_state()
    cache = state.tavily_cache.copy()
    cache[query] = result
    update_workflow_state(tavily_cache=cache)


def get_cached_tavily(query: str) -> Optional[str]:
    """Get cached Tavily result if exists."""
    state = get_workflow_state()
    return state.tavily_cache.get(query)


def log_message(message: str, level: str = "INFO") -> None:
    """Add a log message to session state AND print to terminal."""
    import logging
    logger = logging.getLogger(__name__)
    
    # ALWAYS print to terminal for visibility
    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)
    
    # Also store in session state for UI display
    try:
        init_session_state()
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        st.session_state['logs'].append(log_entry)
        
        # Keep only last 100 logs to prevent memory bloat
        if len(st.session_state['logs']) > 100:
            st.session_state['logs'] = st.session_state['logs'][-100:]
    except Exception:
        # Outside Streamlit context - already printed above
        pass


def get_logs() -> list:
    """Get all log messages."""
    init_session_state()
    return st.session_state.get('logs', [])


def clear_logs() -> None:
    """Clear all log messages."""
    st.session_state['logs'] = []


def set_processing(is_processing: bool) -> None:
    """Set processing state."""
    st.session_state['processing'] = is_processing


def is_processing() -> bool:
    """Check if currently processing."""
    return st.session_state.get('processing', False)


def set_error(error: Optional[str]) -> None:
    """Set or clear error state."""
    st.session_state['error'] = error


def get_error() -> Optional[str]:
    """Get current error if any."""
    return st.session_state.get('error')


def clear_error() -> None:
    """Clear error state."""
    st.session_state['error'] = None


def reset_session() -> None:
    """Completely reset the session state."""
    keys_to_keep = []  # Could keep some keys if needed
    
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    
    init_session_state()
    log_message("Session reset complete", "INFO")


def validate_state_for_phase(target_phase: int) -> tuple[bool, str]:
    """
    Validate that state is ready for a target phase.
    Returns (is_valid, error_message)
    """
    state = get_workflow_state()
    
    # Phase-specific validation
    if target_phase == 2:
        if not state.context:
            return False, "Document context not available. Complete Phase 1 first."
    
    elif target_phase == 3:
        if not state.user_stories:
            return False, "User stories not generated. Complete Phase 2 first."
        if not state.architecture:
            return False, "Architecture not defined. Complete Phase 2 first."
    
    elif target_phase == 4:
        if not state.context:
            return False, "Document context lost. Restart from Phase 1."
    
    elif target_phase == 5:
        if not state.backend_draft:
            return False, "Backend draft not available. Complete Phase 4 first."
        if not state.frontend_draft:
            return False, "Frontend draft not available. Complete Phase 4 first."
    
    elif target_phase == 6:
        if not state.qa_report:
            return False, "QA report not available. Complete Phase 5 first."
    
    elif target_phase == 7:
        if not state.backend_final:
            return False, "Final backend spec not available. Complete Phase 6 first."
        if not state.frontend_final:
            return False, "Final frontend spec not available. Complete Phase 6 first."
    
    elif target_phase == 8:
        if not state.pm_evaluation:
            return False, "PM evaluation not available. Complete Phase 7 first."
    
    return True, ""


def get_phase_status(phase: int) -> str:
    """
    Get status icon for a phase.
    Returns: ✅ (complete), ⏳ (running), ⏸️ (pending), ⚠️ (warning)
    """
    current = get_workflow_state().phase
    
    if phase < current:
        return "✅"
    elif phase == current:
        return "⏳" if is_processing() else "▶️"
    else:
        return "⏸️"


def export_state_for_recovery() -> str:
    """Export current state as JSON for recovery."""
    state = get_workflow_state()
    return json.dumps(state.model_dump(), indent=2)


def import_state_for_recovery(json_str: str) -> bool:
    """Import state from JSON. Returns success status."""
    try:
        data = json.loads(json_str)
        validated = WorkflowState.model_validate(data)
        st.session_state['workflow'] = validated.model_dump()
        log_message("State recovered from backup", "INFO")
        return True
    except Exception as e:
        log_message(f"State recovery failed: {str(e)}", "ERROR")
        return False


def get_evolution_level() -> int:
    """Count total learned rules across all playbooks."""
    memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory')
    total_rules = 0
    
    playbook_files = [
        'pm_playbook.md',
        'tech_lead_playbook.md',
        'backend_playbook.md',
        'frontend_playbook.md',
        'qa_playbook.md'
    ]
    
    for filename in playbook_files:
        filepath = os.path.join(memory_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count lines starting with '-' (rules)
                    rules = [line for line in content.split('\n') if line.strip().startswith('-')]
                    total_rules += len(rules)
            except Exception:
                pass
    
    return total_rules
