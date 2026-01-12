"""
Discussion module for multi-agent collaboration.
"""

from src.discussion.protocol import (
    MessageType,
    DiscussionMessage,
    ConsensusStatus,
    Discussion
)
from src.discussion.memory import SharedMemory
from src.discussion.orchestrator import DiscussionOrchestrator
from src.discussion.topics import DISCUSSION_TOPICS, DiscussionTopic

__all__ = [
    'MessageType',
    'DiscussionMessage',
    'ConsensusStatus',
    'Discussion',
    'SharedMemory',
    'DiscussionOrchestrator',
    'DISCUSSION_TOPICS',
    'DiscussionTopic'
]
