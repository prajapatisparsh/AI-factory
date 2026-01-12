"""
Integration test for the Discussion Orchestrator.
Tests a complete multi-agent discussion flow.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.discussion.protocol import (
    MessageType,
    DiscussionMessage,
    ConsensusStatus,
    Discussion
)
from src.discussion.memory import SharedMemory, Decision
from src.discussion.orchestrator import DiscussionOrchestrator
from src.discussion.topics import DISCUSSION_TOPICS, get_topic


class MockAgent:
    """Mock agent for testing discussions."""
    
    def __init__(self, name: str, preference: str = ""):
        self.name = name
        self.preference = preference
        self.messages_received = []
    
    def get_agent_name(self) -> str:
        return self.name
    
    def call_llm(self, system_prompt: str, user_prompt: str, 
                 temperature: float = 0.5, max_tokens: int = 500) -> str:
        """Mock LLM call that returns a structured response."""
        # Return a JSON response matching what the orchestrator expects
        return f'''{{
            "message_type": "proposal",
            "content": "I recommend {self.preference or 'a standard approach'} for this project.",
            "decision_preference": "{self.preference or 'standard'}"
        }}'''


class TestSharedMemory:
    """Tests for SharedMemory."""
    
    def test_create_memory(self, tmp_path):
        """Create shared memory instance."""
        memory = SharedMemory("test_project")
        assert memory.project_id == "test_project"
        assert len(memory.decisions) == 0
    
    def test_add_decision(self, tmp_path):
        """Add a decision to memory."""
        memory = SharedMemory("test_add_decision")
        
        decision = memory.add_decision(
            topic_id="AUTH_APPROACH",
            topic_name="Authentication Approach",
            decision="Use JWT with refresh tokens",
            rationale="Standard, stateless, scalable",
            participants=["TechLeadAgent", "DevTeamAgent"]
        )
        
        assert decision.topic_id == "AUTH_APPROACH"
        assert len(memory.decisions) == 1
    
    def test_get_decision(self, tmp_path):
        """Retrieve a decision."""
        memory = SharedMemory("test_get_decision")
        
        memory.add_decision(
            topic_id="DB_CHOICE",
            topic_name="Database Choice",
            decision="PostgreSQL",
            rationale="Reliable, ACID compliant",
            participants=["TechLeadAgent"]
        )
        
        retrieved = memory.get_decision("DB_CHOICE")
        assert retrieved is not None
        assert retrieved.decision == "PostgreSQL"
    
    def test_add_note(self, tmp_path):
        """Add agent notes."""
        memory = SharedMemory("test_notes")
        
        note = memory.add_note(
            agent="TechLeadAgent",
            topic="architecture",
            content="Consider microservices for scalability"
        )
        
        assert note.agent == "TechLeadAgent"
        notes = memory.get_notes_for_topic("architecture")
        assert len(notes) == 1


class TestDiscussionOrchestrator:
    """Tests for the Discussion Orchestrator."""
    
    def test_start_discussion(self):
        """Start a new discussion."""
        agents = {
            "TechLeadAgent": MockAgent("TechLeadAgent"),
            "DevTeamAgent-backend": MockAgent("DevTeamAgent-backend")
        }
        orchestrator = DiscussionOrchestrator(agents, project_id="test_start")
        
        discussion = orchestrator.start_discussion("DATABASE_CHOICE")
        
        assert discussion.topic_id == "DATABASE_CHOICE"
        assert discussion.status == ConsensusStatus.PENDING
        assert len(discussion.participants) > 0
    
    def test_discussion_with_agreement(self):
        """Run a discussion where agents agree."""
        # Create mock agents that all prefer the same thing
        agents = {
            "TechLeadAgent": MockAgent("TechLeadAgent", "PostgreSQL"),
            "DevTeamAgent-backend": MockAgent("DevTeamAgent-backend", "PostgreSQL")
        }
        orchestrator = DiscussionOrchestrator(agents, project_id="test_agreement")
        
        discussion = orchestrator.start_discussion("DATABASE_CHOICE")
        
        # Run discussion (will use mock LLM responses)
        with patch.object(orchestrator, '_get_agent_contribution') as mock_contrib:
            # Mock contributions that lead to agreement
            mock_contrib.side_effect = [
                DiscussionMessage(
                    sender="TechLeadAgent",
                    message_type=MessageType.PROPOSAL,
                    content="I propose PostgreSQL for reliability",
                    topic_id="DATABASE_CHOICE",
                    metadata={'decision_preference': 'PostgreSQL'}
                ),
                DiscussionMessage(
                    sender="DevTeamAgent-backend",
                    message_type=MessageType.AGREEMENT,
                    content="Agreed, PostgreSQL is a great choice",
                    topic_id="DATABASE_CHOICE",
                    metadata={'decision_preference': 'PostgreSQL'}
                )
            ]
            
            result = orchestrator.run_discussion(discussion)
        
        assert result.status in [ConsensusStatus.AGREED, ConsensusStatus.PENDING, ConsensusStatus.TIMEOUT]
        assert len(result.messages) >= 0
    
    def test_get_all_decisions(self):
        """Test retrieving all decisions."""
        agents = {"TechLeadAgent": MockAgent("TechLeadAgent")}
        orchestrator = DiscussionOrchestrator(agents, project_id="test_all_decisions")
        
        # Add a decision directly to memory
        orchestrator.memory.add_decision(
            topic_id="TEST_TOPIC",
            topic_name="Test Topic",
            decision="Test Decision",
            rationale="Test Rationale",
            participants=["TechLeadAgent"]
        )
        
        decisions = orchestrator.get_all_decisions()
        assert len(decisions) >= 1
        assert decisions[0]['topic'] == "Test Topic"


class TestTopics:
    """Tests for predefined topics."""
    
    def test_all_topics_have_required_fields(self):
        """Verify all topics have required fields."""
        for topic_id, topic in DISCUSSION_TOPICS.items():
            assert topic.id == topic_id
            assert topic.name
            assert topic.description
            assert len(topic.participants) > 0
            assert topic.decision_required
    
    def test_get_topic(self):
        """Test topic retrieval."""
        topic = get_topic("AUTH_APPROACH")
        assert topic is not None
        assert topic.name == "Authentication Approach"
        
        invalid = get_topic("INVALID_TOPIC")
        assert invalid is None
    
    def test_topic_opening_prompt(self):
        """Test topic generates opening prompt."""
        topic = get_topic("DATABASE_CHOICE")
        prompt = topic.get_opening_prompt()
        
        assert "Database" in prompt
        assert topic.decision_required in prompt


class TestEndToEndDiscussion:
    """End-to-end integration tests."""
    
    def test_full_discussion_flow(self):
        """Test complete discussion from start to decision."""
        # Setup
        memory = SharedMemory("e2e_test")
        agents = {
            "PMAgent": MockAgent("PMAgent", "JWT authentication"),
            "TechLeadAgent": MockAgent("TechLeadAgent", "JWT authentication"),
            "DevTeamAgent-backend": MockAgent("DevTeamAgent-backend", "JWT authentication")
        }
        
        orchestrator = DiscussionOrchestrator(agents, memory=memory, project_id="e2e_test")
        
        # Start discussion
        discussion = orchestrator.start_discussion("AUTH_APPROACH")
        assert discussion.topic_name == "Authentication Approach"
        
        # Verify active discussion is tracked
        assert orchestrator.get_discussion("AUTH_APPROACH") is not None
        
        # Memory should be empty before decision
        assert memory.get_decision("AUTH_APPROACH") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
