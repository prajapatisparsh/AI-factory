// TypeScript types mirroring the Python Pydantic schemas

export type ProjectType = 'web_app' | 'mobile_app' | 'api' | 'desktop' | 'other';
export type Priority = 'Critical' | 'High' | 'Medium' | 'Low';
export type EvaluationStatus = 'APPROVED' | 'REJECTED';
export type PipelineMode = 'auto' | 'guided';

export interface DocumentAnalysis {
  project_type: ProjectType;
  features: string[];
  personas: string[];
  tech_hints: string[];
  ambiguities: string[];
  full_text: string;
}

export interface UserStory {
  id: string;
  title: string;
  user_role: string;
  action: string;
  benefit: string;
  acceptance_criteria: string[];
  priority: Priority;
}

export interface ScoreBreakdown {
  requirements: number;  // 0-30
  architecture: number;  // 0-25
  completeness: number;  // 0-20
  qa_compliance: number; // 0-15
  security: number;      // 0-10
}

export interface PMEvaluation {
  score: number;
  status: EvaluationStatus;
  breakdown: ScoreBreakdown;
  strengths: string[];
  issues: string[];
  scolding: string;
}

export interface QAIssue {
  id: string;
  desc: string;
  location: string;
}

export interface QAReport {
  critical: QAIssue[];
  high: QAIssue[];
  medium: QAIssue[];
  low: QAIssue[];
  security_flags: string[];
}

export interface ClarificationQA {
  id: string;
  question: string;
  context: string;
  source_agent: string;
  answer?: string;
}

export interface LearnedRule {
  date: string;
  rule: string;
  target_playbook: string;
}

export interface AgentMessage {
  agent: string;
  role: string;
  content: string;
  timestamp: number;
}

export interface DiscussionEvent {
  topic: string;
  agents: string[];
  messages: AgentMessage[];
  consensus?: string;
  disagreements?: string[];
}

export interface CoachEvent {
  trigger: 'rejection';
  rules_extracted: LearnedRule[];
  playbooks_updated: string[];
  message: string;
}

export interface RetryInfo {
  cycle: number;
  reason: string;
  feedback: string;
  score_previous: number;
}

export type PhaseStatus = 'pending' | 'running' | 'complete' | 'paused' | 'failed';

export interface PhaseResult {
  phase: number;
  name: string;
  status: PhaseStatus;
  started_at?: number;
  completed_at?: number;
  // Phase-specific outputs
  document_analysis?: DocumentAnalysis;
  user_stories?: UserStory[];
  architecture?: string;
  discussion?: DiscussionEvent;
  clarifications?: ClarificationQA[];
  backend_spec?: string;
  frontend_spec?: string;
  qa_report?: QAReport;
  qa_discussion?: DiscussionEvent;
  pm_evaluation?: PMEvaluation;
  coach_event?: CoachEvent;
  retry_info?: RetryInfo;
  output_files?: OutputFile[];
}

export interface OutputFile {
  name: string;
  filename: string;
  description: string;
  exists?: boolean;
}

export interface EvolutionStats {
  total_rules: number;
  by_agent: {
    pm: { learned: number; written: number };
    tech_lead: { learned: number; written: number };
    backend: { learned: number; written: number };
    frontend: { learned: number; written: number };
    qa: { learned: number; written: number };
  };
}

export interface ActivityLogEntry {
  timestamp: number;
  phase: number;
  type: 'info' | 'phase_start' | 'phase_complete' | 'agent_event' | 'discussion' | 'coach' | 'error' | 'retry';
  message: string;
  agent?: string;
}

export interface RunHistory {
  id: string;
  name: string;
  started_at: number;
  completed_at?: number;
  score?: number;
  retries: number;
  status: 'running' | 'complete' | 'failed';
}

export interface PipelineState {
  run_id: string;
  mode: PipelineMode;
  current_phase: number;
  overall_status: 'idle' | 'running' | 'paused' | 'complete' | 'failed';
  paused_at_phase?: number;
  phases: PhaseResult[];
  retry_count: number;
  current_cycle: number;
  activity_log: ActivityLogEntry[];
  evolution: EvolutionStats;
  run_history: RunHistory[];
}

export const PHASE_META: { name: string; description: string; agent: string }[] = [
  { name: 'Document Parsing',      description: 'VisionAgent reads and understands your requirements',        agent: 'VisionAgent' },
  { name: 'User Stories + Arch',   description: 'PM generates stories; TechLead designs the architecture',   agent: 'PM + TechLead' },
  { name: 'Clarifications',        description: 'DevTeam raises questions; PM resolves ambiguities',         agent: 'PM + DevTeam' },
  { name: 'Draft Specs',           description: 'DevTeam writes backend and frontend specifications',        agent: 'DevTeam' },
  { name: 'QA Analysis',           description: 'QA agent reviews specs for critical issues and gaps',       agent: 'QAAgent' },
  { name: 'Fixes Applied',         description: 'DevTeam corrects issues surfaced by QA',                   agent: 'DevTeam' },
  { name: 'PM Evaluation',         description: 'PM scores the output. Below 85 triggers retry + learning', agent: 'PM + Coach' },
  { name: 'Output Saved',          description: 'Final approved specs packaged into 8 Markdown files',      agent: 'System' },
];

export const OUTPUT_FILES: OutputFile[] = [
  { name: 'Executive Summary',  filename: '00_EXECUTIVE_SUMMARY.md',  description: 'One-page brief of the entire project' },
  { name: 'Master Prompt',      filename: '01_MASTER_PROMPT.md',      description: 'The distilled system prompt for future agents' },
  { name: 'User Stories',       filename: '02_User_Stories.md',       description: 'All user stories with acceptance criteria' },
  { name: 'Architecture',       filename: '03_Architecture.md',       description: 'System design, tech stack, data models' },
  { name: 'Backend Spec',       filename: '04_Backend_Final.md',      description: 'API endpoints, services, infrastructure' },
  { name: 'Frontend Spec',      filename: '05_Frontend_Final.md',     description: 'Components, routes, UX patterns' },
  { name: 'QA Report',          filename: '06_QA_Report.md',          description: 'Issues found, severity, and resolutions' },
  { name: 'Cost Estimation',    filename: '08_Cost_Estimation.md',    description: 'Monthly infra cost breakdown' },
];
