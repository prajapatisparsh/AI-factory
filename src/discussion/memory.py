"""
Shared Memory - Persistent scratchpad for agent collaboration.
Stores decisions, reasoning, and notes that all agents can access.
"""

import json
import logging
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Decision:
    """A finalized decision from a discussion."""
    topic_id: str
    topic_name: str
    decision: str
    rationale: str
    participants: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 1.0  # 0.0 to 1.0


@dataclass
class AgentNote:
    """A note left by an agent for others to see."""
    agent: str
    topic: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)


class SharedMemory:
    """
    Persistent shared memory for multi-agent collaboration.
    Stores decisions, notes, and context that all agents can access.
    """
    
    def __init__(self, project_id: str = "default"):
        """Initialize shared memory for a project."""
        self.project_id = project_id
        self.decisions: List[Decision] = []
        self.notes: List[AgentNote] = []
        self.context: Dict[str, Any] = {}
        self._file_path = self._get_file_path()
        self._load()
    
    def _get_file_path(self) -> str:
        """Get the file path for persistence."""
        base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "memory",
            "discussions"
        )
        os.makedirs(base_dir, exist_ok=True)
        # Restrict to owner-only on Linux/macOS (H-6)
        if os.name != 'nt':
            import stat
            os.chmod(base_dir, stat.S_IRWXU)
        return os.path.join(base_dir, f"{self.project_id}_memory.json")
    
    def _load(self) -> None:
        """Load from disk if exists."""
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.decisions = [Decision(**d) for d in data.get('decisions', [])]
                    self.notes = [AgentNote(**n) for n in data.get('notes', [])]
                    self.context = data.get('context', {})
            except json.JSONDecodeError as e:
                logger.error(
                    f"Memory file corrupted (JSON error) for project '{self.project_id}': {e}. Starting fresh."
                )
            except OSError as e:
                logger.error(
                    f"Memory file unreadable for project '{self.project_id}': {e}. Starting fresh."
                )
    
    def _save(self) -> None:
        """Persist to disk using atomic write to prevent file corruption."""
        data = {
            'decisions': [
                {
                    'topic_id': d.topic_id,
                    'topic_name': d.topic_name,
                    'decision': d.decision,
                    'rationale': d.rationale,
                    'participants': d.participants,
                    'timestamp': d.timestamp,
                    'confidence': d.confidence
                }
                for d in self.decisions
            ],
            'notes': [
                {
                    'agent': n.agent,
                    'topic': n.topic,
                    'content': n.content,
                    'timestamp': n.timestamp,
                    'tags': n.tags
                }
                for n in self.notes
            ],
            'context': self.context
        }
        tmp_path = self._file_path + ".tmp"
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, self._file_path)
        except OSError as e:
            logger.error(
                f"Failed to persist memory for project '{self.project_id}': {e}"
            )
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    
    def add_decision(
        self,
        topic_id: str,
        topic_name: str,
        decision: str,
        rationale: str,
        participants: List[str],
        confidence: float = 1.0
    ) -> Decision:
        """Record a finalized decision."""
        d = Decision(
            topic_id=topic_id,
            topic_name=topic_name,
            decision=decision,
            rationale=rationale,
            participants=participants,
            confidence=confidence
        )
        self.decisions.append(d)
        self._save()
        return d
    
    def add_note(
        self,
        agent: str,
        topic: str,
        content: str,
        tags: Optional[List[str]] = None
    ) -> AgentNote:
        """Agent leaves a note for others."""
        note = AgentNote(
            agent=agent,
            topic=topic,
            content=content,
            tags=tags or []
        )
        self.notes.append(note)
        self._save()
        return note
    
    def get_decisions(self, topic_id: Optional[str] = None) -> List[Decision]:
        """Get all decisions, optionally filtered by topic."""
        if topic_id:
            return [d for d in self.decisions if d.topic_id == topic_id]
        return self.decisions
    
    def get_decision(self, topic_id: str) -> Optional[Decision]:
        """Get the most recent decision for a topic."""
        matching = [d for d in self.decisions if d.topic_id == topic_id]
        return matching[-1] if matching else None
    
    def get_notes_for_topic(self, topic: str) -> List[AgentNote]:
        """Get all notes related to a topic."""
        return [n for n in self.notes if n.topic == topic]
    
    def get_notes_by_agent(self, agent: str) -> List[AgentNote]:
        """Get all notes from a specific agent."""
        return [n for n in self.notes if n.agent == agent]
    
    def get_context_for_agent(self, agent: str, topic: str) -> str:
        """
        Build context string for an agent joining a discussion.
        Includes relevant decisions and notes.
        """
        lines = []
        
        # Add relevant decisions
        decisions = self.get_decisions(topic)
        if decisions:
            lines.append("## Previous Decisions")
            for d in decisions[-3:]:  # Last 3 decisions
                lines.append(f"- **{d.topic_name}**: {d.decision}")
                lines.append(f"  Rationale: {d.rationale}")
        
        # Add recent notes from other agents
        notes = [n for n in self.notes if n.topic == topic and n.agent != agent]
        if notes:
            lines.append("\n## Notes from Other Agents")
            for n in notes[-5:]:  # Last 5 notes
                lines.append(f"- **{n.agent}**: {n.content}")
        
        return "\n".join(lines) if lines else "No prior context available."
    
    def set_context(self, key: str, value: Any) -> None:
        """Store arbitrary context data."""
        self.context[key] = value
        self._save()
    
    def get_context_value(self, key: str, default: Any = None) -> Any:
        """Retrieve context data."""
        return self.context.get(key, default)
    
    def clear(self) -> None:
        """Clear all memory (for new projects)."""
        self.decisions = []
        self.notes = []
        self.context = {}
        self._save()
    
    def format_summary(self) -> str:
        """Format a summary of all decisions made."""
        if not self.decisions:
            return "No decisions have been made yet."
        
        lines = ["# Team Decisions Summary\n"]
        for d in self.decisions:
            lines.append(f"## {d.topic_name}")
            lines.append(f"**Decision:** {d.decision}")
            lines.append(f"**Rationale:** {d.rationale}")
            lines.append(f"**Participants:** {', '.join(d.participants)}")
            lines.append("")
        
        return "\n".join(lines)
