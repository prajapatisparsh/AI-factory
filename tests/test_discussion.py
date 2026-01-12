"""
Unit tests for the discussion protocol.
"""

import pytest
from datetime import datetime

from src.discussion.protocol import (
    MessageType,
    DiscussionMessage,
    ConsensusStatus,
    Discussion
)


class TestMessageType:
    """Tests for MessageType enum."""
    
    def test_all_types_exist(self):
        """Verify all expected message types exist."""
        expected = ['proposal', 'question', 'answer', 'agreement', 
                    'disagreement', 'suggestion', 'decision', 'summary']
        for t in expected:
            assert hasattr(MessageType, t.upper())
    
    def test_type_values(self):
        """Verify enum values are strings."""
        assert MessageType.PROPOSAL.value == "proposal"
        assert MessageType.AGREEMENT.value == "agreement"


class TestDiscussionMessage:
    """Tests for DiscussionMessage."""
    
    def test_create_basic_message(self):
        """Create a basic message."""
        msg = DiscussionMessage(
            sender="TechLeadAgent",
            message_type=MessageType.PROPOSAL,
            content="We should use PostgreSQL for the database.",
            topic_id="DATABASE_CHOICE"
        )
        assert msg.sender == "TechLeadAgent"
        assert msg.recipient == "all"  # Default
        assert msg.message_type == MessageType.PROPOSAL
        assert "PostgreSQL" in msg.content
    
    def test_message_with_recipient(self):
        """Create a message with specific recipient."""
        msg = DiscussionMessage(
            sender="QAAgent",
            recipient="DevTeamAgent",
            message_type=MessageType.QUESTION,
            content="How will you handle rate limiting?",
            topic_id="API_SECURITY"
        )
        assert msg.recipient == "DevTeamAgent"
    
    def test_is_terminal(self):
        """Test terminal message detection."""
        decision = DiscussionMessage(
            sender="Moderator",
            message_type=MessageType.DECISION,
            content="We will use JWT.",
            topic_id="AUTH_APPROACH"
        )
        agreement = DiscussionMessage(
            sender="TechLead",
            message_type=MessageType.AGREEMENT,
            content="Agreed.",
            topic_id="AUTH_APPROACH"
        )
        proposal = DiscussionMessage(
            sender="PM",
            message_type=MessageType.PROPOSAL,
            content="Let's consider OAuth.",
            topic_id="AUTH_APPROACH"
        )
        
        assert decision.is_terminal() is True
        assert agreement.is_terminal() is True
        assert proposal.is_terminal() is False


class TestDiscussion:
    """Tests for Discussion class."""
    
    def test_create_discussion(self):
        """Create a new discussion."""
        disc = Discussion(
            topic_id="AUTH_APPROACH",
            topic_name="Authentication Approach",
            participants=["PMAgent", "TechLeadAgent", "DevTeamAgent"]
        )
        assert disc.topic_id == "AUTH_APPROACH"
        assert len(disc.participants) == 3
        assert disc.status == ConsensusStatus.PENDING
        assert disc.decision is None
    
    def test_add_message(self):
        """Add messages to discussion."""
        disc = Discussion(
            topic_id="DB_CHOICE",
            topic_name="Database Choice",
            participants=["TechLeadAgent"]
        )
        
        msg = DiscussionMessage(
            sender="TechLeadAgent",
            message_type=MessageType.PROPOSAL,
            content="Use PostgreSQL",
            topic_id="DB_CHOICE"
        )
        
        disc.add_message(msg)
        assert len(disc.messages) == 1
        assert disc.messages[0].content == "Use PostgreSQL"
    
    def test_format_history(self):
        """Test history formatting."""
        disc = Discussion(
            topic_id="TEST",
            topic_name="Test Topic",
            participants=["A", "B"]
        )
        
        disc.add_message(DiscussionMessage(
            sender="A",
            message_type=MessageType.PROPOSAL,
            content="Idea 1",
            topic_id="TEST"
        ))
        disc.add_message(DiscussionMessage(
            sender="B",
            message_type=MessageType.AGREEMENT,
            content="Sounds good",
            topic_id="TEST"
        ))
        
        history = disc.format_history()
        assert "A" in history
        assert "PROPOSAL" in history
        assert "B" in history
    
    def test_finalize_discussion(self):
        """Test finalizing a discussion."""
        disc = Discussion(
            topic_id="TEST",
            topic_name="Test",
            participants=["A"]
        )
        
        disc.finalize("Use option X", "Best tradeoff")
        
        assert disc.decision == "Use option X"
        assert disc.decision_rationale == "Best tradeoff"
        assert disc.status == ConsensusStatus.AGREED
        assert disc.ended_at is not None
    
    def test_count_agreements_and_disagreements(self):
        """Test counting message types."""
        disc = Discussion(
            topic_id="TEST",
            topic_name="Test",
            participants=["A", "B", "C"]
        )
        
        disc.add_message(DiscussionMessage(
            sender="A", message_type=MessageType.PROPOSAL,
            content="X", topic_id="TEST"
        ))
        disc.add_message(DiscussionMessage(
            sender="B", message_type=MessageType.AGREEMENT,
            content="Yes", topic_id="TEST"
        ))
        disc.add_message(DiscussionMessage(
            sender="C", message_type=MessageType.DISAGREEMENT,
            content="No", topic_id="TEST"
        ))
        disc.add_message(DiscussionMessage(
            sender="A", message_type=MessageType.AGREEMENT,
            content="I also agree", topic_id="TEST"
        ))
        
        assert disc.count_agreements() == 2
        assert disc.count_disagreements() == 1


class TestConsensusStatus:
    """Tests for ConsensusStatus enum."""
    
    def test_all_statuses(self):
        """Verify all statuses exist."""
        assert ConsensusStatus.PENDING.value == "pending"
        assert ConsensusStatus.AGREED.value == "agreed"
        assert ConsensusStatus.DISAGREED.value == "disagreed"
        assert ConsensusStatus.ESCALATED.value == "escalated"
        assert ConsensusStatus.TIMEOUT.value == "timeout"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
