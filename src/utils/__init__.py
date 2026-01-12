"""Utility modules for AI Factory."""

from src.utils.state import (
    init_session_state,
    get_workflow_state,
    update_workflow_state,
    set_phase,
    increment_retry,
    reset_retry_count,
    get_retry_count,
    store_artifact,
    get_artifact,
    cache_tavily_result,
    get_cached_tavily,
    log_message,
    get_logs,
    clear_logs,
    set_processing,
    is_processing,
    set_error,
    get_error,
    clear_error,
    reset_session,
    validate_state_for_phase,
    get_phase_status,
    get_evolution_level,
    PHASE_NAMES
)

from src.utils.files import (
    load_playbook,
    save_playbook,
    append_rule_to_playbook,
    get_playbook_rules,
    count_playbook_rules,
    archive_old_rules,
    create_project_folder,
    save_project_file,
    generate_master_prompt,
    save_all_project_files,
    read_uploaded_file
)

from src.utils.fuzzy import (
    similarity_ratio,
    is_duplicate_rule,
    normalize_rule,
    find_most_similar,
    is_actionable_rule,
    is_generic_rule,
    validate_rule_quality,
    deduplicate_rules
)

__all__ = [
    # State management
    'init_session_state',
    'get_workflow_state',
    'update_workflow_state',
    'set_phase',
    'increment_retry',
    'reset_retry_count',
    'get_retry_count',
    'store_artifact',
    'get_artifact',
    'cache_tavily_result',
    'get_cached_tavily',
    'log_message',
    'get_logs',
    'clear_logs',
    'set_processing',
    'is_processing',
    'set_error',
    'get_error',
    'clear_error',
    'reset_session',
    'validate_state_for_phase',
    'get_phase_status',
    'get_evolution_level',
    'PHASE_NAMES',
    
    # File operations
    'load_playbook',
    'save_playbook',
    'append_rule_to_playbook',
    'get_playbook_rules',
    'count_playbook_rules',
    'archive_old_rules',
    'create_project_folder',
    'save_project_file',
    'generate_master_prompt',
    'save_all_project_files',
    'read_uploaded_file',
    
    # Fuzzy matching
    'similarity_ratio',
    'is_duplicate_rule',
    'normalize_rule',
    'find_most_similar',
    'is_actionable_rule',
    'is_generic_rule',
    'validate_rule_quality',
    'deduplicate_rules',
]
