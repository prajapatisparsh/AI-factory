"""
Interactive Refinement Module - Chat-based requirement refinement.
Allows users to refine requirements mid-pipeline through conversation.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from src.agents.base import BaseAgent
from src.schemas import DocumentAnalysis, UserStory


@dataclass
class RefinementMessage:
    """A single message in the refinement conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass  
class RefinementContext:
    """Context for the refinement session."""
    original_context: DocumentAnalysis
    user_stories: List[UserStory]
    architecture: str
    messages: List[RefinementMessage] = field(default_factory=list)
    refinements_applied: List[str] = field(default_factory=list)


class InteractiveRefiner(BaseAgent):
    """
    Interactive refinement agent for mid-pipeline adjustments.
    
    Usage:
        refiner = InteractiveRefiner()
        
        # Start refinement session
        session = refiner.start_session(context, user_stories, architecture)
        
        # User sends refinement request
        response, updated_context = refiner.refine(
            session,
            "Add Google OAuth authentication"
        )
        
        # Continue pipeline with updated context
    """
    
    def __init__(self):
        super().__init__(playbook_name=None)
    
    def get_agent_name(self) -> str:
        return "InteractiveRefiner"
    
    def start_session(
        self,
        context: DocumentAnalysis,
        user_stories: List[UserStory],
        architecture: str
    ) -> RefinementContext:
        """
        Start a new refinement session.
        
        Returns:
            RefinementContext for the session
        """
        self.log("Starting interactive refinement session")
        
        return RefinementContext(
            original_context=context,
            user_stories=user_stories,
            architecture=architecture,
            messages=[],
            refinements_applied=[]
        )
    
    def refine(
        self,
        session: RefinementContext,
        user_request: str
    ) -> Tuple[str, RefinementContext]:
        """
        Process a refinement request from the user.
        
        Args:
            session: Current refinement session
            user_request: User's refinement request
        
        Returns:
            Tuple of (assistant response, updated session)
        """
        self.log(f"Processing refinement: {user_request[:50]}...")
        
        # Add user message to history
        session.messages.append(RefinementMessage(
            role="user",
            content=user_request
        ))
        
        # Build conversation history
        history = "\n".join([
            f"{m.role.upper()}: {m.content}"
            for m in session.messages[-10:]  # Last 10 messages
        ])
        
        system_prompt = """You are an AI Product Manager helping refine MVP requirements.

Your role is to:
1. Understand the user's refinement request
2. Analyze how it impacts the current requirements
3. Suggest specific changes to user stories, architecture, or features
4. Ask clarifying questions if the request is ambiguous

CURRENT PROJECT CONTEXT:
- Project Type: Will be provided
- Features: Will be provided
- User Stories: Will be provided

RESPOND IN THIS FORMAT:
## Understanding
[Summarize what the user wants]

## Impact Analysis
[What parts of the current specs need to change]

## Proposed Changes
[Specific changes to make - be concrete]

## Questions (if any)
[Clarifying questions before proceeding]

## Ready to Apply?
[Yes/No - whether you have enough info to apply changes]
"""

        user_prompt = f"""CURRENT PROJECT:
Type: {session.original_context.project_type.value}
Features: {', '.join(session.original_context.features[:10])}

CURRENT USER STORIES ({len(session.user_stories)} total):
{chr(10).join(f'- {s.title}: {s.action}' for s in session.user_stories[:10])}

ARCHITECTURE SUMMARY:
{session.architecture[:1500]}

CONVERSATION HISTORY:
{history}

USER'S LATEST REQUEST:
{user_request}

Analyze this request and provide your response."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.5, max_tokens=2000)
            
            # Add assistant response to history
            session.messages.append(RefinementMessage(
                role="assistant",
                content=response
            ))
            
            # Check if ready to apply
            if "ready to apply?" in response.lower() and "yes" in response.lower():
                session.refinements_applied.append(user_request)
            
            self.log("Refinement response generated")
            return response, session
            
        except Exception as e:
            self.log(f"Refinement failed: {e}", "ERROR")
            error_response = f"Sorry, I encountered an error processing your request: {str(e)}"
            session.messages.append(RefinementMessage(
                role="assistant",
                content=error_response
            ))
            return error_response, session
    
    def apply_refinements(
        self,
        session: RefinementContext
    ) -> Tuple[List[UserStory], str]:
        """
        Apply approved refinements to generate updated specs.
        
        Returns:
            Tuple of (updated user stories, updated architecture notes)
        """
        if not session.refinements_applied:
            return session.user_stories, ""
        
        self.log(f"Applying {len(session.refinements_applied)} refinements")
        
        system_prompt = """You are a Product Manager applying requirement refinements.

Based on the refinements requested, generate:
1. NEW user stories to add
2. MODIFICATIONS to existing stories
3. STORIES to remove (if any)
4. ARCHITECTURE notes for the changes

FORMAT:
## New User Stories
[List new stories in format: US-NEW-001: Title - As a [role], I want [action] so that [benefit]]

## Modified Stories  
[List modified stories with changes noted]

## Removed Stories
[List stories to remove and why]

## Architecture Notes
[Any architectural changes needed]
"""

        refinements_text = "\n".join([f"- {r}" for r in session.refinements_applied])
        stories_text = "\n".join([
            f"- {s.id}: {s.title} - As a {s.user_role}, I want {s.action} ({s.priority.value})"
            for s in session.user_stories
        ])
        
        user_prompt = f"""CURRENT USER STORIES:
{stories_text}

REFINEMENTS TO APPLY:
{refinements_text}

Generate the updated specifications."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.4, max_tokens=2500)
            
            # For now, return original stories + architecture notes
            # In a full implementation, we'd parse and update the stories
            architecture_notes = f"\n\n## Refinements Applied\n{response}"
            
            self.log("Refinements applied")
            return session.user_stories, architecture_notes
            
        except Exception as e:
            self.log(f"Apply refinements failed: {e}", "ERROR")
            return session.user_stories, ""
    
    def get_quick_suggestions(
        self,
        session: RefinementContext
    ) -> List[str]:
        """
        Get quick refinement suggestions based on current context.
        
        Returns:
            List of suggested refinements
        """
        # Common refinement suggestions
        suggestions = [
            "Add user authentication with email/password",
            "Add Google/GitHub OAuth login",
            "Add email notification system",
            "Add admin dashboard for management",
            "Add data export functionality (CSV/PDF)",
            "Add API rate limiting",
            "Add comprehensive logging",
            "Add dark mode support",
            "Add mobile responsive design",
            "Add search functionality"
        ]
        
        # Filter out suggestions that might already be covered
        features_lower = " ".join(session.original_context.features).lower()
        
        filtered = [
            s for s in suggestions
            if not any(word in features_lower for word in s.lower().split()[:3])
        ]
        
        return filtered[:5]  # Return top 5 suggestions
