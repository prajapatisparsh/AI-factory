"""
Discussion Topics - Predefined topics for agent discussions.
Each topic defines which agents participate and what decision is needed.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from enum import Enum


class TopicCategory(str, Enum):
    """Categories of discussion topics."""
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    USER_EXPERIENCE = "user_experience"
    DATA = "data"
    INTEGRATION = "integration"
    SCOPE = "scope"


@dataclass
class DiscussionTopic:
    """Definition of a discussion topic."""
    id: str
    name: str
    description: str
    category: TopicCategory
    participants: List[str]  # Agent names
    decision_required: str  # What needs to be decided
    max_rounds: int = 5
    requires_human_approval: bool = False
    context_keys: List[str] = field(default_factory=list)  # Keys to fetch from shared memory
    
    def get_opening_prompt(self) -> str:
        """Generate the opening prompt for this discussion."""
        return f"""We need to discuss and decide on: **{self.name}**

{self.description}

**Decision Required:** {self.decision_required}

Please share your professional perspective. Consider tradeoffs, best practices, and project constraints."""


# Predefined discussion topics
DISCUSSION_TOPICS = {
    # Architecture decisions
    "AUTH_APPROACH": DiscussionTopic(
        id="AUTH_APPROACH",
        name="Authentication Approach",
        description="Decide on the authentication strategy for the application.",
        category=TopicCategory.SECURITY,
        participants=["PMAgent", "TechLeadAgent", "DevTeamAgent-backend"],
        decision_required="Auth method: JWT, OAuth2, Session-based, or hybrid",
        context_keys=["project_type", "security_requirements"]
    ),
    
    "DATABASE_CHOICE": DiscussionTopic(
        id="DATABASE_CHOICE",
        name="Database Selection",
        description="Choose the primary database technology and justify the decision.",
        category=TopicCategory.DATA,
        participants=["TechLeadAgent", "DevTeamAgent-backend"],
        decision_required="Database type: PostgreSQL, MongoDB, MySQL, or other",
        context_keys=["data_requirements", "scale_expectations"]
    ),
    
    "API_SECURITY": DiscussionTopic(
        id="API_SECURITY",
        name="API Security Measures",
        description="Define security measures for all API endpoints.",
        category=TopicCategory.SECURITY,
        participants=["TechLeadAgent", "QAAgent", "DevTeamAgent-backend"],
        decision_required="Security measures: rate limiting, input validation, CORS policy",
        context_keys=["auth_approach", "threat_model"]
    ),
    
    "UI_FRAMEWORK": DiscussionTopic(
        id="UI_FRAMEWORK",
        name="Frontend Framework",
        description="Select the frontend framework and UI library.",
        category=TopicCategory.USER_EXPERIENCE,
        participants=["TechLeadAgent", "DevTeamAgent-frontend"],
        decision_required="Framework: React, Vue, Angular, or other; UI library choice",
        context_keys=["project_type", "team_expertise"]
    ),
    
    "STATE_MANAGEMENT": DiscussionTopic(
        id="STATE_MANAGEMENT",
        name="State Management Strategy",
        description="Decide on state management approach for the frontend.",
        category=TopicCategory.ARCHITECTURE,
        participants=["TechLeadAgent", "DevTeamAgent-frontend"],
        decision_required="State approach: Redux, Zustand, Context API, or other",
        context_keys=["ui_framework", "app_complexity"]
    ),
    
    # Scope decisions
    "SCOPE_VALIDATION": DiscussionTopic(
        id="SCOPE_VALIDATION",
        name="Scope Validation",
        description="Verify the extracted features and requirements are correct.",
        category=TopicCategory.SCOPE,
        participants=["PMAgent"],
        decision_required="Confirm or modify the extracted scope",
        requires_human_approval=True,
        max_rounds=1,
        context_keys=["extracted_features", "ambiguities"]
    ),
    
    "MVP_PRIORITIZATION": DiscussionTopic(
        id="MVP_PRIORITIZATION",
        name="MVP Feature Prioritization",
        description="Decide which features are essential for MVP vs. future releases.",
        category=TopicCategory.SCOPE,
        participants=["PMAgent", "TechLeadAgent"],
        decision_required="List of MVP-essential features vs. post-MVP features",
        requires_human_approval=True,
        context_keys=["all_features", "timeline", "resources"]
    ),
    
    # Integration decisions
    "THIRD_PARTY_INTEGRATIONS": DiscussionTopic(
        id="THIRD_PARTY_INTEGRATIONS",
        name="Third-Party Integrations",
        description="Decide on external services and APIs to integrate.",
        category=TopicCategory.INTEGRATION,
        participants=["TechLeadAgent", "DevTeamAgent-backend"],
        decision_required="List of third-party services with justification",
        context_keys=["features", "budget_constraints"]
    ),
    
    # Data decisions
    "DATA_MODEL": DiscussionTopic(
        id="DATA_MODEL",
        name="Core Data Model",
        description="Define the core data entities and their relationships.",
        category=TopicCategory.DATA,
        participants=["TechLeadAgent", "DevTeamAgent-backend", "PMAgent"],
        decision_required="Entity list with key relationships",
        context_keys=["user_stories", "features"]
    ),
    
    # Workflow-specific topics for team discussions
    "USER_STORIES_REVIEW": DiscussionTopic(
        id="USER_STORIES_REVIEW",
        name="User Stories Review",
        description="Review and refine generated user stories as a team.",
        category=TopicCategory.SCOPE,
        participants=["PMAgent", "TechLeadAgent", "QAAgent"],
        decision_required="Approved user stories with any refinements",
        max_rounds=2,
        context_keys=["features", "personas"]
    ),
    
    "ARCHITECTURE_REVIEW": DiscussionTopic(
        id="ARCHITECTURE_REVIEW",
        name="Architecture Review",
        description="Review the proposed architecture as a team and finalize decisions.",
        category=TopicCategory.ARCHITECTURE,
        participants=["TechLeadAgent", "PMAgent", "DevTeamAgent"],
        decision_required="Approved architecture with technology choices",
        max_rounds=2,
        context_keys=["user_stories", "project_type"]
    ),
    
    "SPEC_REVIEW": DiscussionTopic(
        id="SPEC_REVIEW",
        name="Specification Review",
        description="Review generated backend and frontend specifications.",
        category=TopicCategory.ARCHITECTURE,
        participants=["TechLeadAgent", "DevTeamAgent", "QAAgent"],
        decision_required="Approved specifications or list of required changes",
        max_rounds=2,
        context_keys=["architecture", "user_stories"]
    ),
    
    "QUALITY_ASSESSMENT": DiscussionTopic(
        id="QUALITY_ASSESSMENT",
        name="Quality Assessment",
        description="Assess the overall quality of generated specifications.",
        category=TopicCategory.SCOPE,
        participants=["QAAgent", "TechLeadAgent", "PMAgent"],
        decision_required="Quality score and approval/rejection decision",
        max_rounds=2,
        context_keys=["backend_spec", "frontend_spec", "qa_report"]
    ),
}


def get_topic(topic_id: str) -> Optional[DiscussionTopic]:
    """Get a discussion topic by ID."""
    return DISCUSSION_TOPICS.get(topic_id)


def get_topics_by_category(category: TopicCategory) -> List[DiscussionTopic]:
    """Get all topics in a category."""
    return [t for t in DISCUSSION_TOPICS.values() if t.category == category]


def get_topics_for_agent(agent_name: str) -> List[DiscussionTopic]:
    """Get all topics an agent participates in."""
    return [t for t in DISCUSSION_TOPICS.values() if agent_name in t.participants]
