"""
Tech Lead Agent - Architecture and system design.
Generates comprehensive technical architecture specifications.
"""

from typing import List, Optional

from src.agents.base import BaseAgent
from src.schemas import DocumentAnalysis, UserStory, ArchitectureSpec


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
        
        # Detect domain and get domain-specific guidance
        domain = self._detect_domain(context)
        domain_guidance = self._get_domain_template(domain)
        
        base_system = f"""You are a senior Technical Architect designing MVP architecture.

Create a comprehensive architecture document that includes:
1. **Technology Stack** - Justified choices for each layer
2. **System Architecture** - High-level component diagram description
3. **Database Design** - Schema with tables, relationships, indexes
4. **API Design** - RESTful endpoints with methods and payloads
5. **Security Strategy** - Authentication, authorization, data protection
6. **Scalability Plan** - How the system handles growth
7. **Observability** - Logging, monitoring, alerting approach

Design for:
- Clean separation of concerns
- Horizontal scalability
- Security by default
- Developer experience
- Production readiness

{domain_guidance}"""

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
- Domain: {domain.upper()}
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
Justify each technology choice based on the requirements and DOMAIN-SPECIFIC needs."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.4, max_tokens=4000)
            
            # Ensure proper markdown formatting
            architecture = self._format_architecture(response)
            self.log("Architecture specification generated")
            return architecture
            
        except Exception as e:
            self.log(f"Architecture generation failed: {e}", "ERROR")
            return self._fallback_architecture(context, user_stories)
    
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
    
    def _detect_domain(self, context: DocumentAnalysis) -> str:
        """Detect the project domain from features and requirements."""
        features_text = ' '.join(context.features).lower()
        full_text = context.full_text.lower() if context.full_text else ''
        combined = features_text + ' ' + full_text
        
        # E-commerce indicators
        if any(kw in combined for kw in ['cart', 'checkout', 'product catalog', 'inventory', 'shop', 'store', 'e-commerce', 'ecommerce', 'order management', 'sku']):
            return 'ecommerce'
        
        # SaaS indicators
        if any(kw in combined for kw in ['subscription', 'tenant', 'multi-tenant', 'saas', 'billing plan', 'tier', 'usage meter', 'seat license']):
            return 'saas'
        
        # Healthcare indicators
        if any(kw in combined for kw in ['patient', 'medical', 'healthcare', 'health', 'hipaa', 'appointment', 'doctor', 'clinic', 'diagnosis', 'prescription']):
            return 'healthcare'
        
        # Fintech indicators
        if any(kw in combined for kw in ['payment', 'transaction', 'wallet', 'banking', 'fintech', 'money transfer', 'ledger', 'kyc', 'compliance', 'financial']):
            return 'fintech'
        
        # Social media indicators
        if any(kw in combined for kw in ['social', 'feed', 'post', 'follow', 'like', 'share', 'comment', 'friend', 'profile', 'timeline', 'community']):
            return 'social'
        
        # Marketplace indicators
        if any(kw in combined for kw in ['marketplace', 'seller', 'buyer', 'listing', 'bid', 'auction', 'vendor', 'commission', 'escrow']):
            return 'marketplace'
        
        # Content/CMS indicators
        if any(kw in combined for kw in ['content', 'cms', 'article', 'blog', 'publish', 'editor', 'media library']):
            return 'content'
        
        # Education/LMS indicators
        if any(kw in combined for kw in ['course', 'student', 'learning', 'lesson', 'quiz', 'enrollment', 'instructor', 'lms', 'education']):
            return 'education'
        
        return 'general'
    
    def _get_domain_template(self, domain: str) -> str:
        """Get domain-specific architecture guidance."""
        templates = {
            'ecommerce': """
## E-COMMERCE DOMAIN REQUIREMENTS
Apply these e-commerce specific patterns:
- **Product Catalog**: Implement product variants (size, color), SKU management, inventory tracking
- **Shopping Cart**: Session-based cart with persistence, abandoned cart recovery
- **Checkout Flow**: Multi-step checkout with address validation, shipping calculation
- **Payment Integration**: Stripe/PayPal integration with webhook handling for payment confirmation
- **Order Management**: Order states (pending, paid, shipped, delivered, refunded), email notifications
- **Inventory**: Real-time stock tracking, low-stock alerts, backorder handling
- **Search**: Elasticsearch or Algolia for product search with faceted filtering
- **Security**: PCI-DSS compliance considerations for payment data
""",
            'saas': """
## SAAS DOMAIN REQUIREMENTS
Apply these SaaS-specific patterns:
- **Multi-tenancy**: Data isolation strategy (schema-per-tenant vs row-level security)
- **Subscription Management**: Plan tiers, billing cycles, usage metering, Stripe/Chargebee integration
- **User Management**: Roles within organization (Admin, Member, Viewer), invite system
- **Feature Flags**: LaunchDarkly or custom solution for feature gating by plan
- **Onboarding**: Setup wizard, data import tools, sample data generation
- **Usage Analytics**: Track feature usage for billing and product insights
- **API Access**: Rate limiting by plan, API key management, webhook system
- **Audit Logs**: Track all configuration changes for compliance
""",
            'healthcare': """
## HEALTHCARE DOMAIN REQUIREMENTS
Apply these healthcare-specific patterns:
- **HIPAA Compliance**: Encryption at rest (AES-256), encryption in transit (TLS 1.3), audit logging
- **Patient Data**: PHI protection, consent management, data retention policies
- **Authentication**: MFA required, session timeout after 15 minutes of inactivity
- **Audit Trail**: Immutable logs of all data access with user, timestamp, action
- **Appointment System**: Calendar integration, reminder notifications, booking rules
- **Interoperability**: HL7 FHIR standards for health data exchange
- **Access Control**: Role-based (Doctor, Nurse, Admin, Patient) with fine-grained permissions
- **Data Backup**: Daily encrypted backups with 90-day retention, disaster recovery plan
""",
            'fintech': """
## FINTECH DOMAIN REQUIREMENTS
Apply these financial-specific patterns:
- **Transaction Integrity**: ACID compliance, double-entry accounting, idempotency keys
- **KYC/AML**: Identity verification integration (Jumio, Onfido), watchlist screening
- **Security**: PCI-DSS compliance, HSM for key management, fraud detection
- **Audit Trail**: Immutable transaction logs, regulatory reporting exports
- **Money Movement**: Ledger architecture, settlement processing, reconciliation
- **Notification**: Real-time transaction alerts, two-factor for high-value operations
- **Rate Limiting**: Strict limits on financial operations, velocity checks
- **Compliance**: Regulatory holds, suspicious activity reporting, data retention requirements
""",
            'social': """
## SOCIAL PLATFORM DOMAIN REQUIREMENTS
Apply these social-specific patterns:
- **Content Feed**: Personalized feed algorithm, pagination with cursor-based approach
- **Real-time Features**: WebSocket connections for notifications, live updates
- **Media Handling**: Image/video upload, CDN delivery, thumbnail generation
- **Engagement**: Like/reaction system, comment threading, share tracking
- **Notifications**: Push notifications (FCM/APNs), email digests, in-app alerts
- **Content Moderation**: Flagging system, automated content scanning, admin tools
- **Privacy Controls**: Block/mute, visibility settings, data export (GDPR)
- **Scalability**: Read-heavy architecture, caching layer, eventual consistency acceptable
""",
            'marketplace': """
## MARKETPLACE DOMAIN REQUIREMENTS
Apply these marketplace-specific patterns:
- **Dual-sided**: Separate flows for buyers and sellers, verification for sellers
- **Listing Management**: Approval workflow, listing lifecycle, featured placement
- **Search & Discovery**: Full-text search, category hierarchy, location-based filtering
- **Transaction Flow**: Escrow for payments, dispute resolution, refund handling
- **Commission System**: Fee calculation, payout scheduling, seller statements
- **Messaging**: Buyer-seller communication, inquiry system, notifications
- **Reviews & Ratings**: Verified purchase reviews, rating aggregation, moderation
- **Trust & Safety**: Fraud detection, identity verification, content moderation
""",
            'education': """
## EDUCATION/LMS DOMAIN REQUIREMENTS
Apply these education-specific patterns:
- **Course Structure**: Modules, lessons, content types (video, text, quiz)
- **Progress Tracking**: Completion status, resume position, learning paths
- **Assessment**: Quiz engine, grading system, certificates generation
- **Enrollment**: Cohort management, prerequisites, access expiration
- **Video Delivery**: Adaptive streaming, progress tracking, DRM for paid content
- **Discussion**: Course forums, Q&A, instructor responses
- **Reporting**: Student progress reports, course analytics, completion rates
- **Accessibility**: WCAG compliance, closed captions, screen reader support
""",
            'content': """
## CONTENT/CMS DOMAIN REQUIREMENTS
Apply these content-specific patterns:
- **Content Types**: Flexible schema for articles, pages, media
- **Editorial Workflow**: Draft, review, publish, schedule states
- **Media Management**: Asset library, image optimization, CDN delivery
- **SEO**: Meta tags, sitemap generation, structured data
- **Versioning**: Content history, rollback capability, diff view
- **Personalization**: User segments, A/B testing, recommendations
- **Performance**: Static generation where possible, cache invalidation
- **Multi-language**: i18n support, translation workflow, locale routing
"""
        }
        
        return templates.get(domain, """
## GENERAL APPLICATION PATTERNS
Apply standard best practices:
- RESTful API design with consistent error handling
- JWT authentication with refresh token rotation
- PostgreSQL with proper indexing strategy
- Redis for caching and session management
- Queue-based background job processing
- Structured logging with correlation IDs
- Health check endpoints for monitoring
""")
    
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
        except Exception as e:
            self.log(f"Architecture review failed: {e}", "ERROR")
            # Return original with issues noted
            return architecture + f"\n\n## Pending QA Issues\n" + "\n".join([f"- {i}" for i in qa_issues])
    
    def generate_architecture_diagram(
        self,
        context: DocumentAnalysis,
        architecture: str
    ) -> str:
        """
        Generate Mermaid diagram for the architecture.
        
        Args:
            context: Document analysis
            architecture: Generated architecture spec
        
        Returns:
            Mermaid diagram code
        """
        self.log("Generating architecture diagram")
        
        system_prompt = """You are a technical diagramming expert.

Create a Mermaid.js diagram that visualizes the system architecture.

DIAGRAM TYPES TO USE:
1. Use 'graph TD' for system overview (top-down flow)
2. Use 'sequenceDiagram' for API flows
3. Use 'erDiagram' for database relationships

RULES:
- Keep diagrams clean and readable
- Use clear node names (no special characters)
- Include all major components
- Show data flow direction
- Group related components

OUTPUT FORMAT:
Provide the Mermaid code wrapped in ```mermaid blocks.
"""

        user_prompt = f"""Create architecture diagrams for this system:

PROJECT TYPE: {context.project_type.value}

FEATURES:
{chr(10).join(f'- {f}' for f in context.features)}

ARCHITECTURE SUMMARY:
{architecture[:2500]}

Generate THREE diagrams:
1. System Overview (graph TD) - Show all components and their connections
2. API Flow (sequenceDiagram) - Show a typical user request flow
3. Database Schema (erDiagram) - Show main entities and relationships

Format each in separate ```mermaid code blocks with labels."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=2000)
            self.log("Architecture diagrams generated")
            return response
        except Exception as e:
            self.log(f"Diagram generation failed: {e}", "ERROR")
            return self._fallback_diagram(context)
    
    def _fallback_diagram(self, context: DocumentAnalysis) -> str:
        """Generate a simple fallback diagram."""
        return f"""## Architecture Diagrams

### System Overview

```mermaid
graph TD
    Client[Client Browser/App]
    API[API Server]
    DB[(Database)]
    Cache[Cache Layer]
    
    Client -->|HTTP/HTTPS| API
    API -->|Query| DB
    API -->|Read/Write| Cache
    Cache -->|Fallback| DB
```

### Typical Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API Server
    participant D as Database
    
    C->>A: Request
    A->>D: Query Data
    D-->>A: Return Data
    A-->>C: JSON Response
```

### Database Schema (Simplified)

```mermaid
erDiagram
    USER ||--o{{ ORDER : places
    USER {{
        string id PK
        string email
        string name
    }}
    ORDER {{
        string id PK
        string user_id FK
        datetime created_at
    }}
```

*Note: These are simplified placeholder diagrams. Actual architecture may differ.*
"""

