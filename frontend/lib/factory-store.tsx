'use client';

/**
 * factory-store.tsx — React Context that drives the factory pipeline page.
 *
 * All pipeline data now comes from the real Python FastAPI backend via
 * Server-Sent Events (SSE).  Mock data is NOT used for pipeline runs.
 */

import React, { createContext, useContext, useReducer, useCallback, useRef, useEffect } from 'react';
import type { PipelineState, PipelineMode, PhaseResult, ActivityLogEntry, EvolutionStats } from './types';
import { PHASE_META } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// ── Empty / default values ───────────────────────────────────────────────────

const EMPTY_EVOLUTION: EvolutionStats = {
  total_rules: 0,
  by_agent: {
    pm:        { learned: 0, written: 0 },
    tech_lead: { learned: 0, written: 0 },
    backend:   { learned: 0, written: 0 },
    frontend:  { learned: 0, written: 0 },
    qa:        { learned: 0, written: 0 },
  },
};

// ── State & Actions ──────────────────────────────────────────────────────────

type Stage = 'idle' | 'running' | 'paused' | 'complete';

interface FactoryState {
  stage: Stage;
  pipeline: PipelineState | null;
  input_text: string;
  input_file: File | null;
  mode: PipelineMode;
  error: string | null;
}

type Action =
  | { type: 'SET_MODE'; mode: PipelineMode }
  | { type: 'SET_INPUT_TEXT'; text: string }
  | { type: 'SET_INPUT_FILE'; file: File | null }
  | { type: 'START_PIPELINE'; run_id: string }
  | { type: 'PHASE_START'; phase: number }
  | { type: 'PHASE_COMPLETE'; phase: number; result: Partial<PhaseResult> }
  | { type: 'PAUSE_PIPELINE'; phase: number }
  | { type: 'RESUME_PIPELINE' }
  | { type: 'COMPLETE_PIPELINE' }
  | { type: 'LOG'; entry: ActivityLogEntry }
  | { type: 'UPDATE_EVOLUTION'; delta: number }
  | { type: 'INCREMENT_RETRY' }
  | { type: 'SET_ERROR'; message: string }
  | { type: 'PHASE_UPDATE'; phase: number; result: Partial<PhaseResult> }
  | { type: 'RESET' };

function buildInitialPhases(): PhaseResult[] {
  return PHASE_META.map((meta, i) => ({
    phase: i + 1,
    name: meta.name,
    status: 'pending',
  }));
}

function reducer(state: FactoryState, action: Action): FactoryState {
  switch (action.type) {
    case 'SET_MODE':       return { ...state, mode: action.mode };
    case 'SET_INPUT_TEXT': return { ...state, input_text: action.text };
    case 'SET_INPUT_FILE': return { ...state, input_file: action.file };
    case 'SET_ERROR':      return { ...state, error: action.message };

    case 'START_PIPELINE': {
      return {
        ...state,
        stage: 'running',
        error: null,
        pipeline: {
          run_id: action.run_id,
          mode: state.mode,
          current_phase: 1,
          overall_status: 'running',
          phases: buildInitialPhases(),
          retry_count: 0,
          current_cycle: 1,
          activity_log: [],
          evolution: EMPTY_EVOLUTION,
          run_history: [],
        },
      };
    }

    case 'PHASE_START': {
      if (!state.pipeline) return state;
      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          current_phase: action.phase,
          phases: state.pipeline.phases.map(p =>
            p.phase === action.phase ? { ...p, status: 'running', started_at: Date.now() } : p
          ),
        },
      };
    }

    case 'PHASE_COMPLETE': {
      if (!state.pipeline) return state;
      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          phases: state.pipeline.phases.map(p =>
            p.phase === action.phase
              ? { ...p, status: 'complete', completed_at: Date.now(), ...action.result }
              : p
          ),
        },
      };
    }

    case 'PAUSE_PIPELINE': {
      if (!state.pipeline) return state;
      return {
        ...state,
        stage: 'paused',
        pipeline: {
          ...state.pipeline,
          overall_status: 'paused',
          paused_at_phase: action.phase,
          phases: state.pipeline.phases.map(p =>
            p.phase === action.phase ? { ...p, status: 'paused' } : p
          ),
        },
      };
    }

    case 'RESUME_PIPELINE': {
      if (!state.pipeline) return state;
      return {
        ...state,
        stage: 'running',
        pipeline: {
          ...state.pipeline,
          overall_status: 'running',
          paused_at_phase: undefined,
          phases: state.pipeline.phases.map(p =>
            p.status === 'paused' ? { ...p, status: 'running' } : p
          ),
        },
      };
    }

    case 'COMPLETE_PIPELINE': {
      if (!state.pipeline) return state;
      return {
        ...state,
        stage: 'complete',
        pipeline: { ...state.pipeline, overall_status: 'complete' },
      };
    }

    case 'LOG': {
      if (!state.pipeline) return state;
      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          activity_log: [...state.pipeline.activity_log, action.entry],
        },
      };
    }

    case 'UPDATE_EVOLUTION': {
      if (!state.pipeline) return state;
      const ev = state.pipeline.evolution;
      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          evolution: { ...ev, total_rules: ev.total_rules + action.delta },
        },
      };
    }

    case 'INCREMENT_RETRY': {
      if (!state.pipeline) return state;
      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          retry_count: state.pipeline.retry_count + 1,
          current_cycle: state.pipeline.current_cycle + 1,
        },
      };
    }

    case 'PHASE_UPDATE': {
      if (!state.pipeline) return state;
      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          phases: state.pipeline.phases.map(p =>
            p.phase === action.phase ? { ...p, ...action.result } : p
          ),
        },
      };
    }

    case 'RESET':
      return { stage: 'idle', pipeline: null, input_text: '', input_file: null, mode: 'auto', error: null };

    default: return state;
  }
}

