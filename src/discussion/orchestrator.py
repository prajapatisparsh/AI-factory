"""
Discussion Orchestrator - Main engine for multi-agent collaboration.
Manages discussion flow, routes messages, and detects consensus.
"""

from typing import List, Dict, Optional, Tuple, Callable, Any
from datetime import datetime
import logging

from src.discussion.protocol import (
    Discussion,
    DiscussionMessage,
    MessageType,
    ConsensusStatus
)
from src.discussion.memory import SharedMemory
from src.discussion.topics import DiscussionTopic, DISCUSSION_TOPICS, get_topic

logger = logging.getLogger(__name__)


class DiscussionOrchestrator:
    """
    Orchestrates multi-agent discussions.
    
    Responsibilities:
    - Start discussions on topics
    - Route messages between agents
    - Detect consensus or deadlock
    - Escalate to human when needed
    - Record decisions in shared memory
    
    Usage:
        orchestrator = DiscussionOrchestrator(agents, memory)
        discussion = orchestrator.start_discussion("AUTH_APPROACH")
        result = orchestrator.run_discussion(discussion)
    """
    
    def __init__(
        self,
        agents: Dict[str, Any],
        memory: Optional[SharedMemory] = None,
        project_id: str = "default"
    ):
        """
        Initialize the orchestrator.
        
        Args:
            agents: Dictionary mapping agent names to agent instances
            memory: Shared memory instance (created if not provided)
            project_id: Project identifier for memory persistence
        """
        self.agents = agents
        self.memory = memory or SharedMemory(project_id)
        self.project_id = project_id
        self.active_discussions: Dict[str, Discussion] = {}
        self._human_callback: Optional[Callable] = None
    
    def set_human_callback(self, callback: Callable[[str, str], str]) -> None:
        """Set callback function for human escalation."""
        self._human_callback = callback
    
    def start_discussion(self, topic_id: str) -> Discussion:
        """
        Start a new discussion on a topic.
        
        Args:
            topic_id: ID of the topic from DISCUSSION_TOPICS
            
        Returns:
            New Discussion instance
        """
        topic = get_topic(topic_id)
        if not topic:
            raise ValueError(f"Unknown topic: {topic_id}")
        
        # Check if we already have a decision for this topic
        existing = self.memory.get_decision(topic_id)
        if existing:
            logger.info(f"Topic {topic_id} already decided: {existing.decision}")
        
        discussion = Discussion(
            topic_id=topic_id,
            topic_name=topic.name,
            participants=topic.participants
        )
        
        self.active_discussions[topic_id] = discussion
        logger.info(f"Started discussion: {topic.name} with {topic.participants}")
        
        return discussion
    
    def run_discussion(
        self,
        discussion: Discussion,
        initial_context: Optional[str] = None
    ) -> Discussion:
        """
        Run a complete discussion to reach consensus.
        
        Args:
            discussion: The Discussion to run
            initial_context: Additional context to provide to agents
            
        Returns:
            Completed Discussion with decision
        """
        topic = get_topic(discussion.topic_id)
        if not topic:
            raise ValueError(f"Unknown topic: {discussion.topic_id}")
        
        max_rounds = topic.max_rounds
        
        # Build context for discussion
        context = self._build_context(topic, initial_context)
        
        # First round: each participant shares their perspective
        for round_num in range(max_rounds):
            discussion.rounds_completed = round_num + 1
            logger.info(f"Discussion round {round_num + 1}/{max_rounds}")
            
            # Get speaking order for this round
            speakers = self._get_speaking_order(discussion, round_num)
            
            for agent_name in speakers:
                agent = self.agents.get(agent_name)
                if not agent:
                    logger.warning(f"Agent {agent_name} not found, skipping")
                    continue
                
                # Generate agent's contribution
                message = self._get_agent_contribution(
                    agent,
                    agent_name,
                    discussion,
                    context,
                    round_num
                )
                
                if message:
                    discussion.add_message(message)
                    logger.info(f"{agent_name}: {message.message_type.value}")
            
            # Check for consensus after each round
            consensus = self._check_consensus(discussion)
            
            if consensus == ConsensusStatus.AGREED:
                discussion.status = ConsensusStatus.AGREED
                self._record_decision(discussion)
                return discussion
            
            elif consensus == ConsensusStatus.DISAGREED:
                # Try to resolve disagreement
                if round_num < max_rounds - 1:
                    self._attempt_resolution(discussion)
                else:
                    # Final round, escalate
                    discussion.status = ConsensusStatus.ESCALATED
                    self._escalate_to_human(discussion, topic)
                    return discussion
        
        # Max rounds reached without consensus
        discussion.status = ConsensusStatus.TIMEOUT
        logger.warning(f"Discussion {discussion.topic_id} timed out after {max_rounds} rounds")
        
        # Make a decision based on majority or moderator
        self._force_decision(discussion)
        
        return discussion
    
    def _build_context(self, topic: DiscussionTopic, additional: Optional[str] = None) -> str:
        """Build context string for the discussion."""
        parts = [f"# Discussion: {topic.name}\n"]
        parts.append(topic.get_opening_prompt())
        
        # Add context from shared memory
        for key in topic.context_keys:
            value = self.memory.get_context_value(key)
            if value:
                parts.append(f"\n**{key}:** {value}")
        
        # Add previous decisions that might be relevant
        all_decisions = self.memory.get_decisions()
        if all_decisions:
            parts.append("\n## Previous Team Decisions")
            for d in all_decisions[-3:]:
                parts.append(f"- {d.topic_name}: {d.decision}")
        
        if additional:
            parts.append(f"\n## Additional Context\n{additional}")
        
        return "\n".join(parts)
    
    def _get_speaking_order(self, discussion: Discussion, round_num: int) -> List[str]:
        """Determine which agents speak and in what order."""
        participants = discussion.participants.copy()
        
        if round_num == 0:
            # First round: everyone speaks in order
            return participants
        
        # Subsequent rounds: prioritize those who disagreed
        disagreers = set()
        for msg in discussion.messages:
            if msg.message_type == MessageType.DISAGREEMENT:
                disagreers.add(msg.sender)
        
        # Disagreers first, then others
        ordered = [p for p in participants if p in disagreers]
        ordered.extend([p for p in participants if p not in disagreers])
        
        return ordered
    
    def _get_agent_contribution(
        self,
        agent: Any,
        agent_name: str,
        discussion: Discussion,
        context: str,
        round_num: int
    ) -> Optional[DiscussionMessage]:
        """Get an agent's contribution to the discussion."""
        # Build prompt for the agent
        history = discussion.format_history(max_messages=10)
        
        if round_num == 0:
            # First round: share initial perspective
            prompt_type = "proposal"
            instruction = "Share your professional perspective on this topic. What approach do you recommend and why?"
        else:
            # Later rounds: respond to others
            prompt_type = "response"
            instruction = "Based on the discussion so far, do you agree with the emerging decision? If not, explain your concerns."
        
        system_prompt = f"""You are participating in a team discussion as {agent_name}.

{context}

## Discussion History
{history if history else "No messages yet - you are starting the discussion."}

## Your Task
{instruction}

RESPOND IN THIS JSON FORMAT:
{{
    "message_type": "proposal|agreement|disagreement|suggestion",
    "content": "Your contribution (2-4 sentences, be concise)",
    "decision_preference": "Your preferred decision for this topic"
}}"""

        try:
            # Use the agent's LLM to generate response
            if hasattr(agent, 'call_llm'):
                response = agent.call_llm(
                    system_prompt,
                    f"Discussion topic: {discussion.topic_name}",
                    temperature=0.5,
                    max_tokens=500
                )
                
                # Parse the response
                parsed = self._parse_agent_response(response)
                
                return DiscussionMessage(
                    sender=agent_name,
                    recipient="all",
                    message_type=parsed.get('message_type', MessageType.PROPOSAL),
                    content=parsed.get('content', response[:500]),
                    topic_id=discussion.topic_id,
                    metadata={'decision_preference': parsed.get('decision_preference', '')}
                )
        except Exception as e:
            logger.error(f"Agent {agent_name} failed to contribute: {e}")
        
        return None
    
    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        """Parse agent's JSON response."""
        import json
        import re
        
        # Try to extract JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group())
                # Convert message_type string to enum
                msg_type_str = data.get('message_type', 'proposal').lower()
                type_map = {
                    'proposal': MessageType.PROPOSAL,
                    'agreement': MessageType.AGREEMENT,
                    'disagreement': MessageType.DISAGREEMENT,
                    'suggestion': MessageType.SUGGESTION,
                    'question': MessageType.QUESTION
                }
                data['message_type'] = type_map.get(msg_type_str, MessageType.PROPOSAL)
                return data
            except json.JSONDecodeError:
                pass
        
        # Fallback: treat entire response as content
        return {
            'message_type': MessageType.PROPOSAL,
            'content': response[:500],
            'decision_preference': ''
        }
    
    def _check_consensus(self, discussion: Discussion) -> ConsensusStatus:
        """Check if consensus has been reached."""
        if not discussion.messages:
            return ConsensusStatus.PENDING
        
        # Count message types in recent messages
        recent = discussion.get_last_n_messages(len(discussion.participants) * 2)
        
        agreements = sum(1 for m in recent if m.message_type == MessageType.AGREEMENT)
        disagreements = sum(1 for m in recent if m.message_type == MessageType.DISAGREEMENT)
        
        # Check decision preferences
        preferences = {}
        for msg in recent:
            pref = msg.metadata.get('decision_preference', '')
            if pref:
                preferences[pref] = preferences.get(pref, 0) + 1
        
        total = len(discussion.participants)
        
        # Strong agreement: >70% agree on same thing
        if preferences:
            max_pref = max(preferences.values())
            if max_pref >= total * 0.7:
                return ConsensusStatus.AGREED
        
        # Strong disagreement: >50% explicitly disagree
        if disagreements >= total * 0.5:
            return ConsensusStatus.DISAGREED
        
        return ConsensusStatus.PENDING
    
    def _attempt_resolution(self, discussion: Discussion) -> None:
        """Try to resolve disagreements."""
        # Add a moderator message to guide resolution
        moderator_msg = DiscussionMessage(
            sender="Moderator",
            recipient="all",
            message_type=MessageType.SUMMARY,
            content="There are differing opinions. Let's focus on finding common ground. What aspects do we all agree on?",
            topic_id=discussion.topic_id
        )
        discussion.add_message(moderator_msg)
    
    def _escalate_to_human(self, discussion: Discussion, topic: DiscussionTopic) -> None:
        """Escalate to human for decision."""
        summary = self._summarize_discussion(discussion)
        
        if self._human_callback:
            human_decision = self._human_callback(topic.name, summary)
            discussion.finalize(human_decision, "Human decision")
        else:
            logger.warning(f"No human callback set, cannot escalate {topic.name}")
            discussion.status = ConsensusStatus.ESCALATED
    
    def _force_decision(self, discussion: Discussion) -> None:
        """Force a decision when consensus cannot be reached."""
        # Find the most popular decision preference
        preferences = {}
        for msg in discussion.messages:
            pref = msg.metadata.get('decision_preference', '')
            if pref:
                preferences[pref] = preferences.get(pref, 0) + 1
        
        if preferences:
            decision = max(preferences, key=preferences.get)
            discussion.finalize(
                decision,
                f"Majority decision after {discussion.rounds_completed} rounds"
            )
        else:
            # Use first proposal
            for msg in discussion.messages:
                if msg.message_type == MessageType.PROPOSAL:
                    discussion.finalize(
                        msg.content[:200],
                        "Based on initial proposal (no consensus reached)"
                    )
                    break
    
    def _summarize_discussion(self, discussion: Discussion) -> str:
        """Create a summary of the discussion for human review."""
        lines = [f"# Discussion Summary: {discussion.topic_name}\n"]
        lines.append(f"**Rounds:** {discussion.rounds_completed}")
        lines.append(f"**Participants:** {', '.join(discussion.participants)}\n")
        
        lines.append("## Key Points")
        for msg in discussion.messages:
            if msg.message_type in [MessageType.PROPOSAL, MessageType.DISAGREEMENT]:
                lines.append(f"- **{msg.sender}** ({msg.message_type.value}): {msg.content[:150]}...")
        
        lines.append("\n## Decision Preferences")
        seen = set()
        for msg in discussion.messages:
            pref = msg.metadata.get('decision_preference', '')
            if pref and pref not in seen:
                lines.append(f"- {msg.sender}: {pref}")
                seen.add(pref)
        
        return "\n".join(lines)
    
    def _record_decision(self, discussion: Discussion) -> None:
        """Record the decision in shared memory."""
        if discussion.decision:
            self.memory.add_decision(
                topic_id=discussion.topic_id,
                topic_name=discussion.topic_name,
                decision=discussion.decision,
                rationale=discussion.decision_rationale or "",
                participants=discussion.participants
            )
            logger.info(f"Decision recorded: {discussion.topic_name} → {discussion.decision}")
    
    def get_discussion(self, topic_id: str) -> Optional[Discussion]:
        """Get an active or completed discussion."""
        return self.active_discussions.get(topic_id)
    
    def get_all_decisions(self) -> List[Dict]:
        """Get all decisions from shared memory."""
        return [
            {
                'topic': d.topic_name,
                'decision': d.decision,
                'rationale': d.rationale
            }
            for d in self.memory.get_decisions()
        ]
