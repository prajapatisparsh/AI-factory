"""
File I/O operations for the AI Factory.
Handles playbook reading/writing and project output generation.
"""

import os
from datetime import datetime
from typing import Optional, List
from pathlib import Path


# Base directories
BASE_DIR = Path(__file__).parent.parent.parent
MEMORY_DIR = BASE_DIR / "memory"
PROJECTS_DIR = BASE_DIR / "projects"


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    MEMORY_DIR.mkdir(exist_ok=True)
    PROJECTS_DIR.mkdir(exist_ok=True)


def load_playbook(name: str) -> str:
    """
    Load a playbook file from memory directory.
    
    Args:
        name: Playbook name (e.g., 'pm', 'tech_lead', 'backend', 'frontend', 'qa')
    
    Returns:
        Playbook content as string, or empty string if not found.
    """
    ensure_directories()
    filename = f"{name}_playbook.md"
    filepath = MEMORY_DIR / filename
    
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        return ""
    except Exception as e:
        print(f"Error loading playbook {name}: {e}")
        return ""


def save_playbook(name: str, content: str) -> bool:
    """
    Save content to a playbook file.
    
    Args:
        name: Playbook name
        content: Full playbook content
    
    Returns:
        Success status
    """
    ensure_directories()
    filename = f"{name}_playbook.md"
    filepath = MEMORY_DIR / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving playbook {name}: {e}")
        return False


def append_rule_to_playbook(name: str, rule: str) -> bool:
    """
    Append a single rule to a playbook.
    
    Args:
        name: Playbook name
        rule: Rule to append (will be prefixed with '- ')
    
    Returns:
        Success status
    """
    current_content = load_playbook(name)
    
    # Ensure rule has proper format
    formatted_rule = rule if rule.startswith('-') else f"- {rule}"
    
    # Add to Learned Rules section
    if "## Learned Rules" in current_content:
        new_content = current_content.rstrip() + f"\n{formatted_rule}\n"
    else:
        new_content = current_content.rstrip() + f"\n\n## Learned Rules\n{formatted_rule}\n"
    
    return save_playbook(name, new_content)


def get_playbook_rules(name: str) -> List[str]:
    """
    Get all rules from a playbook as a list.
    
    Args:
        name: Playbook name
    
    Returns:
        List of rule strings (with [BASELINE] tags removed)
    """
    content = load_playbook(name)
    rules = []
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('-'):
            # Remove the leading '- ' and get the rule text
            rule_text = line[1:].strip()
            if rule_text:
                # Remove [BASELINE] and [LEARNED] tags for clean output
                rule_text = rule_text.replace('[BASELINE]', '').replace('[LEARNED]', '').strip()
                if rule_text:
                    rules.append(rule_text)
    
    return rules


def count_playbook_rules(name: str) -> int:
    """Count number of rules in a playbook."""
    return len(get_playbook_rules(name))


def archive_old_rules(name: str, max_rules: int = 100) -> bool:
    """
    Archive oldest learned rules when playbook exceeds max_rules.
    Baseline rules are never archived.
    
    Args:
        name: Playbook name
        max_rules: Maximum rules allowed
    
    Returns:
        Success status
    """
    content = load_playbook(name)
    lines = content.split('\n')
    
    baseline_rules = []
    learned_rules = []
    other_lines = []
    
    in_learned_section = False
    
    for line in lines:
        if "## Learned Rules" in line:
            in_learned_section = True
            other_lines.append(line)
        elif line.strip().startswith('-'):
            if '[BASELINE]' in line:
                baseline_rules.append(line)
            elif in_learned_section:
                learned_rules.append(line)
            else:
                baseline_rules.append(line)
        else:
            other_lines.append(line)
    
    # Check if archiving is needed
    total_rules = len(baseline_rules) + len(learned_rules)
    if total_rules <= max_rules:
        return True
    
    # Archive oldest learned rules
    rules_to_keep = max_rules - len(baseline_rules)
    if rules_to_keep < 0:
        rules_to_keep = 0
    
    # Keep most recent learned rules (assuming newer rules are at the end)
    kept_learned = learned_rules[-rules_to_keep:] if rules_to_keep > 0 else []
    archived_rules = learned_rules[:-rules_to_keep] if rules_to_keep > 0 else learned_rules
    
    # Save archived rules to separate file
    if archived_rules:
        archive_path = MEMORY_DIR / f"{name}_archive.md"
        archive_content = f"# Archived Rules - {datetime.now().isoformat()}\n\n"
        archive_content += '\n'.join(archived_rules) + '\n'
        
        try:
            # Append to existing archive
            mode = 'a' if archive_path.exists() else 'w'
            with open(archive_path, mode, encoding='utf-8') as f:
                f.write(archive_content)
        except Exception as e:
            print(f"Error archiving rules: {e}")
    
    # Rebuild playbook content
    new_content = []
    for line in other_lines:
        if "## Baseline Rules" in line or (not line.strip() and new_content and new_content[-1].strip() == ''):
            continue
        new_content.append(line)
    
    # Add baseline rules section
    if baseline_rules:
        new_content.append("\n## Baseline Rules")
        new_content.extend(baseline_rules)
    
    # Add learned rules section
    new_content.append("\n## Learned Rules")
    new_content.extend(kept_learned)
    
    return save_playbook(name, '\n'.join(new_content))


