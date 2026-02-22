"""
Coach Agent - Memory updater and lesson extractor.
Analyzes PM rejections to extract generic lessons and update playbooks.
"""

from typing import List, Tuple, Optional
from datetime import datetime
import re

from src.agents.base import BaseAgent
from src.schemas import PMEvaluation, LearnedRule, extract_json_array
from src.utils.files import (
    load_playbook, 
    append_rule_to_playbook, 
    get_playbook_rules,
    archive_old_rules,
    count_playbook_rules
)
from src.utils.fuzzy import (
    is_duplicate_rule, 
    validate_rule_quality,
    normalize_rule
)


class CoachAgent(BaseAgent):
    """
    Coach agent responsible for:
    - Extracting lessons from PM rejections
    - Updating appropriate playbooks
    - Ensuring rule quality and uniqueness
    - Preventing playbook bloat
    """
    
    MAX_RULES_PER_PLAYBOOK = 100
    SIMILARITY_THRESHOLD = 0.80
    
    def __init__(self):
        super().__init__(playbook_name=None)  # Coach doesn't have its own playbook
    
    def get_agent_name(self) -> str:
        return "CoachAgent"
    
    def process_rejection(self, evaluation: PMEvaluation) -> List[Tuple[str, str]]:
        """
        Process a PM rejection and extract lessons for playbooks.
        
        Args:
            evaluation: The PM evaluation that rejected the specs
        
        Returns:
            List of (playbook_name, rule) tuples that were added
        """
        self.log(f"Processing rejection (score: {evaluation.score})")
        
        if evaluation.status.value == "APPROVED":
            self.log("No rejection to process - specs were approved")
            return []
        
        # Extract lessons from the scolding
        lessons = self._extract_lessons(evaluation.scolding, evaluation.issues)
        
        if not lessons:
            self.log("No actionable lessons extracted from rejection")
            return []
        
        self.log(f"Extracted {len(lessons)} potential lessons")
        
        # Process each lesson
        added_rules = []
        for lesson in lessons:
            result = self._add_lesson_to_playbook(lesson)
            if result:
                added_rules.append(result)
        
        self.log(f"Added {len(added_rules)} new rules to playbooks")
        return added_rules
    
    def _extract_lessons(
        self, 
        scolding: str, 
        issues: List[str]
    ) -> List[LearnedRule]:
        """
        Extract generic, actionable lessons from rejection feedback.
        
        Args:
            scolding: Detailed feedback from PM
            issues: List of specific issues
        
        Returns:
            List of LearnedRule objects
        """
        system_prompt = """You are a coach extracting generic lessons from project feedback.

Extract 1-3 lessons that:
1. Are ACTIONABLE (contain Never/Always/Ensure/Check/Verify)
2. Are GENERIC (no project names, client names, specific features)
3. Are CONCISE (max 150 characters)
4. Explain WHY (include 'because', 'to prevent', 'ensures')

Map each lesson to the correct playbook:
- pm: Requirements, user stories, evaluation criteria
- tech_lead: Architecture, tech stack, database, API design
- backend: Server code, API implementation, data handling
- frontend: UI components, state, routing, user experience
- qa: Testing, security checks, quality criteria

Good examples:
- "[pm] Always require 2+ personas for user stories because single-persona design misses edge cases"
- "[backend] Never expose stack traces in API errors because they reveal system vulnerabilities"
- "[frontend] Ensure loading states on all async operations to prevent confusion"

Bad examples (DO NOT USE):
- "Fix the login" (too specific, not actionable)
- "Backend needs work" (no specific guidance)
- "The client's auth was wrong" (project-specific)"""

        combined_feedback = f"""Scolding:
{scolding}

Specific Issues:
{chr(10).join(f'- {issue}' for issue in issues)}"""

        user_prompt = f"""Extract generic lessons from this rejection feedback:

{combined_feedback}

Return JSON array of lessons:
[
    {{
        "date": "{datetime.now().strftime('%Y-%m-%d')}",
        "rule": "Always/Never/Ensure [action] because [reason]",
        "target_playbook": "pm|tech_lead|backend|frontend|qa"
    }}
]

Maximum 3 lessons. Each must be actionable, generic, and explain why."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=1000)
            
            # Parse response
            lessons = self._parse_lessons_response(response)
            return lessons
            
        except Exception as e:
            self.log(f"Lesson extraction failed: {e}", "ERROR")
            return []
    
    def _parse_lessons_response(self, response: str) -> List[LearnedRule]:
        """Parse LLM response into LearnedRule objects."""
        data = extract_json_array(response)
        if data:
            lessons = []
            for item in data[:3]:  # Max 3 lessons
                if isinstance(item, dict):
                    try:
                        rule = LearnedRule(
                            date=item.get('date', datetime.now().strftime('%Y-%m-%d')),
                            rule=item.get('rule', '')[:150],
                            target_playbook=item.get('target_playbook', 'pm')
                        )
                        lessons.append(rule)
                    except Exception:
                        continue
            return lessons

        return []
    
    def _add_lesson_to_playbook(
        self, 
        lesson: LearnedRule
    ) -> Optional[Tuple[str, str]]:
        """
        Add a lesson to the appropriate playbook if it passes quality checks.
        
        Args:
            lesson: The lesson to add
        
        Returns:
            Tuple of (playbook_name, rule) if added, None otherwise
        """
        playbook_name = lesson.target_playbook
        rule_text = lesson.rule
        
        # Validate playbook name
        valid_playbooks = ['pm', 'tech_lead', 'backend', 'frontend', 'qa']
        if playbook_name not in valid_playbooks:
            self.log(f"Invalid playbook name: {playbook_name}", "WARNING")
            playbook_name = 'pm'  # Default to PM playbook
        
        # Check rule quality
        is_valid, quality_issues = validate_rule_quality(rule_text)
        if quality_issues:
            self.log(f"Rule quality issues: {', '.join(quality_issues)}", "DEBUG")
            # Continue anyway - we want to learn even from imperfect rules
        
        # Get existing rules for deduplication
        existing_rules = get_playbook_rules(playbook_name)
        
        # Check for duplicates
        is_dup, matched_rule = is_duplicate_rule(rule_text, existing_rules, self.SIMILARITY_THRESHOLD)
        if is_dup:
            self.log(f"Skipping duplicate rule (matches: {matched_rule[:50]}...)", "DEBUG")
            return None
        
        # Check playbook size and archive if needed
        current_count = count_playbook_rules(playbook_name)
        if current_count >= self.MAX_RULES_PER_PLAYBOOK:
            self.log(f"Archiving old rules in {playbook_name} playbook", "INFO")
            archive_old_rules(playbook_name, self.MAX_RULES_PER_PLAYBOOK - 10)
        
        # Format the rule with date
        formatted_rule = f"[{lesson.date}] {rule_text}"
        
        # Add to playbook
        success = append_rule_to_playbook(playbook_name, formatted_rule)
        
        if success:
            self.log(f"Added rule to {playbook_name} playbook: {rule_text[:50]}...")
            return (playbook_name, rule_text)
        else:
            self.log(f"Failed to add rule to {playbook_name} playbook", "ERROR")
            return None
    
    def get_playbook_stats(self) -> dict:
        """Get statistics about all playbooks."""
        playbooks = ['pm', 'tech_lead', 'backend', 'frontend', 'qa']
        stats = {}
        
        for pb in playbooks:
            rules = get_playbook_rules(pb)
            baseline = sum(1 for r in rules if '[BASELINE]' in r)
            learned = len(rules) - baseline
            
            stats[pb] = {
                'total': len(rules),
                'baseline': baseline,
                'learned': learned
            }
        
        return stats
    
    def get_total_learned_rules(self) -> int:
        """Get total count of learned rules across all playbooks."""
        stats = self.get_playbook_stats()
        return sum(s['learned'] for s in stats.values())
    
    def generate_learning_summary(self) -> str:
        """Generate a summary of all learned rules."""
        stats = self.get_playbook_stats()
        
        lines = ["# System Learning Summary\n"]
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        
        total_baseline = sum(s['baseline'] for s in stats.values())
        total_learned = sum(s['learned'] for s in stats.values())
        
        lines.append(f"## Overall Statistics")
        lines.append(f"- Total Baseline Rules: {total_baseline}")
        lines.append(f"- Total Learned Rules: {total_learned}")
        lines.append(f"- Evolution Level: {total_baseline + total_learned}\n")
        
        lines.append("## Playbook Breakdown\n")
        
        for pb_name, pb_stats in stats.items():
            lines.append(f"### {pb_name.replace('_', ' ').title()} Playbook")
            lines.append(f"- Baseline: {pb_stats['baseline']}")
            lines.append(f"- Learned: {pb_stats['learned']}")
            
            # Show recent learned rules
            rules = get_playbook_rules(pb_name)
            learned_rules = [r for r in rules if '[BASELINE]' not in r]
            if learned_rules:
                lines.append("\nRecent learned rules:")
                for rule in learned_rules[-3:]:  # Last 3 rules
                    lines.append(f"- {normalize_rule(rule)[:80]}...")
            lines.append("")
        
        return "\n".join(lines)