// ── Context ──────────────────────────────────────────────────────────────────

interface FactoryContextValue {
  state: FactoryState;
  dispatch: React.Dispatch<Action>;
  startPipeline: () => void;
  resumePipeline: () => void;
  resetFactory: () => void;
}

const FactoryContext = createContext<FactoryContextValue | null>(null);

// ── SSE event → PhaseResult mapping ─────────────────────────────────────────

function parsePhaseResult(data: Record<string, unknown>): Partial<PhaseResult> {
  const result: Partial<PhaseResult> = {};
  if (data.document_analysis) result.document_analysis = data.document_analysis as PhaseResult['document_analysis'];
  if (data.user_stories)      result.user_stories      = data.user_stories as PhaseResult['user_stories'];
  if (data.architecture)      result.architecture      = data.architecture as string;
  if (data.clarifications)    result.clarifications    = data.clarifications as PhaseResult['clarifications'];
  if (data.backend_spec)      result.backend_spec      = data.backend_spec as string;
  if (data.frontend_spec)     result.frontend_spec     = data.frontend_spec as string;
  if (data.qa_report)         result.qa_report         = data.qa_report as PhaseResult['qa_report'];
  if (data.pm_evaluation)     result.pm_evaluation     = data.pm_evaluation as PhaseResult['pm_evaluation'];
  if (data.output_files)      result.output_files      = data.output_files as PhaseResult['output_files'];
  return result;
}

// ── Provider ─────────────────────────────────────────────────────────────────

