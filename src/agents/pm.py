"""
Product Manager Agent - Three responsibilities:
1. Phase 2: Generate user stories from requirements
2. Phase 3: Answer clarification questions
3. Phase 7: Evaluate final specifications (Gatekeeper)
"""

from typing import List, Dict, Optional
import json

from src.agents.base import BaseAgent, AgentError
from src.schemas import (
    DocumentAnalysis, 
    UserStory, 
    UserStoriesCollection,
    PMEvaluation,
    ScoreBreakdown,
    EvaluationStatus,
    ClarificationQuestion
)


class PMAgent(BaseAgent):
    """
    Product Manager agent responsible for:
    - Generating user stories from requirements
    - Answering technical clarification questions
    - Final quality evaluation (gatekeeper role)
    """
    
    def __init__(self):
        super().__init__(playbook_name="pm")
    
    def get_agent_name(self) -> str:
        return "PMAgent"
    
    def generate_user_stories(self, context: DocumentAnalysis) -> List[UserStory]:
        """
        Phase 2: Generate user stories from document analysis.
        
        Args:
            context: Parsed document analysis
        
        Returns:
            List of UserStory objects (5-20 stories)
        """
        self.log("Generating user stories from requirements")
        
        base_system = """You are an experienced Product Manager creating user stories.

Create comprehensive user stories that:
1. Cover ALL features mentioned in the requirements
2. Include acceptance criteria that are testable and measurable
3. Prioritize based on business value and dependencies
4. Map each story to a specific user persona
5. Use the format: "As a [role], I want [action] so that [benefit]"

Each story must have:
- Unique ID (US-001, US-002, etc.)
- Clear title
- User role from the personas
- Specific action
- Clear benefit
- 2-5 measurable acceptance criteria
- Priority (Critical/High/Medium/Low)"""

        system_prompt = self.build_system_prompt(base_system)
        
        user_prompt = f"""Based on this requirements analysis, create 5-20 comprehensive user stories:

PROJECT TYPE: {context.project_type.value}

FEATURES TO COVER:
{chr(10).join(f'- {f}' for f in context.features)}

USER PERSONAS:
{chr(10).join(f'- {p}' for p in context.personas)}

TECHNOLOGY HINTS:
{chr(10).join(f'- {t}' for t in context.tech_hints)}

AMBIGUITIES TO ADDRESS:
{chr(10).join(f'- {a}' for a in context.ambiguities)}

FULL REQUIREMENTS:
{context.full_text[:3000]}

Return a JSON object with a "stories" array containing user story objects.
Each story must have: id, title, user_role, action, benefit, acceptance_criteria (array), priority.
Example:
{{
    "stories": [
        {{
            "id": "US-001",
            "title": "User Registration",
            "user_role": "New User",
            "action": "create an account with email and password",
            "benefit": "I can access the platform's features",
            "acceptance_criteria": [
                "Email format is validated",
                "Password must be at least 8 characters",
                "Confirmation email is sent"
            ],
            "priority": "Critical"
        }}
    ]
}}"""

        try:
            success, stories_collection, error = self.call_llm_json(
                system_prompt, 
                user_prompt, 
                UserStoriesCollection
            )
            
            if success and stories_collection:
                self.log(f"Generated {len(stories_collection.stories)} user stories")
                return stories_collection.stories
            else:
                self.log(f"Story generation failed: {error}", "WARNING")
                # Try to parse response manually
                return self._fallback_story_generation(context)
                
        except Exception as e:
            self.log(f"User story generation error: {e}", "ERROR")
            return self._fallback_story_generation(context)
    
    def _fallback_story_generation(self, context: DocumentAnalysis) -> List[UserStory]:
        """Generate context-aware user stories when main generation fails."""
        self.log("Using fallback story generation with smart defaults", "WARNING")
        
        stories = []
        
        # Priority assignment based on position (first features tend to be more important)
        def get_priority(index: int) -> str:
            if index <= 2:
                return "Critical"
            elif index <= 5:
                return "High"
            elif index <= 8:
                return "Medium"
            return "Low"
        
        # Generate context-aware acceptance criteria based on feature keywords
        def generate_acceptance_criteria(feature: str) -> List[str]:
            feature_lower = feature.lower()
            criteria = []
            
            # Authentication-related
            if any(kw in feature_lower for kw in ['login', 'auth', 'signin', 'register', 'signup']):
                criteria = [
                    "Email validation rejects invalid formats (e.g., missing @, invalid domain)",
                    "Password requires minimum 8 characters with at least 1 number and 1 special character",
                    "Login attempt limit of 5 failures before 15-minute lockout",
                    "Session expires after 24 hours of inactivity"
                ]
            # Payment/billing related
            elif any(kw in feature_lower for kw in ['payment', 'checkout', 'billing', 'subscription', 'purchase']):
                criteria = [
                    "Payment processing completes within 10 seconds",
                    "Failed transactions display clear error messages with retry option",
                    "Receipt/confirmation email sent within 2 minutes of successful payment",
                    "Payment information is never stored in plain text"
                ]
            # Search/filter related
            elif any(kw in feature_lower for kw in ['search', 'filter', 'find', 'browse']):
                criteria = [
                    "Search results return within 2 seconds for queries up to 100 characters",
                    "Minimum 3 characters required before search executes",
                    "Empty results display helpful suggestions or alternatives",
                    "Search history is saved for logged-in users"
                ]
            # Dashboard/analytics related
            elif any(kw in feature_lower for kw in ['dashboard', 'analytics', 'report', 'stats']):
                criteria = [
                    "Dashboard loads within 3 seconds on standard connection",
                    "Data refreshes automatically every 60 seconds",
                    "Date range filter allows custom start/end dates",
                    "Export to CSV/PDF completes within 30 seconds for up to 10,000 records"
                ]
            # Profile/settings related
            elif any(kw in feature_lower for kw in ['profile', 'settings', 'account', 'preferences']):
                criteria = [
                    "All changes require confirmation before saving",
                    "Profile photo upload accepts JPG/PNG up to 5MB",
                    "Email change requires verification via link sent to new address",
                    "Password change requires current password confirmation"
                ]
            # Notification related
            elif any(kw in feature_lower for kw in ['notification', 'alert', 'message', 'email']):
                criteria = [
                    "Notifications appear within 5 seconds of triggering event",
                    "User can enable/disable notification types individually",
                    "Unread notifications clearly distinguished visually",
                    "Notification history retained for 30 days"
                ]
            # Upload/media related
            elif any(kw in feature_lower for kw in ['upload', 'image', 'file', 'media', 'document']):
                criteria = [
                    "Supported formats clearly listed before upload",
                    "Progress indicator shows during upload",
                    "Maximum file size of 25MB with clear error for oversized files",
                    "Upload can be cancelled mid-progress"
                ]
            # Default criteria
            else:
                criteria = [
                    f"Feature completes primary action within 3 seconds",
                    f"Error states display user-friendly messages with recovery steps",
                    f"Loading states shown for operations exceeding 500ms",
                    f"Feature is accessible via keyboard navigation"
                ]
            
            return criteria[:4]  # Return max 4 criteria
        
        for i, feature in enumerate(context.features[:10], 1):
            persona = context.personas[i % len(context.personas)] if context.personas else "User"
            priority = get_priority(i)
            
            # Generate specific action based on feature name
            feature_action = feature.lower()
            if feature_action.startswith(('user ', 'admin ', 'customer ')):
                feature_action = feature_action.split(' ', 1)[1] if ' ' in feature else feature_action
            
            story = UserStory(
                id=f"US-{i:03d}",
                title=feature[:100],
                user_role=persona,
                action=f"access and use {feature_action}",
                benefit=f"I can {self._infer_benefit(feature)}",
                acceptance_criteria=generate_acceptance_criteria(feature),
                priority=priority
            )
            stories.append(story)
        
        return stories
    
    def _infer_benefit(self, feature: str) -> str:
        """Infer a specific benefit based on the feature name."""
        feature_lower = feature.lower()
        
        if any(kw in feature_lower for kw in ['login', 'auth', 'register']):
            return "securely access my account and personal data"
        elif any(kw in feature_lower for kw in ['payment', 'checkout', 'purchase']):
            return "complete transactions quickly and securely"
        elif any(kw in feature_lower for kw in ['search', 'filter', 'find']):
            return "quickly locate the information I need"
        elif any(kw in feature_lower for kw in ['dashboard', 'analytics', 'report']):
            return "make data-driven decisions based on insights"
        elif any(kw in feature_lower for kw in ['profile', 'settings', 'account']):
            return "customize my experience and manage my information"
        elif any(kw in feature_lower for kw in ['notification', 'alert']):
            return "stay informed about important updates in real-time"
        elif any(kw in feature_lower for kw in ['upload', 'file', 'media']):
            return "share and manage my content efficiently"
        else:
            return "accomplish my task efficiently and effectively"
    
    def answer_clarifications(
        self,
        questions: List[ClarificationQuestion],
        context: DocumentAnalysis,
        user_stories: List[UserStory]
    ) -> Dict[str, str]:
        """
        Phase 3: Answer clarification questions from the dev team.
        
        Args:
            questions: List of questions needing answers
            context: Original document analysis
            user_stories: Generated user stories
        
        Returns:
            Dict mapping question_id to answer
        """
        self.log(f"Answering {len(questions)} clarification questions")
        
        if not questions:
            return {}
        
        base_system = """You are a Product Manager answering technical clarification questions.

Provide clear, actionable answers that:
1. Reference specific requirements when available
2. Make reasonable decisions for ambiguous cases
3. Prioritize user experience and security
4. Consider scalability implications
5. Flag when a decision needs stakeholder input"""

        system_prompt = self.build_system_prompt(base_system)
        
        # Format questions
        questions_text = "\n".join([
            f"Q{i+1} (ID: {q.id}): {q.question}\nContext: {q.context}"
            for i, q in enumerate(questions)
        ])
        
        # Format user stories for context
        stories_summary = "\n".join([
            f"- {s.id}: {s.title} ({s.priority})"
            for s in user_stories[:10]
        ])
        
        user_prompt = f"""Answer these clarification questions based on the project requirements:

PROJECT CONTEXT:
Type: {context.project_type.value}
Features: {', '.join(context.features[:5])}

USER STORIES:
{stories_summary}

QUESTIONS:
{questions_text}

Return JSON with answers for each question ID:
{{
    "{questions[0].id if questions else 'Q1'}": "Your detailed answer here",
    ...
}}"""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.5)
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                answers = json.loads(json_match.group())
                self.log(f"Provided {len(answers)} answers")
                return answers
            
            # Fallback: Generate intelligent answers based on question context
            self.log("JSON parsing failed, using intelligent fallback", "WARNING")
            return self._generate_fallback_answers(questions, context)
            
        except Exception as e:
            self.log(f"Clarification answering failed: {e}, using smart fallback", "WARNING")
            return self._generate_fallback_answers(questions, context)
    
    def _generate_fallback_answers(
        self,
        questions: List[ClarificationQuestion],
        context: DocumentAnalysis
    ) -> Dict[str, str]:
        """Generate intelligent fallback answers based on question content and project context."""
        answers = {}
        
        for q in questions:
            question_lower = q.question.lower()
            
            # Authentication related questions
            if any(kw in question_lower for kw in ['auth', 'login', 'password', 'session', 'token']):
                answers[q.id] = (
                    "Use JWT-based authentication with refresh tokens. Passwords should be hashed "
                    "with bcrypt (cost factor 12). Sessions expire after 24 hours of inactivity. "
                    "Implement rate limiting at 5 failed attempts per 15 minutes."
                )
            # Database/storage questions
            elif any(kw in question_lower for kw in ['database', 'storage', 'data', 'persist', 'store']):
                answers[q.id] = (
                    "Use PostgreSQL as the primary database with proper indexing on frequently "
                    "queried columns. Implement soft deletes for data retention. Use connection "
                    "pooling for performance (max 20 connections per instance)."
                )
            # Performance/scalability questions
            elif any(kw in question_lower for kw in ['performance', 'scale', 'load', 'cache', 'speed']):
                answers[q.id] = (
                    "Implement Redis for session caching and frequently accessed data. Use "
                    "pagination with a default of 20 items per page. Add database indexes on "
                    "foreign keys and frequently filtered columns. Target <200ms response time."
                )
            # API/endpoint questions
            elif any(kw in question_lower for kw in ['api', 'endpoint', 'rest', 'request', 'response']):
                answers[q.id] = (
                    "Follow RESTful conventions with JSON request/response format. Include "
                    "proper error codes (400 for validation, 401 for auth, 403 for permissions, "
                    "404 for not found, 500 for server errors). Implement request validation "
                    "at the controller level."
                )
            # Security questions
            elif any(kw in question_lower for kw in ['security', 'protect', 'encrypt', 'secure', 'xss', 'sql']):
                answers[q.id] = (
                    "Implement input sanitization on all user inputs. Use parameterized queries "
                    "to prevent SQL injection. Enable HTTPS only. Add CSRF tokens for form "
                    "submissions. Set appropriate CORS headers for the production domain only."
                )
            # UI/UX questions
            elif any(kw in question_lower for kw in ['ui', 'ux', 'design', 'interface', 'user experience']):
                answers[q.id] = (
                    "Follow a mobile-first responsive design approach. Ensure WCAG 2.1 AA "
                    "accessibility compliance. Use loading spinners for operations >300ms. "
                    "Implement form validation with inline error messages."
                )
            # Validation/error handling questions
            elif any(kw in question_lower for kw in ['valid', 'error', 'handling', 'exception']):
                answers[q.id] = (
                    "Implement validation at both frontend and backend. Return structured error "
                    "responses with error codes and user-friendly messages. Log all errors with "
                    "stack traces for debugging. Show users actionable recovery steps."
                )
            # File/upload questions
            elif any(kw in question_lower for kw in ['file', 'upload', 'image', 'media', 'document']):
                answers[q.id] = (
                    "Support common file formats (JPG, PNG, PDF) with a 25MB maximum size. "
                    "Scan uploads for malware. Store files in cloud storage (S3 or equivalent) "
                    "with CDN delivery. Generate thumbnails for images asynchronously."
                )
            # Notification questions
            elif any(kw in question_lower for kw in ['notification', 'email', 'alert', 'message']):
                answers[q.id] = (
                    "Use a queue-based email service (SendGrid, SES) for reliability. Allow "
                    "users to configure notification preferences. Implement in-app notifications "
                    "with WebSocket for real-time updates. Batch non-urgent emails hourly."
                )
            # Default answer with context
            else:
                project_type = context.project_type.value
                answers[q.id] = (
                    f"For this {project_type} project, follow industry best practices. "
                    f"This decision will be documented in the technical specification. "
                    f"If this requires stakeholder input, flag it during implementation review. "
                    f"Context from requirements: {', '.join(context.features[:3])}."
                )
        
        return answers
    
    def evaluate_specifications(
        self,
        context: DocumentAnalysis,
        user_stories: List[UserStory],
        architecture: str,
        backend_spec: str,
        frontend_spec: str,
        qa_report: str,
        previous_scolding: str = ""
    ) -> PMEvaluation:
        """
        Phase 7: Evaluate all specifications as gatekeeper.
        
        Args:
            context: Original requirements
            user_stories: Generated user stories
            architecture: Architecture specification
            backend_spec: Backend specification
            frontend_spec: Frontend specification
            qa_report: QA report
            previous_scolding: Previous rejection feedback (if retry)
        
        Returns:
            PMEvaluation with score and detailed feedback
        """
        self.log("Evaluating final specifications")
        
        base_system = """You are a senior Product Manager performing final quality evaluation.

Score the specifications strictly using this rubric:
- Requirements Coverage (0-30): Are ALL features from requirements addressed?
- Architecture Soundness (0-25): Is the tech stack appropriate? Will it scale?
- Specification Completeness (0-20): Is there enough detail to implement?
- QA Compliance (0-15): Were critical issues from QA addressed?
- Security (0-10): Is there proper auth, input validation, data protection?

Be STRICT. A score of 90+ means production-ready. Most first drafts score 60-80.

If REJECTING (score < 90), provide detailed scolding in this format:
WHAT: [specific issue]
WHY: [impact on users/business]
FIX: [concrete guidance for improvement]"""

        system_prompt = self.build_system_prompt(base_system)
        
        # Include previous feedback if this is a retry
        retry_context = ""
        if previous_scolding:
            retry_context = f"""
PREVIOUS REJECTION FEEDBACK (must be addressed):
{previous_scolding}

This is a RETRY. The issues above MUST be fixed or explained.
"""
        
        user_prompt = f"""Evaluate these MVP specifications:

{retry_context}

ORIGINAL REQUIREMENTS:
Type: {context.project_type.value}
Features: {', '.join(context.features)}
Personas: {', '.join(context.personas)}

USER STORIES ({len(user_stories)} total):
{chr(10).join(f'- {s.id}: {s.title}' for s in user_stories[:10])}

ARCHITECTURE (excerpt):
{architecture[:2000] if architecture else 'No architecture provided'}

BACKEND SPEC (excerpt):
{backend_spec[:2000] if backend_spec else 'No backend spec provided'}

FRONTEND SPEC (excerpt):
{frontend_spec[:2000] if frontend_spec else 'No frontend spec provided'}

QA REPORT (excerpt):
{qa_report[:1500] if qa_report else 'No QA report provided'}

Return JSON evaluation:
{{
    "score": <0-100>,
    "status": "APPROVED" or "REJECTED",
    "breakdown": {{
        "requirements": <0-30>,
        "architecture": <0-25>,
        "completeness": <0-20>,
        "qa_compliance": <0-15>,
        "security": <0-10>
    }},
    "strengths": ["list of things done well"],
    "issues": ["list of issues found (if rejecting)"],
    "scolding": "Detailed WHAT/WHY/FIX feedback (if rejecting)"
}}

CRITICAL: Return ONLY the JSON object with actual evaluation data. 
DO NOT return the schema definition.
DO NOT include any markdown code blocks.
DO NOT include explanatory text before or after the JSON.
Just return the raw JSON object."""

        try:
            success, evaluation, error = self.call_llm_json(
                system_prompt,
                user_prompt,
                PMEvaluation
            )
            
            if success and evaluation:
                self.log(f"Evaluation complete: {evaluation.status.value} ({evaluation.score})")
                return evaluation
            else:
                self.log(f"Evaluation parsing failed: {error}", "WARNING")
                # Try fallback with more lenient scoring
                return self._fallback_evaluation()
                
        except Exception as e:
            self.log(f"Evaluation failed: {e}", "ERROR")
            return self._fallback_evaluation()
    
    def _fallback_evaluation(self) -> PMEvaluation:
        """Return conservative evaluation when parsing fails."""
        return PMEvaluation(
            score=70,
            status=EvaluationStatus.REJECTED,
            breakdown=ScoreBreakdown(
                requirements=20,
                architecture=15,
                completeness=15,
                qa_compliance=10,
                security=10
            ),
            strengths=["Specifications were generated"],
            issues=["Evaluation could not be completed properly"],
            scolding="""WHAT: Evaluation system encountered an error
WHY: Cannot guarantee specification quality
FIX: Review specifications manually before proceeding"""
        )
    
    def format_user_stories_markdown(self, stories: List[UserStory]) -> str:
        """Format user stories as Markdown document."""
        lines = ["# User Stories\n"]
        lines.append(f"*Generated {len(stories)} user stories*\n")
        
        # Group by priority
        priority_order = ["Critical", "High", "Medium", "Low"]
        
        for priority in priority_order:
            priority_stories = [s for s in stories if s.priority.value == priority]
            if priority_stories:
                lines.append(f"\n## {priority} Priority\n")
                
                for story in priority_stories:
                    lines.append(f"### {story.id}: {story.title}\n")
                    lines.append(f"**As a** {story.user_role}, **I want** {story.action} **so that** {story.benefit}.\n")
                    lines.append("\n**Acceptance Criteria:**")
                    for ac in story.acceptance_criteria:
                        lines.append(f"- [ ] {ac}")
                    lines.append("")
        
        return "\n".join(lines)
