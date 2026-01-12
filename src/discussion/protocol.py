"""
Discussion Protocol - Data structures for agent-to-agent communication.
Defines message types, conversation structures, and consensus tracking.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MessageType(str, Enum):
    """Types of messages agents can send."""
    PROPOSAL = "proposal"       # Agent proposes an idea or solution
    QUESTION = "question"       # Agent asks another for clarification
    ANSWER = "answer"           # Response to a question
    AGREEMENT = "agreement"     # Agent agrees with a proposal
    DISAGREEMENT = "disagreement"  # Agent disagrees with reasoning
    SUGGESTION = "suggestion"   # Alternative or modification
    DECISION = "decision"       # Final decision on a topic
    SUMMARY = "summary"         # Moderator's summary of discussion


class ConsensusStatus(str, Enum):
    """Status of consensus in a discussion."""
    PENDING = "pending"         # Discussion ongoing
    AGREED = "agreed"           # All participants agree
    DISAGREED = "disagreed"     # Fundamental disagreement exists
    ESCALATED = "escalated"     # Sent to human for decision
    TIMEOUT = "timeout"         # Max rounds reached without consensus


class DiscussionMessage(BaseModel):
    """A single message in an agent discussion."""
    id: str = Field(default_factory=lambda: datetime.now().strftime("%H%M%S%f"))
    sender: str = Field(..., description="Agent name sending the message")
    recipient: str = Field(default="all", description="Target agent or 'all'")
    message_type: MessageType = Field(..., description="Type of message")
    content: str = Field(..., description="Message content")
    topic_id: str = Field(..., description="ID of the discussion topic")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    references: List[str] = Field(default_factory=list, description="IDs of messages being referenced")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    def is_terminal(self) -> bool:
        """Check if this message ends a discussion branch."""
        return self.message_type in [MessageType.DECISION, MessageType.AGREEMENT]


class Discussion(BaseModel):
    """A complete discussion on a topic."""
    topic_id: str = Field(..., description="Unique topic identifier")
    topic_name: str = Field(..., description="Human-readable topic name")
    participants: List[str] = Field(..., description="List of participating agent names")
    messages: List[DiscussionMessage] = Field(default_factory=list)
    status: ConsensusStatus = Field(default=ConsensusStatus.PENDING)
    decision: Optional[str] = Field(default=None, description="Final decision if reached")
    decision_rationale: Optional[str] = Field(default=None, description="Why this decision was made")
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = Field(default=None)
    rounds_completed: int = Field(default=0)
    
    def add_message(self, message: DiscussionMessage) -> None:
        """Add a message to the discussion."""
        self.messages.append(message)
    
    def get_messages_by_agent(self, agent: str) -> List[DiscussionMessage]:
        """Get all messages from a specific agent."""
        return [m for m in self.messages if m.sender == agent]
    
    def get_last_n_messages(self, n: int = 5) -> List[DiscussionMessage]:
        """Get the last N messages."""
        return self.messages[-n:] if self.messages else []
    
    def format_history(self, max_messages: int = 10) -> str:
        """Format discussion history as readable text."""
        recent = self.messages[-max_messages:]
        lines = []
        for msg in recent:
            prefix = f"[{msg.message_type.value.upper()}]"
            target = f" → {msg.recipient}" if msg.recipient != "all" else ""
            lines.append(f"{msg.sender}{target} {prefix}: {msg.content}")
        return "\n".join(lines)
    
    def count_agreements(self) -> int:
        """Count agreement messages."""
        return sum(1 for m in self.messages if m.message_type == MessageType.AGREEMENT)
    
    def count_disagreements(self) -> int:
        """Count disagreement messages."""
        return sum(1 for m in self.messages if m.message_type == MessageType.DISAGREEMENT)
    
    def finalize(self, decision: str, rationale: str) -> None:
        """Finalize the discussion with a decision."""
        self.decision = decision
        self.decision_rationale = rationale
        self.status = ConsensusStatus.AGREED
        self.ended_at = datetime.now().isoformat()
