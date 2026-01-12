"""
Discussion Renderer - Streamlit UI components for displaying team discussions.
"""

import streamlit as st
from typing import List, Optional, Dict, Any
from src.discussion.protocol import Discussion, DiscussionMessage, MessageType, ConsensusStatus


# Agent emoji mapping for visual distinction
AGENT_EMOJIS = {
    "PMAgent": "👔",
    "TechLeadAgent": "🏗️",
    "DevTeamAgent": "💻",
    "DevTeamAgent-backend": "⚙️",
    "DevTeamAgent-frontend": "🎨",
    "QAAgent": "🔍",
    "ModeratorAgent": "🎯",
    "VisionAgent": "👁️",
    "CoachAgent": "📚",
}

# Agent friendly names
AGENT_NAMES = {
    "PMAgent": "Product Manager",
    "TechLeadAgent": "Tech Lead",
    "DevTeamAgent": "Dev Team",
    "DevTeamAgent-backend": "Backend Dev",
    "DevTeamAgent-frontend": "Frontend Dev",
    "QAAgent": "QA Engineer",
    "ModeratorAgent": "Moderator",
    "VisionAgent": "Vision Agent",
    "CoachAgent": "Coach",
}

# Message type styling
MESSAGE_TYPE_STYLES = {
    MessageType.PROPOSAL: ("💡", "Proposes"),
    MessageType.QUESTION: ("❓", "Asks"),
    MessageType.ANSWER: ("💬", "Answers"),
    MessageType.AGREEMENT: ("✅", "Agrees"),
    MessageType.DISAGREEMENT: ("❌", "Disagrees"),
    MessageType.SUGGESTION: ("💭", "Suggests"),
    MessageType.DECISION: ("🎯", "Decides"),
    MessageType.SUMMARY: ("📋", "Summarizes"),
}


def render_discussion(discussion: Discussion, expanded: bool = True) -> None:
    """
    Render a complete discussion in Streamlit UI.
    
    Args:
        discussion: The Discussion object to render
        expanded: Whether the expander should be open by default
    """
    status_icon = _get_status_icon(discussion.status)
    
    with st.expander(f"{status_icon} {discussion.topic_name}", expanded=expanded):
        # Show discussion summary
        st.caption(f"📍 {len(discussion.messages)} messages | {discussion.rounds_completed} rounds | Status: {discussion.status.value}")
        
        # Render each message
        for message in discussion.messages:
            render_message(message)
        
        # Show final decision if reached
        if discussion.decision:
            st.divider()
            st.success(f"**✅ Decision:** {discussion.decision}")
            if discussion.decision_rationale:
                st.info(f"**📝 Rationale:** {discussion.decision_rationale}")


def render_message(message: DiscussionMessage) -> None:
    """
    Render a single discussion message.
    
    Args:
        message: The DiscussionMessage to render
    """
    agent_emoji = AGENT_EMOJIS.get(message.sender, "🤖")
    agent_name = AGENT_NAMES.get(message.sender, message.sender)
    type_icon, type_verb = MESSAGE_TYPE_STYLES.get(message.message_type, ("💬", "Says"))
    
    # Create a styled message container
    with st.container():
        col1, col2 = st.columns([1, 15])
        
        with col1:
            st.markdown(f"### {agent_emoji}")
        
        with col2:
            # Header with agent name and action
            st.markdown(f"**{agent_name}** {type_verb}:")
            
            # Message content
            st.markdown(message.content)
        
        st.markdown("---")


def render_discussion_summary(discussions: List[Discussion]) -> None:
    """
    Render a summary of multiple discussions.
    
    Args:
        discussions: List of Discussion objects
    """
    st.subheader("📋 Discussion Summary")
    
    for discussion in discussions:
        status_icon = _get_status_icon(discussion.status)
        
        if discussion.decision:
            st.markdown(f"{status_icon} **{discussion.topic_name}:** {discussion.decision}")
        else:
            st.markdown(f"{status_icon} **{discussion.topic_name}:** No decision reached")


def render_team_activity(
    phase_name: str,
    discussions: List[Discussion],
    additional_output: Optional[str] = None
) -> None:
    """
    Render a complete phase with all its discussions.
    
    Args:
        phase_name: Name of the phase
        discussions: List of discussions that occurred
        additional_output: Any additional output to show
    """
    st.header(phase_name)
    
    if discussions:
        # Create tabs for each discussion
        if len(discussions) == 1:
            render_discussion(discussions[0], expanded=True)
        else:
            tabs = st.tabs([d.topic_name for d in discussions])
            for tab, discussion in zip(tabs, discussions):
                with tab:
                    render_discussion(discussion, expanded=True)
        
        # Show decisions summary
        decisions = [d for d in discussions if d.decision]
        if decisions:
            with st.expander("📊 Decisions Made", expanded=False):
                for d in decisions:
                    st.markdown(f"- **{d.topic_name}:** {d.decision}")
    
    if additional_output:
        with st.expander("📄 Generated Output", expanded=False):
            st.markdown(additional_output)


def render_quick_discussion(
    topic: str,
    messages: List[Dict[str, str]],
    decision: str,
    rationale: Optional[str] = None
) -> None:
    """
    Render a simplified discussion view (for simulated discussions).
    
    Args:
        topic: Discussion topic name
        messages: List of dicts with 'agent' and 'content' keys
        decision: Final decision
        rationale: Optional rationale for the decision
    """
    with st.expander(f"💬 {topic}", expanded=True):
        for msg in messages:
            agent = msg.get('agent', 'Agent')
            content = msg.get('content', '')
            emoji = AGENT_EMOJIS.get(agent, "🤖")
            name = AGENT_NAMES.get(agent, agent)
            
            st.markdown(f"**{emoji} {name}:** {content}")
        
        st.divider()
        st.success(f"**✅ Decision:** {decision}")
        if rationale:
            st.caption(f"📝 {rationale}")


def _get_status_icon(status: ConsensusStatus) -> str:
    """Get icon for consensus status."""
    icons = {
        ConsensusStatus.PENDING: "⏳",
        ConsensusStatus.AGREED: "✅",
        ConsensusStatus.DISAGREED: "⚠️",
        ConsensusStatus.ESCALATED: "🆘",
        ConsensusStatus.TIMEOUT: "⏱️",
    }
    return icons.get(status, "❓")


def create_simulated_discussion(
    topic_name: str,
    agents: List[str],
    context: str,
    decision: str,
    rationale: str
) -> Discussion:
    """
    Create a simulated discussion for UI display.
    
    This is useful when we want to show discussion-style output
    without running the full orchestrator.
    """
    from datetime import datetime
    
    discussion = Discussion(
        topic_id=topic_name.upper().replace(" ", "_"),
        topic_name=topic_name,
        participants=agents
    )
    
    # Add a proposal message from first agent
    if agents:
        discussion.add_message(DiscussionMessage(
            sender=agents[0],
            message_type=MessageType.PROPOSAL,
            content=f"Based on the context, I propose we consider: {context[:200]}...",
            topic_id=discussion.topic_id
        ))
    
    # Add agreement from others
    for agent in agents[1:]:
        discussion.add_message(DiscussionMessage(
            sender=agent,
            message_type=MessageType.AGREEMENT,
            content=f"I agree with this approach. {rationale[:100]}...",
            topic_id=discussion.topic_id
        ))
    
    # Finalize
    discussion.decision = decision
    discussion.decision_rationale = rationale
    discussion.status = ConsensusStatus.AGREED
    discussion.ended_at = datetime.now().isoformat()
    
    return discussion
