 import type { PipelineState, PhaseResult, ActivityLogEntry, EvolutionStats } from './types';

export const MOCK_EVOLUTION: EvolutionStats = {
  total_rules: 34,
  by_agent: {
    pm: { learned: 8, written: 3 },
    tech_lead: { learned: 6, written: 2 },
    backend: { learned: 7, written: 2 },
    frontend: { learned: 5, written: 1 },
    qa: { learned: 4, written: 1 },
  },
};

export const MOCK_DOCUMENT_ANALYSIS = {
  project_type: 'web_app' as const,
  features: [
    'User authentication with email and social OAuth',
    'Real-time collaboration on shared documents',
    'AI-assisted writing suggestions',
    'Version history and diff viewer',
    'Workspace and team management',
    'Export to PDF, Word, and Markdown',
    'Offline mode with conflict resolution',
    'Role-based access control',
  ],
  personas: ['Content Creator', 'Team Manager', 'Developer', 'Enterprise Admin'],
  tech_hints: ['React', 'Node.js', 'WebSockets', 'PostgreSQL', 'Redis'],
  ambiguities: [
    'Maximum file size for document uploads not specified',
    'Real-time collaboration limits (number of concurrent editors) unclear',
    'Pricing model not defined — affects feature gating design',
  ],
  full_text: 'Build a collaborative document editing platform…',
};

export const MOCK_USER_STORIES = [
  {
    id: 'US-001', title: 'User Login with Email', user_role: 'Content Creator',
    action: 'log in with my email and password', benefit: 'I can access my workspace securely',
    acceptance_criteria: ['Email/password validation', 'JWT token issued on success', 'Rate limiting on failed attempts', '2FA optional'],
    priority: 'Critical' as const,
  },
  {
    id: 'US-002', title: 'Real-time Document Collaboration', user_role: 'Team Member',
    action: 'edit a document simultaneously with my teammates', benefit: 'we can work without version conflicts',
    acceptance_criteria: ['Changes appear within 200ms', 'Cursor presence shown', 'Conflict-free merging via CRDT', 'Offline edits sync on reconnect'],
    priority: 'Critical' as const,
  },
  {
    id: 'US-003', title: 'AI Writing Suggestions', user_role: 'Content Creator',
    action: 'receive contextual writing suggestions as I type', benefit: 'I can produce higher-quality content faster',
    acceptance_criteria: ['Suggestions appear inline within 1s', 'User can accept, dismiss, or regenerate', 'Toggleable per document', 'Usage tracked for billing'],
    priority: 'High' as const,
  },
  {
    id: 'US-004', title: 'Version History', user_role: 'Team Manager',
    action: 'browse the version history of any document', benefit: 'I can restore to any previous state',
    acceptance_criteria: ['Versions listed with timestamp and author', 'Side-by-side diff view', 'One-click restore', 'Named checkpoints'],
    priority: 'High' as const,
  },
  {
    id: 'US-005', title: 'Workspace Invitations', user_role: 'Team Manager',
    action: 'invite team members to a workspace', benefit: 'we can collaborate on shared documents',
    acceptance_criteria: ['Email invite sent', 'Link-based invite option', 'Role selected at invite time', 'Invite expires after 7 days'],
    priority: 'High' as const,
  },
];

export const MOCK_ARCHITECTURE = `# System Architecture

## Overview
A real-time collaborative editing platform built on a microservices-adjacent monolith with selective service extraction.

## Technology Stack
| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React 18 + Vite | Fast HMR, RSC-ready |
| State | Zustand + CRDT (Yjs) | Offline-first collaboration |
| Backend | Node.js (Fastify) | Low latency WebSocket handling |
| Database | PostgreSQL 15 | JSONB for document metadata |
| Cache | Redis 7 | Session store + pub/sub |
| Realtime | Socket.io | Rooms, namespaces, reconnection |
| AI | OpenAI GPT-4o | Writing suggestions via streaming |
| Storage | S3-compatible (R2) | Document assets and exports |
| Auth | Supabase Auth | OAuth, JWT, RLS policies |

## Data Models

### Document
\`\`\`
document {
  id: uuid (PK)
  workspace_id: uuid (FK)
  title: text
  content_ydoc: bytea  // Yjs document state
  created_by: uuid
  created_at: timestamptz
  updated_at: timestamptz
  version: int
}
\`\`\`

### Workspace
\`\`\`
workspace {
  id: uuid (PK)
  name: text
  owner_id: uuid
  plan: enum(free, pro, enterprise)
  created_at: timestamptz
}
\`\`\`

## Infrastructure
- **Deployment**: Railway (monolith) + Vercel (frontend)
- **WebSocket**: Sticky sessions via Redis adapter
- **CDN**: Cloudflare for static assets
- **Monitoring**: Sentry + Datadog APM`;