export function FactoryProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, {
    stage: 'idle', pipeline: null, input_text: '', input_file: null, mode: 'auto', error: null,
  });

  /** Active EventSource — one at a time */
  const esRef    = useRef<EventSource | null>(null);
  /** Current run_id — needed for resume / cancel calls */
  const runIdRef = useRef<string | null>(null);
  /** Always-current state snapshot — safe to read inside async callbacks without stale closure */
  const stateRef = useRef(state);
  useEffect(() => { stateRef.current = state; }, [state]);

  const log = useCallback((phase: number, type: ActivityLogEntry['type'], message: string, agent?: string) => {
    dispatch({ type: 'LOG', entry: { timestamp: Date.now(), phase, type, message, agent } });
  }, []);

  // ── Connect to SSE stream ─────────────────────────────────────────────────

  const connectToStream = useCallback((run_id: string) => {
    runIdRef.current = run_id;
    if (esRef.current) { esRef.current.close(); }

    const es = new EventSource(`${API_BASE}/api/pipeline/stream/${run_id}`);
    esRef.current = es;

    es.onmessage = (event: MessageEvent) => {
      let data: Record<string, unknown>;
      try { data = JSON.parse(event.data as string); } catch { return; }

      const phase   = (data.phase   as number) ?? 0;
      const message = (data.message as string) ?? '';
      const agent   = (data.agent   as string) ?? undefined;

      switch (data.type) {

        case 'phase_start':
          dispatch({ type: 'PHASE_START', phase });
          log(phase, 'phase_start', message, agent);
          break;

        case 'phase_complete': {
          const innerData = (data.data ?? {}) as Record<string, unknown>;
          dispatch({ type: 'PHASE_COMPLETE', phase, result: parsePhaseResult(innerData) });
          log(phase, 'phase_complete', `Phase ${phase} complete`, agent);
          break;
        }

        case 'log':
          log(phase, 'agent_event', message, agent);
          break;

        case 'discussion': {
          const topic     = (data.topic     as string) ?? '';
          const consensus = (data.consensus as string) ?? '';
          // Wire into phase state so DiscussionBlock renders
          dispatch({ type: 'PHASE_UPDATE', phase, result: {
            discussion: { topic, agents: [], messages: [], consensus },
          }});
          log(phase, 'discussion', `${topic}: ${consensus.slice(0, 120)}`, 'Team');
          break;
        }

        case 'retry': {
          dispatch({ type: 'INCREMENT_RETRY' });
          const cycle    = (data.cycle    as number) ?? 0;
          const feedback = (data.feedback as string) ?? '';
          log(phase, 'retry', `Retry ${cycle}: ${feedback.slice(0, 200)}`, 'PMAgent');
          break;
        }

        case 'coach': {
          const n = (data.rules_count as number) ?? 0;
          if (n > 0) dispatch({ type: 'UPDATE_EVOLUTION', delta: n });
          log(phase, 'coach', message || `Coach extracted ${n} new rule(s)`, 'CoachAgent');
          break;
        }

        case 'pause':
          dispatch({ type: 'PAUSE_PIPELINE', phase });
          log(phase, 'info', `PAUSED at Phase ${phase} — review before continuing`, 'System');
          break;

        case 'complete':
          dispatch({ type: 'COMPLETE_PIPELINE' });
          log(8, 'info', 'Pipeline complete. Your MVP spec is ready.', 'System');
          es.close(); esRef.current = null;
          break;

        case 'error': {
          const msg = (data.message as string) ?? 'Unknown error';
          dispatch({ type: 'SET_ERROR', message: msg });
          log(phase, 'error', `Error: ${msg}`, agent);
          es.close(); esRef.current = null;
          break;
        }

        case 'stream_end':
          es.close(); esRef.current = null;
          break;

        default: break;
      }
    };

    es.onerror = () => {
      log(0, 'error', 'Connection to backend lost. Is the API server running on port 8000?', 'System');
      es.close(); esRef.current = null;
    };
  }, [log]);

  // ── startPipeline ─────────────────────────────────────────────────────────

  const startPipeline = useCallback(async () => {
    const text = state.input_text.trim();
    const file = state.input_file;
    if (!text && !file) {
      dispatch({ type: 'SET_ERROR', message: 'Please enter your project requirements or upload a file before running.' });
      return;
    }

    let run_id: string;
    try {
      let res: Response;
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('mode', state.mode);
        res = await fetch(`${API_BASE}/api/pipeline/start-file`, {
          method: 'POST',
          body: formData,
        });
      } else {
        res = await fetch(`${API_BASE}/api/pipeline/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, mode: state.mode }),
        });
      }
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error((body as { detail?: string }).detail ?? `HTTP ${res.status}`);
      }
      const json = (await res.json()) as { run_id: string };
      run_id = json.run_id;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      dispatch({ type: 'SET_ERROR', message: `Failed to start pipeline: ${msg}. Is the API server running?` });
      return;
    }

    dispatch({ type: 'START_PIPELINE', run_id });
    connectToStream(run_id);
  }, [state.input_text, state.mode, connectToStream]);

  // ── resumePipeline ────────────────────────────────────────────────────────

  const resumePipeline = useCallback(async () => {
    const run_id = runIdRef.current;
    if (!run_id) return;

    // Collect any edited specs from the currently paused phase so the
    // backend can use them instead of its LLM-generated versions.
    const currentPipeline = stateRef.current.pipeline;
    const pausedPhaseNum  = currentPipeline?.paused_at_phase;
    const specOverride: Record<string, string> = {};
    if (pausedPhaseNum) {
      const pausedPhase = currentPipeline?.phases.find(p => p.phase === pausedPhaseNum);
      if (pausedPhase?.backend_spec)  specOverride.backend_spec  = pausedPhase.backend_spec;
      if (pausedPhase?.frontend_spec) specOverride.frontend_spec = pausedPhase.frontend_spec;
    }

    try {
      await fetch(`${API_BASE}/api/pipeline/${run_id}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spec_override: specOverride }),
      });
    } catch {
      log(0, 'error', 'Failed to contact backend to resume.', 'System');
      return;
    }
    dispatch({ type: 'RESUME_PIPELINE' });
    connectToStream(run_id);
  }, [connectToStream, log]);

  // ── resetFactory ──────────────────────────────────────────────────────────

  const resetFactory = useCallback(() => {
    if (esRef.current) { esRef.current.close(); esRef.current = null; }
    const run_id = runIdRef.current;
    if (run_id) {
      fetch(`${API_BASE}/api/pipeline/${run_id}`, { method: 'DELETE' }).catch(() => {});
      runIdRef.current = null;
    }
    dispatch({ type: 'RESET' });
  }, []);

  return (
    <FactoryContext.Provider value={{ state, dispatch, startPipeline, resumePipeline, resetFactory }}>
      {children}
    </FactoryContext.Provider>
  );
}

export function useFactory() {
  const ctx = useContext(FactoryContext);
  if (!ctx) throw new Error('useFactory must be used inside FactoryProvider');
  return ctx;
}
