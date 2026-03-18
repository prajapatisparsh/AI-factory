"""
Tech Lead Agent - Architecture and system design.
Generates comprehensive technical architecture specifications.
"""

from typing import List, Optional

from src.agents.base import BaseAgent, AgentError
from src.schemas import DocumentAnalysis, UserStory


class TechLeadAgent(BaseAgent):
    """
    Tech Lead agent responsible for:
    - Creating system architecture
    - Selecting technology stack
    - Designing database schema
    - Planning API structure
    - Security and scalability strategy
    """
    
    def __init__(self):
        super().__init__(playbook_name="tech_lead")
    
    def get_agent_name(self) -> str:
        return "TechLeadAgent"
    
    def generate_architecture(
        self,
        context: DocumentAnalysis,
        user_stories: List[UserStory]
    ) -> str:
        """
        Phase 2: Generate comprehensive architecture specification.
        
        Args:
            context: Document analysis with requirements
            user_stories: Generated user stories
        
        Returns:
            Architecture specification as Markdown
        """
        self.log("Generating architecture specification")
        
        base_system = """You are a senior Technical Architect designing MVP architecture.

Create a comprehensive architecture document that includes:
1. **Technology Stack** - Justified choices for each layer
2. **System Architecture** - High-level component diagram description
3. **Database Design** - Schema with tables, relationships, indexes
4. **API Design** - RESTful endpoints with methods and payloads
5. **Security Strategy** - Authentication, authorization, data protection
6. **Scalability Plan** - How the system handles growth
7. **Observability** - Logging, monitoring, alerting approach

MANDATORY RULES:
- If the client specified a technology in "Technology Hints", USE IT unless it presents a known security vulnerability. Document any overrides with justification.
- Include SPECIFIC stable version numbers for every library (e.g., FastAPI 0.109.0 — not "latest").
- Every API design MUST include a rate limiting strategy (requests/minute per endpoint).
- Any JWT-based auth MUST specify refresh token rotation strategy and token expiry.
- Every architecture MUST include a DB connection pool size, max overflow, and timeout.

Design for:
- Clean separation of concerns
- Horizontal scalability
- Security by default
- Developer experience
- Production readiness"""

        system_prompt = self.build_system_prompt(base_system)
        
        # Summarize user stories for context
        stories_summary = "\n".join([
            f"- {s.id} ({s.priority.value}): {s.title} - {s.action}"
            for s in user_stories
        ])
        
        # Identify key features that need special consideration
        critical_stories = [s for s in user_stories if s.priority.value == "Critical"]
        critical_features = "\n".join([f"- {s.title}: {s.action}" for s in critical_stories])
        
        user_prompt = f"""Design the architecture for this MVP:

## Project Overview
- Type: {context.project_type.value}
- Features: {', '.join(context.features)}
- User Personas: {', '.join(context.personas)}

## Technology Hints from Requirements
{chr(10).join(f'- {t}' for t in context.tech_hints) if context.tech_hints else '- No specific technology requirements'}

## User Stories to Support
{stories_summary}

## Critical Features (must be robust)
{critical_features if critical_features else '- All features should be production-ready'}

## Known Ambiguities
{chr(10).join(f'- {a}' for a in context.ambiguities) if context.ambiguities else '- None identified'}

Generate a comprehensive Markdown architecture document with all sections listed above.
Include specific technology versions, database schemas, and API endpoint definitions.
Justify each technology choice based on the requirements."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.4, max_tokens=4000)
            
            # Ensure proper markdown formatting
            architecture = self._format_architecture(response)
            self.log("Architecture specification generated")
            return architecture
            
        except AgentError as e:
            self.log(f"Architecture generation failed: {e}", "ERROR")
            return self._fallback_architecture(context, user_stories)
        except Exception:
            raise  # Let programming bugs surface
    
    def _format_architecture(self, raw_response: str) -> str:
        """Format and validate architecture document."""
        # Ensure it starts with a title
        if not raw_response.strip().startswith('#'):
            raw_response = f"# Architecture Specification\n\n{raw_response}"
        
        # Add standard sections if missing
        required_sections = [
            "Technology Stack",
            "Database",
            "API",
            "Security",
            "Scalability"
        ]
        
        content = raw_response
        
        # Check for missing sections and add placeholders
        for section in required_sections:
            if section.lower() not in content.lower():
                content += f"\n\n## {section}\n\n*[Section to be detailed during implementation]*\n"
        
        return content
    
    def _fallback_architecture(
        self,
        context: DocumentAnalysis,
        user_stories: List[UserStory]
    ) -> str:
        """Generate minimal architecture when main generation fails."""
        self.log("Using fallback architecture template", "WARNING")
        
        project_type = context.project_type.value
        
        # Determine default stack based on project type
        stack = self._get_default_stack(project_type)
        
        features_list = "\n".join([f"- {f}" for f in context.features])
        stories_list = "\n".join([f"- {s.title}" for s in user_stories[:10]])
        
        return f"""# Architecture Specification