export const MOCK_BACKEND_SPEC = `# Backend Specification

## Architecture Pattern
Fastify monolith with plugin isolation. Services communicate via dependency injection, not HTTP.

## API Endpoints

### Authentication
\`\`\`
POST /auth/email/signup    — Create account with email/password
POST /auth/email/signin    — Issue JWT access + refresh token
POST /auth/oauth/:provider — OAuth callback (Google, GitHub)
POST /auth/refresh         — Rotate access token
DELETE /auth/signout       — Invalidate refresh token
\`\`\`

### Documents
\`\`\`
GET    /workspaces/:wid/documents          — List documents
POST   /workspaces/:wid/documents          — Create document
GET    /documents/:id                      — Get document metadata
PUT    /documents/:id                      — Update title/settings
DELETE /documents/:id                      — Soft delete (30-day grace)
GET    /documents/:id/versions             — List version history
POST   /documents/:id/versions/restore/:v  — Restore version
\`\`\`

### Collaboration
\`\`\`
WS /collab/:docId  — Yjs awareness + update channel
\`\`\`

## Services

### CollaborationService
- Manages Yjs document state in Redis (active) / PostgreSQL (persisted)
- Broadcasts updates to room participants via Socket.io
- Persists full ydoc snapshot every 30s or on last-user-leave

### AIService  
- Streams GPT-4o completions for writing suggestions
- Rate limits: 10 requests/min free, 60/min pro
- Caches frequent completions for 5 min

## Error Handling
All errors return: \`{ code: string, message: string, requestId: string }\`
HTTP status codes follow RFC 9110.`;

export const MOCK_FRONTEND_SPEC = `# Frontend Specification

## Framework & Tooling
- React 18 with Vite 5
- TypeScript strict mode
- Zustand for client state
- TanStack Query for server state
- Tailwind CSS + shadcn/ui
- Yjs + y-websocket for collaboration

## Route Structure
\`\`\`
/                       — Marketing landing
/auth/signin            — Sign in
/auth/signup            — Sign up  
/app                    — Workspace list (authenticated)
/app/:workspaceId       — Workspace documents
/app/:workspaceId/:docId — Document editor
/app/settings           — User & workspace settings
\`\`\`

## Core Components

### Editor (DocumentEditor)
- Wraps Tiptap with Yjs extension
- Renders AI suggestion tooltips
- Version history sidebar panel
- Presence avatars + cursor colors
- Toolbar: bold, italic, headings, lists, code, link, image, AI

### RealtimeProvider
- Connects y-websocket to \`/collab/:docId\`
- Exposes shared Yjs types to child components
- Handles reconnection with exponential backoff
- Shows "reconnecting" banner when connection drops

## State Management
\`\`\`
useAuthStore    — user, session, signIn, signOut
useDocStore     — currentDoc, saveStatus, versionHistory
useCollabStore  — peers, awareness, connectionState
useUIStore      — sidebarOpen, activePanel, theme
\`\`\`

## Performance Targets
- LCP < 2.5s on cold load
- Editor keystroke latency < 50ms
- Collaboration sync < 200ms`;