def create_project_folder(prefix: str = "MVP") -> Path:
    """
    Create a new project output folder with timestamp.
    
    Args:
        prefix: Folder name prefix
    
    Returns:
        Path to created folder
    """
    ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{prefix}_{timestamp}"
    folder_path = PROJECTS_DIR / folder_name
    folder_path.mkdir(exist_ok=True)
    return folder_path


def save_project_file(folder: Path, filename: str, content: str) -> Path:
    """
    Save a file to a project folder.
    
    Args:
        folder: Project folder path
        filename: Name of file to create
        content: File content
    
    Returns:
        Path to created file
    """
    filepath = folder / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath


def generate_master_prompt(
    context,
    user_stories,
    architecture: str,
    backend_final: str,
    frontend_final: str,
    qa_report: str,
    playbook_rules: dict
) -> str:
    """
    Generate the master prompt file content.
    
    Args:
        context: DocumentAnalysis object
        user_stories: List of user stories
        architecture: Architecture spec
        backend_final: Backend spec
        frontend_final: Frontend spec
        qa_report: QA report markdown
        playbook_rules: Dict of playbook name -> rules list
    
    Returns:
        Master prompt markdown content
    """
    # Build project summary
    project_type = context.project_type.value if hasattr(context, 'project_type') else "MVP"
    features = context.features if hasattr(context, 'features') else []
    story_count = len(user_stories) if user_stories else 0
    
    content = f"""# MVP Development Master Prompt

## Project Overview
**Type:** {project_type}
**Features:** {len(features)}
**User Stories:** {story_count}

## Implementation Sequence
1. Review user requirements: 01_User_Stories.md
2. Set up architecture: 02_Architecture.md
3. Implement backend: 03_Backend_Final.md
4. Implement frontend: 04_Frontend_Final.md
5. Test using checklist: 05_QA_Report.md
6. Review phases: 06_Development_Phases.md
7. Review costs: 07_Cost_Estimation.md

## Key Features
{chr(10).join(f'- {f}' for f in features[:10])}

## Active Best Practices

"""
    
    for playbook_name, rules in playbook_rules.items():
        content += f"### {playbook_name.replace('_', ' ').title()}\n"
        for rule in rules[:5]:  # Limit to 5 rules per playbook
            content += f"- {rule}\n"
        content += "\n"
    
    content += """---
*Use this document as your guide to implement the MVP. Start with architecture, then backend, then frontend.*
"""
    
    return content


def save_all_project_files(
    user_stories: str,
    architecture: str,
    backend_final: str,
    frontend_final: str,
    qa_report: str,
    master_prompt: str,
    warnings: Optional[str] = None,
    development_phases: Optional[str] = None,
    cost_estimation: Optional[str] = None,
    executive_summary: Optional[str] = None
) -> Path:
    """
    Save all project output files to a new project folder.
    
    Returns:
        Path to project folder
    """
    folder = create_project_folder()
    
    # Executive summary first - for stakeholders
    if executive_summary:
        save_project_file(folder, "00_EXECUTIVE_SUMMARY.md", executive_summary)
    
    save_project_file(folder, "01_MASTER_PROMPT.md", master_prompt)
    save_project_file(folder, "02_User_Stories.md", user_stories)
    save_project_file(folder, "03_Architecture.md", architecture)
    save_project_file(folder, "04_Backend_Final.md", backend_final)
    save_project_file(folder, "05_Frontend_Final.md", frontend_final)
    save_project_file(folder, "06_QA_Report.md", qa_report)
    
    if development_phases:
        save_project_file(folder, "07_Development_Phases.md", development_phases)
    
    if cost_estimation:
        save_project_file(folder, "08_Cost_Estimation.md", cost_estimation)
    
    if warnings:
        save_project_file(folder, "WARNING_UNRESOLVED_RISKS.md", warnings)
    
    return folder


def read_uploaded_file(file_bytes: bytes, filename: str) -> str:
    """
    Read content from uploaded file bytes.
    Handles text files directly, returns filename for binary files.
    
    Args:
        file_bytes: Raw file bytes
        filename: Original filename
    
    Returns:
        File content or indicator for binary files
    """
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    # Text files
    if extension in ['txt', 'md', 'json', 'csv']:
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_bytes.decode('latin-1')
            except:
                return f"[Binary file: {filename}]"
    
    # Binary files (PDF, images) - return indicator for vision processing
    elif extension in ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp']:
        return f"[BINARY:{extension.upper()}:{filename}]"
    
    else:
        return f"[Unknown file type: {filename}]"
