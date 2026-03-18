'use client';

import { useRef, useEffect, useState } from 'react';
import gsap from 'gsap';
import {
  Brain, Activity, History, CheckCircle2, XCircle,
  Clock, TrendingUp, Cpu, Zap, BarChart3,
} from 'lucide-react';
import { useFactory } from '@/lib/factory-store';
import { PHASE_META } from '@/lib/types';

// Ã¢â€â‚¬Ã¢â€â‚¬ Agent color map Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
const AGENT_COLORS: Record<string, string> = {
  pm:         '#6366f1',
  tech_lead:  '#8b5cf6',
  backend:    '#10b981',
  frontend:   '#22d3ee',
  qa:         '#f87171',
  vision:     '#fbbf24',
  coach:      '#fb923c',
};

const TYPE_COLOR: Record<string, string> = {
  phase_start:  '#818cf8',
  agent_output: '#10b981',
  discussion:   '#8b5cf6',
  evaluation:   '#fbbf24',
  coach:        '#f87171',
  system:       '#353560',
};

// Ã¢â€â‚¬Ã¢â€â‚¬ Section wrapper Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function PanelCard({
  children,
  accent = '#6366f1',
  className = '',
}: {
  children: React.ReactNode;
  accent?: string;
  className?: string;
}) {
  return (
    <div
      className={`relative rounded-2xl overflow-hidden transition-all duration-300 ${className}`}
      style={{ background: 'rgba(7,7,16,0.9)', border: `1px solid ${accent}18`, backdropFilter: 'blur(12px)' }}
      onMouseEnter={e => (e.currentTarget.style.borderColor = `${accent}30`)}
      onMouseLeave={e => (e.currentTarget.style.borderColor = `${accent}18`)}
    >
      {/* Top accent */}
      <div className="absolute top-0 left-0 right-0 h-px"
        style={{ background: `linear-gradient(90deg, transparent, ${accent}50, transparent)` }} />
      {children}
    </div>
  );
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Phase Progress Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function PhaseProgress({
  currentPhase,
  phases,
}: {
  currentPhase: number;
  phases: { phase: number; status: string }[];
}) {
  const barRef   = useRef<HTMLDivElement>(null);
  const meta     = PHASE_META[currentPhase - 1];
  const progress = Math.min((currentPhase / 8) * 100, 100);
  const runningPhase = phases.find(p => p.status === 'running');
  const completedCount = phases.filter(p => p.status === 'complete').length;

  useEffect(() => {
    if (barRef.current) {
      gsap.to(barRef.current, { width: `${Math.round((completedCount / 8) * 100)}%`, duration: 0.9, ease: 'power2.out' });
    }
  }, [completedCount]);

  return (
    <PanelCard accent="#6366f1">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-xl flex items-center justify-center relative"
              style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.22)' }}>
              <Cpu className={`w-3.5 h-3.5 text-[#818cf8]${runningPhase ? ' rotate-slow' : ''}`} />
              {runningPhase && (
                <div className="absolute inset-0 rounded-xl border border-[rgba(99,102,241,0.4)] ping-ring" />
              )}
            </div>
            <span className="text-xs font-bold text-[#c0c0e0]">Pipeline Progress</span>
          </div>
          <span className="text-sm font-black font-mono"
            style={{ color: '#818cf8' }}>
            {Math.round((completedCount / 8) * 100)}%
          </span>
        </div>

        {/* Segmented progress track */}
        <div className="flex gap-0.5 mb-3 h-1.5">
          {phases.map((p) => (
            <div key={p.phase} className="flex-1 rounded-full overflow-hidden relative transition-all duration-500"
              style={{ background: 'rgba(99,102,241,0.06)' }}>
              <div className="absolute inset-0 rounded-full transition-all duration-700"
                style={{
                  background:
                    p.status === 'complete' ? '#10b981' :
                    p.status === 'running'  ? 'linear-gradient(90deg, #6366f1, #8b5cf6)' :
                    p.status === 'paused'   ? '#fbbf24' : 'transparent',
                  boxShadow:
                    p.status === 'running' ? '0 0 6px rgba(99,102,241,0.6)' : 'none',
                }} />
            </div>
          ))}
        </div>

        {/* Overall bar */}
        <div className="h-1 rounded-full overflow-hidden mb-4"
          style={{ background: 'rgba(99,102,241,0.06)' }}>
          <div ref={barRef} className="h-full rounded-full"
            style={{ width: '0%', background: 'linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa)', boxShadow: '0 0 6px rgba(99,102,241,0.4)' }} />
        </div>

        {/* Current phase info */}
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs text-[#353560] uppercase tracking-[0.15em] mb-0.5 font-bold">Current Phase</div>
            <div className="text-xs font-semibold text-[#a0a0c0] truncate max-w-[140px]">
              {meta?.name ?? `Phase ${currentPhase}`}
            </div>
          </div>
          {runningPhase && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-widest"
              style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)', color: '#818cf8' }}>
              <span className="w-1.5 h-1.5 rounded-full bg-[#6366f1] dot-pulse" />
              Live
            </div>
          )}
        </div>
      </div>
    </PanelCard>
  );
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Evolution Panel Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function EvolutionPanel({
  evolution,
}: {
  evolution: NonNullable<ReturnType<typeof useFactory>['state']['pipeline']>['evolution'];
}) {
  const total = evolution.total_rules;
  const agentEntries = Object.entries(evolution.by_agent) as [string, { learned: number; written: number }][];
  const totalForBar = agentEntries.reduce((sum, [, s]) => sum + s.learned + s.written, 0) || 1;

  const prevTotal = useRef(0);
  const totalRef  = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (total > prevTotal.current && totalRef.current) {
      gsap.fromTo(totalRef.current,
        { scale: 1.3, color: '#10b981' },
        { scale: 1, color: '#818cf8', duration: 0.5, ease: 'elastic.out(1,0.5)' }
      );
    }
    prevTotal.current = total;
  }, [total]);

  return (
    <PanelCard accent="#8b5cf6">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)' }}>
              <Brain className="w-3.5 h-3.5 text-[#8b5cf6]" />
            </div>
            <span className="text-xs font-bold text-[#c0c0e0]">Self-Evolution</span>
          </div>
          {total > 0 && (
            <div className="flex items-center gap-1 text-[#10b981]">
              <TrendingUp className="w-3 h-3" />
              <span className="text-micro font-black uppercase tracking-widest">Active</span>
            </div>
          )}
        </div>

        {/* Big total */}
        <div className="flex items-end gap-2 mb-3">
          <span ref={totalRef} className="text-5xl font-black leading-none text-gradient-indigo">
            {total}
          </span>
          <div className="pb-1">
            <div className="text-xs text-[#5a5a80] leading-tight">rules learned</div>
            <div className="text-micro text-[#353560] leading-tight">across all agents</div>
          </div>
        </div>

        {/* Segmented color bar */}
        {agentEntries.length > 0 && (
          <div className="relative flex h-2 rounded-full overflow-hidden gap-px mb-3">
            {agentEntries.map(([agent, stats]) => {
              const count = stats.learned + stats.written;
              if (!count) return null;
              return (
                <div key={agent}
                  title={`${agent.replace('_', ' ')}: ${count} rules`}
                  className="transition-all duration-700 rounded-full"
                  style={{
                    background: AGENT_COLORS[agent] ?? '#6366f1',
                    flex: count / totalForBar,
                    minWidth: count ? '3px' : undefined,
                    boxShadow: count > 0 ? `0 0 4px ${AGENT_COLORS[agent] ?? '#6366f1'}80` : 'none',
                  }} />
              );
            })}
            {/* Shimmer sweep over the bar */}
            <div className="absolute inset-0 shimmer-fast pointer-events-none rounded-full opacity-40"
              style={{ background: 'linear-gradient(90deg,transparent,rgba(255,255,255,0.12),transparent)' }} />
          </div>
        )}

        {/* Agent breakdown */}
        <div className="space-y-1 max-h-40 overflow-y-auto scrollbar-thin pr-0.5">
          {agentEntries.map(([agent, stats]) => {
            const count = stats.learned + stats.written;
            const color = AGENT_COLORS[agent] ?? '#6366f1';
            return (
              <div key={agent}
                className="flex items-center justify-between py-0.5 group transition-all hover:bg-[rgba(99,102,241,0.04)] -mx-1 px-1 rounded-lg">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="w-2 h-2 rounded-full flex-shrink-0 transition-transform group-hover:scale-125"
                    style={{ background: color, boxShadow: `0 0 4px ${color}80` }} />
                  <span className="text-xs text-[#8888aa] capitalize group-hover:text-[#a0a0c0] transition-colors truncate">
                    {agent.replace('_', ' ')}
                  </span>
                </div>
                <span className="text-xs font-black tabular-nums"
                  style={{ color: count > 0 ? color : '#353560' }}>{count}</span>
              </div>
            );
          })}
        </div>
      </div>
    </PanelCard>
  );
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Activity Log Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function ActivityLog({
  entries,
}: {
  entries: { timestamp: number; type: string; message: string; phase: number; agent?: string }[];
}) {
  const logRef  = useRef<HTMLDivElement>(null);
  const prevLen = useRef(0);
  const [filter, setFilter] = useState<string | null>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
    if (entries.length > prevLen.current && logRef.current) {
      const rows = logRef.current.querySelectorAll('.log-row');
      const last = rows[rows.length - 1];
      if (last) {
        gsap.fromTo(last,
          { opacity: 0, x: -8, background: 'rgba(99,102,241,0.06)' },
          { opacity: 1, x: 0, background: 'transparent', duration: 0.35, ease: 'power2.out' }
        );
      }
    }
    prevLen.current = entries.length;
  }, [entries.length]);

  const visible = filter ? entries.filter(e => e.type === filter) : entries;

  return (
    <PanelCard accent="#10b981">
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-xl flex items-center justify-center relative"
              style={{ background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.18)' }}>
              <Activity className={`w-3.5 h-3.5 text-[#10b981]${entries.length > 0 ? ' animate-pulse' : ''}`} />
              {entries.length > 0 && (
                <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full text-micro flex items-center justify-center font-black"
                  style={{ background: '#10b981', color: '#020208' }}>
                  {entries.length > 99 ? '9+' : entries.length}
                </span>
              )}
            </div>
            <span className="text-xs font-bold text-[#c0c0e0]">Activity</span>
          </div>
          <button
            onClick={() => setFilter(null)}
            className="text-micro text-[#353560] hover:text-[#5a5a80] transition-colors font-mono uppercase tracking-widest">
            {filter ? 'clear' : `${entries.length} events`}
          </button>
        </div>

        <div ref={logRef} className="space-y-0.5 max-h-52 overflow-y-auto scrollbar-thin pr-0.5">
          {visible.length === 0 ? (
            <div className="py-8 text-center">
              <div className="w-8 h-8 rounded-xl mx-auto mb-3 flex items-center justify-center" style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.12)' }}>
                <Zap className="w-4 h-4" style={{ color: 'rgba(16,185,129,0.35)' }} />
              </div>
              <p className="text-micro text-[#353560]">Waiting for pipeline&hellip;</p>
            </div>
          ) : (
            visible.slice(-30).map((e, i) => {
              const dotColor = TYPE_COLOR[e.type] ?? '#353560';
              return (
                <div key={`${e.timestamp}-${i}`}
                  className="log-row flex items-start gap-2 py-1 px-1 rounded-lg group hover:bg-[rgba(99,102,241,0.04)] transition-colors cursor-default">
                  <span className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 transition-all group-hover:scale-125"
                    style={{ background: dotColor, boxShadow: `0 0 4px ${dotColor}80` }} />
                  <p className="text-micro text-[#5a5a80] leading-snug group-hover:text-[#a0a0c0] transition-colors wrap-break-word">
                    {e.message}
                  </p>
                </div>
              );
            })
          )}
        </div>
      </div>
    </PanelCard>
  );
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Run History Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function RunHistoryPanel({
  history,
}: {
  history: { id: string; name: string; score?: number; status: string; retries: number; started_at: number }[];
}) {
  return (
    <PanelCard accent="#818cf8">
      <div className="p-4">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-7 h-7 rounded-xl flex items-center justify-center"
            style={{ background: 'rgba(129,140,248,0.07)', border: '1px solid rgba(129,140,248,0.18)' }}>
            <BarChart3 className="w-3.5 h-3.5 text-[#818cf8]" />
          </div>
          <span className="text-xs font-bold text-[#c0c0e0]">Run History</span>
        </div>

        {history.length === 0 ? (
          <div className="py-8 text-center">
            <div className="w-8 h-8 rounded-xl mx-auto mb-3 flex items-center justify-center" style={{ background: 'rgba(129,140,248,0.06)', border: '1px solid rgba(129,140,248,0.12)' }}>
              <BarChart3 className="w-4 h-4" style={{ color: 'rgba(129,140,248,0.35)' }} />
            </div>
            <p className="text-micro text-[#353560]">No previous runs</p>
          </div>
        ) : (
          <div className="space-y-1">
            {history.slice(0, 5).map((run) => {
              const complete    = run.status === 'complete';
              const scoreColor  =
                (run.score ?? 0) >= 90 ? '#10b981' :
                (run.score ?? 0) >= 80 ? '#6366f1' :
                (run.score ?? 0) >= 70 ? '#fbbf24' : '#f87171';

              return (
                <div key={run.id}
                  className="flex items-center gap-2.5 p-2.5 rounded-xl group transition-all hover:bg-[rgba(99,102,241,0.05)] cursor-default">
                  {complete
                    ? <CheckCircle2 className="w-3.5 h-3.5 text-[#10b981] flex-shrink-0" />
                    : <XCircle className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'rgba(248,113,113,0.5)' }} />
                  }
                  <div className="flex-1 min-w-0">
                    <div className="text-2xs text-[#c0c0e0] truncate font-medium group-hover:text-[#f0f0fc] transition-colors">
                      {run.name}
                    </div>
                    <div className="text-xs text-[#5a5a80] flex items-center gap-2 mt-0.5">
                      <Clock className="w-2.5 h-2.5" />
                      <span>{new Date(run.started_at).toLocaleDateString()}</span>
                      {run.retries > 0 && (
                        <span className="text-[#fbbf24] font-semibold">{run.retries}Ãƒâ€” retry</span>
                      )}
                    </div>
                  </div>
                  <div className="text-sm font-black tabular-nums"
                    style={{ color: run.score != null ? scoreColor : '#353560' }}>
                    {run.score != null ? run.score : 'Ã¢â‚¬â€'}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </PanelCard>
  );
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Main AmbientPanel Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
export function AmbientPanel() {
  const { state }    = useFactory();
  const { pipeline } = state;
  const panelRef     = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (panelRef.current && pipeline) {
      const sections = panelRef.current.querySelectorAll('.panel-section');
      gsap.fromTo(sections,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: 'power3.out', delay: 0.15 }
      );
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [!!pipeline]);

  if (!pipeline) return null;

  return (
    <div ref={panelRef} className="space-y-3 sticky top-24">
      <div className="panel-section">
        <PhaseProgress currentPhase={pipeline.current_phase} phases={pipeline.phases} />
      </div>
      <div className="panel-section">
        <EvolutionPanel evolution={pipeline.evolution} />
      </div>
      <div className="panel-section">
        <ActivityLog entries={pipeline.activity_log} />
      </div>
      <div className="panel-section">
        <RunHistoryPanel history={pipeline.run_history} />
      </div>
    </div>
  );
}