export const MOCK_QA_REPORT = {
  critical: [
    { id: 'C-001', desc: 'No CSRF protection on mutation endpoints', location: 'Backend API layer' },
    { id: 'C-002', desc: 'Yjs ydoc not validated before persistence — malformed state could corrupt document', location: 'CollaborationService' },
  ],
  high: [
    { id: 'H-001', desc: 'No rate limiting on document creation — denial of service risk', location: 'POST /workspaces/:wid/documents' },
    { id: 'H-002', desc: 'Version restore endpoint lacks authorization check (any authenticated user can restore any version)', location: 'POST /documents/:id/versions/restore/:v' },
    { id: 'H-003', desc: 'AI streaming response not bounded — single request can exhaust token budget', location: 'AIService' },
  ],
  medium: [
    { id: 'M-001', desc: 'Editor toolbar missing undo/redo for collaborative operations', location: 'DocumentEditor component' },
    { id: 'M-002', desc: 'Offline sync conflict UI not specified — user needs feedback when merge fails', location: 'RealtimeProvider' },
  ],
  low: [
    { id: 'L-001', desc: 'Version history list missing pagination — will degrade for documents with 100+ versions', location: 'GET /documents/:id/versions' },
  ],
  security_flags: [
    'JWT refresh tokens stored in localStorage — migrate to httpOnly cookies',
    'OAuth state parameter not validated — CSRF on OAuth callback',
  ],
};

export const MOCK_PM_EVALUATION = {
  score: 88,
  status: 'APPROVED' as const,
  breakdown: { requirements: 26, architecture: 22, completeness: 18, qa_compliance: 13, security: 9 },
  strengths: [
    'Architecture selection is well-justified with clear tradeoffs documented',
    'API endpoints cover all user stories with appropriate HTTP methods',
    'State management strategy is cohesive and covers all identified use cases',
    'QA issues addressed with clear resolutions in the final spec',
  ],
  issues: [],
  scolding: '',
};

export const MOCK_CLARIFICATIONS = [
  { id: 'Q-001', question: 'What is the maximum document size we should support?', context: 'Affects storage tier selection and collaboration performance', source_agent: 'dev_team', answer: 'PM Response: 50MB per document. Larger files (.pdf exports) stored separately in R2.' },
  { id: 'Q-002', question: 'Should we support guest editor access (non-authenticated collaboration)?', context: 'Affects auth middleware and Yjs room isolation design', source_agent: 'dev_team', answer: 'PM Response: Not for MVP. All collaborators must be authenticated workspace members.' },
  { id: 'Q-003', question: 'How many concurrent editors should a single document support?', context: 'Critical for Redis pub/sub and Socket.io room sizing', source_agent: 'dev_team', answer: 'PM Response: 25 concurrent editors per document for pro plan, 5 for free.' },
];

export const MOCK_DISCUSSION_1 = {
  topic: 'Architecture validation: Is the chosen stack appropriate for the real-time requirements?',
  agents: ['PMAgent', 'TechLeadAgent', 'DevTeamAgent'],
  messages: [
    { agent: 'TechLeadAgent', role: 'Architect', content: 'I selected Yjs with Socket.io for the collaboration layer. This is the industry-standard approach — Notion, Linear, and Figma all use CRDTs for conflict-free merging. The Redis adapter for Socket.io handles horizontal scaling.', timestamp: 1 },
    { agent: 'DevTeamAgent', role: 'Developer', content: 'One concern: Socket.io adds connection overhead vs raw WebSockets. For the AI streaming suggestion feature, we\'ll be running two simultaneous WebSocket connections. Worth splitting into separate endpoints from the start.', timestamp: 2 },
    { agent: 'TechLeadAgent', role: 'Architect', content: 'Valid point. I\'ll update the architecture to route AI streaming through a dedicated \`/ai/stream\` WebSocket endpoint, separate from \`/collab/:docId\`. This also lets us apply different rate limits independently.', timestamp: 3 },
    { agent: 'PMAgent', role: 'Product Manager', content: 'Agreed on the separation. Also confirming: we need to document the conflict resolution UX for offline edits before the QA phase. If a user edits offline and another user deletes the document, Yjs merge will succeed but the UX needs to surface this state.', timestamp: 4 },
  ],
  consensus: 'Stack approved. AI streaming will use a dedicated WebSocket endpoint. Offline conflict UX documentation added to Phase 3 clarifications.',
};

