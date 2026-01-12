"""
Fuzzy text matching utilities for playbook deduplication.
Uses difflib for similarity comparison.
"""

from difflib import SequenceMatcher
from typing import List, Optional, Tuple


def similarity_ratio(text1: str, text2: str) -> float:
    """
    Calculate similarity ratio between two strings.
    
    Args:
        text1: First string
        text2: Second string
    
    Returns:
        Float between 0.0 and 1.0 (1.0 = identical)
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize strings
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()
    
    return SequenceMatcher(None, t1, t2).ratio()


def is_duplicate_rule(new_rule: str, existing_rules: List[str], threshold: float = 0.80) -> Tuple[bool, Optional[str]]:
    """
    Check if a new rule is a duplicate of any existing rule.
    
    Args:
        new_rule: The rule to check
        existing_rules: List of existing rules to compare against
        threshold: Similarity threshold (0.0-1.0), default 0.80
    
    Returns:
        Tuple of (is_duplicate, matched_rule_or_none)
    """
    if not new_rule or not existing_rules:
        return False, None
    
    # Normalize new rule
    normalized_new = normalize_rule(new_rule)
    
    for existing in existing_rules:
        normalized_existing = normalize_rule(existing)
        ratio = similarity_ratio(normalized_new, normalized_existing)
        
        if ratio >= threshold:
            return True, existing
    
    return False, None


def normalize_rule(rule: str) -> str:
    """
    Normalize a rule string for comparison.
    Removes dates, leading characters, and standardizes format.
    
    Args:
        rule: Raw rule string
    
    Returns:
        Normalized rule string
    """
    import re
    
    # Remove leading dash and whitespace
    text = rule.strip()
    if text.startswith('-'):
        text = text[1:].strip()
    
    # Remove date markers like [2025-01-15] or [BASELINE]
    text = re.sub(r'\[\d{4}-\d{2}-\d{2}\]', '', text)
    text = re.sub(r'\[BASELINE\]', '', text, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def find_most_similar(query: str, candidates: List[str], min_threshold: float = 0.5) -> Optional[Tuple[str, float]]:
    """
    Find the most similar string from a list of candidates.
    
    Args:
        query: String to match
        candidates: List of candidate strings
        min_threshold: Minimum similarity to consider a match
    
    Returns:
        Tuple of (best_match, similarity) or None if no match above threshold
    """
    if not query or not candidates:
        return None
    
    best_match = None
    best_ratio = 0.0
    
    normalized_query = normalize_rule(query)
    
    for candidate in candidates:
        normalized_candidate = normalize_rule(candidate)
        ratio = similarity_ratio(normalized_query, normalized_candidate)
        
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = candidate
    
    if best_ratio >= min_threshold:
        return (best_match, best_ratio)
    
    return None


def extract_actionable_terms(rule: str) -> List[str]:
    """
    Extract actionable terms from a rule.
    
    Args:
        rule: Rule string
    
    Returns:
        List of actionable terms found
    """
    action_terms = [
        'never', 'always', 'ensure', 'check', 'verify',
        'include', 'avoid', 'must', 'should', 'require',
        'validate', 'implement', 'add', 'remove', 'use',
        'define', 'specify', 'document', 'test', 'review'
    ]
    
    lower_rule = rule.lower()
    found_terms = [term for term in action_terms if term in lower_rule]
    
    return found_terms


def is_actionable_rule(rule: str) -> bool:
    """
    Check if a rule is actionable (contains action words).
    
    Args:
        rule: Rule string
    
    Returns:
        True if rule contains actionable terms
    """
    return len(extract_actionable_terms(rule)) > 0


def is_generic_rule(rule: str) -> bool:
    """
    Check if a rule is generic (not project-specific).
    
    Args:
        rule: Rule string
    
    Returns:
        True if rule appears to be generic
    """
    # Look for signs of project-specific content
    specific_indicators = [
        # Common project names or specifics
        r'\bv\d+\.\d+',  # Version numbers like v1.0
        r'\b(client|customer)\s+name',
        r'\b(john|jane|acme|corp|inc)\b',  # Common placeholder names
        r'@\w+\.com',  # Email addresses
        r'https?://',  # URLs
    ]
    
    import re
    lower_rule = rule.lower()
    
    for pattern in specific_indicators:
        if re.search(pattern, lower_rule):
            return False
    
    return True


def validate_rule_quality(rule: str) -> Tuple[bool, List[str]]:
    """
    Validate that a rule meets quality criteria.
    
    Criteria:
    - Actionable (contains Never/Always/Ensure etc.)
    - Generic (no project names, client names)
    - Concise (max 150 chars)
    - Explains "why" not just "what"
    
    Args:
        rule: Rule to validate
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    normalized = normalize_rule(rule)
    
    # Check length
    if len(normalized) > 150:
        issues.append("Rule exceeds 150 characters")
    
    # Check actionability
    if not is_actionable_rule(normalized):
        issues.append("Rule lacks actionable terms (Never/Always/Ensure/etc.)")
    
    # Check genericity
    if not is_generic_rule(normalized):
        issues.append("Rule appears project-specific")
    
    # Check for explanation (look for 'because', 'since', 'to', 'for')
    explanation_words = ['because', 'since', ' to ', ' for ', 'prevents', 'ensures', 'avoids']
    has_explanation = any(word in normalized.lower() for word in explanation_words)
    if not has_explanation:
        issues.append("Rule lacks explanation (missing 'because' or similar)")
    
    is_valid = len(issues) == 0
    return is_valid, issues


def deduplicate_rules(rules: List[str], threshold: float = 0.80) -> List[str]:
    """
    Remove duplicate rules from a list.
    
    Args:
        rules: List of rules
        threshold: Similarity threshold for considering duplicates
    
    Returns:
        Deduplicated list of rules
    """
    if not rules:
        return []
    
    unique_rules = []
    
    for rule in rules:
        is_dup, _ = is_duplicate_rule(rule, unique_rules, threshold)
        if not is_dup:
            unique_rules.append(rule)
    
    return unique_rules
