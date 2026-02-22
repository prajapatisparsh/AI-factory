"""
Text formatting utilities shared across agents.
"""

from typing import Iterable


def bullet_list(items: Iterable[str]) -> str:
    """Format an iterable of strings as a Markdown bullet list.

    Example::

        bullet_list(["Feature A", "Feature B"])
        # -> "- Feature A\\n- Feature B"
    """
    return "\n".join(f"- {item}" for item in items)


def numbered_list(items: Iterable[str]) -> str:
    """Format an iterable of strings as a Markdown numbered list.

    Example::

        numbered_list(["Step 1", "Step 2"])
        # -> "1. Step 1\\n2. Step 2"
    """
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))


def truncate(text: str, max_chars: int = 3000, suffix: str = "...") -> str:
    """Truncate *text* to *max_chars* characters, appending *suffix* if cut."""
    return text if len(text) <= max_chars else text[:max_chars] + suffix