export const MOCK_DISCUSSION_2 = {
  topic: 'QA findings severity assessment: Are the 2 Critical issues blockers for approval?',
  agents: ['PMAgent', 'QAAgent', 'DevTeamAgent'],
  messages: [
    { agent: 'QAAgent', role: 'QA Engineer', content: 'C-001 (no CSRF protection) and C-002 (ydoc not validated before persistence) are both Critical. C-001 is straightforward — add \`fastify-csrf-protection\` and double-submit cookie pattern. C-002 requires a Yjs document schema validator before any persist call.', timestamp: 1 },
    { agent: 'DevTeamAgent', role: 'Developer', content: 'C-001 fix is one plugin and two lines of config. I can address it inline. C-002 is more involved — Yjs documents are binary encoded, we need to decode and validate structure before writing to PostgreSQL. I\'ll add a validation wrapper in CollaborationService.', timestamp: 2 },
    { agent: 'PMAgent', role: 'Product Manager', content: 'Both must be fixed before we proceed. H-002 (authorization on version restore) is also effectively Critical given it allows privilege escalation. I\'m upgrading it. Do not pass QA until all three are resolved in the spec.', timestamp: 3 },
    { agent: 'QAAgent', role: 'QA Engineer', content: 'Agreed on H-002 re-classification. JWT in localStorage is a deferred concern for MVP but must be a P0 post-launch item. I\'ll flag it as tech debt in the QA report rather than a spec blocker.', timestamp: 4 },
  ],
  consensus: 'C-001, C-002, and (upgraded) H-002 must all be explicitly addressed in Phase 6 fixes. JWT storage deferred to post-launch tech debt.',
};

export const MOCK_COACH_EVENT = {
  trigger: 'rejection' as const,
  rules_extracted: [
    { date: '2026-02-23', rule: 'Always include CSRF protection explicitly in the backend security section', target_playbook: 'backend_playbook.md' },
    { date: '2026-02-23', rule: 'Never persist binary collaborative document state without input validation step', target_playbook: 'backend_playbook.md' },
    { date: '2026-02-23', rule: 'Always specify authorization checks on every admin/destructive endpoint', target_playbook: 'qa_playbook.md' },
  ],
  playbooks_updated: ['backend_playbook.md', 'qa_playbook.md'],
  message: 'Three rules extracted from rejection cycle. Backend and QA playbooks updated. Next retry will include these constraints in agent prompts.',
};

export const MOCK_OUTPUT_FILES = [
  { name: 'Executive Summary', filename: '00_EXECUTIVE_SUMMARY.md', description: 'One-page project brief', path: '/projects/MVP_20260223/' },
  { name: 'Master Prompt', filename: '01_MASTER_PROMPT.md', description: 'Distilled system prompt for future agents', path: '/projects/MVP_20260223/' },
  { name: 'User Stories', filename: '02_User_Stories.md', description: '5 user stories with acceptance criteria', path: '/projects/MVP_20260223/' },
  { name: 'Architecture', filename: '03_Architecture.md', description: 'System design, tech stack, data models', path: '/projects/MVP_20260223/' },
  { name: 'Backend Spec', filename: '04_Backend_Final.md', description: 'API endpoints, services, infrastructure', path: '/projects/MVP_20260223/' },
  { name: 'Frontend Spec', filename: '05_Frontend_Final.md', description: 'Components, routes, UX patterns', path: '/projects/MVP_20260223/' },
  { name: 'QA Report', filename: '06_QA_Report.md', description: 'Issues found, severity, resolutions', path: '/projects/MVP_20260223/' },
  { name: 'Cost Estimation', filename: '08_Cost_Estimation.md', description: 'Monthly infrastructure cost breakdown', path: '/projects/MVP_20260223/' },
];

export const MOCK_RUN_HISTORY = [
  { id: 'run_001', name: 'E-commerce Platform', started_at: Date.now() - 86400000 * 3, completed_at: Date.now() - 86400000 * 3 + 180000, score: 91, retries: 0, status: 'complete' as const },
  { id: 'run_002', name: 'SaaS Analytics Dashboard', started_at: Date.now() - 86400000 * 2, completed_at: Date.now() - 86400000 * 2 + 240000, score: 87, retries: 1, status: 'complete' as const },
  { id: 'run_003', name: 'Mobile Fitness Tracker API', started_at: Date.now() - 86400000, completed_at: Date.now() - 86400000 + 210000, score: 93, retries: 0, status: 'complete' as const },
];
