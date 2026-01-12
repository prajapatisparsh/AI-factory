"""
Moderator Agent - Facilitates multi-agent discussions.
Summarizes, identifies disagreements, proposes compromises, and escalates.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime

from src.agents.base import BaseAgent
from src.discussion.protocol import (
    Discussion,
    DiscussionMessage,
    MessageType,
    ConsensusStatus
)


class ModeratorAgent(BaseAgent):
    """
    Moderator agent that facilitates discussions between other agents.
    
    Responsibilities:
    - Summarize discussion progress
    - Identify points of disagreement
    - Propose compromises
    - Prepare escalation messages for humans
    - Call votes when needed
    """
    
    def __init__(self):
        super().__init__(playbook_name=None)
    
    def get_agent_name(self) -> str:
        return "ModeratorAgent"
    
    def summarize_discussion(self, discussion: Discussion) -> str:
        """
        Create a concise summary of the discussion so far.
        
        Args:
            discussion: The discussion to summarize
            
        Returns:
            Summary string
        """
        self.log(f"Summarizing discussion: {discussion.topic_name}")
        
        system_prompt = """You are a neutral meeting facilitator summarizing a team discussion.

Create a brief summary (3-5 bullet points) covering:
1. The main topic and decision required
2. Key perspectives shared
3. Points of agreement
4. Points of disagreement (if any)
5. Current status

Be neutral and factual. Do not take sides."""

        history = discussion.format_history(max_messages=15)
        
        user_prompt = f"""Summarize this discussion:

Topic: {discussion.topic_name}
Participants: {', '.join(discussion.participants)}
Rounds completed: {discussion.rounds_completed}

Discussion history:
{history}

Provide a concise summary."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=500)
            return response.strip()
        except Exception as e:
            self.log(f"Summary generation failed: {e}", "ERROR")
            return f"Discussion on {discussion.topic_name} with {len(discussion.messages)} messages."
    
    def identify_disagreements(self, discussion: Discussion) -> List[Dict[str, str]]:
        """
        Identify points of disagreement between participants.
        
        Returns:
            List of disagreement dicts with 'issue', 'positions', and 'agents'
        """
        self.log("Identifying disagreements")
        
        disagreements = []
        
        # Find disagreement messages
        for i, msg in enumerate(discussion.messages):
            if msg.message_type == MessageType.DISAGREEMENT:
                # Find what they're disagreeing with
                context = ""
                if i > 0:
                    context = discussion.messages[i-1].content[:100]
                
                disagreements.append({
                    'agent': msg.sender,
                    'issue': msg.content[:200],
                    'context': context
                })
        
        return disagreements
    
    def propose_compromise(
        self,
        discussion: Discussion,
        disagreements: List[Dict[str, str]]
    ) -> DiscussionMessage:
        """
        Propose a compromise solution for the disagreements.
        
        Returns:
            A suggestion message with the proposed compromise
        """
        self.log("Proposing compromise")
        
        system_prompt = """You are a neutral facilitator proposing a compromise.

Given the different positions, suggest a middle-ground solution that:
1. Acknowledges each perspective
2. Identifies shared goals
3. Proposes a practical compromise
4. Explains why this compromise works

Be constructive and solution-oriented."""

        disagreement_text = "\n".join([
            f"- {d['agent']}: {d['issue']}"
            for d in disagreements
        ])
        
        user_prompt = f"""Topic: {discussion.topic_name}

Points of disagreement:
{disagreement_text}

Discussion context:
{discussion.format_history(max_messages=5)}

Propose a compromise that could satisfy all parties."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.5, max_tokens=400)
            
            return DiscussionMessage(
                sender="ModeratorAgent",
                recipient="all",
                message_type=MessageType.SUGGESTION,
                content=response.strip(),
                topic_id=discussion.topic_id
            )
        except Exception as e:
            self.log(f"Compromise proposal failed: {e}", "ERROR")
            return DiscussionMessage(
                sender="ModeratorAgent",
                recipient="all",
                message_type=MessageType.SUGGESTION,
                content="Consider finding common ground on the core requirements.",
                topic_id=discussion.topic_id
            )
    
    def format_for_human(
        self,
        discussion: Discussion,
        summary: str,
        question: str
    ) -> str:
        """
        Format a message for human escalation.
        
        Args:
            discussion: The discussion being escalated
            summary: Summary of the discussion
            question: Specific question for the human
            
        Returns:
            Formatted message for human
        """
        return f"""# Decision Required: {discussion.topic_name}

## Background
The team has been discussing this topic for {discussion.rounds_completed} rounds but could not reach consensus.

## Summary
{summary}

## Team Positions
{self._format_positions(discussion)}

## Your Decision Needed
{question}

Please provide your decision to continue the project development."""
    
    def _format_positions(self, discussion: Discussion) -> str:
        """Format participant positions for human review."""
        positions = {}
        
        for msg in discussion.messages:
            pref = msg.metadata.get('decision_preference', '')
            if pref and msg.sender not in positions:
                positions[msg.sender] = pref
        
        if not positions:
            return "No clear positions recorded."
        
        return "\n".join([f"- **{agent}**: {pos}" for agent, pos in positions.items()])
    
    def call_vote(
        self,
        discussion: Discussion,
        options: List[str]
    ) -> DiscussionMessage:
        """
        Create a vote message with options.
        
        Args:
            discussion: The discussion
            options: List of options to vote on
            
        Returns:
            A message calling for a vote
        """
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        return DiscussionMessage(
            sender="ModeratorAgent",
            recipient="all",
            message_type=MessageType.QUESTION,
            content=f"Please vote on the following options:\n\n{options_text}\n\nReply with your choice number and brief rationale.",
            topic_id=discussion.topic_id,
            metadata={'vote_options': options}
        )
    
    def determine_majority(self, votes: List[Tuple[str, str]]) -> Optional[str]:
        """
        Determine the majority decision from votes.
        
        Args:
            votes: List of (agent, choice) tuples
            
        Returns:
            Majority choice or None if no clear majority
        """
        if not votes:
            return None
        
        counts = {}
        for _, choice in votes:
            counts[choice] = counts.get(choice, 0) + 1
        
        # Need >50% for majority
        total = len(votes)
        for choice, count in counts.items():
            if count > total / 2:
                return choice
        
        return None
    
    def generate_decision_rationale(
        self,
        discussion: Discussion,
        decision: str
    ) -> str:
        """
        Generate a rationale for a decision.
        
        Args:
            discussion: The discussion that led to the decision
            decision: The decision made
            
        Returns:
            Rationale string
        """
        system_prompt = """Generate a brief rationale for a team decision.

The rationale should:
1. Summarize why this choice was made
2. Note key factors considered
3. Be 2-3 sentences

Be professional and objective."""

        user_prompt = f"""Topic: {discussion.topic_name}
Decision: {decision}
Discussion summary: {discussion.format_history(max_messages=5)}

Generate the rationale."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=150)
            return response.strip()
        except Exception as e:
            return f"Decision made after {discussion.rounds_completed} rounds of team discussion."