*⚠️ Auto-generated fallback architecture - requires manual review*

## Project Overview

**Type:** {project_type}
**Features:**
{features_list}

## Technology Stack

### Backend
- **Runtime:** {stack['backend_runtime']}
- **Framework:** {stack['backend_framework']}
- **Database:** {stack['database']}

### Frontend
- **Framework:** {stack['frontend_framework']}
- **Styling:** {stack['styling']}

### Infrastructure
- **Hosting:** {stack['hosting']}
- **Authentication:** {stack['auth']}

## Database Design

*Schema to be detailed based on user stories:*
{stories_list}

### Core Tables (to be designed)
- Users - authentication and profiles
- [Feature-specific tables based on requirements]

## API Design

### Base URL
`/api/v1`

### Endpoints (to be detailed)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Current user
- [Feature-specific endpoints]

## Security Strategy

1. **Authentication:** JWT-based with refresh tokens
2. **Authorization:** Role-based access control (RBAC)
3. **Data Protection:** 
   - HTTPS only
   - Password hashing (bcrypt)
   - Input validation on all endpoints
4. **API Security:**
   - Rate limiting
   - CORS configuration
   - Request validation

## Scalability Plan

1. **Database:** Connection pooling, read replicas for scale
2. **API:** Stateless design for horizontal scaling
3. **Caching:** Redis for session and frequently accessed data
4. **CDN:** Static assets served via CDN

## Observability

1. **Logging:** Structured JSON logs
2. **Monitoring:** Health check endpoints
3. **Alerts:** Error rate thresholds

---
*This is a template architecture. Detailed specifications will be provided in backend and frontend documents.*
"""
    
    def _get_default_stack(self, project_type: str) -> dict:
        """Get default technology stack based on project type."""
        stacks = {
            "web_app": {
                "backend_runtime": "Node.js 20 LTS",
                "backend_framework": "Express.js / NestJS",
                "database": "PostgreSQL 16",
                "frontend_framework": "React 18 / Next.js 14",
                "styling": "Tailwind CSS",
                "hosting": "Vercel / AWS",
                "auth": "NextAuth.js / Auth0"
            },
            "mobile_app": {
                "backend_runtime": "Node.js 20 LTS",
                "backend_framework": "Express.js with REST API",
                "database": "PostgreSQL 16",
                "frontend_framework": "React Native / Flutter",
                "styling": "StyleSheet / Theme",
                "hosting": "AWS / Firebase",
                "auth": "Firebase Auth"
            },
            "api": {
                "backend_runtime": "Python 3.11+ / Node.js 20",
                "backend_framework": "FastAPI / Express.js",
                "database": "PostgreSQL 16",
                "frontend_framework": "N/A (API only)",
                "styling": "N/A",
                "hosting": "AWS Lambda / Railway",
                "auth": "JWT / OAuth2"
            },
            "desktop": {
                "backend_runtime": "Node.js 20 / Python 3.11",
                "backend_framework": "Electron / Tauri",
                "database": "SQLite / PostgreSQL",
                "frontend_framework": "React / Svelte",
                "styling": "Tailwind CSS",
                "hosting": "Local / Auto-update server",
                "auth": "Local credentials / OAuth"
            },
            "other": {
                "backend_runtime": "Node.js 20 LTS",
                "backend_framework": "Express.js",
                "database": "PostgreSQL 16",
                "frontend_framework": "React 18",
                "styling": "Tailwind CSS",
                "hosting": "Cloud platform",
                "auth": "JWT"
            }
        }
        
        return stacks.get(project_type, stacks["other"])
    
    def review_architecture(
        self,
        architecture: str,
        qa_issues: List[str]
    ) -> str:
        """
        Review and update architecture based on QA feedback.
        
        Args:
            architecture: Current architecture document
            qa_issues: List of QA issues related to architecture
        
        Returns:
            Updated architecture document
        """
        if not qa_issues:
            return architecture
        
        self.log(f"Reviewing architecture with {len(qa_issues)} QA issues")
        
        base_system = """You are a Technical Architect reviewing architecture based on QA feedback.
        
Update the architecture document to address the QA issues while maintaining consistency.
Mark changes clearly with [UPDATED] tags."""

        system_prompt = self.build_system_prompt(base_system)
        
        user_prompt = f"""Review and update this architecture based on QA feedback:

## Current Architecture
{architecture}

## QA Issues to Address
{chr(10).join(f'- {issue}' for issue in qa_issues)}

Return the complete updated architecture document with issues addressed.
Add [UPDATED] markers to changed sections."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=4000)
            self.log("Architecture review complete")
            return response
        except AgentError as e:
            self.log(f"Architecture review failed: {e}", "ERROR")
            # Return original with issues noted
            return architecture + f"\n\n## Pending QA Issues\n" + "\n".join([f"- {i}" for i in qa_issues])
